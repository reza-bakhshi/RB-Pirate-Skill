<div align="center">

# RB-Pirate Skill

**Agent Skill & CLI Automation Suite for Bus Pirate 5/6 and RB-Pirate Hardware**

[![MCU: RP2350B](https://img.shields.io/badge/MCU-RP2350B-c51a4a?style=flat-square)](https://github.com/reza-bakhshi/RB-Pirate-Firmware)
[![Platform: OpenCode & Antigravity](https://img.shields.io/badge/Platform-OpenCode%20%7C%20Antigravity-4285f4?style=flat-square)](#installation)
[![Use: Educational Purposes](https://img.shields.io/badge/Use-Educational%20Purposes-orange?style=flat-square)](#disclaimer)
[![License: MIT](https://img.shields.io/badge/License-MIT-f5c518?style=flat-square)](LICENSE)

</div>

**RB-Pirate Skill** is a comprehensive agent skill and terminal automation toolkit designed for [OpenCode](https://opencode.ai) and [Google Antigravity](https://github.com/google-deepmind). It enables AI agents and developers to connect to, configure, probe, and automate hardware buses using **Bus Pirate 5 / 6** and the custom **[RB-Pirate](https://github.com/reza-bakhshi/RB-Pirate)** hardware fork — without needing to memorize commands or read extensive manuals.

> [!NOTE]
> ### Educational & Research Purposes Only
> This project, its documentation, and associated tools are developed and provided strictly for **educational purposes**, authorized hardware research, development, and laboratory experimentation.

---

## Features

- **Zero-Manual AI Agent Control**: Provides progressive context, hardware safety constraints, and executable command mappings for 19+ protocol modes.
- **Host Serial Automation Runner (`bp.py`)**:
  - Automatically identifies Bus Pirate CDC terminal ports.
  - Automatically handles the fresh boot `VT100 compatible color mode? (Y/n)>` prompt.
  - Strips ANSI color escape codes for clean terminal logs and scripted workflows.
  - Executes single commands, command chains, or script files with configurable timeouts.
- **Full Coverage of Upstream & RB-Pirate Extended Modes**:
  - **Sub-GHz RF (CC1101)**: 300–928 MHz spectrum scan, waterfall, Flipper Zero `.sub` recording/loading, KeeLoq keys, RSSI-to-audio `ear`, and fixed-code `bruteforce`.
  - **RFID / NFC (PN532)**: ISO14443A/B, FeliCa, MIFARE Classic/Ultralight/NTAG dumping, UID cloning to Magic Cards (Gen1A/Gen2), and NDEF read/write.
  - **2.4 GHz RF (nRF24L01+)**: Channel energy scan, multi-channel sweep, spectrum waterfall, packet TX/RX.
  - **Passive LCD Sniffing (LCDTAP)**: Parallel capture on I2C/SPI display buses and direct framebuffer reconstruction to `.bmp` image files.
  - **Cellular Modem Integration (CELL)**: 3GPP AT modem commands inside UART mode (`cellmodem`, `cellnet`, `cellsms`, `cellcall`, `cellussd`, `cellat`).
  - **Classic Protocols**: Full support for I2C, SPI, UART, HDUART, 1-Wire, 2-Wire, 3-Wire, Digital IO, JTAG/SWD (blueTag), and WS2812/APA102 LEDs.
  - **Hardware Diagnostics**: Automated inter-pin continuity wire tracing (`trace`), logic analysis (`logic`), and EEPROM/Flash programming.

---

## Directory Structure

```text
RB-Pirate-Skill/
├── README.md               # Project documentation & installation
├── SKILL.md                # Agent skill specification & operational guide
├── references/
│   ├── commands.md         # Exhaustive catalog of every command, option, and flag
│   └── protocols.md        # Pinouts, wiring diagrams, and electrical rules
└── scripts/
    └── bp.py               # Standalone non-interactive Python runner
```

---

## Installation

### For OpenCode
Clone or copy this repository into your OpenCode skills directory:
```bash
git clone https://github.com/reza-bakhshi/RB-Pirate-Skill.git ~/.config/opencode/skills/bus-pirate
```
Add the skill path to your `~/.config/opencode/opencode.jsonc`:
```jsonc
{
  "skills": [
    "/home/YOUR_USER/.config/opencode/skills/bus-pirate"
  ]
}
```

To enable the slash command `/buspirate <args>`, add the command wrapper:
```bash
mkdir -p ~/.config/opencode/commands
cat << 'EOF' > ~/.config/opencode/commands/buspirate.md
---
description: "Control Bus Pirate / RB-Pirate: protocols, pinouts, and hardware tasks"
subtask: false
---
$ARGUMENTS
EOF
```

### For Antigravity / Gemini CLI
Symlink or copy into `~/.gemini/skills/`:
```bash
ln -sf ~/.config/opencode/skills/bus-pirate ~/.gemini/skills/bus-pirate
```

---

## Quick Usage Examples

### 1. Using the Host Runner (`bp.py`)

No interactive terminal required. The tool auto-detects the port, answers prompts, and outputs clean text:

```bash
# General board info & firmware status
python3 scripts/bp.py run "i"

# Scan I2C devices with 3.3V power & pull-ups enabled
python3 scripts/bp.py run "m i2c" "W 3.3 50" "P" "scan -v"

# Probe SPI Flash and dump first 64 bytes
python3 scripts/bp.py run "m spi" "W 3.3 50" "P" "flash probe" "flash dump -s 0 -b 64"

# Tune CC1101 Sub-GHz radio to 433.92 MHz and record signal to Flipper .sub
python3 scripts/bp.py run "m subghz" "setfrequency 433920" "record /capture.sub"

# Read RFID tag UID and type
python3 scripts/bp.py run "m rfid" "read"

# Check cellular modem network registration and signal quality
python3 scripts/bp.py run "m uart" "cellmodem" "cellnet"
```

### 2. Slash Command in AI Agent Chat

In OpenCode or Antigravity, simply prompt the agent naturally or use the slash command:

```text
/buspirate i2c scan
/buspirate subghz 433920 scan
/buspirate rfid dump -f /card.bin
/buspirate lcdtap save /screenshot.bmp
/buspirate uart 115200 read gps data
```

---

## Supported Modes & Commands Summary

| Mode | Key Commands |
| :--- | :--- |
| **I2C** | `scan -v`, `sniff`, `i2c dump`, `eeprom`, `ddr4`, `ddr5`, `usbpd`, `fusb302`, `mpu6050`, sensors |
| **SPI** | `flash probe|dump|read|write|erase|test`, `eeprom`, `sniff` |
| **UART & CELL** | `bridge`, `gps`, `glitch`, `cellmodem`, `cellnet`, `cellops`, `cellsim`, `cellsms`, `cellussd`, `cellat` |
| **SUBGHZ** | `setfrequency`, `rssi`, `scan`, `sweep`, `waterfall`, `trace`, `receive`, `replay`, `record`, `load`, `clone`, `ear`, `jam` |
| **RFID / NFC** | `info`, `read`, `scan`, `scanner`, `dump`, `restore`, `write`, `clone`, `ndef`, `pwauth`, `nonce` |
| **RF24** | `setchannel`, `scan`, `sweep`, `waterfall`, `send`, `receive`, `jam` |
| **LCDTAP** | `status`, `cmddump`, `reset`, `save <file.bmp>` (ST7789, ILI9341, SSD1306, etc.) |
| **1-Wire / 2-Wire** | `scan`, `ds18b20`, `sle4442 init|dump|unlock|write|psc`, `sniff` |
| **Diagnostics** | `trace` (wire continuity), `rogue`, `crack`, `xflash`, `logic`, `jep106` |

---

## Related Projects

- **[RB-Pirate](https://github.com/reza-bakhshi/RB-Pirate)** — RP2350B hardware design.
- **[RB-Pirate-Firmware](https://github.com/reza-bakhshi/RB-Pirate-Firmware)** — Custom firmware build with merged Sub-GHz, RFID, RF24, and LCDTAP modes.
- **[RB-Pirate-RGB-HAT](https://github.com/reza-bakhshi/RB-Pirate-RGB-HAT)** — Optional RGB and user button add-on.

---

## Disclaimer

This project is strictly for **educational, prototyping, and authorized research purposes**. 
- Always ensure target circuits operate within safe voltage (1.65–5V) and current (max 300mA) limits before enabling power or pull-ups.
- Radio frequency (Sub-GHz and 2.4GHz) features such as jamming or code generation must only be operated in controlled, shielded laboratory environments in full compliance with local RF regulations and laws.
- The authors assume no liability for misuse, damaged components, or unauthorized hardware interactions.

---

## License

Released under the [MIT License](LICENSE). Based on the command architecture of Bus Pirate by Dangerous Prototypes.
