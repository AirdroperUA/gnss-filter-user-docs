# WeAct H743 DroneCAN Guide

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

This page is the complete H743-specific setup path for the WeAct Studio
MiniSTM32H743VITX board with a 3.3 V CAN transceiver such as the SN65HVD230.
Use it when you want the filter to publish GPS, MS4525DO airspeed and HMC5983
compass data to ArduPilot, while carrying MAVLink2 over the same DroneCAN
connection instead of using flight-controller UARTs.

## 1) Supported H743 firmware families

| Firmware environment | Purpose | Upload path |
|----------------------|---------|-------------|
| `weact_mini_h743vitx` | Standalone H743 UART development build | ST-Link |
| `weact_mini_h743vitx_usb` | Same standalone UART build | USB-C ROM DFU |
| `weact_mini_h743vitx_dronecan` | H743 DroneCAN GPS build | ST-Link |
| `weact_mini_h743vitx_dronecan_usb` | Same DroneCAN GPS build | USB-C ROM DFU |
| `weact_mini_h743vitx_dronecan_bootloader` | H743 DroneCAN secure bootloader | ST-Link |
| `weact_mini_h743vitx_dronecan_phaseb_app` | Signed H743 DroneCAN app at `0x08020000` | ST-Link |
| `weact_mini_h743vitx_dronecan_phaseb_app_usb` | Signed H743 DroneCAN app at `0x08020000` | USB-C ROM DFU |

The recommended H743 flight configuration is the DroneCAN family:

- GNSS input on `PA2/PA3`
- CAN to the flight controller on `PB8/PB9` through a CAN transceiver
- OpenIPC camera MAVLink2 on `PA10` RX / `PA9` TX at `115200` baud
- shared I2C2 sensor bus on `PB10` SCL / `PB11` SDA for an MS4525DO
  differential-pressure sensor and HMC5983 magnetometer
- USB-C kept on `PA11/PA12` for ROM DFU and bench/debug USB
- two bidirectional `uavcan.tunnel.Targetted` virtual serial ports over CAN:
  index `0` for the camera, index `1` for filter-owned MAVLink and FC telemetry
- no physical FC MAVLink or FC GPS serial port
- tune parameters edited through Mission Planner DroneCAN/UAVCAN node `42`
  Params on firmware `v0.1.4+`, or by connecting Mission Planner directly to
  the H743 USB-C COM port on firmware `v0.1.5+`

The standalone H743 UART build exists for development and compatibility work.
It uses the same idea as the F401 UART build, but its FC GPS UART is `PC6/PC7`
so `PA11/PA12` remain available for USB-C.

## 2) Required hardware

| Item | Notes |
|------|-------|
| WeAct Studio MiniSTM32H743VITX | STM32H743VIT6 board |
| GNSS receiver | u-blox, UM980/UM981/UM982, or Septentrio Mosaic X5; Mosaic SBF is supported on H743 DroneCAN `v0.1.9+` |
| OpenIPC SSC338Q camera | 3.3 V UART configured for MAVLink2 at 115200 baud |
| 3.3 V CAN transceiver module | SN65HVD230 is the documented baseline |
| CAN cable to flight controller | CANH, CANL, and GND |
| Camera UART cable | Camera TX, camera RX, and common GND; power the camera from a suitable separate supply |
| MS4525DO airspeed sensor | Default firmware scaling is specifically for `4525DO-DS3AI001DP`; see the ordering-code warning below |
| HMC5983 magnetometer | Genuine HMC5983 at I2C address `0x1E`; verify identity before flight |
| Keyed 4-pin I2C connector/harness | Separate from the full HD-15 connector; carries 3V3, GND, SCL, and SDA |
| USB-C cable | For H743 ROM DFU flashing and bench power/debug |
| ST-Link V2 | Optional for development and required for locked production provisioning |

The CAN transceiver is mandatory. The H743 `FDCAN1` pins are logic-level TX/RX
signals; they cannot be connected directly to a flight-controller CAN port.

Use the transceiver module's 120 ohm termination only when the H743 node is at
a physical end of the CAN bus. If the H743 is in the middle of the bus, leave
that termination disabled.

## 3) DroneCAN wiring

| Link | WeAct H743 pin | Module / FC pin | Notes |
|------|----------------|-----------------|-------|
| GNSS TX to STM32 RX | `PA3` | GNSS TX | Cross TX to RX |
| STM32 TX to GNSS RX | `PA2` | GNSS RX | Cross TX to RX |
| Camera TX to STM32 RX | `PA10` | OpenIPC camera TX | 3.3 V UART, cross TX to RX |
| STM32 TX to camera RX | `PA9` | OpenIPC camera RX | 3.3 V UART, cross TX to RX |
| Sensor I2C clock | `PB10` | MS4525DO and HMC5983 `SCL` | I2C2, shared bus |
| Sensor I2C data | `PB11` | MS4525DO and HMC5983 `SDA` | I2C2, shared bus |
| Sensor power | `3V3` | Sensor `VCC` | Only for confirmed 3.3 V-compatible parts/modules |
| Sensor ground | `GND` | Sensor `GND` | Common signal/power ground |
| CAN TX | `PB9` | Transceiver `TXD` | FDCAN1_TX |
| CAN RX | `PB8` | Transceiver `RXD` | FDCAN1_RX |
| CAN power | `3V3` | Transceiver `VCC` | Use a 3.3 V module |
| Ground | `GND` | Transceiver `GND` and FC CAN GND | Common ground required |
| CAN bus high | Transceiver `CANH` | FC CANH | Twisted pair recommended |
| CAN bus low | Transceiver `CANL` | FC CANL | Twisted pair recommended |
| DR1 event output | `PB5` | Optional LED/logger input | 3 second pulse on DR0 -> DR1 |
| USB-C | `PA11/PA12` internally | USB-C connector | Do not wire these pins externally |

The camera and H743 must share signal ground. Do not connect 5 V logic to
`PA9/PA10`. Supply the camera from a regulator sized for the camera/LTE load;
the UART wiring described here is not a camera power feed.

<a id="sensor-i2c-connector"></a>

### Shared I2C2 airspeed/compass connector (`SENSOR_I2C`)

The HD-15 assignment below is already full. Do not repurpose one of its pins.
Install a separate, keyed and clearly labelled 4-pin connector for the sensor
bus. This recommended enclosure pin order is deliberately different from the
HD-15 numbering:

| I2C connector pin | Signal | Inside the box | Sensor harness |
|-------------------|--------|----------------|----------------|
| 1 | `3V3_SENSOR` | Protected H743-compatible 3.3 V rail | Both sensor VCC pins, only if 3.3 V compatible |
| 2 | `GND` | Box ground | Both sensor GND pins |
| 3 | `I2C2_SCL` | H743 `PB10` | Both sensor SCL pins |
| 4 | `I2C2_SDA` | H743 `PB11` | Both sensor SDA pins |

Use the connector manufacturer's mating-face numbering and key the housing so
it cannot be inserted reversed. Confirm pin 1 with a meter before connecting a
sensor. The MS4525DO and HMC5983 are wired in parallel on the same bus; they are
not daisy-chained through CAN.

Use one effective set of pull-ups from SCL and SDA to **3.3 V** (typically
2.2-4.7 kohm each, selected for the actual harness capacitance). Many breakout
boards already contain pull-ups, so check the assembled harness and do not
blindly parallel several strong sets. Never pull either I2C line to 5 V. Keep
the I2C harness short, route it away from motor/ESC and LTE power wiring, and
verify clean edges with the complete harness installed. I2C is intended for
short in-box or short sensor-mast wiring, not a long vehicle cable.

The firmware's MS4525 defaults match the complete TE ordering code
`4525DO-DS3AI001DP`: dual side ports, 3.3 V supply, transfer function A
(10-90% counts), I2C address `0x28`, bidirectional differential range of
`-1..+1 psi`, with negative pressure polarity matching the ArduPilot pitot
convention used by this build. Confirm the **complete marking/order code** on
the sensor or its traceable documentation. `DS5...`, another address letter,
another pressure range, transfer function B, an absolute/gauge part, or an
unidentified breakout is not a drop-in substitute. Change and revalidate the
firmware build settings for its voltage, address, range, transfer function and
polarity before using such a part. On the bench, gently apply pressure and
confirm that the flight controller reports increasing positive airspeed;
never validate the sign for the first time in flight.

The magnetometer driver expects HMC5983 address `0x1E` and identification bytes
`H43`. Numerous modules sold as HMC5983 use HMC5883-compatible or unmarked
clones. An address scan alone is not proof of the device. This firmware rejects
the wrong identity, but a module that imitates `H43` can still have different
gain, noise or temperature behavior; use a traceable part and bench-compare it
against a known compass.

Mount the HMC5983 rigidly and record its axis orientation. Prefer an external
mast/location away from motors, magnets, steel fasteners, high-current battery
and ESC wiring, switching regulators, the CAN transceiver, and the camera/LTE
radio. Keep the MS4525 and its pitot hoses away from prop wash, leaks, sharp
bends and water traps. The magnetometer's location and axes affect heading;
the airspeed sensor's pressure-port plumbing affects sign and scale.

The WeAct onboard 80 x 160 ST7735 color TFT is used by the DroneCAN build. It
is a TFT, not an OLED. The firmware
uses `PE12` SCK, `PE14` MOSI, `PE11` CS, `PE13` DC, and `PE10` backlight.
Official WeAct V10-V12 schematics tie LCD reset to the board `NRST` or
`SYS_RESET` net, not `PF0`; firmware therefore uses the shared board reset plus
the ST7735 software-reset command. Those display pins do not overlap USB-C,
CAN, GNSS, LED, or DR1 event wiring. Compile-time checks enforce the pin
contract.

### Optional HD-15 D-sub box connector

If the H743 board, SN65HVD230 CAN transceiver, display, power protection, and
USB-C port are all inside one enclosure, use this as the user-facing 15-pin
"VGA" style connector on the box. The connector exposes only external harness
signals: flight-controller CAN, box power, GNSS UART/power, optional DR1 status,
and the camera MAVLink UART. Raw H743 `PB8/PB9` FDCAN logic stays inside the box
between the MCU and CAN transceiver.

Use a high-density DE-15/HD-15 connector only as a rugged custom harness
connector. It is not a VGA interface. Label it `CAN/GNSS/CAMERA/POWER` and
never plug it into a monitor, PC, or normal VGA cable.

Use this numbering from the mating face of the female panel connector, wide
side up. The solder-cup side is mirrored, so verify the tiny molded pin numbers
on the connector before crimping or soldering.

```text
Female panel connector, mating face

   1   2   3   4   5
    6   7   8   9  10
  11  12  13  14  15
```

Recommended box pinout:

| HD-15 pin | Box connector signal | User connects to | Inside the box | Notes |
|-----------|----------------------|------------------|----------------|-------|
| 1 | `CANH` | Flight controller CANH | SN65HVD230 `CANH` | Twist with pin 2 |
| 2 | `CANL` | Flight controller CANL | SN65HVD230 `CANL` | Twist with pin 1 |
| 3 | `CAN_GND` | Flight controller CAN GND | Box ground | CAN reference ground |
| 4 | `BOX_5V_IN_A` | FC/BEC 5 V output | Box 5 V input | Main power input |
| 5 | `BOX_5V_IN_B` | FC/BEC 5 V output, optional parallel | Same net as pin 4 | Use for lower voltage drop/current sharing |
| 6 | `BOX_GND_A` | FC/BEC ground | Box ground | Main power return |
| 7 | `GNSS_TX_TO_BOX` | GNSS TX | H743 `PA3` RX | Receiver output into filter |
| 8 | `GNSS_RX_FROM_BOX` | GNSS RX | H743 `PA2` TX | Filter output to receiver |
| 9 | `GNSS_VOUT_FUSED` | GNSS VCC/VIN | Fused or switched receiver power output | Output from box, not input |
| 10 | `GNSS_GND` | GNSS GND | Box ground | GNSS power/UART return |
| 11 | `SHIELD` | Cable shield/drain | Shell/chassis or single-point ground | Do not use as current return |
| 12 | `DR1_EVENT` | Optional LED/logger/status input | H743 `PB5` through protection/series resistor | 3.3 V logic pulse, optional |
| 13 | `CAM_MAV_TX_FROM_BOX` | OpenIPC camera RX | H743 `PA9` TX | 3.3 V MAVLink2 output from filter to camera |
| 14 | `CAM_MAV_RX_TO_BOX` | OpenIPC camera TX | H743 `PA10` RX | 3.3 V MAVLink2 input from camera |
| 15 | `BOX_GND_B` | FC/BEC ground, optional parallel | Box ground | Use with pin 5 for current sharing |

Build rules for this connector:

- Put the CAN transceiver inside the H743 box. The HD-15 connector carries
  only `CANH/CANL/GND` to the flight controller, not raw `PB8/PB9`.
- Keep `CANH/CANL` as a twisted pair all the way to the FC CAN port.
- Power the box from pins 4/6 at minimum. If the receiver or screen current is
  high, also wire pins 5/15 in parallel. Do not rely on CAN ground alone for
  box power return.
- `GNSS_VOUT_FUSED` on pin 9 is an output from the box to the receiver. It
  should come from a fuse, current limiter, or protected switch inside the box.
  Do not back-power the box through pin 9 unless you intentionally design that
  path.
- `GNSS_VOUT_FUSED` must match the receiver. Many GNSS modules accept 5 V on a
  `VCC`/`VIN` pin but use 3.3 V UART logic; raw receivers may require 3.3 V.
  Do not feed 5 V into a raw 3.3 V receiver. Label the selected voltage on the
  enclosure.
- Keep GNSS UART wires separate from the CAN twisted pair. For long runs, use
  a shielded or twisted GNSS cable and keep the 460800 baud noise margin in
  mind.
- Cross the camera UART: pin 13/H743 `PA9` TX goes to camera RX, and camera TX
  goes to pin 14/H743 `PA10` RX. Use 3.3 V logic and a common ground.
- Include a camera signal-ground return to box ground; pins 13/14 alone are not
  a complete UART connection. Do not use the cable shield as signal ground.
- Pins 13/14 carry camera UART data only. They do not power the camera; provide
  a suitable camera/LTE supply unless the enclosure has a separately engineered
  and protected camera-power output.
- All grounds are common inside the box, but keep CAN, box-power, and GNSS
  return conductors separated in the harness until they reach the connector.
- Do not power the H743 through USB-C and the HD-15 `BOX_5V_IN` pins at the
  same time unless the box has proper power ORing/back-feed protection.
- Use 120 ohm CAN termination only when this H743 node is at a physical end of
  the CAN bus. The connector pinout itself does not add termination.

## 4) USB-C flashing

For the unlocked development DroneCAN build:

```powershell
pio run -e weact_mini_h743vitx_dronecan_usb -t upload
```

For the signed secure app build behind the H743 bootloader:

```powershell
pio run -e weact_mini_h743vitx_dronecan_phaseb_app_usb -t upload
```

The secure-app USB environment writes the app slot at `0x08020000`. Use it
only when the H743 bootloader is already installed or when you intentionally
want an app image linked for that address.

To enter STM32 ROM DFU:

1. Hold `BOOT0`.
2. Press reset or power-cycle the WeAct H743.
3. Connect USB-C to the computer.
4. Release `BOOT0` after the board enumerates in DFU mode.

The Windows **AirDroper GNSS Filter** app version `2026.06.23.10` or newer can
update an already activated H743 over USB-C ROM DFU:

1. Set **Board target** to **H743 WeAct DroneCAN**.
2. Set **Update transport** to **USB-C ROM DFU**.
3. Enter the license key.
4. Put the H743 into ROM DFU with `BOOT0` + reset/power-cycle.
5. Click **Update**.

The `.exe` uses two USB-C update paths:

- **Readable/unlocked board:** writes the signed H743 application at
  `0x08020000` and metadata at `0x081E0000`; bootloader and option bytes are
  left unchanged.
- **RDP1-protected production board:** asks the operator to type the expected
  UID-short from the license preflight, removes RDP over USB DFU, requires a
  full power-cycle back into ROM DFU with `BOOT0` held, mass-erases flash,
  writes app + metadata + bootloader, verifies app/metadata readback, then
  restores H743 RDP Level 1.

RDP1 hides the physical UID until after erase, so the protected USB-C path is
intentionally operator-confirmed. If the typed UID-short is wrong or the dialog
is cancelled, the app stops before RDP removal and the board is not changed.

## 5) ST-Link flashing and provisioning

Development ST-Link upload:

```powershell
pio run -e weact_mini_h743vitx_dronecan -t upload
```

Windows app provisioning and updates:

1. Connect ST-Link V2 to the WeAct H743 SWD pins:

   | ST-Link V2 | WeAct H743 |
   |------------|------------|
   | `3V3` | `3V3` |
   | `GND` | `GND` |
   | `SWDIO` | `PA13` / `DIO` |
   | `SWCLK` | `PA14` / `CLK` |

2. Open **AirDroper GNSS Filter** app version `2026.06.23.10` or newer.
3. Set **Board target** to **H743 WeAct DroneCAN**.
4. Set **Update transport** to **ST-Link (SWD)** when updating through SWD.
5. Enter the license key.
6. Click **Activate** for a new board, or **Update** for an already activated
   H743 DroneCAN board.

The app reads the H743 UID at `0x1FF1E800`, requests `target=h743_dronecan`
from the server, flashes app `0x08020000`, metadata `0x081E0000`,
bootloader `0x08000000`, and then applies H743 RDP Level 1 with `RDP=0xBB`.
Version `2026.06.23.10+` writes the H743 application and metadata as separate
flash operations. If CubeProgrammer already erased the board and a repeated
mass erase fails, the app checks blank bootloader/app/metadata sentinels and
continues with write + verify when those slots are already blank.
The app's **Recover Board** button is target-aware. With **Board target** set
to **H743 WeAct DroneCAN**, it uses ST-Link/SWD, removes H743 RDP Level 1 with
the H743 RDP-only path, mass-erases flash, verifies `0x08000000` is blank, and
then tells you to run **Activate** again. Recovery is destructive: it removes
the firmware, license metadata, and saved settings from the connected H743.

If CubeProgrammer reports `DEV_TARGET_HELD_UNDER_RESET`, the H743 reset line is
being held low. Release the board RESET button, remove any suspect ST-Link
`RST/NRST` wire, disconnect the external CAN/GNSS/D-sub harness, power-cycle
the H743, and retry with only `3V3`, `GND`, `SWDIO`, and `SWCLK` connected.
If you do use ST-Link `RST/NRST`, connect it only to the WeAct `NRST/RST` pin.
Do not hold RESET continuously while clicking **Activate**, **Update**, or
**Recover Board**.

If STM32CubeProgrammer GUI connects with **Mode = Normal** and
**Reset mode = Software reset**, use app `2026.06.23.10` or newer. That build
uses the same `mode=NORMAL reset=SWrst` path for H743 before trying
under-reset and hotplug fallbacks.

Close STM32CubeProgrammer GUI before using the AirDroper app. App
`2026.06.23.10+` also checks for running STM32 flashing tools before hardware
access and stops with a clear message if one is still open. If
`STM32_Programmer_CLI.exe` remains after closing the GUI, end it from Windows
Task Manager and retry.

Production-style build:

```powershell
pio run -e weact_mini_h743vitx_dronecan_bootloader
pio run -e weact_mini_h743vitx_dronecan_phaseb_app
```

Target-aware CLI provisioning is still available:

```powershell
python tools/gnss_provision.py activate --target h743_dronecan --license GF-XXXX-XXXX-XXXX --server https://gps.airdroper.org
```

The H743 secure layout is separate from F401:

| Region | Address range | Purpose |
|--------|---------------|---------|
| Bootloader | `0x08000000 - 0x0801FFFF` | Secure bootloader |
| Active app | `0x08020000 - 0x080FFFFF` | Signed H743 DroneCAN firmware |
| Reserved stage | `0x08100000 - 0x081DFFFF` | Reserved for future DroneCAN firmware update |
| Metadata | `0x081E0000 - 0x081FFFFF` | Signed metadata / update state |

Do not flash H743 app or metadata images at F401 addresses.

Firmware update over the standard Mission Planner DroneCAN firmware-update
window is planned but not active in the current H743 firmware. Use the
AirDroper Windows app with **ST-Link (SWD)** or **USB-C ROM DFU** for H743
updates today. When DroneCAN self-update is implemented, already-deployed H743
boards will need one wired update first so the CAN-update-capable bootloader is
installed.

## 6) Flight controller setup

Configure the ArduPilot CAN port connected to the H743 transceiver:

| Parameter | CAN1 example | CAN2 example |
|-----------|--------------|--------------|
| CAN driver enable | `CAN_P1_DRIVER = 1` | `CAN_P2_DRIVER = 2` |
| DroneCAN protocol | `CAN_D1_PROTOCOL = 1` | `CAN_D2_PROTOCOL = 1` |
| CAN bitrate | `CAN_P1_BITRATE = 1000000` | `CAN_P2_BITRATE = 1000000` |
| GPS type | `GPS1_TYPE = 9` | `GPS1_TYPE = 9` (use `GPS2_TYPE` only for a deliberate second GPS instance) |
| GPS auto-config | `GPS_AUTO_CONFIG = 1` | Same global parameter |
| Optional GPS node lock | `GPS1_CAN_OVRIDE = 42` | Same (`GPS2_CAN_OVRIDE` only for a deliberate second GPS instance) |

`CAN_Px_DRIVER` selects a virtual driver. The table maps physical CAN1 to
driver 1 and physical CAN2 to driver 2; use `CAN_Dn_*` parameters matching the
driver number you assign. H743 DroneCAN `v0.2.0+` implements both virtual serial
ports. These examples use driver 1; for driver 2, replace every `CAN_D1_`
prefix below with `CAN_D2_`:

| Purpose | ArduPilot parameter | Value |
|---------|---------------------|-------|
| Enable DroneCAN serial | `CAN_D1_UC_SER_EN` | `1` |
| Camera port node | `CAN_D1_UC_S1_NOD` | `42` |
| Camera port index | `CAN_D1_UC_S1_IDX` | `0` |
| Camera port baud | `CAN_D1_UC_S1_BD` | `115` (115200) |
| Camera port protocol | `CAN_D1_UC_S1_PRO` | `2` (MAVLink2) |
| Filter port node | `CAN_D1_UC_S2_NOD` | `42` |
| Filter port index | `CAN_D1_UC_S2_IDX` | `1` |
| Filter port baud | `CAN_D1_UC_S2_BD` | `115` (115200) |
| Filter port protocol | `CAN_D1_UC_S2_PRO` | `2` (MAVLink2) |

Port S1/index `0` is a transparent bidirectional path between the OpenIPC
camera UART and ArduPilot. Port S2/index `1` is separate: it carries MAVLink2
generated by the H743 filter and returns FC telemetry used by its existing
EKF, barometer, arm-state, parameter, and status logic. Keeping separate serial
IDs prevents camera bytes from being interleaved with filter-owned MAVLink.
ArduPilot's `_PRO = 2` value is its serial-protocol setting; the standard
Targetted DSDL encodes MAVLink2 as on-wire protocol value `1`.

Some OpenIPC cameras can be held in their bootloader when bytes arrive on RX
during startup. If needed, set ArduPilot `MAV_TELEM_DELAY = 5` so MAVLink output
waits five seconds after FC boot (older ArduPilot versions may call this
`TELEM_DELAY`). Reboot the flight controller after changing CAN or DroneCAN
serial parameters.

### ArduPilot airspeed and compass setup

The FC sees both I2C sensors as DroneCAN devices from node `42`; do not select
the FC's local I2C MS4525 backend. After the H743 node and sensors are powered:

1. Set the chosen FC airspeed instance to DroneCAN: normally
   `ARSPD_TYPE = 8`. If another airspeed sensor already occupies instance 1,
   use the matching `ARSPD2_TYPE`, `ARSPD3_TYPE`, and so on.
2. Set the matching `ARSPDx_USE` according to the vehicle and intended control
   strategy. For Plane this is normally enabled only after a successful bench
   check and airspeed calibration; follow the current ArduPilot airspeed setup
   procedure for offset, ratio, tube order and pre-arm validation.
3. Allow ArduPilot to discover the DroneCAN compass. In Mission Planner open
   `Setup -> Mandatory Hardware -> Compass`, confirm a compass from node `42`
   appears, mark/use it as external as appropriate, and assign its priority.
4. Set or auto-detect the HMC5983 orientation, then perform a complete compass
   calibration in the installed vehicle. Never copy offsets from another
   airframe or sensor. Confirm all compass axes respond in the correct direction
   while rotating the aircraft and inspect motor-current interference before
   relying on it for yaw.

ArduPilot automatically identifies DroneCAN airspeed and compass publishers;
there is no extra virtual-serial mapping for these sensors. A healthy MS4525
sample is published as `uavcan.equipment.air_data.RawAirData` at up to 20 Hz.
A healthy HMC5983 sample is published as
`uavcan.equipment.ahrs.MagneticFieldStrength2` with sensor ID `0` at up to
25 Hz. The sensor messages share the existing node ID and CAN transceiver with
GPS and both MAVLink tunnels.

Classic CAN carries only seven payload bytes in each multi-frame transport
frame. Keep ArduPilot stream rates modest: camera full duplex plus a chatty
filter port and the 20/25 Hz sensor publications can approach the capacity of a
1 Mbps bus. GPS and NodeStatus have higher priority, while bounded MAVLink
queues shed overload. A red `MAV` row or nonzero `ERR` row indicates
loss/overload; reduce stream rates before flight.
A yellow `MAV` row means queued data expired after a stalled link.
Partial camera data is batched for at most 10 ms to limit CAN framing overhead.
If either camera direction makes no progress for 500 ms, bytes still in the
firmware queues are discarded instead of being replayed after a link outage.
Frames already handed to the FDCAN controller cannot be recalled.

The H743 firmware uses static DroneCAN node ID `42` and CAN bitrate `1 Mbps`.
It publishes native DroneCAN GPS messages:

- `uavcan.protocol.NodeStatus`
- `uavcan.protocol.GetNodeInfo` response
- `uavcan.equipment.gnss.Fix2`
- `uavcan.equipment.gnss.Auxiliary`
- `uavcan.equipment.air_data.RawAirData` for MS4525 differential pressure and
  sensor temperature, up to 20 Hz
- `uavcan.equipment.ahrs.MagneticFieldStrength2` for HMC5983 magnetic field,
  sensor ID `0`, up to 25 Hz
- `uavcan.tunnel.Targetted` for the two MAVLink2 virtual serial ports

The MAVLink2 streams are tunneled; raw GNSS NMEA, UBX, and SBF receiver streams
are not. GPS remains native `Fix2/Auxiliary`, and the physical FC GPS UART stays
disabled.

### Septentrio Mosaic X5 SBF input

H743 DroneCAN firmware `v0.1.9+` can parse Mosaic X5 native SBF on the GNSS
UART when `GNSS_TYPE=2`. Configure the Mosaic serial stream in RxTools/Web UI
for `460800`, 8N1, and SBF output. Enable these blocks on the stream wired to
H743 `PA3/PA2`:

| SBF block | Recommended rate | Firmware use |
|-----------|------------------|--------------|
| `PVTGeodetic` | 5-10 Hz | fix mode, position, MSL/ellipsoid height, velocity, satellites, receiver clock |
| `DOP` | 1-5 Hz | HDOP/VDOP/PDOP/TDOP for DroneCAN and guards |
| `ReceiverTime` | 1 Hz | UTC timestamp in DroneCAN `Fix2` |
| `MeasEpoch` | 1-5 Hz | C/N0/SNR guard |
| `PosCovGeodetic` | 1-5 Hz | position covariance in DroneCAN `Fix2` |
| `VelCovGeodetic` | 1-5 Hz | velocity covariance in DroneCAN `Fix2` |

The H743 firmware still accepts Mosaic NMEA in `GNSS_TYPE=2`, but SBF is the
preferred H743 DroneCAN profile because it carries velocity, DOP, covariance,
receiver time, and C/N0 in a binary format without needing a serial GPS driver
on the flight controller.

For spoof-confidence scoring, Mosaic SBF `MeasEpoch` contributes the C/N0
temporal-correlation signal. It does not enable the pseudorange-residual signal:
that score remains u-blox-only because it depends on UBX `NAV-SAT` `prRes`.

Because the FC receives native DroneCAN GPS, H743 DroneCAN is not byte-for-byte
GPS packet pass-through. The firmware parses the receiver stream and publishes
the same live fix values in DroneCAN units. It does not generate synthetic GPS
coordinates, blend coordinates, or rewrite raw NMEA/UBX/SBF packets; in DR1 it
suppresses `Fix2/Auxiliary` instead of sending altered GPS data.

`GPS_AUTO_CONFIG=1` is ArduPilot's default serial-only GPS auto-config mode and
is the safest setting for this filter. H743 DroneCAN firmware `v0.1.2` and
newer responds to ArduPilot's optional DroneCAN `param.GetSet` queries for
`GPS_TYPE`/`GPS1_TYPE`, so `GPS_AUTO_CONFIG=2` will not block GPS data.

If the CAN bus has more than one DroneCAN GPS-like node, set the matching
`GPSx_CAN_OVRIDE` parameter to `42` so ArduPilot binds that GPS instance to the
filter's static node ID. On a single-GPS bus this is optional.

## 7) Mission Planner Params

H743 DroneCAN firmware `v0.1.4` and newer exposes the spoofing/tuning
parameters through the DroneCAN parameter service. H743 DroneCAN firmware
`v0.1.5` and newer also exposes the same parameters over the H743 USB-C COM
port as a direct MAVLink management link.

With S2/index `1` configured, the H743's own MAVLink2 also reaches the flight
controller and FC telemetry returns to the filter. A GCS connected through the
FC can select filter system ID `42` where its interface supports MAVLink system
selection. The DroneCAN node Params window remains the most direct on-aircraft
configuration path.

### Option A: DroneCAN through the flight controller

Use this while the board is on the aircraft CAN bus:

1. Open Mission Planner.
2. Go to **SETUP -> Optional Hardware -> DroneCAN/UAVCAN**.
3. Select the active CAN driver, usually `MAVLinkCAN1`, and press **Connect**.
4. Wait for node `42` named `org.airdroper.gnss_filter.h743_dronecan`.
5. Press **Menu** on node `42`, then open **Parameters**.
6. Edit the tune row, press **Write Params**, then press **Commit Params**.
7. Reboot the H743 and re-open node `42` Params if you want to confirm the
   value persisted.

### Option B: Direct USB-C to the H743

Use this on the bench when you want the familiar Mission Planner MAVLink
parameter screen without using any flight-controller serial port:

1. Power the H743 normally, not in `BOOT0` ROM DFU mode.
2. Connect the H743 USB-C port to the computer.
3. In Mission Planner, select the new H743 COM port and `115200` baud.
4. Click **Connect**. Mission Planner should see system ID `42`.
5. Open **CONFIG -> Full Parameter Tree** or **Full Parameter List**.
6. Edit the spoofing/tuning values and click **Write Params**.
7. Wait a few seconds for the firmware to save, then reboot/reconnect and
   verify the value if needed.

This USB-C mode is a normal application management port. It is separate from
USB-C ROM DFU flashing: hold `BOOT0` only when updating firmware, and leave
`BOOT0` released when editing parameters.

In the DroneCAN node Params window, the first two rows, `GPS_TYPE` and
`GPS1_TYPE`, are compatibility rows for ArduPilot and are locked to `9`
(`DroneCAN GPS`). Spoofing/tuning rows start after those rows. In the direct
USB-C MAVLink parameter screen, the list starts directly with the
spoofing/tuning rows. The tune names match the F401 firmware, such as
`BOOT_NSATS`, `BOOT_NHDOP`, `RJ_BASE_M`, `SP_JMP_MPS`, `SNR_EN`, `FENCE_RAD`,
and `GNSS_TYPE`.

`UBX_RESET` is a one-shot command, not a saved setting:

- set `UBX_RESET=1` for a u-blox hot start
- set `UBX_RESET=2` for a u-blox cold start
- set `UBX_RESET=3` to clear u-blox config and reinitialize

H743 DroneCAN keeps only the raw FC GPS UART settings locked off:

- `FCGPS_UART = 0`
- `FCGPS_FWD = 0`

`RJ_REQEKF` and the other FC-telemetry-dependent guards remain available
because S2/index `1` supplies the filter with flight-controller MAVLink2.

The firmware still auto-saves changed values after a short debounce, but
Mission Planner's **Commit Params** button is the explicit save path.

## 8) Display behavior

H743 DroneCAN `v0.4.0` redesigns the onboard 80 x 160 ST7735 color TFT with a
high-contrast, professional dark interface. The display is not an OLED and has
no touch input or page buttons.

At power-up, an animated status ring and progress rail appear immediately while
the receiver is initialized. The boot scene uses rounded tiles for firmware and
node status, then changes from GNSS initialization to `READY` / `BOOT GUARD`
before opening the dashboard. After the splash, the hero remains
`FILTER CHECK / GUARD` for
the real configurable startup spoof-guard interval; it cannot report
`FILTER ONLINE / RUN` while those checks are still delayed. `USB CONFIG` means
the normal application USB-C management link is available. It does not mean
that ROM DFU is active;
entering ROM DFU still requires holding `BOOT0` while resetting or powering the
board.

The dashboard keeps three areas visible:

- an activity header for the product, CAN, and MAVLink links
- a large custom striped and outlined `OK`, `!!`, or `XX` hero with
  `FILTER ONLINE`, `FILTER CHECK`, `FILTER BLOCK`, or `FC ALERT` beneath it,
  plus a short reason such as `RUN`, `GPS`, `CAN ERR`, `SENSOR`, or the active
  DR1 cause
- a persistent footer showing recent GPS publication as `PUB+`, an open gate
  without a recent Fix2 as `PUB?`, or blocked/unavailable publication as
  `PUB-`, followed by `DR0`/`DR1` and this filter's DroneCAN node such as `N42`

`PUB+` means a recent Fix2 transfer was accepted into the filter's local
DroneCAN transmit queue. It is not an acknowledgement from the FC. Confirm FC
reception independently in DroneCAN/Mission Planner telemetry before flight.

The center of the dashboard uses proportional body text, compact icons,
rounded information tiles, gradient health rails, and segmented activity rails
across four automatic pages:

| Page | Information shown |
|------|-------------------|
| **Overview** | Fresh GPS fix/satellites, FC node health and generic UAVCAN node mode, ArduPilot `NotifyState`, arm state, and safety state |
| **Sensors** | MS4525 and HMC5983 freshness, differential pressure, sensor temperature, and magnetic-field magnitude |
| **Links** | CAN and aggregate camera/filter MAVLink TX/RX counters, CAN errors, and MAVLink dropped/expired counters |
| **System** | I2C error/recovery counters, firmware version/build, uptime, or Mosaic SBF accepted/bad-CRC counters |

Page dots and a footer underline identify the active page. When the filter is
healthy and the FC is known to be disarmed, each page remains visible for about
five seconds and the UI uses an eased five-frame slide to the next page. There
are no controls to select a page manually.
Automatic page rotation and sliding stop when attention is needed. A sensor,
CAN, or MAVLink warning pins the Sensors or Links page that explains it; bad FC
NodeStatus, GPS/guard warnings, or an armed FC pin Overview. A filter block or
high-priority ArduPilot notification instead activates a dedicated alert
takeover in the center area while the hero state, subtle activity animation,
and footer remain visible.
Rotation also waits for a fresh FC arming-status broadcast that positively
confirms disarmed state. If arm state is unknown or the FC is armed, Overview
uses its third row to summarize a hidden sensor/link warning. Simultaneous
filter and FC alerts are labelled `DUAL ALERT` so neither fault is concealed.

The redesign changes presentation only. Display state cannot open a spoofing
gate or reroute traffic: DR0/DR1 enforcement, DroneCAN GPS and sensor
publication, the OpenIPC tunnel, and the filter's own MAVLink2 virtual port keep
their existing behavior.

For a pixel-exact desktop review of all pages and animations, run:

```powershell
python tools/render_h743_display_preview.py
```

Then open `dist/h743_display_preview.html`. Its scenarios use the same portable
C++ RGB565 renderer that is linked into the firmware; the browser does not
recreate the panel graphics with HTML fonts.

The Overview page shows generic UAVCAN node modes rather than exact ArduPilot
flight-mode names such as Loiter, Auto, Guided, or RTL. MAVLink tunnelling is
independent of what the display currently shows.

Treat the screen as a convenient local diagnostic, not as authoritative flight
instrumentation. Its counters and freshness indicators do not replace
Mission Planner pre-arm checks, DroneCAN inspection, sensor calibration, or
flight-log review. In particular, magnetic-field magnitude is not a calibrated
heading, and a `FILTER ONLINE` display does not prove correct compass
orientation, pitot plumbing, CAN termination, or MAVLink routing.

By default `FILTER_DRONECAN_FC_NODE_ID=0`, so the tunnel locks to the first
valid Targetted transfer addressed to node `42`. After that, tunnel and status
traffic from other nodes is ignored. On a busy multi-node bus, set
`FILTER_DRONECAN_FC_NODE_ID` at build time to lock the tunnel and display to one
FC node from boot.

## 9) DR0 and DR1 behavior on DroneCAN

The spoofing/guard logic is the same GNSS-side protection logic as the UART
firmware, but the output transport is different.

In DR0:

- the firmware publishes DroneCAN `Fix2` on each fresh GNSS update, capped at
  10 Hz
- it publishes `Auxiliary` at 1 Hz
- `NodeStatus` stays online

In spoof/fault DR1:

- `Fix2` and `Auxiliary` are suppressed
- the flight controller stops receiving fresh GPS from this node
- `NodeStatus` continues at 1 Hz with warning health and vendor status bits
- the display locks to the red `BLOCK` alert view with the active reason, while
  its footer shows `PUB-` and `DR1`

No-fix, low satellites, boot guard, or GNSS reconfiguration can also suppress
`Fix2/Auxiliary`, including latched no-fix/low-sat DR1 internally, but those
states keep `NodeStatus` health `OK` and report the output block only through
vendor status bits and the onboard screen. This avoids ArduPilot
`PreArm: DroneCAN: Node 42 unhealthy!` while the GPS is simply not ready yet.

Both MAVLink2 virtual ports remain active in DR0 and DR1. DR1 blocks only the
native GPS `Fix2/Auxiliary` output; it does not cut the OpenIPC camera tunnel or
the filter-owned MAVLink2 stream. S2/index `1` preserves FC telemetry input,
EKF-status and barometer comparisons, filter `STATUSTEXT`/`NAMED_VALUE`
logging, parameter traffic, and the other existing MAVLink behavior. The
physical `FCGPS_FWD` raw UART bypass remains unavailable.

The MS4525 `RawAirData` and HMC5983 `MagneticFieldStrength2` publications are
also independent of DR0/DR1. A spoofing decision suppresses only GNSS
`Fix2/Auxiliary`; it does not intentionally remove airspeed, compass,
NodeStatus, camera MAVLink, or filter MAVLink. A failed or disconnected I2C
sensor stops producing its own valid sensor publication and must be treated as
a separate pre-arm/maintenance fault.

GNSS-only guards remain active: no-fix, low satellites, position jumps,
altitude rate/jump, SNR, hemisphere, geofence, heading reversal, GPS time
sanity, velocity-position consistency, and receiver clock jump when available.

## 10) Bring-up checklist

1. Flash `weact_mini_h743vitx_dronecan_usb` or `weact_mini_h743vitx_dronecan`.
2. Wire GNSS to `PA2/PA3`.
3. Cross the 3.3 V OpenIPC UART: camera TX -> `PA10`, `PA9` -> camera RX, plus
   common ground and an appropriately rated separate camera supply.
4. On a separate keyed connector, wire both sensors to shared `PB10` SCL,
   `PB11` SDA, 3.3 V and ground. Confirm the MS4525 complete ordering code and
   HMC5983 identity before power-up.
5. Wire `PB9/PB8` through the CAN transceiver to the FC CAN port.
6. Configure ArduPilot CAN driver, DroneCAN protocol, 1 Mbps bitrate, and
   `GPS1_TYPE=9`.
7. Enable DroneCAN serial, mapping S1 to node `42`/index `0`/115/MAVLink2 and
   S2 to node `42`/index `1`/115/MAVLink2.
8. Set the FC airspeed instance to DroneCAN (`ARSPD_TYPE=8` for instance 1),
   confirm the node-42 compass appears, and reboot the flight controller.
9. Confirm the H743 screen lights and shows `GNSS FILTER`.
10. Confirm the DroneCAN node appears as node ID `42` in DroneCAN/SLCAN tooling.
11. Confirm ArduPilot reports a DroneCAN GPS and airspeed instance, a node-42
    compass, camera MAVLink2 reaches
    the FC, and filter system ID `42` is visible through MAVLink routing.
12. With the pitot still and both ports at equal pressure, calibrate zero;
    gently apply differential pressure and verify positive, stable airspeed.
13. Calibrate the compass after final installation, check axis/orientation and
    motor-current interference, and verify it remains healthy for several
    minutes with the camera/LTE transmitter active.
14. Trigger a bench DR1 condition and confirm `Fix2/Auxiliary` stop while
    `NodeStatus` stays online.
15. Confirm airspeed, compass and both MAVLink2 paths remain online during DR1,
    then clear the condition and confirm GPS publishing resumes after rejoin.

## 11) Troubleshooting

### Node does not appear on DroneCAN

- Confirm CAN is enabled on the correct FC CAN port.
- Confirm `CAN_Dx_PROTOCOL = 1` and bitrate is `1000000`.
- Confirm `PB9 -> TXD` and `PB8 <- RXD`.
- Confirm transceiver `VCC` is 3.3 V and all grounds are common.
- Confirm CANH/CANL are not swapped.
- Confirm termination exists at both physical ends of the bus and not in the
  middle.

### Node appears but FC does not get GPS

- Confirm `GPS1_TYPE=9` or the matching GPS instance type is set to DroneCAN.
- Confirm `GPS_AUTO_CONFIG=1` on firmware older than H743 DroneCAN `v0.1.2`.
- If there are multiple DroneCAN GPS nodes, set `GPS1_CAN_OVRIDE=42` or the
  matching GPS instance override.
- Confirm the GNSS receiver has a fresh valid fix; the Overview page should
  show `GPS FIX` rather than `GPS STALE` or `GPS NO FIX`.
- Confirm the persistent footer shows `PUB+` and `DR0`, not `PUB-` / `DR1`.
- `PUB?` means the publication gate is open but no recent Fix2 was accepted
  into the local DroneCAN transmit queue; check GPS freshness and CAN readiness
  before flight. `PUB+` still is not proof that the FC received the transfer.
- Confirm the hero card is not `BLOCK` with `GNSSCFG`, `GPS`, `SOUTH`, `FENCE`,
  `NOFIX`, `SATS`, `JUMP`, or another DR1 cause label.

### Camera or filter MAVLink2 does not cross DroneCAN

- Confirm `CAN_D1_UC_SER_EN=1` (or the matching `CAN_D2_` parameter).
- Confirm S1 is node `42`, index `0`, baud `115`, protocol `2`; confirm S2 is
  node `42`, index `1`, baud `115`, protocol `2`.
- Confirm camera TX goes to `PA10`, H743 `PA9` goes to camera RX, both sides use
  3.3 V UART logic, and signal ground is common.
- Confirm the OpenIPC UART is configured for MAVLink2 at 115200 baud.
- If the camera fails to boot only when the UART is attached, try
  `MAV_TELEM_DELAY=5` and verify camera power integrity.
- Do not diagnose a DR1 GPS block as a tunnel failure: the MAVLink2 virtual
  ports intentionally stay active while `Fix2/Auxiliary` are suppressed.

### Airspeed or compass is missing/unhealthy

- Confirm the sensor firmware options are enabled in the H743 DroneCAN build,
  then confirm `PB10 -> SCL`, `PB11 <-> SDA`, 3.3 V power and common ground.
- Measure idle SCL/SDA. Both must pull up to approximately 3.3 V, never 5 V.
  Disconnect power immediately if either line exceeds the H743 I/O voltage.
- Check for one sensible effective set of pull-ups, shorts, swapped SCL/SDA,
  excessive cable length, electrical noise and duplicate I2C addresses.
- MS4525: confirm the full code `4525DO-DS3AI001DP` and address `0x28`.
  Equalize both ports for zero calibration, then apply a small known pressure
  and confirm the indicated sign and magnitude. Do not compensate for the wrong
  sensor range using only `ARSPD_RATIO`.
- HMC5983: confirm address `0x1E` and identity `H43`. If a cheap module is not
  accepted or calibrates inconsistently, assume it may be a clone rather than
  weakening the identity check.
- Confirm `ARSPDx_TYPE=8` selects DroneCAN on the FC. Do not use type `1`, which
  is the FC's own local-I2C MS4525 driver.
- For the compass, inspect Mission Planner's detected compass list and device
  IDs, remove stale missing devices if necessary, set the correct priority and
  orientation, then recalibrate in the final installed position.
- A DR1 GPS block does not disable these sensors. If airspeed or compass stops
  in DR1, diagnose I2C integrity, CAN load/errors and sensor health separately.

### Screen does not show FC arm or safety state

- Confirm the FC is on the same CAN bus and DroneCAN is running.
- If the bus has many nodes, rebuild with `FILTER_DRONECAN_FC_NODE_ID=<fc id>`.
- Some FC status rows depend on ArduPilot broadcasts. GPS publishing does not
  require those rows to be present.

### Node 42 Params only shows GPS_TYPE/GPS1_TYPE

- Update the H743 DroneCAN firmware to `v0.1.4` or newer.
- Disconnect/reconnect the Mission Planner DroneCAN/UAVCAN page and reopen
  node `42` Params.
- If the value list still looks stale, close and restart Mission Planner.

### USB-C Mission Planner connection does not show params

- Update the H743 DroneCAN firmware to `v0.1.5` or newer.
- Do not hold `BOOT0`; USB-C parameter editing works only in the normal app,
  not in ROM DFU mode.
- Select the H743 USB COM port directly in Mission Planner at `115200`.
- If Mission Planner is already connected to the flight controller telemetry
  link, disconnect that session first, then connect to the H743 USB COM port.

### Screen turns off after boot

- If the board is on H743 DroneCAN firmware `v0.1.0`, the app boots and the
  blue LED blinks every few seconds, but the screen stays black, update to
  H743 DroneCAN `v0.1.1` or newer. `v0.1.1` fixes the WeAct LCD backlight
  polarity (`PE10` is active-low).
- The firmware turns the display backlight off if SPI display writes fail, so
  a bad screen connection cannot keep delaying the flight loop.
- Recheck the onboard display pins, especially `PE12`, `PE14`, `PE11`, `PE13`,
  and `PE10`. Do not try to reset the LCD with `PF0`; use the board reset.
- DroneCAN GPS publishing and guard logic continue without the screen.

### USB-C ROM DFU upload does not start

- Make sure you entered ROM DFU with `BOOT0` held during reset/power-up.
- Try a known data-capable USB-C cable.
- Disconnect ST-Link or other tools that may hold the MCU in reset.
- If the chip is RDP Level 1 locked, raw PlatformIO app-only ROM DFU upload
  cannot update it. Use the desktop app's **USB-C ROM DFU** update path for an
  already activated H743, or use ST-Link/manual recovery when intentionally
  recovering a development board.

## 12) What H743 DroneCAN still intentionally does not do

- no DroneCAN firmware update protocol
- no raw NMEA/UBX/SBF GNSS tunnel over CAN; GPS uses native `Fix2/Auxiliary`
- no physical FC GPS UART or `FCGPS_FWD` bypass
- no exact ArduPilot flight-mode names on the screen
- no direct connection from H743 FDCAN pins to the flight controller without a
  CAN transceiver

For normal F401 UART operation, use the rest of the user documentation. For
H743 DroneCAN, this page is the source of truth.

## 13) Protocol references

- [Official WeAct MiniSTM32H7xx V12 schematic](https://github.com/WeActStudio/MiniSTM32H7xx/blob/master/Hardware/STM32H7xx%20SchDoc%20V12.pdf)
- [Official WeAct ST7735 LCD driver](https://github.com/WeActStudio/MiniSTM32H7xx/blob/master/SDK/HAL/STM32H743/03-LCD_Test/Drivers/BSP/ST7735/lcd.c)
- [DroneCAN `uavcan.tunnel.Targetted` DSDL](https://github.com/DroneCAN/DSDL/blob/master/uavcan/tunnel/3001.Targetted.uavcan)
- [DroneCAN `uavcan.equipment.air_data.RawAirData` DSDL](https://github.com/DroneCAN/DSDL/blob/master/uavcan/equipment/air_data/1027.RawAirData.uavcan)
- [DroneCAN `uavcan.equipment.ahrs.MagneticFieldStrength2` DSDL](https://github.com/DroneCAN/DSDL/blob/master/uavcan/equipment/ahrs/1002.MagneticFieldStrength2.uavcan)
- [ArduPilot DroneCAN serial-port setup](https://ardupilot.org/sub/docs/common-dronecan-serial.html)
- [ArduPilot DroneCAN setup and automatically detected sensor types](https://ardupilot.org/copter/docs/common-uavcan-setup-advanced.html)
- [ArduPilot advanced compass setup](https://ardupilot.org/copter/docs/common-compass-setup-advanced.html)
- [TE Connectivity `4525DO-DS3AI001DP` product data](https://www.te.com/en/product-4525DO-DS3AI001DP.html)
- [OpenIPC FPV/UART guidance](https://github.com/OpenIPC/wiki/blob/master/en/fpv.md)
