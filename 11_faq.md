# Frequently Asked Questions

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

---

## General

### What does this filter do?

It sits between your GPS receiver and flight controller. It monitors GPS
quality in real time and blocks GPS data from reaching the FC when it
detects anomalies like spoofing, jamming, or signal loss. The FC then falls
back to dead-reckoning (inertial navigation) until clean GPS returns.
See the [Device Overview](#device-overview) for a detailed explanation.

### Which flight controllers are supported?

Any ArduPilot-based FC running **ArduPilot 4.6.1 or later** (Copter, Plane,
Rover). The F401 and H743 UART builds communicate via standard MAVLink2
telemetry plus an FC GPS UART. The H743 DroneCAN build publishes native
DroneCAN GPS and does not use the FC serial ports.

### Which GNSS receivers work?

- **u-blox**: M8, M9, M10, F9, F10 families (`GNSS_TYPE=0`)
- **Unicore**: UM980, UM981, UM982 (`GNSS_TYPE=1`) — requires one-time setup, see [Receiver Config](#receiver-config)
- **Septentrio**: Mosaic X5 (`GNSS_TYPE=2`) — NMEA mode, requires one-time setup, see [Receiver Config](#receiver-config)

### Can I use it with PX4 or iNav?

Not currently. The filter's MAVLink integration is designed for ArduPilot.

### Which EW systems does it protect against?

All of them. The filter detects GPS spoofing and jamming based on signal
anomalies (position jumps, SNR patterns, altitude divergence, satellite
count drops), not by identifying specific EW hardware.

**Tested/designed against:**

- **Ukrainian:** Lima, Patelnia, Pokrova (GPS spoofing); Bukovel, Nota, Damba, Enclave (GNSS jamming); Dandelion, PARASOL, Piranha AVD 360 (drone suppression)
- **Russian:** Pole-21/Field-21, Shipovnik-Aero (GPS spoofing); R-330Zh Zhitel (GNSS jamming+spoofing); Krasukha-2/4 (radar jamming); Borisoglebsk-2, Leer-3, Murmansk-BN, Palantin (comms jamming); Repellent-1, Infauna (drone/IED suppression)
- **Belarusian:** Groza (GNSS jamming)

It also works against any future EW system that affects GNSS signals.
See [Device Overview — EW Systems Compatibility](#device-overview) for
a full table with frequencies and capabilities.

---

## Hardware

### What board do I need?

STM32F401CC BlackPill V2.0 (WeAct Studio). Available from AliExpress,
Amazon, or electronics stores for ~$5. You can [buy a pre-flashed board](https://airdroper.org/products/gps-spoofing-filter) or flash it yourself — see the [Self-Install Guide](#self-install).

For H743 DroneCAN, use a WeAct Studio MiniSTM32H743VITX plus a 3.3 V CAN
transceiver such as SN65HVD230. See the
[H743 DroneCAN Guide](13_h743_dronecan.md).

### Can I use a different STM32 board?

Only the supported board targets are documented. The firmware is compiled for
board-specific pinouts and flash layouts.

### Does the H743 support CAN directly?

The STM32H743 has an internal FDCAN peripheral, but it still needs an external
CAN transceiver. Connect `PB9/PB8` to a 3.3 V transceiver module, then connect
that module's `CANH/CANL/GND` to the flight controller CAN port. Do not connect
`PB8/PB9` directly to CANH/CANL.

### What baud rates are used?

| Link | Baud rate |
|------|-----------|
| GNSS ↔ STM32 | 460800 (default, auto-detected) |
| FC MAVLink ↔ STM32 | 115200 |
| FC GPS ← STM32 | 460800 |

H743 DroneCAN uses `1 Mbps` CAN on `PB8/PB9` through the transceiver.

### Do I need to power the STM32 separately?

F401 production boards should be powered from the aircraft wiring or SWD during
flashing, not from the BlackPill USB-C connector. WeAct H743 can use USB-C for
bench power/ROM DFU, but flight wiring still needs common ground between GNSS,
H743, CAN transceiver, and flight controller. See the [Wiring Guide](#wiring)
and [H743 DroneCAN Guide](13_h743_dronecan.md).

---

## Setup

### My FC shows "No GPS" or "GPS: not healthy"

1. Check wiring — TX and RX must be crossed (see the [Wiring Guide](#wiring))
2. Check that `SERIAL_BAUD` matches (460800 for GPS UART, 115200 for MAVLink)
3. Set `FCGPS_FWD=1` temporarily to force the FC GPS UART on, raw-forward GPS, and verify data reaches the FC, even before the filter accepts the fix. Return it to `0` before flight.
4. For UM980 or Mosaic X5: make sure the receiver is pre-configured and ArduPilot is not overwriting that profile (see [Receiver Config](#receiver-config))

If still stuck, see the [Wiring Debug](#wiring-debug) guide for step-by-step troubleshooting.

For H743 DroneCAN, `FCGPS_FWD` and FC serial checks do not apply. Check CAN
bitrate `1000000`, DroneCAN protocol on the correct FC CAN driver,
`GPS1_TYPE=9`, `PB9 -> TXD`, `PB8 <- RXD`, CANH/CANL/GND, bus termination, and
the H743 screen `WHY`/`PUB` rows.

### How do I know which GNSS_TYPE to use?

- If your receiver is u-blox (NEO-M8, NEO-M9, ZED-F9P, etc.): `GNSS_TYPE=0`
- If your receiver is Unicore UM980, UM981, or UM982: `GNSS_TYPE=1`
- If your receiver is Septentrio Mosaic X5 outputting NMEA: `GNSS_TYPE=2`

See [Setup & Flash](#setup-flash) for how to change this parameter.

### Do I need to configure my UM980 receiver?

Yes. The filter does **not** auto-configure the UM980. You must apply the
configuration profile via UPrecise before first flight. See
[Receiver Config](#receiver-config) for the exact commands.

### Do I need to configure my Mosaic X5 receiver?

Yes. The filter does **not** auto-configure Mosaic X5. Configure the receiver with Septentrio RxTools/Web UI so it outputs NMEA `GGA`, `RMC`, `GSA`, `GSV`, and `VTG` on the serial stream connected to STM32, then save the profile to boot.

### Do I need to configure my u-blox receiver?

No. The filter auto-configures u-blox receivers at boot. Just plug it in.

---

## Operation

### What is DR0 and DR1?

- **DR0** = normal mode. GPS data flows to the flight controller.
- **DR1** = protection mode. GPS data is blocked. The FC uses dead-reckoning.

See the [Device Overview](#device-overview) for more details.

### How fast does DR1 trigger?

Depends on the trigger type:
- **No fix / low satellites**: immediate
- **Position jump**: immediate on detection
- **EKF trip**: configurable delay via `EKF_TRIPMS` (default 0 = immediate)
- **SNR anomaly**: after `SNR_HOLDMS` hold time

See [Tuning](#tuning) to adjust these thresholds.

### How does the plane rejoin GPS after DR1?

The filter checks:
1. Satellite count >= `RJ_MIN_SATS`
2. HDOP <= `RJ_MAX_HD`
3. Conditions held for `RJ_STAB_MS`
4. Minimum DR1 time `DR_LOCK_MS` elapsed
5. (Optional) EKF healthy for `EKF_OKRJMS`

When all pass, DR0 is restored and GPS data flows again. See [Tuning](#tuning) for details on each parameter.

### What happens if the plane loses GPS for a long time?

The FC uses dead-reckoning (IMU + compass + airspeed). DR accumulates
drift over time, so the plane should be configured to return home or
loiter when GPS is lost. The filter has a GNSS recovery watchdog that
automatically tries to restart the GPS receiver.

### Can I see what the filter is doing during flight?

Yes. The filter sends status messages via MAVLink every 10 seconds
(configurable via `LOG_MS`). In Mission Planner's Messages tab you'll see:
- GNSS summary: `data=... fix=... nav=... SATS=... SNR=...`
- Mode/state: `ARM=... DR=... BLEND=... LAT=... LONG=...`

See the [Cheat Sheet](#cheat-sheet) for a quick reference on reading these messages.

On H743 DroneCAN v1, the filter does not send MAVLink status text because it
does not use an FC MAVLink serial link. Use the onboard screen and DroneCAN node
status instead. The screen shows filter OK/warn/no-OK, a `WHY` reason, FC node
health/mode, arm/safety state when broadcast, `STATE` from ArduPilot
NotifyState when available, GPS fix, publish gate, CAN counters, and firmware
version.

### Where do I download the Mission Planner parameter patch?

Download [AirDroper Mission Planner Params](https://gps.airdroper.org/download/mission-planner-mod). It installs parameter descriptions, ranges, units, option labels, and ready `.param` presets for the STM32 filter. Close Mission Planner before running the installer, then reopen Mission Planner and refresh the parameter list.

### What does the B5 pin do?

It outputs a 3-second high pulse on each DR0→DR1 transition. You can
connect it to an LED, buzzer, or external logger to get a physical
indication when protection mode activates. See the [Wiring Guide](#wiring) for connection details.

### What is the spoofing confidence score (DR_CONF)?

Starting with v1.5.5, the filter computes a 0–100 confidence score from up to
8 independent detection signals. Higher = more evidence of spoofing. The score
is sent as `DR_CONF` in MAVLink telemetry and logged in each spoofing event.

u-blox receivers use all 8 signals (SNR, pseudorange residual, SNR temporal
correlation, heading, GDOP, time, velocity-position, clock bias). Passive
NMEA receivers such as UM980 and Mosaic X5 use the signals available via NMEA (~5 of 8). The score adapts
automatically — unavailable signals are excluded from the weighted average.

### Do all detection features work with NMEA receivers?

Most features work with u-blox and passive NMEA receivers such as
UM980/UM981/UM982 and Mosaic X5. Three advanced signals are **u-blox only**
because they require UBX binary protocol data:

- **Pseudorange residual analysis** (from NAV-SAT)
- **GDOP sudden change detection** (from NAV-DOP)
- **Clock bias jump detection** (from NAV-CLOCK)

The core protections (position jump, altitude, SNR, heading, time, geo-fence)
work with both receiver classes.

### What are the new DR1_MAXMS and FENCE_RAD parameters?

- **DR1_MAXMS**: Forces exit from DR1 after this many milliseconds, even if
  GPS hasn't recovered. Default `0` = disabled (infinite latch). Useful for
  long-range missions where indefinite GPS blocking is worse than uncertain GPS.
- **FENCE_RAD**: Triggers DR1 if GPS reports a position more than this many
  meters from the first fix (max 2,000,000 m = 2000 km). Default `0` (disabled)
  — opt in by setting a non-zero radius. Catches slow-drift spoofing attacks.

### Can I export spoofing events to Google Earth?

Yes, via the flight controller's dataflash log. Pull the `.bin` log from the
FC's SD card (or download it over MAVFTP), open it in **Mission Planner** →
*DataFlash Logs* → *Review a Log*, then use *File* → *Create KML+GPX* to
export the flight track. The `MSG` lines beginning with `GNSS:` or `DR1:`
mark the spoofing events along that track, and the `NVLI` `DR_CONF` records
carry the per-event confidence score. The filter board itself stores
**no spoofing event logs** — the FC's SD-card dataflash is the single
source of truth (the on-board EEPROM ring buffer was removed in v1.6.8).

---

## UM980 Specific

### My UM980 shows red velocity/position in Mission Planner

Most likely causes:
1. **`GPS_AUTO_CONFIG` is enabled** (default) — ArduPilot overwrites your
   UM980 config with `MODE MOVINGBASE`, which is wrong for a single-antenna
   UAV. Set `GPS_AUTO_CONFIG=0`.
2. **Missing `MODE ROVER UAV`** in your UM980 config — apply the full profile
   from [Receiver Config](#receiver-config).

### What messages does ArduPilot need from the UM980?

Only three: **GNGGA**, **GNRMC**, and **AGRICA** — all at 5 Hz (period 0.2).
The driver does not parse GPGSA, GPGSV, GPGST, or any binary messages.

### Do I need to configure the UM980 every time I power it on?

No. The `SAVECONFIG` command at the end of the UPrecise profile saves
everything to the UM980's non-volatile flash. Configure once, fly forever.

---

## Licensing and Updates

### Can I install the firmware myself?

For H743 DroneCAN, use target-aware provisioning with
`--target h743_dronecan` and follow the
[H743 DroneCAN Guide](13_h743_dronecan.md). Unlocked H743 development builds
can also be flashed through USB-C ROM DFU.

Yes. Purchase a license key from the [store](https://airdroper.org/products/gps-spoofing-filter) and follow the [Self-Install Guide](#self-install). All F401 operations — initial activation, firmware updates, and recovery — use the **same ST-Link V2 adapter (~$3)** connected to the 4-pin SWD header (3V3, GND, A14/SWCLK, A13/SWDIO). **The F401 board has no functional USB path** — never plug any cable into the BlackPill's USB-C connector, including for power. PA11/PA12 (which carry the FC GPS UART) are physically the same lines as USB D-/D+, and any USB host signaling will block GPS forwarding to the flight controller.

### Can I use my license on multiple boards?

No. Each license key activates **one board**. The firmware is locked to
that board's unique hardware ID.

### How do I update the firmware?

For H743 DroneCAN, use the CLI target `h743_dronecan` or the desktop app
**Board target -> H743 WeAct DroneCAN** for production provisioning/update.
App version `2026.06.23.4+` can also update an already activated H743 through
**Update transport -> USB-C ROM DFU**. Readable boards get app+metadata updates;
RDP1-protected boards go through UID-short confirmation, USB DFU RDP removal,
mass erase, app+metadata+bootloader rewrite, and RDP1 relock. For unlocked
development boards, USB-C ROM DFU can flash `weact_mini_h743vitx_dronecan_usb`
or `weact_mini_h743vitx_dronecan_phaseb_app_usb`.

Wire an ST-Link V2 to the 4-pin SWD header (3V3 → 3V3, GND → GND, SWCLK → A14, SWDIO → A13), open the **AirDroper GNSS Filter** app, enter your license key, choose the firmware version if support asked you to test a specific build, and click **Update**. The app handles RDP removal, flashing, and re-protection automatically. See the update section in the [Self-Install Guide](#self-install).

### Can I re-provision a board that already has firmware?

If the board already has RDP1 (readout protection), you need to remove it first — this erases the flash. Connect an **ST-Link adapter** ($3–5) via SWD — the provisioning tool handles RDP removal automatically.

### How do I download spoofing logs?

Spoofing logs are no longer extracted from the filter board. As of firmware v1.6.0, every detection event is emitted as MAVLink **STATUSTEXT** and **NAMED_VALUE_INT** messages, which ArduPilot writes to the flight controller's SD card as standard `MSG` and `NVLI` dataflash records. Pull the `.bin` log from the SD card (or download it via MAVFTP / Mission Planner) and review it in Mission Planner or [UAV Log Viewer](https://plot.ardupilot.org). See the logs section in the [Self-Install Guide](#self-install).

### What if my board dies?

Contact support. We can deactivate the old board's UID so you can
use the same license on a new board.

### Can someone steal my firmware?

The flash is protected by readout protection — reading it back via the debug port triggers
a mass erase. The firmware is also encrypted with a per-board key, so even
if extracted, it wouldn't work on a different board.

---

## EW Interference Map

### What is the EW interference map?

A live web map at [gps.airdroper.org/ew-map](https://gps.airdroper.org/ew-map) showing global GNSS interference in real time. It combines data from multiple sources:

- **ADS-B aircraft data** (OpenSky) — detects interference by comparing barometric vs GPS altitude across 5 world regions
- **Marine AIS vessel data** — detects ships reporting GPS failures in the Baltic and beyond
- **Ukraine air raid alerts** — real-time per-oblast alert status
- **61 known EW zones** — static military interference zones worldwide, cross-referenced with live data
- **GDELT conflict events** — recent conflict signals that can correlate with EW activity
- **NASA FIRMS thermal anomalies** — fire/thermal detections that can help confirm active risk areas
- **Crowdsourced reports** — user-submitted interference sightings

The map is free and requires no login. Data refreshes automatically.

### Can I embed the EW map on my website?

Yes. Use the embeddable widget at `gps.airdroper.org/ew-map/embed` in an iframe:
```html
<iframe src="https://gps.airdroper.org/ew-map/embed" width="100%" height="500"></iframe>
```

### Can I get alerts when interference is detected?

Yes, three ways:
1. **Email/webhook** — subscribe at the bottom of the EW map page or via `POST /api/v1/ew-map/subscribe`
2. **Telegram** — message the bot (if configured) with `/subscribe`
3. **Public API** — register a free API key at `POST /api/v1/ew-map/register-key` (100 requests/day)

### Can I check interference risk for a flight route?

Yes. Use the route risk assessment API:
```
POST https://gps.airdroper.org/api/v1/ew-map/route-check
Body: {"waypoints": [[lat1, lon1], [lat2, lon2], ...]}
```
Returns per-segment risk scores (0–100) based on known zones, live ADS-B data, and air raid status.

### Does the map predict future interference?

Yes. The server builds time-of-day probability patterns from 7 days of historical data. Query predictions at `GET /api/v1/ew-map/predictions/now` for the current hour, or filter by zone/day/hour.
