# Bus Pirate & RB-Pirate Complete Command Reference

Exhaustive command catalog for Bus Pirate 5, 5XL, 6 and the **RB-Pirate** fork (`RP2350B`, TF card storage).
Every command documented here is verified directly against the firmware source code.
On the device, `<command> -h` is authoritative and provides interactive help.

---

## 1. Global Commands (Available in HiZ and All Modes)

### Hardware IO & Power
| Command | Usage / Flags | Description |
| :--- | :--- | :--- |
| `W` | `W <volts> <mA> [-u <limit%>]` | Enable Programmable Power Supply (PPSU). Volts: 0.8–5.0V, Current: 0–500mA (default 300mA, 0=unlimited). `-u` sets undervoltage trip limit % (default 10%). |
| `w` | `w` | Disable power supply. |
| `P` | `P` | Enable onboard 10kΩ pull-up resistors (powered from VREF/VOUT). Required for open-drain buses. |
| `p` | `p` | Disable onboard pull-up resistors. |
| `v` | `v` | Single voltage and current measurement report across all pins and power rails. |
| `V` | `V` | Continuous real-time voltage/current monitoring (any key exits). |
| `a` | `a <pin>` | Set auxiliary pin output LOW (0V). Space syntax at prompt. |
| `A` | `A <pin>` | Set auxiliary pin output HIGH (VCC). Space syntax at prompt. |
| `@` | `@ <pin>` | Set auxiliary pin to input (HiZ) and read logic level (0 or 1). |
| `f` | `f <pin>` | Measure frequency once on odd pins (1, 3, 5, 7). |
| `F` | `F <pin>` | Continuous frequency measurement on odd pins (any key exits). |
| `G` | `G` | Frequency generator menu: set frequency (Hz/kHz/MHz), period (ns/us/ms), and duty cycle (%). |
| `g` | `g [pin]` | Disable PWM frequency generator globally or on a specific pin. |

### System & Configuration
| Command | Usage / Flags | Description |
| :--- | :--- | :--- |
| `i` | `i` | Board identity (RB-Pirate / BP6), firmware version, git hash, RP2350 chip info, serial number, storage size, and active mode status. |
| `c` | `c` | Configuration menu: language, ANSI color mode, ANSI toolbar status line, LCD screensaver, LED brightness/effects. Saved to `bpconfig.bp`. |
| `cls` | `cls` | Clear terminal screen and redraw prompt/status bar. |
| `d` | `d` | Toggle LCD display mode: 1 Default (pin voltages/labels), 2 Scope mode. |
| `o` | `o` | Number display format menu: 1 Auto*, 2 HEX, 3 DEC, 4 BIN, 5 ASCII. |
| `l` | `l` | Set bit order to MSB-first (default). |
| `L` | `L` | Set bit order to LSB-first. |
| `~` | `~` | Run factory self-test (HiZ mode only, all external wires/devices must be disconnected). |
| `reboot` | `reboot` | Soft reboot the microcontroller. |
| `$` | `$` | Jump to UF2 USB bootloader (RP2040/RP2350 USB mass-storage drive). |
| `ovrclk` | `ovrclk [-m MHz \| -k kHz] [-v mV]` | Overclock microcontroller CPU frequency and core voltage. |
| `smps` | `smps` | Configure switch-mode power supply parameters. |
| `bug` | `bug` | Microcontroller errata test and reproduction helper. |
| `otpdump` | `otpdump` | Dump RP2350 One-Time Programmable (OTP) memory. |
| `#` | `# <comment>` | Comment line (ignored by parser, useful in scripts). |

### Storage & Filesystem (TF / MicroSD Card)
| Command | Usage / Flags | Description |
| :--- | :--- | :--- |
| `ls` | `ls [path]` | List files and directories on the TF card. |
| `cd` | `cd <path>` | Change current working directory on the storage card. |
| `mkdir` | `mkdir <name>` | Create a new directory. |
| `rm` | `rm <file\|dir>` | Delete a file or empty directory. |
| `cat` | `cat <file>` | Display text file contents to the terminal. |
| `hex` | `hex <file> [-s start] [-b bytes] [-q]` | Hex dump file contents. `-s` start offset, `-b` byte count, `-q` quiet (raw hex without headers). |
| `dump` | `dump <file>` | Dump bus read data directly into a file. |
| `edit` | `edit <file>` | Full-screen terminal text editor on the TF card. |
| `hexedit`| `hexedit <file>` | Full-screen interactive hex editor for binary files. |
| `label` | `label <name>` | Set volume label for the storage card. |
| `format` | `format` | Erase and format storage card as FAT. (Destructive!) |

### Scripting & Automation
| Command | Usage / Flags | Description |
| :--- | :--- | :--- |
| `script` | `script <file>` | Execute commands line-by-line from a script file on storage. |
| `macro` | `macro [-f file] [-l] [id]` | Macro system: `-f` load macro file, `-l` list macros, `<id>` run macro. |
| `button` | `button <file>` | Assign a script file to execute when the physical user button is pressed. |
| `pause` | `pause` | Pause script execution and wait for user to press a key. |

### Engineering Diagnostics & Tools
| Command | Usage / Flags | Description |
| :--- | :--- | :--- |
| `logic` | `logic [start\|stop\|hide\|show\|nav] [-i] [-o oversample] [-f freq] [-d debug]` | Onboard follow-along logic analyzer. `start`/`stop` capture, `nav` inspect waveforms with arrow keys. |
| `toolbar` | `toolbar [enable\|disable]` | Enable or disable the live ANSI status bar. |
| `trace` | `trace` | Wire tracer: automatically tests continuity and shorts between all Bus Pirate pins. |
| `rogue` | `rogue` | Rogue probe testing / scanning tool. |
| `crack` | `crack` | Cryptographic cracking / brute-force helper. |
| `xflash` | `xflash` | Cross-flash utility for external microcontroller programming. |
| `jep106` | `jep106 <bank> <id>` | Lookup JEDEC 2-byte manufacturer ID (e.g. `jep106 0x00 0x2C` -> Micron). |
| `=` | `= <number>` | Convert number between HEX, DEC, and BIN format. |
| `\|` | `\| <number>` | Bit-reverse a number. |

### On-board Entertainment / Demos
`life`, `snake`, `2048`, `ttt` (Tic-Tac-Toe), `hangman`, `mines`, `bricks`, `drop4`, `fleet`, `worm`, `pcbrun`, `invaders`, `sigride`, `stkover`, `gates` (Logic gates simulator).

---

## 2. Bus Syntax Mini-Language

All manual bus operations in protocol modes use these tokens:

| Token | Meaning | Example |
| :--- | :--- | :--- |
| `[` or `{` | Bus START condition (assert CS in SPI; I2C Start; UART open; 1-Wire reset). | `[0xA0 0x00 [0xA1 r:4]` |
| `]` or `}` | Bus STOP condition (deassert CS; I2C Stop; UART close). | `[0x9F r:3]` |
| `>` | Execute bus commands without START. | `>0xAA 0x55` |
| `r` / `r:n` | Read 1 byte / $n$ bytes (up to 255). | `r:8` |
| `0xNN` / `NN` / `0bNN` | Write byte (hex, decimal, or binary). | `0x50` or `80` or `0b01010000` |
| `"text"` | Write ASCII string bytes directly to bus. | `"AT\r\n"` |
| `d` / `d:n` | Delay $n$ microseconds (default 1µs). | `d:100` |
| `D` / `D:n` | Delay $n$ milliseconds (default 1ms). | `D:10` |
| `:` | Repeat operator. | `0x00:16` (write 16 zeros) |
| `.n` | Partial bit count for reads/writes. | `r.4` (read 4 bits), `0x5A.4` |
| `v.<pin>` | Measure voltage of a pin inline during bus transaction. | `[0xA0 v.1 r]` |
| `a.<pin>` / `A.<pin>` / `@.<pin>` | Set pin LOW / HIGH / read logic inline during bus commands. | `a.0 [0x01] A.0` |
| `^` `/` `\` `-` `_` `.` | Bit-banging (2-Wire/3-Wire): tick clock / clock high / clock low / data high / data low / read bit. | `^ .` |

---

## 3. Protocol Mode Command References

Select modes with `m <mode>` (e.g. `m i2c`, `m spi`, `m subghz`).

### A. I2C (`m i2c`)
- **Pins**: `SDA ↔ SDA`, `SCL → SCL`, `GND`. Pull-ups `P` mandatory!
- **Commands**:
  - `scan`: 7-bit address search. Flags: `-v` (verbose chip identification).
  - `sniff`: Live I2C bus sniffer (up to 500 kHz). Flags: `-7` (7-bit address format), `-r` (raw bytes).
  - `i2c`: Generic register read/dump: `i2c dump -a 0x50 -w 1 -r 0x00 -b 64`.
  - `eeprom`: 24Cxx I2C EEPROM tool:
    - `eeprom list`: List supported chips (24X01 to 24XM02).
    - `eeprom dump -d 24x02 [-s start] [-b bytes]`: Dump contents to terminal.
    - `eeprom read -d 24x02 -f backup.bin [-v]`: Read EEPROM to binary file.
    - `eeprom write -d 24x02 -f file.bin [-v]`: Write file to EEPROM.
    - `eeprom erase -d 24x02 [-v]`: Erase EEPROM chip.
    - `eeprom test -d 24x02`: Full erase/write/verify diagnostic test.
  - `ddr4`: DDR4 SPD EEPROM tool:
    - `ddr4 probe`: Identify SPD chip.
    - `ddr4 dump [-s start] [-b bytes]`: Dump SPD memory (512 bytes).
    - `ddr4 read -f spd.bin` / `ddr4 write -f spd.bin`: Read/write SPD image.
    - `ddr4 lock -b <0-3>` / `ddr4 unlock`: Lock/unlock SPD write protection blocks.
    - `ddr4 crc -f file.bin` / `ddr4 patch -f file.bin`: Check or patch JEDEC CRC bytes 0–125.
  - `ddr5`: DDR5 SPD EEPROM tool:
    - `ddr5 probe` / `ddr5 dump` / `ddr5 read -f spd.bin` / `ddr5 write -f spd.bin` (1024 bytes).
    - `ddr5 lock -b <0-15>` / `ddr5 unlock -b <0-15>`: Lock/unlock SPD block.
    - `ddr5 crc -f file.bin`: Calculate/verify CRC for JEDEC blocks 0–7.
  - `usbpd`: AP33772S USB-PD sink controller:
    - `usbpd status`: Query available Power Delivery Profiles (PDO).
    - `usbpd request -p <idx> [-v mV] [-i mA]`: Request fixed or PPS profile.
    - `usbpd reset`: Hard reset PD connection.
  - `fusb302`: FUSB302 USB Type-C and PD controller helper.
  - `mpu6050`: Read MPU-6050 6-axis accelerometer/gyroscope.
  - Sensor demos: `sht3x`, `sht4x` (Sensirion temp/humidity), `si7021`, `ms5611` (barometric pressure), `tsl2561` (light), `tcs3472` (RGB color sensor).

---

### B. SPI (`m spi`)
- **Pins**: `MOSI → MOSI`, `MISO ← MISO`, `CS → CS`, `CLK → CLK`, `GND`.
- **Commands**:
  - `flash`: SPI NOR flash tool (uses SFUD/SFDP):
    - `flash probe`: Detect flash ID, manufacturer, and SFDP parameters.
    - `flash dump [-s start] [-b bytes] [-q] [-c]`: Dump to terminal (`-q` quiet, `-c` no paging).
    - `flash read -f flash.bin [-v]`: Dump flash to file.
    - `flash read -o -b <bytes> -f file.bin`: Force generic 0x03 read when chip unlisted.
    - `flash write -f flash.bin [-e] [-v]`: Program flash (`-e` erase first, `-v` verify).
    - `flash erase`: Chip erase.
    - `flash test`: Full erase/write/verify diagnostic test.
  - `eeprom`: SPI EEPROMs (25Cxx, AT25x, M95x, 93x Microwire):
    - `eeprom list` / `eeprom dump` / `eeprom read` / `eeprom write` / `eeprom erase`.
    - `eeprom protect -d 25x020 [-p bits] [-t]`: Read/update write-protect bits or test protection.
  - `sniff`: SPI bus sniffer using PIO (`spisnif.pio`).

---

### C. UART & CELL (`m uart`)
- **Pins**: `TX → RX`, `RX → TX`, `GND`.
- **Commands**:
  - `bridge`: Transparent USB-to-UART bridge (Bus Pirate button exits).
  - `gps`: Live NMEA GPS sentence decoder (decodes coordinates, altitude, satellites, fix).
  - `glitch`: Hardware glitching timing and trigger framework.
  - **CELL Modem Commands** (SIMCom / Quectel / 3GPP AT modems):
    - `cellmodem`: Probe modem, read manufacturer, model, IMEI, IMSI, firmware revision.
    - `cellnet`: Network registration (CREG/CEREG), signal quality (CSQ RSSI and BER).
    - `cellops`: List available network operators (`AT+COPS=?`) or configure operator.
    - `cellsim`: SIM card status, ICCID, PIN status.
    - `cellpin [-p pin]`: Enter SIM PIN or PUK code.
    - `cellbook`: Read or write modem phonebook entries.
    - `cellsms [-r \| -s <num> -m <msg>]`: Read inbox SMS or send SMS message.
    - `cellcall [-d <number> \| -h]`: Originate voice call or hang up (`-h`).
    - `cellussd -u "<code">`: Send USSD code query (e.g. `*100#`) and display reply.
    - `cellmode <mode>`: Set phone functionality level (full, flight mode, minimum).
    - `cellat "<cmd>"`: Send arbitrary raw AT command and display response.

---

### D. Half-Duplex UART (`m hduart`)
- **Pins**: `RXTX ↔ RXTX`, `GND`. Pull-ups `P` mandatory! RST on `IO2`.
- **Commands**:
  - `bridge [-s]`: Transparent bridge (`-s` suppresses local echo for smart card tools like pySim).
  - `{` / `}`: Drive RST pin on IO2 HIGH / LOW.

---

### E. 1-Wire (`m 1wire`)
- **Pins**: `OWD ↔ OWD`, `GND`. Pull-ups `P` mandatory!
- **Commands**:
  - `scan`: 1-Wire ROM search, prints 64-bit device addresses.
  - `ds18b20`: Read temperature from DS18B20 digital thermometer.
  - `eeprom`: Read/write/dump/erase 1-Wire EEPROMs (DS2431, DS2433).

---

### F. 2-Wire & Smart Cards (`m 2wire`)
- **Pins**: `SDA ↔ SDA`, `SCL → SCL`, `RST → RST`, `GND`. Pull-ups `P` mandatory!
- **Commands**:
  - `sniff`: 2-Wire bus sniffer.
  - `sle4442`: SLE4442 smart card tool:
    - `sle4442 init`: Read ATR (Answer to Reset).
    - `sle4442 dump`: Dump main memory (256 bytes).
    - `sle4442 unlock -p <0xFFFFFF>`: Unlock with 3-byte PSC code.
    - `sle4442 write -a <addr> -v <val>`: Write byte to memory.
    - `sle4442 psc -p <new_psc>`: Change security passcode.
    - `sle4442 protect`: Read/write write-protection memory.

---

### G. 3-Wire (`m 3wire`)
- **Pins**: `MOSI, MISO, CS, CLK, GND`.
- **Commands**:
  - Bit-level control with `^` (tick clock), `/` (clock high), `\` (clock low), `-` (data high), `_` (data low), `.` (read bit).

---

### H. JTAG (`m jtag`)
- **Pins**: Connect `IO0..IO7` to suspected target pins + `GND`.
- **Commands**:
  - `bluetag jtag -c <channels> [-d] [-v]`: Search for JTAG pinout (TDI, TDO, TCK, TMS, TRST).
  - `bluetag swd -c <channels> [-d] [-v]`: Search for SWD pinout (SWDIO, SWCLK).
  - `-d` disables pin pulsing for stubborn targets.

---

### I. SUBGHZ (`m subghz` — RB-Pirate / CC1101)
- **Pins**: CC1101 SPI (`SCK, MOSI, MISO, CS`) + `GDO0` on IO0 + `3.3V/GND`.
- **Commands**:
  - `setfrequency <kHz>`: Set tuning frequency (e.g. `433920`, `868350`, `315000`).
  - `rssi [-p]`: Instantaneous or peak-held (`-p`) RSSI.
  - `scan [-s start] [-e end] [-b step]`: Scan frequency bands for energy.
  - `sweep`: Multi-sample RF activity detector.
  - `waterfall`: Live ASCII waterfall display of spectrum over time.
  - `trace`: Terminal logic-analyzer trace of GDO0 pulse levels.
  - `receive`: Capture raw GDO0 pulse train and run protocol decoders.
  - `monitor`: Continuous live protocol decoding with deduplication.
  - `replay`: Replay captured pulse buffer via CC1101 TX.
  - `record <file.sub>`: Record raw pulse stream directly to Flipper `.sub` file on TF card.
  - `load <file.sub>`: Load and parse Flipper RAW or protocol key file.
  - `decode <file.sub>`: Inspect and decode `.sub` file without transmitting.
  - `clone`: Guided capture, decode, and save key file in one step.
  - `savekey <file.sub>`: Save last decoded frame as Flipper protocol key file.
  - `send <proto> <payload>`: Transmit protocol frame, Princeton payload, or BinRAW.
  - `burst`: Transmit pseudo-random RF jitter pulse bursts for testing.
  - `ear [-p pin]`: Map real-time RSSI to audible PWM tone on a buffered pin.
  - `jam`: Transmit jamming RF energy: 30µs pulse train or band-hopping (lab use only!).
  - `bruteforce`: Transmit all 4096 codes of 12-bit fixed-code protocol (Nice, Came, etc.).
  - `keyload <file>` / `keys` / `keyadd <name> <key>`: KeeLoq manufacturer decryption keys management.
  - `power [-d dBm]`: Set CC1101 transmit output power.
  - `bitrate [-b baud]`: Configure data rate (600–500000 baud).
  - `preset <name>`: Load or export CC1101 modulation presets.
  - `hop`: Frequency hopping monitor.
  - `txallow`: Transmit policy configuration (strict ISM bands or open).
  - `scanprofile`: Configure custom scan profile (bandwidth, data rate).
  - `info`: Display CC1101 radio status and register values.

---

### J. RFID / NFC (`m rfid` — RB-Pirate / PN532)
- **Pins**: PN532 HSU UART (`TX → RX`, `RX → TX`, `VCC 3.3V/5V`, `GND`).
- **Commands**:
  - `info`: Query PN532 firmware version and connection status.
  - `read`: Scan tag and display UID, type, and ATQA/SAK.
  - `scan`: Poll ISO14443A/B, FeliCa, and Jewel tags.
  - `scanner`: Bulk tag inventory: log every unique UID with ATQA/SAK.
  - `dump [-f file.bin]`: Dump full tag memory (MIFARE Classic 1K/4K, Ultralight, NTAG).
  - `restore -f file.bin`: Restore binary image to tag.
  - `write -b <block> -d <hex>`: Write 16-byte block, 4-byte page, or magic UID.
  - `clone`: Clone UID to Magic Card (Gen1A / Gen2 UID changeable tag).
  - `erase`: Erase tag user memory blocks to zero.
  - `ndef [-r \| -w]`: Read or write NDEF URI or Text record on NFC tags.
  - `pwauth`: NTAG/Ultralight-EV1 PWD_AUTH and GET_VERSION.
  - `nonce`: Collect MIFARE auth nonces for offline key recovery (crapto1 / mfkey32).
  - `transceive`: Select target and exchange raw frames or APDUs.
  - `jewel`: Read or write Jewel/Topaz static memory.
  - `forum3`: Read NFC Forum Type 3 (FeliCa) NDEF message.
  - `forum4`: Emulate NFC Forum Type 4 NDEF tag.
  - `tools`: Display libnfc utility equivalents and hardware limits.

---

### K. RF24 (`m rf24` — RB-Pirate / nRF24L01+)
- **Pins**: nRF24L01+ SPI (`SCK, MOSI, MISO, CS`) + `CE` + `VCC 3.3V` + `GND`.
- **Commands**:
  - `setchannel <ch>`: Set 2.4 GHz channel (0–125).
  - `scan [-n samples]`: Energy / carrier detection scan across 2.4 GHz channels.
  - `sweep`: Multi-channel energy sweep.
  - `waterfall`: ASCII spectrum waterfall over time.
  - `send <hex>`: Transmit RF24 packet payload.
  - `receive`: Listen for packets on configured address.
  - `jam <ch>`: Transmit continuous carrier / jamming bursts (lab use only).

---

### L. LCDTAP (`m lcdtap` — RB-Pirate / LCD Bus Sniffer)
- **Pins**: Parallel connection to LCD I2C or SPI lines.
- **Supported Controllers**: `ST7032`, `ST7789`, `ILI9341`, `SSD1306`, `SSD1331`, `KS0108`.
- **Commands**:
  - `status`: Show frame sync, line counts, and pixel dimensions.
  - `cmddump`: Dump captured LCD controller command stream.
  - `save <file.bmp>`: Export reconstructed framebuffer directly as BMP on TF card!
  - `reset`: Reset capture state machine.

---

### M. Enhanced Infrared (`m infrared`)
- **Commands**:
  - `load <file.ir>`: Load Flipper `.ir` file from TF card.
  - `send`: Transmit protocol packet or loaded code.
  - `record <file.ir>`: Record incoming IR signal to Flipper format.
  - `receive`: Live IR demodulator / protocol decoder.
  - `replay`: Replay last captured IR signal.
  - `jam`: Transmit continuous IR carrier disruption.
  - `devicebgone`: Blast power-off codes for TVs and projectors.
  - `tvbgone`: Classic TV-B-Gone power codes.
  - `remote`: Interactive terminal remote control interface.
  - `setprotocol`: Select IR protocol engine.
  - `config`: Configure TX modulation frequency and RX sensor.
  - `irtx` / `irrx`: Raw aIR packet transmit / receive.
  - `test`: Hardware IR loopback / self-test.

---

### N. Specialized Peripheral Modes
- **PS2 (`m ps2`)**:
  - `sniff`: Live PS/2 keyboard and mouse packet sniffer.
- **USB (`m usb`)**:
  - `sniff`: USB Low/Full-Speed packet sniffer via PIO.
- **I2S (`m i2s`)**:
  - `sine [Hz] [-s seconds]`: Generate sine test tone on I2S audio DAC.
  - `wav -f <file.wav>`: Play `.wav` audio file from TF card over I2S bus.
- **LED (`m led`)**:
  - WS2812, SK6812, APA102, SK9822 RGB LED control using bus syntax.
