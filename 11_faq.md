# Frequently Asked Questions

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

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
Rover). The filter communicates via standard MAVLink2 telemetry.

### Which GNSS receivers work?

- **u-blox**: M8, M9, M10, F9, F10 families (`GNSS_TYPE=0`)
- **Unicore**: UM980, UM981 (`GNSS_TYPE=1`) — requires one-time setup, see [Receiver Config](#receiver-config)

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
Amazon, or electronics stores for ~$5. You can [buy a pre-flashed board](https://airdroper.org/product/gps-spoofing-filter/) or flash it yourself — see the [Self-Install Guide](#self-install).

### Can I use a different STM32 board?

No. The firmware is compiled specifically for the STM32F401CC BlackPill
pinout and memory layout.

### What baud rates are used?

| Link | Baud rate |
|------|-----------|
| GNSS ↔ STM32 | 460800 (default, auto-detected) |
| FC MAVLink ↔ STM32 | 115200 |
| FC GPS ← STM32 | 460800 |

### Do I need to power the STM32 separately?

No. It draws power from the FC telemetry UART or from USB. Make sure
all devices share a common ground. See the [Wiring Guide](#wiring) for details.

---

## Setup

### My FC shows "No GPS" or "GPS: not healthy"

1. Check wiring — TX and RX must be crossed (see the [Wiring Guide](#wiring))
2. Check that `SERIAL_BAUD` matches (460800 for GPS UART, 115200 for MAVLink)
3. Set `FCGPS_FWD=1` temporarily to bypass DR1 and verify data reaches the FC
4. For UM980: make sure `GPS_AUTO_CONFIG=0` in ArduPilot (see [Receiver Config](#receiver-config))

If still stuck, see the [Wiring Debug](#wiring-debug) guide for step-by-step troubleshooting.

### How do I know which GNSS_TYPE to use?

- If your receiver is u-blox (NEO-M8, NEO-M9, ZED-F9P, etc.): `GNSS_TYPE=0`
- If your receiver is Unicore UM980 or UM981: `GNSS_TYPE=1`

See [Setup & Flash](#setup-flash) for how to change this parameter.

### Do I need to configure my UM980 receiver?

Yes. The filter does **not** auto-configure the UM980. You must apply the
configuration profile via UPrecise before first flight. See
[Receiver Config](#receiver-config) for the exact commands.

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
- Mode/state: `ARM=... DR=... BLEND=... LAT=... LONG=...`
- GNSS summary: `data=... fix=... nav=... SATS=... SNR=...`

See the [Cheat Sheet](#cheat-sheet) for a quick reference on reading these messages.

### What does the B5 pin do?

It outputs a 3-second high pulse on each DR0→DR1 transition. You can
connect it to an LED, buzzer, or external logger to get a physical
indication when protection mode activates. See the [Wiring Guide](#wiring) for connection details.

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

Yes. Purchase a license key from the [store](https://airdroper.org/product/gps-spoofing-filter/) and follow the [Self-Install Guide](#self-install). Two options for initial provisioning:

- **USB-C (no extra hardware)**: Hold BOOT0, press RESET to enter DFU mode, then run the provisioning tool.
- **ST-Link V2 (~$3)**: Connect via SWD pins. Required if the board already has RDP1 protection (see below).

### Can I use my license on multiple boards?

No. Each license key activates **one board**. The firmware is locked to
that board's unique hardware ID.

### How do I update the firmware?

Connect a USB-C cable, select "(USB-C auto-detect)" as the port, and press RESET. The tool detects the board and installs the update automatically. You can also use a USB-UART adapter on PA9/PA10 if you prefer. See the update section in the [Self-Install Guide](#self-install).

### Can I re-provision a board that already has firmware?

If the board already has RDP1 (readout protection), you need to remove it first — this erases the flash. **USB DFU cannot remove RDP1** — this is a hardware limitation of the STM32 chip, not a bug. You need either:

- **ST-Link adapter** ($3-5): connect via SWD, the provisioning tool handles RDP removal automatically.
- **STM32CubeProgrammer GUI**: manually set Option Bytes > Read Out Protection = Level 0 (triggers mass erase), then re-provision via USB DFU.

### How do I download spoofing logs?

The easiest way is **USB-C** — just plug in a USB-C cable, select "(USB-C auto-detect)" as the port in the [AirDroper GNSS Filter](https://gps.airdroper.org/download/app) app, and press reset on the board. You can also use a USB-UART adapter if you prefer. Logs are uploaded to the [Cloud Dashboard](https://gnss-filter.online/dashboard). See the logs section in the [Self-Install Guide](#self-install).

### What if my board dies?

Contact support. We can deactivate the old board's UID so you can
use the same license on a new board.

### Can someone steal my firmware?

The flash is protected by readout protection — reading it back via the debug port triggers
a mass erase. The firmware is also encrypted with a per-board key, so even
if extracted, it wouldn't work on a different board.
