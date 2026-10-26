#!/usr/bin/env python3
"""Minimal Bus Pirate 5/6 serial helper.

Examples
--------
    bp.py list
    bp.py list --probe
    bp.py run "i"
    bp.py run "m i2c" "P" "W 3.3 50" "scan"
    bp.py run -p /dev/ttyACM0 -t 120 "flash probe" "flash read -f /tmp/flash.bin"
    bp.py script setup.bp

The helper targets the Bus Pirate *terminal* port (the one with a `HiZ>` prompt).
It answers interactive menu prompts with their defaults, declines destructive
y/n confirmations unless --yes is given, and strips ANSI escape codes.

Requires pyserial:  python3 -m pip install pyserial
"""

from __future__ import annotations

import argparse
import re
import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:  # pragma: no cover - dependency check
    serial = None
    list_ports = None

ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")

MODE_PROMPT = re.compile(
    r"(?:^|\n)"
    r"(?:HiZ|1WIRE|UART|HDUART|I2C|SPI|2WIRE|3WIRE|DIO"
    r"|LED(?:-\([A-Z0-9]*\))?|INFRARED(?:-\([A-Z0-9]*\))?|JTAG"
    r"|SUBGHZ(?:-\([A-Z0-9]*\))?|RF24|RFID|LCDTAP|PS2|USB|I2S|[A-Za-z0-9_]+)"
    r">\s*$"
)

MENU_DEFAULT = re.compile(r"(?:\([^)]*\)|\[[^\]]*\])\s*>\s*$")

MENU_NAMED = re.compile(
    r"(?:Mode|Display|Type|Protocol|Parity|Data bits|Bits|Stop bits|Speed|Baud"
    r"|Clock|CS|Flow control|Invert signals|RX sensor|TX modulation"
    r"|Choose available pin|Voltage|Current)\b[^\n]*>\s*$",
    re.IGNORECASE,
)

CONFIRM = re.compile(r"(?:y/n|are you sure|erase the internal storage|skip confirmation)", re.IGNORECASE)

VT100_PROMPT = "VT100 compatible color mode"


def fail(message: str, code: int = 2) -> "NoReturn":  # type: ignore[name-defined]
    print(message, file=sys.stderr)
    raise SystemExit(code)


def require_pyserial() -> None:
    if serial is None:
        fail(
            "pyserial is not installed.\n"
            "Install it with:  python3 -m pip install pyserial\n"
            "or use a terminal program (picocom/screen/Tera Term) instead.",
            2,
        )


def clean(data: bytes) -> str:
    text = data.decode("utf-8", "replace")
    return ANSI.sub("", text).replace("\r\n", "\n").replace("\r", "\n")


def port_rows():
    require_pyserial()
    rows = []
    for p in sorted(list_ports.comports(), key=lambda x: x.device):
        text = " ".join(
            str(v) for v in (p.description, p.manufacturer, p.product, p.hwid) if v
        )
        likely = bool(
            p.vid == 0x2E8A
            or re.search(r"bus\s*pirate|raspberry\s*pi|pico|usb\s*serial|cdc", text, re.I)
        )
        rows.append((p.device, p.vid, p.pid, p.description or "", likely))
    return rows


def candidates():
    return [row for row in port_rows() if row[4]]


def probe_port(device: str, baud: int) -> bool:
    """Send a bare CR and look for a Bus Pirate prompt. Safe at a prompt."""
    try:
        with serial.Serial(device, baud, timeout=0.3, write_timeout=1) as ser:
            ser.reset_input_buffer()
            ser.write(b"\r\n")
            time.sleep(0.5)
            data = clean(ser.read(4096))
            return bool(MODE_PROMPT.search(data) or VT100_PROMPT in data or "Bus Pirate" in data)
    except Exception:
        return False


def resolve_port(explicit: str | None, baud: int) -> str:
    require_pyserial()
    if explicit:
        return explicit
    rows = port_rows()
    if not rows:
        fail("No serial ports found. Is the Bus Pirate connected?", 2)
    pool = [row for row in rows if row[4]]
    if not pool:
        listing = "\n".join(
            f"  {dev}  {vid or '----'}:{pid or '----'}  {desc}"
            for dev, vid, pid, desc, _ in rows
        )
        fail(
            "No likely Bus Pirate port found; refusing to probe unrelated ports.\n"
            f"Ports:\n{listing}\n"
            "Pass --port explicitly if you know the terminal port.",
            2,
        )
    responsive = [row[0] for row in pool if probe_port(row[0], baud)]
    if responsive:
        if len(responsive) > 1:
            print(
                f"note: multiple ports responded ({', '.join(responsive)}); using {responsive[0]}",
                file=sys.stderr,
            )
        return responsive[0]
    listing = "\n".join(
        f"  {dev}  {vid or '----'}:{pid or '----'}  {desc}" for dev, vid, pid, desc, _ in rows
    )
    fail(
        "Could not auto-detect the Bus Pirate terminal port.\n"
        f"Ports:\n{listing}\n"
        "If another program holds the port, close it. Otherwise pass --port.",
        2,
    )


def open_port(device: str, baud: int, keep_vt100: bool = False):
    require_pyserial()
    try:
        ser = serial.Serial(device, baud, timeout=0.1, write_timeout=2)
    except Exception as exc:
        fail(f"Cannot open {device}: {exc}", 2)
    ser.reset_input_buffer()
    ser.write(b"\r\n")
    time.sleep(0.6)
    greeting = clean(ser.read(8192))
    if VT100_PROMPT in greeting:
        # Default to ASCII so automated captures have no status-bar escape codes.
        ser.write(b"\r\n" if keep_vt100 else b"n\r\n")
        time.sleep(0.6)
        greeting += clean(ser.read(8192))
    return ser, greeting


def run_one(
    ser,
    command: str,
    timeout: float,
    auto_defaults: bool,
    assume_yes: bool,
    raw: bool,
    verbose: bool,
) -> tuple[str, str]:
    """Return (output, status). status is ok|timeout|declined."""
    ser.reset_input_buffer()
    ser.write(command.encode("utf-8", "replace") + b"\r\n")

    deadline = time.monotonic() + timeout
    buffer = ""
    answered = 0
    vetoes = 0
    status = "ok"

    while time.monotonic() < deadline:
        chunk = ser.read(4096)
        if chunk:
            buffer += chunk.decode("utf-8", "replace")

        text = clean(buffer.encode("utf-8", "replace"))
        tail = text[-300:]

        if MODE_PROMPT.search(text):
            break

        if auto_defaults and tail.rstrip().endswith(">"):
            if CONFIRM.search(tail):
                if assume_yes:
                    ser.write(b"y\r\n")
                    if verbose:
                        print("[auto-confirm] y", file=sys.stderr)
                    time.sleep(0.1)
                    continue
                ser.write(b"n\r\n")
                vetoes += 1
                status = "declined"
                if verbose:
                    print("[safety] declined y/n prompt with n", file=sys.stderr)
                if vetoes >= 2:
                    break
                time.sleep(0.1)
                continue

            if MENU_DEFAULT.search(tail) or MENU_NAMED.search(tail):
                ser.write(b"\r\n")
                answered += 1
                if verbose:
                    print(f"[default] answered menu prompt #{answered}", file=sys.stderr)
                if answered > 12:
                    break
                time.sleep(0.05)
                continue

        time.sleep(0.02)
    else:
        status = "timeout"

    output = buffer if raw else clean(buffer.encode("utf-8", "replace"))
    return output.rstrip(), status


def cmd_list(args) -> int:
    rows = port_rows()
    if not rows:
        print("No serial ports found.")
        return 1
    print(f"{'DEVICE':<18} {'VID:PID':<12} DESCRIPTION")
    for dev, vid, pid, desc, likely in rows:
        marker = " *" if likely else ""
        vidpid = f"{vid:04x}:{pid:04x}" if vid and pid else "-"
        print(f"{dev:<18} {vidpid:<12} {desc}{marker}")
    print("\n* likely Bus Pirate / USB CDC candidate")
    if args.probe:
        print("\nProbing candidates with a bare CR:")
        for dev, _, _, _, likely in rows:
            if likely:
                print(f"  {dev}: {'terminal responded' if probe_port(dev, args.baud) else 'no prompt'}")
    return 0


def cmd_run(args) -> int:
    device = resolve_port(args.port, args.baud)
    ser, greeting = open_port(device, args.baud, keep_vt100=args.vt100)
    if args.verbose:
        print(greeting.strip(), file=sys.stderr)
        print(f"[port] {device} @ {args.baud}", file=sys.stderr)

    exit_code = 0
    try:
        for command in args.commands:
            print(f">>> {command}")
            output, status = run_one(
                ser,
                command,
                timeout=args.timeout,
                auto_defaults=not args.no_defaults,
                assume_yes=args.yes,
                raw=args.raw,
                verbose=args.verbose,
            )
            if output:
                print(output)
            if status == "timeout":
                print(f"[timeout after {args.timeout:g}s]", file=sys.stderr)
                exit_code = 3
                if not args.keep_going:
                    break
            elif status == "declined":
                print("[confirmation declined; pass --yes only for intentional destructive use]", file=sys.stderr)
                exit_code = 4
                if not args.keep_going:
                    break
    finally:
        ser.close()
    return exit_code


def cmd_script(args) -> int:
    try:
        with open(args.file, "r", encoding="utf-8") as handle:
            lines = [line.rstrip("\n") for line in handle]
    except OSError as exc:
        fail(f"Cannot read script: {exc}", 2)

    commands = [
        line.strip()
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not commands:
        fail("Script has no commands.", 2)
    args.commands = commands
    return cmd_run(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bus Pirate 5/6 serial helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--baud", type=int, default=115200, help="port speed (default 115200; irrelevant for USB CDC)")
    common.add_argument("--vt100", action="store_true", help="keep VT100 mode instead of switching to ASCII")
    common.add_argument("-v", "--verbose", action="store_true", help="show connection info and auto-answers")

    sub = parser.add_subparsers(dest="mode", required=True)

    p_list = sub.add_parser("list", parents=[common], help="list serial ports")
    p_list.add_argument("--probe", action="store_true", help="probe likely candidates for a prompt")
    p_list.set_defaults(func=cmd_list)

    p_run = sub.add_parser("run", parents=[common], help="run one or more commands")
    p_run.add_argument("-p", "--port", help="serial device (auto-detect by default)")
    p_run.add_argument("-t", "--timeout", type=float, default=60.0, help="per-command timeout seconds (default 60)")
    p_run.add_argument("--no-defaults", action="store_true", help="do not auto-answer menu prompts")
    p_run.add_argument("--yes", action="store_true", help="auto-confirm y/n prompts (dangerous)")
    p_run.add_argument("--raw", action="store_true", help="keep ANSI escapes and CR characters")
    p_run.add_argument("-k", "--keep-going", action="store_true", help="continue after timeout/declined")
    p_run.add_argument("commands", nargs="+", help="commands to send, quoted individually")
    p_run.set_defaults(func=cmd_run)

    p_script = sub.add_parser("script", parents=[common], help="run commands from a file (# comments, one per line)")
    p_script.add_argument("file", help="script file")
    p_script.add_argument("-p", "--port", help="serial device (auto-detect by default)")
    p_script.add_argument("-t", "--timeout", type=float, default=60.0, help="per-command timeout seconds")
    p_script.add_argument("--no-defaults", action="store_true", help="do not auto-answer menu prompts")
    p_script.add_argument("--yes", action="store_true", help="auto-confirm y/n prompts (dangerous)")
    p_script.add_argument("--raw", action="store_true", help="keep ANSI escapes and CR characters")
    p_script.add_argument("-k", "--keep-going", action="store_true", help="continue after timeout/declined")
    p_script.set_defaults(func=cmd_script)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
