# Bus Pirate & RB-Pirate Protocols, Wiring, and Electrical Notes

Complete hardware interface and pinout reference for Bus Pirate 5, 5XL, 6 and **RB-Pirate** (`RP2350B`, TF card storage).
Use alongside `SKILL.md` and `references/commands.md`.

---

## 1. Mode Interface Matrix

| Mode | Bus / Standard | Pins (Bus Pirate → Target) | Output Type | Pull-ups | Voltage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HiZ** | High Impedance | None | Disconnected | None | Safe idle (up to 5V) |
| **I2C** | Inter-Integrated Circuit | `SDA ↔ SDA`, `SCL → SCL`, `GND` | Open-drain | **Mandatory** (`P`) | 1.2V – 5.0V |
| **SPI** | Serial Peripheral Interface | `MOSI → MOSI`, `MISO ← MISO`, `CS → CS`, `CLK → CLK`, `GND` | Push-pull | Optional (for WP/HOLD) | 1.65V – 5.0V |
| **UART** | Asynchronous Serial / CELL | `TX → RX`, `RX ← TX`, `GND` | Push-pull | No | 1.65V – 5.0V (TTL, not RS232!) |
| **HDUART**| Half-Duplex Single-Wire UART | `RXTX ↔ RXTX`, `GND` (RST on IO2) | Open-drain | **Mandatory** (`P`) | 1.65V – 5.0V |
| **1WIRE** | Maxim/Dallas 1-Wire | `OWD ↔ OWD`, `GND` | Open-drain | **Mandatory** (`P`) | 2.8V – 5.0V |
| **2WIRE** | Generic 2-Wire / Smart Card | `SDA ↔ SDA`, `SCL → SCL`, `RST → RST`, `GND` | Open-drain | **Mandatory** (`P`) | 1.65V – 5.0V |
| **3WIRE** | 3-Wire Synchronous Serial | `MOSI, MISO, CS, CLK, GND` | Push-pull | No | 1.65V – 5.0V |
| **DIO** | Raw Digital I/O | Any IO pin (`IO0..IO7`), `GND` | Push-pull / HiZ | Configurable (`P`) | 1.65V – 5.0V |
| **LED** | Addressable LEDs | `SDO → DIN` (+ `SCL → CKI` for APA102), `GND` | Push-pull | No | 1.65V – 5.0V |
| **INFRARED**| Optical Infrared (38/56kHz) | `IRTX`, `IRRX` (demodulator/barrier), `GND` | Open-drain in, Push-pull out | No | 3.3V / 5.0V |
| **SUBGHZ**| CC1101 SPI Transceiver | `SCK, MOSI, MISO, CS`, `GDO0 (IO0)`, `3.3V, GND` | Push-pull SPI + interrupt | No | 3.3V (300–928 MHz) |
| **RFID** | PN532 NFC Module (HSU) | `TX → RX`, `RX ← TX`, `3.3V/5V`, `GND` | Push-pull UART (115200) | No | 3.3V / 5.0V (13.56 MHz) |
| **RF24** | nRF24L01+ 2.4GHz Radio | `SCK, MOSI, MISO, CS`, `CE (IO)`, `3.3V, GND` | Push-pull SPI + CE | No | 3.3V (2.4 GHz) |
| **LCDTAP**| Passive LCD Bus Sniffer | Parallel sniff on `SDA/SCL` or `CLK/MOSI/CS/DC` | Passive high-impedance | No | 1.65V – 5.0V |
| **PS2** | PS/2 Keyboard / Mouse | `IO0 (Clock)`, `IO1 (Data)`, `5V, GND` | Passive sniffer (PIO) | External / Pull-up | 5.0V |
| **USB** | USB Low / Full Speed | `IO0 (D+)`, `IO1 (D-)`, `GND` | Passive sniffer (PIO) | External | 3.3V |
| **I2S** | Inter-IC Sound Audio DAC | `IO0 (BCLK)`, `IO1 (LRCLK)`, `IO2 (DOUT)`, `GND` | Push-pull | No | 3.3V |
| **JTAG** | blueTag Pinout Finder | `IO0..IO7` to suspected target pins + `GND` | Push-pull test patterns | No | Match target rail via `W` |

---

## 2. Power & Pull-ups Architecture

- **Programmable Power Supply (PPSU)**:
  - Command: `W <volts> <mA> [-u <limit%>]` (e.g. `W 3.3 50`).
  - Output range: **0.80V to 5.00V**, adjustable in 10mV steps.
  - Current sensing & digital fuse: **0 to 500mA** (300mA continuous rated). Overcurrent trips PPSU automatically.
  - Back-power protection: An internal one-way valve prevents reverse current into the PPSU when target has its own supply.
- **Onboard Pull-up Resistors (`P`)**:
  - Value: 10kΩ on all buffered IO lines.
  - Power rail: Driven directly from the `VREF/VOUT` pin.
  - **Rule**: If `VREF/VOUT` has 0V (neither `W` enabled nor target rail connected), pull-ups do nothing. Always check `v` to verify pull-up voltage.
- **Open-drain rule**:
  - I2C, 1-Wire, 2-Wire, and HDUART devices can only pull low (`0`). They rely on pull-up resistors to pull high (`1`). Without pull-ups, reads return 0x00, fail ACKs, or report false devices at every address.

---

## 3. Detailed Hardware Wiring & Protocols

### I2C
- **Wiring**: `SDA ↔ SDA`, `SCL → SCL`, `GND ↔ GND`.
- **Pull-ups**: Enable `P` and set `W 3.3 50` (or connect target VCC to `VREF`).
- **Speed options**: 1 kHz to 1000 kHz (standard: 100 kHz, fast: 400 kHz*, fast+: 1000 kHz). Optional clock stretching.
- **Diagnostics**:
  - `scan` reports all addresses ACKed → missing pull-ups or shorted lines.
  - `scan` finds nothing → address shifted (Bus Pirate uses 7-bit addresses like `0x50`, shifted byte is `0xA0/0xA1`).

### SPI
- **Wiring**: `MOSI → MOSI`, `MISO ← MISO`, `CS → CS`, `CLK → CLK`, `GND ↔ GND`.
- **Clock modes**:
  - Speed: 1 kHz to 62.5 MHz (default 100 kHz).
  - Polarity: Idle LOW (CPOL=0*) or Idle HIGH (CPOL=1).
  - Phase: Leading edge (CPHA=0*) or Trailing edge (CPHA=1).
  - CS: Active LOW (`/CS`*).
- **EEPROM / Flash holding**: Many SPI chips require `WP` (Write Protect) and `HOLD` tied high to work.

### UART & Cellular
- **Wiring**: `TX → RX`, `RX ← TX`, `GND ↔ GND`.
- **TTL Levels**: 1.65V to 5.0V logic levels. Do NOT connect directly to RS-232 COM ports (±12V) without a level converter (MAX3232).
- **Cellular modems**: Cellular modules (SIMCom, Quectel) experience up to 2A burst current during RF transmission. **Always use an external 3.8V–4.2V supply** for the modem; share GND with Bus Pirate.

### SUBGHZ (CC1101 Radio Module)
- **Wiring**:
  - `SCK` → CC1101 SCK
  - `MOSI` → CC1101 MOSI
  - `MISO` → CC1101 MISO
  - `CS` → CC1101 CSN
  - `IO0 / GDO0` → CC1101 GDO0 (digital baseband pulse stream)
  - `VCC` → 3.3V (Bus Pirate `W 3.3 100`)
  - `GND` → Ground
- **Frequencies**: 300–348 MHz, 387–464 MHz, 779–928 MHz.
- **Modulation**: OOK / ASK, 2-FSK, 4-FSK, GFSK, MSK.

### RFID / NFC (PN532 Module)
- **Wiring (HSU UART mode: DIP switches SEL0=0, SEL1=0)**:
  - `TX` → PN532 RXD
  - `RX` → PN532 TXD
  - `VCC` → 3.3V or 5.0V (check module LDO regulator)
  - `GND` → Ground
- **Standard Protocol**: ISO/IEC 14443 Type A & B, FeliCa, ISO/IEC 18092 (NFCIP-1).

### RF24 (nRF24L01+ Radio)
- **Wiring**:
  - `SCK` → nRF24L01 SCK
  - `MOSI` → nRF24L01 MOSI
  - `MISO` → nRF24L01 MISO
  - `CS` → nRF24L01 CSN
  - `IO` → nRF24L01 CE
  - `VCC` → 3.3V (Strict 3.3V VCC! 5V inputs tolerated, but 5V power destroys the chip).
  - `GND` → Ground

### LCDTAP (Passive External Display Sniffer)
- **Wiring**:
  - Attach Bus Pirate probe clips in parallel to the running target board's display connector.
  - I2C Displays: `SDA`, `SCL`, `GND`.
  - SPI Displays: `CLK`, `MOSI`, `CS`, `DC` (Data/Command), `GND`.
- **Signal Quality**: Keep wires short (<10 cm) to prevent capacitive loading from disturbing high-speed SPI display data.

### PS/2 Sniffer (`m ps2`)
- **Wiring**:
  - `IO0` → PS/2 Clock
  - `IO1` → PS/2 Data
  - `GND` → Target Ground
  - Power: 5V rail from target or external supply.

### USB Sniffer Lite (`m usb`)
- **Wiring**:
  - `IO0` → USB D+
  - `IO1` → USB D-
  - `GND` → USB Shield / Ground
  - Speed: USB Low Speed (1.5 Mbps) and Full Speed (12 Mbps).

### I2S Audio (`m i2s`)
- **Wiring**:
  - `IO0` → BCLK (Bit Clock)
  - `IO1` → LRCLK / WCLK (Left/Right Word Clock)
  - `IO2` → DOUT (Serial Audio Data Out)
  - `GND` → Audio DAC Ground
