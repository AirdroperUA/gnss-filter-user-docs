# Runtime Tuning Manual

The filter exposes selected constants as MAVLink `PARAM_*` values, so you can tune behavior without updating firmware.

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

## Parameter Reference (detailed)

### Rejoin gate and timing

- **RJ_BASE_M**: Base lateral gate used when evaluating rejoin. It is the starting allowed distance between the synthetic position and the real GNSS position. Increase if long DR1 periods cause large drift; decrease to reduce the chance of accepting spoofed jumps.
- **RJ_SPD_MULT**: Speed multiplier term added to the rejoin gate. It increases tolerance at higher air/ground speeds. Too high can allow large jumps at speed; too low can prevent rejoin when moving fast.
- **RJ_EXP_RMPS**: Expansion rate of the rejoin gate while in DR1 (meters per second). It lets the allowed gate grow over time. Higher values rejoin sooner after long DR1 periods but reduce protection against large offsets.
- **RJ_EXP_MAXM**: Maximum cap on the expansion term. This **does not limit flight distance**; it only caps how large the rejoin gate can grow. If too low, rejoin may never happen after long DR1; if too high, very large offsets can be accepted.
- **RJ_DOP2M**: Converts HDOP into meters for the rejoin gate. Higher values make the gate larger when HDOP is high. Lower values make rejoin stricter under poor geometry.
- **RJ_HDOP_MUL**: Additional multiplier on the HDOP term. Use this to scale overall DOP influence without changing the base conversion.
- **RJ_MIN_SATS**: Minimum satellites required for rejoin. Raise to demand a stronger fix; lower to rejoin sooner in weak sky conditions.
- **RJ_MAX_HD**: Maximum HDOP allowed for rejoin. Lower values require better geometry; higher values allow rejoin under noisier GNSS.
- **RJ_LOIT_V**: Loiter speed threshold. If GNSS quality is loose and speed stays below this, the loiter gate can be used.
- **RJ_LOIT_MS**: How long the vehicle must remain below the loiter speed before the loiter gate applies. Longer times reduce false rejoin when moving slowly.
- **RJ_LOIT_GM**: Loiter gate override distance. It replaces the dynamic gate after the loiter hold time. Increase for very slow loitering; decrease for tighter protection.
- **RJ_STAB_MS**: Required stability window before rejoin/blend starts. Longer values improve safety but delay rejoin.
- **BLEND_MS**: Duration of the DR1 to DR0 blend. Longer blends smooth transitions; shorter blends rejoin faster.
- **DR_LOCK_MS**: Minimum lockout time after entering DR1. During this time rejoin is blocked even if GNSS looks good. Increase to avoid rapid flip-flopping; decrease for faster recovery.

### Spoof guard (position jump)

- **SP_JMP_MPS**: Speed-based spoof limit. If the implied speed between fixes exceeds this, DR1 triggers once armed. Lower values are stricter but can false-trigger on jitter; higher values are more permissive.
- **SP_ABS_M**: Absolute distance step limit. If the fix jumps more than this in one update, DR1 triggers once armed. Use this to catch large teleports even at low update rates.

### Guard arming (when spoof checks start)

- **ARM_MIN_S**: Minimum satellites before spoof guard arms. Prevents false triggers at boot. Increase for safer arming; decrease if you need early protection.
- **ARM_MAX_HD**: Maximum HDOP allowed for arming. Lower means higher quality required.
- **ARM_STABMS**: Time GNSS quality must remain good before the guard arms. Longer is safer; shorter arms faster.

### Altitude guards

- **ALT_BSATS**: Minimum satellites to calibrate GNSS-vs-baro bias. If too high, bias may never lock in poor sky conditions.
- **ALT_BHDOP**: Maximum HDOP allowed for bias calibration. Lower values require better geometry.
- **ALT_CALM_V**: Max climb rate allowed during bias calibration. Prevents bias learning while maneuvering.
- **ALT_BCMS**: Duration of the calm window for bias calibration.
- **ALT_JMP_M**: Absolute altitude jump threshold. Large single-step changes beyond this trigger DR1.
- **ALT_RMPS**: Altitude rate threshold (m/s). Sustained rate above this can trigger DR1 when combined with other rate settings.
- **ALT_RDTMS**: Minimum time window used for altitude rate detection.
- **ALT_RDH_M**: Minimum altitude delta required inside the rate window. Prevents false triggers from noise.
- **ALT_BSEP_M**: Maximum GNSS-vs-baro separation. Exceeding this for the hold time triggers DR1.
- **ALT_BSEPMS**: Hold time for altitude separation before triggering.
- **ALT_RJSEP**: Maximum altitude separation allowed for rejoin. If GNSS is too far from expected baro altitude, rejoin is blocked.

### DR behavior

- **DR_NOFIX**: If enabled, the filter reports NO_FIX to the FC during DR1/blend. This prevents the FC from using GNSS while protected.
- **PT_ONLY**: Pass-through-only mode. The filter only blocks GNSS during DR1; no synthetic position or blending is used.
- **FCGPS_FWD**: Forces GNSS forwarding even in DR1. Use only for diagnostics; it defeats protection.
- **NMEA_NOFIX**: Emits NMEA “no-fix” beacons (optional). Useful for some FC configurations that expect NMEA signals.

### EKF gates

- **RJ_REQEKF**: If enabled, rejoin requires an EKF OK window in addition to GNSS quality. Safer, but slower to rejoin.
- **EKF_TRIPMS**: Time EKF must be bad before DR1 triggers. Shorter values are more sensitive; longer values tolerate brief glitches.
- **EKF_OKRJMS**: Minimum time EKF must be good before rejoin when `RJ_REQEKF` is enabled.
- **EKF_GRCMS**: Grace period after exiting DR1 during which EKF issues are ignored. Helps avoid immediate re-trips.

### Boot north gate

- **BOOT_NSATS**: Minimum satellites required before publishing GNSS on boot (if north gate is active).
- **BOOT_NHDOP**: Maximum HDOP allowed for boot publishing.
- **BOOT_NSTAB**: Stability window before the initial north gate unlocks.

### GNSS recovery watchdog

- **GN_HOTMS**: Time with zero satellites before a GNSS hotstart is triggered (during DR1).
- **GN_COLDMS**: Time with zero satellites before a GNSS coldstart is triggered (during DR1).

### GNSS handling and logging

- **LOG_MS**: Status log period (ms). Lower values give more frequent logs but add traffic.
- **NAV_AGEMS**: Maximum NAV age to consider GNSS data valid/present.
- **NAV_STALLMS**: NAV stall warning threshold. If exceeded, a warning is logged.
- **GNSS_SWAP**: Swaps GNSS RX/TX pin roles at runtime. Use if TX/RX are physically reversed.

### SNR guard (nearby jammer/spoofer)

- **SNR_EN**: Enables SNR-spread guard. When on, tight SNR spread can trigger DR1.
- **SNR_MSATS**: Minimum satellites required for the SNR guard to evaluate.
- **SNR_DMAX**: Maximum allowed SNR spread (max-min) before triggering. Lower values are stricter.
- **SNR_MMAX**: Minimum required strongest SNR. Prevents triggering on low-signal noise.
- **SNR_HOLDMS**: Time the SNR condition must persist before DR1 triggers.
- **SNR_MAXAGE**: Maximum age of the SNR sample. Old samples are ignored.

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
