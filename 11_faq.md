# Frequently Asked Questions

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

---

## General

### What does this filter do?

It sits between your GNSS receiver and flight controller. It monitors GPS
quality in real time and blocks GNSS data from reaching the FC when it
detects anomalies like spoofing, jamming, or signal loss. The FC then falls
back to dead-reckoning (inertial navigation) until clean GPS returns.

### Which flight controllers are supported?

Any ArduPilot-based FC running **ArduPilot 4.6.1 or later** (Copter, Plane,
Rover). The filter communicates via standard MAVLink2 telemetry.

### Which GNSS receivers work?

- **u-blox**: M8, M9, M10, F9, F10 families (`GNSS_TYPE=0`)
- **Unicore**: UM980, UM981 (`GNSS_TYPE=1`)

### Can I use it with PX4 or iNav?

Not currently. The filter's MAVLink integration is designed for ArduPilot.

---

## Hardware

### What board do I need?

STM32F401CC BlackPill V2.0 (WeAct Studio). Available from AliExpress,
Amazon, or electronics stores for ~$5.

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
all devices share a common ground.

---

## Setup

### My FC shows "No GPS" or "GPS: not healthy"

1. Check wiring — TX and RX must be crossed (see `02_wiring.md`)
2. Check that `SERIAL_BAUD` matches (460800 for GPS UART, 115200 for MAVLink)
3. Set `FCGPS_FWD=1` temporarily to bypass DR1 and verify data reaches the FC
4. For UM980: make sure `GPS_AUTO_CONFIG=0` in ArduPilot (see `09_receiver_config.md`)

### How do I know which GNSS_TYPE to use?

- If your receiver is u-blox (NEO-M8, NEO-M9, ZED-F9P, etc.): `GNSS_TYPE=0`
- If your receiver is Unicore UM980 or UM981: `GNSS_TYPE=1`

### Do I need to configure my UM980 receiver?

Yes. The STM32 does **not** auto-configure the UM980. You must apply the
configuration profile via UPrecise before first flight. See
`09_receiver_config.md` for the exact commands.

### Do I need to configure my u-blox receiver?

No. The STM32 auto-configures u-blox receivers at boot. Just plug it in.

---

## Operation

### What is DR0 and DR1?

- **DR0** = normal mode. GPS data flows to the flight controller.
- **DR1** = protection mode. GPS data is blocked. The FC uses dead-reckoning.

### How fast does DR1 trigger?

Depends on the trigger type:
- **No fix / low satellites**: immediate
- **Position jump**: immediate on detection
- **EKF trip**: configurable delay via `EKF_TRIPMS` (default 0 = immediate)
- **SNR anomaly**: after `SNR_HOLDMS` hold time

### How does the plane rejoin GPS after DR1?

The filter checks:
1. Satellite count >= `RJ_MIN_SATS`
2. HDOP <= `RJ_MAX_HD`
3. Conditions held for `RJ_STAB_MS`
4. Minimum DR1 time `DR_LOCK_MS` elapsed
5. (Optional) EKF healthy for `EKF_OKRJMS`

When all pass, DR0 is restored and GPS data flows again.

### What happens if the plane loses GPS for a long time?

The FC uses dead-reckoning (IMU + compass + airspeed). DR accumulates
drift over time, so the plane should be configured to return home or
loiter when GPS is lost. The filter has a GNSS recovery watchdog that
sends hot/cold restart commands to the receiver.

### Can I see what the filter is doing during flight?

Yes. The filter sends status messages via MAVLink every 10 seconds
(configurable via `LOG_MS`). In Mission Planner's Messages tab you'll see:
- Mode/state: `ARM=... DR=... BLEND=... LAT=... LONG=...`
- GNSS summary: `data=... fix=... nav=... SATS=... SNR=...`

### What does the B5 pin do?

It outputs a 3-second high pulse on each DR0→DR1 transition. You can
connect it to an LED, buzzer, or external logger to get a physical
indication when protection mode activates.

---

## UM980 Specific

### My UM980 shows red velocity/position in Mission Planner

Most likely causes:
1. **`GPS_AUTO_CONFIG` is enabled** (default) — ArduPilot overwrites your
   UM980 config with `MODE MOVINGBASE`, which is wrong for a single-antenna
   UAV. Set `GPS_AUTO_CONFIG=0`.
2. **Missing `MODE ROVER UAV`** in your UM980 config — apply the full profile
   from `09_receiver_config.md`.

### What messages does ArduPilot need from the UM980?

Only three: **GNGGA**, **GNRMC**, and **AGRICA** — all at 5 Hz (period 0.2).
The driver does not parse GPGSA, GPGSV, GPGST, or any binary messages.

### Do I need to configure the UM980 every time I power it on?

No. The `SAVECONFIG` command at the end of the UPrecise profile saves
everything to the UM980's non-volatile flash. Configure once, fly forever.

---

## Licensing and Updates

### Can I install the firmware myself?

Yes. Purchase a license key from the store and follow the self-install
guide (`10_self_install.md`). You'll need an ST-Link V2 programmer (~$3).

### Can I use my license on multiple boards?

No. Each license key activates **one board**. The firmware is locked to
that board's unique hardware ID.

### How do I update the firmware?

After the initial flash, updates use a USB-UART adapter connected to
PA9/PA10 (no ST-Link needed). See the update section in `10_self_install.md`.

### What if my board dies?

Contact support. We can deactivate the old board's UID so you can
use the same license on a new board.

### Can someone steal my firmware?

The flash is protected by RDP Level 1 — reading it back via SWD triggers
a mass erase. The firmware is also encrypted with a per-board key, so even
if extracted, it wouldn't work on a different board.
