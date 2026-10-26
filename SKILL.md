---
name: bus-pirate
description: >-
  Connect to a Bus Pirate 5/6 or RB-Pirate over USB serial and run terminal commands without reading the
  full manual. Use for I2C/SPI/UART/1-Wire/HDUART/2-Wire/3-Wire/JTAG/DIO probing, bus scans,
  SUBGHZ (CC1101), RFID/NFC (PN532), RF24 (nRF24L01), LCDTAP (LCD bus sniffer), CELL (AT modem),
  infrared (Flipper .ir), register and EEPROM reads, SPI flash dump/read/write, UART bridges,
  voltage and pull-up checks, logic captures, and scripted sequences on the command line.
---

# Bus Pirate & RB-Pirate — connect and run commands

Compact operational guide distilled from https://docs.buspirate.com/docs/command-reference/
and the custom **RB-Pirate** firmware fork (`RP2350B`, TF card storage, merged Sub-GHz/RFID/RF24/LCDTAP/Cellular modes).
Load `references/commands.md` for full flags and `references/protocols.md` for wiring/config.

## 0. 60-second quick start

```bash
# Linux: the Bus Pirate exposes two USB CDC ports (terminal + binmode)
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null

# Helper shipped with this skill (requires pyserial)
python3 ~/.config/opencode/skills/bus-pirate/scripts/bp.py list
python3 ~/.config/opencode/skills/bus-pirate/scripts/bp.py run "i"
```

Manual terminal:

```bash
picocom -b 115200 /dev/ttyACM0     # exit: Ctrl-A Ctrl-X
screen  /dev/ttyACM0 115200        # exit: Ctrl-A K
```

Windows: Tera Term/PuTTY on `COMx`, 115200 8N1. Port speed is emulated over USB CDC.

- Always boots in **HiZ** (safe: all outputs off). Pick a protocol with `m`.
- The board exposes **two** serial ports: one is the terminal (`HiZ>`), the other is `binmode` (PulseView/Flashrom).
- On fresh boot the terminal asks `VT100 compatible color mode? (Y/n)>`. Enter = VT100, `n` = ASCII (recommended for scripts/captures).
- `cls` redraws the screen; `i` prints firmware/board/active mode info (reports **RB-Pirate** on custom hardware).
- Storage: RB-Pirate uses a **TF (MicroSD) card** on the SPI bus for configurations, dumps, `.sub`, `.ir`, and BMP captures.

## 1. Rules that prevent most failures

1. **Every command has help:** `help`, `help mode`, or `<command> -h` (e.g. `W -h`, `subghz -h`, `rfid -h`).
2. **Menus**: Enter accepts the default in `( )` / `*`; `x` exits without saving. Saved settings are offered on the next mode change — Enter reloads them.
3. **Use argument forms** (`W 3.3 50`, `m i2c`, `flash read -f dump.bin`, `m subghz`) so the command never hangs in an interactive menu.
4. **Bus commands must start with `[`, `{`, or `>`** and are limited to 255 characters/line.
5. Open-drain buses (**I2C, 1-Wire, 2-Wire, HDUART**) need pull-ups: `P` enables onboard 10K pull-ups (powered from VREF/VOUT, so voltage must be present via `W` or external target).
6. Prefer ASCII terminal mode for automated scripts (`bp.py` strips ANSI automatically).

## 2. Safety checklist

- Start/return to **HiZ** (`m hiz`) when unsure; it disables all outputs.
- Check target voltage before connecting. Bus Pirate IO is 1.65–5 V. Set supply with `W <volts> <mA>`; read it back with `v`.
- PPSU is rated **300 mA** (500 mA maximum limit). More current needs an external supply.
- `~` self-test only works in HiZ and **requires everything disconnected**.
- Irreversible/destructive: `format`, `flash erase|write|test`, `eeprom erase|write|test`, `ddr4/ddr5 write`, `sle4442 erase|psc`, `$` (bootloader).
- Radio / RF modes (`subghz jam`, `rf24 jam`, `bruteforce`): Use only in controlled lab/shielded environments! Respect local RF regulations.

## 3. Global commands

| Command | Action |
| --- | --- |
| `i` | Version, hardware (RB-Pirate / BP6), serial, storage, active mode |
| `m [mode]` | Mode menu, or jump directly: `m i2c`, `m spi`, `m uart`, `m subghz`, `m rfid`, `m rf24`, `m lcdtap`, `m hiz` |
| `c` | Configuration menu (language, ANSI color/toolbar, LCD screensaver, LED effect) |
| `l` / `L` | MSB-first (default) / LSB-first |
| `o` | Output format: Auto*, HEX, DEC, BIN, ASCII |
| `d` | LCD display mode: Default / Scope |
| `~` | Self-test (HiZ only, nothing connected) |
| `cls` | Clear and redraw terminal |
| `reboot` / `$` | Reboot / jump to UF2 bootloader (RP2350) |
| `trace` | Wire trace between pins (checks inter-pin continuity) |
| `rogue` | Rogue probe testing / scanning |
| `crack` | Crypto cracking helper |
| `xflash` | Cross-flash utility |
| `hexedit <file>` / `edit <file>` | On-device hex and text editors for TF card files |
| `?` / `help` / `help mode` | All commands / current-mode commands |

## 4. Utilities

| Command | Action |
| --- | --- |
| `w` / `W` | PSU off / on. `W <V> <mA> [-u <%>]`; `W 3.3` = 300 mA default; `0` = unlimited |
| `v` / `V` | Voltage report once / continuous (any key exits) |
| `p` / `P` | Pull-ups off / on |
| `g` / `G` | Frequency generator off / menu. `g <pin>` disables one pin |
| `f` / `F` | Measure frequency once / continuous. Odd pins only (1,3,5,7) |
| `= <n>` | Convert to HEX/DEC/BIN |
| `\| <n>` | Reverse bits |
| `a <pin>` / `A <pin>` / `@ <pin>` | Pin low / high / input+read (space syntax at prompt) |
| `logic` | Logic analyzer: `logic start\|stop\|hide\|show\|nav [-i] [-o N] [-f Hz]` |
| `jep106 <bank> <id>` | JEDEC JEP106 vendor lookup |

## 5. Bus command mini-language

| Token | Meaning |
| --- | --- |
| `[` / `{` | START / alternate START (SPI+3WIRE: CS active; UART: open; 1-Wire: reset; 2WIRE: RST high) |
| `]` / `}` | STOP / alternate STOP (SPI: CS idle; UART: close; 2WIRE: RST low) |
| `>` | Execute bus commands without START |
| `r`, `r:n` | Read one byte / $n$ bytes (up to 255) |
| `0xNN`, `0bNN`, `NN` | Write HEX / binary / decimal byte |
| `"text"` | Write ASCII string |
| `d`, `d:n`, `D`, `D:n` | Delay 1 µs / $n$ µs / 1 ms / $n$ ms |
| `:` | Repeat previous item: `0x55:2`, `r:5` |
| `.n` | Partial bits: `0x5a.4`, `r.4` |
| `v.<pin>` | Measure pin voltage during bus commands |
| `a.<pin>` / `A.<pin>` / `@.<pin>` | Pin low / high / input+read during bus commands |
| `^` `/` `\` `-` `_` `.` | Tick clock / clock high / clock low / data high / data low / read data (2WIRE/3WIRE) |

---

## 6. Mode Cheat Sheet & Custom RB-Pirate Modes

| Mode | Target Hardware | Pull-ups | Key Commands |
| --- | --- | --- | --- |
| **HiZ** | none | n/a | Safe idle state |
| **I2C** | SDA, SCL, GND | **required** | `scan -v`, `sniff`, `i2c dump`, `eeprom`, `ddr4`, `ddr5` |
| **SPI** | MOSI, MISO, CS, CLK, GND | usually no | `flash probe`, `flash read`, `flash write`, `eeprom` |
| **UART** | TX, RX, GND | no | `bridge`, `gps`, `glitch`, plus **CELL** modem suite |
| **HDUART**| RXTX ↔ RXTX, GND | **required** | `bridge -s`, `{`/`}` = RST high/low (IO2) |
| **1WIRE** | OWD ↔ OWD, GND | **required** | `scan`, `ds18b20`, `eeprom` |
| **2WIRE** | SDA, SCL, RST, GND | **required** | `sniff`, `sle4442 init|dump|unlock|write` |
| **3WIRE** | MOSI, MISO, CS, CLK, GND | no | Bit-level `^ / \ - _ .` |
| **DIO** | Any IO pins | no | `>0xff`, `>r`, `@ 0`, `G`, `f 1` |
| **LED** | SDO→DIN, GND | no | WS2812, SK6812, APA102 |
| **INFRARED**| IRTX/IRRX + GND | no | `load`, `send`, `record`, `receive`, `replay`, `jam`, `devicebgone`, `tvbgone` |
| **SUBGHZ**| CC1101 module (SPI + GDO0) | no | `setfrequency`, `scan`, `sweep`, `receive`, `replay`, `record`, `load`, `ear`, `jam`, `bruteforce` |
| **RFID** | PN532 over HSU UART | no | `info`, `read`, `scan`, `dump`, `restore`, `write`, `clone`, `erase`, `ndef`, `nonce` |
| **RF24** | nRF24L01+ module (SPI) | no | `setchannel`, `scan`, `sweep`, `waterfall`, `send`, `receive`, `jam` |
| **LCDTAP**| External LCD Bus (I2C/SPI) | no | `status`, `cmddump`, `reset`, `save <out.bmp>` |
| **PS2** | IO0 (CLK), IO1 (DAT), GND | external | `sniff` (PS/2 keyboard & mouse traffic sniffer) |
| **USB** | IO0 (D+), IO1 (D-), GND | external | `sniff` (Low/Full-Speed USB packet sniffer) |
| **I2S** | IO0 (BCLK), IO1 (LRCLK), IO2 (DOUT) | no | `sine [Hz]`, `wav -f <file.wav>` |
| **JTAG** | IO0..IO7 → target pins | no | `bluetag jtag -c 8`, `bluetag swd -c 8` |

---

### SUBGHZ (CC1101 Sub-GHz Transceiver)
Operates between 300–928 MHz (ISM bands: 315MHz, 433.92MHz, 868MHz, 915MHz):
```text
m subghz                        # Enter Sub-GHz mode
setfrequency 433920             # Set frequency to 433.92 MHz (in kHz)
rssi                            # Read signal strength / peak
scan                            # Scan frequency range or discrete channels
sweep                           # Multi-sample signal detection
waterfall                       # ASCII waterfall of RF spectrum over time
receive                         # Capture pulse train from GDO0 and run protocol decoders
record /capture.sub             # Record raw pulses directly to Flipper .sub file on TF card
load /remote.sub                # Load and parse Flipper RAW or protocol key file
decode /remote.sub              # Inspect/decode .sub without transmitting
replay                          # Replay captured pulse buffer via CC1101 TX
clone                           # Guided capture, decode, and save in one step
send princeton 0x123456 24      # Transmit protocol frame / payload
ear                             # Map real-time RSSI to audible PWM tone on a buffered pin
jam                             # Transmit RF energy (lab use only!)
bruteforce                      # Transmit all 4096 codes of a 12-bit fixed-code protocol (Nice, Came, etc.)
keyload keeloq_mfcodes          # Load KeeLoq manufacturer decryption keys
```

### RFID / NFC (PN532 over HSU UART)
Full 13.56 MHz RFID/NFC toolkit:
```text
m rfid                          # Enter RFID mode
info                            # PN532 firmware version and connection check
read                            # Scan and display tag UID, type, and ATQA/SAK
scan                            # Poll ISO14443A/B, FeliCa, and Jewel tags
scanner                         # Bulk tag inventory (logs unique UIDs)
dump -f tag.bin                 # Dump full tag memory (MIFARE Classic 1K/4K, Ultralight, NTAG)
restore -f tag.bin              # Restore binary image to tag
clone                           # Clone UID to Magic Card (Gen1A / Gen2 UID changeable)
write -b 4 -d 00112233445566778899AABBCCDDEEFF  # Write data block
ndef -r                         # Read NDEF record (URI, text)
nonce                           # Collect MIFARE auth nonces for offline key recovery (mfkey32/crapto1)
pwauth                          # NTAG/Ultralight-EV1 password authentication
```

### RF24 (nRF24L01+ 2.4GHz)
```text
m rf24                          # Enter RF24 mode
setchannel 76                   # Set 2.4GHz channel (0-125)
scan                            # Channel energy/carrier detection scan
sweep                           # Multi-channel sweep across 2.4GHz band
waterfall                       # 2.4GHz spectrum waterfall display
receive                         # Listen for packets on configured address/channel
send 0xDEADBEEF                 # Transmit packet payload
jam 76                          # Continuous carrier / jamming (lab use only)
```

### LCDTAP (Passive External LCD Bus Sniffer)
Passively listens on external LCD connections (I2C, 4-line SPI, 9-bit SPI3) and reconstructs the image:
```text
m lcdtap                        # Enter LCDTAP mode
status                          # Check incoming frame synchronization and pixel count
cmddump                         # Dump captured LCD controller commands
save /screenshot.bmp            # Export captured framebuffer directly as BMP on TF card!
reset                           # Reset framebuffer capture state
```
Supported display controllers: `ST7032`, `ST7789`, `ILI9341`, `SSD1306`, `SSD1331`, `KS0108`.

### CELL (Cellular AT Modem inside UART Mode)
When connected to a SIMCom / Quectel / 3GPP cellular modem via UART:
```text
m uart                          # Set baud to modem rate (usually 115200)
cellmodem                       # Query manufacturer, model, IMEI, firmware version
cellnet                         # Network registration status, signal strength (CSQ RSSI/BER)
cellops                         # Scan and list available cellular operators
cellsim                         # Check SIM status, ICCID, PIN requirement
cellpin -p 1234                 # Enter SIM PIN or PUK
cellsms -r                      # Read SMS inbox messages
cellsms -s +123456789 -m "Test" # Send SMS
cellussd -u "*100#"             # Send USSD query and display network response
cellat "AT+CSQ"                 # Send raw AT command and display response
```

### Enhanced INFRARED
```text
m infrared
load /tv.ir                     # Load Flipper .ir file from TF card
send                            # Transmit loaded IR command
record /remote.ir               # Record incoming IR signal to Flipper format
receive                         # Live IR demodulator / protocol decoder
replay                          # Replay last captured IR signal
jam                             # Transmit continuous IR carrier disruption
devicebgone                     # Blast power-off codes for TVs/projectors
remote                          # Interactive terminal remote control interface
```

---

## 7. Host Helper: `scripts/bp.py`

Run commands non-interactively from terminal, scripts, or agent workflows:

```bash
# General health & hardware check:
python3 ~/.config/opencode/skills/bus-pirate/scripts/bp.py run "i"

# Sub-GHz scan on 433.92 MHz:
python3 ~/.config/opencode/skills/bus-pirate/scripts/bp.py run "m subghz" "setfrequency 433920" "rssi"

# RFID tag reading:
python3 ~/.config/opencode/skills/bus-pirate/scripts/bp.py run "m rfid" "read"

# Cellular modem check:
python3 ~/.config/opencode/skills/bus-pirate/scripts/bp.py run "m uart" "cellmodem" "cellnet"

# I2C bus scan:
python3 ~/.config/opencode/skills/bus-pirate/scripts/bp.py run "m i2c" "W 3.3 50" "P" "scan -v"

# SPI Flash chip probe:
python3 ~/.config/opencode/skills/bus-pirate/scripts/bp.py run "m spi" "W 3.3 50" "P" "flash probe"
```

## 8. Reference Files
- `references/commands.md` — Complete flag and parameter catalog for all Bus Pirate & RB-Pirate commands.
- `references/protocols.md` — Wiring diagrams, pinouts, and electrical notes.
- `scripts/bp.py` — Serial runner helper.
