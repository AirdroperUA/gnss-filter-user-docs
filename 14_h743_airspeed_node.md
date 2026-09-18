# H743 Airspeed Node

The Airspeed Node is a separate, cut-down firmware for the same WeAct Studio
MiniSTM32H743VITX board the GNSS filter runs on. It does three things:

- reads an **MS4525DO** pitot sensor and publishes it to ArduPilot as DroneCAN
  airspeed (`uavcan.equipment.air_data.RawAirData`, 20 Hz);
- bridges the **OpenIPC SSC338Q camera** serial port to the flight controller
  through a DroneCAN serial tunnel, exactly like the filter's camera port;
- shows the airspeed and the **flight controller's status** on the board's
  display.

> **It is not a GPS filter.** The Airspeed Node has no GNSS input, no spoofing
> or jamming detection and no dead reckoning. An aircraft flying with it has
> **no GPS spoofing protection** from this board. Use the
> [H743 DroneCAN Guide](13_h743_dronecan.md) firmware when you need the filter.

It also has no MAVLink console, no parameters and no USB connection of its own.
Everything it needs is fixed in the firmware.

## 1) Wiring

It uses the same board, pins and connectors as the H743 DroneCAN filter, minus
the GNSS receiver.

| Function | Board pins | Notes |
|----------|------------|-------|
| CAN to the flight controller | `PB8` RX / `PB9` TX | through a 3.3 V CAN transceiver (for example SN65HVD230); 1 Mbit/s classic CAN |
| MS4525DO airspeed sensor | `PB10` SCL / `PB11` SDA (I2C2) | address `0x28`; external pull-ups required |
| OpenIPC SSC338Q camera | `PA10` RX / `PA9` TX (USART1) | 115200 baud; optional |
| Status LED | `PE3` | onboard |
| Display | onboard ST7735 | onboard |

Leave `PA2`/`PA3` (the filter's GNSS port) unconnected. The firmware is set for
the ±1 psi (±6894.757 Pa) differential MS4525DO with output type A (10–90 %),
the same sensor the filter reads.

## 2) Installing the firmware

The Airspeed Node is installed with the same provisioning application and the
same license as the filter. It needs application version **2026.09.17.1 or
later**; older versions do not list the Airspeed Node target.

1. In the provisioning application, choose the target
   **"[!] H743 Airspeed Node (NO GPS filter)"**. The application shows an amber
   warning banner and amber Activate/Update buttons for this target so it cannot
   be picked by mistake.
2. Connect the board through ST-Link and press **Activate AIRSPEED NODE** (a
   new board) or **Update AIRSPEED NODE**.

**Switching products.** A board activated as the filter can be re-flashed as an
Airspeed Node, and back, on the same license without using another activation.
The application asks you to confirm the switch because the aircraft's
protection changes with it.

The node's firmware versions (`1.x`) are separate from the filter's (`0.5.x`).

## 3) Flight controller setup (ArduPlane)

Load the Mission Planner preset
`arduplane_FC_4.6.3_h743_airspeed_node_CAN1.param` **into the flight
controller**. It sets:

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `CAN_P1_DRIVER` | 1 | CAN1 on driver 1 |
| `CAN_P1_BITRATE` | 1000000 | 1 Mbit/s |
| `CAN_D1_PROTOCOL` | 1 | DroneCAN |
| `CAN_D1_UC_SER_EN` | 1 | DroneCAN serial tunnels on |
| `CAN_D1_UC_S1_NOD` | 43 | the Airspeed Node |
| `CAN_D1_UC_S1_IDX` | 0 | the node's camera port |
| `CAN_D1_UC_S1_BD` | 115 | 115200 baud |
| `CAN_D1_UC_S1_PRO` | 2 | MAVLink2 |
| `ARSPD_TYPE` | 8 | DroneCAN airspeed |

Reboot the flight controller, then read the parameters back.

It does **not** set `ARSPD_USE`. Set that to 1 only after a bench check shows
sane differential pressure and the airspeed has been calibrated in the
installed airframe. It sets no GPS parameter: configure your GPS as you
normally would.

Manual checks:

- `CAN_D1_UC_NODE` (the flight controller's own node ID) must not be 43.
- `CAN_D1_UC_OPTION` bit 2 (CAN-FD) must be clear.
- No camera? Leave `S1` disabled (`S1_NOD=0`, `S1_IDX=-1`, `S1_PRO=-1`).
  Airspeed does not depend on the tunnel.
- **Filter and Airspeed Node on one aircraft.** They can share the bus (node 42
  and node 43), but the filter's camera port also uses `S1` and index 0: fit
  the camera to one board only and point `S1` at that board's node. Fit an
  MS4525 to one board only, or ArduPlane sees two DroneCAN airspeed sources.

## 4) The display

Every Airspeed Node screen has a solid **blue "AIRSPEED" title band** across
the top. The filter never shows that band, so you can tell the two firmwares
apart at a glance.

The airspeed is always shown in large digits under the band, with the sensor
state beneath it: `OK`, `ZEROING`, `STALE`, `NO SENSOR` or `BAD VALUE`. It
shows `--` whenever there is no fresh, valid reading.

**Keep the pitot still and out of any draught for the first 2 seconds after
power-up.** The node shows `ZEROING` while it averages the sensor's resting
offset, then subtracts it and computes the airspeed the way ArduPlane does:
√(|ΔP − zero| × 1.9936), where 1.9936 is ArduPlane's default `ARSPD_RATIO`.
It should then read close to Mission Planner at rest; small noise of a meter or
two per second is normal at zero airflow, on both. Differences remain if the FC's
`ARSPD_RATIO` has been calibrated away from its default, or if the FC took its
own zero at a different moment. The number on the screen is for the bench only:
the node sends the flight controller the **raw** pressure, and the flight
controller applies its own zero and calibration.

The footer shows `AIR+` (publishing), `AIR?` or `AIR-`, the arming state
(`ARM`, `DIS`, `ARM?`) and the node number.

The node cycles through four pages:

| Page | Shows |
|------|-------|
| **OVERVIEW** | the FC banner (flight stage, or a red alert), vehicle armed state, safety switch, camera link, and the publishing status |
| **FLIGHT** | FC node, FC health, FC mode, arming and safety |
| **LINKS** | CAN frame counts and errors, camera link state and byte counters in each direction, dropped bytes |
| **SYSTEM** | firmware version, node ID, differential pressure, sensor temperature, I2C errors and recoveries, uptime |

The pages stop cycling and stay on OVERVIEW while the flight controller reports
an alert or while there is no airspeed to show.

**Flight stage** comes from ArduPilot's own notify state: `INIT`, `NOT RDY`
(pre-arm checks failing), `READY` (pre-arm checks passing), `ARMED`,
`TAKEOFF`, `FLYING`, `LANDING`, or `ESC CAL`, `MAG CAL`, `FW UPD`, `PWR OFF`.

**FC alerts** (red): `CHUTE`, `VEH LOST`, `FS BATT`, `FS RADIO`, `FS GCS`,
`EKF BAD`, `GPS GLITCH`, `LEAK`.

The node shows flight controller status only after it has identified the
flight controller: through the camera tunnel, or from the arming and safety
messages every ArduPilot flight controller broadcasts on DroneCAN. It does
not need the camera tunnel to show status.

## 5) Status LED

| LED | Meaning |
|-----|---------|
| steady on | CAN controller not running |
| fast blink (5 Hz) | airspeed sensor missing, stale, or its data is not getting onto the bus |
| short blip once a second | healthy |

## 6) Diagnostics

**"PreArm: DroneCAN: Node 43 unhealthy".** Five seconds after power-up the node
reports itself unhealthy while the airspeed is missing, stale, or cannot be sent.
Check the pitot, its I2C wiring and the pull-ups; the message clears by itself.

**Node log messages.** The node reports `I2C scan: ...`, `I2C bus down: SDA/SCL
low - pullups or wiring`, `MS4525 found at 0x28` and `MS4525 lost at 0x28` as
DroneCAN log messages. ArduPlane always writes them to its onboard log as
`CAN[43] ...`. To see them in Mission Planner's Messages tab, set
`CAN_LOGLEVEL` to 3 on the flight controller.

**DroneCAN inspector.** Under Setup → Optional Hardware → DroneCAN/UAVCAN,
node 43 appears as `org.airdroper.h743_airspeed`. Its NodeStatus vendor-status
bits are: bit 0 sensor identified, bit 1 reading fresh, bit 2 camera tunnel
bound, bit 6 sensor fault.

## 7) Checklist before flight

1. Node 43 is present and healthy in the DroneCAN inspector.
2. Blowing gently across the pitot moves the airspeed on the node's display and
   in Mission Planner's status tab.
3. With the camera powered, the node's LINKS page shows the camera link live.
4. The airspeed is calibrated in the installed airframe, and `ARSPD_USE` is set
   deliberately.
5. You have confirmed this aircraft does not need GPS spoofing protection from
   this board.
