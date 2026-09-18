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
DroneCAN GPS and has no physical FC serial ports. Instead, `v0.2.0+` carries
OpenIPC camera MAVLink2 on DroneCAN S1/index `0` and the filter's MAVLink2 plus
returning FC telemetry on S2/index `1`.

H743 DroneCAN `v0.5.30+` explicitly requests `AUTOPILOT_VERSION` and fails
closed if the FC does not answer or reports a version older than 4.6.1:
`Fix2/Auxiliary` are suppressed immediately. The 15-second grace period delays
only `FC VERSION UNKNOWN` / `AUTOPILOT_VERSION REQUIRED` (or `FIRMWARE TOO OLD`
/ `UPDATE TO ARDUPILOT 4.6.1+`) and hard fault processing; it never permits GPS
while identity is unknown or unsupported.

### Which GNSS receivers work?

- **u-blox**: M8, M9, M10, F9, F10 families (`GNSS_TYPE=0`)
- **Unicore**: UM980, UM981, UM982 (`GNSS_TYPE=1`) — requires one-time setup, see [Receiver Config](#receiver-config)
- **Septentrio**: Mosaic X5 (`GNSS_TYPE=2`) — H743 DroneCAN can use SBF; UART builds use NMEA, see [Receiver Config](#receiver-config)

### Can I use it with PX4 or iNav?

Not currently. The filter's MAVLink integration is designed for ArduPilot.

### Which EW systems does it protect against?

Protection is determined by the anomaly an installation can observe, not the
name of the transmitting system. The filter can react to position/time jumps,
receiver spoof verdicts, SNR patterns, altitude-rate divergence, and fix or
satellite loss when those inputs are available. It does **not** guarantee
detection of every EW system, a gradual internally consistent takeover, or an
attack already present when the boot anchor is established.

The following systems illustrate relevant threat classes; inclusion is not a
claim that every model/configuration has been reproduced in a controlled test:

- **Ukrainian:** Lima, Patelnia, Pokrova (GPS spoofing); Bukovel, Nota, Damba, Enclave (GNSS jamming); Dandelion, PARASOL, Piranha AVD 360 (drone suppression)
- **Russian:** Pole-21/Field-21, Shipovnik-Aero (GPS spoofing); R-330Zh Zhitel (GNSS jamming+spoofing); Krasukha-2/4 (radar jamming); Borisoglebsk-2, Leer-3, Murmansk-BN, Palantin (comms jamming); Repellent-1, Infauna (drone/IED suppression)
- **Belarusian:** Groza (GNSS jamming)

See [Device Overview — EW Systems Compatibility](#device-overview) for
a threat-reference table, and complete the lab-validation checklist for the
actual receiver and airframe before flight.

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
| OpenIPC camera ↔ H743 | 115200 (3.3 V MAVLink2 UART) |
| H743 DroneCAN S1/S2 virtual ports | 115200 metadata (`BD=115`) |

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
the H743 screen `WHY`/`PUB` rows. If GPS works but camera or filter MAVLink does
not, also check `CAN_Dx_UC_SER_EN=1`, S1 node `42`/index `0`/baud `115`/protocol
`2`, and S2 node `42`/index `1`/baud `115`/protocol `2`.

### How do I know which GNSS_TYPE to use?

- If your receiver is u-blox (NEO-M8, NEO-M9, ZED-F9P, etc.): `GNSS_TYPE=0`
- If your receiver is Unicore UM980, UM981, or UM982: `GNSS_TYPE=1`
- If your receiver is Septentrio Mosaic X5: `GNSS_TYPE=2`. Use the SBF profile on H743 DroneCAN `v0.1.9+`; use NMEA on UART builds.

See [Setup & Flash](04_setup_and_flash.md) for how to change this parameter.

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
- **No fix**: at least 3 distinct invalid epochs spanning at least 600 ms
- **Low satellites**: 3 distinct low-count epochs spaced at least 200 ms
  apart, using the peak count from a rolling approximately 3-second window
- **Position jump**: immediate on detection
- **EKF trip**: every bad category, including `GPS_GLITCHING` and post-healthy
  `UNINITIALIZED`, needs at least 2 newly decoded reports spanning
  `EKF_TRIPMS`; both released targets default to 500 ms, and a tuned zero still
  keeps the two-report minimum
- **SNR anomaly**: after `SNR_HOLDMS` hold time

See [Tuning](#tuning) to adjust these thresholds.

### How does the plane rejoin GPS after DR1?

The filter checks:
1. Satellite count >= `RJ_MIN_SATS`
2. HDOP <= `RJ_MAX_HD`
3. Conditions held for `RJ_STAB_MS`
4. Minimum DR1 time `DR_LOCK_MS` elapsed
5. On H743, the independent multi-evidence recovery quorum passes

When all pass, DR0 is restored and GPS data flows again. See [Tuning](#tuning) for details on each parameter.

Legacy parameters `RJ_REQEKF` and `EKF_OKRJMS` are retained only for schema
compatibility. F401 v1.6.26+ and H743 v0.5.5+ report them as zero and ignore
writes, including non-zero values saved by older releases; they do not gate recovery.

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

On H743 DroneCAN `v0.2.0+`, filter status uses S2/index `1`. Configure that
virtual port to receive `STATUSTEXT`/`NAMED_VALUE` and return FC telemetry. The
onboard screen and DroneCAN node status remain useful supplementary checks: the
screen shows filter OK/warn/no-OK, a `WHY` reason, FC node health/mode,
arm/safety state when broadcast, `STATE` from ArduPilot NotifyState when
available, GPS fix, publish gate, CAN counters, and firmware version. Camera
S1/index `0` and filter S2/index `1` remain active in DR1.

### Where do I download the Mission Planner plugin and parameter package?

Download [AirDroper Mission Planner Mod](https://gps.airdroper.org/download/mission-planner-mod). It installs the spoofing-telemetry map plugin plus descriptions and ready `.param` presets for the STM32 filter and flight controller. Close Mission Planner before running the installer, then reopen it and refresh the parameter list. Live red/orange positions and the three-axis intersection require a second direct USB-C connection to the H743; the open purple RF axis can use normal FC telemetry.

### What does the B5 pin do?

It outputs a 3-second high pulse on each DR0→DR1 transition. You can
connect it to an LED, buzzer, or external logger to get a physical
indication when protection mode activates. See the [Wiring Guide](#wiring) for connection details.

### What is the spoofing confidence score (DR_CONF)?

Starting with v1.5.5, the filter computes a 0–100 confidence score from up to
10 distinct evidence rows. Higher = more evidence of spoofing. Only the
receiver `SEC-SIG` verdict and barometric vertical-rate row are independent of
attacker-shaped GNSS content. The score
is sent as `DR_CONF` in MAVLink telemetry and logged in each spoofing event.

| Signal | Weight | Availability |
|--------|--------|--------------|
| Barometer-vs-GNSS vertical-rate divergence | 20 | DroneCAN build with fresh FC barometer telemetry and GNSS vertical velocity |
| SNR span anomaly | 20 | All supported receiver modes with fresh SNR/C/N0 |
| Receiver spoof verdict (`SEC-SIG`) | 25 | H743 with a supported u-blox only |
| Pseudorange residual stddev | 15 | u-blox `NAV-SAT` only |
| SNR temporal correlation | 12 | u-blox, partial passive NMEA, Mosaic SBF |
| Heading reversal | 12 | All supported receiver modes |
| GDOP sudden change | 8 | u-blox `NAV-DOP` only |
| GPS time sanity | 12 | All supported receiver modes |
| Velocity-position consistency | 10 | All; partial on passive NMEA |
| Clock bias jump | 11 | u-blox and Mosaic SBF |

The score adapts automatically: unavailable target-, transport-, and
protocol-specific rows are excluded from the weighted average.

### Do all detection features work with NMEA receivers?

Most features work with u-blox and passive NMEA receivers such as
UM980/UM981/UM982 and Mosaic X5. Three advanced rows use UBX binary data:

- **Pseudorange residual analysis** (from NAV-SAT)
- **GDOP sudden change detection** (from NAV-DOP)
- **Clock bias jump detection** (from NAV-CLOCK)

H743 DroneCAN Mosaic SBF restores binary C/N0 temporal and clock-bias coverage,
but not pseudorange residual or GDOP-jump confidence scoring.

The receiver-spoof verdict is a separate H743-only `SEC-SIG` row and therefore
requires a supported u-blox. Barometric vertical-rate divergence is a
DroneCAN-build row and instead depends on fresh FC barometer telemetry plus
GNSS vertical velocity, regardless of receiver protocol.

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
ArduPilot's driver does not parse GPGSA, GPGSV, GPGST, or UM980 binary
diagnostics. The STM32 parser is separate: it parses GGA/RMC, ignores AGRICA
and proprietary binary diagnostics, and can optionally parse GSV for SNR.
The documented GGA/RMC/AGRICA deployment profile therefore shows `SNR=NA`;
optional GSV is additional evidence and is not required for DR1 recovery.

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
App version `2026.08.02.1+` can also update an already activated H743 through
**Update transport -> USB-C ROM DFU**. It validates the RDP option byte and
always mass-erases and installs the complete validated app+metadata+bootloader
bundle. RDP1 boards also require UID-short confirmation, verified RDP0 after
unlock, and a physical UID re-read. Success is reported only after an independent
option-byte read verifies final RDP1. For unlocked
development boards, USB-C ROM DFU can directly flash only the standalone
`weact_mini_h743vitx_dronecan_usb` environment. Phase-B environments are
build-only templates and intentionally refuse direct upload; use the
provisioning app for a UID-bound secure update.

Wire an ST-Link V2 to the 4-pin SWD header (3V3 → 3V3, GND → GND, SWCLK → A14, SWDIO → A13), open the **AirDroper GNSS Filter** app, enter your license key, confirm the active qualified firmware shown for the selected board target, and click **Update**. The app handles RDP removal, flashing, and re-protection automatically. Inactive candidates and revoked releases are never offered. See the update section in the [Self-Install Guide](#self-install).

### Can I re-provision a board that already has firmware?

If the board already has RDP1 (readout protection), you need to remove it first — this erases the flash. Connect an **ST-Link adapter** ($3–5) via SWD — the provisioning tool handles RDP removal automatically.

### How do I download spoofing logs?

Spoofing logs are no longer extracted from the filter board. As of firmware v1.6.0, every detection event is emitted as MAVLink **STATUSTEXT** and **NAMED_VALUE_INT** messages, which ArduPilot writes to the flight controller's SD card as standard `MSG` and `NVLI` dataflash records. H743 DroneCAN `v0.2.0+` carries these messages on S2/index `1`. Pull the `.bin` log from the SD card (or download it via MAVFTP / Mission Planner) and review it in Mission Planner or [UAV Log Viewer](https://plot.ardupilot.org). See the logs section in the [Self-Install Guide](#self-install).

### What if my board dies?

Contact support. We can deactivate the old board's UID so you can
use the same license on a new board.

### Can someone steal my firmware?

RDP Level 1 makes a normal debug-port read attempt trigger mass erase, and the
production application is signed and bound to the board's full hardware UID.
Encrypted update packages are also device-specific where that update path is
supported. These controls make casual extraction and copying fail closed and
raise the cost of analysis; they do not make advanced physical reverse
engineering impossible.

---

## Fuel estimation

### Can the filter tell me how much fuel I have left?

It can estimate it, from H743 DroneCAN `v0.5.28+`. It works out what your
propeller must be absorbing from the engine RPM your flight controller already
sends, and reports that to ArduPilot as an EFI device — so the figure shows up
in your GCS and your logs with no extra sensor and no extra wiring.

It is an estimate, not a measurement. There is no flow meter and no tank
sensor anywhere in the path. On an aircraft with no fuel gauge it will be the
only fuel indication you have, so it is deliberately built to read HIGH rather
than low, and it stays advisory until you calibrate it against one weighed
flight. See "Calibrating the fuel estimate" in [Tuning](06_tuning.md).

### Why does my fuel figure read far too high?

Because it is supposed to, until calibrated. Uncalibrated it reads roughly
1.2–2x high by design — the underlying propeller coefficient carries deliberate
margin, because under-reporting fuel is what stops an engine and over-reporting
only lands you early. One weighed flight and one `FUEL_TRIM` value brings it to
10–20%. Expect to end up around 0.5–0.9.

### My fuel total did not reset after refuelling

Write `FUEL_CAPG`. That is the only thing that zeroes the running total, and
it is intentional — the total now survives a mid-flight reboot, so it cannot
also reset itself whenever the board restarts. Write it after every refuel,
even if the tank size has not changed. You will see
`FUEL_CAPG written - fuel total zeroed`. The write is normally accepted only
after fresh stopped-engine quorum: disarmed, valid zero RPM, and closed
throttle. A manually started engine whose GPIO pickup reports exact `-1/-1`
before its first start may use the narrowly gated cold declaration described
below. If the
numerical capacity changed, that message confirms only the runtime reset: EFI
remains silent until the asynchronous journal save reports `Tune saved`.
`Tune save failed` leaves the total LOST and must not be treated as recovery.
Use a positive weighed mass; never write zero as a placeholder. H743 DroneCAN
v0.5.31+ suppresses ICE Status for zero/non-finite capacity, while firmware
through v0.5.30 could expose fresh zero-consumption EFI after a zero write.
Version v0.5.31 itself is a retired ambiguous development identity; use v0.5.32
or later.

Set `FUEL_DENS` before `FUEL_CAPG`. Density writes require the same normal
quorum or a ready cold manual-start declaration; they do not consume that
one-shot. An actual change marks the total LOST, cancels any older
pending capacity commit, and blocks capacity writes with
`FUEL_CAPG blocked: wait for FUEL_DENS save` until the density journal save is verified. A failed
save stays blocked/LOST. `Tune saved` clears that block but does not restore EFI;
then a subsequent stop-authorized positive `FUEL_CAPG` establishes a fresh zero.

### Why does an engine that is off at power-up show RPM `-1` and max burn?

ArduPilot's GPIO pulse RPM backend sends the exact MAVLink pair
`RPM1=-1,RPM2=-1` when a stopped pickup has no pulse quality. That means
**unavailable**, not a measured zero. The filter deliberately keeps it invalid
globally, because treating `-1` as zero after a sensor wire breaks could stop
fuel accounting while the engine is running.

For the pre-start case only, H743 DroneCAN v0.5.32 provides a one-shot operator
declaration. Fully remove power, make a genuine cold POR, and keep the FC
positively identified as a supported ArduPilot family/version, freshly
DISARMED, both RPM fields exactly `-1`, and throttle
freshly closed for at least 3 continuous seconds. Then write a **positive
weighed** `FUEL_CAPG` when re-establishing a LOST/unconfigured total from
positively known fuel aboard, or after an actual refuel. With a LOST or
unconfigured total, readiness says `Cold manual-start ready: write positive FUEL_CAPG`.
If a trustworthy total survived, it instead says
`Cold OFF ready; write FUEL_CAPG only if refuelled`; do not destroy the retained total merely to
silence the conservative latch. A valid retained backup controls the old total,
not physical-stop eligibility. An accepted positive CAPG clears the RAM engine
latch and consumes the one-shot. Zero is rejected with
`Cold FUEL_CAPG must be positive weighed fuel`. You may write
`FUEL_DENS` first under the same evidence; it does not consume the one-shot,
but after a real change wait for `Tune saved` before CAPG.

Do not arm, open throttle, or turn the engine before CAPG: any armed report,
RPM `>=1`, or open-throttle evidence revokes the declaration. An observed FC
peer/session reset also revokes it. Every H743 reset restores the conservative
may-run latch; reset button, watchdog, brownout, or warm reboot is not enough
to retry—perform a true all-power removal and satisfy cold eligibility again.
After the engine has run, exact `-1/-1` remains sensor loss and rated-power
charging, never proof that it stopped.

### What happens if FC telemetry or the saved fuel total is lost?

Fuel accounting continues through FC-link loss and the FC-version output
block. Every boot starts with the conservative engine-may-be-running latch set;
link silence cannot clear it, and missing RPM is charged at rated power until
fresh disarmed state, zero RPM, and closed throttle all say it is stopped. A
normal `FUEL_CAPG` write is accepted only after those same three inputs are
fresh. The only exception is the explicit positive CAPG in the eligible
one-shot cold manual-start window; no reset preserves that RAM-only OFF result.

If any boot has no trustworthy V2 backup record (including a normal power-on, a
warm reset, or a legacy V1 record), the total is unknown and the filter sends no
DroneCAN ICE Status at all. The same fail-closed result applies when the H743
tune journal is missing, corrupt, or has no valid record: a surviving numeric
total cannot be trusted when the capacity, density, and model settings under
which it accumulated have unknown provenance. POR/PDR cannot prove a refuel.
ArduPilot's EFI backend therefore ages stale/unhealthy instead of accepting a
false zero. The filter repeats `Fuel total LOST - write FUEL_CAPG to restart
it` every 60 s. Land or remain on the ground, verify the fuel configuration,
obtain fresh normal stopped quorum (disarmed + valid zero RPM + closed
throttle) or the eligible cold declaration above, and rewrite positive
`FUEL_CAPG` for the fuel aboard—even if its numerical
value is unchanged. A changed value clears the lockout only after `Tune saved`;
the same-value path schedules no new save, so its accepted-write message and
exact readback are the completion evidence. Disarmed alone is rejected. A
valid restore also receives a bounded
conservative 25-second rated-power reset-gap charge; it is not an exact
measurement of the fuel consumed during reset/startup. An accepted write that
establishes a new total cancels any pending charge attached to the old restored
total.

A factory-reset attempt writes TOTAL LOST to backup SRAM before flash work can
start. Even a failed attempt can therefore conservatively leave EFI silent.
After any attempt, verify all fuel-model settings and perform the stopped-engine
`FUEL_CAPG` recovery; if the capacity changed, wait for `Tune saved`.

### What does `Fuel held up by throttle - check RPM_SCALING` mean?

The throttle position implies more power than the RPM reading does, so the
filter is propping the estimate up rather than believing an RPM that looks too
low. The usual cause is `RPM1_SCALING` set for the wrong number of pulses per
revolution. Do not infer that count from the number of cylinders: DLE does not
specify the DLE120 tach lead's pulses per crank revolution. Measure the real
pickup, then use scaling `1 / pulses per revolution` for a GPIO pulse source.

**Check it against a hand tachometer or oscilloscope before flying again.** Do
not use FC `RPM1_TYPE=3` or `RPM2_TYPE=3` (EFI) for whichever instance the
filter selects, because this filter's EFI RPM is derived from FC RPM and would
create a circular source. Inspect both instances live. The filter ultimately
has one selected RPM source, so nothing else catches a bad value.

---

## Finding the source of interference

### Can I find out where a jammer is?

Roughly. From `v0.5.27+` the filter emits and logs the RF measurements needed
to estimate a bearing. Mission Planner plugin `v0.3.0+` shows a provisional
live two-way axis; after the flight, run `python tools/df_analyze.py flight.bin`
on the flight controller's log. Expected accuracy when the fit answers is
roughly ±20–45°, but the displayed fit sigma does not include FC heading age.

You must **fly a full orbit** through the interference for it to work. The
method reads how interference power changes with your heading, so a straight
pass gives it nothing and the tool will tell you so rather than guess.

One bearing is an axis, not a position. Plugin `v0.3.0+` can show a purple
**UNVALIDATED advisory intersection**, but only after three finalized axes
captured at separated positions. Requiring three lets it reject an inconsistent
segment; any two nonparallel mathematical lines would always appear to
intersect. Until polarity is checked against a transmitter you control, treat
each bearing as a line rather than an arrow.

The live plugin needs at least 20 samples and a real turn; 90° is the minimum
and a full orbit is better. It says `COLLECTING` or `ABSTAIN` instead of
guessing. The RF axis arrives through normal FC telemetry. The source
intersection needs the private USB cable because it anchors each saved axis to
the moving DR reference; it never uses the attacker-controlled red position.
Capture three qualified 20–120 second segments within three minutes. **Every
pair** of anchors must be at least 500 m apart and every pair of axis directions
must differ by at least 30°. The newest axis expires
after 30 seconds. The purple target and dotted sensitivity circle assume one
stationary emitter and are not ground truth, an accuracy radius, or a waypoint.

Nothing about this feeds back into spoof detection or aircraft control. The
firmware only emits/logs observables; all fitting is in the GCS/offline tool.

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
