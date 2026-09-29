# APMPX4 CAN (STM32L433) Guide

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

The APMPX4 CAN board (EasyEDA project "APMPX4 CAN-JSTGH", schematic V1.0,
2026-03-17) runs the same filter firmware as the
[H743 DroneCAN Guide](13_h743_dronecan.md) on a smaller STM32L433RCT6, and
publishes to the flight controller as DroneCAN node `42`. This guide covers
firmware `0.5.39`.

**Status: not released yet.** No L433 firmware has been published yet, so the
desktop app cannot install it. The `0.5.39` bench image has run on a bench
board with ArduPlane 4.7.1: under a clear sky it passed GPS to the flight
controller, and at a spoofed site it kept GPS blocked, as designed (see
`docs/dev/evidence/l433-bench-live-spoofing-2026-09-26.md`). Treat this board
as a bench and test-team device until a release is announced in the
[Changelog](CHANGELOG.md).

## 1) Two firmware builds

| Build | What it does | Installed by |
|-------|--------------|--------------|
| `apmpx4_can_l433rc_dronecan` | The GNSS spoofing filter: GNSS in on CN2, filtered GPS out as DroneCAN, plus airspeed, compass, the camera tunnel, fuel estimation and parameters. | The desktop app (release image), or directly over SWD (bench image) |
| `apmpx4_can_l433rc_dronecan_nognss` | Everything except GNSS: airspeed, compass, the camera tunnel, fuel estimation and parameters on node `42`. CN2 is unused, and there is no DR0/DR1. | Directly over SWD only (bench image) |

Both builds use node ID `42`, so do not put one of each on the same CAN bus.
DroneCAN tools show them as `org.airdroper.gnss_filter.l433_dronecan` and
`org.airdroper.gnss_filter.l433_nognss`, with hardware version `2.0` (the WeAct
H743 is `1.0`). The node information's VCS field holds the full firmware
version: a tool that shows it in hex shows `00000539` for 0.5.39.

If two nodes with ID `42` do share a bus, each of them reports
`CAN: another node uses ID 42 - ID clash` every 10 s and reports itself
unhealthy, so the flight controller refuses to arm until one is removed.

## 2) Board and connectors

- STM32L433RCT6 at 80 MHz, clocked from an 8 MHz resonator.
- TJA1051 CAN transceiver at 1 Mbit/s. The 120 Ω termination (R56) is always
  fitted, so the board must sit at one end of the CAN bus: never in the
  middle, and never at the same end as another terminated node.
- JST GH 1.25 mm connectors in Pixhawk pin order. Pin 1 of every connector is
  the same 5 V rail.
- No USB and no display. Programming is over SWD on header H1.
- Status LED `LED1` on `PB1` (see section 8 for what it shows).

| Connector | Use | Pins |
|-----------|-----|------|
| U142 | CAN to the flight controller | 1 `5V`, 2 `CAN_H`, 3 `CAN_L`, 4 `GND` |
| CN2 | GNSS receiver (filter build only), USART2 | 1 `5V`, 2 `TX2` (`PA2`), 3 `RX2` (`PA3`), 4 `SCL3`, 5 `SDA3`, 6 `GND` |
| CN1 | Camera MAVLink tunnel, USART1 at 115200 | 1 `5V`, 2 `TX1` (`PB6`), 3 `RX1` (`PB7`), 4 `SCL2`, 5 `SDA2`, 6 `GND` |
| U141 | I2C2 sensors: MS4525 airspeed | 1 `5V`, 2 `SCL2` (`PB13`), 3 `SDA2` (`PB14`), 4 `GND` |
| CN3 | Spare UART (USART3) and I2C2; unused | 1 `5V`, 2 `TX3`, 3 `RX3`, 4 `SCL2`, 5 `SDA2`, 6 `GND` |
| H1 | SWD for ST-Link, 2.54 mm; no NRST | 1 `3V3`, 2 `SWDIO` (`PA13`), 3 `SWCLK` (`PA14`), 4 `GND` |

U138 and U140 carry the spare I2C3 bus, and S1–S4 are servo headers (signal,
not connected, GND) with no power on them. The firmware uses none of them; it
holds S1–S4 and the buzzer and RGB LED lines low. The compass on CN2 pins 4–5
(I2C3) is not read either. The onboard MMC5983MA compass sits on I2C2 at
`0x30`.

The complete pinout, with both board sides, every solder pad and the pin tables,
is an A3 drawing:
[l433_apmpx4_can_pinout.pdf](https://github.com/AirdroperUA/gnss-filter-user-docs/blob/main/diagrams/l433_apmpx4_can_pinout.pdf)
(Ukrainian:
[l433_apmpx4_can_pinout_uk.pdf](https://github.com/AirdroperUA/gnss-filter-user-docs/blob/main/diagrams/l433_apmpx4_can_pinout_uk.pdf)).

## 3) Wiring and power

![APMPX4 CAN wiring: the flight controller on U142, a u-blox receiver on CN2, and the pins of every connector](diagrams/l433_apmpx4_can_wiring.png)

1. **Flight controller:** a straight Pixhawk CAN cable from U142 to the FC's
   CAN1 port, pin 1 to pin 1. This cable also powers the board: feed the 5 V
   rail from exactly one source, normally the FC's CAN port.
2. **GNSS receiver (filter build):** a straight Pixhawk GPS cable from CN2 to
   the receiver's UART. Board `TX2` lands on the receiver's RX and `RX2` on its
   TX. The receiver type is the node's `GNSS_TYPE` parameter: `0` u-blox (the
   default, autoconfigured to 460800 baud), `1` UM980/UM981, `2` Septentrio
   Mosaic. For a UM980 or Mosaic, set `GNSS_TYPE` (section 5 says how to reach
   the node's parameters), wait for the node's `Tune saved` message (a few
   seconds, or up to about a minute after an earlier save), and then remove
   the board's power for a few seconds; only after that power-up is the
   receiver found by a baud scan. The board has no reset button, and Mission
   Planner's DroneCAN restart does nothing on this node. A UM980 also needs its
   one-time setup from the [GNSS Receiver Configuration](09_receiver_config.md)
   guide, and a Mosaic the SBF setup in the H743 guide's
   [Septentrio Mosaic X5 SBF input](13_h743_dronecan.md#septentrio-mosaic-x5-sbf-input)
   section.
3. **Camera:** CN1 to the camera's UART, crossing TX and RX by function. Power
   the camera from its own supply unless its draw fits the FC CAN port budget,
   and leave CN1 pins 4–5 free: they are the sensor bus.
4. **Airspeed:** a Pixhawk-style MS4525DO airspeed module on U141, straight
   cable. Pin 1 of U141 is the 5 V rail, and the sensor bus is pulled up to
   3.3 V on the board and shared with the onboard compass, so use a module that
   takes 5 V in, regulates its own 3.3 V and keeps its I2C lines at 3.3 V. Do
   not wire a bare 3.3 V sensor to U141. The sensor on the module must be the
   one the H743 guide specifies (`4525DO-DS3AI001DP`: address `0x28`,
   `-1..+1 psi`, transfer function A).

**3.3 V logic only.** CN2 takes 3.3 V logic only: the board's receive pin
there (`RX2`, `PA3`) is not 5 V tolerant, and the STM32L433 datasheet rates it
3.6 V tolerant. Connect a receiver's 3.3 V UART (the u-blox, UM980 and Mosaic
receivers this guide covers have one), never 5 V TTL or RS-232 levels. The
servo headers S1–S4 and CN1's receive pin (`RX1`, `PB7`) are 3.3 V-only too,
the way the firmware sets them up: the internal pull resistors it enables
remove the chip's 5 V tolerance.

**Onboard compass.** The MMC5983MA sits a few millimetres from the status LED
and from the 5 V tracks that feed CN1 (the camera). If you use the onboard
compass, power the camera separately where possible, and check the compass
heading with the camera on and off.

The ST-Link's 3.3 V is not enough for CAN. The TJA1051 runs from the 5 V rail,
so on ST-Link power alone the MCU runs but CAN goes bus-off.

## 4) Flashing

Flashing with the desktop app (activation, update or recovery) erases the
board's saved parameters. `GNSS_TYPE` returns to `0` (u-blox), so a board with
a UM980 or Mosaic then finds no receiver until `GNSS_TYPE` is set again
(section 3, step 2). Set it, `FUEL_CAPG` and any other changed parameter again
afterwards. A bench upload with PlatformIO over SWD
(`pio run -e ... -t upload`) erases only the flash pages the image covers, so
the saved parameters survive it and carry over between the filter and no-GNSS
builds.

**With the desktop app (release image).** In the AirDroper desktop app choose
**L433 APMPX4 CAN (ST-Link)**. The app downloads the image bound to this board's
unique ID, checks its signature, writes it over ST-Link, reads it back, and then
locks the chip (RDP1). The board has no reset button: when the app asks you to
power-cycle the board, and again when it finishes, remove all power for at
least 10 seconds and then power it again. It needs a published L433 release, so
it does not work yet (see Status above).

After an L433 flash the app also prints the board's
`Authenticated DR-recovery signing key` and tells you to save it now: there is
one key per board, and it cannot be recovered later. Keep it secret, like a
password: anyone who has it can authorize a DR1 recovery on that board.

A release image refuses to start on a board it is not bound to, and on a board
that is not locked. It then blinks the LED fast, 100 ms on and 100 ms off. Run
the update again in the desktop app.

**Directly over SWD (bench images).** Wire H1 to the ST-Link: `SWDIO`, `SWCLK`
and `GND`. On a genuine ST-LINK/V2, V3 or Nucleo probe, pin 1 (`3V3`) is the
target-voltage sense and must be connected, and the board must be powered from
elsewhere; on a clone probe that pin supplies 3.3 V, so connect it only when
nothing else powers the board. H1 has no NRST, so connect in Normal or Hot-plug
mode, never under reset. Then build and upload:

```text
pio run -e apmpx4_can_l433rc_dronecan -t upload
pio run -e apmpx4_can_l433rc_dronecan_nognss -t upload
```

A board the desktop app has locked (RDP1) cannot be programmed this way. Unlock
it first. The desktop app's **Recover Board** does that for an L433: it removes
the lock, which erases the whole chip, and checks that the flash is blank. From
the command line, use STM32CubeProgrammer and set only the RDP option byte,
then remove all power for at least 10 seconds:

```text
STM32_Programmer_CLI -c port=SWD mode=NORMAL -ob RDP=0xAA
```

Unlocking erases the whole chip: the firmware and its parameters. The
power-off after it clears the fuel record and any DR1 state the board kept
across resets (section 8). Never write `RDP=0xCC`: that is level 2, which
disables SWD for good.

Never flash `apmpx4_can_l433rc_dronecan_release` directly: it only runs after
the server has bound it to a board and the desktop app has locked the chip.

After the first flash of a blank chip, power-cycle the board. A blank STM32L4
keeps starting its ROM bootloader until a power-on reset.

## 5) Flight controller setup (ArduPilot)

ArduPilot 4.6.1 or newer is required: the filter build keeps GPS off an older
autopilot.

The CAN and tunnel settings are the same as on the H743. The H743 guide's
section 6 applies unchanged, including its hard preconditions for GPS output:
the filter tunnel carrying a live `EKF_STATUS_REPORT`, and the flight
controller's MAVLink system ID set to 1: `MAV_SYSID = 1` on ArduPilot 4.7 and
newer, `SYSID_THISMAV = 1` on 4.6. The filter accepts flight controller
telemetry only from system 1, component 1.

| Purpose | Parameter | Value |
|---------|-----------|-------|
| CAN driver on CAN1 | `CAN_P1_DRIVER` | `1` |
| DroneCAN protocol | `CAN_D1_PROTOCOL` | `1` |
| CAN bitrate | `CAN_P1_BITRATE` | `1000000` |
| GPS type (filter build) | `GPS1_TYPE` | `9` (DroneCAN) |
| GPS auto-config (filter build) | `GPS_AUTO_CONFIG` | `1` |
| Optional GPS node lock (filter build only, see section 7) | `GPS1_CAN_OVRIDE` | `42` |
| Enable DroneCAN serial | `CAN_D1_UC_SER_EN` | `1` |
| Camera port node / index / baud / protocol | `CAN_D1_UC_S1_NOD` / `_IDX` / `_BD` / `_PRO` | `42` / `0` / `115` / `2` |
| Filter port node / index / baud / protocol | `CAN_D1_UC_S2_NOD` / `_IDX` / `_BD` / `_PRO` | `42` / `1` / `115` / `2` |
| FC MAVLink system ID (4.6: `SYSID_THISMAV`) | `MAV_SYSID` | `1` |
| Airspeed | `ARSPD_TYPE` | `8` (DroneCAN) |

- **Airspeed:** calibrate the pitot in the installed airframe, then set
  `ARSPD_USE = 1` and `AHRS_OPTIONS` bit 0. With the filter build this is a
  flight-safety requirement: the aircraft has to fly GPS-denied the moment DR1
  latches (see the H743 guide).
- **Compass:** in Mission Planner open `Setup -> Mandatory Hardware -> Compass`,
  confirm a compass from node `42` appears, set its orientation and priority,
  and calibrate it in the installed vehicle. The onboard MMC5983MA is compass
  `0` of node `42`, and an external compass on the sensor bus is compass `1`,
  so each keeps its own orientation and calibration: after you add, remove or
  change an external compass, the flight controller sees a different compass
  to set up, not the old one with the wrong calibration.
- **Tunnel ports:** `_PRO` must be `2` (MAVLink2) on both ports; with `1`, the
  node discards that port's traffic. Reboot the flight controller after
  changing any CAN or `CAN_D1_UC_*` serial setting: ArduPilot sets up the CAN
  driver and the tunnel ports only when it boots.
- **The node's own parameters** (`GNSS_TYPE`, `FUEL_CAPG` and the rest) are
  reached through the flight controller, since the board has no USB: in Mission
  Planner open `SETUP -> Optional Hardware -> DroneCAN/UAVCAN`, connect, and
  open **Menu -> Parameters** on node `42`. The H743 guide's section 7,
  Option A, has the full procedure. Where it says to reboot the board, that
  means a power cycle here: wait until the node has saved the value (it reports
  `Tune saved`), then remove the board's power for a few seconds, and check
  afterwards that the value survived. The board has no reset button, and the
  node does not implement DroneCAN's RestartNode, so Mission Planner's DroneCAN
  restart does nothing.
- **Swapping boards:** the flight controller remembers which board holds node
  `42`. After replacing it with another board (an L433 for an H743, or one L433
  for another), it reports `Duplicate Node` and refuses to arm. Set bit 0 of
  `CAN_D1_UC_OPTION` without changing its other bits (if the value is even,
  add 1 to it), then reboot the flight controller once: at boot ArduPilot
  clears its node database and then the bit. Calibrate the compass again as
  well: to the flight controller the new board's compass is the old one, and
  it would keep the old board's calibration.

## 6) Optional sensors

The MS4525 airspeed sensor and the compass are both compiled into both builds,
and both are optional:

- A sensor that does not answer after power-up counts as not fitted. It raises
  no fault and no `I2C AIR=... MAG=...` warning, so the node stays healthy.
- A sensor that answered and then stops answering raises the fault: ArduPilot
  reports `Node 42 unhealthy!` and refuses to arm, as on the H743.
- A sensor that first answers later than power-up counts as fitted from then on.
  ArduPilot, however, looks for airspeed sensors only when it boots, so reboot
  the flight controller after plugging one in.
- The first compass found after power-up is the only one used until power-off.
  If it stops answering, the node reports the fault; it never switches to
  another compass, such as the onboard MMC5983MA, whose calibration and
  orientation would differ.

The node publishes airspeed as `RawAirData` and the compass as
`MagneticFieldStrength2`, raw. All calibration belongs to ArduPilot.

**Flying the filter build without a pitot** costs DR1 recovery: the
ground-speed-versus-airspeed check can never pass, so leaving DR1 in flight
needs a real climb or a steady turn; straight-and-level flight will not do it.

## 7) The no-GNSS build

`apmpx4_can_l433rc_dronecan_nognss` is for aircraft that take GPS from
elsewhere and want the board only as an airspeed, compass and camera node:

- It never publishes GPS, never latches DR1 and never blocks anything, and its
  NodeStatus never reports GNSS as blocked.
- The GNSS and DR1 parameters are still in the node's parameter list, but they
  do nothing in this build, and saving one says so, for example
  `GNSS_TYPE=1 saved (no GNSS in this build)`. Setting `UBX_RESET` to a reset
  answers `UBX_RESET ignored: no GNSS in this build`; its idle value `0`, which
  a parameter file writes, is accepted without a message. The read-only
  `GPS1_TYPE` and `GPS_TYPE` entries that a DroneCAN GPS node lists are not in
  its list.
- The operator "block GNSS" command is answered `UNSUPPORTED`, and a DR1
  release is answered that the node is not in DR1. With no DR1 there is no
  authenticated DR recovery either, and no signing key.
- Its status messages come once, from system 42. The filter build also repeats
  each one as the flight controller's GPS component (system 1, component 220);
  this build is not a GPS, so it does not.
- Leave `GPS1_TYPE` for whatever GPS the aircraft really uses. When an
  aircraft moves from the filter build to this one, set `GPS1_CAN_OVRIDE` back
  to `0` (or to the node ID of the real DroneCAN GPS): node `42` never sends
  GPS here, so a lock on `42` blocks the real GPS.
- Keep the CAN, tunnel, airspeed and compass settings from section 5,
  including the filter tunnel (S2) and the flight controller's system ID of 1.
  The node's status messages reach Mission Planner only through that tunnel,
  the node accepts parameter changes only from the flight controller it found
  through the tunnels, and the flight controller telemetry it reads there (the
  throttle and RPM for the fuel estimate, for example) counts only from
  system 1.

## 8) Troubleshooting

The board has no display. Its status messages reach Mission Planner through the
filter tunnel (DroneCAN serial port 2 on the flight controller, index `1`), so
without that tunnel there are no messages at all. The lines from the first
seconds after power-up, before the tunnel connects, are held and sent as soon
as it does: the start-up banner, the firmware version and board ID, and, with
room of their own, the warnings, such as the reset and DR1 lines below. The LED
shows the state:

| LED1 | Meaning |
|------|---------|
| 80 ms flash every 6 s | Running, DR0 (GNSS output allowed if every other check passes); the no-GNSS build always shows this |
| 50 ms flash every 250 ms | DR1: GNSS blocked |
| 100 ms on, 100 ms off, right after power-up | The firmware refused to start: the release image is bound to another board, or the board is not locked. Run the update again in the desktop app |

- **Node 42 does not appear:** check that U142 has 5 V, that the cable is
  straight (pin 1 to pin 1), the bitrate is `1000000`, and that the board sits
  at an end of the bus.
- **CAN bus-off on the bench:** the board is probably on ST-Link power only.
  Give the 5 V rail power.
- **`Node 42 unhealthy!`:** the node reports itself unhealthy for four
  reasons:
  - a sensor that was found has stopped answering, or its data is not reaching
    CAN; the `I2C AIR=... MAG=...` status message names which one;
  - DR1 (the filter build), for a spoofing or a fault reason: see "GPS blocked
    (DR1)" below;
  - the clock: `CLOCK: resonator failed, on HSI16 - CAN marginal` means the
    8 MHz resonator did not start, and `CLOCK: resonator stopped, on HSI16 -
    CAN marginal` that it stopped while running, which reset the board. Either
    way the board runs on its internal oscillator until the next power-off,
    and that may be too inaccurate for CAN: after three bus-off events on it
    the node stays off the bus until power-off, so the flight controller loses
    node `42` rather than the whole bus. The board needs repair;
  - another node with ID `42` on the bus: `CAN: another node uses ID 42 - ID
    clash`, repeated every 10 s while it lasts. Remove one of them (section 1).
- **GPS blocked (DR1, filter build):** the first `GNSS BLOCKED #n: <reason>`
  line of an episode names why DR1 tripped, and so does `DR_REASON`, a value
  the node sends every 5 s. The same line then repeats every 5 s, but from then
  on it names what blocks recovery now, not the trip reason: `no-anchor`, for
  example, means there has been no trusted fix since power-up. DR1 has several
  reasons; two of them are worth knowing here:
  - `FC LINK STALE`, common on a new installation: the filter tunnel or the
    flight controller's system ID (`MAV_SYSID`, or `SYSID_THISMAV` on 4.6) is
    wrong, and the H743 guide's "FC LINK STALE: one cause, four messages"
    explains it;
  - `SOUTH HEMISPHERE` (`DR_REASON` 8) is live spoofing: the receiver reported
    a valid fix south of the equator and west of Greenwich. On the ground the
    node never releases it by itself. After the spoofing stops, remove the
    board's power for at least 10 seconds. A reset that keeps the power, or a
    shorter interruption, brings DR1 back with the same reason (see "DR1 kept
    across reset" below), and a flight controller reboot helps only if it cuts
    the 5 V on the CAN port for that long. Until then the flight controller shows
    `PreArm: GPS 1: Bad fix` and `PreArm: DroneCAN: Node 42 unhealthy!`. With
    a u-blox receiver, `GNSS hot ...` and `GNSS cold ...` after 10 minutes
    without a fix, and then `GNSS cold retry` every 2 minutes, are expected.
- **`DR1 kept across reset: <reason>` (filter build):** the board reset
  without losing power (the watchdog, a crash, a power dip) while DR1 was
  latched, and came back latched, with the same reason and the trusted
  position it had. GNSS output stays blocked until the normal recovery
  evidence releases it, or, for `SOUTH HEMISPHERE` and `OPERATOR BLOCK`,
  until the board's power is removed for at least 10 seconds. After a reset
  outside DR1 the node keeps only its trusted position
  (`North anchor kept across reset`), and GNSS output waits for the start-up
  guard (20 s, or 2 s while the flight controller reports itself armed)
  before it opens.
- **`RESET: ...` after power-up:** the board reset without a power-off, and
  says why. `RESET: watchdog` means the firmware stopped responding;
  `RESET: HardFault PC=... CFSR=...` (or `MemManage`, `BusFault`,
  `UsageFault`, `NMI ...`) means it crashed, and the two values say where.
  Report either line in full. `RESET: software` follows a debugger upload,
  and `RESET: option-byte load` the lock the desktop app applies. A normal
  power-up says nothing.
- **`BACKUP: store failed, nothing kept across reset`:** the registers that
  keep the fuel total and the DR1 state across resets failed their start-up
  test. The board keeps neither, so the fuel total reads lost after every
  reset. The board needs repair.
- **`CAN rxerr=... boff=... purge=...`:** the node's CAN counters since
  power-up: received frames it lost, bus-off events, and transmit queues it
  dropped, which includes the drop every DR1 entry makes on purpose. The line
  comes when a counter changes, with ` EPASS` added while the node's CAN
  controller is error-passive. `rxerr` or `boff` that keeps rising, or
  `EPASS`, points at the wiring, the termination (section 2) or the 5 V
  supply.
- **`Fuel total unknown: no engine RPM from FC`:** the fuel total starts
  unknown at every power-up on this board (nothing keeps it through a
  power-off), and the flight controller has sent no engine RPM yet, so there is
  nothing to estimate. It is said once, and is normal on an aircraft without an
  engine RPM source. Once RPM arrives, `Fuel total LOST - write FUEL_CAPG to
  restart it` repeats every minute until `FUEL_CAPG` is written; see the H743
  guide's engine fuel estimation section.
- **`Duplicate Node` after swapping boards:** see "Swapping boards" in
  section 5.
- **No GPS on the FC (filter build):** check the LED first. If it shows DR1,
  see "GPS blocked (DR1)" above. If it shows DR0, work through "Node appears
  but FC does not get GPS" in the H743 guide, ignoring its display checks; the
  causes are the same.
