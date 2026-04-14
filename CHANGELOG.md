# Changelog

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

All notable firmware and tool changes are documented here.

---

## v1.6.3 — 2026-04-14

Stability and privacy release on top of v1.6.2. No new tuning parameters, no wiring changes, no in-field action required beyond running the provisioning tool.

### Firmware

- **NMEA satellite-count safety clamp**: the NMEA GGA parser now caps the satellites-in-view field at 255 before passing it on. Guards against corrupt or spec-violating sentences from multi-constellation receivers with unusually high sat counts.
- **Watchdog margin during receiver config**: every u-blox `CFG-*` write-and-wait-for-ACK step now pats the independent watchdog on entry. The 20-step boot-time configuration burst no longer nibbles away at the watchdog budget on slow-responding receivers.
- **Spoofing-event logger robustness**: the on-board event writer now reports which slot it used (or explicitly signals "skipped"), so a debounced duplicate-write cannot corrupt unrelated events when the board exits dead-reckoning and backfills the trigger duration.

### Bootloader

- **Build-time anti-rollback safety net**: the bootloader now fails the build outright if the anti-rollback floor is missing from the build configuration, instead of silently defaulting to zero (which would have accepted any firmware version). Bit-field overflow in version encoding is likewise caught at build time.
- **Staged-update resumability policy documented**: bounded power-fail retry behaviour is now an explicit invariant (documented, not changed). No functional change for operators; matters only to developers pulling the source.

### Server

- **License key no longer in URL**: the licence-status lookup has a new `POST /api/v1/license-status` variant that takes the key in the request body. The landing-page self-service form uses the new path so keys stop appearing in nginx access logs. The legacy `GET ?key=…` form still works for older clients.
- **Audit IPs are XFF-aware**: the retention-sweep and PII-erase admin actions now record the real client IP via `X-Forwarded-For`, not the nginx reverse-proxy loopback address. Audit rows written before this release remain as-is.
- **Pin an older firmware version on activation**: `/api/v1/activate` now accepts an optional `version` field. The provisioning tool uses this when you've selected something other than "(latest)" in the version dropdown.

### Tools — AirDroper GNSS Filter app

- **Clean shutdown during provisioning**: closing the app window while an ST-Link write is in progress now kills the child `STM32_Programmer_CLI` cleanly, instead of leaving orphaned processes holding the SWD port.
- **Multi-adapter pre-check on Activate**: the Activate button now refuses to start if more than one ST-Link V2 is plugged in, with the same "unplug the others" dialog that Recovery has used since v1.6.0. Prevents the wrong board being re-provisioned when a lab bench has several adapters attached.
- **Version-pinned activations**: when you pick a non-latest version in the firmware dropdown, Activate now sends that choice to the server (matches what Update already did).

### Docs

- **Recovery guide** ([04_recovery.md](https://github.com/AirdroperUA/gnss-filter-user-docs/blob/main/04_recovery.md)): added gate-failure diagnostics and recovery recipes for anti-rollback reject, UID-binding reject, RDP-write-failure mid-provision, and hard-brick escalation. Developer-only reference; normal field use is unchanged.

---

## v1.6.2 — 2026-04-14

Receiver-compatibility and provisioning-resilience release. Completes the USB-C → ST-Link transition from v1.6.0.

### Firmware

- **u-blox F10 / M10 NAV-SAT auto-config**: newer u-blox generations (F10 series, M10 series) use the `CFG-VALSET` configuration interface and do not always respond to the legacy per-message enable. The filter now sends a `CFG-VALSET` profile at boot that enables `NAV-SAT` on the correct port at the correct rate. Spoofing detection signals that rely on per-satellite SNR and carrier-to-noise analysis now work out-of-the-box on F10/M10 receivers without a u-center pre-config step. No effect on M8/M9 or UM980.

### Tools / Provisioning

- **Provisioning recovers from write-protected sectors**: if flash erase fails because option-byte write-protection (`nWRP`) is active on the previous image, the provisioning tool now clears the protection and retries automatically. Previously these boards required a manual trip through STM32CubeProgrammer.
- **Power-cycle prompt is now blocking**: when the board needs a hard power-cycle mid-provision (e.g. after an option-byte change), the dialog now blocks the flow until you confirm the cycle completed. Prevents the race where the next write started against a half-re-enumerated target.
- **Bootloader USB-C CDC fully disabled**: `BOOTLOADER_PHASEC_ENABLE=0` is now permanent. Pins `PA11/PA12` are unconditionally available to the flight-controller GPS UART (USART6). This change was announced in v1.6.0; v1.6.2 removes the last code paths.
- **USB-C row removed from the app**: the old "(USB-C auto-detect)" port selector is gone. Activate, Update, and Recover all use the ST-Link V2 SWD path.

### Docs

- User-facing guides re-read and trimmed for the ST-Link-only flow. The [Self-Install Guide](10_self_install.md) and the firmware-update FAQ no longer mention the USB-C path.

---

## v1.6.1 — 2026-04-13

Reliability release. Patches three independent issues that surfaced in the field after v1.6.0. No configuration changes.

### Firmware

- **Bootloader → application handoff hardened**: on some boards, a firmware-validation failure followed by a retry could leave the application starting with stale NVIC interrupt state, with interrupts masked (`PRIMASK=1`), or with the `AHB2ENR` clock-enable register still configured for the bootloader's USB peripheral — symptoms were an instantly-frozen board with the status LED stuck off after the bootloader finished. The handoff now explicitly clears NVIC pending/enable bits, resets `AHB2ENR`, clears `PRIMASK` so interrupts are enabled when the app starts, and clears any latched fault flags.
- **Diagnostic GPS forwarding restored** (`FCGPS_FWD=1`): when the parameter `FCGPS_FWD` is set to `1`, the filter now bypasses the spoof guard in DR1 (dead-reckoning) and forwards the raw GPS stream to the flight controller. Intended for **diagnostic bench use only** — it defeats the whole point of the filter in flight. Default stays at `0`.

### Tools — AirDroper GNSS Filter app

- **Ctrl+V paste works under Cyrillic keyboard layouts**: the license-key field used to ignore Ctrl+V when the active keyboard layout was Ukrainian or Russian (the "V" keysym under those layouts is not `v`). The binding now triggers on the physical keycode, so paste works regardless of the currently-selected layout.

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
