# Runtime Tuning Manual

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

The filter exposes selected constants as MAVLink `PARAM_*` values, so you can tune behavior without updating firmware.

## Mission Planner Parameter Descriptions

Mission Planner may show the spoofing-board parameters as raw names only. To add
descriptions, ranges, units, and option labels, install the Mission Planner
metadata pack:

[Download AirDroper Mission Planner Mod](https://gps.airdroper.org/download/mission-planner-mod)

Unzip it, close Mission Planner, then double-click
`install_airdroper_params.bat`. The same ZIP includes ready-to-load Mission
Planner `.param` presets. The installer supports both modern
`*.apm.pdef.xml` metadata and older cached `ParameterMetaData.xml`
installations. On the H743 DroneCAN fixed-wing build, use
`airdroper_filter_field_safe.param` as the production baseline after bench
testing. It is tuned for cruise near 120 km/h and assumes validated legitimate
ground speed does not exceed 65 m/s (234 km/h). It enables the SNR guard, uses
conservative position-jump thresholds and independent recovery evidence, redacts coordinates
from filter status text, and keeps DR1 locked for at least two minutes. Do not
load this H743 profile onto F401 without deliberately reviewing every value;
faster H743 aircraft also require log-based jump-threshold validation.
The preset does not replace receiver validation, pitot zero/ratio calibration,
compass orientation and calibration, or a staged ground test.

## Exposed Tune Parameters

The default column below is the **H743 DroneCAN production fixed-wing profile**,
tuned for an aircraft cruising near 120 km/h (33.3 m/s) with validated maximum
ground speed no higher than 65 m/s (234 km/h). F401 firmware keeps its
current compiled defaults for the four profile-specific values:
`RJ_LOIT_V=0.8`, `SP_JMP_MPS=500`, `SP_ABS_M=1000`, and `EKF_TRIPMS=500`.
Starting with F401
v1.6.26 and H743 v0.5.5, the obsolete `RJ_REQEKF` and `EKF_OKRJMS` schema slots
both report `0` and ignore writes. The H743 DroneCAN build also locks its unused
raw FC GPS UART off (`FCGPS_UART=0`); F401 keeps that UART enabled by default.
Do not copy the H743 jump limits to another airframe until
you have checked its maximum (not only cruise) speed and real GNSS logs.

Saved operator-tuned parameters normally take precedence over compiled
defaults. On the first profile upgrade, H743 migrates only values that still
exactly equal the legacy migration sentinels (`0.8/500/1000/0`) to the new profile;
non-default operator values survive unchanged. Read the four rows back after
updating. If you intentionally want to replace custom values, load the H743
field preset or perform a factory-parameter reset while the FC is freshly and
positively disarmed.

| Param | Meaning | H743 default | Min | Max |
|---|---|---:|---:|---:|
| `RJ_BASE_M` | Base rejoin lateral gate (meters) | 120 | 10 | 10000 |
| `RJ_SPD_MULT` | Speed multiplier term for gate | 8 | 0 | 100 |
| `RJ_EXP_RMPS` | Gate expansion rate while in DR1 (m/s) | 30 | 30 | 200 |
| `RJ_EXP_MAXM` | Max expansion cap (m) | 1000000 | 800000 | 1000000 |
| `RJ_DOP2M` | HDOP to meters scaling | 20 | 0 | 200 |
| `RJ_HDOP_MUL` | HDOP multiplier | 2 | 0 | 20 |
| `RJ_MIN_SATS` | Rejoin minimum satellites | 8 | 4 | 30 |
| `RJ_MAX_HD` | Rejoin max HDOP | 2.5 | 0.5 | 10 |
| `RJ_LOIT_V` | Low-speed loiter threshold (m/s, 0=disabled) | 0 | 0 | 10 |
| `RJ_LOIT_MS` | Loiter hold time before wider gate (ms) | 8000 | 500 | 120000 |
| `RJ_LOIT_GM` | Loiter gate floor after hold (m) | 2500 | 10 | 1000000 |
| `RJ_STAB_MS` | Stable window before rejoin/blend (ms) | 5000 | 500 | 120000 |
| `BLEND_MS` | Blend duration DR1 to DR0 (ms) | 10000 | 1000 | 120000 |
| `DR_LOCK_MS` | Minimum DR1 lockout window (ms) | 120000 | 1000 | 600000 |
| `DR1_MAXMS` | Maximum DR1 latch duration before forced exit after `DR_LOCK_MS` (ms, 0=disabled) | 0 | 0 | 3600000 |
| `SP_JMP_MPS` | Maximum implied travel speed between fixes (m/s) | 200 | 50 | 20000 |
| `SP_ABS_M` | Spoof guard absolute step limit (m) | 400 | 100 | 50000 |
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
| `ALT_BSEP_M` | Inactive absolute alt-vs-baro compatibility threshold (m) | 100 | 10 | 500 |
| `ALT_BSEPMS` | Inactive absolute alt-vs-baro compatibility hold (ms) | 1500 | 100 | 20000 |
| `ALT_RJSEP` | Inactive absolute alt-vs-baro rejoin compatibility limit (m) | 50 | 5 | 500 |
| `RJ_REQEKF` | Retired compatibility slot (no runtime effect) | 0 | 0 | 0 |
| `NUDGE_EN` | Enable DR1 nudge toward GNSS (0/1) | 1 | 0 | 1 |
| `NUDGE_MPS` | DR1 nudge speed (m/s) | 8 | 0 | 50 |
| `NUDGE_FRAC` | DR1 max nudge fraction per step | 0.5 | 0 | 1 |
| `EKF_TRIPMS` | Generic EKF horizontal-loss duration to DR1 (ms) | 500 | 0 | 10000 |
| `EKF_OKRJMS` | Retired compatibility slot (no runtime effect) | 0 | 0 | 0 |
| `EKF_GRCMS` | EKF grace after DR1 exit (ms) | 60000 | 20000 | 60000 |
| `BOOT_NSATS` | Boot north gate minimum satellites | 6 | 4 | 30 |
| `BOOT_NHDOP` | Boot north gate max HDOP | 4 | 0.5 | 10 |
| `BOOT_NSTAB` | Boot north gate stable window (ms) | 1000 | 200 | 20000 |
| `BOOT_DLYMS` | Startup DR trigger guard delay (ms) | 20000 | 2000 | 120000 |
| `GN_HOTMS` | GNSS hotstart watchdog trigger (ms) | 15000 | 1000 | 120000 |
| `GN_COLDMS` | GNSS coldstart watchdog trigger (ms) | 45000 | 2000 | 300000 |
| `PT_ONLY` | Pass-through-only mode (0/1) | 1 | 0 | 1 |
| `FCGPS_UART` | FC GPS UART: 1=enabled, 0=released (locked to 0 on H743 DroneCAN) | 0 | 0 | 1 |
| `FCGPS_FWD` | Force FC GPS UART on and raw-forward GPS, bypassing DR1, boot north gate, and hemisphere fence (bench only, 0/1) | 0 | 0 | 1 |
| `LOG_MS` | Filter status log period (ms) | 10000 | 1000 | 120000 |
| `NAV_AGEMS` | Max NAV age for valid/present GPS (ms) | 5000 | 200 | 60000 |
| `NAV_STALLMS` | NAV stall warning threshold (ms) | 7000 | 500 | 120000 |
| `UBX_BAUD` | u-blox baud control: 0=autoconfig ON, >0=manual baud (reboot to apply) | 0 | 0 | 2000000 |
| `UBX_RESET` | One-shot u-blox recovery command: 0=idle, 1=hot, 2=cold, 3=clear saved config | 0 | 0 | 3 |
| `GNSS_TYPE` | Receiver mode: 0=u-blox/UBX, 1=UM980/UM981/UM982 NMEA, 2=Septentrio Mosaic X5 (H743 DroneCAN SBF/NMEA, UART NMEA; reboot to apply) | 0 | 0 | 2 |
| `UM980_HIGHDYN` | Reserved UM980/UM981/UM982 dynamics selector (currently no runtime effect) | 0 | 0 | 1 |
| `SNR_EN` | Enable SNR-spread spoof guard (0/1) | 1 | 0 | 1 |
| `SNR_MSATS` | SNR guard minimum satellites | 8 | 4 | 30 |
| `SNR_DMAX` | Largest SNR spread still treated as suspicious (max-min, dB-Hz) | 6 | 1 | 40 |
| `SNR_MMAX` | Minimum required strongest SNR (dB-Hz) | 35 | 10 | 60 |
| `SNR_HOLDMS` | SNR guard hold time before DR1 (ms) | 1500 | 100 | 20000 |
| `SNR_MAXAGE` | Max age of SNR sample (ms) | 2000 | 100 | 10000 |
| `FENCE_RAD` | Geo-fence radius from first fix (m, 0=disabled) | 0 | 0 | 2000000 |
| `HEMI_EN` | Northern hemisphere hard fence (locked on) | 1 | 1 | 1 |
| `LOG_LOC` | Include coordinates in periodic DR0 status text only (0/1) | 0 | 0 | 1 |
| `CONF_TRIP` | Weighted spoof-confidence score that latches DR1 | 70 | 30 | 100 |
| `PROP_DIA` | Propeller diameter (in) | 27 | 6 | 40 |
| `PROP_PITCH` | Propeller pitch (in) | 12 | 2 | 30 |
| `FUEL_BSFC` | Engine brake specific fuel consumption (g/kWh) | 700 | 200 | 1500 |
| `FUEL_IDLE` | Idle fuel flow (g/h) | 250 | 0 | 3000 |
| `ENG_PMAXKW` | Rated shaft power (kW) | 8.6 | 0.2 | 60 |
| `FUEL_TRIM` | Fuel estimate calibration multiplier | 1 | 0.2 | 5 |
| `FUEL_CAPG` | Fuel loaded, by weight (g) — not the usable figure | 0 | 0 | 200000 |
| `FUEL_DENS` | Fuel density (g/ml) | 0.75 | 0.5 | 1.2 |

## Parameter Reference (detailed)

### Rejoin gate and timing

- **RJ_BASE_M**: Base lateral gate used when evaluating rejoin. It is the starting allowed distance between the synthetic position and the real GNSS position. Increase if long DR1 periods cause large drift; decrease to reduce the chance of accepting spoofed jumps.
- **RJ_SPD_MULT**: Speed multiplier term added to the rejoin gate. It increases tolerance at higher air/ground speeds. Too high can allow large jumps at speed; too low can prevent rejoin when moving fast.
- **RJ_EXP_RMPS**: Expansion rate of the rejoin gate while in DR1 (meters per
  second). It lets the allowed gate grow over time. Higher values rejoin sooner
  after long DR1 periods but reduce protection against large offsets. Firmware
  enforces a 30 m/s minimum on live writes and on legacy persisted values.

  The safety floor must cover the strongest wind the aircraft flies in. While
  DR1 is latched the filter dead-reckons from airspeed and heading, which is
  the only velocity a spoofer cannot influence - but it is air-relative, so the
  reference drifts away from the true position at the wind speed. If the gate
  opens slower than that drift it closes permanently and the aircraft cannot
  rejoin for the rest of the flight, even with a perfectly healthy receiver.
  The enforced value of 30 covers the shipped fixed-wing profile's flyable
  envelope. Profiles for aircraft that can operate above 30 m/s wind must raise
  this value; the firmware never permits lowering it below 30.
- **RJ_EXP_MAXM**: Maximum cap on the expansion term. This **does not limit flight
  distance**; it only caps how large the rejoin gate can grow. If too low, rejoin
  may never happen after long DR1; if too high, very large offsets can be accepted.
  The rate, not this cap, is the real invariant: 30 m/s exceeds any wind the
  airframe can fly against, so while the gate is still expanding it outruns the
  drift and cannot close. This cap is what ends that. At the former default of
  200000 the gate froze after 1 h 51 m while drift kept growing at wind speed, so
  a 350 km GNSS-denied leg became **permanently** unrecoverable above roughly
  9-12 m/s of wind - `DR1_MAXMS` is 0, so nothing times out. The default is now
  1000000, which is not reached until 9 h 15 m of continuous DR1 and is therefore
  a sanity backstop rather than an operating limit. The minimum is floored at
  200000 in the setter: tuning it down re-creates the in-air latch.
- **RJ_DOP2M**: Converts HDOP into meters for the rejoin gate. Higher values make the gate larger when HDOP is high. Lower values make rejoin stricter under poor geometry.
- **RJ_HDOP_MUL**: Additional multiplier on the HDOP term. Use this to scale overall DOP influence without changing the base conversion.
- **RJ_MIN_SATS**: Minimum satellites required for rejoin. Raise to demand a stronger fix; lower to rejoin sooner in weak sky conditions.
- **RJ_MAX_HD**: Maximum HDOP allowed for rejoin. Lower values require better geometry; higher values allow rejoin under noisier GNSS.
- **RJ_LOIT_V**: Loiter speed threshold. If GNSS quality is loose and speed stays below a non-zero threshold, the low-speed timer can arm the loiter gate floor. `0` disables this path, which is the H743 fixed-wing production default; it prevents a stationary/near-stationary fix from receiving a special 2500 m rejoin allowance.
- **RJ_LOIT_MS**: How long the vehicle must remain below the enabled loiter speed before the loiter gate floor applies. It has no effect while `RJ_LOIT_V=0`.
- **RJ_LOIT_GM**: Minimum gate used after the low-speed hold. The firmware applies `max(dynamic_gate, RJ_LOIT_GM)`; it never replaces or shrinks a larger dynamic gate. Increase only when a validated low-speed mission needs a wider recovery gate.
- **RJ_STAB_MS**: Required stability window before rejoin/blend starts. Longer values improve safety but delay rejoin.
- **BLEND_MS**: Duration of the DR1 to DR0 blend. Longer blends smooth transitions; shorter blends rejoin faster.
- **DR_LOCK_MS**: Minimum lockout time after entering DR1. During this time the rejoin stability timer, GNSS blend, and DR0 exit are blocked even if GNSS looks good. It also takes precedence over `DR1_MAXMS`, so DR1 cannot be force-exited before this lock window expires. Short values are useful for bench testing; after bench validation, set `DR_LOCK_MS=120000` or higher for real flights unless you intentionally need faster recovery. This keeps DR1 active for at least 2 minutes after any trigger and avoids rapid DR0/DR1 flip-flopping.
- **DR1_MAXMS**: Hard upper bound on how long the filter is allowed to stay latched in DR1 after the `DR_LOCK_MS` minimum has elapsed. When non-zero, DR1 is forcibly exited after this many milliseconds regardless of spoof confidence, but not before the lock window. Default `0` = disabled (infinite latch — the filter stays in DR1 until rejoin gates clear normally). Use a non-zero value only if your mission profile prefers "possibly-wrong GPS" over "inertial-only forever" — e.g. a long-range flight where losing GPS for the entire remaining leg is worse than accepting a partially-recovered spoofed signal. Most users should leave this at `0`.

### Spoof guard (position jump)

- **SP_JMP_MPS**: Maximum implied position-travel speed between consecutive fresh fixes. It is not a delta in the receiver's reported speed. If `distance / elapsed_time` exceeds this value, DR1 triggers once armed. The H743 fixed-wing default of 200 m/s is six times a 120 km/h cruise speed; validate against the aircraft's full speed envelope and logs before lowering it.
- **SP_ABS_M**: Absolute distance limit between consecutive fresh fixes. The guard uses an **OR**: exceeding either `SP_ABS_M` or `SP_JMP_MPS * elapsed_time` triggers DR1. The H743 default of 400 m still covers about 167 m of legitimate travel at 120 km/h across the full default 5 s NAV-validity window while rejecting a larger recovered-fix teleport.

### Guard arming (when spoof checks start)

- **ARM_MIN_S**: Minimum satellites before spoof guard arms. Prevents false triggers at boot. Increase for safer arming; decrease if you need early protection.
- **ARM_MAX_HD**: Maximum HDOP allowed for arming. Lower means higher quality required.
- **ARM_STABMS**: Time GNSS quality must remain good before the guard arms. Longer is safer; shorter arms faster.

### Altitude guards

- **ALT_BSATS**, **ALT_BHDOP**, **ALT_CALM_V**, **ALT_BCMS**: Retained
  calibration settings for the disabled absolute altitude-vs-baro path; they
  do not arm a live guard in released builds.
- **ALT_JMP_M**: Absolute altitude jump threshold. Large single-step changes beyond this trigger DR1.
- **ALT_RMPS**: Altitude rate threshold (m/s). Sustained rate above this can trigger DR1 when combined with other rate settings.
- **ALT_RDTMS**: Minimum time window used for altitude rate detection.
- **ALT_RDH_M**: Minimum altitude delta required inside the rate window. Prevents false triggers from noise.
- **ALT_BSEP_M**, **ALT_BSEPMS**, **ALT_RJSEP**: Inactive compatibility
  settings. `ALT_BARO_GUARD_ENABLE` remains false because the absolute
  pressure-altitude comparison is not flight-qualified. They neither trip DR1
  nor gate rejoin. DroneCAN's separate barometric **vertical-rate** detector
  remains live and is not configured by these rows.

### DR behavior

H743 DroneCAN `v0.1.4+` exposes these guard/tune parameters through Mission
Planner `DroneCAN/UAVCAN -> node 42 -> Params`, and `v0.1.5+` also exposes them
through the H743 USB-C COM port at `115200`. In `v0.2.0+`, S2/index `1` adds a
CAN-backed filter MAVLink2/FC-telemetry path, so MAVLink parameter requests and
telemetry-dependent EKF/barometer logic work through the FC. There is still no
physical FC MAVLink UART or FC GPS raw-UART bypass. DR1 suppresses only native
DroneCAN `Fix2/Auxiliary`; the camera and filter MAVLink virtual ports remain
active.

- **PT_ONLY**: Pass-through output mode. The FC receives live GNSS in DR0 and no GNSS in DR1. The filter still maintains an internal DR reference and applies lateral, altitude, quality, stability, spoof-confidence, and available independent-evidence checks. Only synthetic GNSS output, output blending (`BLEND_MS`), and nudge behavior (`NUDGE_*`) are inactive while `PT_ONLY=1`.
- **FCGPS_UART**: H743 DroneCAN has no physical FC GPS UART and locks this row to `0`; GPS reaches the FC as native DroneCAN. On F401 or H743 UART builds it controls the FC GPS UART (`A11/A12` or `C6/C7`): `1` enables forwarding and `0` releases the pins. Do not set it to `0` in flight on those UART builds.
- **FCGPS_FWD**: H743 DroneCAN locks this diagnostic raw-UART bypass to `0`. On UART builds, setting `1` forces the FC GPS UART on and raw-forwards GNSS, bypassing the DR1 latch, boot north gate, and `HEMI_EN` hard north fence. Use it only on the bench. In normal protected mode on u-blox firmware v1.6.18+, FC GPS back-channel bytes are drained and are not forwarded into the receiver.

### EKF gates

- **RJ_REQEKF**: Retired compatibility slot, locked to `0` in F401 v1.6.26+ and H743 v0.5.5+. The former rejoin gate was unsatisfiable because the FC EKF depended on the GPS being withheld in DR1, and it was circular as an independent security witness. It remains in the schema only so old journals and parameter tooling keep stable indices. Older firmware may still show a stored non-zero value; upgrading ignores it and reports `0`.
- **EKF_TRIPMS**: Minimum interval covered by bad EKF evidence before DR1. Every bad category, including `GPS_GLITCHING` and `UNINITIALIZED` after the FC session has first reported healthy, requires at least 2 newly decoded `EKF_STATUS_REPORT` messages spanning the full interval. Both released targets default to 500 ms. A tuned value of `0` removes the time requirement but still keeps the two-report minimum. Startup `UNINITIALIZED` is exempt only until the first healthy report in that FC session.
- **EKF_OKRJMS**: Retired compatibility slot, locked to `0` in F401 v1.6.26+ and H743 v0.5.5+; it has no runtime effect. Older stored values are ignored after upgrade.
- **EKF_GRCMS**: Grace period after exiting DR1 during which EKF issues are ignored.
  This must EXCEED the time the flight controller needs to regain absolute
  horizontal position after GPS is restored, or recovery deadlocks: the
  estimator needs sustained GPS to leave constant-position mode, and if the
  filter re-trips before that completes it withholds GPS again and the
  estimator can never converge. Measured 2026-08-10 on an H743 + ArduPlane:
  10.6 s from GPS available to `POSH_ABS` present, in the easy cold-start case
  with no dead-reckoning error to reconcile. The default of 30000 is three
  times that, with margin for the larger correction after a long DR1. Do not
  reduce it toward the convergence time.

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
- **CONF_TRIP**: Threshold on the weighted spoof-confidence score (0-100) that latches DR1. This score is **not** the primary detector, and the default is not a compromise between sensitivity and false alarms. The score divides by the weight of the indicators that are *available*, so an indicator that is present and reads clean is a pure divisor. An attacker who keeps his broadcast internally self-consistent reads clean on every indicator except the receiver's own UBX-SEC-SIG verdict and the barometric-vs-GNSS climb-rate divergence - the two he can neither observe nor shape - which caps the score at 31. That is why those two trip **standalone**, independently of this threshold, and why no setting of `CONF_TRIP` catches a competent attacker. What this threshold governs is the naive and mid-effort attacker, who does leave dirty signal statistics. Lower it only with flight evidence: below about 35 it approaches the range a clean flight can reach on its own.
- **LOG_LOC**: At `1`, coordinates may appear only in filter-generated
  periodic status while the output is fully in DR0 (not latched, synthetic, or
  blending). Trip/transition text and every message sent while DR1 is active
  remain coordinate-redacted. Default `0` also redacts DR0 periodic status.
  The direct-USB-only `SP_*` overlay diagnostics remain on the private USB
  connection and never enter the FC/CAN status path. `LOG_LOC` does not alter
  GNSS forwarded to the FC, DroneCAN `Fix2`, or the FC's own flight/dataflash
  logs.
- In Mission Planner `Messages`, the default user-visible behavior is roughly one periodic log pair every **10 seconds**.
- **NAV_AGEMS**: Maximum age to consider GNSS position/altitude data valid. If updates get older than this, the filter treats the fix as stale for rejoin, forwarding, and receiver recovery logic.
- **NAV_STALLMS**: NAV stall warning threshold. If exceeded, a warning is logged.
- **UBX_BAUD**: u-blox baud/autoconfig control. `0` keeps autoconfig enabled (default behavior) for direct single-receiver u-blox modules. In firmware v1.6.22+ that autoconfig boot path clears/loads receiver defaults, rescans baud, then writes and saves the filter's UBX profile. Any value `>0` disables the full autoconfig path and uses this manual baud directly. Applied after reboot. In manual mode the filter still makes a best-effort request for `NAV-SAT` so SNR can work, but if the receiver ignores that request, `SNR=NA` is still expected. Gateway modules with an intermediary MCU - including dual-F9P products such as Quadro GPS and UNA3 / UNA4-SFE - must use manual baud (`UBX_BAUD` set explicitly); filter autobaud is not possible for that class of device.
- **UBX_RESET**: One-shot u-blox recovery command available in firmware v1.6.15+. It is a virtual parameter: the value always reports back as `0` and is not stored in the tuning blob. Set `1` for hot start, `2` for cold start, or `3` to clear saved receiver BBR/Flash configuration, reload defaults, reset the receiver, and let the STM32 reinitialize GNSS. Use `3` only on the bench or during recovery, because it deletes the receiver's saved u-blox configuration; do not make it a normal default setting.
- **SNR=NA with SNR_EN=1**: If `SNR_EN=1` and `SNR=NA` persists beyond 30 seconds after boot, the filter logs `WARNING: SNR_EN=1 but SNR=NA/stale (no fresh GSV/NAV-SAT?)`. This means the receiver is not providing fresh SNR data. The SNR guard will not trip in this state. With u-blox, fix the NAV-SAT stream or set `SNR_EN=0`. With the documented UM980 GGA/RMC/AGRICA profile, `SNR=NA` is expected because GSV is deliberately omitted; optional GSV can add SNR evidence, but it is not required for DR1 recovery. On u-blox firmware v1.6.12+, a `snrdbg` line decodes the NAV-SAT stream: `n` frames seen, `a` frame age, `l` last length, `s` reported satellites, `g` usable C/N0 satellites, `o` oversize drops, `b` malformed/checksum drops.
- **u-blox NAV-SAT recovery**: v1.6.15+ re-enables NAV-SAT using legacy `CFG-MSG` plus `CFG-VALSET` on UART1/UART2 only when NAV-SAT frames are missing or stale. If `snrdbg` shows fresh NAV-SAT with `g0`, the receiver is alive but currently has no usable C/N0, so the firmware does not keep rewriting configuration. v1.6.16+ starts the recovery timer as soon as SNR goes stale, so intermittent NAV-SAT loss typically recovers after about one stale window instead of two. v1.6.18+ also prevents the normal FC GPS back-channel from changing the u-blox receiver profile, which avoids ArduPilot auto-config writes followed by stale NAV-SAT. v1.6.21+ uses a faster first re-enable, about 8 seconds, when a healthy fix already exists and NAV-SAT disappears; startup and no-fix cases keep the slower 30-second path.
- **u-blox no-fix diagnostics and assist**: v1.6.15+ polls `UBX-MON-RF`, `UBX-SEC-SIG`, and `UBX-CFG-GNSS` while a u-blox receiver has no valid position fix or `SATS=0`. Mission Planner then shows `ubxpvt ...` for NAV-PVT fix flags, `ubxrf ...` for antenna/RF state, `ubxsig ...` for explicit jamming/spoofing state when supported, and `ubxgnss ...` for enabled GNSS constellation blocks. `ubxgnss en00` points to disabled constellations; high `ubxrf c` or `n`, abnormal antenna status, or `ubxsig j2`/`j3` point to RF/antenna/interference problems. v1.6.19+ also sends an automatic u-blox cold start plus STM32 reinit after about 2 minutes at `SATS=0`. v1.6.22+ direct autoconfig also starts from receiver defaults at boot; use `UBX_BAUD>0` to preserve custom/gateway receiver profiles.
- **GNSS_TYPE**: Receiver mode selector. `0` = u-blox/UBX, `1` = UM980/UM981/UM982 NMEA, `2` = Septentrio Mosaic X5. Change is saved immediately but applied after STM32 reboot. H743 DroneCAN firmware `v0.1.9+` accepts Mosaic SBF or NMEA and publishes GPS over DroneCAN; UART/F401 deployments should keep using the Mosaic NMEA profile. The STM32 does not send Septentrio reset or auto-configuration commands.
- **UM980_HIGHDYN**: UM980/UM981/UM982 rover dynamics mode. `0` = `MODE ROVER UAV` (standard, default). `1` = `MODE ROVER UAV HIGHDYN` (use for aggressive airframes with rapid attitude changes). Reserved for future use — currently has no runtime effect. The STM32 does **not** send any `MODE` command to the UM980.

### Geo-fence

- **DR1_MAXMS**: See the full description above under *Rejoin gate and timing* — this is the hard upper bound on time spent in DR1 before a forced exit, after the `DR_LOCK_MS` minimum has elapsed.
- **FENCE_RAD**: Geo-fence radius in meters from the first-fix position (max 2,000,000 m = 2000 km). **Default `0` (disabled)** — the fence is opt-in. If GPS reports a position outside this radius, DR1 triggers. Catches spoofing attacks that slowly drift position over time. Note: the fence center is set at first fix after boot — not at an arming position, so enable it only for missions where the first fix is close to the mission area. Typical values once enabled: `50000` (50 km) for local flights, `600000` (600 km) for long-range.

### Hemisphere fence

- **HEMI_EN**: Compatibility parameter for the northern hemisphere hard fence. It is locked to `1`: the normal forwarding path waits for a stable northern fix before publishing FC GPS and rejects south/equator fixes in the parser. Runtime or stored attempts to set `0` are clamped back to `1`. `FCGPS_FWD=1` is the only diagnostic raw-forwarding bypass and must not be used in flight.

### SNR guard (nearby jammer/spoofer)

- **SNR_EN**: Enables the SNR-spread guard and defaults to `1`. Tight SNR spread can trigger DR1 only when the receiver provides fresh NAV-SAT/GSV data. `SNR=NA` or stale data cannot trigger this guard, so verify a live SNR stream before relying on it.
- **SNR_MSATS**: Minimum satellites required for the SNR guard to evaluate.
- **SNR_DMAX**: Largest `max(C/N0)-min(C/N0)` spread still classified as suspicious. The SNR guard is a *narrow-spread* detector: it can trip when `spread <= SNR_DMAX` and the satellite-count, strongest-signal, freshness, and hold-time checks also pass. Raising this value is more sensitive/stricter; lowering it accepts more samples and detects only unusually uniform signal sets.
- **SNR_MMAX**: Minimum required strongest SNR. Prevents triggering on low-signal noise.
- **SNR_HOLDMS**: Time the SNR condition must persist before DR1 triggers.
- **SNR_MAXAGE**: Maximum age of the SNR sample. Old samples are ignored.

## Persistence

- Parameter reads are always available. A change is accepted only while the
  filter has a fresh, positive **FC disarmed** report; unknown, stale, or armed
  state is fail-closed. `UBX_RESET`, explicit save, and factory reset use the
  same gate. On DroneCAN, mutation requests must also come from the configured
  or currently bound FC node.
- Accepted changes are applied immediately and then scheduled for persistence.
- One global 60-second wear limit covers every non-volatile write attempt. The
  first accepted change normally saves after the short debounce; later changes
  remain active and dirty until the cooldown expires. Power loss while a save
  is pending can lose the latest change, but cannot replace the last committed
  configuration with a torn transaction.
- H743 uses a power-loss-safe A/B flash journal. Within a supported record
  schema, stable name keys let older firmware apply the parameters it
  understands when extra unknown keys are present, without automatically
  rewriting and destroying those settings. An unsupported future schema is
  rejected, and an intentional parameter save from older firmware can replace
  the record with its own key set. F401 uses an append-only, transactional delta journal in the fixed
  8 KiB tail of flash: it never erases that sector at runtime, ignores
  interrupted transactions, and safely refuses a save when no complete
  transaction fits. Both formats migrate the released `BTN1`/`BTK2` records.
- F401 has only one spare 128 KiB erase sector, shared by the staged-image area
  and parameter tail, so true A/B erase recovery is impossible without changing
  the signed app/staging layout. A clean journal has 640 entry slots; the
  current initial snapshot uses 64 and a typical one-parameter save uses three,
  allowing roughly 192 such delta saves. Older retained log bytes reduce that
  number. When full, the board reports `Tune save failed` and keeps the last
  committed configuration; a controlled service reflash/sector erase is
  required before another value can persist. Erasing or restaging sector 5
  also erases the saved F401 configuration, so record/reapply the desired tune.
- `UBX_RESET` is a command, not a stored setting; it returns to `0` after every write.
- `GNSS_TYPE` and `UBX_BAUD` require reboot to apply.
- After the final write, allow up to **65 seconds** if another save was attempted
  during the preceding minute. A refresh confirms the live value; a controlled
  reboot after that window confirms persistence.
- Reboot after every parameter change is **not** required.
- Reboot STM32 (`NRST` or power cycle) when changing `GNSS_TYPE` or `UBX_BAUD`, or if behavior does not match updated values.

## Using Mission Planner for Parameter Writes

Use Mission Planner to read and write all STM32 filter params:

1. Open `Config/Tuning` -> `Full Parameter List`.
2. Select the STM32 filter target (**SYSID 42**) in the system dropdown.
3. Click **Refresh Params**.
4. Confirm the FC is connected and disarmed, then edit one or more values.
5. Click **Write Params**.
6. Click **Refresh Params** again to verify saved values.

Notes:

- If a value does not update, first confirm a fresh disarmed FC state and the
  correct target/node. Repeated writes do not bypass the safety gate.
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

- `SP_ABS_M=400`
- `SP_JMP_MPS=200`

Will trigger DR1:

- One fix jumps 500 m in ~1 s (`500 m > 400 m` and `500 m/s > 200 m/s`).

Will not trigger DR1:

- 50 m movement in 1 s.
- About 167 m of normal travel over a 5 s GNSS gap at 120 km/h.

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

### Absolute altitude vs baro path (disabled)

Settings:

- `ALT_BSEP_M=100`
- `ALT_BSEPMS=1500`

These stored compatibility settings do not trigger DR1 or gate rejoin in the
released firmware because `ALT_BARO_GUARD_ENABLE=false`. Do not use this as a
validation scenario. On DroneCAN, validate the separate live barometric
vertical-rate detector instead.

### EKF trigger

Settings (example override, not the H743 production default):

- `EKF_TRIPMS=1500`

Will trigger DR1:

- At least 2 newly decoded EKF reports show the same bad evidence, including
  `GPS_GLITCHING` or post-healthy `UNINITIALIZED`, and the first-to-latest
  report span reaches 1.5 s.

Will not trigger DR1:

- A single bad report, or a bad sequence whose distinct reports do not span
  the configured `EKF_TRIPMS` interval.

## Calibrating the fuel estimate

The filter estimates fuel burn from engine RPM. The propeller is the engine's
load, so its absorbed power is what the engine must produce, and fuel follows
from that:

```
P    = Cp0 x shape(J) x rho x n^3 x D^5   n = rev/s, D = diameter, J = V/(nD)
fuel = BSFC x P + idle flow
```

**Uncalibrated this OVER-reports, typically by 1.5-2x. Calibrated, +/-10-20%.**
Calibration is one flight and one weighing, and until you have done it the
number is advisory only - but it errs on the side of telling you that you have
less fuel than you do.

### What `shape(J)` is, and what it is not

It is **not** a propeller power curve. Absorbed power is greatest with the
aircraft stationary, so the static figure is already the worst case, and the
only thing airspeed can do to this estimate is take fuel off it - on the word
of a single pitot tube, on an aircraft where this is the only fuel indication.

So airspeed is allowed a **bounded discount of at most 15%**, and no more. A
blocked static port, an iced pitot, or an airspeed that is simply wrong cannot
drive the estimate down more than that. An earlier version let airspeed reduce
the figure without limit and a 27% high reading took the reported burn from
2332 g/h to the bare idle flow, at full throttle, silently. That is fixed and
it will not be reintroduced.

The cost is a deliberate over-report at genuine high-speed cruise. That is the
trade, and `FUEL_TRIM` is where you buy it back.

### Why there is exactly one knob

Only the PRODUCT of the propeller's power coefficient and the engine's BSFC is
observable in flight. Nothing in a log separates "the propeller absorbs more
than we thought" from "the engine is thirstier than we thought" - that needs a
dyno. So `FUEL_BSFC` and the propeller geometry stay at their book values, and
`FUEL_TRIM` absorbs the difference.

### Procedure

1. Set `PROP_DIA`, `PROP_PITCH`, `ENG_PMAXKW`, `FUEL_BSFC`, `FUEL_IDLE`, and
   `FUEL_DENS` from your engine, propeller, and fuel, or load an engine preset.
   Set density **before** capacity: an actual `FUEL_DENS` change requires fresh
   stopped-engine quorum, marks the total LOST before applying the new value,
   cancels any older pending capacity commit, and cannot resume EFI by itself.
   Wait for the verified density save to report `Tune saved`; until then every
   capacity write is rejected with `FUEL_CAPG blocked: wait for FUEL_DENS save`,
   and a failed save remains blocked and LOST. After save success, write
   `FUEL_CAPG` under the same fresh quorum to establish the fresh zero.
2. Fill the tank and **weigh the fuel you put in**. Set `FUEL_CAPG` to that
   figure in grams. Weight, not volume - the model integrates mass, and
   volume drifts with temperature.

   **Writing `FUEL_CAPG` also zeroes the running total.** It is the only thing
   that does. The total now survives resets (see below), so telling the filter
   the tank size is how you tell it the tank is full again - write it after
   every refuel, even if the number has not changed. You must also rewrite it
   after an ordinary power-on that reports TOTAL LOST because no valid retained
   record exists, again even when the numerical value is unchanged. Before the
   write, wait until the FC's stopped-engine quorum is all fresh: positively
   disarmed, valid zero RPM, and closed throttle. A disarmed report alone is
   insufficient; a rejected write reports `FUEL_CAPG blocked: engine not confirmed stopped`.
   You will see `FUEL_CAPG written - fuel total zeroed` only after the write is
   accepted. If the numerical capacity changed, that message confirms the
   runtime reset only: the fuel total deliberately remains TOTAL LOST and EFI
   stays silent until the asynchronous tune-journal write succeeds and reports
   `Tune saved`. If it reports `Tune save failed`, do not fly on the gauge; the
   total remains lost while persistence retries. A same-value write does not
   need a new capacity snapshot and can re-establish the current-session total
   immediately.
3. Fly a representative sortie. Not a hover, not a full-throttle climb: the
   mix of cruise and manoeuvre you actually fly, for long enough to burn a
   decent fraction of the tank.
4. **Weigh the fuel remaining.** Actual burn = loaded minus remaining.
5. Read the reported consumption from the flight controller's EFI fuel total,
   or from the log.
6. Set `FUEL_TRIM` = actual burn / reported burn, multiplied by whatever
   `FUEL_TRIM` was during the flight. Write it, and confirm it read back
   (tunables are flash-backed; a changed value does nothing until it is on the
   board).
7. Repeat once. If the second flight lands within about 10%, you are done.

> **Expect a trim below 1.** The model starts from `Cp0 = 0.030 + 0.050 x
> pitch/diameter`, which is 0.052 for a 27x12. Published static power
> coefficients for two-blade fixed-pitch propellers at that pitch ratio sit
> around 0.035-0.045, so the model carries roughly 1.2-1.5x margin
> deliberately: that is what pays for the 15% airspeed discount and keeps the
> estimate on the over-reporting side. A first flight therefore typically wants
> a trim around 0.5-0.9. That is the calibration working, not a fault.
>
> The over-report is largest at low power and shrinks towards full throttle,
> where the estimate meets `ENG_PMAXKW` and stops rising. One scalar cannot
> flatten that, which is why the guidance below is to trim at the power
> setting you actually cruise at.
>
> **`FUEL_TRIM` scales the failure paths too.** The rated-power charge used
> when the RPM sensor dies, and the throttle floor, are both multiplied by it.
> A trim of 0.5 halves the protection those provide. Trim to the point you
> actually cruise at, take the over-report everywhere else, and do not chase
> the last 10% by pushing the trim down further than one weighed burn
> justifies.
>
> **A trim above about 2 means something is wrong, not untrimmed.** Check
> `RPM_SCALING` against a hand tachometer, then `PROP_DIA` and `PROP_PITCH`,
> before believing the number. The parameter stops at 5.

### What the estimate does when things go wrong

Every failure the filter can **detect** is biased toward reporting more fuel
burned, because under-reporting is what stops an engine. Two things can still
make it under-report, and both are listed at the end of the table - read them.

| Situation | Behaviour |
|---|---|
| RPM sensor dies while the engine runs | Charges the engine's RATED power and announces `RPM sensor lost - fuel charged at max burn`. A large over-report, deliberately. |
| RPM reads zero with the throttle open | Treated as a failed sensor, not a stopped engine - a failed pickup reports a perfectly plausible zero. |
| RPM reads zero with the throttle shut | Believed. This is a stopped or idling engine, and billing rated power through every glide would be absurd. |
| No airspeed | Assumes static, which maximises absorbed power and therefore the burn. |
| Airspeed wrong, however wrong | Costs at most 15% off the estimate. It cannot collapse it. |
| Air density implausible **or stale** | Falls back to sea level, which is denser and burns more. A frozen static port no longer keeps feeding a density learned at altitude. |
| Throttle reading goes stale | Treated as unknown, so it can no longer hold the estimate down at idle. The propeller model carries it alone. |
| FC telemetry disappears or its firmware version is unknown/unsupported | Fuel accounting keeps running even while the GPS output gate is closed. Once fresh RPM/throttle evidence has shown that the engine may be running, link silence cannot clear that latch; missing RPM is charged at rated power. Only fresh disarmed state together with zero RPM and closed throttle clears it. |
| Main loop stalls past 10 s | The interval is charged at RATED power, not dropped, and announces `Main loop stalled - fuel charged at max burn`. Capped at 60 s per stall. |
| Every boot | Starts with the conservative engine-may-be-running latch set. Only fresh disarmed state together with fresh valid zero RPM and fresh closed throttle clears it. A `FUEL_CAPG` write is accepted only after that same stopped-engine quorum exists; the write itself is not evidence of a mechanical stop. |
| A trustworthy V2 record survives a reset | Restores the running total regardless of the reset-cause flag and reports `Fuel total kept: N g - re-set FUEL_CAPG if refuelled`. Before risky setup, the retained record is durably rewritten as TOTAL LOST. It becomes known again only after the fixed 25-second rated-power charge and the first measured interval have both been integrated and committed. The 25 seconds cover up to 2 s of backup-save staleness, the roughly 11.5 s longest UM980 setup path, other startup overhead, and margin; H743 has no Phase-C boot wait. This is a bounded conservative charge, not an exact consumption measurement. Because the integration clock starts during early backup initialization, any further setup elapsed time is charged too. If the operator establishes a new total first with an accepted `FUEL_CAPG` write, the pending charge associated with the old restored total is cancelled. |
| Another reset occurs before the restored total is committed known again | The durable write-ahead marker remains LOST (or an interrupted commit is invalid), so the next boot suppresses EFI until stopped-engine quorum permits a `FUEL_CAPG` write. It never reuses the stale known record while silently omitting another startup gap. |
| Any boot has no usable backup record, a corrupt backup record, or a legacy V1 backup record | The cumulative total is LOST. POR/PDR cannot prove a refuel or engine stop, so this applies to a normal power-on as well as a warm reset. The filter sends no DroneCAN ICE Status, so ArduPilot's EFI backend ages stale/unhealthy instead of accepting a false zero. It repeats `Fuel total LOST - write FUEL_CAPG to restart it` every 60 s and mutes the warning ladder. Land or remain on the ground, wait for fresh stopped-engine quorum (disarmed + valid zero RPM + closed throttle), and rewrite `FUEL_CAPG` even if its numerical value is unchanged. A same-value write can clear the current lockout immediately; a changed value resumes EFI only after `Tune saved`. Disarmed alone is rejected. |
| H743 tune journal is missing, corrupt, or has no valid record | Any surviving numeric fuel total is invalidated and EFI stays silent. The retained total was accumulated under capacity, density, and model settings whose provenance is now unknown; compiled defaults are not evidence that those settings match. Verify the complete fuel configuration and re-establish the loaded fuel with stopped-quorum `FUEL_CAPG`. |
| An accepted `FUEL_CAPG` write changes the numerical capacity | The running counter is zeroed and the old restore-gap charge is cancelled, but the total stays TOTAL LOST and no ICE Status is sent until the asynchronous tune-journal save succeeds. `FUEL_CAPG written - fuel total zeroed` confirms acceptance, not durability. Wait for `Tune saved`; `Tune save failed` leaves EFI silent and the dirty snapshot pending for retry. |
| An actual `FUEL_DENS` change | The same fresh stopped-engine quorum is required; otherwise the write reports `FUEL_DENS blocked: engine not confirmed stopped`. Before runtime density changes, the total is marked LOST and any older CAPG commit intent is cancelled so FC-visible cumulative volume cannot move backwards. Until the verified journal save succeeds, every `FUEL_CAPG` write is rejected with `FUEL_CAPG blocked: wait for FUEL_DENS save`; failure stays blocked/LOST. `Tune saved` clears only the pending-density latch, not the lost total. Then make a subsequent stopped-quorum `FUEL_CAPG` write to establish a fresh zero under the new density. |
| Factory reset is attempted | The firmware writes a durable TOTAL LOST marker before flash work can begin, because defaults can change capacity, density, or the model without proving a refuel. A failed start or interrupted reset may conservatively leave the total LOST too. After any attempt, verify every fuel-model setting and rewrite `FUEL_CAPG` with the engine stopped; after a changed value, wait for `Tune saved`. |
| Phase-C maintenance | **Never perform it while the engine is running.** The fixed 25-second charge covers bounded reset/startup work, not an arbitrarily long connected maintenance session. |
| Engine believed stopped, no RPM | Integrates nothing. There is no burn to account for. |
| `FUEL_CAPG` unset | Reports UNKNOWN, never OK. A healthy fuel state on an unconfigured aircraft is the worst possible default. |

**The two that can still under-report:**

| Situation | Behaviour |
|---|---|
| `RPM_SCALING` wrong on the flight controller | Halve the reported RPM and the propeller term drops eightfold. Nothing contradicts it - there is one RPM source, so there is nothing to disagree with. The open throttle puts a floor under the estimate that recovers roughly half the shortfall and announces `Fuel held up by throttle - check RPM_SCALING`. **If you see that message, check RPM_SCALING against a hand tachometer before you fly again.** |
| `FUEL_TRIM` set too low | Scales everything, including the failure paths above. A trim of 0.5 halves the rated-power charge too. Only ever lower it on the evidence of a weighed burn, and see the warning under Procedure. |

### Reserve and warnings

`FUEL_CAPG` is the fuel you loaded. **20% of it is withheld as a reserve
covering estimator error** - that error is a fraction of the whole tank by the
end of a flight, not of the remaining fuel. Warnings are struck against the
usable 80%, so the margin is not quietly spent before the first alert:

- `FUEL est NN% usable left` at 30% of usable, WARNING
- the same at 10% of usable, CRITICAL
- usable exhausted: only the error reserve remains

Warnings escalate and never step back down within a flight. Fuel does not come
back, and an alert that oscillates around a threshold teaches you to ignore it.

### Reading it on the flight controller

The filter publishes `uavcan.equipment.ice.reciprocating.Status` over DroneCAN
at 1 Hz. Set the flight controller's `EFI_TYPE` to its DroneCAN option and
ArduPilot will decode it into `EFI_STATUS`, giving a GCS fuel display and a
dataflash record with no side channel. Sensors this engine does not have -
oil pressure, coolant temperature and the rest - are reported as NaN rather
than zero, because zero is a measurement and a false one is alarming.

## Rejoin Examples

### Rejoin profile

- `RJ_MIN_SATS=8`
- `RJ_MAX_HD=2.5`
- `RJ_STAB_MS=5000`

Rejoin can start as soon as GNSS quality and geometry checks are stable for `RJ_STAB_MS`, then blend for `BLEND_MS`.

For a more conservative profile, increase the independent geometry/evidence
hold and lockout windows, for example:

- `RJ_STAB_MS=8000`
- `DR_LOCK_MS=120000`

`RJ_REQEKF` and `EKF_OKRJMS` cannot be used to strengthen this profile; both
are retired and locked to zero. Validate any changed profile in the lab before
flight.
