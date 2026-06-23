# Changelog

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

All notable firmware and tool changes are documented here.

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
