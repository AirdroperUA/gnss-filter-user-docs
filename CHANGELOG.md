# Changelog

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

All notable firmware and tool changes are documented here.

---

## H743 DroneCAN v0.5.30 — 2026-08-17 (corrective candidate)

- The filter now requests and verifies `AUTOPILOT_VERSION` before publishing
  GPS. An unknown version or ArduPilot older than 4.6.1 blocks GPS immediately;
  the 15-second delay applies only to the warning messages.
- Parked recovery works with named GNSS-time and fresh same-epoch receiver-speed
  evidence. Optional GSV/SNR is not required; any explicit contradiction still
  blocks release. Airborne recovery rules are unchanged.
- Location text is safer: even with `LOG_LOC=1`, coordinates appear only in
  periodic true-DR0 status, never trip/DR1/synthetic/blend messages.
- Fuel burn keeps counting through FC-link and FC-version blocks. Every boot
  starts by assuming the engine may be running until fresh disarmed, valid
  zero-RPM, and closed-throttle evidence all confirm a stop.
- After the first H743 `v0.5.30+` promotion, the update service permanently
  refuses to promote or deliver any pre-`v0.5.30` H743 firmware. Older fuel
  readers cannot safely preserve the new lost/known provenance, so even the
  generic owner-authorized rollback option cannot cross this global boundary.
- A missing, invalid, or legacy V1 backup record now means TOTAL LOST on every
  boot, including an ordinary power-on: POR/PDR cannot prove that you refuelled.
  A missing, corrupt, or otherwise invalid H743 tune journal also invalidates a
  surviving numeric total because its capacity, density, and model provenance
  is unknown.
  EFI packets stop until you land or remain on the ground, obtain fresh
  stopped-engine quorum (disarmed + valid zero RPM + closed throttle), and
  rewrite `FUEL_CAPG` even when its numerical value is unchanged. Disarmed alone
  is rejected. An accepted reset cancels a pending charge belonging to the old
  total. A valid V2 restore otherwise gets a bounded conservative 25-second
  rated-power reset-gap charge plus the first measured interval. Before risky
  setup, its retained known record is durably marked TOTAL_LOST and is committed
  known again only after both charges are integrated. If reset happens first,
  the next boot stays LOST until stopped-quorum `FUEL_CAPG`; it never reuses a
  stale known total. The 25 seconds cover backup staleness, longest UM980 setup,
  other startup overhead, and margin; H743 has no Phase-C boot wait. It is not
  an exact consumption measurement. Never perform Phase-C maintenance with the
  engine running.
- A changed `FUEL_CAPG` remains TOTAL LOST and EFI-silent until its asynchronous
  tune-journal save is verified. The accepted-write message is not proof of
  durability; a failed save stays LOST. Factory reset marks fuel LOST before
  flash starts, so even a failed reset attempt may conservatively require the
  stopped-engine `FUEL_CAPG` recovery.
- `FUEL_DENS` now requires the same fresh stopped-engine quorum. A real change
  marks fuel LOST, cancels an older CAPG commit, and rejects capacity writes with
  `FUEL_CAPG blocked: wait for FUEL_DENS save` until verified save success. The
  density save alone does not restore EFI: afterward, write `FUEL_CAPG` again
  under stopped-engine quorum to establish a fresh zero.
- Mission Planner's secondary H743 USB connection now works with its default
  DTR-low open/reconnect sequence, with independent USB and FC packet counters.
  The private spoof-position stream itself remains a v0.5.29+ feature.
- Mission Planner plugin `0.3.1` makes the map legend opaque and keeps it left
  of Mission Planner's native zoom controls, removing the white-line repaint
  flicker after resize or DPI changes.
- `PARKED_MOVE` is now shown as `PARKED MOVE` (or `PARKED` on the board screen),
  and the H743/UM980/build documentation and parameter descriptions were
  corrected. No firmware parameter values or defaults changed. The Mission
  Planner package adds an aircraft-specific 5 L FC preset that preserves BATT1,
  enables DroneCAN EFI on a verified-free BATT2, and exposes 4000 mL usable
  fuel with the final 1000 mL retained as estimator-error reserve. Automatic
  FC fuel failsafe actions remain off until aircraft HIL is complete.

v0.5.29 was uploaded only as an inactive candidate and was never promoted.
v0.5.30 has not yet been hardware/HIL-qualified or publicly promoted; v0.5.25
remains the public production release at the time of this entry.

---

## H743 DroneCAN v0.5.29 — 2026-08-17

Supersedes v0.5.28. Adds a live Mission Planner spoofing overlay.

### New: see where the receiver-reported solution is being pulled

The AirDroper Mission Planner package now installs a plugin with a status strip,
detailed telemetry window, and map overlay. During DR1 it shows:

- **red aircraft:** the receiver-reported, untrusted GNSS position and trail;
- **orange aircraft:** the filter's wind-blind dead-reckoning reference estimate;
- **green aircraft:** the flight controller's position estimate;
- distance/bearing lines, DR reason and confidence, freshness, and RF/jamming
  diagnostics.

These labels matter. Red is where the GNSS receiver says the aircraft is, not a
measurement of its real physical location. Orange can drift with wind or freeze
when speed/yaw telemetry is stale. Green is the FC estimate. None is guaranteed
ground truth, and the plugin hides stale map points.

Live red/orange points require a second USB-C cable directly from the H743 to
the Mission Planner computer. Keep the flight controller as the primary link
and add the H743 COM port as a secondary link at 115200 baud. The untrusted
coordinates are USB-only and never enter the flight controller's DroneCAN
MAVLink tunnel. Without that cable, DR state/reason/confidence still work but
the live spoof path does not.

For the flight controller, the package now includes the reviewed ten-row
`arduplane_FC_4.6.3_h743_dronecan_CAN1_core.param`. Load it into ArduPlane
4.6.3/SYSID 1; a fresh disabled-CAN setup may need three load/write passes with
reboot/reconnect/refresh between them before all hidden rows exist.

This USB arrangement is for a bench or a GCS physically tethered to the
aircraft. Long-range use requires a separately designed out-of-band link. Bench
test the plugin and capture CAN simultaneously before flight; in DR1, CAN must
contain no GPS `Fix2`/`Auxiliary` and no private `SP_*` position records.

### New: provisional live direction to the jammer/spoofer

Mission Planner plugin `0.3.0` adds a purple dashed RF axis. After at least 20
samples and a real turn, it can show `b / b+180°`; while evidence is
insufficient it shows `COLLECTING` or a specific `ABSTAIN` reason. A 90° turn
is the practical minimum and a full orbit is much better.

This is an **unvalidated two-way axis**, not an arrow, range, or source
position. The fit rejects a plain approach/range trend, weak signal, poor turn
geometry, and disagreeing RF metrics. It uses fixed segments no longer than
120 seconds and is labelled provisional because the open-segment result can
move as samples arrive. The displayed sigma excludes FC-heading age.

The open RF axis works through normal FC telemetry. The second private USB
cable is required for the red/orange tracks and for a map intersection, because
only that link provides sample-aligned moving DR-reference anchors. Direction
fitting runs only in Mission Planner/offline tools and cannot change DR1 or
aircraft control.

### New: aircraft icons and a guarded three-axis intersection

The red/orange/green map points are now heading-aware aircraft icons, with a
non-directional dot fallback when heading is unavailable, and a fixed legend.
**Capture qualified axis** freezes a strict, non-overlapping RF
observation at the mean moving DR-reference position. After three compatible
axes are captured from widely separated positions, Mission Planner may show a
purple target and a dotted geometry-sensitivity circle.

This is deliberately difficult to qualify: each saved segment needs 40 samples
over 20–120 seconds, strong/stable two-metric evidence and at least 90% moving
DR-reference coverage. The three axes must be captured within three minutes,
put every anchor pair at least 500 m apart, separate every axis direction by at
least 30°, share one private-USB session/event/metric, and pass yaw-age,
distance, conditioning, perturbation, and disagreement gates. A
stale or failed gate removes the target instead of preserving an old answer.
The bounded local projection operates only from 70°S to 70°N and includes map
scale distortion in the displayed sensitivity bound.

The label says **UNVALIDATED INTERFERENCE-AXIS INTERSECTION — ADVISORY ONLY**.
It assumes one stationary emitter; it is not a located jammer, ground truth,
an accuracy circle, or a waypoint. It never uses the red untrusted coordinates
and nothing is sent back to the flight controller.

---

## H743 DroneCAN v0.5.28 — 2026-08-17

Supersedes v0.5.27. Adds engine fuel estimation.

### New: fuel estimation from engine RPM

The filter can now estimate fuel burn from the engine RPM your flight
controller already sends it, and report it to ArduPilot as an EFI device. Set
the FC's `EFI_TYPE` to its DroneCAN option and the fuel figure appears in your
GCS and in the dataflash log, with no extra wiring and no extra sensor.

There is no flow meter and no tank sensor in this — it is a model of what the
propeller must be absorbing, calibrated by one number you set after one
weighed flight. Eight parameters describe your engine and propeller, and
presets are included for a DLE-120 on a 27x12 and an RCGF-70 on a 23x10.

**On an aircraft with no fuel gauge, this is the only fuel indication you
have.** It is built to over-report rather than under-report, because
under-reporting is what stops an engine. Uncalibrated, expect it to read
roughly 1.2–2x high; after one weighed burn expect 10–20%. Until you have
calibrated it, fly the clock and treat the number as advisory.

Two things to know before the first flight:

- **Writing `FUEL_CAPG` zeroes the running total.** It is the only thing that
  does. Write it after every refuel, even if the number has not changed.
- **Check `RPM1_SCALING` against a hand tachometer once.** The filter has one
  RPM source, so nothing can contradict it. A twin CDI gives two pulses per
  revolution; configure it for one and the estimate reads far too low. If you
  ever see `Fuel held up by throttle - check RPM_SCALING`, stop and check it.

The running total now survives a mid-flight reboot — watchdog, fault or a
brownout — instead of restarting at zero and showing you a full tank. If it
cannot be recovered the tank reads UNKNOWN and says so every 60 seconds,
rather than quietly reading full.

See "Calibrating the fuel estimate" in the tuning guide for the procedure.

### Fixed: two firmware variants would not build

The sensorless and standalone H743 builds could not be compiled at all. Both
are fixed, and the build system now compiles every variant so this cannot
recur. The DroneCAN firmware is unchanged by that fix.

---

## H743 DroneCAN v0.5.27 — 2026-08-15

### New: interference direction logging

The filter now records what is needed to work out **which direction** a jammer
or spoofer is transmitting from. It does not compute a bearing in the air and
does not use any of it for spoof detection — it only writes the measurements
to your flight log, deliberately kept separate from the protection logic.

After a flight, run `python tools/df_analyze.py flight.bin` on the FC's log to
get a bearing, accurate to roughly ±20–45°.

To get a usable answer you must **fly a full orbit** through the interference.
The method works by watching how received interference power changes with your
heading, so a straight pass gives it nothing to work with and the tool will
correctly refuse to answer.

Two honest limits: one bearing gives you a direction, not a position — you need
two from separated points to triangulate. And until the polarity has been
confirmed against a known transmitter, treat the answer as a line (bearing or
bearing+180°) rather than a direction.

---

## H743 DroneCAN v0.5.26 — 2026-08-14

Supersedes v0.5.25. Flash this one.

**Recovery after jamming is dramatically faster.** If you have seen the filter
sit in DR1 for tens of minutes after a jamming event ended — with no spoofing
involved — this release is the fix.

### What was wrong

The filter was resetting your GPS receiver while it was trying to reacquire.

A u-blox keeps its satellite almanac for hours. Jam it, and once the jamming
stops it normally regains a fix in **seconds**. But the filter was sending a
full receiver reset about 50 seconds into every jamming event — erasing
exactly the data that makes reacquisition fast — and then repeating that reset
every two minutes for as long as the fix was missing. Under the weak signal
that follows a jamming event, a cold reacquisition can take longer than two
minutes, so each reset destroyed the progress the last one had made. The
filter recovered only once conditions improved enough to win the race.

### What changed

- **The receiver is left alone while it is working.** A receiver that is still
  reporting to the filter is acquiring, not stuck, and is no longer reset. A
  genuinely unresponsive receiver is still reset as before. You will see
  `GNSS acquiring - reset held` once per event while this applies.
- **Normal weak-signal warm-up is no longer treated as a spoofing signal.**
  A recovering receiver briefly shows all satellites at similar low strength,
  which the recovery check was scoring as an attack and penalising.
- **A momentary telemetry hiccup no longer throws away the whole countdown.**
  The ground recovery countdown tolerates brief gaps instead of restarting
  from zero. A genuine spoofing indication still stops it instantly.
- **Repeated honest events stop stacking penalties.** Each recovery used to
  make the next one 60 s longer for the rest of the power cycle, and after
  four the unit would not recover at all without a power cycle. Ten minutes of
  normal operation now clears one step.
- **Jamming is no longer mislabelled as spoofing.** A timing quirk meant a
  jamming outage was often recorded as a spoof-class event, which triples the
  required countdown and limits you to one recovery per power cycle.

### Please re-test on the bench

These fixes are verified by code review and automated tests, **not yet by
hardware**. Repeat your jamming test and tell us the recovery time. Watch the
`gnd=` field in the status line — it shows the countdown progressing.

---

## H743 DroneCAN v0.5.25 — 2026-08-13

Supersedes v0.5.24.

Septentrio Mosaic-X5 support is now production-grade, and the same review
that fixed it found two issues that affect **u-blox setups too** — one of
them needs a one-time check on your board.

### Check your board (u-blox and Mosaic alike)

- **If you ever loaded a receiver preset** (`ublox_autoconfig`,
  `manual_ublox_460800`, or `mosaic_x5_nmea`), it silently switched off the
  SNR spoof detector (`SNR_EN=0`) — one of the strongest checks against
  single-transmitter spoofing, and the docs described it as active. The
  presets are fixed; **read `SNR_EN` back from your board and set it to `1`**
  if it reads 0. The value is stored on the board, so flashing new firmware
  alone does not repair it.
- The `field_safe` tuning preset no longer changes your receiver type: it
  used to write `GNSS_TYPE,0`, which turned a Mosaic board back into a
  u-blox profile at its **next power cycle in the field**.

### Fixed — Mosaic X5 on SBF

- **DR1 recovery now works.** The recovery evidence required a timing
  alignment only u-blox receivers produce, so any DR1 trip on a Mosaic —
  even a brief antenna knock — stayed latched until power cycle, and parked
  ground release could never complete. All recovery paths (in-flight rejoin,
  ground release, and the GPS-time spoof trip itself) now evaluate correctly
  on SBF.
- A Mosaic outputting both NMEA and SBF no longer risks silently running in
  NMEA-only mode after boot; SBF takes over within seconds and the richer
  data (covariance, clock checks, per-satellite signal levels) is actually
  used.
- No more GPS dropout seconds after a recovery: an internal receiver rescan
  that only makes sense for other receiver types no longer fires on Mosaic
  right after DR1 clears.
- Routine Mosaic clock adjustments no longer inflate the spoof-confidence
  score; degraded receiver output (error-flagged satellite counts, missing
  geoid data) is no longer taken at face value.

### Added

- The filter now **warns if the configured receiver type contradicts what is
  actually wired** (`GNSS_TYPE mismatch?`) instead of failing silently, and
  tells you if a Mosaic is running NMEA-only with reduced detection coverage.
- Changing `GNSS_TYPE` now genuinely applies at reboot, exactly as the
  confirmation message says, and reads back the saved value.

### Docs

The per-receiver detection coverage tables were over-promising on plain NMEA
(UM980 / Mosaic-in-NMEA): three signals that require velocity or
per-satellite data are now honestly marked unavailable there. If you run a
Mosaic, use SBF mode — NMEA mode costs real detection coverage.

**Bench note:** the Mosaic fixes are verified in code review and static
tests; if you fly a Mosaic, run the standard bench check first — antenna off,
wait for DR1, antenna on, confirm recovery — and confirm `SIG`-free status
with your receiver before a mission.

---

## H743 DroneCAN v0.5.24 — 2026-08-13

Supersedes v0.5.16 through v0.5.23.

The theme of this release group is recovery: DR1 now clears **in the field,
without a power cycle**, on the ground and after long GNSS-denied legs — while
every release still requires evidence, never elapsed time.

### Added

- **Ground release: a parked, disarmed unit recovers from DR1 by itself.**
  When the flight controller independently attests the airframe is parked and
  disarmed, and the returning fix stays self-consistent through a dwell
  (90 s for signal-loss trips, 240 s for integrity trips, escalating on each
  use), DR1 clears where it stands. Releases are budgeted per power cycle,
  every one is announced with a CRITICAL banner, and a probation watch re-trips
  instantly if the fix wanders while the aircraft hasn't moved. `SOUTH` is
  never released automatically: a south-hemisphere fix on this airframe is
  physically impossible and always costs a deliberate human action.
- **Long-flight rejoin now covers the whole mission envelope.** The rejoin
  gate's ceiling was ending recovery after ~1 h 51 m of dead reckoning; it now
  covers the full 8-hour endurance envelope, so a 70 km or 350 km denied leg
  can rejoin when the attack ends. The clock-drift check likewise no longer
  hard-fails on a long outage: its allowance grows with how long the baseline
  has been standing.
- **Honest repositioning no longer strands the unit.** Carrying the parked
  airframe from the bench to the launch point after a ground release re-trips
  DR1 (by design — the fix moved under a stationary airframe), and the unit
  now re-releases from its new position instead of blocking until power cycle.

### Fixed

- **Boards provisioned before v0.5.21 automatically repair a stored recovery
  parameter.** The EKF grace period is stored on the board, and old boards
  kept their stored 7 s — short enough to re-trip DR1 before the flight
  controller's estimator could converge, making recovery effectively
  impossible. The firmware now floors the stored value at 20 s (default 60 s),
  and re-provisioning writes the default outright. If your unit ever seemed to
  "never recover no matter how long you wait", this was very likely why.
- Provisioning no longer re-installs an obsolete rejoin ceiling on new boards.
- The status line no longer publishes a negative DOP, and normal bus traffic
  is no longer counted as CAN errors.

### After flashing

Nothing to reconfigure: parameters you have deliberately tuned are preserved,
and only unsafe stored values are floored. Verify on the bench before flying —
remove the GNSS antenna, wait for DR1, reattach it, and confirm the status
line reaches DR0 again on its own.

---

## H743 DroneCAN v0.5.16 — 2026-08-08

Supersedes v0.5.13.

### Added

- **The magnetometer is no longer compiled into the default build.** Airframes
  that take their compass from the flight controller no longer see a node
  reported unhealthy for a sensor that was never fitted. Boards that do have one
  build `weact_mini_h743vitx_dronecan_mag`; boards with neither sensor build
  `weact_mini_h743vitx_dronecan_nosensors`.
- **The receiver's spoof-detection state is now reported.** The status line gains
  `enXY`, and the filter warns if the receiver has spoof detection switched off -
  previously that looked identical to "no spoofing seen", while three of the
  strongest checks were silently doing nothing.

### Fixed

- A flaky airspeed sensor can no longer inflate the DR1 recovery hold without
  limit. Contradicted recovery attempts still cost time, but the penalty now
  decays once the evidence stops contradicting.

### Changing the filter's parameters

The filter's parameters are **not** in Mission Planner's Full Parameter List.
That list edits the flight controller. The filter is a separate node, **system ID
42**, and writes typed into the FC's list silently go nowhere.

Use the DroneCAN parameter screen (SETUP -> Optional Hardware -> DroneCAN/UAVCAN,
`MAVLink - CAN1`, node 42 -> Parameters), or the new script:

```
python tools/mission_planner/filter_params.py --port COM25 --list
python tools/mission_planner/filter_params.py --port COM25 --set LOG_MS=2000
```

Writes are refused while the flight controller is armed, and the filter says so.
`ARM=1` in the filter's own status line does **not** mean the FC is armed - that
field is the spoof guard's warm-up state and is healthy.

---

## H743 DroneCAN v0.5.13 — 2026-08-08

Supersedes v0.5.7 through v0.5.12, which were same-day iterations. Flash this one.

### Fixed — DR1 could latch when nothing was wrong

- **A stationary or slow aircraft no longer contradicts itself out of recovery.**
  The ground-speed plausibility row required at least 8 m/s to recover, so a unit
  that latched DR1 while stationary recorded 0 m/s as its reference and then
  refused to clear forever. This is the `ev3/3F1p` some units showed after a GPS
  antenna was unplugged and reconnected. In flight the same check fired on a
  takeoff roll and in any headwind strong enough to hold ground speed under
  8 m/s. It is now referenced against the flight controller's own speed estimate
  instead of against remembered GNSS.
- **An aircraft flying without a compass no longer latches DR1 while parked.** A
  stationary airframe with no magnetometer cannot complete EKF yaw alignment, so
  the flight controller reported a state the filter read as a spoof. It then
  sustained itself, because withheld GNSS is exactly what stops the estimator
  aligning. A never-yet-aligned EKF is now treated as a startup state.
- **A brief CAN tunnel stall no longer costs minutes of GPS.** Suppression on a
  stale flight-controller link stays immediate; the DR1 latch now waits 10 s.
- **One indicator can no longer trip the spoof-confidence quorum on its own.**

### Changed

- The boot spoof veto is unchanged in behaviour after an intermediate release
  briefly weakened it. If you flashed v0.5.11, replace it.

### Known limits, stated plainly

- **DR1 will not clear on a stationary bench, and no release will change that.**
  Clearing requires an independent non-GNSS witness, and a desk supplies none.
  Expect `ev3/3F0p` and power-cycle instead of waiting.
- **With no airspeed sensor and no compass fitted**, recovery needs a sustained
  climb or a steady turn - an autopilot loiter is ideal. Straight-and-level
  flight will not clear DR1.

---

## Desktop app 2026.08.02.2 — 2026-08-02

### Fixed

- Every SWD command and reconnect is pinned to the serial number of the sole
  enumerated ST-Link. A missing, replaced, or additional probe stops the flow
  before further board access.
- USB DFU is re-enumerated immediately before every erase, firmware write, and
  option-byte transition. Device-count or exposed-serial changes abort instead
  of risking the wrong board.
- Recover Board now reads every byte of physical flash before reporting a
  board blank: 256 KiB for F401 and 2 MiB for H743, including staging, saved
  tuning, reserved, and metadata regions.
- Firmware and ordinary API responses are streamed, size-bounded, decoded
  within that bound, and closed on every success and error path.
- The app now carries a separately reviewed firmware-signing public key and
  rejects any server bundle whose key differs. It also verifies a separate
  target-bound Ed25519 signature over every exact personalized bootloader byte,
  so a server response cannot substitute executable bootloader code.

---

## H743 DroneCAN v0.5.6 — 2026-08-02

### Fixed

- If filtered GNSS output becomes blocked, all already queued DroneCAN frames
  are now revoked before recovery can resume publishing. The firmware resets
  FDCAN through RCC, drains libcanard, and repeats the complete timing, filter,
  and controller-start sequence while output stays fail-closed.

This build remains a release candidate until the hardware/HIL checklist is
signed for its exact SHA-256 values.

---

## Desktop app 2026.08.02.1 — 2026-08-02

### Fixed

- Activation and protected updates now validate the entire server bundle before
  any erase: response target/UID, metadata format and plaintext fields, packed
  version, vector table, BLAKE2b app hash, Ed25519 signature, patched bootloader
  keys, UID binding, and report token must all agree.
- The exact validated bytes are retained across an RDP reconnect; the app never
  fetches replacement firmware after the board has been erased.
- Protected USB DFU now stops before writing if the physical UID cannot be read
  and verified after RDP removal. It no longer substitutes the activation UID
  for an unavailable hardware measurement.
- Firmware version selection, tuning-loss/recommission warnings, and physical
  UID mismatch failures are explicit in both English and Ukrainian flows.
- Every destructive flow now requires the exact physical-board phrase
  `F401CC BLACKPILL` or `WEACT H743VI` before hardware access and after each
  reconnect/transport change. `--yes` cannot bypass it; explicit 128 KiB F401
  and 1 MiB H743 identities are rejected before option-byte or erase access.

---

## H743 DroneCAN v0.5.5 / F401 v1.6.26 - 2026-08-02

### Fixed

- GNSS forwarding no longer resumes with the post-DR1 position/time integrity
  guards temporarily disabled. Parser handling for invalid altitude, UTC,
  SNR, SEC-SIG, malformed frames, and receiver reset was tightened.
- H743 CAN faults now recover through bounded retries while output remains
  fail-closed. Stuck I2C lines, tune-journal stalls, and runtime watchdog hangs
  now have bounded recovery or reset behavior.
- F401 and H743 production applications enforce the UID embedded for the
  physical board; unprovisioned templates cannot be uploaded directly.

### Provisioning and releases

- The desktop/CLI tools validate the complete downloaded bundle before any
  destructive operation and verify the physical UID before success.
- New firmware is inactive until an owner completes qualification and promotes
  it. Revoked, inactive, malformed, or storage-tampered binaries are never
  offered to customers.
- These builds remain release candidates until the hardware/HIL checklist is
  signed for their exact SHA-256 values.

## Desktop app 2026.07.23.2 - 2026-07-23

### Added

- **Recover Board** for H743 now finishes the job even when SWD cannot erase
  the chip at all: after the watchdog-frozen and BOOT0-mode SWD attempts it
  retries once at a low SWD clock, then walks you through a **USB-C ROM DFU
  erase** — the chip's own bootloader erases the flash internally on USB
  power, with no SWD link or ST-Link supply involved. This also recovers
  boards whose flash was left half-erased (reads as zeros) by an interrupted
  earlier update.
- The final failure message now explains that a chip which cannot be erased
  even by its own ROM bootloader on stable USB power most likely has damaged
  flash and should be replaced.

---

## H743 DroneCAN v0.4.3 - 2026-07-23

### Fixed

- The firmware now freezes its 15-second hardware watchdog whenever a
  debugger or the provisioning app halts the chip over SWD (DBGMCU freeze
  bit set at boot), so long flash operations like a full-chip erase can no
  longer be reset mid-way by the firmware's own watchdog. This has no effect
  in flight — the freeze only applies while a debugger holds the core halted.
- The automatic boot-time parameter migration no longer starts background
  flash writes while a debugger session is active; it completes on the next
  normal boot instead. Parameter changes you make yourself are saved as
  always.

---

## Desktop app 2026.07.23.1 - 2026-07-23

### Fixed

- H743 mass-erase failures (`Mass erase operation failed. Please verify flash
  protection` with RDP already at `0xAA`) were caused by the installed
  firmware's 15-second hardware watchdog resetting the chip mid-erase, not by
  flash protection. Every H743 ST-Link erase now freezes that watchdog for the
  halted debug session (`DBGMCU` `DBG_IWDG1` write in the same CubeProgrammer
  invocation) before erasing.
- Removed the H743 `-ob unlockchip` fallback: CubeProgrammer only supports
  `unlockchip` on STM32WL, so it always failed on H743 and filled the log with
  `Error: Only STM32WL devices are supported`.
- The failed-erase "already blank" shortcut now uploads and verifies every
  written region (bootloader, application, metadata) plus the H743
  parameter-journal sectors instead of checking six sentinel words, so a
  partially erased chip can no longer slip through to the write step.

### Added

- Guided **BOOT0 power-cycle** recovery for H743: if the erase still fails,
  the app walks you through holding BOOT0 while reconnecting power, so the
  chip boots its ROM bootloader instead of the firmware and the erase runs
  with no watchdog at all. The final error message now names the watchdog
  cause instead of pointing at flash protection.

---

## H743 DroneCAN v0.4.2 - 2026-07-21

### Changed

- Tuned the H743 fixed-wing defaults for aircraft cruising near 120 km/h:
  `EKF_TRIPMS=500`, `SP_JMP_MPS=200`, `SP_ABS_M=400`, and
  `RJ_LOIT_V=0`. Existing custom settings are preserved during upgrade, and
  F401 defaults are unchanged. Mathematical guard tests cover a 65 m/s
  (234 km/h) design envelope; this is not a substitute for flight-log validation.

### Fixed

- Jump detection now uses GNSS receiver epochs instead of UART arrival time,
  preventing duplicate or backlogged messages from creating false speed
  alarms. Generic EKF loss uses the configured debounce, while explicit
  `GPS_GLITCHING` is immediate after inhibition and startup `UNINITIALIZED`
  cannot reopen after a healthy FC session.
- Explicit no-fix reports, receiver handovers, and same-epoch DroneCAN Fix2
  completion now fail closed without mixing fields or bypassing jump checks.
  Malformed active-owner coordinates invalidate the fix, and source handover
  clears old quality/SNR evidence;
  Fix2 UTC timestamps retain receiver millisecond precision.
- Boot, DR lock, rejoin, and EKF grace timers remain correct beyond 24.9 days
  of uptime and across the 32-bit timer rollover.

---

## H743 DroneCAN v0.4.1 - 2026-07-21

### Added

- Added a dual-sector, commit-last H743 parameter journal with stable name keys
  that preserve unknown values within supported schemas.
- Replaced F401 runtime sector erase with a transactional append-only journal;
  a full journal refuses persistence and retains the last committed settings.

### Changed

- Production defaults now fail closed with live FC heartbeat/EKF evidence,
  EKF-confirmed rejoin, a two-minute DR1 lock, enabled SNR guard, no forced DR1
  timeout, and location-redacted status text.
- Parameter writes and resets require fresh, explicitly disarmed FC evidence
  from the configured or leased DroneCAN peer.
- Secure H743 app/staging windows are 640 KiB each. The production bootloader
  verifies RDP1 and retains the v0.4.0 anti-rollback compatibility floor; the
  server enforces the same floor across customer-visible selection paths.

### Fixed

- Kept all private DR geometry, altitude, confidence, EKF, and fence gates live
  in pass-through mode and during optional GNSS blending.
- Made malformed, stale, non-finite, out-of-range, or wrong-source GNSS,
  MAVLink, and DroneCAN safety evidence fail closed. Fixed 1 Hz heading
  reversal confirmation, antimeridian residuals, and GetSet DSDL decoding.
- Lease expiry and FC reboot now purge both directions of both MAVLink tunnels,
  reset every FC-derived state, and re-request the complete telemetry set.
- Hardened MS4525 and HMC5983 reads, I2C recovery, nonblocking display/USB work,
  and the non-overlapping `NodeStatus` vendor layout.

---

## H743 DroneCAN v0.4.0 - 2026-07-21

### Added

- Replaced the row-only status screen with a professional dark dashboard for
  the onboard 80 x 160 ST7735 color TFT. It uses custom striped `OK` / `!!` /
  `XX` hero glyphs, proportional body typography, rounded metric tiles,
  gradient health rails, and segmented CAN/MAVLink activity rails.
- Added a matching animated startup scene, page dots and footer underline, and
  eased five-frame transitions between Overview, Sensors, Links, and System.
- Added a dependency-free, pixel-exact browser preview generated by the same
  portable C++ RGB565 renderer as the firmware, plus native renderer safety and
  state-transition tests.

### Changed

- The persistent footer now shows GPS publication, DR0/DR1, and DroneCAN node
  ID. Sensor/link warnings pin the page that explains them; armed state,
  filter blocks, and FC alerts lock the UI to the relevant safety view; filter
  or FC faults use a dedicated alert takeover. The dashboard reports
  `FILTER CHECK / GUARD` until the real startup spoof-guard timer
  expires; page sliding requires a fresh, positively disarmed FC state.
  `PUB+`, `PUB?`, and `PUB-` now distinguish a recent Fix2 accepted into the
  local transmit queue, allowed-but-idle output, and blocked/unavailable output.
  `PUB+` is not an FC acknowledgement. Dual filter/FC alerts remain visible.
- Renamed the normal USB indication to `USB CONFIG`; ROM DFU still requires
  `BOOT0` plus reset or power-up.
- Display transfers are incremental and yield to GNSS/CAN processing. Screen
  values remain convenience diagnostics and do not replace FC pre-arm checks,
  sensor calibration, or flight-log review.
- The redesign changes presentation only. Spoofing gates, DR0/DR1 behavior,
  DroneCAN GPS/sensor publication, and both MAVLink2 virtual ports are
  unchanged.

---

## H743 DroneCAN v0.3.0 - 2026-07-21

### Added

- Added a shared 400 kHz I2C2 sensor bus on H743 `PB10` SCL / `PB11` SDA for
  the default `4525DO-DS3AI001DP` differential-pressure sensor and a genuine
  HMC5983 magnetometer.
- Added native DroneCAN `RawAirData` publication at up to 20 Hz and
  `MagneticFieldStrength2` publication at up to 25 Hz through the existing CAN
  transceiver and node ID `42`.
- Documented a separate keyed 4-pin 3.3 V sensor connector because the HD-15
  assignment is full, including full-part-code, clone, placement, calibration,
  pull-up and bench-test requirements.

### Changed

- Airspeed and compass publications remain active independently of the GNSS
  DR0/DR1 gate, just like NodeStatus and both MAVLink2 tunnel ports.
- Optional I2C work is staggered behind pending GNSS input with a 2 ms core
  timeout, and the H743 GNSS RX ring is 1024 bytes so a missing or stuck sensor
  cannot crowd out spoof-filter input processing.

---

## H743 DroneCAN v0.2.0 - 2026-07-21

### Added

- Added bidirectional OpenIPC camera MAVLink2 on H743 `PA10` RX / `PA9` TX,
  carried to ArduPilot through standard `uavcan.tunnel.Targetted` port index
  `0`.
- Added a separate DroneCAN virtual serial port at index `1` for the filter's
  own MAVLink2 and returning FC telemetry, preserving heartbeat, status,
  tuning, EKF, barometer, arm-state, and rejoin behavior.

### Changed

- Increased UART and FDCAN buffering, added bounded application queues and
  libcanard pool reservation, and serviced CAN between GNSS/display operations
  so continuous camera traffic cannot crowd out native GPS `Fix2/Auxiliary`.
- Kept both MAVLink ports active in DR1 while GPS publication remains subject
  to all existing spoofing-filter gates.

---

## H743 DroneCAN v0.1.11 - 2026-06-24

### Fixed

- Split spoof-confidence freshness tracking for pseudorange residuals and C/N0
  temporal correlation. Mosaic X5 SBF `MeasEpoch` now contributes only the C/N0
  temporal signal, while the u-blox-only pseudorange residual score stays
  disabled in Mosaic mode instead of inheriting a stale/default value.

---

## H743 DroneCAN v0.1.10 - 2026-06-24

### Added

- Published TDOP from u-blox `NAV-DOP` and Mosaic X5 SBF `DOP` into DroneCAN
  `uavcan.equipment.gnss.Auxiliary` when the field is fresh.
- Added a compact Mosaic-only `SBF good/bad` line to the H743 onboard screen.
  The first number is accepted SBF frames; the second number is bad SBF CRCs.

---

## H743 DroneCAN v0.1.9 - 2026-06-24

### Fixed

- Corrected Mosaic X5 SBF `DOP` mapping for DroneCAN. Septentrio block `4001`
  reports PDOP, HDOP, and VDOP but not GDOP, so H743 DroneCAN now publishes the
  SBF value as PDOP and leaves GDOP unknown instead of reporting PDOP as GDOP.
- Aligned the Mosaic PVT mode mapping with the Septentrio reference: reserved
  mode `9` is no longer reported as PPP.

---

## H743 DroneCAN v0.1.8 - 2026-06-23

### Added

- Added native Septentrio Mosaic X5 SBF parsing to the H743 DroneCAN firmware
  when `GNSS_TYPE=2`. The firmware now accepts validated SBF frames on the GNSS
  UART and maps `PVTGeodetic`, `DOP`, `ReceiverTime`, `MeasEpoch`,
  `PosCovGeodetic`, and `VelCovGeodetic` into the same DroneCAN GPS and
  spoof-guard state used by other receivers.
- The passive GNSS baud scanner now scores valid SBF frames as well as NMEA
  sentences, so a Mosaic configured for SBF-only output can be detected at boot.

### Changed

- Updated the H743 Mosaic setup docs with the recommended SBF block profile.
  UART/F401 Mosaic deployments still use the NMEA profile unless a custom
  SBF-enabled build is produced.

---

## Docs/Tools - 2026-06-23

### Changed

- Reserved a separate H743 DroneCAN flash staging region for future
  Mission Planner/AirDroper app DroneCAN firmware updates. Current H743 updates
  still use ST-Link/SWD or USB-C ROM DFU.
- Updated the H743 DroneCAN guide to show the full secure flash layout and to
  clarify that standard DroneCAN firmware update is planned but not active yet.
- Documented and test-guarded the GPS data integrity contract: UART builds
  forward unchanged receiver bytes in DR0, while H743 DroneCAN publishes parsed
  live receiver fix values and never sends synthetic/blended GPS coordinates.

---

## H743 DroneCAN v0.1.7 - 2026-06-23

### Fixed

- Refined H743 DroneCAN `NodeStatus` health again so latched no-fix and
  low-satellite DR1 reasons also keep node health `OK`. Only spoof/fault DR1
  reasons now report warning health, so ArduPilot should stop showing
  `PreArm: DroneCAN: Node 42 unhealthy!` when the receiver simply has no GPS
  fix yet.

---

## H743 DroneCAN v0.1.6 - 2026-06-23

### Fixed

- Fixed H743 DroneCAN `NodeStatus` health so boot guard and
  receiver-reconfiguration output suppression stays `OK`. This release was
  superseded by `v0.1.7`, which also keeps no-fix and low-satellite DR1 cases
  from marking the node unhealthy.

---

## H743 DroneCAN v0.1.5 - 2026-06-23

### Added

- Added a direct USB-C MAVLink management port for H743 DroneCAN boards. In the
  normal app, with `BOOT0` released, Mission Planner can connect to the H743
  USB COM port at `115200` and edit the same spoofing/tuning parameters from
  **CONFIG -> Full Parameter Tree/List**.

### Changed

- H743 DroneCAN still does not use any flight-controller serial port. DroneCAN
  node Params remain the in-aircraft tuning path; USB-C MAVLink is for direct
  bench/service access to the H743 itself.

---

## H743 DroneCAN v0.1.4 - 2026-06-23

### Added

- Added editable H743 spoofing/tuning parameters through Mission Planner's
  DroneCAN/UAVCAN node `42` Params window. `GPS_TYPE`/`GPS1_TYPE` remain
  read-only compatibility rows at value `9`; the guard/tune params follow
  those rows and persist through DroneCAN **Commit Params**.
- Added DroneCAN `uavcan.protocol.param.ExecuteOpcode` save handling so
  Mission Planner's **Commit Params** button commits changed H743 parameters
  to flash.
- Added `UBX_RESET` as a DroneCAN one-shot command for u-blox hot start, cold
  start, or config reset.

### Changed

- H743 DroneCAN now loads and saves the same tuning blob used by the UART
  firmware while keeping MAVLink-dependent settings locked off:
  `RJ_REQEKF=0`, `FCGPS_UART=0`, and `FCGPS_FWD=0`.

---

## H743 DroneCAN v0.1.3 - 2026-06-23

### Changed

- The WeAct H743 LCD now shows an immediate boot/progress page before the longer
  GNSS startup path. During receiver autobaud/config, the screen should show
  `GNSS INIT` instead of staying black until the main loop starts.

---

## H743 DroneCAN v0.1.2 - 2026-06-23

### Added

- Added a minimal read-only DroneCAN `uavcan.protocol.param.GetSet` response
  for ArduPilot `GPS_TYPE`/`GPS1_TYPE` queries. This keeps H743 DroneCAN GPS
  usable even if `GPS_AUTO_CONFIG=2` is enabled on the flight controller.
- Documented ArduPilot `GPS_AUTO_CONFIG=1` as the recommended setup and
  `GPS1_CAN_OVRIDE=42` as the optional node lock when multiple DroneCAN GPS
  nodes are present.

---

## H743 DroneCAN v0.1.1 - 2026-06-23

### Fixed

- Fixed the WeAct H743 onboard LCD backlight polarity. If an H743 DroneCAN
  board on `v0.1.0` boots with the blue LED blinking every few seconds but the
  screen stays black, update to `v0.1.1` with the AirDroper GNSS Filter app.
  DroneCAN GPS output still runs without the screen.

---

## H743 DroneCAN v0.1.0 - 2026-06-23

### Added

- Published the separate **H743 WeAct DroneCAN** firmware family for WeAct
  Studio MiniSTM32H743VITX boards with an external 3.3 V CAN transceiver.
- Added native DroneCAN GPS publishing for ArduPilot: `Fix2` on fresh GNSS
  updates, `Auxiliary` at 1 Hz, and `NodeStatus` while the node is online.
- Added the H743 target to the Windows provisioning app as
  **Board target -> H743 WeAct DroneCAN**.
- Added H743 update transports in the provisioning app:
  **ST-Link (SWD)** for activation/update and **USB-C ROM DFU** for already
  activated H743 boards.
- Added the complete H743 DroneCAN documentation page, including SN65HVD230
  wiring, `PB9/PB8` CAN pins, USB-C DFU steps, ArduPilot `GPS1_TYPE=9`
  setup, onboard screen behavior, and the optional HD-15 D-sub box pinout.

### Changed

- The public download link now serves the desktop app build with H743 DroneCAN
  target support:
  [gps.airdroper.org/download/app](https://gps.airdroper.org/download/app).
- Rebuilt the desktop app as `2026.06.23.1` so H743 mass-erase failures that
  report `Please verify flash protection` now run the H743 option-byte recovery
  retry path before giving up.
- Rebuilt the desktop app again as `2026.06.23.2` so an H743 app/metadata
  write failure after a successful erase also runs the same recovery path and
  retries before stopping.
- Rebuilt the desktop app as `2026.06.23.3` so every ST-Link and USB-C flash
  log prints the flasher app version separately from the board firmware version
  (`v0.1.0` for the current H743 DroneCAN firmware).
- Rebuilt the desktop app as `2026.06.23.4` so **Recover Board** also supports
  the H743 WeAct DroneCAN target through ST-Link/SWD using the H743 RDP-only
  unlock, mass erase, and blank-flash verification path.
- Rebuilt the desktop app as `2026.06.23.5` so H743 ST-Link/SWD attach tries
  lower hardware-reset and hotplug speeds down to 125 kHz and prints a direct
  `DEV_TARGET_HELD_UNDER_RESET` reset-line diagnostic.
- Rebuilt the desktop app as `2026.06.23.6` so H743 ST-Link/SWD activation,
  update, and recovery use CubeProgrammer's GUI-equivalent
  `mode=NORMAL reset=SWrst` path before the under-reset/hotplug fallbacks.
- Rebuilt the desktop app as `2026.06.23.7` so ST-Link/DFU connection
  diagnostics explicitly tell users to close STM32CubeProgrammer GUI or other
  flashing tools before retrying.
- Rebuilt the desktop app as `2026.06.23.8` so Activate, Update, USB-C DFU,
  and Recover stop before hardware access when STM32CubeProgrammer GUI or a
  leftover STM32 programmer process is already running.
- Rebuilt the desktop app as `2026.06.23.9` so the busy-programmer preflight
  tells users to end a stale `STM32_Programmer_CLI.exe` from Windows Task
  Manager before retrying.
- Rebuilt the desktop app as `2026.06.23.10` so H743 full rewrites write the
  app and metadata as separate flash operations, and continue after a failed
  mass erase when the bootloader/app/metadata slots already read blank.
- The provisioning server now exposes a separate `h743_dronecan` firmware
  channel. F401 firmware remains on the existing `1.6.24` stable channel.

---

## Docs/Tools - 2026-06-06

### Changed

- Updated the Mission Planner parameter metadata installer so it supports both
  modern `*.apm.pdef.xml` metadata files and older cached
  `ParameterMetaData.xml` installations.
- Added `README_UK.md` to the downloadable Mission Planner ZIP so Ukrainian
  setup instructions are available inside the package.
- Repeated the Mission Planner params download link in setup, tuning, receiver
  configuration, FAQ, and troubleshooting pages so users can find the metadata
  package while working through the relevant workflow.

---

## Docs/Tools - 2026-06-05

### Added

- Published the Mission Planner parameter metadata ZIP at
  [gps.airdroper.org/download/mission-planner-mod](https://gps.airdroper.org/download/mission-planner-mod).
  The package installs descriptions, ranges, units, option labels, and ready
  `.param` presets for the STM32 filter parameters.

---

## v1.6.24 - 2026-06-03

Official stable release, promoted on 2026-06-06 after field validation.

### Changed

- Periodic status logs now emit only one `data=...` line and one
  `ARM=... DR=...` line per `LOG_MS` interval, instead of duplicating each
  line under both MAVLink identities.
- The normal periodic `fcgps tx=... rx=...` diagnostic line was removed to keep
  Mission Planner Messages readable during healthy operation.

---

## v1.6.23 - 2026-06-02

Official stable release, promoted on 2026-06-03 after field validation of the
u-blox F9P SNR recovery path and Mosaic X5 passive-NMEA support.

### Added

- Added `GNSS_TYPE=2` for Septentrio Mosaic X5 receivers configured for NMEA.
- Added Mosaic X5 setup guidance to the receiver configuration docs.

### Changed

- Mosaic X5 mode uses passive NMEA autobaud and does not send receiver reset or auto-configuration commands. If no fix persists, the filter only re-runs the passive NMEA baud scan.

---

## v1.6.22 - 2026-06-02

Firmware-only u-blox autoconfig cleanup build. At release time, v1.6.15
remained the stable server default; choose `v1.6.22 (dev)` only when support
asks you to test it.

### Firmware

- **Autoconfig starts from receiver defaults**: in direct u-blox mode with
  `UBX_BAUD=0`, boot now forces the receiver to the target baud, clears/loads
  receiver defaults, rescans baud, then applies and saves the filter's UBX
  profile.
- **Manual baud/gateway mode is excluded**: if `UBX_BAUD>0`, the filter skips
  the boot clear/autoconfig path and keeps using the configured baud directly.
  This preserves intentional operator/vendor profiles.
- **Expected UX**: direct F9/F10/M9/M10 receivers should recover from stale
  saved u-center or vendor settings without needing a manual `UBX_RESET=3`
  bench step first.

---

## v1.6.21 - 2026-06-02

Firmware-only u-blox SNR recovery correction. At release time, v1.6.15
remained the stable server default. Superseded by `v1.6.22 (dev)`.

### Firmware

- **Corrected fast NAV-SAT recovery gate**: v1.6.20 shortened the stale-SNR
  timer, but the old 30-second NAV-SAT freshness gate could still block the
  fast path. v1.6.21 uses the same 8-second window for both checks when a
  healthy u-blox fix already exists.
- **No change to startup/no-fix behavior**: no-fix, zero-C/N0, and startup
  acquisition cases still use the slower 30-second path.

---

## v1.6.20 - 2026-06-02

Firmware-only u-blox SNR recovery test build. At release time, v1.6.15
remained the stable server default. Superseded by `v1.6.21 (dev)`.

### Firmware

- **Faster intermittent NAV-SAT recovery**: when a u-blox receiver already has a
  healthy fix and NAV-SAT later disappears, the firmware now re-enables NAV-SAT
  after about 8 seconds instead of waiting the full 30-second stale-SNR window.
- **Startup/no-fix behavior stays conservative**: no-fix, zero-C/N0, and
  startup acquisition cases still use the slower existing path so the firmware
  does not churn receiver configuration while RF acquisition is still unstable.
- **SNR guard remains safe**: stale or missing SNR still cannot trigger DR1 by
  itself. The faster recovery only shortens the `SNR=NA` display gap.

---

## v1.6.19 - 2026-06-02

Firmware-only u-blox no-fix recovery test build. At release time, v1.6.15
remained the stable server default; choose `v1.6.19 (dev)` only when support
asks you to test it.

### Firmware

- **u-blox zero-satellite assist before DR1**: when the receiver is alive but
  remains at `SATS=0`, the filter now sends a cold start plus STM32 reinit
  after about 2 minutes. This is limited to u-blox autoconfig mode and does not
  run in DR1, raw bridge mode, or FC GPS forward-bypass mode.
- **No automatic destructive u-blox config clear**: `UBX_RESET=3` remains a
  manual bench/recovery command. The firmware does not clear saved u-blox
  BBR/Flash configuration automatically, because that can slow acquisition or
  delete an intentionally saved receiver profile.
- **Manual fallback stays documented**: if automatic zero-satellite recovery
  does not restore acquisition, the bench fallback remains `UBX_RESET=3`
  followed by a full power-cycle. The firmware now prints
  `If stuck: bench UBX_RESET=3` after the automatic retry.

---

## v1.6.18 - 2026-06-02

Firmware-only u-blox SNR stability test build. At release time, v1.6.15
remained the stable server default; choose `v1.6.18 (dev)` only when support
asks you to test it.

### Firmware

- **FC GPS back-channel can no longer change the u-blox receiver profile in
  normal protected mode**: field logs showed repeated `SNR=NA` bursts with
  healthy position/fix data and small `fcgps rx` increments just before
  `NAV-SAT` stopped. The filter now drains and counts those FC back-channel
  bytes but does not forward them into the receiver, so ArduPilot
  auto-config/probe writes cannot disable the `NAV-SAT` stream used for SNR.
- **`fcgps rx` is now a drain counter in normal mode**: it still shows that the
  flight controller is sending bytes on the GPS back-channel, but those bytes
  are not allowed to reconfigure the receiver. Dedicated raw-lab bridge builds
  remain bidirectional.
- **u-blox CFG-GNSS diagnostics corrected**: the `ubxgnss ... ch.../...` line
  now reads the receiver channel counts from the correct `UBX-CFG-GNSS`
  payload fields. This fixes misleading diagnostics such as `ch60/0`; it does
  not change constellation configuration.

---

## Tooling update - 2026-05-29

Follow-up recovery fix for STM32F401 boards that are already readable as
`RDP0` but still latched in `SPRMOD=1` / PCROP mode.

- **License-only firmware status check**: the desktop app now has a
  **Check Status** button that uses only the license key and does not touch
  ST-Link or the board. It shows registered boards, boards that have reported
  completed flashing, registered boards without a flash report, total reported
  successful flash attempts, default stable firmware, and per-board flash
  timestamps.
- **Completed flashing is now tracked separately from activation**: server
  registration still happens before board writes start, but the app reports
  physical flash completion only after the final bootloader/RDP lock step.
  Older activations may show as registered without a flash report until they
  are updated with a reporting app build; they are shown as legacy/unknown,
  not as confirmed failed flashes.
- **Flash-status reports are now authenticated**: the server returns a
  short-lived report token with each ST-Link Activate/Update bundle, and the
  final flash-status callback rejects missing, expired, reused, or mismatched
  tokens. Use desktop app `2026.05.29.9` or newer for authenticated
  flash-status counts.
- **Successful Activate/Update now shows a clear popup**: after the final
  physical success point, the desktop app opens an OK dialog with firmware
  version and board UID so users do not have to inspect the log to know the
  operation finished correctly.
- **Successful Recover Board now shows the next step**: after recovery verifies
  blank flash and cleared RDP, the desktop app opens an OK dialog telling the
  user to click **Activate** to provision the recovered board.
- **Multi-board licenses can now update a selected board**: when a license has
  multiple registered boards, the desktop app and CLI ask the operator to type
  the target UID-short or full UID from the server list before any ST-Link
  access starts. The protected-board RDP1 erase confirmation still appears
  later if the connected board hides its physical UID.
- **Landing-page app download now points at the pinned published EXE**: the
  server no longer depends on GitHub's moving `latest` redirect, so the public
  download link cannot serve an older cached desktop app after a release.
- **Power-cycle prompts no longer tell users to plug into BlackPill USB-C**:
  desktop app, CLI, and self-install docs now say to remove and restore board
  power. If the board is powered from ST-Link 3V3, unplug/replug the ST-Link
  USB from the PC; do not use the BlackPill USB-C connector.
- **Firmware label now separates stable default from selected dev builds**:
  the desktop app labels the server value as **Default stable firmware** instead
  of "Server firmware version" / "Latest firmware", so selecting a dev firmware
  in the dropdown no longer looks inconsistent with the stable default shown
  below it.
- **Firmware dropdown now marks the first entry as stable default**: the desktop
  app shows `vX.Y.Z (stable default)` instead of `vX.Y.Z (latest)`, while dev
  builds remain separate `vX.Y.Z (dev)` entries.
- **Landing-page license status uses the same stable-default wording**: the
  public license checker now labels the server firmware value as **Default
  stable firmware** instead of the generic "Firmware".
- **Activation logs now separate server registration from physical flashing**:
  Activate reports whether the UID was already registered on the server or is
  being newly reserved, then logs when the firmware bundle has been returned
  and board flashing starts. The board is only physically provisioned after
  the final `Provisioning complete` line.
- **Activation now writes the bootloader last and locks in the same ST-Link
  session**: the app mass-erases first, writes/verifies the application and
  metadata while the bootloader sector is blank, then writes/verifies the
  bootloader and applies RDP1/BOR/SPRMOD/WRP in one CubeProgrammer command.
  This prevents the bootloader from running and making flash unreadable before
  host-side verification finishes.
- **Bootloader option-byte cleanup now detects F401xD/E layout**: if the
  bootloader ever has to enforce RDP itself, it uses the eight-bit WRP mask on
  STM32F401xD/E devices instead of the six-bit F401xB/C mask.
- **STM32F401xD/E write-protect recovery now uses per-sector WRP bits**: some
  boards expose `WRP0..WRP7` as individual option bytes and reject the packed
  `WRP0=0x3F` value. Recover/Update now falls back to
  `WRP0=0x1 ... WRP7=0x1` and no longer treats CubeProgrammer's
  "invalid value / unchanged" warning as success.
- **STM32F401xD/E RDP-drop recovery now clears all per-sector PCROP bits**:
  when option bytes expose `WRP0..WRP7`, the RDP1->RDP0 repair write now uses
  `WRP0=0x0 ... WRP7=0x0` instead of the packed `WRP0=0x00` form. This prevents
  Activate/Recover from relocking boards with `SPRMOD=1` and PCROP still active.
- **Forced PCROP re-arm now writes only RDP1**: Recover Board now re-arms the
  temporary RDP1 state with `RDP=0xBB` only. It no longer tries to clear
  `WRP0` during the RDP0->RDP1 step, because STM32F4 only allows PCROP/WRP0
  bits to be cleared during the following RDP1->RDP0 regression.
- **Recover skips the invalid RDP-drop write when RDP is already clear**: if
  the board is already at `RDP0`, the app goes straight to SPRMOD
  verification/repair instead of attempting a no-op `RDP=0xAA` transaction
  that also carried unsafe `WRP0=0x00` at RDP0.
- **Recover Board confirmation is back to OK/Cancel**: the typed `RECOVER`
  prompt was removed. The app now uses the normal destructive-action
  confirmation dialog.

---

## Tooling update — 2026-05-28

Emergency recovery update for STM32F401 boards left in `SPRMOD=1` / PCROP
mode after failed updates.

- **PCROP salvage sequence changed to F401 WRP0 semantics**: Recover Board now
  drops RDP with `RDP=0xAA` + `SPRMOD=0` + `WRP0=0x00` + `BOR_LEV=3`, then
  after the power cycle clears normal sector write protection with `WRP0=0x3F`.
  CubeProgrammer's own STM32F401 database defines WRP0 as six bits; while
  `SPRMOD=1`, `WRP0=1` means PCROP is active, so the old all-ones value could
  keep PCROP selected while trying to clear SPRMOD.
- **Option-byte writes are now truly atomic**: critical RDP/SPRMOD/WRP/BOR
  changes are sent as one CubeProgrammer `-ob` operation. Repeating `-ob`
  flags can execute separate option-byte launches, which lets `RDP=0xAA`
  reset the chip before SPRMOD/WRP are applied.
- **Bootloader option-byte mask corrected**: the bootloader sanitizer now uses
  the STM32F401 six-bit WRP0 field instead of a generic eight-bit nWRP mask.
- **Last-resort bad-option-byte recovery added**: if the legal RDP1->RDP0
  recycle still leaves `SPRMOD=1`, Recover Board now tries ST's
  `STM32_Programmer_CLI -ob unlockchip` fallback once, requires another real
  power cycle, and only reports a hardware-stuck chip if option bytes still do
  not clear.
- **Unlockchip now uses robust ST-Link attach modes**: if the default SWD
  under-reset attach reports an ambiguous `target not found` / lost-connection
  message, the tool keeps trying hardware-reset and hotplug modes before
  deciding whether to power-cycle and verify.
- **Option-byte diagnostics now use the same attach fallbacks**: `-ob displ`
  retries with hardware-reset and hotplug modes before giving up, so recovery
  does not falsely fail just because the normal SWD attach is unstable. The CLI
  recovery path also routes its option-byte writes through the shared timeout
  wrapper.
- **Post-RDP verification now prefers option bytes**: after the required power
  cycle following an RDP1->RDP0 drop, Activate/Update and Recover Board parse
  `RDP` from `-ob displ` before using any flash-read fallback. This prevents
  PCROP-blocked flash reads at RDP0 from being mistaken for still-active RDP1
  and lets the SPRMOD/WRP repair path run.
- **Initial update RDP detection now also prefers option bytes**: before
  writing firmware, Activate/Update checks `RDP` from option bytes first. A
  board already left readable at `RDP0/SPRMOD1` now goes directly into the
  PCROP repair path instead of being treated as a fresh RDP1-removal case.
- **CLI flash operations now have bounded timeouts**: the command-line tool now
  routes UID reads, RDP flash probes, flash word reads, mass erase, and flash
  write through the same timeout wrapper used by the safer option-byte paths.
  Flash/erase operations get the long 300 s timeout; probe/read operations use
  the short connect timeout.
- **Recover Board final RDP check now prefers option bytes**: after the final
  mass erase, recovery reads `RDP` from option bytes before using a flash-read
  fallback. This avoids a misleading "RDP is still active" result when the
  target is actually RDP0 but the flash read is transiently blocked or busy.
- **Malformed option-byte dumps now fall back safely**: if the desktop app or
  CLI can read option bytes but the `RDP` line is missing or unparseable, it no
  longer treats that as a clear board. It falls back to the flash-read RDP
  probe and stops if protection still appears active.
- **Desktop app flash-read probes now have bounded timeouts**: chip-family
  detection, RDP flash probes, UID reads, UID-stub reads, and single-word flash
  readback now use the short CubeProgrammer timeout. This keeps unstable
  ST-Link sessions from looking like the app is stuck.
- **SPRMOD verification now fails closed**: the desktop app and CLI no longer
  continue to `WRP0=0x3F` or flash writes unless option bytes prove
  `SPRMOD=0`. This avoids making a still-latched PCROP state worse when
  ST-Link reads are unstable.
- **Activate/Update now applies the same SPRMOD gate**: if option-byte RDP is
  missing or unreadable but a flash-read probe suggests RDP0, the tool still
  verifies SPRMOD before clearing WRP0 or writing firmware.
- **WRP0/nWRP0 compatibility fallback added**: if CubeProgrammer rejects the
  `WRP0` option-byte name, the desktop app and CLI retry with `nWRP0`. This
  helps across CubeProgrammer database variants while avoiding repeated RDP
  transitions after a reset.
- **CLI option-byte timeout now matches the desktop app**: command-line
  option-byte writes now use the documented 180 s timeout, matching the GUI.
- **PCROP repair re-arm is RDP-only**: forced recovery now writes only
  `RDP=0xBB` during temporary RDP1 re-arm. `WRP0=0x00` is applied only during
  the following RDP1->RDP0 clear, which is the legal transition for clearing
  PCROP/WRP0 bits on STM32F4.
- **Bootloader option-byte writes fail closed when SPRMOD is active**: if a
  board somehow boots with `SPRMOD=1` still latched, the bootloader no longer
  attempts BOR or RDP option-byte writes. Recover Board must repair that state.
- **Command-line flashing refuses multiple ST-Link probes**: the CLI now
  aborts before flashing if more than one ST-Link adapter is attached, matching
  the desktop app guard against writing the wrong board.
- **Update preflights license activation before touching RDP**: the desktop app
  and CLI now call `POST /api/v1/lookup-uid` before ST-Link Update. If the
  license is invalid or has no activated board, the tool stops before
  CubeProgrammer connects or an RDP1 erase can start. If multiple boards are
  registered, the operator must explicitly select the target UID before
  hardware access starts.
- **Activate refuses all RDP1-protected boards**: Activate now checks the
  license before hardware access, but still refuses to remove RDP1 even if the
  entered license has no activations. RDP1 hides the UID, so Activate cannot
  prove the connected board is blank or belongs to that license before erase.
  Use Update for an already activated board, or Recover Board for an
  intentional erase/re-provision.
- **Protected-board Update now requires operator confirmation before erase**:
  when RDP1 blocks UID reads, the desktop app shows the expected activation UID
  and UID-short, then requires typing the UID-short before dropping RDP. The
  CLI requires typing the expected UID-short, or the full UID, before it starts
  the erase. This cannot prove the physical UID before mass erase, but it
  prevents blind updates of the wrong protected board.
- **Recover Board confirmation uses OK/Cancel again**: the desktop app keeps a
  destructive-action confirmation, but no longer requires typing `RECOVER`.
- **Retired Phase-C paths now fail closed**: the visible Update button has
  used ST-Link/SWD since v1.6.0, but the old USB-C/Phase-C update and log
  worker methods still existed in the desktop app file. They now return a
  disabled-transport error immediately if an old callback ever reaches them,
  and the underlying Phase-C protocol mutators refuse BEGIN/DATA/END/log
  commands before writing any serial bytes.

---

## Tooling update — 2026-05-27

Provisioning app / CLI update for boards that already have RDP1 protection.
This is a tool-side reliability change, not a firmware behavior change.

- **Safer re-flash of protected boards**: Activate/Update now blocks for a
  physical unplug/replug power-cycle immediately after dropping RDP1, before
  any firmware write. This matches the recovery flow and avoids writing while
  the STM32F4 flash controller is still half-latched after the RDP1->RDP0
  transition.
- **PCROP/SPRMOD clear fixed for protected-board updates**: the RDP removal
  write now sends `RDP=0xAA` + `SPRMOD=0` + WRP bits together. STM32F4 only
  allows SPRMOD to clear during the RDP1->RDP0 transition, so the app no
  longer tries to clear SPRMOD afterward and no longer falsely labels normal
  boards as hardware-stuck.
- **Retry works for boards already left at RDP0/SPRMOD1**: if a previous failed
  update left the board readable but PCROP-blocked, the app now runs the legal
  RDP recycle with SPRMOD and WRP bits bundled into the RDP drop, power-cycles,
  and retries the firmware write.
- **CLI brick window reduced**: `gnss_provision.py` no longer performs a
  separate mass erase before the combined firmware write. It writes the full
  combined image in one CubeProgrammer operation, after the same RDP1
  power-cycle preparation.
- **CLI retry parity added**: if the command-line updater finds a board already
  readable but blocked by old `RDP0/SPRMOD1` option bytes, it now runs the same
  legal RDP recycle as the desktop app, power-cycles, and retries the combined
  firmware write once.
- **RDP re-arm verification added**: during the forced PCROP/SPRMOD recovery
  cycle, the app now confirms the temporary `RDP=0xBB` re-arm latched before
  issuing the `RDP=0xAA` + `SPRMOD=0` drop. If not, it stops before an invalid
  SPRMOD clear.
- **PCROP recovery hardened**: the app now verifies RDP by parsing the option
  bytes, not by reading flash, because PCROP can make flash reads look blocked
  even at RDP0.
- **Recovery wording corrected**: Recover Board unlocks, erases, and verifies
  a blank chip. It does not reinstall firmware; after recovery, run
  **Activate** or **Update** with the license key.
- **BOR recovery handling corrected**: recovery uses `BOR_LEV=3` (BOR off on
  STM32F4) during erase, then the final lock restores production
  `RDP=0xBB` + `BOR_LEV=0` in the same option-byte write.
- **Fewer false update failures**: if CubeProgrammer reports option-byte
  programming success but exits non-zero during the final lock, the app now
  treats the lock as committed instead of showing a failed flash.
- **Safer app close behavior**: the desktop app no longer kills an active
  Activate, Update, or Recover operation when the window is closed. It shows a
  warning and keeps the operation active until flash/erase, option-byte writes,
  erase settling, and power-cycle prompts are finished.
- **Longer CubeProgrammer timeouts**: flash write and mass-erase operations now
  allow up to 300 seconds, and option-byte writes allow up to 180 seconds, so
  slower PCs or marginal USB hubs are less likely to interrupt a valid update.
- **Flash readback before RDP1**: after the combined firmware write, the app
  reads back sentinel words from the bootloader, application, and metadata
  regions. If any check fails, it stops before re-locking RDP1 so the board
  stays readable for another attempt.
- **Legacy UART update blocked**: `gnss-provision update --uart` is hidden from
  help and now exits before opening the port or flashing. Updates are supported
  only through ST-Link/SWD or the desktop app Update button.
- **ST-Link USB communication reset handled during RDP removal**: if
  CubeProgrammer reports `DEV_USB_COMM_ERR` while dropping `RDP=0xAA`, the app
  now continues to the mandatory unplug/replug and verifies whether RDP really
  cleared. This avoids a false failure before firmware writing starts.
- **More robust first ST-Link connection**: if the normal SWD connection fails,
  the desktop app retries with hardware-reset and hotplug attach modes,
  including a lower SWD speed, and prints the useful CubeProgrammer diagnostics.
  If all modes still fail, the board is not reachable over SWD and the remaining
  checks are wiring, power, reset, probe, or MCU hardware.
- **Clearer reset guidance on connection failure**: when all ST-Link attach
  modes fail, the app and CLI now suggest wiring NRST/RST to the ST-Link reset
  pin or holding RESET during the start of Update/Recover. The CLI uses the
  same reset/hotplug attach fallbacks as the app.
- **Visible desktop app version**: the app shows its own version in the window
  and startup log, separate from the firmware version list.
- **Connection progress is no longer silent**: the app logs each SWD attach
  mode while it is trying to connect, and each attach probe is limited to 10
  seconds.
- **Faster ST-Link adapter check**: the app now lists ST-Link adapters without
  trying to connect to the target first, so a bad board cannot stall before the
  visible attach-mode logs start.

---

## v1.6.17 — 2026-05-26

Firmware-only DR lock enforcement update. This build keeps the v1.6.16 u-blox
SNR recovery behavior and tightens DR1 timing semantics.

### Firmware

- **`DR_LOCK_MS` is now a true minimum DR1 time**: if `DR1_MAXMS` is also set
  and expires before the DR lock window, the firmware stays in DR1 until
  `DR_LOCK_MS` has elapsed.
- **Rejoin timing waits for the lock to expire**: the rejoin stability timer and
  GNSS blend do not start while `DR_LOCK_MS` is active.
- **Status LED blink timing is more stable**: Mission Planner parameter-list
  downloads no longer stall the main loop, and the DR1 LED pattern now follows
  the same `DR=` state shown in logs.

---

## v1.6.16 — 2026-05-21

Dev/test u-blox SNR recovery timing update. At release time, v1.6.15 remained
the stable server default; v1.6.16 is selectable only when you explicitly choose the
`v1.6.16 (dev)` firmware entry in the provisioning app. No wiring or tuning
change is required.

### Provisioning app / server

- **Dev firmware is clearly separated from stable**: the firmware dropdown
  keeps `v1.6.15 (stable default)` as the normal default and shows
  `v1.6.16 (dev)` at the bottom of the list.
- **Selecting the dev build flashes the right image**: the server and updated
  app carry separate display and raw-version metadata, so `v1.6.16 (dev)` is
  shown to the operator but the board receives raw firmware version `1.6.16`.

### Firmware

- **Faster recovery when NAV-SAT is disabled after boot**: field logs showed
  healthy `NAV-PVT`/fix data and `SATS=29`, but `NAV-SAT` stopped after a small
  FC GPS back-channel write and `SNR=NA` persisted until the recovery path
  re-enabled NAV-SAT. The stale-SNR timer now starts as soon as SNR goes stale,
  while still waiting for NAV-SAT itself to be stale before rewriting receiver
  config. This keeps the v1.6.15 stream-aware behavior but reduces the typical
  recovery delay from about two stale windows to one.
- **SNR guard remains false-trip safe**: `SNR_EN=1` still cannot trigger DR1
  from `SNR=NA` or stale SNR data. Stale SNR is ignored by the direct SNR guard
  and by spoof-confidence scoring.

---

## v1.6.15 — 2026-05-21

Firmware-only u-blox compatibility and recovery release. This is the public
follow-up to v1.6.12; intermediate 1.6.13/1.6.14 test builds were folded into
this release and are not listed as selectable server firmware versions.

### Firmware

- **u-blox no-fix diagnostics**: while `SATS=0` or no position fix is valid,
  the firmware polls `UBX-MON-RF`, `UBX-SEC-SIG`, and `UBX-CFG-GNSS` and logs
  `ubxpvt ...`, `ubxrf ...`, `ubxsig ...`, and `ubxgnss ...` lines in Mission
  Planner. These show PVT fix flags, antenna/RF state, explicit
  jamming/spoofing state when supported, and enabled GNSS constellation
  configuration.
- **Manual u-blox reset command**: new virtual parameter `UBX_RESET` appears in
  Mission Planner but is not saved to flash. Set `1` for hot start, `2` for
  cold start, or `3` to clear saved u-blox BBR/Flash configuration, reload
  defaults, reset the receiver, and let the STM32 reinitialize GNSS.
- **No automatic factory reset**: destructive receiver config clearing only
  happens from a directed `PARAM_SET` command to the STM32 filter.
- **Clearer no-fix logs**: the periodic `fix=...` field now reports only the
  age of a valid position fix. A receiver that is alive but has no fix will show
  stale `fix=...` and fresh `nav=...`.
- **u-blox SNR recovery is now stream-aware**: the firmware reissues NAV-SAT
  configuration only when NAV-SAT frames are missing or stale. If NAV-SAT is
  arriving with zero usable C/N0, the receiver is acquiring or has no usable RF,
  so the firmware logs diagnostics but does not keep rewriting configuration.
- **Boot-time VALSET profile narrowed**: UART2 NAV-SAT is no longer persisted at
  boot. UART2 remains part of the RAM-only recovery path for boards where
  NAV-SAT is genuinely absent from the monitored link.

---

## v1.6.12 — 2026-05-21

Firmware-only receiver compatibility release. Existing boards update in place
through the standard ST-Link provisioning flow.

### Firmware

- **F9P NAV-SAT / SNR fix**: the UBX parser now accepts larger `NAV-SAT`
  payloads from F9P-class receivers with many satellites in view. This fixes
  Mission Planner logs where `SATS` and fix age were healthy but `SNR=NA`
  persisted.
- **Stale-SNR diagnostics**: if u-blox SNR goes stale, the periodic messages add
  a compact `snrdbg` line so support can see whether `NAV-SAT` is absent,
  malformed/checksum-failing, too large, or present with zero usable C/N0
  values.
- **Stale-SNR recovery**: the recovery command now re-enables `NAV-SAT` through
  both legacy `CFG-MSG` and `CFG-VALSET` on UART1/UART2, covering F9/F10 carrier
  boards where the active receiver port is not UART1.
- **Stale SNR skipped in confidence scoring**: SNR, pseudorange residual, and
  SNR-correlation confidence inputs now use the same freshness window as the
  Mission Planner `SNR=...` status line.

---

## v1.6.11 — 2026-05-15

Firmware-only diagnostic release. Existing boards update in place through the
standard ST-Link provisioning flow; no wiring, tuning, or provisioning-app
change is required.

### Firmware

- **Raw FC GPS forwarding bypass** (`FCGPS_FWD=1`): when enabled, the filter
  forces the FC GPS UART on and forwards receiver traffic to the flight
  controller before DR1 spoofing protection, boot north gate, hemisphere fence,
  UM980 config holdoff, or no-fix recovery reset logic can block it. Use this
  only for bench and wiring diagnostics; keep `FCGPS_FWD=0` for protected
  flight.

---

## v1.6.3 — 2026-04-14

Stability and privacy release on top of v1.6.2. No new tuning parameters, no wiring changes, no in-field action required beyond running the provisioning tool.

### Firmware

- **NMEA satellite-count safety clamp**: the NMEA GGA parser now caps the satellites-in-view field at 255 before passing it on. Guards against corrupt or spec-violating sentences from multi-constellation receivers with unusually high sat counts.
- **Watchdog margin during receiver config**: every u-blox `CFG-*` write-and-wait-for-ACK step now pats the independent watchdog on entry. The 20-step boot-time configuration burst no longer nibbles away at the watchdog budget on slow-responding receivers.
- **Spoofing-event logger robustness**: the on-board event writer now reports which slot it used (or explicitly signals "skipped"), so a debounced duplicate-write cannot corrupt unrelated events when the board exits dead-reckoning and backfills the trigger duration.

### Bootloader

- **Build-time anti-rollback safety net**: the bootloader now fails the build outright if the anti-rollback floor is missing from the build configuration, instead of silently defaulting to zero (which would have accepted any firmware version). Bit-field overflow in version encoding is likewise caught at build time.
- **Staged-update resumability policy documented**: bounded power-fail retry behaviour is now an explicit invariant (documented, not changed). No functional change for operators; matters only to developers pulling the source.

### Server

- **License key no longer in URL**: the licence-status lookup has a new `POST /api/v1/license-status` variant that takes the key in the request body. The landing-page self-service form uses the new path so keys stop appearing in nginx access logs. The legacy `GET ?key=…` form still works for older clients.
- **Audit IPs are XFF-aware**: the retention-sweep and PII-erase admin actions now record the real client IP via `X-Forwarded-For`, not the nginx reverse-proxy loopback address. Audit rows written before this release remain as-is.
- **Pin an older firmware version on activation**: `/api/v1/activate` now accepts an optional `version` field. The provisioning tool uses this when you've selected something other than the stable default in the version dropdown.

### Tools — AirDroper GNSS Filter app

- **Clean shutdown during provisioning**: closing the app window while an ST-Link write is in progress now kills the child `STM32_Programmer_CLI` cleanly, instead of leaving orphaned processes holding the SWD port.
- **Multi-adapter pre-check on Activate**: the Activate button now refuses to start if more than one ST-Link V2 is plugged in, with the same "unplug the others" dialog that Recovery has used since v1.6.0. Prevents the wrong board being re-provisioned when a lab bench has several adapters attached.
- **Version-pinned activations**: when you pick a version other than the stable default in the firmware dropdown, Activate now sends that choice to the server (matches what Update already did).

### Docs

- **Recovery guide** ([04_recovery.md](https://github.com/AirdroperUA/gnss-filter-user-docs/blob/main/04_recovery.md)): added gate-failure diagnostics and recovery recipes for anti-rollback reject, UID-binding reject, RDP-write-failure mid-provision, and hard-brick escalation. Developer-only reference; normal field use is unchanged.

---

## v1.6.2 — 2026-04-14

Receiver-compatibility and provisioning-resilience release. Completes the USB-C → ST-Link transition from v1.6.0.

### Firmware

- **u-blox F10 / M10 NAV-SAT auto-config**: newer u-blox generations (F10 series, M10 series) use the `CFG-VALSET` configuration interface and do not always respond to the legacy per-message enable. The filter now sends a `CFG-VALSET` profile at boot that enables `NAV-SAT` on the correct port at the correct rate. Spoofing detection signals that rely on per-satellite SNR and carrier-to-noise analysis now work out-of-the-box on F10/M10 receivers without a u-center pre-config step. No effect on M8/M9 or UM980.

### Tools / Provisioning

- **Provisioning recovers from write-protected sectors**: if flash erase fails because option-byte write-protection (`nWRP`) is active on the previous image, the provisioning tool now clears the protection and retries automatically. Previously these boards required a manual trip through STM32CubeProgrammer.
- **Power-cycle prompt is now blocking**: when the board needs a hard power-cycle mid-provision (e.g. after an option-byte change), the dialog now blocks the flow until you confirm the cycle completed. Prevents the race where the next write started against a half-re-enumerated target.
- **Bootloader USB-C CDC fully disabled**: `BOOTLOADER_PHASEC_ENABLE=0` is now permanent. Pins `PA11/PA12` are unconditionally available to the flight-controller GPS UART (USART6). This change was announced in v1.6.0; v1.6.2 removes the last code paths.
- **USB-C row removed from the app**: the old "(USB-C auto-detect)" port selector is gone. Activate, Update, and Recover all use the ST-Link V2 SWD path.

### Docs

- User-facing guides re-read and trimmed for the ST-Link-only flow. The [Self-Install Guide](10_self_install.md) and the firmware-update FAQ no longer mention the USB-C path.

---

## v1.6.1 — 2026-04-13

Reliability release. Patches three independent issues that surfaced in the field after v1.6.0. No configuration changes.

### Firmware

- **Bootloader → application handoff hardened**: on some boards, a firmware-validation failure followed by a retry could leave the application starting with stale NVIC interrupt state, with interrupts masked (`PRIMASK=1`), or with the `AHB2ENR` clock-enable register still configured for the bootloader's USB peripheral — symptoms were an instantly-frozen board with the status LED stuck off after the bootloader finished. The handoff now explicitly clears NVIC pending/enable bits, resets `AHB2ENR`, clears `PRIMASK` so interrupts are enabled when the app starts, and clears any latched fault flags.
- **Diagnostic GPS forwarding restored** (`FCGPS_FWD=1`): when the parameter `FCGPS_FWD` is set to `1`, the filter now forces the FC GPS UART on, raw-forwards the GPS stream to the flight controller, and bypasses DR1, the boot north gate, and the hemisphere fence. Intended for **diagnostic bench use only**; it defeats the whole point of the filter in flight. Default stays at `0`.

### Tools — AirDroper GNSS Filter app

- **Ctrl+V paste works under Cyrillic keyboard layouts**: the license-key field used to ignore Ctrl+V when the active keyboard layout was Ukrainian or Russian (the "V" keysym under those layouts is not `v`). The binding now triggers on the physical keycode, so paste works regardless of the currently-selected layout.

---

## v1.6.0 — 2026-04-11

Security and reliability hardening release. Four parallel deep-review waves (R19–R22) across firmware, server, and bootloader. **No configuration changes — existing boards upgrade in place and keep working. No new tuning parameters, no wiring changes.**

### Firmware

- **Spoof-guard arming timer hardened**: the "stable fix for N seconds before arming" window is now measured in wall-clock time. Fixes an edge case where a stale GPS fix could arm the guard prematurely.
- **MAVLink parameter-dump latency insurance**: dumping all ~62 tuning parameters to a GCS (e.g. Mission Planner) no longer briefly starves the spoof guard — the dump now yields to the GNSS parser and watchdog every 8 parameters.
- **Post-rejoin guard rearm**: after exiting DR1 (dead-reckoning) back to normal tracking, the spoof guard now fully re-qualifies its arming window on every cycle instead of carrying the previous armed state forward. No user-visible behaviour change in normal operation — this is a semantic cleanup so the arming invariant always holds.
- **Stricter GCS parameter authentication**: `PARAM_SET` messages are now rejected if the sender's MAVLink system ID doesn't match the expected autopilot. If you run a GCS with a non-standard `SYSID_MYGCS`, verify it matches your autopilot before upgrading.
- **u-blox coordinate sanity guard**: guards against NaN / out-of-range latitude or longitude from corrupt NAV-PVT frames.
- **UM980 autobaud timing**: watchdog reload during the receiver autobaud probe. Fixes rare boot stalls on slow-responding UM980 units.
- **Anti-reverse-engineering build flags**: stripped symbols, link-time optimization, dead-code elimination, stack protector — makes the shipped binary harder to reverse-engineer.

### Server / Tools

- **Exact-pinned Python dependencies**: all server dependencies now pinned with `==` instead of `~=`. Eliminates patch-level drift between deploys.
- **License keys masked in audit logs**: the `gnss-license` audit log now stores only a fingerprint (`first4...last4#sha256[:12]`) instead of the full key. Existing logs are unaffected; new entries use the fingerprint format.
- **DNS-rebind hardening**: webhook challenge endpoint now resolves and validates target hostnames server-side.
- **Rate-limiter cleanup**: fixed a memory-usage edge case in the per-IP rate limiter where 429-rejected IPs could leave empty entries behind.
- **HTTPS enforcement on /health and /api**: direct HTTP traffic now returns 403 instead of falling through to the app layer.
- **Device registration fix**: tightened `require_owner` on the `/register-key` endpoint (body-parsing bug fix).

### Bootloader

- **USB-C firmware updates removed**: the bootloader no longer enumerates as a USB CDC device. Pins PA11/PA12 are reserved for flight-controller GPS UART (USART6). All firmware updates, recovery, and activation now use the **ST-Link V2 SWD** path only.
- Internal parity updates from the R19 hardening wave; anti-rollback floor stays at v1.5.5 so existing field units can accept this release.

### Tools

- **AirDroper GNSS Filter app**: the "(USB-C auto-detect)" port option and the **Download Logs** button have been removed. Activate, Update, and Recover all run through the ST-Link V2 wired to the 4-pin SWD header (3V3, GND, A14/SWCLK, A13/SWDIO).

### Logging

- **Log retrieval moved to the flight controller SD card**: spoofing detections are now emitted as MAVLink **STATUSTEXT** and **NAMED_VALUE_INT** messages and recorded by ArduPilot as `MSG` / `NVLI` dataflash entries in the `.bin` log on the FC's SD card. The on-board event log and its USB-based download flow no longer exist.

### Docs

- Rewrote the "Firmware updates" and "Spoofing event logs" sections in the [Self-Install Guide](#self-install) for the ST-Link-only update path and SD-card log retrieval.
- Updated the FAQ entries on firmware updates and log download to match.

---

## v1.5.5 — 2026-04-05

### Firmware

- **Confidence scoring**: new `DR_CONF` (0–100) from 8 weighted detection signals — SNR anomalies, pseudorange residuals, SNR temporal correlation, heading reversals, GDOP changes, GPS time drift, velocity-position mismatch, clock bias jump. Score adapts automatically when signals are unavailable (e.g. UM980 uses ~5 of 8).
- **Heading reversal detection**: triggers DR1 on sudden course flip inconsistent with IMU.
- **GPS time anomaly detection**: triggers DR1 when GPS time jumps unexpectedly.
- **Geo-fence** (`FENCE_RAD`): triggers DR1 if position drifts beyond a radius from the first fix (default 600 km, max 2000 km). Catches slow-drift spoofing.
- **South-hemisphere hard block**: instant DR1 when latitude goes below 0°. Now configurable via `HEMI_EN` parameter.
- **Clock bias jump detection** (u-blox only): uses NAV-CLOCK to detect receiver clock manipulation.
- **Velocity-position mismatch** (u-blox only): cross-checks reported velocity against position delta.
- **DR1 max duration** (`DR1_MAXMS`): forces exit from DR1 after a configurable timeout. Useful for long-range missions.
- **USB-C firmware updates**: connect USB-C cable, press RESET — no extra hardware needed after initial flash.
- **USB-C log download**: spoofing logs can be downloaded over USB-C directly.
- **App boot fix**: corrected application vector table at 0x0800C000.
- **RDP1 re-enabled**: readout protection restored after v1.5.4 debugging.

### Server / Tools

- **SpoofEvent v2**: richer event format with confidence score and trigger breakdown.
- **KML/GPX export**: download spoofing events as KML (Google Earth) or GPX from the cloud dashboard.
- **Fleet anomaly detection**: dashboard flags unusual patterns across multiple boards.
- **Provisioning tool**: USB-C auto-detect mode — select "(USB-C auto-detect)" as port.

### Docs

- Added confidence score documentation with signal weight table.
- Added u-blox vs UM980 feature coverage table.
- Documented new DR1 triggers (heading, time, geo-fence, clock bias, velocity-position).
- Added `DR1_MAXMS`, `FENCE_RAD`, `HEMI_EN` to tuning manual.

---

## v1.5.4 — 2026-04-04

### Firmware

- **Critical fix**: compiler constant-folded key sentinel checks, causing provisioning validation to always pass. Fixed with volatile barriers.
- **PLL init reorder**: moved PLL clock init before app validation for faster boot.
- **Detailed error codes**: added BEGIN BAD_METADATA diagnostic codes for easier debugging.

---

## v1.5.3 — 2026-04-04

### Firmware

- **Anti-clone UID binding**: firmware is now cryptographically locked to each board's unique hardware ID. Copying firmware to another board renders it non-functional.
- **Security hardening**: additional integrity checks in bootloader.

### Server / Tools

- **Landing page and docs site**: launched gps.airdroper.org with full documentation.
- **Desktop app (.exe)**: AirDroper GNSS Filter provisioning tool with GUI.
- **Docs version selector**: browse documentation for specific firmware versions.

---

## v1.5.0 — 2026-04-03

### Firmware

- **SpoofAnalytics event logging**: spoofing events are stored in on-board flash with timestamp, position, trigger reason, satellite count, and SNR data.
- **Log download**: events can be uploaded to the cloud dashboard via USB-UART or USB-C.

### Server

- **Cloud dashboard** (gps.airdroper.org/dashboard): web interface for viewing spoofing events, flight tracks, and board status.
- **EW interference map** (gps.airdroper.org/ew-map): live global GNSS interference map with ADS-B, marine AIS, air raid alerts, 61 known EW zones, crowdsourced reports, route risk assessment, Telegram alerts, and predictive model.
- **License server**: automated provisioning and firmware distribution.
- **Server hardening**: rate limiting, input validation, HTTPS enforcement.
