# Changelog

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

All notable firmware and tool changes are documented here.

---

## v1.6.0 — 2026-04-11

Security and reliability hardening release. Four parallel deep-review waves (R19–R22) across firmware, server, and bootloader. **No configuration changes — existing boards upgrade in place and keep working. No new tuning parameters, no wiring changes.**

### Firmware

- **Spoof-guard arming timer hardened**: the "stable fix for N seconds before arming" window is now measured in wall-clock time. Fixes an edge case where a stale GPS fix could arm the guard prematurely.
- **MAVLink parameter-dump latency insurance**: dumping all ~62 tuning parameters to a GCS (e.g. Mission Planner) no longer briefly starves the spoof guard — the dump now yields to the GNSS parser and watchdog every 8 parameters.
- **Post-rejoin guard rearm**: after exiting DR1 (dead-reckoning) back to normal tracking, the spoof guard now fully re-qualifies its arming window on every cycle instead of carrying the previous armed state forward. No user-visible behaviour change in normal operation — this is a semantic cleanup so the arming invariant always holds.
- **Stricter GCS parameter authentication**: `PARAM_SET` messages are now rejected if the sender's MAVLink system ID doesn't match the expected autopilot. If you run a GCS with a non-standard `SYSID_MYGCS`, verify it matches your autopilot before upgrading.
- **u-blox coordinate sanity guard**: guards against NaN / out-of-range latitude or longitude from corrupt NAV-PVT frames.
- **UM980 autobaud timing**: watchdog reload during the receiver autobaud probe. Fixes rare boot stalls on slow-responding UM980 units.
- **Anti-reverse-engineering build flags**: stripped symbols, link-time optimization, dead-code elimination, stack protector — makes the shipped binary harder to reverse-engineer.

### Server / Tools

- **Exact-pinned Python dependencies**: all server dependencies now pinned with `==` instead of `~=`. Eliminates patch-level drift between deploys.
- **License keys masked in audit logs**: the `gnss-license` audit log now stores only a fingerprint (`first4...last4#sha256[:12]`) instead of the full key. Existing logs are unaffected; new entries use the fingerprint format.
- **DNS-rebind hardening**: webhook challenge endpoint now resolves and validates target hostnames server-side.
- **Rate-limiter cleanup**: fixed a memory-usage edge case in the per-IP rate limiter where 429-rejected IPs could leave empty entries behind.
- **HTTPS enforcement on /health and /api**: direct HTTP traffic now returns 403 instead of falling through to the app layer.
- **Device registration fix**: tightened `require_owner` on the `/register-key` endpoint (body-parsing bug fix).

### Bootloader

- **USB-C firmware updates removed**: the bootloader no longer enumerates as a USB CDC device. Pins PA11/PA12 are reserved for flight-controller GPS UART (USART6). All firmware updates, recovery, and activation now use the **ST-Link V2 SWD** path only.
- Internal parity updates from the R19 hardening wave; anti-rollback floor stays at v1.5.5 so existing field units can accept this release.

### Tools

- **AirDroper GNSS Filter app**: the "(USB-C auto-detect)" port option and the **Download Logs** button have been removed. Activate, Update, and Recover all run through the ST-Link V2 wired to the 4-pin SWD header (3V3, GND, A14/SWCLK, A13/SWDIO).

### Logging

- **Log retrieval moved to the flight controller SD card**: spoofing detections are now emitted as MAVLink **STATUSTEXT** and **NAMED_VALUE_INT** messages and recorded by ArduPilot as `MSG` / `NVLI` dataflash entries in the `.bin` log on the FC's SD card. The on-board event log and its USB-based download flow no longer exist.

### Docs

- Rewrote the "Firmware updates" and "Spoofing event logs" sections in the [Self-Install Guide](#self-install) for the ST-Link-only update path and SD-card log retrieval.
- Updated the FAQ entries on firmware updates and log download to match.

---

## v1.5.5 — 2026-04-05

### Firmware

- **Confidence scoring**: new `DR_CONF` (0–100) from 8 weighted detection signals — SNR anomalies, pseudorange residuals, SNR temporal correlation, heading reversals, GDOP changes, GPS time drift, velocity-position mismatch, clock bias jump. Score adapts automatically when signals are unavailable (e.g. UM980 uses ~5 of 8).
- **Heading reversal detection**: triggers DR1 on sudden course flip inconsistent with IMU.
- **GPS time anomaly detection**: triggers DR1 when GPS time jumps unexpectedly.
- **Geo-fence** (`FENCE_RAD`): triggers DR1 if position drifts beyond a radius from the first fix (default 600 km, max 2000 km). Catches slow-drift spoofing.
- **South-hemisphere hard block**: instant DR1 when latitude goes below 0°. Now configurable via `HEMI_EN` parameter.
- **Clock bias jump detection** (u-blox only): uses NAV-CLOCK to detect receiver clock manipulation.
- **Velocity-position mismatch** (u-blox only): cross-checks reported velocity against position delta.
- **DR1 max duration** (`DR1_MAX_MS`): forces exit from DR1 after a configurable timeout. Useful for long-range missions.
- **USB-C firmware updates**: connect USB-C cable, press RESET — no extra hardware needed after initial flash.
- **USB-C log download**: spoofing logs can be downloaded over USB-C directly.
- **App boot fix**: corrected application vector table at 0x0800C000.
- **RDP1 re-enabled**: readout protection restored after v1.5.4 debugging.

### Server / Tools

- **SpoofEvent v2**: richer event format with confidence score and trigger breakdown.
- **KML/GPX export**: download spoofing events as KML (Google Earth) or GPX from the cloud dashboard.
- **Fleet anomaly detection**: dashboard flags unusual patterns across multiple boards.
- **Provisioning tool**: USB-C auto-detect mode — select "(USB-C auto-detect)" as port.

### Docs

- Added confidence score documentation with signal weight table.
- Added u-blox vs UM980 feature coverage table.
- Documented new DR1 triggers (heading, time, geo-fence, clock bias, velocity-position).
- Added `DR1_MAX_MS`, `FENCE_RAD`, `HEMI_EN` to tuning manual.

---

## v1.5.4 — 2026-04-04

### Firmware

- **Critical fix**: compiler constant-folded key sentinel checks, causing provisioning validation to always pass. Fixed with volatile barriers.
- **PLL init reorder**: moved PLL clock init before app validation for faster boot.
- **Detailed error codes**: added BEGIN BAD_METADATA diagnostic codes for easier debugging.

---

## v1.5.3 — 2026-04-04

### Firmware

- **Anti-clone UID binding**: firmware is now cryptographically locked to each board's unique hardware ID. Copying firmware to another board renders it non-functional.
- **Security hardening**: additional integrity checks in bootloader.

### Server / Tools

- **Landing page and docs site**: launched gps.airdroper.org with full documentation.
- **Desktop app (.exe)**: AirDroper GNSS Filter provisioning tool with GUI.
- **Docs version selector**: browse documentation for specific firmware versions.

---

## v1.5.0 — 2026-04-03

### Firmware

- **SpoofAnalytics event logging**: spoofing events are stored in on-board flash with timestamp, position, trigger reason, satellite count, and SNR data.
- **Log download**: events can be uploaded to the cloud dashboard via USB-UART or USB-C.

### Server

- **Cloud dashboard** (gps.airdroper.org/dashboard): web interface for viewing spoofing events, flight tracks, and board status.
- **EW interference map** (gps.airdroper.org/ew-map): live global GNSS interference map with ADS-B, marine AIS, air raid alerts, 61 known EW zones, crowdsourced reports, route risk assessment, Telegram alerts, and predictive model.
- **License server**: automated provisioning and firmware distribution.
- **Server hardening**: rate limiting, input validation, HTTPS enforcement.
