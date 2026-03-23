# GNSS Receiver Configuration

Set `GNSS_TYPE` in Mission Planner to match your receiver, then reboot the STM32.

| `GNSS_TYPE` | Receiver family | ArduPilot `GPS1_TYPE` |
|---|---|---|
| `0` | u-blox M8 / M9 / M10 | `1` (AUTO) or `2` (u-blox) |
| `1` | Unicore UM980 / UM981 | `24` (UnicoreNMEA) |

---

## UM980 / UM981

**No manual pre-configuration required.** When `GNSS_TYPE=1`, the STM32 automatically
sends the full configuration profile to the UM980 over COM1 at every boot — the same
way it auto-configures u-blox receivers. The receiver mode, anti-jam settings, and all
output messages are applied and saved to the UM980's non-volatile memory.

### STM32 filter settings for UM980

| Parameter | Value | Notes |
|---|---|---|
| `GNSS_TYPE` | `1` | Selects UM980/UM981 path, reboot to apply |
| `UM980_HIGHDYN` | `0` | Standard UAV mode (default) |
| `UM980_HIGHDYN` | `1` | High-dynamic UAV mode — use for aggressive airframes |
| `UBX_BAUD` | `0` | Leave at default (unused for UM980) |

After changing `UM980_HIGHDYN`, reboot the STM32 so the new `MODE ROVER UAV [HIGHDYN]`
command is sent to the receiver.

### ArduPilot FC settings for UM980

| Parameter | Value |
|---|---|
| `GPS1_TYPE` | `24` (UnicoreNMEA) |
| `SERIAL3_BAUD` (GPS1 serial) | `460` |

### What the auto-config applies

The following profile is sent to the UM980 at every boot:

```text
UNLOG COM1

MODE ROVER UAV          (or MODE ROVER UAV HIGHDYN if UM980_HIGHDYN=1)
CONFIG ANTIJAM FORCE
CONFIG MMP ENABLE
CONFIG PVTALG MULTI
CONFIG SMOOTH PSRVEL ENABLE
MASK 5
CONFIG NMEA0183 V410

AGRICA COM1 1
GNGGA COM1 1
GPGGA COM1 1
GPRMC COM1 1
GPGSA COM1 1
GPGSV COM1 1
GPGBS COM1 1
GPGST COM1 1
PVTSLNB COM1 1
OBSVMCMPB COM1 0.1
SATSINFOB COM1 1
BESTSATB COM1 1
STADOPB COM1 1
JAMSTATUSB COM1 1
FREQJAMSTATUSB COM1 1
HWSTATUSB COM1 1
AGCB COM1 1
RTKSTATUSB COM1 1
RTCMSTATUSB COM1 ONCHANGED

SAVECONFIG
```

### Notes

- `GPGGA`, `GPRMC`, `PVTSLNB`, and `AGRICA` are configured at **1 Hz**.
  Values of 0.1 Hz cause ArduPilot to intermittently show "GPS 1: not healthy"
  because its health watchdog times out between 10-second updates.
- `GNGGA` is also enabled at 1 Hz so the filter sees all-constellation satellite counts,
  while `GPGGA` remains enabled for FC compatibility.
- `GPGSV` is used for SNR data only. The filter's low-satellite guard uses the
  satellites-in-use count from `GGA`, not the satellites-in-view count from `GSV`.
- `COM2` is not needed for the filter. Leave unused or use for diagnostics only.
- The auto-config does **not** change the COM1 baud rate. The STM32 autobaud scan
  finds the receiver at its current speed; that speed is preserved in `SAVECONFIG`.
  UM980 factory default is 460800 — no action needed for a fresh receiver.

---

## u-blox M8 / M9 / M10

The STM32 filter automatically configures u-blox receivers over UBX protocol at startup.
No manual receiver configuration is needed.

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
UBX-CFG-MSG    NAV-SAT     rate=2

UBX-CFG-TMODE3 mode=disabled
UBX-CFG-CFG    save current configuration to BBR/Flash
```

Nothing to do on the receiver side.

### Notes for default auto-config

- `NAV-PVT` and `NAV-POSLLH` run at 10 Hz. `NAV-STATUS`, `NAV-VELNED`, `NAV-DOP`,
  `NAV-SOL`, and `NAV-SAT` run at 5 Hz.
- `UBX-CFG-PRT` is sent during the autobaud scan; the rest of the profile is
  ACK-verified after the link is already at `460800`.
- This path makes the receiver UART UBX-only. Keep the FC GPS type in `AUTO` or
  `u-blox`, not NMEA.

### Manual baud mode (`UBX_BAUD` set to receiver baud rate)

Use this if the u-blox must stay at a fixed baud (e.g. another device shares the port).

1. Pre-configure the u-blox in u-center with your target baud rate.
2. Enable UBX output and disable NMEA on the UART connected to the filter.
3. Enable **NAV-PVT** at 10 Hz minimum. NAV-DOP and NAV-SAT at 5 Hz recommended.
4. Set `UBX_BAUD` in Mission Planner to the configured baud and reboot.

At boot the filter only makes a best-effort volatile request for:

```text
UBX-CFG-RATE   measRate=100ms navRate=1 timeRef=GPS
UBX-CFG-MSG    NAV-PVT  rate=1
UBX-CFG-MSG    NAV-DOP  rate=2
UBX-CFG-MSG    NAV-SAT  rate=2
```

It does **not** change UART1 baud, does **not** disable NMEA, and does **not** save to
BBR/Flash in manual mode.

### STM32 filter settings for u-blox

| Parameter | Value |
|---|---|
| `GNSS_TYPE` | `0` |
| `UBX_BAUD` | `0` for auto, or exact baud (e.g. `460800`) for manual |

### ArduPilot FC settings for u-blox

| Parameter | Value |
|---|---|
| `GPS1_TYPE` | `1` (AUTO) or `2` (u-blox binary) |
| `SERIAL3_BAUD` (GPS1 serial) | `460` |

The filter forwards the raw UBX binary stream to the FC GPS port —
set the FC to u-blox or AUTO type, not NMEA.
