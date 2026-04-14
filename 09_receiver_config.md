# GNSS Receiver Configuration

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

Set `GNSS_TYPE` in Mission Planner to match your receiver, then reboot the STM32.

| `GNSS_TYPE` | Receiver family | ArduPilot `GPS1_TYPE` |
|---|---|---|
| `0` | u-blox M8 / M9 / M10 / F9 / F10, plus u-blox-compatible gateway modules | `1` (AUTO) or `2` (u-blox) |
| `1` | Unicore UM980 / UM981 / UM982 | `24` (UnicoreNMEA) |

---

## UM980 / UM981 / UM982

**Manual pre-configuration required.** Use UPrecise to apply the command profile
below before first flight. The STM32 performs passive autobaud detection at boot
(finds whatever baud the UM980 is saved at) and forwards the raw NMEA/binary
stream to the FC GPS port unchanged. It does **not** send configuration commands
to the UM980.

### Step 1 — Configure the UM980 via UPrecise

Connect the UM980 to UPrecise and send the following commands one at a time.
Use the **Standard UAV** profile for most airframes, or the **High-Dynamic UAV**
variant for aggressive platforms.

#### Standard UAV profile

```text
FRESET
UNLOG COM1

MODE ROVER UAV
CONFIG ANTIJAM FORCE
CONFIG MMP ENABLE
CONFIG PVTALG MULTI
CONFIG SMOOTH PSRVEL ENABLE
MASK 5
CONFIG NMEA0183 V410
CONFIG COM1 460800

GNGGA COM1 0.2
GNRMC COM1 0.2
AGRICA COM1 0.2

SAVECONFIG
```

#### High-Dynamic UAV profile

Same as above but replace the MODE line:

```text
MODE ROVER UAV HIGHDYN
```

### Step 2 — STM32 filter settings

| Parameter | Value | Notes |
|---|---|---|
| `GNSS_TYPE` | `1` | Selects UM980/UM981/UM982 path, reboot to apply |

### Step 3 — ArduPilot FC settings

| Parameter | Value | Notes |
|---|---|---|
| `GPS1_TYPE` | `24` (UnicoreNMEA) | |
| `GPS_AUTO_CONFIG` | `0` | **Required.** Prevents ArduPilot from overwriting UM980 settings (see below) |
| `SERIAL3_BAUD` (GPS1 serial) | `460` | |

### Why these settings matter

- **`MODE ROVER UAV`** — sets the UM980 internal Kalman filter to UAV dynamics.
  Without this, the receiver uses a generic motion model that produces noisy
  velocity and position, causing red EKF bars in Mission Planner.
- **`CONFIG COM1 460800`** — matches the STM32 default GNSS baud. The autobaud
  scan finds 460800 first, so boot is fastest at this baud.
- **`GNGGA` at 5 Hz** — ArduPilot needs position updates at 5 Hz minimum.
  `GN`-prefix gives multi-constellation satellite counts. The driver uses GGA
  for fix status, satellite count, and HDOP.
- **`GNRMC` at 5 Hz** — provides date/time and backup velocity to ArduPilot.
- **`AGRICA` at 5 Hz** — ArduPilot's UnicoreNMEA driver uses AGRICA for
  high-precision 3D NED velocity, velocity accuracy, position accuracy, and
  undulation. Without AGRICA the EKF has no speed accuracy data and uses
  conservative defaults that degrade flight performance.
- **`GPS_AUTO_CONFIG = 0`** — **critical.** ArduPilot 4.6.x's UnicoreNMEA
  auto-config sends `MODE MOVINGBASE` and `CONFIG COM1 230400` to the UM980
  on every config cycle. `MODE MOVINGBASE` overwrites your `MODE ROVER UAV`,
  switching the receiver to a mode intended for moving RTK base stations.
  `CONFIG COM1 230400` changes the baud to 230400 while the FC serial port
  stays at 460800, breaking communication. Disabling auto-config prevents
  ArduPilot from touching the UM980 at all.
- **`CONFIG ANTIJAM FORCE`** — hardware anti-jamming always active.
- **`MASK 5`** — 5-degree elevation mask, filters low-elevation noisy satellites.
- `COM2` is not needed for the filter. Leave unused or use for diagnostics only.
- **GPGSA / GPGSV / GPGST are not needed** — the UnicoreNMEA driver does not
  parse these sentences. The driver gets DOP from GGA and accuracy data from
  AGRICA. Omitting them saves serial bandwidth.

### Detection feature coverage (UM980 vs u-blox)

The UM980/NMEA path supports all core detection features (position jump,
altitude, SNR, heading reversal, geo-fence, GPS time). However, three
advanced signals are u-blox only because NMEA does not provide the
underlying data:

- **Pseudorange residual analysis** — requires UBX NAV-SAT `prRes` field
- **GDOP sudden change** — requires UBX NAV-DOP `gDOP` field (NMEA GSA only has PDOP/HDOP/VDOP)
- **Clock bias jump** — requires UBX NAV-CLOCK

The spoofing confidence score (`DR_CONF`) adapts automatically — unavailable
signals are excluded from the weighted average.

### Common mistakes

- **Leaving `GPS_AUTO_CONFIG` at default (enabled)** — ArduPilot overwrites
  `MODE ROVER UAV` with `MODE MOVINGBASE` and changes baud to 230400, causing
  red velocity/position and intermittent GPS dropouts. Always set
  `GPS_AUTO_CONFIG = 0` when using a pre-configured UM980.
- Using the Holybro "factory reset" config without `MODE ROVER UAV` — this is
  a minimal reset profile, not a flight-ready config. Missing the rover mode
  causes red velocity/position in Mission Planner.
- Setting `CONFIG COM1 230400` — works but slower autobaud detection at boot.
  Use 460800 for fastest startup.
- Setting message rates to 1 Hz (period `1`) instead of 5 Hz (period `0.2`) —
  ArduPilot works but EKF performance is worse with 1 Hz GPS updates.
- Adding `GPGGA`, `GPRMC`, `GPGSA`, `GPGSV`, `GPGST` — the driver only needs
  `GNGGA`, `GNRMC`, and `AGRICA`. Extra sentences waste bandwidth and can slow
  parsing on the FC.

---

## u-blox M8 / M9 / M10 / F9 / F10

For direct single-receiver u-blox modules, the STM32 filter automatically configures the
receiver over UBX protocol at startup. No manual receiver configuration is needed for that path.

This direct u-blox path is intended for modules that expose a normal single-UART UBX
receiver stream and support the NAV-PVT / NAV-DOP / NAV-SAT message set used by the filter.
Typical examples include:

- M8-class modules such as `NEO-M8*`, `SAM-M8*`, `ZOE-M8*`
- M9-class modules such as `NEO-M9N`
- M10-class modules such as `MAX-M10*` and `MIA-M10*`
- F9-class modules such as `NEO-F9P` and `ZED-F9P`
- F10-class modules such as `NEO-F10N` and `DAN-F10N`

Older u-blox generations before M8 are not documented here because this project's default
profile relies on newer UBX navigation messages.

### Gateway / dual-receiver modules

Some GPS products put one or more internal u-blox receivers behind their own MCU and export
only one downstream GPS stream to the outside world. This includes dual-F9P products such as
Quadro GPS and UNA3 / UNA4-SFE style modules.

These modules can still be used with `GNSS_TYPE=0` if their external output is a normal
UBX / u-blox-compatible stream, but the STM32 filter cannot autobaud or fully auto-configure
them at boot. For this class of module:

1. Pre-configure the module on the vendor side so it emits the baud and UBX messages you want.
2. Set `GNSS_TYPE=0`.
3. Set `UBX_BAUD` to the exact downstream output baud in Mission Planner.
4. Reboot the STM32.

### Default auto-config profile (recommended, `UBX_BAUD = 0`)

Leave the u-blox at factory defaults if possible. At boot the filter scans common baud
rates and repeatedly sends this port command until the receiver moves to `460800`:

```text
UBX-CFG-PRT    UART1 460800 8N1 in=UBX out=UBX
```

Once the filter has switched its own UART to `460800`, it applies the following
ACK-verified profile:

```text
UBX-CFG-MSG    NMEA-GGA  off
UBX-CFG-MSG    NMEA-GLL  off
UBX-CFG-MSG    NMEA-GSA  off
UBX-CFG-MSG    NMEA-GSV  off
UBX-CFG-MSG    NMEA-RMC  off
UBX-CFG-MSG    NMEA-VTG  off
UBX-CFG-MSG    NMEA-ZDA  off

UBX-CFG-RATE   measRate=100ms navRate=1 timeRef=GPS
UBX-CFG-MSG    NAV-PVT     rate=1
UBX-CFG-MSG    NAV-POSLLH  rate=1
UBX-CFG-MSG    NAV-STATUS  rate=2
UBX-CFG-MSG    NAV-VELNED  rate=2
UBX-CFG-MSG    NAV-DOP     rate=2
UBX-CFG-MSG    NAV-SOL     rate=2
UBX-CFG-MSG    NAV-CLOCK   rate=2
UBX-CFG-MSG    NAV-SAT     rate=2

UBX-CFG-TMODE3 mode=disabled
UBX-CFG-CFG    save current configuration to BBR/Flash
```

Nothing to do on the receiver side.

**F10 / M10 note (firmware 1.6.2+):** newer u-blox generations use the
`CFG-VALSET` configuration interface and do not reliably respond to the
legacy `CFG-MSG` enable above for `NAV-SAT`. On top of the profile shown,
the filter sends a `CFG-VALSET` block that re-enables `NAV-SAT` at 5 Hz
on the active UART using `CFG-MSGOUT-UBX_NAV_SAT_UART1/2`. If you were
previously running an F10 or M10 without NAV-SAT coming through, upgrade
to 1.6.2+ and no u-center pre-config step is needed.

### Notes for default auto-config

- `NAV-PVT` and `NAV-POSLLH` run at 10 Hz. `NAV-STATUS`, `NAV-VELNED`, `NAV-DOP`,
  `NAV-SOL`, `NAV-CLOCK`, and `NAV-SAT` run at 5 Hz.
- `NAV-CLOCK` provides receiver clock bias/drift data used for spoofing detection (v1.5.5+).
- `UBX-CFG-PRT` is sent during the autobaud scan; the rest of the profile is
  ACK-verified after the link is already at `460800`.
- This path makes the receiver UART UBX-only. Keep the FC GPS type in `AUTO` or
  `u-blox`, not NMEA.

### Manual baud mode (`UBX_BAUD` set to receiver baud rate)

Use this if the u-blox must stay at a fixed baud (e.g. another device shares the port), or
if the GPS is a gateway module that outputs a preconfigured downstream UBX stream.

1. Pre-configure the u-blox in u-center with your target baud rate.
2. Enable UBX output and disable NMEA on the UART connected to the filter.
3. Enable **NAV-PVT** at 10 Hz minimum. NAV-DOP and NAV-SAT at 5 Hz recommended.
4. Set `UBX_BAUD` in Mission Planner to the configured baud and reboot.

At boot the filter only makes a best-effort volatile request for:

```text
UBX-CFG-RATE   measRate=100ms navRate=1 timeRef=GPS
UBX-CFG-MSG    NAV-PVT    rate=1
UBX-CFG-MSG    NAV-DOP    rate=2
UBX-CFG-MSG    NAV-CLOCK  rate=2
UBX-CFG-MSG    NAV-SAT    rate=2
```

It does **not** change UART1 baud, does **not** disable NMEA, and does **not** save to
BBR/Flash in manual mode.

Manual baud mode is the required path for gateway modules with an intermediary MCU, including
dual-F9P products such as Quadro GPS and UNA3 / UNA4-SFE. Do not use `UBX_BAUD=0` for those
modules; set the exact output baud explicitly.

### STM32 filter settings for u-blox

| Parameter | Value |
|---|---|
| `GNSS_TYPE` | `0` |
| `UBX_BAUD` | `0` for direct single-receiver auto-config, or exact baud (e.g. `460800`) for manual / gateway modules |

### ArduPilot FC settings for u-blox

| Parameter | Value |
|---|---|
| `GPS1_TYPE` | `1` (AUTO) or `2` (u-blox binary) |
| `SERIAL3_BAUD` (GPS1 serial) | `460` |

The filter forwards the raw UBX binary stream to the FC GPS port.
Set the FC to u-blox or AUTO type, not NMEA.
