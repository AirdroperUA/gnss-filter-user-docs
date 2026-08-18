# WeAct H743 DroneCAN Guide

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

This page is the complete H743-specific setup path for the WeAct Studio
MiniSTM32H743VITX board with a 3.3 V CAN transceiver such as the SN65HVD230.
The production/default build publishes GPS and MS4525DO airspeed to ArduPilot
while carrying MAVLink2 over the same DroneCAN connection instead of using
flight-controller UARTs. It compiles the HMC5983 driver out. HMC5983 compass
publication is available only in the optional direct-flash `*_dronecan_mag`
variant described below.

## 1) Supported H743 firmware families

| Firmware environment | Purpose | Upload path |
|----------------------|---------|-------------|
| `weact_mini_h743vitx` | Standalone H743 UART development build | ST-Link |
| `weact_mini_h743vitx_usb` | Same standalone UART build | USB-C ROM DFU |
| `weact_mini_h743vitx_dronecan` | H743 DroneCAN GPS build | ST-Link |
| `weact_mini_h743vitx_dronecan_usb` | Same DroneCAN GPS build | USB-C ROM DFU |
| `weact_mini_h743vitx_dronecan_mag` | Optional HMC5983-enabled DroneCAN build | ST-Link |
| `weact_mini_h743vitx_dronecan_mag_usb` | Same optional HMC5983-enabled build | USB-C ROM DFU |
| `weact_mini_h743vitx_dronecan_bootloader` | H743 DroneCAN secure bootloader | ST-Link |
| `weact_mini_h743vitx_dronecan_phaseb_app` | UID-patchable H743 app template at `0x08020000` | Provisioner only |
| `weact_mini_h743vitx_dronecan_phaseb_app_usb` | Identical build-validation template | Provisioner only |

The default direct-flash builds and both signed phase-B production templates
set `FILTER_DRONECAN_HMC5983_ENABLE=0`; node 42 publishes no
`MagneticFieldStrength2` from them. There is currently no production/signed
phase-B magnetometer variant. Select a `*_dronecan_mag` environment only for a
deliberate direct-flash installation with a physically fitted HMC5983.

The recommended H743 flight configuration is the DroneCAN family:

- GNSS input on `PA2/PA3`
- CAN to the flight controller on `PB8/PB9` through a CAN transceiver
- OpenIPC camera MAVLink2 on `PA10` RX / `PA9` TX at `115200` baud
- shared I2C2 sensor bus on `PB10` SCL / `PB11` SDA for the default MS4525DO
  differential-pressure sensor; an HMC5983 may share it only with a
  `*_dronecan_mag` build
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
| HMC5983 magnetometer | Optional, and used only with a direct-flash `*_dronecan_mag` build; genuine device at I2C address `0x1E` required |
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
| Sensor I2C clock | `PB10` | MS4525DO `SCL`; optional HMC5983 `SCL` only for `*_dronecan_mag` | I2C2, shared bus |
| Sensor I2C data | `PB11` | MS4525DO `SDA`; optional HMC5983 `SDA` only for `*_dronecan_mag` | I2C2, shared bus |
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

### Shared I2C2 airspeed/optional-compass connector (`SENSOR_I2C`)

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
sensor. The default build uses this bus for the MS4525DO. When a direct-flash
`*_dronecan_mag` build and HMC5983 are deliberately used, the two sensors are
wired in parallel on the same bus; they are not daisy-chained through CAN.

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

Only the optional direct-flash `*_dronecan_mag` builds enable the magnetometer
driver. It expects HMC5983 address `0x1E` and identification bytes
`H43`. Numerous modules sold as HMC5983 use HMC5883-compatible or unmarked
clones. An address scan alone is not proof of the device. This firmware rejects
the wrong identity, but a module that imitates `H43` can still have different
gain, noise or temperature behavior; use a traceable part and bench-compare it
against a known compass.

For that optional variant, mount the HMC5983 rigidly and record its axis orientation. Prefer an external
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

Build the secure-app template behind the H743 bootloader with:

```powershell
pio run -e weact_mini_h743vitx_dronecan_phaseb_app_usb
```

The phase-B environments deliberately reject `-t upload`. Their binary still
contains an unprovisioned UID sentinel and is not a complete secure bundle.
Use the AirDroper provisioning app for licensed ST-Link/SWD or USB-C ROM DFU
updates; it obtains a UID-bound application, matching signed metadata, and the
correct bootloader layout before modifying a protected board.

To enter STM32 ROM DFU:

1. Hold `BOOT0`.
2. Press reset or power-cycle the WeAct H743.
3. Connect USB-C to the computer.
4. Release `BOOT0` after the board enumerates in DFU mode.

The Windows **AirDroper GNSS Filter** app version `2026.08.02.1` or newer can
update an already activated H743 over USB-C ROM DFU:

1. Set **Board target** to **H743 WeAct DroneCAN**.
2. Set **Update transport** to **USB-C ROM DFU**.
3. Enter the license key.
4. Put the H743 into ROM DFU with `BOOT0` + reset/power-cycle.
5. Click **Update**.

The `.exe` first reads and parses the physical RDP option byte. It refuses to
write when that read fails, is unparseable, or reports irreversible RDP2. Both
readable RDP0 and protected RDP1 boards then use the same secure destination:
a mass erase, the complete prevalidated application at `0x08020000`, metadata
at `0x081E0000`, the matching bootloader at `0x08000000`, and final RDP1.

An RDP1 board additionally requires the expected UID-short from license
preflight, RDP removal, a verified RDP0 readback, and a physical re-read of the
exact UID before any firmware is written. Application/metadata readback is
verified before the bootloader and lock are applied. A separate final
option-byte read must prove RDP1; if it does not, the app does not claim or
report a successful update.

RDP1 hides the physical UID until after erase, so the protected USB-C path is
intentionally operator-confirmed. If the typed UID-short is wrong or the dialog
is cancelled, the app stops before RDP removal and the board is not changed.
The H743 verifier does not write option bytes itself: it refuses to boot an
unlocked production image. Provisioning/update tooling must apply and verify
`RDP=0xBB`. The production bootloader also rejects signed H743 applications
older than the v0.4.0 anti-rollback floor.

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
mass erase fails, app `2026.07.23.1+` uploads and verifies that every written
region (and the parameter-journal sectors) reads fully blank before it
continues with write + verify.

**Mass erase and the firmware watchdog (app `2026.07.23.1+`).** The installed
H743 firmware arms a 15-second hardware watchdog at boot, and that watchdog
keeps counting even while the programmer holds the chip halted. An H743
full-flash erase takes long enough that the watchdog can reset the chip
mid-erase, which CubeProgrammer reports as
`Mass erase operation failed. Please verify flash protection` even though the
board is NOT protected (RDP reads `0xAA`). App `2026.07.23.1+` prevents this
automatically: every H743 erase first freezes the firmware watchdog for the
debug session (a `DBGMCU` register write in the same CubeProgrammer call). If
the erase still fails, the app walks you through a **BOOT0 power cycle**:

1. Remove power from the H743.
2. Hold the **BOOT0** button on the WeAct board.
3. Reconnect power while still holding BOOT0.
4. Release BOOT0 about one second after power-up.

With BOOT0 held during power-up the chip starts its built-in ROM bootloader
instead of the installed firmware, so no watchdog runs and the erase always
has a clean chip. Firmware `v0.4.3` and newer also freezes the watchdog under
any debugger on its own, so boards flashed with it do not need any of this.

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

NRST wiring note: the 4-wire hookup above is the supported default. A
*correctly* wired ST-Link `RST` -> WeAct `NRST` is also fine and even helps —
it lets CubeProgrammer connect "under reset", which stops the installed
firmware (and its watchdog) from running before an erase. Remove the wire only
when it causes `DEV_TARGET_HELD_UNDER_RESET` (wrong pin, damaged wire, or the
probe holding reset low). The generic F401 advice in
[10_self_install.md](10_self_install.md) to "wire NRST when connection fails"
applies to H743 only with this caveat.

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
| Active app | `0x08020000 - 0x080BFFFF` | Signed H743 DroneCAN firmware |
| Bank 1 reserve | `0x080C0000 - 0x080FFFFF` | Growth/guard area |
| Reserved stage | `0x08100000 - 0x0819FFFF` | Reserved for future DroneCAN firmware update |
| Parameter journals | `0x081A0000 - 0x081DFFFF` | Power-fail-safe parameter storage |
| Metadata | `0x081E0000 - 0x081FFFFF` | Signed metadata / update state |

Do not flash H743 app or metadata images at F401 addresses.

Firmware update over the standard Mission Planner DroneCAN firmware-update
window is planned but not active in the current H743 firmware. Use the
AirDroper Windows app with **ST-Link (SWD)** or **USB-C ROM DFU** for H743
updates today. When DroneCAN self-update is implemented, already-deployed H743
boards will need one wired update first so the CAN-update-capable bootloader is
installed.

## 6) Flight controller setup

For **ArduPlane 4.6.3 on CAN1**, the recommended starting point is
`presets/arduplane_FC_4.6.3_h743_dronecan_CAN1_core.param` in the
[AirDroper Mission Planner Mod](https://gps.airdroper.org/download/mission-planner-mod).
Load it into the **flight controller (normally SYSID 1), never node 42**. On a
fresh disabled-CAN setup, Mission Planner exposes enable-dependent parameters
in stages: Load/Write, reboot, reconnect/refresh, and load the same file again
until there is no missing-parameter popup and all ten values read back exactly.
This may require three imports. The core file deliberately preserves CAN2,
camera S1, airspeed, optional compass, EKF, arming, SR streams, and `GPS_AUTO_CONFIG`;
complete every manual safety check written inside it. The tables below remain
the reference for deliberate CAN2 or optional-accessory configurations.

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

**The index-`1` (filter) tunnel, plus a live `EKF_STATUS_REPORT` on it, is a
HARD PRECONDITION for any GPS output from node `42`.** It is not a camera
convenience, an optional enrichment, or a logging nicety. The filter is
fail-closed on flight-controller telemetry freshness: it publishes
`Fix2`/`Auxiliary` only while it is receiving BOTH a FC `HEARTBEAT` (within
3000 ms) and a FC `EKF_STATUS_REPORT` within its own freshness window. If
either message is missing, the filter suppresses BOTH `Fix2` AND `Auxiliary`,
so the flight controller receives NO GPS at all from this node - not degraded
GPS, not unfiltered GPS, none. Configure `CAN_D1_UC_S2_*` even if you never
intend to read filter status messages, and confirm the FC is actually streaming
`EKF_STATUS_REPORT` on that channel.

**`SYSID_THISMAV = 1` is also a hard requirement.** The filter accepts FC
safety telemetry only from MAVLink system ID `1` and component ID `1`
(`MAV_COMP_ID_AUTOPILOT1`). Both values are compile-time constants in the
firmware; no filter parameter can change them. With any other
`SYSID_THISMAV`, the FC `HEARTBEAT` and `EKF_STATUS_REPORT` frames still cross
the tunnel and are still parsed, but they are discarded before they can refresh
the safety evidence. The result is a permanent GPS block on a perfectly working
CAN tunnel: node `42` is present, tunnel byte counters increase, camera
MAVLink2 works, and GPS never appears. ArduPilot's own default is `1`; this
failure shows up on aircraft where `SYSID_THISMAV` was changed for a
multi-vehicle GCS setup.

Port S1/index `0` is a transparent bidirectional path between the OpenIPC
camera UART and ArduPilot. Port S2/index `1` is separate: it carries MAVLink2
generated by the H743 filter and returns FC telemetry used by its existing
EKF, arm-state, parameter, and status logic. Keeping separate serial
IDs prevents camera bytes from being interleaved with filter-owned MAVLink.
ArduPilot's `_PRO = 2` value is its serial-protocol setting; the standard
Targetted DSDL encodes MAVLink2 as on-wire protocol value `1`.

Some OpenIPC cameras can be held in their bootloader when bytes arrive on RX
during startup. If needed, set ArduPilot `MAV_TELEM_DELAY = 5` so MAVLink output
waits five seconds after FC boot (older ArduPilot versions may call this
`TELEM_DELAY`). Reboot the flight controller after changing CAN or DroneCAN
serial parameters.

### Stream rates on the filter's tunnel channel

ArduPlane compiles every stream group to a `1 Hz` default on EVERY MAVLink
channel, including DroneCAN tunnel channels, so a correct installation normally
needs no `SRn_*` write at all. The filter additionally asks the FC for
`EKF_STATUS_REPORT` at 2 Hz using `SET_MESSAGE_INTERVAL` after binding, and
retries while the field is stale.

- **Never set the filter tunnel channel's `SRn_EXTRA3` to `0`.** `EXTRA3` is the
  stream group that carries `EKF_STATUS_REPORT`. Setting that group to `0` on
  the filter's channel removes the message, and the filter then blocks GPS
  permanently while everything else on the tunnel keeps working.
- **`SRn` is a MAVLink CHANNEL ordinal, not a `SERIALn` number.** There is no
  `SERIAL8`/`SERIAL9` behind the DroneCAN tunnels, and `SR2_` does not mean
  "`SERIAL2`". To find the right group, count every `SERIAL0`..`SERIAL7` whose
  `SERIALn_PROTOCOL` is a MAVLink variant (MAVLink1 or MAVLink2), and include
  the second USB port in that count - it occupies a MAVLink channel even on
  boards where the default parameter table shows `None` for it. Call that count
  P. The camera tunnel is then `SR(P)` and the filter tunnel is `SR(P+1)`: the
  DroneCAN serial ports are appended after the physical MAVLink channels, and
  the filter port is always the last one.
- **Only `SR0_` through `SR6_` exist.** If the filter's channel lands beyond
  `SR6`, it has no parameter group at all and no `SRn_*` write can reach it;
  only `SET_MESSAGE_INTERVAL` from a GCS or script can. The compiled `1 Hz`
  default still applies to that channel, which is why the standard setup works
  with no `SRn` editing whatsoever.
- **If you raise `EXTRA3` for margin, change ONE candidate group at a time,
  reboot the FC, and check whether the block clears.** Never blanket-set several
  `SRn_EXTRA3` values hoping that one of them is the right channel. `SR*`
  parameters raise whole message GROUPS rather than single messages, so a wrong
  guess can saturate a `57600` telemetry radio or flood the camera UART and the
  CAN bus.

### ArduPilot airspeed and optional compass setup

The production/default build exposes the MS4525 as a DroneCAN device from node
`42`; do not select the FC's local I2C MS4525 backend. Only a direct-flash
`*_dronecan_mag` build also exposes the HMC5983. After the H743 node and fitted
sensors are powered:

1. Set the chosen FC airspeed instance to DroneCAN: normally
   `ARSPD_TYPE = 8`. If another airspeed sensor already occupies instance 1,
   use the matching `ARSPD2_TYPE`, `ARSPD3_TYPE`, and so on.
2. Set the matching `ARSPDx_USE` according to the vehicle and intended control
   strategy. For Plane this is normally enabled only after a successful bench
   check and airspeed calibration; follow the current ArduPilot airspeed setup
   procedure for offset, ratio, tube order and pre-arm validation.
3. **`*_dronecan_mag` only:** allow ArduPilot to discover the DroneCAN compass. In Mission Planner open
   `Setup -> Mandatory Hardware -> Compass`, confirm a compass from node `42`
   appears, mark/use it as external as appropriate, and assign its priority.
4. **`*_dronecan_mag` only:** set or auto-detect the HMC5983 orientation, then perform a complete compass
   calibration in the installed vehicle. Never copy offsets from another
   airframe or sensor. Confirm all compass axes respond in the correct direction
   while rotating the aircraft and inspect motor-current interference before
   relying on it for yaw.

ArduPilot automatically identifies the DroneCAN airspeed publisher; there is
no extra virtual-serial mapping for it. A healthy MS4525 sample is published as
`uavcan.equipment.air_data.RawAirData` at up to 20 Hz. On a
`*_dronecan_mag` build only, a healthy HMC5983 sample is published as
`uavcan.equipment.ahrs.MagneticFieldStrength2` with sensor ID `0` at up to
25 Hz. The sensor messages share the existing node ID and CAN transceiver with
GPS and both MAVLink tunnels.

These publications are raw sensor transports, not calibrated airspeed or
heading. The H743 does not learn pitot zero/ratio or compensate tube order, and
it does not apply vehicle compass orientation, hard/soft-iron offsets, or
motor-current compensation. Those calibrations belong to the selected
ArduPilot sensor instances and must be completed again after changing the
sensor, tubing, mounting, orientation, wiring, or nearby power equipment.

Classic CAN carries only seven payload bytes in each multi-frame transport
frame. Keep ArduPilot stream rates modest: camera full duplex plus a chatty
filter port and the 20 Hz airspeed publication can approach the capacity of a
1 Mbps bus; a `*_dronecan_mag` build adds the 25 Hz compass publication. GPS
and NodeStatus have higher priority, while bounded MAVLink queues shed
overload. A red `MAV` row or nonzero `ERR` row indicates
loss/overload; reduce stream rates before flight.
**Carve-out: never reduce the filter tunnel channel's `EXTRA3` below its
compiled `1 Hz` default, and never set it to `0`.** That group carries
`EKF_STATUS_REPORT`, which the filter requires for any GPS output at all, so
"trimming" it turns a bandwidth concern into a total GPS block. Trim the other
stream groups, and the camera channel, instead.
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
  sensor ID `0`, up to 25 Hz — `*_dronecan_mag` builds only
- `uavcan.tunnel.Targetted` for the two MAVLink2 virtual serial ports
- `uavcan.equipment.ice.reciprocating.Status` at 1 Hz, the engine fuel estimate
  (H743 DroneCAN `v0.5.28+`)

The MAVLink2 streams are tunneled; raw GNSS NMEA, UBX, and SBF receiver streams
are not. GPS remains native `Fix2/Auxiliary`, and the physical FC GPS UART stays
disabled.

### Engine fuel estimation (EFI)

The filter estimates fuel burn from the engine RPM the flight controller
already streams to it, and publishes the result as
`uavcan.equipment.ice.reciprocating.Status` (data type `1120`) at 1 Hz. This is
an ESTIMATE computed from a propeller model, not a measurement: there is no
flow sensor and no tank sensor anywhere in the path.

To consume it:

| Purpose | ArduPilot parameter | Value |
|---------|---------------------|-------|
| EFI backend | `EFI_TYPE` | `5` (DroneCAN in full ArduPlane 4.6.3) |
| Fuel gauge backend | `BATT2_MONITOR` | `27` (EFI), only if battery instance 2 is unused |
| Usable gauge capacity for this 5 L tank | `BATT2_CAPACITY` | `4000` (numeric mL despite Mission Planner's `mAh` label) |
| RPM source the filter reads | `RPM1_TYPE` | whatever matches your pickup |
| RPM scaling | `RPM1_SCALING` | **see the warning below** |

The package includes
`presets/arduplane_FC_4.6.3_h743_dronecan_CAN1_5L_EFI.param` for this aircraft.
It requires node-42 H743 DroneCAN firmware **v0.5.31 or later**; do not import
it with public v0.5.25 or any v0.5.30-or-older build. On a fresh setup, first
fully load/reboot/read back the separate non-EFI CAN1 core FC preset so CAN/S2
can deliver stopped-engine evidence, then configure and verify the real RPM
pickup. Next configure node 42, require a positive weighed `FUEL_CAPG` readback
and its accepted-write message, and wait for `Tune saved` if the numerical
value changed. Only then import the FC EFI/BATT2 file.
It keeps the existing electrical BATT1 monitor and requires the operator to
confirm from a live readback that BATT2 is unused,
and makes the gauge reach zero after 4000 mL estimated consumption so the
filter's 1000 mL (20%) estimator-error reserve remains. The EFI backend uses a
synthetic 1.0 V and reports fuel flow through a field Mission Planner labels as
current, so the preset zeros BATT2 voltage, arming-voltage, watt-limit,
capacity-failsafe, and automatic-action rows for initial HIL. Do not enable an
automatic RTL/Land action until the estimator is calibrated and tested on this
aircraft. Until node 42 has a trustworthy total and publishes ICE Status,
BATT2 is unhealthy and may block arming; fix the filter configuration instead
of weakening `ARMING_CHECK`.

Here `EFI_TYPE=5` names ArduPilot's DroneCAN engine-telemetry backend. It does
not mean the mechanically carbureted DLE120 has electronic fuel injection.

For the stated DLE120/Walbro, user-installed wooden CW 27x12, and 5 L tank,
load the paired node-42 starting file
`presets/airdroper_filter_aircraft_dle120_walbro_27x12_wood_cw_5L.param` into
the **filter**, not the FC. It deliberately omits `FUEL_CAPG` because every
capacity write is a state-changing refuel/reset action. After its model rows
are saved, separately write measured density and weighed loaded mass. Exactly
5000 mL at `0.75 g/mL` is only the 3750 g example. Match the FC gauge using
`BATT2_CAPACITY = 0.8 * FUEL_CAPG / FUEL_DENS` (numeric mL); 4000 is valid only
for that exact full-load example. The file uses DLE's published 12 hp rating
(`ENG_PMAXKW=8.95`), while v0.5.30 and v0.5.31 firmware retain the 8.6 kW
compiled fallback. The 8.95 kW value is active only after the profile is loaded
and exact `ENG_PMAXKW` readback confirms it.
DLE publishes 26x10, 26x12, 27x10, and 28x10 for the DLE120, not 27x12, so the
file records the installed geometry but is not propeller approval. Verify
wide-open RPM, temperatures, clearance, balance, fastening, and airframe load
before flight, and confirm it is the two-blade fixed-pitch propeller assumed by
the model. If density changes, wait for its `Tune saved`, then write the
weighed `FUEL_CAPG` separately and always require its accepted-write message.
If the numerical capacity changed, also require the **second** `Tune saved`
before trusting persistence or EFI/BATT2 health. If the value was unchanged,
the firmware schedules no new journal save; the accepted-write message and
exact readback are the expected completion.
Never write `FUEL_CAPG=0`: it is a state-changing reset, not a placeholder.
Firmware through v0.5.30 could publish fresh zero-consumption EFI while a fixed
FC capacity made the gauge look falsely full. Required v0.5.31+ suppresses ICE
Status at zero, but a positive weighed value remains mandatory.
The source specifications are DLE's
[DLE120 product page](https://www.dlengine.com/en/rcengine/dle120) and
[manufacturer manual](https://cdn.dlengine.com/pdf/DLE120%20USER%20MANUAL%20.pdf).

ArduPilot decodes the message into `EFI_STATUS`, which gives a GCS fuel display
and a dataflash record with no side channel. The consumed-volume field is
monotonic and is what the FC's EFI battery-monitor mapping uses; the sensors
this engine does not have - oil pressure, coolant temperature and the rest -
are published as NaN rather than zero, because zero is a measurement and a
false one is alarming.

**RPM scaling is an especially dangerous setting.** The filter
has a single RPM source, so nothing on the aircraft can contradict it. DLE's
DLE120 documentation does not specify the tach lead's electrical interface or
pulses per crank revolution; twin-cylinder count is not proof of either. For a
separate GPIO pulse pickup, ArduPilot computes RPM from pulse frequency times
`RPM1_SCALING`, so scaling is `1 / measured pulses per revolution`.
Configuring the wrong pulse count can divide every RPM reading and reduce the
propeller power term cubically, under-reporting burn.
The filter puts a floor under the estimate from throttle position and
annunciates `Fuel held up by throttle - check RPM_SCALING` when that floor
binds - **if you see that message, check the scaling against a hand tachometer
before flying again.** Verify it at idle and a higher safe bench RPM with a
hand tachometer or oscilloscope. Neither selected FC backend may use
`RPM1_TYPE=3` nor `RPM2_TYPE=3` (EFI): node 42's EFI RPM is derived from FC RPM
and would create a circular source. Inspect both RPM instances live. The pickup
type, FC pin, voltage/interface, and measured pulse count remain
aircraft-specific and are deliberately absent from the preset.
ArduPilot's Plane 4.6.3
[RPM parameter definition](https://github.com/ArduPilot/ardupilot/blob/Plane-4.6.3/libraries/AP_RPM/AP_RPM_Params.cpp#L16-L29)
and [GPIO implementation](https://github.com/ArduPilot/ardupilot/blob/Plane-4.6.3/libraries/AP_RPM/RPM_Pin.cpp#L65-L78)
define this scaling contract.

**On an airframe with no fuel-level sensor this estimate is the ONLY fuel
indication the pilot has**, so it is deliberately biased to over-report and is
advisory until calibrated. Set the eight `PROP_*`/`FUEL_*`/`ENG_PMAXKW`
parameters on the FILTER (node `42`, not the FC), load an engine preset if one
matches your combination, and follow "Calibrating the fuel estimate" in
[06_tuning.md](06_tuning.md). Writing `FUEL_CAPG` zeroes the running total, so
write it after every refuel.

Fuel accounting is deliberately independent of the GNSS output gate. It keeps
running through complete FC-link loss and an unknown/unsupported FC-version
block. Every boot starts with the conservative engine-may-be-running latch set;
link silence cannot clear it, and missing RPM is charged at rated power until
fresh disarmed state, zero RPM, and closed throttle all confirm a stop. Writing
`FUEL_CAPG` is accepted only after those same three inputs are fresh; the write
itself does not clear that latch.

If any boot has no trustworthy V2 backup record (including a normal power-on, a
warm reset, or any legacy V1 record), the total is marked LOST and the filter
sends **no DroneCAN ICE Status**. A missing, corrupt, or otherwise invalid H743
tune journal also invalidates a surviving fuel total because the capacity,
density, and model settings under which it accumulated have unknown provenance.
POR/PDR cannot prove a refuel or mechanical engine stop. ArduPilot's EFI backend
therefore ages stale/unhealthy instead of accepting a false zero/full tank. The
filter repeats `Fuel total LOST - write FUEL_CAPG to restart it` every 60 s.
Land or remain on the ground, verify the complete fuel configuration, wait for
fresh stopped-engine quorum (disarmed + valid zero RPM + closed throttle), and
rewrite `FUEL_CAPG` for the fuel aboard even if its numerical value is unchanged.
Disarmed alone is rejected. If the numerical capacity changed, the accepted
write zeroes the runtime counter but leaves TOTAL LOST and EFI silent until the
asynchronous tune-journal save reports `Tune saved`; `Tune save failed` leaves
the lockout in place. A valid V2 restore receives a bounded conservative
25-second rated-power reset-gap charge, not an exact measurement of
reset/startup burn. An accepted write establishing a new total cancels any
pending charge belonging to the old restored total.

`FUEL_DENS` requires the same fresh stopped-engine quorum. An actual density
change marks the total LOST before runtime assignment, cancels any older CAPG
commit intent, and blocks capacity writes with
`FUEL_CAPG blocked: wait for FUEL_DENS save` until verified journal save. Failure stays blocked/LOST;
`Tune saved` clears the density latch but not the lost total. Only then can a
subsequent stopped-quorum `FUEL_CAPG` write establish a fresh zero.

Factory reset marks the fuel total LOST in backup SRAM before flash work starts.
A failed attempt may conservatively leave it LOST too. After any attempt,
recheck every fuel-model parameter and perform the stopped-engine `FUEL_CAPG`
recovery; after a changed capacity, wait for `Tune saved`.

**Never perform Phase-C maintenance with the engine running.** A connected
maintenance session can exceed that fixed 25-second bound.

The estimate needs no extra stream configuration: RPM, throttle and air density
all arrive on the filter tunnel channel that the GPS path already requires.

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

> ### The filter's parameters are NOT in Mission Planner's Full Parameter List
>
> This is the single most common way to waste an afternoon, so it is stated
> before the procedures rather than after them.
>
> The filter is a **separate MAVLink node: system ID 42, component ID 191** - the
> same identity printed on every filter status line in the Messages tab. Mission
> Planner's Full Parameter List and Full Parameter Tree edit the **connected
> vehicle, system ID 1**, which is the flight controller.
>
> Typing a filter parameter name there and pressing **Write Params** sends the
> write to the flight controller. The filter never receives it. There is **no
> error and no rejection**, because nothing arrived to be refused - the value
> simply never changes, through any number of retries and reboots.
>
> Use one of the three options below. All of them address node 42 directly.

> ### `ARM=1` in the filter's status line does not mean the FC is armed
>
> Mutations are fail-closed on the FC being disarmed, so it is natural to read
> `ARM=1` as the blocker. It is not. That field is `guard_armed` - the spoof
> guard having completed warm-up - and it is a **healthy** indication that says
> nothing about the flight controller.
>
> When a write really is refused for arming, the filter says so explicitly:
> `Write blocked: FC armed/unknown`. If you see silence instead, the write did
> not reach the filter; re-read the box above.

Reads are available at any time, but every mutation is fail-closed unless the
filter has received a fresh, positive **FC disarmed** report. This includes
parameter writes, `UBX_RESET`, **Commit Params**, and factory reset. The FC must
therefore remain powered, connected over DroneCAN, and disarmed even when the
parameter UI itself is connected directly over USB-C. DroneCAN mutations must
also originate from the configured or currently bound FC node.

### Option A: DroneCAN through the flight controller

Use this while the board is on the aircraft CAN bus:

1. Open Mission Planner.
2. Go to **SETUP -> Optional Hardware -> DroneCAN/UAVCAN**.
3. Select the active CAN driver, usually `MAVLinkCAN1`, and press **Connect**.
4. Wait for node `42` named `org.airdroper.gnss_filter.h743_dronecan`.
5. Press **Menu** on node `42`, then open **Parameters**.
6. Confirm the FC is disarmed, edit the tune row, press **Write Params**, then
   press **Commit Params**.
7. Allow up to 65 seconds if another storage operation was attempted during the
   preceding minute, then reboot and re-open node `42` Params to confirm the
   value persisted.

### Option C: Scripted, from a PC on the FC's USB port

Use this when you want the values recorded, diffable, or applied repeatably -
and when you would rather not depend on the GCS addressing node 42 correctly.
`tools/mission_planner/filter_params.py` talks to system ID 42 directly through
the flight controller's MAVLink link.

Disconnect Mission Planner first; it holds the COM port exclusively.

```bash
# what does the filter actually expose?
python tools/mission_planner/filter_params.py --port COM25 --list

# read and write single values; every write is read back and confirmed
python tools/mission_planner/filter_params.py --port COM25 --get LOG_MS
python tools/mission_planner/filter_params.py --port COM25 --set LOG_MS=2000

# capture the whole tune before changing anything, and put it back later
python tools/mission_planner/filter_params.py --port COM25 --backup before.params
python tools/mission_planner/filter_params.py --port COM25 --restore before.params

# make Mission Planner's DroneCAN parameter screen usable (see Option A)
python tools/mission_planner/filter_params.py --port COM25 --enable-dronecan-ui
```

The script refuses to report success on anything it cannot read back, and it
surfaces the filter's own refusal messages rather than failing silently. Values
commit to flash a couple of seconds after the ack - the filter logs
`Tune saved` - and survive a power cycle.

`--enable-dronecan-ui` checks `CAN_SLCAN_CPORT`, and sets `CAN_SLCAN_TIMOUT` to
30 s if it is 0. Zero means SLCAN never reverts to MAVLink, so if it is ever
engaged and anything goes wrong the link stays dead until a power cycle. It
deliberately leaves `CAN_SLCAN_SERNUM` at `-1`: Mission Planner sets that itself
when you enter SLCAN mode, and pinning it hands a serial port away permanently.
Prefer `MAVLink - CAN1` in the DroneCAN screen over SLCAN for exactly that
reason - it cannot take the serial link away from you.

### Option B: Direct USB-C to the H743

Use this on the bench when you want the familiar Mission Planner MAVLink
parameter screen without using any flight-controller serial port. The FC must
still be present on DroneCAN to provide fresh disarmed state:

1. Power the H743 normally, not in `BOOT0` ROM DFU mode.
2. Connect the H743 USB-C port to the computer.
3. In Mission Planner, select the new H743 COM port and `115200` baud.
4. Click **Connect**. Mission Planner should see system ID `42`.
5. Open **CONFIG -> Full Parameter Tree** or **Full Parameter List**.
6. Confirm the FC is disarmed, edit the spoofing/tuning values, and click
   **Write Params**.
7. Allow up to 65 seconds when the one-minute storage cooldown is active, then
   reboot/reconnect and verify persistence.

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

The production H743 DroneCAN fixed-wing profile uses:

- `RJ_LOIT_V=0` (disables the special low-speed 2500 m rejoin-gate floor)
- `SP_JMP_MPS=200`
- `SP_ABS_M=400`
- `EKF_TRIPMS=500`

At 120 km/h the aircraft travels about 33.3 m/s, or about 167 m during the
full default 5 s NAV-validity window. The 400 m absolute limit leaves recovery
margin across that gap, while the 200 m/s implied-speed limit is six times
cruise speed. Mathematical guard tests cover a 65 m/s (234 km/h) design
envelope, which travels 325 m in 5 s and preserves 75 m of absolute-limit
margin; this is not flight or hardware validation. These
are fixed-wing production values, not universal airframe
recommendations: validate them against maximum speed and flight logs.

On the first fixed-wing-profile update, H743 migrates a stored value only when
it still exactly matches the legacy migration sentinel (`0.8/500/1000/0`). A custom
operator value survives unchanged. Read the four rows back after updating; to
replace custom values intentionally, load `airdroper_filter_field_safe.param`
or perform a factory-parameter reset while the FC is freshly and positively
disarmed.

`UBX_RESET` is a one-shot command, not a saved setting:

- set `UBX_RESET=1` for a u-blox hot start
- set `UBX_RESET=2` for a u-blox cold start
- set `UBX_RESET=3` to clear u-blox config and reinitialize

H743 DroneCAN keeps the raw FC GPS UART settings locked off:

- `FCGPS_UART = 0`
- `FCGPS_FWD = 0`

In H743 v0.5.5+, `RJ_REQEKF` and `EKF_OKRJMS` are also locked to `0`; writes
are ignored, including non-zero values retained by older journals. Their former EKF rejoin
gate was unsatisfiable/circular and has been replaced on H743 by independent
multi-evidence recovery (barometric rate, pitot, attitude/course, SNR, UTC, and
the dead-reckoned anchor). `PT_ONLY=1` disables synthetic output/blending/nudge
only; it does not bypass geometry, quality, stability, confidence, or evidence
checks.

The firmware auto-saves accepted values after a short debounce. A single
60-second wear limiter covers auto-save, explicit commit, and factory reset;
values remain active and dirty until a deferred save can run. The A/B journal
commits the new record before an old sector is eligible for erase, so an
interrupted write retains the last complete settings record.

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
| **Sensors** | MS4525 freshness, differential pressure, and sensor temperature; `*_dronecan_mag` builds also show HMC5983 freshness and magnetic-field magnitude |
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
flight-log review. In particular, on a `*_dronecan_mag` build magnetic-field
magnitude is not a calibrated heading, and a `FILTER ONLINE` display does not prove correct compass
orientation, pitot plumbing, CAN termination, or MAVLink routing.

By default `FILTER_DRONECAN_FC_NODE_ID=0`. The tunnel requires two valid
Targetted transfers addressed to node `42` from the same source before it binds
that FC. The binding expires after three seconds without a valid tunnel
transfer; all old serial queues are discarded before another node can bind.
Generic status broadcasts cannot claim the FC identity. On a busy multi-node
bus, set
`FILTER_DRONECAN_FC_NODE_ID` at build time to lock the tunnel and display to one
FC node from boot.

At lease expiry, or when a same-node `NodeStatus` uptime rollback reveals a
quick FC reboot, the H743 discards both directions of both MAVLink tunnels,
resets the MAVLink parser, and clears all FC-derived heartbeat, arm, EKF,
attitude, speed, barometer/bias, firmware-version, and warning state. A new
binding starts fail-closed. The filter immediately requests the complete FC
telemetry set after binding or detected reboot, retries every five seconds
while required fields are stale, and refreshes it every 30 seconds when fresh.

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

The inverse is equally important: `FC_LINK` and the other fault reasons DO
report DroneCAN warning health. So `PreArm: DroneCAN: Node 42 unhealthy!` is the
EXPECTED companion message of `GNSS BLOCKED #1: FC LINK STALE`, not a second,
separate CAN fault to chase. Do not start re-checking CAN wiring, termination,
or bitrate because that pre-arm line appeared alongside a `FCLINK` block.

Both MAVLink2 virtual ports remain active in DR0 and DR1. DR1 blocks only the
native GPS `Fix2/Auxiliary` output; it does not cut the OpenIPC camera tunnel or
the filter-owned MAVLink2 stream. S2/index `1` preserves FC telemetry input,
EKF-status evidence, filter `STATUSTEXT`/`NAMED_VALUE`
logging, parameter traffic, and the other existing MAVLink behavior. The
physical `FCGPS_FWD` raw UART bypass remains unavailable.

There is one deliberate `v0.5.29+` exception: private Mission Planner
spoof-position records named `SP_*` are **USB-only** and never enter S2. While
DR1 is latched, the USB device is configured, and the core's CDC transmit-ready
latch is set, the H743 emits a 2 Hz transaction:

| Record | Meaning |
|--------|---------|
| `SP_BEGIN` | Transaction sequence and unambiguous assembler reset |
| `SP_G_LAT`, `SP_G_LON` | Receiver-reported/untrusted latitude and longitude, signed degrees x 1e7 |
| `SP_R_LAT`, `SP_R_LON` | Wind-blind DR reference latitude and longitude, signed degrees x 1e7 |
| `SP_FLAGS` | Raw bounds/freshness, reference validity/motion, and DR1 bits |
| `SP_SEQ` | Transaction sequence and final commit record |

All seven are standard MAVLink `NAMED_VALUE_INT` messages from system 42,
component 191 and share one `time_boot_ms`. `SP_BEGIN` is first and `SP_SEQ` is
last with the same sequence; consumers must discard an incomplete, mismatched,
or expired transaction. The navigation north fence is not
applied to this private diagnostic because a south-jump attack must remain
visible, but finite WGS84 bounds and freshness are explicit in `SP_FLAGS`. Raw
freshness has a fixed 1.5-second ceiling and is not extended by the
operator-tunable navigation age.
The encoder runs only in DR1 and its sole production output sink is direct USB
CDC. It does not call the generic MAVLink sender, CAN tunnel, DroneCAN
publisher, or FC UART.

Mission Planner must keep the FC as the primary link and add the H743 USB COM
port as a secondary connection at 115200. This direct cable is a bench/tethered
GCS path, not an in-flight radio path. See the live spoofing-map procedure in
the operation guide. Beginning with firmware `v0.5.30`, the CDC path accepts
Mission Planner's default secondary-link behavior, which opens without
asserting DTR; no
global **Reset APM on connect** workaround is required. The core latch may
remain ready after the host closes the COM port until USB is unplugged or a
transmit timeout occurs; unplug USB when private telemetry must stop
immediately. USB/COMM2 and FC/S2/COMM0 use independent MAVLink sequence
counters, so adding or losing the USB link cannot punch holes in the FC stream.
This does not create any FC, S2, or CAN output path.

The GNSS-altitude versus FC-barometer cross-check is **not currently active**,
and no `ALTITUDE` stream is required from the flight controller. ArduPilot has
no `MSG_ALTITUDE` stream entry, so the MAVLink `ALTITUDE` message can never be
provided at all, and the cross-check has therefore never run in this product's
life. It remains wired but disabled behind a build flag. Treat barometric
altitude cross-checking as a future feature, not as a working guard, and do not
try to configure a stream for it. The FC messages that actually matter for GPS
output are `HEARTBEAT` and `EKF_STATUS_REPORT`.

H743 DroneCAN `v0.5.30+` also explicitly requests `AUTOPILOT_VERSION`. Until a
supported ArduPilot version (4.6.1 or newer) is known, `Fix2/Auxiliary` are
suppressed immediately; an older reported version is suppressed the same way.
The 15-second startup/rebind grace delays only warnings and hard fault
processing, never GNSS publication. After that delay, an unknown version emits
`FC VERSION UNKNOWN` and `AUTOPILOT_VERSION REQUIRED`; an old version emits
`FIRMWARE TOO OLD` and `UPDATE TO ARDUPILOT 4.6.1+`.

The filter-owned S2/index `1` safety stream is fail-closed. After startup and
boot-guard grace, node 42 requires fresh decoded FC `HEARTBEAT` and
`EKF_STATUS_REPORT` messages; empty tunnel keepalives alone are not sufficient.

Suppression and the DR1 latch are two separate decisions, and the difference
matters when you are diagnosing a marginal link:

- **Suppression is immediate.** The moment either message ages out
  (`HEARTBEAT` > 3 s, `EKF_STATUS_REPORT` > 4 s) `Fix2/Auxiliary` stop. That is
  the fail-closed guarantee and it has no debounce.
- **The latch waits 10 s** of continuous staleness before entering `DR1/FCLINK`.
  A brief tunnel stall therefore costs a few seconds of GPS, not the full
  recovery cycle described above. The link must then be continuously fresh for
  5 s before the staleness timer resets, so a link that flaps every few seconds
  still latches rather than withholding GPS silently and indefinitely.
No DR1 auto-recovery or normal rejoin can restore GPS publication until both
messages are fresh again and the configured lock/rejoin gates pass.

The 16-bit `NodeStatus.vendor_specific_status_code` has a fixed, non-overlapping
layout:

| Bits | Meaning |
|------|---------|
| 15 | DR1 latch active |
| 14 | GNSS output blocked for any reason |
| 13:7 | Spoof confidence, integer 0-100 |
| 6 | Enabled I2C sensor missing or stale after startup grace |
| 5:0 | `Dr1Reason` code |

Consumers should mask these fields; bit 6 is the sensor flag, not bit 7.

The MS4525 `RawAirData` publication is also independent of DR0/DR1; the same is
true of HMC5983 `MagneticFieldStrength2` when a `*_dronecan_mag` build is used.
A spoofing decision suppresses only GNSS `Fix2/Auxiliary`; it does not intentionally remove airspeed, an enabled optional compass,
NodeStatus, camera MAVLink, or filter MAVLink. A failed or disconnected I2C
sensor stops producing its own valid sensor publication. After the five-second
sensor startup grace, node 42 also reports DroneCAN warning health and sets
vendor-status bit 6 until both enabled sensors are producing fresh samples,
making it a separate pre-arm/maintenance fault.

GNSS-only guards remain active: no-fix, low satellites, position jumps,
altitude rate/jump, SNR, hemisphere, geofence, heading reversal, GPS time
sanity, velocity-position consistency, and receiver clock jump when available.

### Leaving DR1: recovery requires evidence, never time

`DR1_MAX_DURATION_MS` is `0`. DR1 does **not** expire. The only ways out are the
evidence quorum, ground release, or a power cycle.

The quorum needs at least three evidence rows agreeing, **zero** contradicting,
held continuously, **and at least one independent witness**. A row counts as a
witness only when its operands were physically excited:

| Witness | Needs |
|---------|-------|
| Ground speed vs pitot | real airspeed, IAS >= 12 m/s and ground speed >= 6 m/s |
| Vertical rate | a real climb or descent >= 3 m/s |
| Course vs yaw | a real turn >= 12 deg/s, scored on that pass only |

All three require **motion**. That is deliberate: a stationary airframe has no
physical reference that can contradict a spoofer, so agreement while parked
proves nothing.

**In flight this needs no manoeuvre.** With a working pitot, level cruise holds
the ground-speed witness continuously. Budget `DR_LOCK` 120 s + 60 s hold =
**~180 s** after a fix-loss trip, doubled to ~240 s for a spoof-integrity trip,
plus 30 s per earlier contradicted attempt.

**On the ground no witness is reachable at all**, so a unit that trips during
pre-flight would be stuck until a power cycle. Ground release covers that case.
It replaces the witness with position agreement over a dwell, and it is
confined to a parked, disarmed airframe:

| Condition | Value |
|-----------|-------|
| FC disarmed, positively and recently reported | fail-closed; unknown or stale is not disarmed |
| FC ground speed / climb | < 4 m/s / < 1 m/s (the speed bound sits above the FC's measured dead-reckoning drift, mean 1.95 / max 2.84 m/s on a stationary unit) |
| Filter's own pitot, if fitted and live | < 12 m/s (above the sensor's ~10.6 m/s apparent zero offset) |
| Fix agreement | 30 m horizontal, 30 m vertical |
| Receiver's own spoof indicator | below warning for loss trips; strictly clear for integrity trips |
| Named parked evidence | every available row is non-FAIL; GNSS-time is PASS; receiver speed is finite, nonnegative, fresh within 1500 ms, and at most 4 m/s; speed and location share an epoch generation with at most 1500 ms skew |
| Optional GSV/SNR | may be unavailable; absence does not block release, but an explicit FAIL remains a veto |
| Held continuously for | 90 s loss / 240 s integrity, +60 s per earlier release |

The parked path does **not** use the airborne generic pass count. That distinction
lets a passive GGA/RMC receiver recover honestly while stationary without
inventing three PASS rows or requiring optional GSV. The airborne witness
quorum and its pass floor are unchanged.

What the fix must agree **with** depends on why DR1 tripped. For a signal-loss
trip (`NO FIX`, `LOW SATS`, `FC LINK`) the reference is the position held
*before* the trip. For a detected spoof (`SNR`, `JUMP`, `ALT`, `CONF`,
`HEADING`, ...) that pre-trip anchor cannot be trusted - a slow-walk attacker
was already moving it - so the returning signal must instead stay
**self-consistent**, horizontally and vertically, against a reference captured
when the dwell starts, through the longer 240 s dwell and with the altitude
check mandatory. Integrity releases additionally draw on a separate allowance
of **one per power cycle**. `SOUTH` is never released automatically at any
dwell: a south-hemisphere fix on this airframe is physically impossible and
always costs a deliberate human action.

`DR_LOCK` is not bypassed, so the floor is 120 + 90 + a 10 s blend, about
**3.5 minutes** from a loss trip to `DR0`, and about **6 minutes** for an
integrity trip.

After a ground release the radius keeps binding while the aircraft stays parked
and disarmed. If the fix wanders out of it, node 42 re-enters DR1 with reason
`PARKED_MOVE` (15). This is expected if you physically move a disarmed airframe
more than 30 m - walking pace is below the "parked" threshold, so the filter
cannot tell that apart from a fix being walked away. It is not a fault: the unit
re-releases from its new position after the next dwell, and `PARKED_MOVE` does
not consume the one-per-power-cycle integrity allowance, so repositioning after
an integrity release cannot strand the unit. Ground release is limited to four
times per power cycle in total. Operator status names this reason `PARKED MOVE`;
the shorter board-screen label is `PARKED`.

**Reading the recovery banner.** The 1 Hz debug line names exactly what is
blocking recovery:

```
RJ ev3/3F0W0/1p hold=0/60s gnd=45/90s -
```

| Field | Meaning |
|-------|---------|
| `ev3/3` | airborne evidence rows passing/required; not the parked-release contract |
| `F0` | airborne rows contradicting; ground release separately vetoes every available FAIL |
| `W0/1` | airborne independent witnesses present/required |
| `p` / `a` | airborne speed row using the weak pre-spoof envelope / the pitot |
| `hold=0/60s` | airborne evidence hold banked vs required |
| `gnd=45/90s` | ground-release dwell banked vs required; `0/N` means conditions are not currently met |
| final tag | `-` means no named block; `EVM` means required parked evidence is missing, `EVF` means a contradiction, and `EVPg` is a bounded short missing-evidence lapse |

On a stationary bench, the airborne `W0/1` is normal and does not prevent the
separate named parked path. Watch `gnd=` and the final tag for the recovery that
will actually happen; do not wait for the displayed airborne pass count to
change.

## 10) Bring-up checklist

1. Flash `weact_mini_h743vitx_dronecan_usb` or `weact_mini_h743vitx_dronecan`.
   Only a deliberately magnetometer-equipped direct-flash board should use the
   corresponding `*_dronecan_mag` environment.
2. Wire GNSS to `PA2/PA3`.
3. Cross the 3.3 V OpenIPC UART: camera TX -> `PA10`, `PA9` -> camera RX, plus
   common ground and an appropriately rated separate camera supply.
4. On a separate keyed connector, wire the MS4525 to shared `PB10` SCL,
   `PB11` SDA, 3.3 V and ground, and confirm its complete ordering code. For a
   `*_dronecan_mag` build only, wire the HMC5983 in parallel and confirm its
   identity before power-up.
5. Wire `PB9/PB8` through the CAN transceiver to the FC CAN port.
6. Configure ArduPilot CAN driver, DroneCAN protocol, 1 Mbps bitrate, and
   `GPS1_TYPE=9`.
7. Enable DroneCAN serial, mapping S1 to node `42`/index `0`/115/MAVLink2 and
   S2 to node `42`/index `1`/115/MAVLink2.
8. Set the FC airspeed instance to DroneCAN (`ARSPD_TYPE=8` for instance 1)
   and reboot the flight controller. For a `*_dronecan_mag` build only,
   confirm the node-42 compass also appears.
9. Confirm the H743 screen lights and shows `GNSS FILTER`.
10. Confirm the DroneCAN node appears as node ID `42` in DroneCAN/SLCAN tooling.
11. Confirm ArduPilot reports a DroneCAN GPS and airspeed instance, camera MAVLink2 reaches
    the FC, and filter system ID `42` is visible through MAVLink routing.
    For a `*_dronecan_mag` build only, also confirm the node-42 compass.
    Then confirm the **return** direction as well: the filter must show no
    `FCLINK` block (hero card not `BLOCK`/`FCLINK`, and no
    `GNSS BLOCKED #1: FC LINK STALE`). Everything else in this step only proves
    the filter -> FC direction, which succeeds even when the FC never streams
    `EKF_STATUS_REPORT`; the absence of `FCLINK` is the only check that proves
    the FC -> filter direction is actually carrying `EKF_STATUS_REPORT`.
    Beware one trap here: a normal filter `STATUSTEXT` arriving in the GCS proves
    nothing about the tunnel while the filter's USB-C is plugged into the PC,
    because normal diagnostics are written to both the DroneCAN tunnel and USB
    CDC. (`SP_*` position diagnostics are the deliberate USB-only exception.)
    Unplug the filter's USB before using normal GCS messages as tunnel evidence.
12. With the pitot still and both ports at equal pressure, calibrate zero;
    gently apply differential pressure and verify positive, stable airspeed.
13. **`*_dronecan_mag` only:** calibrate the compass after final installation, check axis/orientation and
    motor-current interference, and verify it remains healthy for several
    minutes with the camera/LTE transmitter active.
14. Trigger a bench DR1 condition and confirm `Fix2/Auxiliary` stop while
    `NodeStatus` stays online.
15. Confirm airspeed and both MAVLink2 paths remain online during DR1; on a
    `*_dronecan_mag` build also confirm the compass. Then clear the condition
    and confirm GPS publishing resumes after rejoin.

## 11) Troubleshooting

### FC LINK STALE: one cause, four messages

A missing FC `EKF_STATUS_REPORT` on the index-`1` tunnel produces all four of
these AT ONCE:

- `GNSS BLOCKED #1: FC LINK STALE`
- `PreArm: DroneCAN: Node 42 unhealthy!`
- `PreArm: Selected GPS Node 42 not set as instance 1`
- `EKF3 waiting for GPS config data`

These are ONE fault, not four. The filter is fail-closed on FC telemetry
freshness, so without `EKF_STATUS_REPORT` it suppresses `Fix2` and `Auxiliary`;
the filter then reports DroneCAN warning health (hence `Node 42 unhealthy!`),
ArduPilot never binds a GPS instance to the node (hence
`not set as instance 1`), and the EKF never gets GPS configuration (hence
`EKF3 waiting for GPS config data`). All four clear themselves once `Fix2` flows
again. Do not chase them separately.

Do not "fix" the symptoms:

- Clearing `GPS1_CAN_OVRIDE` hides the `not set as instance 1` line without
  restoring GPS.
- Adding `GPS1_DELAY_MS` does not help either: there is no timing problem to
  compensate here, and no delay value can make an absent message arrive.

Neither touches the cause, which is that the FC is not delivering
`EKF_STATUS_REPORT` to the filter. Work the checklist in this order: `EXTRA3`
stream rate on the filter's MAVLink channel, `SYSID_THISMAV = 1`, MAVLink
channel budget (`SR0_`..`SR6_` only), then CAN wiring last.

Firmware `v0.4.8+` names which half of the evidence is missing. The DR1 trigger
message carries the ages as `DR: FC telemetry stale (hb=... ekf=...)`, and a
periodic line reports `FC rx=... hb=... ekf=... nack=N`:

- `hb=never` means no FC MAVLink is reaching the filter at all. That is a
  tunnel, protocol, or sysid problem: check `CAN_D1_UC_S2_*`, `_PRO = 2`, and
  `SYSID_THISMAV = 1`.
- `hb=0s ekf=never` means the tunnel works and the FC is talking, but the FC is
  not streaming `EKF_STATUS_REPORT`. That is a stream-rate/channel problem, not
  a wiring problem.

Airborne recovery is not instant, and it is not only a matter of waiting. Three
things have to happen in order:

1. the 120 s DR lock expires (`DR_LOCK_MS`);
2. the evidence quorum then has to be held **continuously for 60 s**
   (`REJOIN_EV_HOLD_MS`) - any contradiction restarts that window;
3. at least one **independent witness** has to be present for the whole of it.

So the airborne floor is about three minutes plus blend, not two. A witness
needs a climb/descent of at least 3 m/s, a genuine turn, or a live pitot at or
above 12 m/s. Straight-and-level cruise **does** satisfy the witness when that
pitot is live and above threshold; without a pitot it does not. See the witness
table in `04_setup_and_flash.md`.

On a stationary bench the separate H743 parked path can now recover after its
own dwell. It requires the named GNSS-time plus fresh same-epoch receiver-speed
contract in the table above, not the airborne witness/pass count, and does not
require optional GSV. A power cycle skips the dwell but is no longer a recovery
prerequisite.

**If you fly with no airspeed sensor**, the pitot row is
permanently unavailable and the only witnesses left are the barometric vertical
rate and the GNSS-course-versus-FC-yaw comparison. Recovery is still reachable,
but it needs a deliberate sustained climb or a steady turn - an autopilot loiter
is ideal. Intermittent hand-flown manoeuvring is not enough, because each dip
below the excitation floor restarts the 60 s window.

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
- On `v0.5.30+`, check for `FC VERSION UNKNOWN` / `AUTOPILOT_VERSION REQUIRED`
  or `FIRMWARE TOO OLD` / `UPDATE TO ARDUPILOT 4.6.1+`. The filter explicitly
  requests `AUTOPILOT_VERSION` and suppresses GPS immediately until a supported
  reply arrives; the 15-second grace delays only the warnings.
- Confirm `GPS_AUTO_CONFIG=1` on firmware older than H743 DroneCAN `v0.1.2`.
- If there are multiple DroneCAN GPS nodes, set `GPS1_CAN_OVRIDE=42` or the
  matching GPS instance override.
- Confirm the GNSS receiver has a fresh valid fix; the Overview page should
  show `GPS FIX` rather than `GPS STALE` or `GPS NO FIX`.
- Confirm the persistent footer shows `PUB+` and `DR0`, not `PUB-` / `DR1`.
- `PUB?` means the publication gate is open but no recent Fix2 was accepted
  into the local DroneCAN transmit queue; check GPS freshness and CAN readiness
  before flight. `PUB+` still is not proof that the FC received the transfer.
- Confirm the hero card is not `BLOCK` with `FCLINK`, `GNSSCFG`, `GPS`, `SOUTH`,
  `FENCE`, `NOFIX`, `SATS`, `JUMP`, or another DR1 cause label. `FCLINK` is not a
  GNSS-side fault at all - see **FC LINK STALE: one cause, four messages** at the
  top of this section.

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
  **This holds for every DR1 reason EXCEPT `FCLINK`.** A `FCLINK` block is
  caused by the FC -> filter direction of the index-`1` tunnel, and the tunnel
  itself is usually perfectly healthy while one required message is simply not
  being streamed. For `FCLINK`, check the `EXTRA3` stream rate on the filter's
  MAVLink channel, `SYSID_THISMAV = 1`, and the MAVLink channel budget
  (`SR0_`..`SR6_` only) FIRST, and check CAN wiring, termination and bitrate
  LAST.

### Airspeed or optional compass is missing/unhealthy

- Confirm the expected sensor firmware option is enabled, then confirm
  `PB10 -> SCL`, `PB11 <-> SDA`, 3.3 V power and common ground. The
  production/default build enables MS4525 only; HMC5983 requires a
  direct-flash `*_dronecan_mag` build.
- Measure idle SCL/SDA. Both must pull up to approximately 3.3 V, never 5 V.
  Disconnect power immediately if either line exceeds the H743 I/O voltage.
- Check for one sensible effective set of pull-ups, shorts, swapped SCL/SDA,
  excessive cable length, electrical noise and duplicate I2C addresses.
- MS4525: confirm the full code `4525DO-DS3AI001DP` and address `0x28`.
  Equalize both ports for zero calibration, then apply a small known pressure
  and confirm the indicated sign and magnitude. Do not compensate for the wrong
  sensor range using only `ARSPD_RATIO`.
- **`*_dronecan_mag` only:** confirm HMC5983 address `0x1E` and identity `H43`. If a cheap module is not
  accepted or calibrates inconsistently, assume it may be a clone rather than
  weakening the identity check.
- Confirm `ARSPDx_TYPE=8` selects DroneCAN on the FC. Do not use type `1`, which
  is the FC's own local-I2C MS4525 driver.
- **`*_dronecan_mag` only:** inspect Mission Planner's detected compass list and device
  IDs, remove stale missing devices if necessary, set the correct priority and
  orientation, then recalibrate in the final installed position.
- A DR1 GPS block does not disable airspeed or an enabled optional compass. If
  either stops in DR1, diagnose I2C integrity, CAN load/errors and sensor
  health separately.

### Screen does not show FC arm or safety state

- Confirm the FC is on the same CAN bus and DroneCAN is running.
- If the bus has many nodes, rebuild with `FILTER_DRONECAN_FC_NODE_ID=<fc id>`.
- Some FC status rows depend on ArduPilot broadcasts. GPS publishing does not
  require those rows to be present.

### Writing filter params in Mission Planner does nothing, with no error

The write went to the flight controller, not to the filter. The filter is system
ID 42 / component 191; Mission Planner's Full Parameter List edits the connected
vehicle, system ID 1. Nothing reaches the filter, so nothing refuses it - hence
the silence rather than a failure.

Confirm the filter is reachable and its parameter service is alive:

```bash
python tools/mission_planner/filter_params.py --port COM25 --list
```

A healthy node returns its full parameter set. If that works but Mission Planner
still will not write, use Option A (DroneCAN node Params) or Option C (script)
instead of the Full Parameter List.

Do not be misled by `ARM=1` in the filter's status line - that is `guard_armed`,
not the FC's arming state. A genuinely arming-blocked write announces itself as
`Write blocked: FC armed/unknown`.

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
- For direct parameter editing, make the H743 COM port the active connection.
  For the `v0.5.29+` spoofing overlay, keep the FC active and add H743 USB as a
  secondary link in **Connection Options** instead.
- If that secondary port opens with DTR deasserted but no telemetry arrives,
  update to `v0.5.30+`; this is the first version that supports Mission
  Planner's default DTR-low secondary-link sequence.

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
