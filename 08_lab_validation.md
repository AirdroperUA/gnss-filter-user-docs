# Anti-Spoof Lab Validation (Defensive Only)

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

This document is focused only on defensive validation of spoofing resilience.

## 1) Scope and Boundaries

- Purpose: verify that the STM32 filter protects FC navigation when GNSS data becomes suspect.
- Allowed use: legal, authorized, isolated lab environments only.
- Not included: attack-enablement instructions (device setup, transmission methods, or procedures to spoof GNSS receivers).

## 2) Video Reference

- Reference video: https://www.youtube.com/watch?v=EFvWup8oCCE
- Treat the video as a demonstration of defensive validation workflow.
- Use it together with this checklist-driven procedure and saved logs.

## 3) Defensive Validation Goals

1. Confirm normal operation in DR0 when GNSS is healthy.
2. Confirm transition to DR1 when spoof-like anomalies appear.
3. Confirm GNSS forwarding is blocked while DR1 is active.
4. Confirm controlled return to DR0 only after stability/rejoin conditions.
5. Confirm no oscillation between DR0 and DR1 under stable inputs.

For WeAct H743 DroneCAN, "GNSS forwarding is blocked" means DroneCAN
`Fix2/Auxiliary` publications stop while `NodeStatus` remains online. Use the
onboard screen and DroneCAN/SLCAN tooling in addition to flight-controller logs.

## 4) Recommended Lab Environment

- RF-isolated test area managed by qualified personnel.
- No radiating tests near live aircraft, real runways, or public operations.
- If your authorized RF lab uses a dedicated SDR source platform, a common hardware set is **HackRF One + PortaPack H2**.
- Full logging enabled:
  - filter status text,
  - FC messages,
  - timestamped test notes for each run.

Note: this document does not include setup or operation steps for HackRF/PortaPack.

## 5) Test Scenarios (Spoofing-Relevant)

Use controlled, authorized anomaly sources and verify expected filter behavior:

1. **Large position discontinuity**
   - Expected with `FCGPS_FWD=0`: DR1 entry, GNSS forwarding blocked.
   - Expected on H743 DroneCAN: `PUB BLK DR1`, no new `Fix2/Auxiliary`, node still online.
2. **Unrealistic implied speed**
   - Expected: DR1 entry and sustained protection state.
3. **Altitude anomaly pattern**
   - Expected: DR1 entry when altitude consistency checks fail.
4. **SNR-pattern anomaly (if enabled in your profile)**
   - Expected: DR1 entry after hold-time logic.
5. **Recovery sequence**
   - Expected: DR0 only after quality/timing gates are satisfied.

## 6) What to Verify in Logs

- DR state changes (`DR=0` -> `DR=1` -> `DR=0`).
- GNSS health trend before and during anomaly windows (`age`, `SATS`, `SNR`, DR state).
- Presence of trigger messages describing why DR1 was entered.
- Rejoin messages when returning to DR0.
- No unexpected FC navigation jumps during DR1.

H743 DroneCAN `v0.2.0+` emits filter MAVLink `STATUSTEXT` and `NAMED_VALUE`
through S2/index `1` when that virtual port is configured. Verify those records
along with:

- screen state changes (`FILTER OK/WARN/NO OK`, `WHY`, `PUB`)
- DroneCAN node ID `42` remains visible
- `NodeStatus` health changes to warning for spoof/fault DR1 reasons or an
  enabled I2C sensor that remains missing/stale after startup grace
- `Fix2/Auxiliary` stop during DR1 and resume after rejoin
- ArduPilot GPS instance reports loss/recovery without accepting suspect fixes
- camera S1/index `0` and filter S2/index `1` remain active in DR1

## 7) Common Validation Failures

- **DR1 never triggers during anomaly**
  - Guard thresholds too permissive or anomaly not strong enough for configured logic.
- **DR1 triggers too often**
  - Overly strict profile, startup instability, or poor baseline GNSS conditions.
- **No clean return to DR0**
  - Rejoin quality/timing conditions not satisfied.
- **Test results are inconsistent**
  - Incomplete environment control, missing logs, or mixed test setups between runs.

## 8) Pass Criteria Before Flight

All must be true:

1. DR1 triggers on spoof-like anomalies in repeated runs.
2. GNSS forwarding remains blocked during DR1 with `FCGPS_FWD=0`.
3. DR0 recovery is stable and repeatable.
4. FC behavior stays controlled (no unsafe navigation jumps).
5. Logs and test records are complete for review.

For H743 DroneCAN, replace item 2 with: DroneCAN `Fix2/Auxiliary` remain
suppressed during DR1 while `NodeStatus` stays online.

## 9) Release-Qualification Evidence

Passing unit tests and compiling firmware are necessary, but they do not
qualify a build for flight. Create one evidence record for every candidate and
do not promote it to the production catalog until every applicable row passes.

Record the firmware SHA-256, semantic version, build name, board revision,
receiver/firmware, flight controller/firmware, enabled sensors, test date,
operator, configuration export, and links to raw filter, receiver, CAN, and FC
logs. A failure followed by a code or configuration change requires a complete
rerun; do not reuse results from the superseded candidate.

Required hardware-in-the-loop coverage:

- Exact-artifact normal-flight envelope: flash the exact binary whose SHA-256
  is recorded in this evidence package. Exercise takeoff and the first 60
  seconds of climb; sustained maximum-rate climb, descent, and dive; aggressive
  turns, steep banks, and course-reversal geometry; and straight cruise in
  controlled/safely simulated wind cases of at least 15 m/s and 30 m/s. Inject
  short multipath, fix, SNR, and EKF glitches. Assert there is no unintended
  DR1 throughout the clean-flight envelope and that any intentional DR1 test
  follows the expected rejoin sequence.
- Real receiver traffic: u-blox NAV-PVT/NAV-SAT, the deployed Unicore/UM980
  GGA/RMC/AGRICA profile, and Septentrio Mosaic SBF. The STM32 must parse
  GGA/RMC, forward but not parse AGRICA, and show `SNR=NA` without optional
  GSV. Run GSV as a separate optional-evidence case; its absence must not block
  recovery. Confirm malformed, truncated, delayed, and interleaved frames break
  detector continuity instead of satisfying a hold timer.
- H743 parked recovery: with the FC positively disarmed and stationary, prove a
  passive receiver can release without GSV when every available evidence row
  is non-FAIL, GNSS time passes, and fresh finite nonnegative receiver speed is
  at most 4 m/s in the same location epoch (both age and skew at most 1500 ms).
  Stale/mismatched speed, speed above 4 m/s, or any explicit FAIL must prevent
  release. Also exercise the unchanged airborne witness quorum and identify
  `EVM`, `EVF`, and `EVPg` separately.
- FC-version and dual-link gates: start with no `AUTOPILOT_VERSION`, then an
  ArduPilot version older than 4.6.1, then a supported version. Unknown and old
  versions must suppress `Fix2/Auxiliary` immediately; verify the explicit
  capability request, the 15-second warning/hard-processing delay, and the
  documented messages. With Mission Planner 1.3.83, boot and reconnect the
  secondary H743 USB link with DTR deasserted. Under ordinary and `SP_*` load,
  prove USB/COMM2 and FC/S2/COMM0 each maintain an independent contiguous
  MAVLink sequence.
- Coordinate containment: test `LOG_LOC=0` and `1`. Raw coordinates may appear
  only in true-DR0 periodic status with `LOG_LOC=1`; trip/transition text and
  every DR1, synthetic, or blend status stay redacted. Verify `SP_*` remains on
  direct USB only, while simultaneous raw CAN contains no DR1 `Fix2`,
  `Auxiliary`, `SP_*`, or coordinate-bearing filter status.
- Fuel provenance and degraded operation: exercise valid V2 records across
  warm and POR/PDR reset flags, legacy V1, corrupt/missing records under every
  reset flag, and repeated resets. Every invalid or missing record must produce
  TOTAL LOST; there is no cold-boot/fresh-tank shortcut. A normal power-on with
  no valid retained record must stop every ICE Status packet until fresh
  stopped-engine quorum (disarmed + valid zero RPM + closed throttle) permits
  an operator to rewrite `FUEL_CAPG`, even when its numerical value is
  unchanged; the FC EFI backend must age stale/unhealthy meanwhile. Prove that
  disarmed alone, stale/missing RPM, nonzero RPM, stale/missing throttle, and
  open throttle each reject the reset and emit `FUEL_CAPG blocked: engine not confirmed stopped`.
  Repeat the quorum matrix for `FUEL_DENS` and require
  `FUEL_DENS blocked: engine not confirmed stopped` on every rejected write.
  Every boot must set the
  engine-may-be-running latch, and only that same fresh three-way evidence may
  clear it; the parameter write itself must not be used as stop evidence.
  A valid restore must add exactly the fixed 25-second rated-power reset-gap
  charge, covering up to 2 s of save staleness, the roughly 11.5 s longest
  UM980 setup path, other startup overhead, and margin; H743 has no Phase-C boot
  wait. Treat this as a bounded conservative charge, not proof of exact
  consumption, and verify that
  elapsed setup time after early backup initialization is charged rather than
  dropped. After a known V2 restore, inspect retained storage and prove the
  firmware durably writes the same numeric state with TOTAL_LOST provenance
  before risky setup. Inject resets during setup, during the first update, and
  during the magic-last known commit: every interrupted path must reboot LOST
  or invalid, suppress all EFI packets, and require stopped-quorum
  `FUEL_CAPG`. Let one first update finish and prove the 25-second charge plus
  the first measured interval are both integrated before the updated record is
  committed known; only a later reset may restore that charged known record.
  Separately, restore a valid record, issue an accepted `FUEL_CAPG` reset before
  the first fuel update, and prove the pending 25-second charge is cancelled so
  it cannot be applied to the newly established total. Change the numerical
  `FUEL_CAPG` value and prove TOTAL LOST is written before the runtime
  assignment, all ICE Status remains suppressed after the accepted-write text,
  and only a successful asynchronous journal completion makes the zero total
  known. Inject journal start, program, verify, and timeout failures: every
  `Tune save failed` path must stay LOST, while a later successful `Tune saved`
  completion may resume EFI. With a valid V2 backup record present, separately
  erase, corrupt, and leave the H743 tune journal without any valid record;
  every case must invalidate the surviving numeric total because capacity,
  density, and model provenance is unavailable. Attempt factory reset with
  failures before flash start and during flash, and prove the durable LOST
  marker precedes the first possible flash operation and may conservatively
  remain after a failed attempt.
  Change `FUEL_DENS` under valid stopped-engine quorum and prove the LOST marker
  precedes runtime assignment, any older CAPG commit intent is cancelled, and
  no EFI packet is sent. Before density persistence completes, every capacity
  attempt must be rejected with `FUEL_CAPG blocked: wait for FUEL_DENS save`.
  Inject density-save failure and prove the block and TOTAL LOST both remain;
  after verified `Tune saved`, prove the pending-density latch clears while EFI
  stays silent. Only a **subsequent** stopped-quorum `FUEL_CAPG` write may
  establish a fresh zero under the new density. Density-save success alone must
  not resume EFI or allow cumulative FC-visible volume to move backwards. Also
  prove fuel burn
  continues through total FC-telemetry loss and the FC-version block, charging
  rated power when RPM is missing.
- Phase-C fuel safety: **never perform Phase-C maintenance with the engine
  running**. Emulate the running inputs on a safe bench and prove a connected
  maintenance session can exceed the fixed 25-second budget; it must not be
  presented as completely accounted fuel burn.
- Operator labels: induce reason 15 and verify Mission Planner shows
  `PARKED_MOVE`/`PARKED MOVE` and the board screen shows `PARKED`.
- Navigation boundaries: impossible altitude, 2D-fix altitude downgrade,
  receiver/session reset followed by position without status, full UTC date
  rollover, cached UTC frames, short SNR bursts, clean SNR while no-fix, and
  missed/corrupt SEC-SIG polls.
- DroneCAN/FDCAN faults: missing ACK, bus-off, dominant bus, cable reconnect,
  failed peripheral stop/start, saturated bus, tunnel traffic, and a node-ID
  collision. The node must recover or fail closed with a visible fault; it must
  never silently publish suspect fixes.
- Sensor faults: stuck SDA and SCL, missing external pull-ups, disconnect and
  reconnect while running, supported/unsupported device identification,
  MS4525 pressure polarity, and magnetometer orientation against a physical
  reference.
- Reset and power faults: prove the runtime watchdog deadline, force flash-busy
  timeout/error paths, and interrupt power at each tune-journal write phase.
  The next boot must select a complete, CRC-valid record or defaults.
- Protected update: exercise actual RDP1 hardware through ST-Link and ROM DFU.
  A network, signature, target, version, UID, or bundle-validation failure must
  occur before erase. After a successful protected update, re-export and verify
  parameters and complete the commissioning checklist because mass erase
  destroys saved tuning.
- Secure boot: reject a modified app, modified metadata, rollback image, wrong
  target, and an app copied to a different MCU UID. Confirm direct PlatformIO
  upload of a phase-B payload is refused and that provisioning installs the
  bootloader, UID-bound app, and matching signed metadata as one validated set.
- Remote operator waiver: released targets must compile with
  `FILTER_REMOTE_OPERATOR_WAIVER_ENABLE=0`. Send forged and replayed
  `MAV_CMD_USER_1` waiver commands and verify they cannot change recovery state
  or bypass the independent-evidence quorum. A lab-only opt-in build must treat
  that command and its public magic value as unauthenticated and may enable it
  only behind a separately authenticated transport.

Archive the signed checklist with the release artifacts. Any unexecuted row is
an explicit release blocker, not an assumed pass.
