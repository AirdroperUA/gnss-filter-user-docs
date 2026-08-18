# Інструкція з налаштування

> Де купити плату: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

> **Обов'язкова перевірка плати під час провізіонування:** перед читанням UID/
> option bytes, RDP, стиранням або записом перевірте фізичну PCB та маркування
> MCU. Введіть точно `F401CC BLACKPILL` для BlackPill 256 KiB або
> `WEACT H743VI` для WeAct 2 MiB. Перевірка повторюється після кожного
> перепідключення чи зміни SWD/DFU; `--yes` її не обходить. F401 128 KiB та
> H743 1 MiB відхиляються, бо production layout не вміщується у їх flash.

## 1) Передумови

- STM32F401 filter board встановлена та попередньо прошита, або WeAct H743
  прошита відповідною standalone/H743 DroneCAN development-прошивкою.
- На платі має бути встановлена firmware family, яка відповідає схемі
  підключення.
- Прошивка FC: ArduPilot 4.6.1 або новіша; FC має відповісти на запит
  `AUTOPILOT_VERSION`. Firmware v0.5.30 одразу suppresses GNSS, поки ця
  identity невідома або unsupported.
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
режим публікує native DroneCAN GNSS messages, не використовує physical FC
MAVLink або FC GPS UART і переносить MAVLink2 через два DroneCAN virtual serial
ports.

Firmware defaults:

- DroneCAN node ID: `42`
- FC DroneCAN node filter: `0` — bind лише після двох valid Targetted transfers,
  адресованих node `42` від одного source; lease спливає через три секунди без
  наступного valid transfer. Set `FILTER_DRONECAN_FC_NODE_ID` at build time,
  щоб зафіксувати конкретний FC node на multi-node CAN bus.
- CAN bitrate: `1 Mbps`
- OpenIPC camera UART: camera TX -> H743 `PA10` RX, H743 `PA9` TX -> camera RX,
  3.3 V logic, common ground, `115200` baud
- Published messages: `uavcan.protocol.NodeStatus`,
  `uavcan.protocol.GetNodeInfo`, `uavcan.equipment.gnss.Fix2`,
  `uavcan.equipment.gnss.Auxiliary`, `uavcan.tunnel.Targetted`
- Onboard screen: filter OK/warn/no-OK with a `WHY` reason line, GNSS publish
  state, CAN counters, FC DroneCAN node health/mode, arm/safety state, and an
  ArduPilot vehicle-state row from `ardupilot.indication.NotifyState` when that
  broadcast is present

Параметри польотного контролера для CAN-порту, до якого підключений H743 node:

- `CAN_P1_DRIVER = 1` для CAN1, або `CAN_P2_DRIVER = 2` для CAN2
- `CAN_D1_PROTOCOL = 1` для CAN1, або `CAN_D2_PROTOCOL = 1` для CAN2
- `CAN_P1_BITRATE = 1000000` або `CAN_P2_BITRATE = 1000000`
- `GPS1_TYPE = 9` для DroneCAN GPS
- `GPS_AUTO_CONFIG = 1` for default serial-only GPS auto-config mode
- optional: `GPS1_CAN_OVRIDE = 42` if the bus has more than one DroneCAN
  GPS-like node

Значення `CAN_Px_DRIVER` вибирає virtual driver. Ці приклади навмисно
прив'язують physical CAN1 до driver 1, а physical CAN2 до driver 2; використовуйте
`CAN_Dn_*`, що відповідають призначеному номеру driver. Після зміни CAN driver
parameters перезавантажте FC. Якщо H743 node стоїть
на фізичному кінці CAN-шини, увімкніть 120 ohm termination на CAN-модулі;
інакше залиште termination вимкненим.

### H743 DroneCAN MAVLink2 virtual ports

Увімкніть DroneCAN serial transport і створіть два окремі порти для node `42`:

| Функція | Node/index | ArduPilot driver 1 parameters |
|---------|------------|-------------------------------|
| Enable transport | - | `CAN_D1_UC_SER_EN = 1` |
| OpenIPC camera, bidirectional | node `42`, index `0` | `CAN_D1_UC_S1_NOD = 42`, `CAN_D1_UC_S1_IDX = 0`, `CAN_D1_UC_S1_BD = 115`, `CAN_D1_UC_S1_PRO = 2` |
| H743 filter MAVLink + FC telemetry | node `42`, index `1` | `CAN_D1_UC_S2_NOD = 42`, `CAN_D1_UC_S2_IDX = 1`, `CAN_D1_UC_S2_BD = 115`, `CAN_D1_UC_S2_PRO = 2` |

Для virtual driver 2 використовуйте відповідні `CAN_D2_UC_*` parameters.
Index `0` прозоро з'єднує OpenIPC UART з ArduPilot. Index `1` несе MAVLink2
самого фільтра до FC і повертає FC telemetry для EKF/barometer/status logic.
Native GPS лишається `Fix2/Auxiliary`; raw NMEA/UBX/SBF не тунелюється.

Якщо UART traffic заважає camera boot, встановіть `MAV_TELEM_DELAY = 5` (у
старих ArduPilot — `TELEM_DELAY`). Живіть camera від відповідного окремого
camera/LTE supply; `PA9/PA10` — 3.3 V signals, а не power output.

Development USB-C ROM DFU flash:

```powershell
pio run -e weact_mini_h743vitx_dronecan_usb -t upload
```

Збірка H743 secure-app template, скомпонованого за адресою `0x08020000`:

```powershell
pio run -e weact_mini_h743vitx_dronecan_phaseb_app_usb
```

Пряме завантаження phase-B template навмисно заблоковано. Використовуйте
AirDroper provisioning app, щоб застосунок був прив'язаний до UID і мав
відповідні signed metadata та правильний bootloader layout. Лише standalone
environment `weact_mini_h743vitx_dronecan_usb` є прямим development ROM DFU
шляхом.
The onboard display shows standard DroneCAN node mode/health and ArduPilot
`NotifyState` vehicle-state bits, not exact flight-mode names such as Loiter or
Auto.

Щоб увійти в DFU: утримуйте `BOOT0`, зробіть reset або power-cycle WeAct H743,
потім підключіть USB-C.

Production H743 DroneCAN boards використовують signed H743 bootloader layout:
bootloader at `0x08000000`, app at `0x08020000`, metadata at `0x081E0000`.
Desktop app `2026.08.02.1+` може оновлювати вже активовану H743 через USB-C ROM
DFU. Спочатку він читає RDP, а потім для RDP0 і RDP1 завжди робить mass erase та
записує повний перевірений пакет app + metadata + bootloader. Для RDP1 потрібні
підтвердження UID-short, перевірка RDP0 після unlock і фізичне повторне читання
UID до запису. Про успіх повідомляється лише після окремого читання option bytes,
яке підтвердило фінальний RDP1; якщо RDP не читається/не розбирається або lock не
підтверджено, оновлення зупиняється без повідомлення про успіх.

Licensed H743 DroneCAN provisioning через ST-Link/SWD:

```powershell
python tools/gnss_provision.py activate --target h743_dronecan --license GF-XXXX-XXXX-XXXX --server https://gps.airdroper.org
```

Для desktop app: оберіть **Board target -> H743 WeAct DroneCAN**. Для ST-Link
activation/update оберіть **Update transport -> ST-Link (SWD)**. Для вже
активованої H743 можна обрати **Update transport -> USB-C ROM DFU**; якщо app
просить power-cycle після RDP removal, тримайте `BOOT0`, щоб плата повернулась
у ROM DFU.

Update service має вкладені permanent H743 fuel-safety boundaries. Promotion
`v0.5.30+` назавжди виключає pre-`v0.5.30` readers, бо вони не зберігають
lost/known fuel provenance. Після першого promotion `v0.5.31+` також назавжди
виключається `v0.5.30`, бо вона може публікувати fresh zero-consumption EFI за
нульової capacity. Owner-authorized rollback не може перейти жодну boundary.
Recovery після цього cutover має бути forward-versioned build `v0.5.31+`.

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
  warning health для spoof/fault DR1 reasons або enabled I2C sensor, який
  missing/stale після п'яти секунд startup grace. Ordinary no-fix, low
  satellites, boot guard або GNSS reconfiguration output suppression сам по
  собі лишає DroneCAN node health `OK`.
- UART-build параметри фільтра змінюються у Mission Planner:
  - `Config/Tuning` -> `Full Parameter List`
  - виберіть STM32 (`SYSID=42`)
  - `Refresh Params` -> змініть значення -> `Write Params`
- Перед тюнінгом UART-збірок встановіть [AirDroper Mission Planner Mod](https://gps.airdroper.org/download/mission-planner-mod), щоб Mission Planner показував описи, діапазони, одиниці та підписи варіантів для параметрів STM32, а не лише сирі назви.
- H743 DroneCAN `v0.1.4+` params змінюються в Mission Planner:
  `SETUP -> Optional Hardware -> DroneCAN/UAVCAN -> node 42 -> Params`, далі
  `Write Params` і `Commit Params`.
- H743 DroneCAN `v0.1.5+` також можна tuning напряму через USB-C: boot normal
  app без `BOOT0`, підключіть Mission Planner до H743 COM port на `115200`,
  потім використайте `CONFIG -> Full Parameter Tree/List`.
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

## 8) Стендова перевірка recovery з DR1

Airborne quorum потребує щонайменше одного незалежного non-GNSS witness:

| Row | Коли стає independent witness |
|-----|-------------------------------|
| Barometric vertical rate | реальний набір або зниження щонайменше 3 м/с |
| Ground speed проти airspeed | live pitot щонайменше 12 м/с |
| GNSS course проти FC yaw | справжній розворот планера |

На нерухомому столі жоден із них недоступний, тому airborne quorum правильно
не завершується. H743 DroneCAN v0.5.30 має окремий parked/disarmed ground
release. Він не залежить від generic three-row pass count. Крім наявних gates
disarmed state, FC motion, position agreement, receiver verdict, dwell і
budget, він вимагає:

- нуль evidence rows із FAIL;
- GNSS-time row у стані PASS;
- fresh, finite, non-negative receiver speed не вище 4 м/с;
- speed із поточного location epoch, віком/skew не більше 1500 мс. Для passive
  NMEA це RMC speed, узгоджений з GGA/RMC fix epoch.

Optional GSV/SNR evidence може заборонити release, якщо явно FAIL, але не
зобов'язане існувати. Тому deployed UM980 GGA/RMC/AGRICA profile може завершити
stationary ground release при `SNR=NA`. У recovery line `EVM` означає відсутнє
named ground evidence, `EVF` — contradiction, а зростання `gnd=` — progress
parked release. Поля `ev...W...` описують лише airborne quorum.

Щоб перевірити саме airborne path, рухайтесь із receiver/FC так, щоб отримати
реальний turn/climb/pitot witness. Power-cycle швидко повертає bench unit у
DR0, але recovery не тестує. Lab-only waiver build із
`FILTER_REMOTE_OPERATOR_WAIVER_ENABLE=1` скасовує лише witness requirement;
він не автентифікований, compiled out з усіх flight builds і **ніколи не має
використовуватися у польоті**.

## 9) Примітка щодо типу збірки

Для штатної експлуатації використовується звичайна робоча прошивка, яку вже встановлює постачальник або сервіс.
