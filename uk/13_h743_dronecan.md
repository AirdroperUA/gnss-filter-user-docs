# WeAct H743 DroneCAN

> Магазин плати: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

Ця сторінка описує окрему H743-версію для WeAct Studio MiniSTM32H743VITX
з 3.3 V CAN-трансивером SN65HVD230. У цій версії GNSS заходить у фільтр по
UART, а у польотний контролер GPS передається як native DroneCAN. Два serial
порти FC для MAVLink/GPS не використовуються.

## Прошивка

Основні середовища:

| PlatformIO env | Призначення | Завантаження |
|----------------|-------------|--------------|
| `weact_mini_h743vitx_dronecan` | H743 DroneCAN GPS build | ST-Link/SWD |
| `weact_mini_h743vitx_dronecan_usb` | Та сама standalone прошивка | USB-C ROM DFU |
| `weact_mini_h743vitx_dronecan_bootloader` | H743 secure bootloader | ST-Link/SWD |
| `weact_mini_h743vitx_dronecan_phaseb_app` | signed app за адресою `0x08020000` | ST-Link/SWD |
| `weact_mini_h743vitx_dronecan_phaseb_app_usb` | signed app за адресою `0x08020000` | USB-C ROM DFU |

Значення за замовчуванням:

- DroneCAN node ID: `42`
- CAN bitrate: `1000000`
- CAN pins: `PB9` TX, `PB8` RX
- GNSS UART: `PA2` TX, `PA3` RX
- USB-C залишається на `PA11/PA12`
- FC MAVLink serial і FC GPS serial вимкнені
- Parameters можна змінювати через Mission Planner DroneCAN node `42` у
  firmware `v0.1.4+`, або напряму через USB-C COM port H743 у firmware
  `v0.1.5+`

## Підключення всередині бокса

H743 не можна підключати напряму до CAN-порту польотного контролера. Піни
`PB8/PB9` є лише logic-level FDCAN сигналами, тому потрібен CAN-трансивер.

| Зв'язок | WeAct H743 | SN65HVD230 / зовнішній сигнал | Примітка |
|---------|------------|-------------------------------|----------|
| GNSS RX фільтра | `PA3` | GNSS TX | TX приймача у RX STM32 |
| GNSS TX фільтра | `PA2` | GNSS RX | TX STM32 у RX приймача |
| CAN TX | `PB9` | `TXD` трансивера | FDCAN1_TX |
| CAN RX | `PB8` | `RXD` трансивера | FDCAN1_RX |
| CAN power | `3V3` | `VCC` трансивера | тільки 3.3 V модуль |
| Ground | `GND` | `GND` трансивера і FC CAN GND | спільна земля |
| CAN bus | трансивер | `CANH/CANL/GND` до FC | кручена пара для CANH/CANL |
| DR1 event | `PB5` | опційний LED/logger | 3.3 V pulse |
| USB-C | `PA11/PA12` | роз'єм USB-C на платі | не виводити ці піни в harness |

Використовуйте 120 ohm termination на CAN-модулі тільки якщо H743 box стоїть
на фізичному кінці CAN-шини.

<a id="optional-hd-15-d-sub-box-connector"></a>

## HD-15 D-sub pinout для зовнішнього harness

Якщо H743, CAN-трансивер, дисплей і захист живлення знаходяться всередині
одного бокса, назовні виводьте тільки HD-15 D-sub. Це не VGA-інтерфейс.
Підпишіть роз'єм як `CAN/GNSS/POWER`.

Нумерація показана з боку підключення кабелю до female panel connector:

```text
   1   2   3   4   5
    6   7   8   9  10
  11  12  13  14  15
```

| Pin | Сигнал на боксі | Користувач підключає до | Всередині бокса |
|-----|-----------------|-------------------------|-----------------|
| 1 | `CANH` | FC CANH | SN65HVD230 `CANH` |
| 2 | `CANL` | FC CANL | SN65HVD230 `CANL` |
| 3 | `CAN_GND` | FC CAN GND | box ground |
| 4 | `BOX_5V_IN_A` | FC/BEC 5 V | box 5 V input |
| 5 | `BOX_5V_IN_B` | optional parallel 5 V | same net as pin 4 |
| 6 | `BOX_GND_A` | FC/BEC ground | box ground |
| 7 | `GNSS_TX_TO_BOX` | GNSS TX | H743 `PA3` |
| 8 | `GNSS_RX_FROM_BOX` | GNSS RX | H743 `PA2` |
| 9 | `GNSS_VOUT_FUSED` | GNSS VCC/VIN | protected output from box |
| 10 | `GNSS_GND` | GNSS GND | box ground |
| 11 | `SHIELD` | cable shield/drain | shell/chassis or single-point ground |
| 12 | `DR1_EVENT` | optional LED/logger | H743 `PB5` through protection |
| 13 | `NC` | no connect | reserved |
| 14 | `NC` | no connect | reserved |
| 15 | `BOX_GND_B` | optional parallel ground | box ground |

Правила:

- HD-15 не несе raw `PB8/PB9`; CAN-трансивер має бути всередині бокса.
- `CANH/CANL` ведіть крученою парою.
- Живіть box мінімум через pins 4/6; для більшого струму додайте pins 5/15.
- Pin 9 є виходом живлення на GNSS receiver. Не back-power box через pin 9.
- Напруга `GNSS_VOUT_FUSED` має відповідати приймачу: деякі модулі мають 5 V
  `VIN`, але raw receiver може вимагати 3.3 V.
- Не живіть H743 одночасно від USB-C і `BOX_5V_IN`, якщо в box немає ORing або
  захисту від back-feed.

## USB-C ROM DFU

Standalone DroneCAN build:

```powershell
pio run -e weact_mini_h743vitx_dronecan_usb -t upload
```

Signed app build:

```powershell
pio run -e weact_mini_h743vitx_dronecan_phaseb_app_usb -t upload
```

Вхід у ROM DFU:

1. Затисніть `BOOT0`.
2. Натисніть reset або power-cycle H743.
3. Підключіть USB-C до комп'ютера.
4. Відпустіть `BOOT0`, коли плата з'явиться як DFU device.

Windows app `AirDroper GNSS Filter` версії `2026.06.23.10` або новіше може
оновити вже активовану H743 через USB-C ROM DFU:

1. `Board target` -> `H743 WeAct DroneCAN`.
2. `Update transport` -> `USB-C ROM DFU`.
3. Введіть license key.
4. Переведіть H743 у ROM DFU через `BOOT0` + reset/power-cycle.
5. Натисніть `Update`.

USB-C ROM DFU шлях має два режими:

- readable/unlocked плата: пише app за `0x08020000` і metadata за
  `0x081E0000`; bootloader і option bytes не змінюються.
- RDP1-protected production плата: app просить ввести очікуваний UID-short,
  знімає RDP через USB DFU, вимагає power-cycle назад у ROM DFU із затиснутим
  `BOOT0`, робить mass erase, пише app + metadata + bootloader, перевіряє
  app/metadata і повертає H743 RDP Level 1.

RDP1 ховає фізичний UID до erase, тому protected USB-C path починається тільки
після підтвердження UID-short. Якщо UID-short неправильний або діалог
скасовано, app зупиняється до RDP removal і плата не змінюється.

## ST-Link/SWD

Підключення ST-Link V2:

| ST-Link V2 | WeAct H743 |
|------------|------------|
| `3V3` | `3V3` |
| `GND` | `GND` |
| `SWDIO` | `PA13` / `DIO` |
| `SWCLK` | `PA14` / `CLK` |

У Windows app:

1. `Board target` -> `H743 WeAct DroneCAN`.
2. `Update transport` -> `ST-Link (SWD)`.
3. Введіть license key.
4. `Activate` для нової плати або `Update` для вже активованої H743.

H743 secure layout:

| Region | Address range | Purpose |
|--------|---------------|---------|
| Bootloader | `0x08000000 - 0x0801FFFF` | Secure bootloader |
| Active app | `0x08020000 - 0x080FFFFF` | Signed H743 DroneCAN firmware |
| Reserved stage | `0x08100000 - 0x081DFFFF` | Reserved for future DroneCAN firmware update |
| Metadata | `0x081E0000 - 0x081FFFFF` | Signed metadata / update state |

Не прошивайте H743 app або metadata у F401 адреси.

Standard Mission Planner DroneCAN firmware update is planned but not active in
the current H743 firmware. Today use AirDroper Windows app `ST-Link (SWD)` or
`USB-C ROM DFU` for H743 updates. Already-deployed H743 boards will need one
wired update first before future DroneCAN self-update can work.

## ArduPilot setup

Налаштуйте CAN-порт польотного контролера:

| Параметр | CAN1 приклад | CAN2 приклад |
|----------|--------------|--------------|
| Enable CAN driver | `CAN_P1_DRIVER = 1` | `CAN_P2_DRIVER = 1` |
| DroneCAN protocol | `CAN_D1_PROTOCOL = 1` | `CAN_D2_PROTOCOL = 1` |
| Bitrate | `CAN_P1_BITRATE = 1000000` | `CAN_P2_BITRATE = 1000000` |
| GPS type | `GPS1_TYPE = 9` | `GPS2_TYPE = 9` |
| GPS auto-config | `GPS_AUTO_CONFIG = 1` | global parameter |
| Optional GPS node lock | `GPS1_CAN_OVRIDE = 42` | `GPS2_CAN_OVRIDE = 42`, якщо це GPS2 |

Після зміни CAN параметрів перезавантажте FC.

Прошивка публікує:

- `uavcan.protocol.NodeStatus`
- `uavcan.protocol.GetNodeInfo`
- `uavcan.equipment.gnss.Fix2`
- `uavcan.equipment.gnss.Auxiliary`

Raw NMEA, UBX або MAVLink через CAN у v1 не тунелюються.

Оскільки FC отримує native DroneCAN GPS, H743 DroneCAN не є byte-for-byte GPS
packet pass-through. Прошивка парсить receiver stream і публікує ті самі live
fix values у DroneCAN units. Вона не генерує synthetic GPS coordinates, не
blend-ить coordinates і не переписує raw NMEA/UBX packets; у DR1 вона suppress
`Fix2/Auxiliary` замість того, щоб надсилати altered GPS data.

`GPS_AUTO_CONFIG=1` є default ArduPilot режимом auto-config тільки для serial
GPS і є найбезпечнішим для цього фільтра. H743 DroneCAN firmware `v0.1.2+`
відповідає на optional DroneCAN `param.GetSet` запити ArduPilot для
`GPS_TYPE`/`GPS1_TYPE`, тому `GPS_AUTO_CONFIG=2` не блокує GPS data.

Якщо на CAN bus є більше одного DroneCAN GPS-like node, задайте відповідний
`GPSx_CAN_OVRIDE` на `42`, щоб ArduPilot прив'язав GPS instance до static node
ID фільтра. На single-GPS bus це optional.

## Mission Planner Params

H743 DroneCAN firmware `v0.1.4+` відкриває spoofing/tuning parameters через
DroneCAN parameter service. H743 DroneCAN firmware `v0.1.5+` також відкриває
ті самі parameters через USB-C COM port самої H743 як direct MAVLink
management link.

Звичайний Mission Planner full parameter tree, підключений до flight
controller, не покаже parameters цієї плати, бо H743 DroneCAN variant не має
FC MAVLink serial link.

### Варіант A: DroneCAN через flight controller

Порядок:

1. Відкрийте Mission Planner.
2. `SETUP -> Optional Hardware -> DroneCAN/UAVCAN`.
3. Виберіть активний CAN driver, зазвичай `MAVLinkCAN1`, і натисніть `Connect`.
4. Дочекайтесь node `42` з назвою `org.airdroper.gnss_filter.h743_dronecan`.
5. Натисніть `Menu` на node `42` і відкрийте `Parameters`.
6. Змініть tune value, натисніть `Write Params`, потім `Commit Params`.
7. Перезавантажте H743 і перевірте, що значення збереглось.

### Варіант B: direct USB-C до H743

Використовуйте це на столі, якщо хочете звичний Mission Planner MAVLink
parameter screen без жодного FC serial port:

1. Увімкніть H743 у normal app mode, не тримайте `BOOT0`.
2. Підключіть USB-C H743 до комп'ютера.
3. У Mission Planner виберіть новий H743 COM port і `115200` baud.
4. Натисніть `Connect`. Mission Planner має побачити system ID `42`.
5. Відкрийте `CONFIG -> Full Parameter Tree` або `Full Parameter List`.
6. Змініть spoofing/tuning values і натисніть `Write Params`.
7. Зачекайте кілька секунд на save, потім перезавантажте/reconnect і
   перевірте value за потреби.

Цей USB-C режим є normal application management port. Це не ROM DFU flashing:
тримайте `BOOT0` тільки для firmware update, а для редагування parameters
залишайте `BOOT0` відпущеним.

У DroneCAN node Params перші два rows, `GPS_TYPE` і `GPS1_TYPE`, є read-only
compatibility rows зі значенням `9`. Реальні tune rows починаються після них.
У direct USB-C MAVLink parameter screen список починається одразу з tune rows:
`BOOT_NSATS`, `BOOT_NHDOP`, `RJ_BASE_M`, `SP_JMP_MPS`, `SNR_EN`, `FENCE_RAD`,
`GNSS_TYPE` тощо.

`UBX_RESET` є one-shot command, не saved setting:

- `UBX_RESET=1` - u-blox hot start
- `UBX_RESET=2` - u-blox cold start
- `UBX_RESET=3` - clear u-blox config and reinitialize

H743 DroneCAN тримає MAVLink-dependent F401 settings locked off:

- `RJ_REQEKF = 0`
- `FCGPS_UART = 0`
- `FCGPS_FWD = 0`

## Дисплей

Onboard ST7735 screen показує:

- `FILTER OK`, `FILTER WARN`, або `FILTER NO OK`
- `WHY RUN`, `WHY GPS`, `WHY CAN ERR`, `WHY NOFIX`, `WHY SATS`, `WHY JUMP`,
  `WHY FENCE`, `WHY TIME` та інші короткі причини
- FC DroneCAN node health/mode
- arm/safety state, якщо FC їх транслює
- ArduPilot NotifyState bits як `STATE FLY`, `STATE FSRAD`, `STATE FSBAT`,
  `STATE GPSGL`, `STATE EKF`
- `PUB ON DR0` або `PUB BLK DR1`
- CAN counters `CAN tx/rx` і `ERR tx/rx`

У H743 DroneCAN `v0.1.3+` екран одразу показує boot/progress page після
display init. Під час довшого receiver autobaud/config має бути видно
`GNSS INIT`; після GNSS startup екран переходить на `BOOT GUARD`, а потім на
звичайну status page.

Точні назви режимів ArduPilot типу Loiter, Auto, Guided або RTL не входять у
стандартні DroneCAN GPS/status повідомлення, які використовує v1. Дисплей
показує доступні стандартні DroneCAN/ArduPilot status bits.

## DR0 / DR1

У DR0:

- `Fix2` публікується на кожен свіжий GNSS update, максимум 10 Hz
- `Auxiliary` публікується 1 Hz
- `NodeStatus` лишається online

У spoof/fault DR1:

- `Fix2` і `Auxiliary` зупиняються
- FC перестає отримувати свіжий GPS від цього node
- `NodeStatus` продовжується 1 Hz з warning health
- дисплей показує `FILTER NO OK`, коротку `WHY` причину і `PUB BLK DR1`

No-fix, low satellites, boot guard, або GNSS reconfiguration теж можуть
suppress `Fix2/Auxiliary`, включно з latched no-fix/low-sat DR1 internally,
але ці стани лишають `NodeStatus` health `OK` і показують output block тільки
через vendor status bits та onboard screen. Це прибирає ArduPilot
`PreArm: DroneCAN: Node 42 unhealthy!`, коли GPS просто ще не готовий.

GNSS-only guards активні: no fix, low satellites, position jump, altitude
rate/jump, SNR anomaly, hemisphere/geofence, heading reversal, GPS time sanity,
velocity-position consistency і receiver clock jump, якщо дані доступні.

## Перевірка

1. Прошийте `weact_mini_h743vitx_dronecan_usb` або ST-Link build.
2. Підключіть GNSS до `PA2/PA3`.
3. Підключіть `PB9/PB8` до SN65HVD230, а `CANH/CANL/GND` до FC CAN.
4. У ArduPilot увімкніть CAN driver, DroneCAN protocol, 1 Mbps і `GPS_TYPE=9`.
5. Перезавантажте FC.
6. Перевірте, що H743 screen світиться і показує GNSS/filter state.
7. Перевірте, що DroneCAN node ID `42` видно у DroneCAN/SLCAN tooling.
8. Перевірте, що ArduPilot бачить DroneCAN GPS.
9. Викличте bench DR1 і переконайтесь, що GPS публікації зупинились, а
   `NodeStatus` залишився online.
10. Приберіть причину DR1 і переконайтесь, що GPS publishing відновився.

## Якщо щось не працює

- Node не видно: перевірте `CAN_Dx_PROTOCOL=1`, bitrate `1000000`, CANH/CANL,
  common ground, termination на кінцях шини, `PB9 -> TXD`, `PB8 <- RXD`.
- FC не бачить GPS: перевірте `GPS1_TYPE=9`, GNSS fix, `PUB ON DR0`, і щоб
  `WHY` не показував `GPS`, `NOFIX`, `SATS`, `JUMP`, `FENCE` або іншу DR1
  причину.
- Для firmware старішої за H743 DroneCAN `v0.1.2` перевірте
  `GPS_AUTO_CONFIG=1`.
- Якщо є кілька DroneCAN GPS nodes, задайте `GPS1_CAN_OVRIDE=42` або override
  для відповідного GPS instance.
- USB-C DFU не стартує: тримайте `BOOT0` під час reset/power-up, використайте
  data-capable USB-C cable, від'єднайте ST-Link, перевірте RDP state. Якщо
  плата має RDP Level 1, raw PlatformIO app-only ROM DFU upload не зможе її
  оновити. Для вже активованої H743 використовуйте desktop app
  **USB-C ROM DFU** update path, або ST-Link/manual recovery для development
  board, яку треба свідомо відновити.
- Якщо плата на H743 DroneCAN `v0.1.0` завантажується, синій LED блимає раз на
  кілька секунд, але екран чорний, оновіть H743 DroneCAN до `v0.1.1` або
  новішої. `v0.1.1` виправляє полярність backlight для WeAct LCD (`PE10`
  active-low).
- Дисплей гасне після boot: firmware вимикає backlight, якщо SPI writes до
  дисплея fail. DroneCAN GPS і guard logic продовжують працювати без екрана.
