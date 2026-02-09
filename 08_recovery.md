# Recovery Runbook (One Page)

Use this when update/boot fails and the board does not start the app.

## Symptoms

- No normal filter heartbeat/status messages.
- Device appears powered but stuck.
- After phase-B flash, app does not boot.

## Quick Diagnosis

1. Check wiring and power first (5V, GND, USB cable).
2. Open STM32CubeProgrammer and verify MCU is detected.
3. Read first flash bytes at:
   - `0x08000000` (bootloader vectors)
   - `0x08007C00` (metadata)
   - `0x08008000` (app vectors)

If metadata/app addresses are empty or corrupted, reflash full phase-B set.

## Full Recovery Flash Order (recommended)

1. Flash bootloader:
   - binary: `firmware.bin` from `blackpill_f401cc_phaseb_bootloader`
   - address: `0x08000000`
2. Flash app:
   - binary: `firmware.bin` from `blackpill_f401cc_phaseb_app`
   - address: `0x08008000`
3. Flash signed metadata:
   - binary: `boot_meta.bin`
   - address: `0x08007C00`
4. Reset board and confirm app starts.

## CubeProgrammer CLI examples (Windows)

```powershell
STM32_Programmer_CLI.exe -c port=USB1 -w bootloader.bin 0x08000000 -v
STM32_Programmer_CLI.exe -c port=USB1 -w app.bin        0x08008000 -v
STM32_Programmer_CLI.exe -c port=USB1 -w boot_meta.bin  0x08007C00 -v -rst
```

## If anti-rollback rejects image

- Bootloader compares `app_version` from metadata against `BOOTLOADER_MIN_APP_VERSION`.
- If image is older than floor, it will never boot.

Fix options:

1. Flash a newer signed app/metadata with version >= floor.
2. Rebuild/flash bootloader with lower floor (only if you intentionally need rollback).

## Safe fallback path

If phase-B recovery is blocked in field, flash stable phase-A app at `0x08000000`
(`blackpill_f401cc` environment) to restore operation quickly, then re-stage phase-B later.

## Preventive checks before each release

- Verify bootloader public key matches signing private key.
- Verify `boot_meta.bin` generated from exact app binary being flashed.
- Keep one known-good release artifact set archived:
  - `bootloader.bin`, `app.bin`, `boot_meta.bin`, `release.json`.
