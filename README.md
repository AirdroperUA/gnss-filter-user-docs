# User Documentation

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

Ukrainian translation set: `docs/user/uk/README.md`.

Important: STM32 filter parameters are changed in Mission Planner:
- `Config/Tuning` -> `Full Parameter List`
- choose STM32 system (`SYSID 42`)
- `Refresh Params` -> edit value -> `Write Params`
- on a busy MAVLink link, a write may need 1-2 attempts; always `Refresh Params` to confirm

Boards for normal flight use are expected to ship with a normal build already installed.

Reboot is not required after every parameter write.
- `GNSS_TYPE` and `UBX_BAUD` require STM32 reboot (`NRST` or power cycle) to apply.
- Most other parameters apply immediately.

1. `01_device_overview.md` - high-level device operation and trigger examples.
2. `02_wiring.md` - physical wiring for STM32, GNSS receiver, and FC.
3. `03_wiring_debug.md` - diagnose GNSS/GPS/MAVLink wiring issues.
4. `04_setup_and_flash.md` - setup and FC serial configuration.
5. `05_operation.md` - runtime behavior (DR0/DR1, GNSS forwarding, event pulse).
6. `06_tuning.md` - live tuning parameters and Mission Planner workflow.
7. `07_cheat_sheet.md` - one-page quick reference for field checks and actions.
8. `08_lab_validation.md` - safe lab validation workflow before real flights.
9. `09_receiver_config.md` - GNSS receiver configuration for UM980 and u-blox (command profiles, ArduPilot GPS type settings).
