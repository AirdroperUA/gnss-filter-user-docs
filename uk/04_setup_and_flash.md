# Інструкція з налаштування

> Де купити плату: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

## 1) Передумови

- STM32F401 filter board встановлена та попередньо прошита, або WeAct H743
  прошита відповідною standalone/H743 DroneCAN development-прошивкою.
- На платі має бути встановлена firmware family, яка відповідає схемі
  підключення.
- Прошивка FC: ArduPilot 4.6.1 або новіша.
- На платформі мають бути виконані базові калібрування з завідомо справним GPS-шляхом:
  - відкалібрований акселерометр,
  - відкалібрований компас.
  Інакше `EKF flags trip` може залишатися активним і FC не повернеться в DR0.
- На FC має бути:
  - один телеметрійний UART для MAVLink2,
  - один GPS UART для підключення GNSS,
  - або DroneCAN-capable CAN port для H743 DroneCAN-прошивки.

## 2) Налаштування UART на FC (ArduPilot)

Використайте два UART-порти FC:

1. **MAVLink-порт (до STM32 `A9/A10`)**
   - `SERIALx_PROTOCOL = 2` (MAVLink2)
   - `SERIALx_BAUD = 115` (115200)
2. **GPS UART**
   - `SERIALy_PROTOCOL = 5` (GPS)
   - `SERIALy_BAUD = 460` (460800)

Для F401 GPS UART іде через `A11/A12`. Для H743 standalone UART-збірки GPS
UART іде через `C6/C7`.

Параметри ArduPilot GPS для сценарію u-blox:

- `GPS_AUTO_SWITCH = 0`
- `GPS1_TYPE = 2` (u-blox)
- `GPS_AUTO_CONFIG = 0`

Якщо використовується інший тип приймача (наприклад UM980/UM981/UM982 або Mosaic X5), протокол GPS на FC має відповідати виходу вашого приймача.
Для `GNSS_TYPE=1` або `GNSS_TYPE=2` STM32 очікує лише один фізичний NMEA-потік:

- UM980 `COM1` -> STM32 `A2/A3`
- STM32 парсить spoofing/SNR із цього потоку
- STM32 пересилає цей самий потік на FC GPS UART (`A11/A12` на F401, `C6/C7` на H743 UART-збірці)

## 3) H743 DroneCAN GPS mode

Використовуйте цей розділ тільки зі збірками
`weact_mini_h743vitx_dronecan` або `weact_mini_h743vitx_dronecan_usb`. Цей
режим публікує native DroneCAN GNSS messages і не використовує FC MAVLink або
FC GPS serial ports.

Firmware defaults:

- DroneCAN node ID: `42`
- FC DroneCAN node filter: `0` auto-detect/identify the FC from
  arm/safety/NotifyState broadcasts, not from arbitrary NodeStatus frames. Set
  `FILTER_DRONECAN_FC_NODE_ID` at build time to lock the onboard screen to one
  FC node on a multi-node CAN bus.
- CAN bitrate: `1 Mbps`
- Published messages: `uavcan.protocol.NodeStatus`,
  `uavcan.protocol.GetNodeInfo`, `uavcan.equipment.gnss.Fix2`,
  `uavcan.equipment.gnss.Auxiliary`
- Onboard screen: filter OK/warn/no-OK with a `WHY` reason line, GNSS publish
  state, CAN counters, FC DroneCAN node health/mode, arm/safety state, and an
  ArduPilot vehicle-state row from `ardupilot.indication.NotifyState` when that
  broadcast is present

Параметри польотного контролера для CAN-порту, до якого підключений H743 node:

- `CAN_P1_DRIVER = 1` для CAN1, або `CAN_P2_DRIVER = 1` для CAN2
- `CAN_D1_PROTOCOL = 1` для CAN1, або `CAN_D2_PROTOCOL = 1` для CAN2
- `CAN_P1_BITRATE = 1000000` або `CAN_P2_BITRATE = 1000000`
- `GPS1_TYPE = 9` для DroneCAN GPS

Після зміни CAN driver parameters перезавантажте FC. Якщо H743 node стоїть
на фізичному кінці CAN-шини, увімкніть 120 ohm termination на CAN-модулі;
інакше залиште termination вимкненим.

Development USB-C ROM DFU flash:

```powershell
pio run -e weact_mini_h743vitx_dronecan_usb -t upload
```

H743 secure app USB-C ROM DFU flash. This env writes the app slot at `0x08020000`:

```powershell
pio run -e weact_mini_h743vitx_dronecan_phaseb_app_usb -t upload
```

These PlatformIO USB environments are direct ROM DFU flash paths for WeAct H743.
The onboard display shows standard DroneCAN node mode/health and ArduPilot
`NotifyState` vehicle-state bits, not exact flight-mode names such as Loiter or
Auto.

Щоб увійти в DFU: утримуйте `BOOT0`, зробіть reset або power-cycle WeAct H743,
потім підключіть USB-C.

Production H743 DroneCAN boards використовують signed H743 bootloader layout:
bootloader at `0x08000000`, app at `0x08020000`, metadata at `0x081E0000`.
Desktop app `2026.06.23.4+` може оновлювати вже активовану H743 через
USB-C ROM DFU. На readable/unlocked платах додаток пише лише app+metadata.
Для RDP1-protected плат потрібне підтвердження UID-short: додаток знімає RDP
через USB DFU, просить повернути плату в ROM DFU із затиснутим `BOOT0`, робить
mass erase, переписує app + metadata + bootloader і повертає H743 RDP Level 1.

Licensed H743 DroneCAN provisioning через ST-Link/SWD:

```powershell
python tools/gnss_provision.py activate --target h743_dronecan --license GF-XXXX-XXXX-XXXX --server https://gps.airdroper.org
```

Для desktop app: оберіть **Board target -> H743 WeAct DroneCAN**. Для ST-Link
activation/update оберіть **Update transport -> ST-Link (SWD)**. Для вже
активованої H743 можна обрати **Update transport -> USB-C ROM DFU**; якщо app
просить power-cycle після RDP removal, тримайте `BOOT0`, щоб плата повернулась
у ROM DFU.

## 4) Режим CAN-ноди (UCAN serial transport)

Цей розділ не є H743 DroneCAN GPS mode. Він описує окремі CAN-ноди, які
тунелюють serial GPS через UCAN.

Параметри CAN-ноди:

- `GPS_AUTO_CONFIG = 0`
- `GPS_SAVE_CFG = 1`
- `GPS_PORT = 2`

Параметри на польотному контролері:

- `GPS1_TYPE = 9`
- `CAN_D1_UC_SER_EN = 1`
- `CAN_D1_UC_S1_BD = 115`
- `CAN_D1_UC_S1_IDX = 1`
- `CAN_D1_UC_S1_NOD = *` (вкажіть фактичний ID вашої CAN-ноди)
- `CAN_D1_UC_S1_PRO = 2`

## 5) Очікувана поведінка фільтра

- ID UART-фільтра: `SYSID=42`, `COMPID=191`.
- Захист DR1 штатно блокує живе пересилання GNSS із входу приймача на GPS UART FC — FC отримує тишу, якщо діагностичний режим сирого пересилання вимкнений.
- У H743 DroneCAN mode захист DR1 suppresses DroneCAN `Fix2/Auxiliary`
  замість GPS UART silence. `NodeStatus` лишається online і повідомляє
  warning health, поки GPS output suppressed.
- UART-build параметри фільтра змінюються у Mission Planner:
  - `Config/Tuning` -> `Full Parameter List`
  - виберіть STM32 (`SYSID=42`)
  - `Refresh Params` -> змініть значення -> `Write Params`
- Перед тюнінгом UART-збірок встановіть [AirDroper Mission Planner Params](https://gps.airdroper.org/download/mission-planner-mod), щоб Mission Planner показував описи, діапазони, одиниці та підписи варіантів для параметрів STM32, а не лише сирі назви.
- H743 DroneCAN v1 не має Mission Planner MAVLink params; defaults compile-time.
- Перезавантаження не потрібне після кожного запису параметра.

Вибір режиму приймача на STM32:

- `GNSS_TYPE=0`: режим u-blox/UBX.
- `GNSS_TYPE=1`: режим UM980/UM981/UM982 (NMEA).
- `GNSS_TYPE=2`: режим Septentrio Mosaic X5 (NMEA).
- Зміни `GNSS_TYPE` застосовуються тільки після перезавантаження.
- Лише для u-blox параметр `UBX_BAUD` керує автоконфігом/ручним baud:
  - `UBX_BAUD=0`: автоконфіг увімкнено (за замовчуванням).
  - `UBX_BAUD>0`: автоконфіг вимкнено; фільтр використовує цей baud напряму.
  - Зміни `UBX_BAUD` також застосовуються тільки після перезавантаження.
  - Gateway-модулі з власним MCU та схемою з двома або внутрішніми приймачами (наприклад Quadro GPS, UNA3, UNA4-SFE або подібні dual-F9P продукти) повинні працювати з `UBX_BAUD>0`; автобауд фільтра для цього класу модулів неможливий.
- Для UM980/UM981/UM982 або Mosaic X5 налаштуйте потік приймача так, щоб його протокол і baud відповідали потоку, який STM32 буде пересилати на FC.

## 6) Перевірки після першого запуску

У повідомленнях GCS перевірте:

- є повідомлення про запуск фільтра,
- лічильники GNSS зростають,
- немає повторюваних помилок зв'язку.

Якщо FC показує **No GPS config data**:

- перевірте протокол/baud GPS UART на FC,
- перевірте перехресне TX/RX підключення (`A11/A12` на F401, `C6/C7` на H743 UART-збірці),
- перевірте спільну землю.

Для H743 DroneCAN mode перевірте, що node з'являється у DroneCAN/SLCAN
tooling з node ID `42`, потім перевірте, що ArduPilot бачить DroneCAN GPS
instance.

## 7) Обов'язковий крок перед експлуатацією

Перед штатною роботою один раз перевірте наскрізний GPS-шлях до FC:

1. Підключіться до фільтра (`SYSID=42`) і встановіть `FCGPS_FWD=1`.
2. Дочекайтесь здорового GNSS у логах (`fix` і `nav` малі, супутники присутні, немає постійного no-fix стану).
3. Переконайтесь, що FC отримує GNSS-дані. Цей режим вмикає FC GPS UART і сирим потоком обходить DR1, стартову північну перевірку та огорожу півкулі, тому може перевірити UART-шлях навіть за стендових умов зі спуфінгом або південною півкулею.
4. Поверніть `FCGPS_FWD=0` для штатного anti-spoof режиму.

`FCGPS_FWD=1` використовуйте лише для діагностики. Не літайте з увімкненим режимом.

Цей commissioning step не застосовується до H743 DroneCAN mode, бо та
прошивка не має raw GPS UART bypass.

## 8) Примітка щодо типу збірки

Для штатної експлуатації використовується звичайна робоча прошивка, яку вже встановлює постачальник або сервіс.
