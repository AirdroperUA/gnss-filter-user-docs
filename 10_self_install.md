# Self-Install Guide

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

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
4. Click **Start** — the app will automatically:
   - Connect to the board via ST-Link
   - Read your board's unique hardware ID
   - Download firmware customized for your board
   - Flash the bootloader, application, and settings
   - Enable readout protection to prevent cloning

You should see output like:
```
Connecting to target via ST-Link...
Reading board UID...
Board UID: aabbccddeeff1122334455 (short: 12345678)
Contacting license server...
Firmware version: 1.5.0
  Bootloader: 32696 bytes
  Application: 73732 bytes
  Metadata: 148 bytes
Erasing flash...
Writing bootloader (0x08000000)...
Writing application (0x08008000)...
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
   Messages tab (e.g. `GNSS filter v1.5.0 UID=12345678`)

**Next steps:** Wire the filter into your drone using the [Wiring Guide](#wiring), then configure your flight controller in [Setup & Flash](#setup-flash).

---

## Firmware updates

After the initial flash, firmware updates use a USB-UART adapter
and do **not** require an ST-Link.

### What you need for updates

| Item | Notes |
|------|-------|
| USB-UART adapter | CP2102, CH340, or FTDI, ~$2 |
| 3 jumper wires | TX, RX, GND |

### Wiring

| USB-UART adapter | BlackPill pin |
|------------------|---------------|
| TX | PA10 (RX) |
| RX | PA9 (TX) |
| GND | GND |

**Important:** Disconnect the flight controller from PA9/PA10 during the update.
These are the same pins used for flight controller telemetry.

```
  USB-UART adapter             BlackPill
  ┌──────────┐                ┌──────────────┐
  │       TX ├────────────────┤ PA10 (RX)    │
  │       RX ├────────────────┤ PA9  (TX)    │
  │      GND ├────────────────┤ GND          │
  └──────────┘                └──────────────┘
     (disconnect flight controller from PA9/PA10 first)
```

### Update procedure

1. Wire the USB-UART adapter as shown above
2. Open the **AirDroper GNSS Filter** app
3. Select **Update (UART)** mode
4. Select the COM port of your USB-UART adapter (auto-detected)
5. Enter your license key
6. Click **Start**
7. When prompted, **press the reset button** on the BlackPill
8. The app will flash the new firmware (~30-60 seconds)
9. The board resets automatically when done

---

## Spoofing event logs and cloud dashboard

Starting with firmware v1.5.0, the filter records every spoofing event to
on-board memory. Each event includes the timestamp, GPS coordinates,
satellite count, signal strength, and the detection reason.

### Downloading logs

**Option A — USB-C (easiest, no extra hardware):**

1. Connect the BlackPill to your PC with a USB-C cable
2. In the app, set Port to **(USB-C auto-detect)**
3. Enter your license key and UID
4. Click **Download Logs** and press the **reset button** on the BlackPill when prompted
5. The app finds the board automatically, downloads events, uploads to your cloud dashboard, and clears the on-board log

**Option B — USB-UART adapter:**

1. Connect a USB-UART adapter (same wiring as firmware updates)
2. In the app, select the COM port of your adapter
3. Enter your license key and UID
4. Click **Download Logs** and press **reset** when prompted

The license key is required to download logs — if someone finds a crashed
aircraft, they cannot access the flight data without the key.

### Cloud dashboard

Visit [gnss-filter.online/dashboard](https://gnss-filter.online/dashboard) and enter your license key to view:

- **Event map** — all spoofing events plotted on a map with colour-coded
  markers by detection reason
- **Statistics** — total events, board count, reason breakdown
- **Event list** — scrollable timeline with coordinates, altitude,
  satellite count, and signal data

The dashboard is accessible from any browser. Each license key can only see
its own data.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "STM32_Programmer_CLI not found" | Install STM32CubeProgrammer and restart the app. If it still does not work, add the CubeProgrammer `bin` folder to your system PATH. |
| "Failed to connect" | Check ST-Link wiring (3V3, GND, SWDIO, SWCLK). Try a different USB port. |
| "Invalid license key" | Double-check the key from your purchase email |
| "License already activated on a different board" | Each key works on one board only. Contact support for replacement. |
| "Timeout: no response from bootloader" (update) | Press the reset button on the BlackPill while the app is waiting |
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

### Firmware update (UART)

```
gnss-provision update --license GF-XXXX-XXXX-XXXX --uid <your-24-char-uid> --uart COM5 --server https://gps.airdroper.org
```

Replace `COM5` with your adapter's port. The UID is the full 24-character
hex string shown during initial activation.

</details>
