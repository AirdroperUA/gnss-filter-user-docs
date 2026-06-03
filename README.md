# User Documentation

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

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

## Video Tutorials

<div style="display: grid; grid-template-columns: minmax(180px, 300px) minmax(240px, 1fr); gap: 16px; align-items: center; margin: 16px 0 24px;">
  <a href="12_video_tutorials.md#flash-new-board" aria-label="Open Flash a New Board with the Windows App tutorial">
    <img src="https://i.ytimg.com/vi/vXlP-tu7s1k/hqdefault.jpg" alt="Preview thumbnail for Flash a New Board with the Windows App" width="300" loading="lazy">
  </a>
  <div>
    <strong>Flash a New Board with the Windows App</strong>
    <p>Watch the full activation and flashing flow for a blank STM32 board using the AirDroper GNSS Filter Windows <code>.exe</code> app.</p>
    <p><a href="12_video_tutorials.md#flash-new-board">Open the tutorial page</a> or <a href="https://youtu.be/vXlP-tu7s1k">watch on YouTube</a>.</p>
  </div>
</div>

<div style="display: grid; grid-template-columns: minmax(180px, 300px) minmax(240px, 1fr); gap: 16px; align-items: center; margin: 16px 0 24px;">
  <a href="12_video_tutorials.md#stlink-pinout" aria-label="Open ST-Link Wiring and Board Pinout tutorial">
    <img src="https://i.ytimg.com/vi/bOzFh70B66g/hqdefault.jpg" alt="Preview thumbnail for ST-Link Wiring and Board Pinout" width="300" loading="lazy">
  </a>
  <div>
    <strong>ST-Link Wiring and Board Pinout</strong>
    <p>Hardware-focused flashing walkthrough for the ST-Link connection, board pinout, and physical setup before using the Windows app.</p>
    <p><a href="12_video_tutorials.md#stlink-pinout">Open the tutorial page</a> or <a href="https://youtube.com/shorts/bOzFh70B66g">watch on YouTube</a>.</p>
  </div>
</div>

<div style="display: grid; grid-template-columns: minmax(180px, 300px) minmax(240px, 1fr); gap: 16px; align-items: center; margin: 16px 0 24px;">
  <a href="12_video_tutorials.md#wiring" aria-label="Open General Wiring Overview tutorial">
    <img src="https://i.ytimg.com/vi/ARGg_KQceoU/hqdefault.jpg" alt="Preview thumbnail for General Wiring Overview" width="300" loading="lazy">
  </a>
  <div>
    <strong>General Wiring Overview</strong>
    <p>Start here for a quick visual walkthrough of the STM32, GNSS receiver, and flight-controller wiring layout.</p>
    <p><a href="12_video_tutorials.md#wiring">Open the tutorial page</a> or <a href="https://youtube.com/shorts/ARGg_KQceoU">watch on YouTube</a>.</p>
  </div>
</div>

1. `01_device_overview.md` - high-level device operation and trigger examples.
2. `02_wiring.md` - physical wiring for STM32, GNSS receiver, and FC.
3. `03_wiring_debug.md` - diagnose GNSS/GPS/MAVLink wiring issues.
4. `04_setup_and_flash.md` - setup and FC serial configuration.
5. `04_recovery.md` - recovery page and support escalation notes.
6. `05_operation.md` - runtime behavior (DR0/DR1, GNSS forwarding, event pulse).
7. `06_tuning.md` - live tuning parameters and Mission Planner workflow.
8. `07_cheat_sheet.md` - one-page quick reference for field checks and actions.
9. `08_lab_validation.md` - safe lab validation workflow before real flights.
10. `09_receiver_config.md` - GNSS receiver configuration for u-blox, UM980, and Mosaic X5 (profiles, ArduPilot GPS type settings).
11. `10_self_install.md` - self-install guide for flashing firmware onto a blank board using a license key.
12. `11_faq.md` - frequently asked questions (hardware, setup, operation, receiver modes, licensing).
13. `12_video_tutorials.md` - YouTube tutorial library with previews, embedded players, and related written guides.
14. `CHANGELOG.md` - full firmware version history and release notes.
