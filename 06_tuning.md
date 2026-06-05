# Runtime Tuning Manual

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

The filter exposes selected constants as MAVLink `PARAM_*` values, so you can tune behavior without updating firmware.

## Mission Planner Parameter Descriptions

Mission Planner may show the spoofing-board parameters as raw names only. To add
descriptions, ranges, units, and option labels, install the Mission Planner
metadata pack:

[Download AirDroper Mission Planner Params](https://gps.airdroper.org/download/mission-planner-mod)

Unzip it, close Mission Planner, then double-click
`install_airdroper_params.bat`. The same ZIP includes ready-to-load Mission
Planner `.param` presets. The installer supports both modern
`*.apm.pdef.xml` metadata and older cached `ParameterMetaData.xml`
installations. Use `airdroper_filter_field_safe.param` as the normal field
baseline after bench testing; it keeps `SNR_EN=0`, sets `LOG_MS=10000`, and
sets `DR_LOCK_MS=120000`.

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
| `DR_LOCK_MS` | Minimum DR1 lockout window (ms) | 15000 | 1000 | 600000 |
| `DR1_MAXMS` | Maximum DR1 latch duration before forced exit after `DR_LOCK_MS` (ms, 0=disabled) | 0 | 0 | 3600000 |
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
| `RJ_REQEKF` | Require EKF OK window for rejoin (0/1) | 0 | 0 | 1 |
| `NUDGE_EN` | Enable DR1 nudge toward GNSS (0/1) | 1 | 0 | 1 |
| `NUDGE_MPS` | DR1 nudge speed (m/s) | 8 | 0 | 50 |
| `NUDGE_FRAC` | DR1 max nudge fraction per step | 0.5 | 0 | 1 |
| `EKF_TRIPMS` | EKF bad duration to trip DR1 (ms) | 0 | 0 | 10000 |
| `EKF_OKRJMS` | EKF good duration needed for rejoin (ms) | 3000 | 200 | 20000 |
| `EKF_GRCMS` | EKF grace after DR1 exit (ms) | 7000 | 0 | 60000 |
| `BOOT_NSATS` | Boot north gate minimum satellites | 6 | 4 | 30 |
| `BOOT_NHDOP` | Boot north gate max HDOP | 4 | 0.5 | 10 |
| `BOOT_NSTAB` | Boot north gate stable window (ms) | 1000 | 200 | 20000 |
| `BOOT_DLYMS` | Startup DR trigger guard delay (ms) | 20000 | 2000 | 120000 |
| `GN_HOTMS` | GNSS hotstart watchdog trigger (ms) | 15000 | 1000 | 120000 |
| `GN_COLDMS` | GNSS coldstart watchdog trigger (ms) | 45000 | 2000 | 300000 |
| `PT_ONLY` | Pass-through-only mode (0/1) | 1 | 0 | 1 |
| `FCGPS_UART` | FC GPS UART on A11/A12: 1=enabled (normal), 0=released (A11/A12 in input mode) | 1 | 0 | 1 |
| `FCGPS_FWD` | Force FC GPS UART on and raw-forward GPS, bypassing DR1, boot north gate, and hemisphere fence (bench only, 0/1) | 0 | 0 | 1 |
| `LOG_MS` | Filter status log period (ms) | 10000 | 1000 | 120000 |
| `NAV_AGEMS` | Max NAV age for valid/present GPS (ms) | 5000 | 200 | 60000 |
| `NAV_STALLMS` | NAV stall warning threshold (ms) | 7000 | 500 | 120000 |
| `UBX_BAUD` | u-blox baud control: 0=autoconfig ON, >0=manual baud (reboot to apply) | 0 | 0 | 2000000 |
| `UBX_RESET` | One-shot u-blox recovery command: 0=idle, 1=hot, 2=cold, 3=clear saved config | 0 | 0 | 3 |
| `GNSS_TYPE` | Receiver mode: 0=u-blox/UBX, 1=UM980/UM981/UM982 NMEA, 2=Septentrio Mosaic X5 NMEA (reboot to apply) | 0 | 0 | 2 |
| `UM980_HIGHDYN` | UM980/UM981/UM982 rover mode: 0=MODE ROVER UAV, 1=MODE ROVER UAV HIGHDYN (reboot to apply) | 0 | 0 | 1 |
| `SNR_EN` | Enable SNR-spread spoof guard (0/1) | 0 | 0 | 1 |
| `SNR_MSATS` | SNR guard minimum satellites | 8 | 4 | 30 |
| `SNR_DMAX` | Max allowed SNR spread (max-min, dB-Hz) to trigger | 6 | 1 | 40 |
| `SNR_MMAX` | Minimum required strongest SNR (dB-Hz) | 35 | 10 | 60 |
| `SNR_HOLDMS` | SNR guard hold time before DR1 (ms) | 1500 | 100 | 20000 |
| `SNR_MAXAGE` | Max age of SNR sample (ms) | 2000 | 100 | 10000 |
| `FENCE_RAD` | Geo-fence radius from first fix (m, 0=disabled) | 0 | 0 | 2000000 |
| `HEMI_EN` | Northern hemisphere hard fence (locked on) | 1 | 1 | 1 |

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
- **DR_LOCK_MS**: Minimum lockout time after entering DR1. During this time the rejoin stability timer, GNSS blend, and DR0 exit are blocked even if GNSS looks good. It also takes precedence over `DR1_MAXMS`, so DR1 cannot be force-exited before this lock window expires. Short values are useful for bench testing; after bench validation, set `DR_LOCK_MS=120000` or higher for real flights unless you intentionally need faster recovery. This keeps DR1 active for at least 2 minutes after any trigger and avoids rapid DR0/DR1 flip-flopping.
- **DR1_MAXMS**: Hard upper bound on how long the filter is allowed to stay latched in DR1 after the `DR_LOCK_MS` minimum has elapsed. When non-zero, DR1 is forcibly exited after this many milliseconds regardless of spoof confidence, but not before the lock window. Default `0` = disabled (infinite latch — the filter stays in DR1 until rejoin gates clear normally). Use a non-zero value only if your mission profile prefers "possibly-wrong GPS" over "inertial-only forever" — e.g. a long-range flight where losing GPS for the entire remaining leg is worse than accepting a partially-recovered spoofed signal. Most users should leave this at `0`.

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

- **PT_ONLY**: Pass-through-only mode. The filter acts as a clean DR0/DR1 switch — raw GNSS bytes or silence. No synthetic position or blending is used.
- **FCGPS_UART**: Controls the FC GPS UART on `A11/A12`. `1` = normal operation (GPS forwarding active). `0` = releases `A11/A12` into input mode. Do not set `0` during flight — this disables GPS forwarding to the FC.
- **FCGPS_FWD**: Forces the FC GPS UART on and raw-forwards GNSS to it. Use only for diagnostics; it bypasses the DR1 latch, boot north gate, and `HEMI_EN` hard north fence so the raw GPS path can be verified on a bench. In normal protected mode on u-blox firmware v1.6.18+, FC GPS back-channel bytes are drained and are not forwarded into the receiver.

### EKF gates

- **RJ_REQEKF**: If enabled, rejoin requires a **fresh** EKF-OK window in addition to GNSS quality. The filter demands a recent `EKF_STATUS_REPORT` message (refreshed within the last 2 s) so that a stale OK-flag held across a MAVLink link drop cannot silently pass the gate on link return. Safer, but slower to rejoin.
- **EKF_TRIPMS**: Time EKF must be bad before DR1 triggers. `0` means immediate trip with no delay.
- **EKF_OKRJMS**: Minimum time EKF must be good before rejoin when `RJ_REQEKF` is enabled.
- **EKF_GRCMS**: Grace period after exiting DR1 during which EKF issues are ignored. Helps avoid immediate re-trips.

### Boot north gate

- **BOOT_NSATS**: Minimum satellites required before publishing GNSS on boot (if north gate is active).
- **BOOT_NHDOP**: Maximum HDOP allowed for boot publishing.
- **BOOT_NSTAB**: Stability window before the initial north gate unlocks.
- **BOOT_DLYMS**: Additional startup guard delay before spoof and EKF trip logic can enter DR1. Increase this if the FC and GNSS need extra time to stabilize after power-on and you see false DR1 right after boot. Minimum is clamped to **2000 ms** — any smaller value stored in EEPROM is corrected on load, because zero would collapse the boot-stabilization window entirely.

### GNSS recovery watchdog

- **GN_HOTMS**: Time in DR1 with no valid fix before GNSS hotstart is triggered (also used when satellites are zero).
- **GN_COLDMS**: Time in DR1 with no valid fix before GNSS coldstart is triggered (also used when satellites are zero).

### GNSS handling and logging

- **LOG_MS**: Status log period (ms). Lower values give more frequent logs but add traffic.
- In Mission Planner `Messages`, the default user-visible behavior is roughly one periodic log pair every **10 seconds**.
- **NAV_AGEMS**: Maximum age to consider GNSS position/altitude data valid. If updates get older than this, the filter treats the fix as stale for rejoin, forwarding, and receiver recovery logic.
- **NAV_STALLMS**: NAV stall warning threshold. If exceeded, a warning is logged.
- **UBX_BAUD**: u-blox baud/autoconfig control. `0` keeps autoconfig enabled (default behavior) for direct single-receiver u-blox modules. In firmware v1.6.22+ that autoconfig boot path clears/loads receiver defaults, rescans baud, then writes and saves the filter's UBX profile. Any value `>0` disables the full autoconfig path and uses this manual baud directly. Applied after reboot. In manual mode the filter still makes a best-effort request for `NAV-SAT` so SNR can work, but if the receiver ignores that request, `SNR=NA` is still expected. Gateway modules with an intermediary MCU - including dual-F9P products such as Quadro GPS and UNA3 / UNA4-SFE - must use manual baud (`UBX_BAUD` set explicitly); filter autobaud is not possible for that class of device.
- **UBX_RESET**: One-shot u-blox recovery command available in firmware v1.6.15+. It is a virtual parameter: the value always reports back as `0` and is not stored in the tuning blob. Set `1` for hot start, `2` for cold start, or `3` to clear saved receiver BBR/Flash configuration, reload defaults, reset the receiver, and let the STM32 reinitialize GNSS. Use `3` only on the bench or during recovery, because it deletes the receiver's saved u-blox configuration; do not make it a normal default setting.
- **SNR=NA with SNR_EN=1**: If `SNR_EN=1` and `SNR=NA` persists beyond 30 seconds after boot, the filter logs `WARNING: SNR_EN=1 but SNR=NA/stale (no fresh GSV/NAV-SAT?)`. This means the receiver is not providing fresh SNR data. The SNR guard will not trip in this state — either fix receiver configuration or set `SNR_EN=0`. On u-blox firmware v1.6.12+, a `snrdbg` line decodes the NAV-SAT stream: `n` frames seen, `a` frame age, `l` last length, `s` reported satellites, `g` usable C/N0 satellites, `o` oversize drops, `b` malformed/checksum drops.
- **u-blox NAV-SAT recovery**: v1.6.15+ re-enables NAV-SAT using legacy `CFG-MSG` plus `CFG-VALSET` on UART1/UART2 only when NAV-SAT frames are missing or stale. If `snrdbg` shows fresh NAV-SAT with `g0`, the receiver is alive but currently has no usable C/N0, so the firmware does not keep rewriting configuration. v1.6.16+ starts the recovery timer as soon as SNR goes stale, so intermittent NAV-SAT loss typically recovers after about one stale window instead of two. v1.6.18+ also prevents the normal FC GPS back-channel from changing the u-blox receiver profile, which avoids ArduPilot auto-config writes followed by stale NAV-SAT. v1.6.21+ uses a faster first re-enable, about 8 seconds, when a healthy fix already exists and NAV-SAT disappears; startup and no-fix cases keep the slower 30-second path.
- **u-blox no-fix diagnostics and assist**: v1.6.15+ polls `UBX-MON-RF`, `UBX-SEC-SIG`, and `UBX-CFG-GNSS` while a u-blox receiver has no valid position fix or `SATS=0`. Mission Planner then shows `ubxpvt ...` for NAV-PVT fix flags, `ubxrf ...` for antenna/RF state, `ubxsig ...` for explicit jamming/spoofing state when supported, and `ubxgnss ...` for enabled GNSS constellation blocks. `ubxgnss en00` points to disabled constellations; high `ubxrf c` or `n`, abnormal antenna status, or `ubxsig j2`/`j3` point to RF/antenna/interference problems. v1.6.19+ also sends an automatic u-blox cold start plus STM32 reinit after about 2 minutes at `SATS=0`. v1.6.22+ direct autoconfig also starts from receiver defaults at boot; use `UBX_BAUD>0` to preserve custom/gateway receiver profiles.
- **GNSS_TYPE**: Receiver mode selector. `0` = u-blox/UBX, `1` = UM980/UM981/UM982 NMEA, `2` = Septentrio Mosaic X5 NMEA. Change is saved immediately but applied after STM32 reboot. Mosaic X5 uses passive NMEA parsing and the STM32 does not send Septentrio reset or auto-configuration commands.
- **UM980_HIGHDYN**: UM980/UM981/UM982 rover dynamics mode. `0` = `MODE ROVER UAV` (standard, default). `1` = `MODE ROVER UAV HIGHDYN` (use for aggressive airframes with rapid attitude changes). Reserved for future use — currently has no runtime effect. The STM32 does **not** send any `MODE` command to the UM980.

### Geo-fence

- **DR1_MAXMS**: See the full description above under *Rejoin gate and timing* — this is the hard upper bound on time spent in DR1 before a forced exit, after the `DR_LOCK_MS` minimum has elapsed.
- **FENCE_RAD**: Geo-fence radius in meters from the first-fix position (max 2,000,000 m = 2000 km). **Default `0` (disabled)** — the fence is opt-in. If GPS reports a position outside this radius, DR1 triggers. Catches spoofing attacks that slowly drift position over time. Note: the fence center is set at first fix after boot — not at an arming position, so enable it only for missions where the first fix is close to the mission area. Typical values once enabled: `50000` (50 km) for local flights, `600000` (600 km) for long-range.

### Hemisphere fence

- **HEMI_EN**: Compatibility parameter for the northern hemisphere hard fence. It is locked to `1`: the normal forwarding path waits for a stable northern fix before publishing FC GPS and rejects south/equator fixes in the parser. Runtime or stored attempts to set `0` are clamped back to `1`. `FCGPS_FWD=1` is the only diagnostic raw-forwarding bypass and must not be used in flight.

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
- `UBX_RESET` is a command, not a stored setting; it returns to `0` after every write.
- `GNSS_TYPE` and `UBX_BAUD` require reboot to apply.
- After a parameter write, wait about **2-3 seconds** to allow the save cycle to complete.
- Reboot after every parameter change is **not** required.
- Reboot STM32 (`NRST` or power cycle) when changing `GNSS_TYPE` or `UBX_BAUD`, or if behavior does not match updated values.

## Using Mission Planner for Parameter Writes

Use Mission Planner to read and write all STM32 filter params:

1. Open `Config/Tuning` -> `Full Parameter List`.
2. Select the STM32 filter target (**SYSID 42**) in the system dropdown.
3. Click **Refresh Params**.
4. Edit one or more values.
5. Click **Write Params**.
6. Click **Refresh Params** again to verify saved values.

Notes:

- If a value does not update on the first try, click **Write Params** again. 1-2 attempts are normal; 3+ attempts indicate a very busy MAVLink link.
- After writing, allow up to 30-45 seconds for link recovery in heavy telemetry conditions.
- Reboot is needed for `GNSS_TYPE` and `UBX_BAUD`; most other params apply without reboot.

## Practical Workflow

1. In Mission Planner, click **Save to file** to store a baseline profile.
2. Change one or two params at a time.
3. Click **Write Params**, then **Refresh Params** to confirm values.
4. Flight test and review logs.
5. Keep known-good saved files so you can roll back quickly.

Notes:

- If your custom u-blox receiver does not accept filter autoconfig, set `UBX_BAUD` to the receiver baud and reboot.
- To fix reversed GNSS TX/RX, correct physical wiring (GNSS TX -> A3, GNSS RX -> A2).

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

Even with good GNSS, DR0 restore waits for both the EKF-good window and the lockout expiry. Use shorter values only for bench testing; after bench validation, `120000` ms is the recommended minimum field setting.
