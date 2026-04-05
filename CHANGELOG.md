# Changelog

All notable changes to the AirDroper GNSS Spoofing Filter firmware and
tooling are documented below.

---

## v1.5.5 — USB-C & Bootloader Upgrade (2026-04-05)

### Firmware
- Bootloader expanded from 32 KiB to 48 KiB (sectors 0-2); app now starts
  at 0x0800C000
- USB CDC support in bootloader via TinyUSB — firmware updates and log
  downloads over USB-C cable (no ST-Link or UART adapter needed)
- Dual-transport bootloader: auto-detects UART or USB CDC, first HELLO wins
- PLL clock init in bootloader (84 MHz system + 48 MHz USB)
- Initial provisioning via USB DFU (STM32 ROM bootloader, BOOT0 button)

### Provisioning tool (GUI)
- Connection mode selector: Auto-detect / ST-Link (SWD) / USB (DFU)
- Auto-detect new USB CDC COM port after board reset
- DFU provisioning: hold BOOT0, press RESET, flash via USB

### Documentation
- Added UM982 as supported receiver alongside UM980/UM981
- Removed green BlackPill board variant (known to differ from reference black PCB)
- Updated all docs for v1.5.5: app address 0x0800C000, 48 KiB bootloader
- Added day/night theme toggle to landing page and docs
- Added docs version selector for switching between past versions
- Interactive wiring checklist checkboxes
- Light/dark theme with dark as default

---

## v1.5.0 — SpoofAnalytics (2026-04-03)

### Firmware
- Spoofing event logging to on-board flash (EEPROM sector 5, ring buffer,
  330 events max)
- Each event records: timestamp, GPS coordinates, altitude, satellite
  count, HDOP, SNR min/max, detection reason, duration
- New Phase-C commands: `LOG_READ` (0x06) and `LOG_CLEAR` (0x07) for
  reading/clearing logs over UART

### License server
- `POST /api/v1/upload-logs` — receive spoofing event logs from boards
- `GET /api/v1/dashboard/events` — paginated event query per license key
- `GET /api/v1/dashboard/summary` — aggregate statistics per license key
- `GET /dashboard` — interactive cloud dashboard with Leaflet map,
  event timeline, and reason breakdown charts
- Single license creation now generates random keys from a prefix
  (no manual key entry required)
- Input validation: UID hex format, event count limits, pagination clamping
- XSS hardening on admin and dashboard HTML pages

### Provisioning tool (GUI)
- "Download Logs (UART)" button — reads events from board, uploads to
  cloud dashboard, clears on-board log
- Logs require license key to download (protects flight data if board is
  found by a third party)
- "View Dashboard" link after successful log upload

### Documentation
- New section in self-install guide: spoofing event logs and cloud dashboard
- Ukrainian translation of new sections

---

## v1.4.3 — ParamSaveFix (2026-03-24)

### Firmware
- Fixed EEPROM parameter save/restore bug that could lose tuning values
  across reboots
- Changed default DR1 lock time to 120 seconds
- Fixed MAVLink log message types for correct Mission Planner display
- Stable quadcopter flight-tested build

### Licensing system (new)
- Ed25519 firmware signing with Monocypher
- BLAKE2b stream encryption — per-device keys derived from board UID
- Phase-C encrypted UART update protocol (HELLO/BEGIN/DATA/END/ABORT)
- Bootloader with RDP Level 1, signature verification, and encrypted
  firmware install
- FastAPI license server with SQLite backend
- Binary patching of bootloader template (no recompilation per board)
- Provisioning GUI (tkinter) with ST-Link activate and UART update flows
- PyInstaller single-file .exe for Windows
- CI pipeline: firmware + bootloader builds, Python test suite
- Server deployment: DigitalOcean, nginx, Let's Encrypt, systemd

### Documentation
- Full user documentation set (EN + UK): wiring, setup, operation, tuning,
  cheat sheet, lab validation, receiver config, self-install, FAQ
- Developer documentation: CI/CD, firmware update guide, licensing system
  architecture, server deployment

---

## v1.4.2 — UM980Support (2026-03-09)

### Firmware
- Added Unicorecomm UM980 receiver support alongside u-blox
- `GNSS_TYPE` parameter: 0 = u-blox (default), 1 = UM980
- UM980 binary protocol parsing (BESTNAV, BESTSAT)
- UM980 auto-configuration command sequence
- Adjusted baud rate handling for UM980 (460800 default)

### Documentation
- Receiver configuration guide (`09_receiver_config.md`) with UM980 and
  u-blox command profiles
- ArduPilot `GPS_AUTO_CONFIG=0` requirement for UM980

---

## v1.4.1 (2026-03-07)

### Firmware
- Parameter hardening: bounds checking on all tunable parameters
- Boot delay parameter for delayed filter start after power-on

---

## v1.4.0 (2026-03-05)

### Firmware
- EEPROM-backed parameter storage with FNV-1a integrity check
- Full MAVLink parameter protocol: GET/SET/PARAM_VALUE with SYSID 42
- Live tuning from Mission Planner without reboot (most parameters)
- UBX baud rate parameter (`UBX_BAUD`)

---

## v1.3.0 (2026-02-04)

### Firmware
- SNR (signal-to-noise ratio) monitoring for spoofing detection
- SNR min/max/span metrics in MAVLink status messages
- CI pipeline setup with PlatformIO and GitHub Actions
- Phase-B bootloader linker script (app origin 0x08008000)

---

## v1.2.0 (2026-02-03)

### Firmware
- All configurable detection parameters exposed
- GNSS TX/RX pin swap option

---

## v1.1.0 (2026-02-03)

### Firmware
- Initial documentation set
- CAN node documentation

---

## v1.0.0 (2026-02-03)

### Firmware
- Initial release from f10n_spoofing_filter codebase
- u-blox UBX protocol parsing (NAV-PVT, NAV-SAT)
- DR0/DR1 state machine with configurable thresholds
- MAVLink telemetry forwarding to flight controller
- Event pulse output on PA8
- USART2 (PA2/PA3) for GNSS at 460800 baud
- USART1 (PA9/PA10) for FC MAVLink at 115200 baud
- STM32F401CC BlackPill V2.0 target
