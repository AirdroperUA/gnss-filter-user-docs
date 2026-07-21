# WeAct H743 DroneCAN

> Магазин плати: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

Ця сторінка описує окрему H743-версію для WeAct Studio MiniSTM32H743VITX
з 3.3 V CAN-трансивером SN65HVD230. У цій версії GNSS заходить у фільтр по
UART, GPS, MS4525DO airspeed та HMC5983 compass передаються у польотний
контролер як native DroneCAN messages, а MAVLink2 від OpenIPC camera і самого
фільтра йде через ту саму CAN-шину. Фізичні serial порти FC для MAVLink/GPS не
використовуються.

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
- OpenIPC MAVLink2 UART: `PA10` RX, `PA9` TX, `115200`, 3.3 V logic
- спільна sensor I2C2 шина (`SENSOR_I2C`): `PB10` SCL, `PB11` SDA для
  MS4525DO і HMC5983
- два bidirectional `uavcan.tunnel.Targetted` порти: index `0` для camera,
  index `1` для MAVLink фільтра та FC telemetry
- USB-C залишається на `PA11/PA12`
- фізичні FC MAVLink serial і FC GPS serial вимкнені
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
| Camera TX до RX фільтра | `PA10` | OpenIPC camera TX | 3.3 V UART, cross TX -> RX |
| TX фільтра до camera RX | `PA9` | OpenIPC camera RX | 3.3 V UART, cross TX -> RX |
| Sensor I2C clock | `PB10` | MS4525DO і HMC5983 `SCL` | I2C2, спільна шина |
| Sensor I2C data | `PB11` | MS4525DO і HMC5983 `SDA` | I2C2, спільна шина |
| Sensor power | `3V3` | Sensor `VCC` | лише для підтверджених 3.3 V parts/modules |
| Sensor ground | `GND` | Sensor `GND` | спільна signal/power ground |
| CAN TX | `PB9` | `TXD` трансивера | FDCAN1_TX |
| CAN RX | `PB8` | `RXD` трансивера | FDCAN1_RX |
| CAN power | `3V3` | `VCC` трансивера | тільки 3.3 V модуль |
| Ground | `GND` | `GND` трансивера і FC CAN GND | спільна земля |
| CAN bus | трансивер | `CANH/CANL/GND` до FC | кручена пара для CANH/CANL |
| DR1 event | `PB5` | опційний LED/logger | 3.3 V pulse |
| USB-C | `PA11/PA12` | роз'єм USB-C на платі | не виводити ці піни в harness |

Camera і H743 повинні мати спільну signal ground. Не подавайте 5 V logic на
`PA9/PA10`. Живіть camera від окремого стабілізованого джерела, розрахованого
на camera/LTE load; ці UART піни не є виходом живлення.

Використовуйте 120 ohm termination на CAN-модулі тільки якщо H743 box стоїть
на фізичному кінці CAN-шини.

<a id="sensor-i2c-connector"></a>

### Окремий роз'єм SENSOR_I2C для airspeed/compass

HD-15 нижче вже повністю зайнятий. Не перепризначайте жоден його pin. Для
sensor I2C2 встановіть окремий keyed 4-pin роз'єм із чіткою міткою:

| Pin I2C-роз'єму | Сигнал | Всередині бокса | Sensor harness |
|-----------------|--------|----------------|----------------|
| 1 | `3V3_SENSOR` | захищена 3.3 V rail | VCC обох sensors, лише якщо вони 3.3 V-compatible |
| 2 | `GND` | box ground | GND обох sensors |
| 3 | `I2C2_SCL` | H743 `PB10` | SCL обох sensors |
| 4 | `I2C2_SDA` | H743 `PB11` | SDA обох sensors |

Перевірте numbering зі сторони mating face конкретного connector і key
housing так, щоб його не можна було вставити навпаки. До підключення sensor
перевірте pin 1 мультиметром. MS4525DO та HMC5983 підключаються паралельно до
однієї I2C-шини; вони не є CAN devices самі по собі.

Потрібен один ефективний комплект pull-ups SCL/SDA до **3.3 V** (типово
2.2-4.7 kohm залежно від capacitance harness). Багато breakout boards уже
мають pull-ups, тому перевірте повністю зібрану схему й не вмикайте паралельно
кілька занадто сильних комплектів. **Ніколи не використовуйте 5 V pull-ups**
на `PB10/PB11`. Тримайте harness коротким, подалі від motor/ESC та LTE power
wiring. I2C не призначений для довгого кабелю через весь апарат.

Default conversion MS4525 відповідає тільки повному TE ordering code
`4525DO-DS3AI001DP`: dual side ports, 3.3 V supply, transfer function A
(10-90% counts), I2C address `0x28`, bidirectional differential range
`-1..+1 psi` і negative pressure polarity, що відповідає ArduPilot pitot
convention у цій збірці. Перевірте **повне маркування/order code** sensor.
`DS5...`, інша address letter, інший pressure range, transfer function B,
absolute/gauge part або невідомий breakout не є drop-in replacement. Для них
треба змінити й заново перевірити firmware build settings voltage, address,
range, transfer function та polarity. На стенді подайте невеликий differential
pressure і переконайтесь, що FC показує зростання додатної airspeed; не
перевіряйте polarity вперше у польоті.

Magnetometer driver очікує HMC5983 за address `0x1E` та identification bytes
`H43`. Багато модулів, проданих як HMC5983, містять HMC5883-compatible або
невідомі clones. Лише відповідь на address scan не доводить тип. Firmware
відхиляє неправильний ID, але clone, що імітує `H43`, все одно може мати інші
gain/noise/temperature характеристики; використовуйте traceable part і
порівняйте його на стенді з відомим compass.

Жорстко закріпіть HMC5983 і запишіть його axis orientation. Розташуйте його
якнайдалі від motors, magnets, steel fasteners, high-current battery/ESC wires,
switching regulators, CAN transceiver і camera/LTE radio. MS4525 та pitot hoses
тримайте подалі від prop wash, leaks, sharp bends і water traps.

<a id="optional-hd-15-d-sub-box-connector"></a>

## HD-15 D-sub pinout для зовнішнього harness

Якщо H743, CAN-трансивер, дисплей і захист живлення знаходяться всередині
одного бокса, назовні виводьте тільки HD-15 D-sub. Це не VGA-інтерфейс.
Підпишіть роз'єм як `CAN/GNSS/CAMERA/POWER`.

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
| 13 | `CAM_MAV_TX_FROM_BOX` | OpenIPC camera RX | H743 `PA9` TX |
| 14 | `CAM_MAV_RX_TO_BOX` | OpenIPC camera TX | H743 `PA10` RX |
| 15 | `BOX_GND_B` | optional parallel ground | box ground |

Правила:

- HD-15 не несе raw `PB8/PB9`; CAN-трансивер має бути всередині бокса.
- `CANH/CANL` ведіть крученою парою.
- Живіть box мінімум через pins 4/6; для більшого струму додайте pins 5/15.
- Pin 9 є виходом живлення на GNSS receiver. Не back-power box через pin 9.
- Напруга `GNSS_VOUT_FUSED` має відповідати приймачу: деякі модулі мають 5 V
  `VIN`, але raw receiver може вимагати 3.3 V.
- Перехрестіть camera UART: pin 13/H743 `PA9` TX -> camera RX, camera TX ->
  pin 14/H743 `PA10` RX. Використовуйте 3.3 V logic і common ground.
- Додайте окремий camera signal-ground return до box ground; pins 13/14 самі
  по собі не є повним UART connection. Не використовуйте shield як signal GND.
- Pins 13/14 передають тільки UART data і не живлять camera. Додайте окреме
  належно захищене camera/LTE power, якщо його не спроєктовано в enclosure.
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
| Enable CAN driver | `CAN_P1_DRIVER = 1` | `CAN_P2_DRIVER = 2` |
| DroneCAN protocol | `CAN_D1_PROTOCOL = 1` | `CAN_D2_PROTOCOL = 1` |
| Bitrate | `CAN_P1_BITRATE = 1000000` | `CAN_P2_BITRATE = 1000000` |
| GPS type | `GPS1_TYPE = 9` | `GPS1_TYPE = 9` (`GPS2_TYPE` лише для навмисного другого GPS instance) |
| GPS auto-config | `GPS_AUTO_CONFIG = 1` | global parameter |
| Optional GPS node lock | `GPS1_CAN_OVRIDE = 42` | те саме (`GPS2_CAN_OVRIDE` лише для другого GPS instance) |

`CAN_Px_DRIVER` вибирає virtual driver. Таблиця навмисно прив'язує physical
CAN1 до driver 1, а physical CAN2 до driver 2; використовуйте `CAN_Dn_*`, що
відповідають призначеному номеру driver. H743 DroneCAN `v0.2.0+` реалізує два
virtual serial порти. Нижче наведено параметри для driver 1; для driver 2
замініть усі prefixes `CAN_D1_` на `CAN_D2_`:

| Призначення | ArduPilot parameter | Значення |
|-------------|---------------------|----------|
| Enable DroneCAN serial | `CAN_D1_UC_SER_EN` | `1` |
| Camera node | `CAN_D1_UC_S1_NOD` | `42` |
| Camera index | `CAN_D1_UC_S1_IDX` | `0` |
| Camera baud | `CAN_D1_UC_S1_BD` | `115` (115200) |
| Camera protocol | `CAN_D1_UC_S1_PRO` | `2` (MAVLink2) |
| Filter node | `CAN_D1_UC_S2_NOD` | `42` |
| Filter index | `CAN_D1_UC_S2_IDX` | `1` |
| Filter baud | `CAN_D1_UC_S2_BD` | `115` (115200) |
| Filter protocol | `CAN_D1_UC_S2_PRO` | `2` (MAVLink2) |

S1/index `0` є прозорим bidirectional каналом між OpenIPC camera UART і
ArduPilot. S2/index `1` є окремим каналом: він несе MAVLink2, який генерує H743,
і повертає FC telemetry для наявної EKF, barometer, arm-state, parameter та
status logic. Окремі serial IDs не дозволяють змішувати camera bytes з MAVLink
самого фільтра.
Значення ArduPilot `_PRO = 2` є serial-protocol setting; стандартний Targetted
DSDL кодує MAVLink2 як on-wire protocol value `1`.

Деякі OpenIPC cameras можуть залишатися у bootloader, якщо під час старту на
RX вже надходять bytes. За потреби встановіть `MAV_TELEM_DELAY = 5`; у старих
ArduPilot цей parameter може називатися `TELEM_DELAY`. Після зміни CAN або
DroneCAN serial parameters перезавантажте FC.

### ArduPilot setup для airspeed і compass

FC бачить обидва I2C sensors як DroneCAN devices від node `42`; не вибирайте
local-I2C MS4525 backend польотного контролера.

1. Для потрібного FC airspeed instance встановіть DroneCAN: зазвичай
   `ARSPD_TYPE = 8`. Якщо instance 1 уже зайнятий, використайте відповідний
   `ARSPD2_TYPE`, `ARSPD3_TYPE` тощо.
2. Встановіть відповідний `ARSPDx_USE` згідно з vehicle і control strategy.
   Для Plane вмикайте використання лише після bench check та airspeed
   calibration; перевірте offset, ratio, tube order і pre-arm status за
   актуальною процедурою ArduPilot.
3. Дозвольте ArduPilot автоматично знайти DroneCAN compass. У Mission Planner
   відкрийте `Setup -> Mandatory Hardware -> Compass`, переконайтесь, що є
   compass від node `42`, позначте/використайте його як external і встановіть
   потрібний priority.
4. Встановіть або auto-detect orientation HMC5983, потім виконайте повну
   compass calibration уже в остаточно зібраному vehicle. Не копіюйте offsets
   з іншого airframe/sensor. Перевірте напрям усіх axes і motor-current
   interference до використання цього compass для yaw.

ArduPilot автоматично визначає DroneCAN airspeed і compass publishers; для них
не потрібен virtual serial mapping. Валідний MS4525 sample публікується як
`uavcan.equipment.air_data.RawAirData` до 20 Hz. Валідний HMC5983 sample
публікується як `uavcan.equipment.ahrs.MagneticFieldStrength2`, sensor ID `0`,
до 25 Hz. Ці messages використовують ті самі node ID і CAN transceiver, що GPS
та обидва MAVLink tunnels.

Тримайте FC MAVLink stream rates помірними. У classic CAN кожен multi-frame
CAN frame переносить лише сім transport payload bytes, тому camera full duplex,
chatty filter port і 20/25 Hz sensor publications можуть наблизити 1 Mbps bus
до saturation. GPS і NodeStatus мають вищий priority. Червоний `MAV` row або ненульовий `ERR` row
означає loss/overload — зменште stream rates перед польотом. Жовтий `MAV` row
означає, що queued data застаріли після stalled link.
Неповні camera chunks збираються не довше 10 ms, щоб зменшити CAN overhead.
Якщо camera traffic у будь-якому напрямку не просувається 500 ms, bytes, які ще
залишаються у firmware queues, відкидаються замість відтворення після відновлення
link. Frames, вже передані до FDCAN controller, відкликати неможливо.

Прошивка публікує:

- `uavcan.protocol.NodeStatus`
- `uavcan.protocol.GetNodeInfo`
- `uavcan.equipment.gnss.Fix2`
- `uavcan.equipment.gnss.Auxiliary`
- `uavcan.equipment.air_data.RawAirData` для MS4525 differential pressure і
  sensor temperature, до 20 Hz
- `uavcan.equipment.ahrs.MagneticFieldStrength2` для HMC5983 magnetic field,
  sensor ID `0`, до 25 Hz
- `uavcan.tunnel.Targetted` для двох MAVLink2 virtual serial ports

MAVLink2 тунелюється, але raw GNSS NMEA, UBX та SBF не тунелюються. GPS
залишається native `Fix2/Auxiliary`, а фізичний FC GPS UART залишається
вимкненим.

### Septentrio Mosaic X5 SBF input

H743 DroneCAN firmware `v0.1.9+` може парсити native SBF від Mosaic X5 на GNSS
UART, коли `GNSS_TYPE=2`. Налаштуйте Mosaic stream у RxTools/Web UI на
`460800`, 8N1 і SBF output. Увімкніть ці блоки на stream, підключеному до
H743 `PA3/PA2`:

| SBF-блок | Рекомендована частота | Використання firmware |
|----------|------------------------|-----------------------|
| `PVTGeodetic` | 5-10 Гц | fix mode, позиція, MSL/ellipsoid height, velocity, satellites, receiver clock |
| `DOP` | 1-5 Гц | HDOP/VDOP/PDOP/TDOP для DroneCAN і guards |
| `ReceiverTime` | 1 Гц | UTC timestamp у DroneCAN `Fix2` |
| `MeasEpoch` | 1-5 Гц | C/N0/SNR guard і temporal-correlation частина `DR_CONF` |
| `PosCovGeodetic` | 1-5 Гц | position covariance у DroneCAN `Fix2` |
| `VelCovGeodetic` | 1-5 Гц | velocity covariance у DroneCAN `Fix2` |

H743 firmware також приймає Mosaic NMEA у `GNSS_TYPE=2`, але SBF є бажаним
профілем для H743 DroneCAN: він передає velocity, DOP, covariance, receiver
time і C/N0 у binary format без serial GPS driver на flight controller.

Для spoof-confidence scoring Mosaic SBF `MeasEpoch` дає C/N0
temporal-correlation сигнал. Він не вмикає pseudorange-residual signal: цей
score залишається тільки для u-blox, бо залежить від UBX `NAV-SAT` `prRes`.

Оскільки FC отримує native DroneCAN GPS, H743 DroneCAN не є byte-for-byte GPS
packet pass-through. Прошивка парсить receiver stream і публікує ті самі live
fix values у DroneCAN units. Вона не генерує synthetic GPS coordinates, не
blend-ить coordinates і не переписує raw NMEA/UBX/SBF packets; у DR1 вона suppress
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

Коли налаштовано S2/index `1`, MAVLink2 самого H743 доходить до flight
controller, а FC telemetry повертається до фільтра. GCS, підключена через FC,
може вибрати filter system ID `42`, якщо її UI підтримує MAVLink system
selection. DroneCAN node Params лишається найпрямішим способом налаштування на
літальному апараті.

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

H743 DroneCAN тримає locked off лише raw FC GPS UART settings:

- `FCGPS_UART = 0`
- `FCGPS_FWD = 0`

`RJ_REQEKF` та інші FC-telemetry-dependent guards доступні, бо S2/index `1`
передає MAVLink2 від flight controller до фільтра.

## Дисплей

H743 DroneCAN `v0.4.0` використовує професійний висококонтрастний темний
інтерфейс на вбудованому кольоровому TFT-дисплеї ST7735 з фактичною
роздільною здатністю 80 x 160 пікселів. Це не OLED. Дисплей не має сенсорного
керування або кнопок перемикання сторінок.

Одразу після ввімкнення з'являються анімоване status ring та progress rail,
поки ініціалізується GNSS-приймач. Rounded boot tiles показують версію firmware
і стан node, потім boot screen переходить від GNSS initialization до
`READY` / `BOOT GUARD`, а далі відкриває dashboard. Після splash hero
залишається у стані
`FILTER CHECK / GUARD` протягом реального configurable startup spoof-guard
interval і не може показати `FILTER ONLINE / RUN`, доки ці перевірки ще
затримані. Напис `USB CONFIG` означає
звичайний USB-C management link застосунку. Він не означає, що ROM DFU вже
активний: для ROM DFU все одно потрібно тримати `BOOT0` під час reset або
power-up.

Dashboard постійно зберігає три області:

- верхній activity header для product, CAN і MAVLink
- великий кастомний штрихований та контурний hero `OK`, `!!` або `XX` з написом
  `FILTER ONLINE`, `FILTER CHECK`, `FILTER BLOCK` чи `FC ALERT` та короткою
  причиною, наприклад `RUN`, `GPS`, `CAN ERR`, `SENSOR` або причиною активного
  DR1
- footer зі станом GPS publication: `PUB+` означає recent Fix2, прийнятий у
  локальну DroneCAN transmit queue, `PUB?` — gate
  відкритий, але recent Fix2 немає, а `PUB-` — publication blocked/unavailable;
  далі показано `DR0`/`DR1` та DroneCAN node фільтра, наприклад `N42`

`PUB+` не є підтвердженням прийому від FC. Перед польотом окремо перевірте
DroneCAN/Mission Planner telemetry на FC.

У центральній частині використано proportional body text, компактні icons,
rounded information tiles, gradient health rails і segmented activity rails.
Автоматично перемикаються чотири сторінки:

| Сторінка | Що показує |
|----------|------------|
| **Overview** | Свіжість GPS fix і satellites, FC node health та generic UAVCAN node mode, ArduPilot `NotifyState`, arm і safety state |
| **Sensors** | Свіжість MS4525/HMC5983, differential pressure, sensor temperature і magnetic-field magnitude |
| **Links** | CAN та сумарні camera/filter MAVLink TX/RX counters, CAN errors, MAVLink dropped/expired counters |
| **System** | I2C error/recovery counters, firmware version/build, uptime або Mosaic SBF accepted/bad-CRC counters |

Page dots та underline у footer показують активну сторінку. Коли фільтр
справний, а FC гарантовано disarmed, кожна сторінка залишається приблизно п'ять
секунд, після чого UI переходить до наступної через eased five-frame slide.
Ручного вибору сторінки немає. Після arm або появи warning/alert автоматичне
перемикання та slide transitions зупиняються.
Sensor, CAN або MAVLink warning фіксує Sensors чи Links page, яка пояснює
проблему; поганий FC NodeStatus, GPS/guard warning або armed FC фіксує Overview.
Filter block чи high-priority ArduPilot notification вмикає dedicated alert
takeover у центральній області, а hero state, невелика activity animation і
footer залишаються видимими.
Rotation також чекає fresh FC arming-status broadcast, який явно підтверджує
disarmed state. Якщо arm state невідомий або FC armed, Overview у третьому рядку
коротко показує прихований sensor/link warning. Одночасні filter і FC alerts
позначаються як `DUAL ALERT`, тому жодна несправність не приховується.

Redesign змінює лише presentation. Стан дисплея не може відкрити spoofing gate
або перенаправити трафік: DR0/DR1 enforcement, DroneCAN GPS/sensor publication,
OpenIPC tunnel та власний MAVLink2 virtual port фільтра зберігають попередню
поведінку.

Для pixel-exact перегляду всіх сторінок і анімацій без прошивання плати виконайте:

```powershell
python tools/render_h743_display_preview.py
```

Потім відкрийте `dist/h743_display_preview.html`. Preview використовує той самий
portable C++ RGB565 renderer, що й H743 firmware, без відтворення графіки
браузерними шрифтами.

Overview показує generic UAVCAN node mode, а не точну назву ArduPilot flight
mode на кшталт Loiter, Auto, Guided або RTL. MAVLink tunnel працює незалежно
від сторінки дисплея.

Сприймайте екран як зручну локальну діагностику, а не як авторитетний flight
instrument. Його counters та freshness indicators не замінюють Mission Planner
pre-arm checks, DroneCAN inspection, sensor calibration або аналіз flight log.
Зокрема, magnetic-field magnitude не є calibrated heading, а `FILTER ONLINE` не
доводить правильність compass orientation, pitot plumbing, CAN termination чи
MAVLink routing.

## DR0 / DR1

У DR0:

- `Fix2` публікується на кожен свіжий GNSS update, максимум 10 Hz
- `Auxiliary` публікується 1 Hz
- `NodeStatus` лишається online

У spoof/fault DR1:

- `Fix2` і `Auxiliary` зупиняються
- FC перестає отримувати свіжий GPS від цього node
- `NodeStatus` продовжується 1 Hz з warning health
- дисплей фіксується на червоній alert page `BLOCK` з активною причиною, а
  footer показує `PUB-` і `DR1`

No-fix, low satellites, boot guard, або GNSS reconfiguration теж можуть
suppress `Fix2/Auxiliary`, включно з latched no-fix/low-sat DR1 internally,
але ці стани лишають `NodeStatus` health `OK` і показують output block тільки
через vendor status bits та onboard screen. Це прибирає ArduPilot
`PreArm: DroneCAN: Node 42 unhealthy!`, коли GPS просто ще не готовий.

Обидва MAVLink2 virtual ports залишаються активними у DR0 і DR1. DR1 блокує
тільки GPS `Fix2/Auxiliary`, але не відключає OpenIPC camera tunnel або MAVLink2
самого фільтра. S2/index `1` зберігає FC telemetry input, EKF-status і barometer
comparisons, `STATUSTEXT`/`NAMED_VALUE`, parameters та іншу наявну MAVLink
logic. Фізичний `FCGPS_FWD` raw UART bypass залишається недоступним.

MS4525 `RawAirData` і HMC5983 `MagneticFieldStrength2` також не залежать від
DR0/DR1. Spoofing decision блокує лише GNSS `Fix2/Auxiliary`; він навмисно не
вимикає airspeed, compass, NodeStatus, camera MAVLink або MAVLink фільтра.
Несправний чи від'єднаний I2C sensor припиняє тільки свою валідну sensor
publication і має розглядатися як окремий pre-arm/maintenance fault.

GNSS-only guards активні: no fix, low satellites, position jump, altitude
rate/jump, SNR anomaly, hemisphere/geofence, heading reversal, GPS time sanity,
velocity-position consistency і receiver clock jump, якщо дані доступні.

## Перевірка

1. Прошийте `weact_mini_h743vitx_dronecan_usb` або ST-Link build.
2. Підключіть GNSS до `PA2/PA3`.
3. Перехрестіть 3.3 V OpenIPC UART: camera TX -> `PA10`, `PA9` -> camera RX,
   додайте common ground та окреме належне camera power.
4. Через окремий keyed connector підключіть обидва sensors до shared
   `PB10` SCL, `PB11` SDA, 3.3 V і GND. До power-up перевірте повний MS4525
   ordering code та HMC5983 identity.
5. Підключіть `PB9/PB8` до SN65HVD230, а `CANH/CANL/GND` до FC CAN.
6. У ArduPilot увімкніть CAN driver, DroneCAN protocol, 1 Mbps і `GPS_TYPE=9`.
7. Налаштуйте S1 як node `42`/index `0`/115/MAVLink2 і S2 як node
   `42`/index `1`/115/MAVLink2.
8. Встановіть airspeed instance FC на DroneCAN (`ARSPD_TYPE=8` для instance 1),
   переконайтесь, що node-42 compass з'явився, і перезавантажте FC.
9. Перевірте, що H743 screen світиться і показує GNSS/filter state.
10. Перевірте, що DroneCAN node ID `42` видно у DroneCAN/SLCAN tooling.
11. Перевірте, що ArduPilot бачить DroneCAN GPS, airspeed і node-42 compass,
    camera MAVLink2 і filter
    system ID `42`.
12. За однакового тиску в обох pitot ports виконайте zero calibration; потім
    обережно подайте differential pressure і перевірте positive stable airspeed.
13. Після final installation відкалібруйте compass, перевірте axes/orientation
    і motor-current interference, а також кілька хвилин роботи з active LTE.
14. Викличте bench DR1 і переконайтесь, що GPS публікації зупинились, а
   `NodeStatus` залишився online.
15. Перевірте, що airspeed, compass і обидва MAVLink2 канали працюють у DR1;
    приберіть причину DR1 і переконайтесь, що GPS publishing відновився.

## Якщо щось не працює

- Node не видно: перевірте `CAN_Dx_PROTOCOL=1`, bitrate `1000000`, CANH/CANL,
  common ground, termination на кінцях шини, `PB9 -> TXD`, `PB8 <- RXD`.
- FC не бачить GPS: перевірте `GPS1_TYPE=9`, свіжий GNSS fix, footer `PUB+` /
  `DR0`, а також що hero card не показує `BLOCK` із причиною `GPS`, `NOFIX`,
  `SATS`, `JUMP`, `FENCE` або іншою DR1 причиною.
- Для firmware старішої за H743 DroneCAN `v0.1.2` перевірте
  `GPS_AUTO_CONFIG=1`.
- Якщо є кілька DroneCAN GPS nodes, задайте `GPS1_CAN_OVRIDE=42` або override
  для відповідного GPS instance.
- MAVLink tunnel не працює: перевірте `CAN_D1_UC_SER_EN=1`, S1 node `42`/index
  `0`/baud `115`/protocol `2` і S2 node `42`/index `1`/baud `115`/protocol `2`.
  Для CAN driver 2 використовуйте `CAN_D2_UC_*`.
- Перевірте camera wiring: camera TX -> `PA10`, `PA9` -> camera RX, 3.3 V logic,
  common ground і MAVLink2 at 115200. Якщо camera не boot-иться з UART,
  спробуйте `MAV_TELEM_DELAY=5` і перевірте її power supply.
- Airspeed/compass не видно: перевірте, що sensor firmware options увімкнені,
  `PB10 -> SCL`, `PB11 <-> SDA`, 3.3 V power і common ground. Idle SCL/SDA
  повинні бути приблизно 3.3 V; **5 V pull-up небезпечний для H743**.
- Перевірте один коректний effective pull-up set, swapped SCL/SDA, shorts,
  cable length/noise та duplicate I2C addresses.
- Для MS4525 перевірте повний code `4525DO-DS3AI001DP`, address `0x28`, sign
  і magnitude з відомим малим pressure. Не маскуйте wrong sensor range тільки
  параметром `ARSPD_RATIO`. На FC має бути `ARSPDx_TYPE=8` (DroneCAN), не type
  `1` (local-I2C MS4525 на самому FC).
- Для HMC5983 перевірте address `0x1E` та ID `H43`. Якщо дешевий module не
  приймається або нестабільно калібрується, підозрюйте clone, а не послаблюйте
  identity check. У Mission Planner перевірте detected compass device ID,
  priority/orientation і повторіть calibration у final position.
- DR1 не вимикає ці sensors. Якщо airspeed/compass зникає у DR1, окремо
  діагностуйте I2C integrity, CAN load/errors і sensor health.
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

## Посилання на протоколи

- [Official WeAct MiniSTM32H7xx V12 schematic](https://github.com/WeActStudio/MiniSTM32H7xx/blob/master/Hardware/STM32H7xx%20SchDoc%20V12.pdf)
- [Official WeAct ST7735 LCD driver](https://github.com/WeActStudio/MiniSTM32H7xx/blob/master/SDK/HAL/STM32H743/03-LCD_Test/Drivers/BSP/ST7735/lcd.c)
- [DroneCAN `uavcan.tunnel.Targetted` DSDL](https://github.com/DroneCAN/DSDL/blob/master/uavcan/tunnel/3001.Targetted.uavcan)
- [DroneCAN `uavcan.equipment.air_data.RawAirData` DSDL](https://github.com/DroneCAN/DSDL/blob/master/uavcan/equipment/air_data/1027.RawAirData.uavcan)
- [DroneCAN `uavcan.equipment.ahrs.MagneticFieldStrength2` DSDL](https://github.com/DroneCAN/DSDL/blob/master/uavcan/equipment/ahrs/1002.MagneticFieldStrength2.uavcan)
- [ArduPilot DroneCAN serial-port setup](https://ardupilot.org/sub/docs/common-dronecan-serial.html)
- [ArduPilot DroneCAN setup](https://ardupilot.org/copter/docs/common-uavcan-setup-advanced.html)
- [ArduPilot advanced compass setup](https://ardupilot.org/copter/docs/common-compass-setup-advanced.html)
- [TE Connectivity `4525DO-DS3AI001DP`](https://www.te.com/en/product-4525DO-DS3AI001DP.html)
- [OpenIPC FPV/UART guidance](https://github.com/OpenIPC/wiki/blob/master/en/fpv.md)
