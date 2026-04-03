# Self-Install Guide

> Board store: [GPS Spoofing Filter](https://airdroper.org/product/gps-spoofing-filter/)

This guide covers flashing the GNSS filter firmware onto a blank
STM32F401CC BlackPill board using a license key purchased from the store.

Each license key activates **one board**. The firmware is cryptographically
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
   and install. The provisioning tool needs `STM32_Programmer_CLI` on your PATH.

2. **Provisioning tool** — download `gnss-provision.exe` from the store downloads page.
   Or if you have Python 3.10+:
   ```
   pip install requests pyserial
   ```
   Then use `tools/gnss_provision.py` from the firmware repository.

---

## How provisioning works

```
  ┌──────────┐      ST-Link       ┌──────────────┐      Internet     ┌──────────────┐
  │ Your PC  │ ◄────(SWD)────────►│  BlackPill   │                   │   License    │
  │          │                    │  STM32F401   │                   │   Server     │
  │ gnss-    │                    │              │                   │              │
  │ provision│ ──── read UID ───► │  (blank)     │                   │              │
  │  .exe    │                    │              │                   │              │
  │          │ ── license + UID ──────────────────────────────────►  │  validates   │
  │          │                    │              │                   │  generates   │
  │          │ ◄── bootloader + firmware + metadata ──────────────── │  per-board   │
  │          │                    │              │                   │  firmware    │
  │          │ ──── flash ──────► │  (running!)  │                   │              │
  │          │ ──── set RDP1 ───► │  (locked)    │                   │              │
  └──────────┘                    └──────────────┘                   └──────────────┘
```

Each board gets a unique encryption key. The firmware is cryptographically
bound to your board's hardware ID and cannot be transferred to another board.

---

## Step 1 — Wire the ST-Link

Connect the ST-Link to the BlackPill SWD header:

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

Open a terminal and run:

```
gnss-provision activate --license GF-XXXX-XXXX-XXXX --server https://license.airdroper.org
```

The tool will:
1. Connect to the board via ST-Link
2. Read the board's unique hardware ID
3. Contact the license server to generate your personalized firmware
4. Flash the bootloader, application, and metadata
5. Enable readout protection (RDP Level 1)

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

## Step 3 — Verify

1. Disconnect the ST-Link
2. Power the board via USB or your aircraft power supply
3. Connect to Mission Planner and check for the filter boot message in the
   Messages tab (e.g. `GNSS filter v1.5.0 UID=12345678`)

---

## Firmware updates

After the initial flash, firmware updates use the Phase-C UART protocol
and do **not** require an ST-Link.

### What you need for updates

| Item | Notes |
|------|-------|
| USB-UART adapter | CP2102, CH340, or FTDI, ~$2 |
| 3 jumper wires | TX, RX, GND |

### Wiring

| USB-UART adapter | BlackPill pin |
|------------------|---------------|
| TX | PA10 (USART1 RX) |
| RX | PA9 (USART1 TX) |
| GND | GND |

**Disconnect the flight controller** from PA9/PA10 during the update.
These are the same pins used for FC MAVLink telemetry.

```
  USB-UART adapter             BlackPill
  ┌──────────┐                ┌──────────────┐
  │       TX ├────────────────┤ PA10 (RX)    │
  │       RX ├────────────────┤ PA9  (TX)    │
  │      GND ├────────────────┤ GND          │
  └──────────┘                └──────────────┘
     (disconnect FC from PA9/PA10 first)
```

### Update procedure

1. Wire the USB-UART adapter as shown above
2. Open a terminal and run:
   ```
   gnss-provision update --license GF-XXXX-XXXX-XXXX --uid <your-24-char-uid> --uart COM5 --server https://license.airdroper.org
   ```
   Replace `COM5` with your adapter's port. The UID is the full 24-character
   hex string shown during initial activation.
3. When prompted, **press the reset button** on the BlackPill
4. The tool will flash the new firmware over UART (~30-60 seconds)
5. The board resets automatically when done

---

## GUI tool (alternative)

If you prefer a graphical interface, use **AirDroper GNSS Filter.exe** instead
of the command-line tool. It supports the same two workflows:

- **Activate (ST-Link)** — first-time provisioning of a blank board.
- **Update (UART)** — firmware updates over a USB-UART adapter.

The GUI auto-detects available COM ports for UART updates. If the board is
already in RDP Level 1 from a previous activation, the tool automatically
removes readout protection, performs a mass erase, and re-provisions the
board from scratch — no manual steps required.

The interface is available in English and Ukrainian (language toggle in the
top-right corner).

---

## Spoofing event logs and cloud dashboard

Starting with firmware v1.5.0 the filter records every spoofing event to
on-board flash memory. Each event includes the timestamp, GPS coordinates,
satellite count, SNR values, and the detection reason.

### Downloading logs

1. Connect a USB-UART adapter (same wiring as firmware updates — TX→PA10,
   RX→PA9, GND→GND)
2. In the GUI tool click **Download Logs (UART)**
3. Enter your license key when prompted
4. The tool reads all stored events, uploads them to your cloud dashboard,
   and clears the on-board log

The license key is required to download logs — if someone finds a crashed
aircraft, they cannot access the flight data without the key.

### Cloud dashboard

Visit `https://gnss-filter.online/dashboard` and enter your license key to
view:

- **Event map** — all spoofing events plotted on a map with colour-coded
  markers by detection reason
- **Statistics** — total events, board count, reason breakdown
- **Event list** — scrollable timeline with coordinates, altitude,
  satellite count, and SNR data

The dashboard is accessible from any browser. Each license key can only see
its own data.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "STM32_Programmer_CLI not found" | Install STM32CubeProgrammer and add its `bin` folder to your PATH |
| "Failed to connect" | Check ST-Link wiring (3V3, GND, SWDIO, SWCLK). Try a different USB port. |
| "Invalid license key" | Double-check the key from your purchase email |
| "License already activated on a different board" | Each key works on one board only. Contact support for replacement. |
| "Timeout: no response from bootloader" (update) | Press the reset button on the BlackPill while the tool is waiting |
| RDP Level 1 warning on re-flash | Board is already protected. A mass erase will happen automatically. |
