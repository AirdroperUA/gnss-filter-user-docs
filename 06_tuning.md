# Runtime Tuning Manual

The filter exposes selected constants as MAVLink `PARAM_*` values, so you can tune behavior without recompiling firmware.

## Exposed Tune Parameters

| Param | Meaning | Default | Min | Max |
|---|---|---:|---:|---:|
| `RJ_BASE_M` | Base rejoin lateral gate (meters) | 120 | 10 | 10000 |
| `RJ_SPD_MULT` | Speed multiplier term for gate | 8 | 0 | 100 |
| `RJ_EXP_RMPS` | Gate expansion rate while in DR1 (m/s) | 8 | 0 | 200 |
| `RJ_EXP_MAXM` | Max expansion cap (m) | 200000 | 100 | 1000000 |
| `RJ_DOP2M` | HDOP to meters scaling | 20 | 0 | 200 |
| `RJ_HDOP_MUL` | HDOP multiplier | 2 | 0 | 20 |
| `RJ_MIN_SATS` | Rejoin minimum satellites | 8 | 4 | 30 |
| `RJ_MAX_HD` | Rejoin max HDOP | 2.5 | 0.5 | 10 |
| `RJ_LOIT_V` | Low-speed loiter threshold (m/s) | 0.8 | 0 | 10 |
| `RJ_LOIT_MS` | Loiter hold time before wider gate (ms) | 8000 | 500 | 120000 |
| `RJ_LOIT_GM` | Loiter gate override (m) | 2500 | 10 | 1000000 |
| `RJ_STAB_MS` | Stable window before rejoin/blend (ms) | 5000 | 500 | 120000 |
| `BLEND_MS` | Blend duration DR1 to DR0 (ms) | 10000 | 1000 | 120000 |
| `DR_LOCK_MS` | Minimum DR1 lockout window (ms) | 120000 | 0 | 600000 |
| `SP_JMP_MPS` | Spoof guard speed jump limit (m/s) | 5000 | 50 | 20000 |
| `SP_ABS_M` | Spoof guard absolute step limit (m) | 5000 | 100 | 50000 |
| `ARM_MIN_S` | Guard arming minimum satellites | 6 | 4 | 30 |
| `ARM_MAX_HD` | Guard arming max HDOP | 4 | 0.5 | 10 |
| `ARM_STABMS` | Guard arming stability window (ms) | 2000 | 200 | 10000 |
| `ALT_BSATS` | Alt-bias calibration min satellites | 8 | 4 | 30 |
| `ALT_BHDOP` | Alt-bias calibration max HDOP | 2.5 | 0.5 | 10 |
| `ALT_CALM_V` | Alt-bias max climb rate for calm window (m/s) | 2 | 0.1 | 20 |
| `ALT_BCMS` | Alt-bias calm window (ms) | 2000 | 200 | 30000 |
| `ALT_JMP_M` | Altitude absolute jump trip (m) | 80 | 5 | 500 |
| `ALT_RMPS` | Altitude rate trip threshold (m/s) | 40 | 1 | 200 |
| `ALT_RDTMS` | Altitude rate minimum dt window (ms) | 600 | 100 | 5000 |
| `ALT_RDH_M` | Altitude rate minimum delta-H (m) | 20 | 1 | 200 |
| `ALT_BSEP_M` | Alt-vs-baro separation trip (m) | 100 | 10 | 500 |
| `ALT_BSEPMS` | Alt-vs-baro hold time (ms) | 1500 | 100 | 20000 |
| `ALT_RJSEP` | Rejoin max altitude separation (m) | 50 | 5 | 500 |
| `DR_NOFIX` | Expose NO_FIX during DR/blend (0/1) | 1 | 0 | 1 |
| `RJ_REQEKF` | Require EKF OK window for rejoin (0/1) | 0 | 0 | 1 |
| `NUDGE_EN` | Enable DR1 nudge toward GNSS (0/1) | 1 | 0 | 1 |
| `NUDGE_MPS` | DR1 nudge speed (m/s) | 8 | 0 | 50 |
| `NUDGE_FRAC` | DR1 max nudge fraction per step | 0.5 | 0 | 1 |
| `EKF_TRIPMS` | EKF bad duration to trip DR1 (ms) | 1500 | 200 | 10000 |
| `EKF_OKRJMS` | EKF good duration needed for rejoin (ms) | 3000 | 200 | 20000 |
| `EKF_GRCMS` | EKF grace after DR0 exit (ms) | 7000 | 0 | 60000 |
| `BOOT_NSATS` | Boot north gate minimum satellites | 6 | 4 | 30 |
| `BOOT_NHDOP` | Boot north gate max HDOP | 4 | 0.5 | 10 |
| `BOOT_NSTAB` | Boot north gate stable window (ms) | 1000 | 200 | 20000 |
| `GN_HOTMS` | GNSS hotstart watchdog trigger (ms) | 15000 | 1000 | 120000 |
| `GN_COLDMS` | GNSS coldstart watchdog trigger (ms) | 45000 | 2000 | 300000 |
| `PT_ONLY` | Pass-through-only mode (0/1) | 1 | 0 | 1 |
| `FCGPS_FWD` | Force FC GPS forwarding even in DR1 (0/1) | 0 | 0 | 1 |
| `NMEA_NOFIX` | Emit NMEA no-fix beacons (0/1) | 0 | 0 | 1 |
| `LOG_MS` | Filter status log period (ms) | 15000 | 1000 | 120000 |
| `NAV_AGEMS` | Max NAV age for valid/present GPS (ms) | 5000 | 200 | 60000 |
| `NAV_STALLMS` | NAV stall warning threshold (ms) | 7000 | 500 | 120000 |
| `GNSS_SWAP` | Swap GNSS UART RX/TX pins (0/1) | 0 | 0 | 1 |
| `SNR_EN` | Enable SNR-spread spoof guard (0/1) | 0 | 0 | 1 |
| `SNR_MSATS` | SNR guard minimum satellites | 8 | 4 | 30 |
| `SNR_DMAX` | Max allowed SNR spread (max-min, dB-Hz) to trigger | 6 | 1 | 40 |
| `SNR_MMAX` | Minimum required strongest SNR (dB-Hz) | 35 | 10 | 60 |
| `SNR_HOLDMS` | SNR guard hold time before DR1 (ms) | 1500 | 100 | 20000 |
| `SNR_MAXAGE` | Max age of SNR sample (ms) | 2000 | 100 | 10000 |

## Persistence

- Changes are applied immediately.
- Filter auto-saves to non-volatile storage about 1.5s after the last change.

## Using `tools/tune_cli.py`

Install dependency:

```bash

python -m pip install pymavlink

```

List current values:

```bash

python tools/tune_cli.py --port COM12 --baud 115200 list

```

Read one value:

```bash

python tools/tune_cli.py --port COM12 --baud 115200 get BLEND_MS

```

Set one value:

```bash

python tools/tune_cli.py --port COM12 --baud 115200 set RJ_BASE_M 180

```

Export snapshot:

```bash

python tools/tune_cli.py --port COM12 --baud 115200 export tune_baseline.json

```

Import snapshot:

```bash

python tools/tune_cli.py --port COM12 --baud 115200 import tune_baseline.json

```

Strict import (fail on unknown keys):

```bash

python tools/tune_cli.py --port COM12 --baud 115200 import tune_baseline.json --strict

```

## Practical Workflow

1. Export baseline JSON.
2. Change one or two params at a time.
3. Flight test and log.
4. Keep known-good JSON profiles so you can roll back quickly.

Notes:

- `GNSS_SWAP` applies a live UART remap and triggers GNSS reconfiguration.
- If you lose GNSS after changing `GNSS_SWAP`, set it back to previous value.

## Trigger Examples

These examples assume guard arming has already happened (`ARM_MIN_S`, `ARM_MAX_HD`, `ARM_STABMS` satisfied).

### SNR spread trigger (new guard)

Settings:

- `SNR_EN=1`
- `SNR_MSATS=8`
- `SNR_DMAX=6`
- `SNR_MMAX=35`
- `SNR_HOLDMS=1500`
- `SNR_MAXAGE=2000`

Will trigger DR1:

- 12 satellites, C/N0 values around `36..40` dB-Hz for more than 1.5 s.
- `max=40`, `min=36`, `span=4` (<= 6), and strongest signal is >= 35.

Will not trigger DR1:

- Same narrow span, but `max=30` (< `SNR_MMAX`), or sample is stale (`age > SNR_MAXAGE`), or satellite count is below `SNR_MSATS`.

### Position jump trigger

Settings:

- `SP_ABS_M=5000`
- `SP_JMP_MPS=5000`

Will trigger DR1:

- One fix jumps ~12 km in ~1 s (`12000 m` > both absolute and speed-based limits).

Will not trigger DR1:

- 50 m movement in 1 s.

### Altitude absolute jump trigger

Settings:

- `ALT_JMP_M=80`

Will trigger DR1:

- GNSS altitude step from `120 m` to `230 m` in one update (`+110 m`).

Will not trigger DR1:

- Normal climb changes within threshold.

### Altitude rate trigger

Settings:

- `ALT_RMPS=40`
- `ALT_RDTMS=600`
- `ALT_RDH_M=20`

Will trigger DR1:

- ~30 m altitude change in 600 ms (`50 m/s` and delta-H >= 20 m).

Will not trigger DR1:

- 10 m change over 1 s (`10 m/s`) or short/noisy movement below `ALT_RDH_M`.

### Altitude vs baro separation trigger

Settings:

- `ALT_BSEP_M=100`
- `ALT_BSEPMS=1500`

Will trigger DR1:

- Persistent GNSS-vs-baro separation > 100 m for more than 1.5 s.

Will not trigger DR1:

- Brief spikes that recover before hold time.

### EKF trigger

Settings:

- `EKF_TRIPMS=1500`

Will trigger DR1:

- EKF reports bad horizontal state (or glitch/accel error) continuously for > 1.5 s.

Will not trigger DR1:

- Short EKF disturbances shorter than `EKF_TRIPMS`.

## Rejoin Examples

### Fast rejoin (looser)

- `RJ_MIN_SATS=8`
- `RJ_MAX_HD=2.5`
- `RJ_STAB_MS=5000`
- `RJ_REQEKF=0`

Rejoin can start as soon as GNSS quality and geometry checks are stable for `RJ_STAB_MS`, then blend for `BLEND_MS`.

### Conservative rejoin

- `RJ_REQEKF=1`
- `EKF_OKRJMS=5000`
- `DR_LOCK_MS=120000`

Even with good GNSS, DR0 restore waits for both EKF-good window and lockout expiry.
