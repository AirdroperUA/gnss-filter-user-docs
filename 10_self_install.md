# Self-Install Guide

> Board store: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

This guide covers flashing the GNSS filter firmware onto a blank
STM32F401CC BlackPill board using a license key purchased from the store.

Each license key activates **one board**. The firmware is uniquely
locked to your specific board and cannot be copied to another.

---

## What you need

| Item | Notes |
|------|-------|
| STM32F401CC BlackPill V2.0 board | WeAct Studio or equivalent |
| ST-Link V2 programmer | Genuine or clone, ~$3 |
| 4 jumper wires | 3V3, GND, SWDIO, SWCLK |
| Windows PC with internet | |
| License key | From your purchase (e.g. `GF-XXXX-XXXX-XXXX`) |

### Software

1. **STM32CubeProgrammer** (free) — download from
   [st.com](https://www.st.com/en/development-tools/stm32cubeprog.html)
   and install. After installation, the provisioning app will find it automatically.

2. **[AirDroper GNSS Filter](https://gps.airdroper.org/download/app)** app — download from the link.
   This is the graphical Windows tool that handles everything for you.

---

## Step 1 — Wire the ST-Link

Connect the ST-Link to the BlackPill SWD header using 4 jumper wires:

| ST-Link pin | BlackPill pin |
|-------------|---------------|
| 3V3 | 3V3 |
| GND | GND |
| SWDIO | DIO (PA13) |
| SWCLK | CLK (PA14) |

Power the BlackPill from the ST-Link 3V3 (or USB, either works).

```
  ST-Link V2                   BlackPill
  ┌──────────┐                ┌──────────────┐
  │      3V3 ├────────────────┤ 3V3          │
  │      GND ├────────────────┤ GND          │
  │    SWDIO ├────────────────┤ DIO (PA13)   │
  │    SWCLK ├────────────────┤ CLK (PA14)   │
  └──────────┘                └──────────────┘
```

## Step 2 — Activate and flash

1. Open the **AirDroper GNSS Filter** app
2. Select **Activate (ST-Link)** mode
3. Enter your license key (e.g. `GF-XXXX-XXXX-XXXX`)
4. Plug in exactly **one** ST-Link V2. If you have more than one
   connected (lab bench with several adapters), the app will stop and
   ask you to unplug the others — this prevents flashing the wrong
   board.
5. Click **Start** — the app will automatically:
   - Connect to the board via ST-Link
   - Read your board's unique hardware ID
   - Download firmware customized for your board
   - Flash the bootloader, application, and settings
   - Enable readout protection to prevent cloning

If you close the app window while a flash is in progress, the in-flight
`STM32_Programmer_CLI` process is killed cleanly — the ST-Link adapter
will not be left locked.

You should see output like:
```
Connecting to target via ST-Link...
Reading board UID...
Board UID: aabbccddeeff1122334455 (short: 12345678)
Contacting license server...
Firmware version: 1.5.5
  Bootloader: 47104 bytes
  Application: 73732 bytes
  Metadata: 148 bytes
Erasing flash...
Writing bootloader (0x08000000)...
Writing application (0x0800C000)...
Writing metadata (0x0801FC00)...
Setting readout protection (RDP Level 1)...

Provisioning complete!
```

> **Note:** If the board was previously activated, the app automatically handles
> removing readout protection, erasing, and re-flashing — no manual steps needed.

## Step 3 — Verify

1. Disconnect the ST-Link
2. Power the board via USB or your aircraft power supply
3. Connect to [Mission Planner](https://ardupilot.org/planner/) and check for the filter boot message in the
   Messages tab (e.g. `GNSS filter v1.5.5 UID=12345678`)

**Next steps:** Wire the filter into your drone using the [Wiring Guide](#wiring), then configure your flight controller in [Setup & Flash](#setup-flash).

---

## Firmware updates

Firmware updates use the **same ST-Link V2 adapter** as initial activation.
USB-C firmware updates have been removed — pins PA11/PA12 are now reserved
for flight-controller GPS UART (USART6) and the bootloader no longer
enumerates as a USB CDC device.

### What you need

The same hardware as the initial flash:

| Item | Notes |
|------|-------|
| ST-Link V2 programmer | Genuine or clone, ~$3 |
| 4 jumper wires | 3V3, GND, SWDIO, SWCLK |

### Wiring (4-pin SWD header on the ICWkey board)

| ST-Link pin | ICWkey SWD pin |
|-------------|----------------|
| 3V3 (VCC) | 3V3 |
| GND | GND |
| SWCLK | A14 |
| SWDIO | A13 |

```
  ST-Link V2                   ICWkey (SWD header)
  ┌──────────┐                ┌──────────────┐
  │  3V3 VCC ├────────────────┤ 3V3          │
  │      GND ├────────────────┤ GND          │
  │    SWCLK ├────────────────┤ A14          │
  │    SWDIO ├────────────────┤ A13          │
  └──────────┘                └──────────────┘
```

### Update procedure (ST-Link V2 SWD)

1. Wire the ST-Link to the ICWkey SWD header as shown above
2. Open the **AirDroper GNSS Filter** app
3. Select **Update (ST-Link)** mode
4. Enter your license key
5. Click **Start**
6. The app connects via ST-Link, downloads the new firmware customised for
   your board, and flashes it (~30–60 seconds)
7. The board resets automatically when done

> **Note:** RDP1 (readout protection) is removed and re-applied automatically
> by the app — no manual steps required.

### Recovery (ST-Link V2 SWD)

If a board ever fails to boot — for example after a power loss mid-flash —
use the same ST-Link V2 wiring above and select **Recover (ST-Link)** in
the app. The recovery flow re-runs the full activation sequence using your
existing license key.

---

## Spoofing event logs

Starting with firmware v1.6.0, the filter no longer stores spoofing events
in on-board flash. Instead, every detection event and confidence-score
update is emitted in real time as MAVLink **STATUSTEXT** and
**NAMED_VALUE_INT** messages, which ArduPilot writes to the flight
controller's SD card as standard dataflash records (`MSG` and `NVLI`).

### Where to find the logs

1. Pull the SD card from your flight controller (or download the `.bin` log
   over MAVFTP / Mission Planner)
2. Open the `.bin` log in **Mission Planner** → *DataFlash Logs* → *Review a Log*
3. Spoofing events appear as `MSG` lines beginning with `GNSS:` or `DR1:`,
   plus `NVLI` records carrying the live `DR_CONF` confidence score
4. Optional: drag the same `.bin` into [UAV Log Viewer](https://plot.ardupilot.org)
   for a graphical timeline

There is no longer any "Download Logs" button in the AirDroper GNSS Filter
app, and no on-board log to extract. All flight-evidence collection
happens through the standard ArduPilot dataflash pipeline.

### EW interference map

The [EW Interference Map](https://gps.airdroper.org/ew-map) is a free, public live map showing global GNSS interference from multiple sources (aircraft ADS-B, marine AIS, Ukraine air raid alerts, 61 known EW zones, crowdsourced reports, and deployed board events). No login required. You can also embed it on your site via [gps.airdroper.org/ew-map/embed](https://gps.airdroper.org/ew-map/embed), subscribe to email/Telegram alerts, or use the public API for route risk assessment. See the [FAQ](#faq) for details.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "STM32_Programmer_CLI not found" | Install STM32CubeProgrammer and restart the app. If it still does not work, add the CubeProgrammer `bin` folder to your system PATH. |
| "Failed to connect" | Check ST-Link wiring (3V3, GND, SWDIO, SWCLK). Try a different USB port. |
| "Invalid license key" | Double-check the key from your purchase email |
| "License already activated on a different board" | Each key works on one board only. Contact support for replacement. |
| "ST-Link not found" (update) | Plug the ST-Link into a different USB port and re-check the 4-pin SWD wiring (3V3, GND, A14/SWCLK, A13/SWDIO). |
| RDP Level 1 warning on re-flash | Board is already protected. The app handles this automatically. |

---

<details>
<summary><strong>Advanced: Command-line alternative</strong></summary>

If you prefer the command line over the graphical app, you can use the CLI tool directly.

### Requirements

You need Python 3.10+ with these packages:
```
pip install requests pyserial
```

### Initial activation (ST-Link)

```
gnss-provision activate --license GF-XXXX-XXXX-XXXX --server https://gps.airdroper.org
```

### Firmware update (ST-Link)

```
gnss-provision update --license GF-XXXX-XXXX-XXXX --uid <your-24-char-uid> --stlink --server https://gps.airdroper.org
```

The UID is the full 24-character hex string shown during initial
activation. Wire the ST-Link to the SWD header (3V3, GND, A14/SWCLK,
A13/SWDIO) before running the command.

</details>
