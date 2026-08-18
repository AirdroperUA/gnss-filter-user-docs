# Журнал змін

> Де купити плату: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

Усі значні зміни прошивки та інструментів задокументовані тут.

---

## H743 DroneCAN v0.5.30 — 2026-08-17 (corrective candidate)

- Фільтр тепер запитує і перевіряє `AUTOPILOT_VERSION` перед публікацією GPS.
  Невідома версія або ArduPilot старіший за 4.6.1 негайно блокує GPS;
  15-секундна затримка стосується лише warning messages.
- Parked recovery працює з named GNSS-time та fresh same-epoch receiver-speed
  evidence. Optional GSV/SNR не потрібен; явна contradiction все одно блокує
  release. Airborne recovery rules не змінені.
- Навіть із `LOG_LOC=1` coordinates з'являються лише у periodic true-DR0 status,
  ніколи у trip/DR1/synthetic/blend messages.
- Fuel burn рахується крізь FC-link і FC-version blocks. Кожен boot починається
  з припущення, що двигун міг працювати, доки fresh disarmed, valid zero-RPM і
  closed-throttle evidence разом не підтвердять зупинку.
- Після першого promotion H743 `v0.5.30+` update service назавжди відмовляється
  promote або deliver будь-яку pre-`v0.5.30` H743 firmware. Старі fuel readers
  не зберігають нову lost/known provenance безпечно, тому цю global межу не
  перетинає навіть generic owner-authorized rollback.
- Missing, invalid або legacy V1 backup record тепер означає TOTAL LOST при
  кожному boot, включно зі звичайним вмиканням: POR/PDR не доводить, що ви
  заправились. Missing, corrupt або іншим чином invalid H743 tune journal також
  анулює surviving numeric total, бо provenance його місткості, густини та
  моделі невідомий. EFI packets припиняються, доки ви не сядете або лишитесь на
  землі, не отримаєте fresh stopped-engine quorum (disarmed + valid zero RPM +
  closed throttle) і повторно не запишете `FUEL_CAPG`, навіть коли його числове
  значення не змінилося. Disarmed alone відхиляється. Прийнятий reset скасовує
  pending charge старого total. Valid V2 restore в іншому разі отримує
  обмежене консервативне 25-секундне reset-gap нарахування за rated
  power плюс перший measured interval. До risky setup його retained known record
  надійно позначається TOTAL_LOST і знову committed як known лише після
  інтегрування обох нарахувань. Якщо reset станеться раніше, наступний boot
  лишиться LOST до stopped-quorum `FUEL_CAPG` і не використає stale known total
  повторно. 25 с покривають backup staleness, найдовший setup UM980, інший
  startup overhead і запас; у H743 немає Phase-C boot wait. Це не точне
  вимірювання витрати. Ніколи не виконуйте Phase-C maintenance при працюючому
  двигуні.
- Змінений `FUEL_CAPG` лишається TOTAL LOST і EFI-silent до verified
  asynchronous save tune journal. Accepted-write message не доводить durability;
  failed save лишається LOST. Factory reset позначає fuel LOST до початку flash,
  тому навіть failed attempt може консервативно вимагати stopped-engine recovery
  через `FUEL_CAPG`.
- `FUEL_DENS` тепер потребує того самого fresh stopped-engine quorum. Фактична
  зміна позначає fuel LOST, скасовує старий CAPG commit і відхиляє capacity
  writes з `FUEL_CAPG blocked: wait for FUEL_DENS save` до verified save success.
  Сам save density не відновлює EFI: після нього знову запишіть `FUEL_CAPG` за
  stopped-engine quorum, щоб установити fresh zero.
- Secondary H743 USB Mission Planner працює з default DTR-low open/reconnect і
  незалежними USB/FC packet counters. Сам private spoof-position stream
  лишається функцією v0.5.29+.
- Mission Planner plugin `0.3.1` робить map legend opaque та тримає її ліворуч
  від штатних zoom controls Mission Planner, прибираючи white-line repaint
  flicker після resize або зміни DPI.
- `PARKED_MOVE` тепер показується як `PARKED MOVE` (або `PARKED` на екрані
  плати); H743/UM980/build docs та parameter descriptions виправлено. Значення
  firmware parameters/defaults не змінені. Mission Planner package додає
  aircraft-specific FC preset для бака 5 л: BATT1 зберігається, DroneCAN EFI
  вмикається на перевіреному вільному BATT2, а 4000 mL показуються як usable
  fuel із 1000 mL estimator-error reserve. Automatic FC fuel failsafe actions
  лишаються off до завершення HIL aircraft.

v0.5.29 був лише inactive uploaded candidate і ніколи не promoted. v0.5.30 ще
не має hardware/HIL qualification і не promoted publicly; v0.5.25 на момент
цього запису лишається public production release.

---

## H743 DroneCAN v0.5.29 — 2026-08-17

Замінює v0.5.28. Додає live overlay спуфінгу в Mission Planner.

### Нове: видно, куди спуфер тягне координату приймача

Пакет AirDroper Mission Planner тепер встановлює plugin зі status strip,
детальним telemetry window та map overlay. Під час DR1 він показує:

- **червоний aircraft:** координату й trail, які повідомляє недовірений GNSS-приймач;
- **помаранчевий aircraft:** wind-blind dead-reckoning reference фільтра;
- **зелений aircraft:** оцінку позиції польотного контролера;
- лінії distance/bearing, причину й confidence DR, freshness та RF/jamming
  diagnostics.

Ці назви принципові. Червона точка — місце, яке повідомляє GNSS-приймач, а не
виміряна фізична позиція літака. Помаранчева оцінка може дрейфувати через вітер
або завмерти при stale speed/yaw. Зелена — оцінка FC. Жодна з них не є
гарантованим ground truth; stale map points plugin приховує.

Для live червоної/помаранчевої позиції потрібен другий USB-C кабель напряму від
H743 до комп'ютера Mission Planner. FC лишається primary link, а COM port H743
додається як secondary link на 115200 baud. Недовірені координати йдуть лише в
USB і ніколи не входять у DroneCAN MAVLink tunnel до FC. Без USB стан/причина/
confidence DR працюють, але live spoof path — ні.

Для flight controller пакет містить reviewed ten-row
`arduplane_FC_4.6.3_h743_dronecan_CAN1_core.param`. Завантажуйте його в
ArduPlane 4.6.3/SYSID 1; fresh disabled-CAN setup може потребувати три
load/write passes із reboot/reconnect/refresh, доки з'являться всі hidden rows.

Це USB-рішення призначене для стенда або фізично tethered GCS. Для long-range
потрібен окремий out-of-band link. Перед польотом перевірте plugin на стенді з
одночасним raw CAN capture: у DR1 на CAN не повинно бути ні GPS
`Fix2`/`Auxiliary`, ні private position records `SP_*`.

### Нове: provisional live напрямок на глушник/спуфер

Mission Planner plugin `0.3.0` додає фіолетову пунктирну RF-вісь. Після
щонайменше 20 samples і справжнього розвороту він може показати
`b / b+180°`; коли evidence недостатньо, видно `COLLECTING` або точну причину
`ABSTAIN`. 90° — практичний мінімум, а повне коло значно краще.

Це **невалідована двостороння вісь**, а не стрілка, range чи position джерела.
Fit відкидає звичайний approach/range trend, слабкий signal, погану geometry та
неузгоджені RF metrics. Fixed segment не довший за 120 с; result позначено
provisional, бо він може рухатися з новими samples. Показаний sigma не враховує
age курсу FC.

Відкрита RF-вісь працює через звичайну телеметрію FC. Другий private USB
потрібен для червоної/помаранчевої tracks і для map intersection, бо лише цей
link дає sample-aligned anchors рухомої DR reference. Fit виконується лише у
Mission Planner/offline tools і не може змінити DR1 чи керування літаком.

### Нове: aircraft icons і guarded intersection трьох осей

Червона/помаранчева/зелена позиції тепер мають heading-aware aircraft icons,
ненапрямлену точку fallback без fresh heading і постійну legend. **Capture
qualified axis** фіналізує строгий неперекривний RF
segment у mean position рухомої DR reference. Після трьох сумісних осей із
рознесених точок Mission Planner може показати фіолетову мішень і пунктирне
коло geometry sensitivity.

Qualification навмисно важка: кожний segment потребує 40 samples за 20–120 с,
strong/stable two-metric evidence і 90% moving-reference coverage. Три осі
треба зібрати за три хвилини: кожна пара anchors має бути рознесена мінімум на
500 м, кожна пара axis directions — мінімум на 30°, з однаковими private-USB
session/event/metric та gates yaw-age/distance/conditioning/perturbation/
disagreement. Stale чи failed gate прибирає мішень, а не залишає стару answer.
Bounded local projection працює лише між 70°S і 70°N та включає map-scale
distortion у показану sensitivity bound.

Напис **UNVALIDATED INTERFERENCE-AXIS INTERSECTION — ADVISORY ONLY** означає,
що це не located jammer, ground truth, accuracy circle або waypoint. Розрахунок
припускає один stationary emitter, ніколи не використовує червоні untrusted
coordinates і нічого не надсилає у FC.

---

## H743 DroneCAN v0.5.28 — 2026-08-17

Замінює v0.5.27. Додає оцінку витрати палива двигуна.

### Нове: оцінка витрати палива за обертами двигуна

Фільтр тепер може оцінювати витрату палива за обертами двигуна, які польотний
контролер і так йому передає, і повідомляти її ArduPilot як пристрій EFI.
Встановіть на FC `EFI_TYPE` у варіант DroneCAN — і показник палива з'явиться в
наземній станції та в логу, без додаткової проводки й без додаткового датчика.

Тут немає ні витратоміра, ні датчика в баку: це модель того, що мусить
поглинати гвинт, скалібрована одним числом, яке ви задаєте після одного
зваженого польоту. Вісім параметрів описують ваш двигун і гвинт; додано пресети
для DLE-120 з гвинтом 27x12 та RCGF-70 з 23x10.

**На літаку без покажчика палива це ЄДИНА індикація палива, яку ви маєте.**
Вона побудована завищувати, а не занижувати, бо саме заниження зупиняє двигун.
Без калібрування очікуйте завищення приблизно в 1.2–2 рази; після одного
зваженого спалювання — 10–20%. Доки не скалібруєте, літайте за годинником і
вважайте число орієнтовним.

Два моменти перед першим польотом:

- **Запис `FUEL_CAPG` обнуляє накопичений підсумок.** Це єдине, що його
  обнуляє. Робіть це після кожної заправки, навіть якщо число не змінилося.
- **Один раз звірте `RPM1_SCALING` з ручним тахометром.** У фільтра одне
  джерело обертів, тож ніщо не може йому заперечити. Здвоєний CDI дає два
  імпульси на оберт; налаштуєте один — і оцінка буде значно заниженою. Якщо
  колись побачите `Fuel held up by throttle - check RPM_SCALING` — зупиніться
  й перевірте.

Накопичений підсумок тепер переживає перезавантаження в польоті — watchdog,
збій або просідання живлення — замість того щоб почати з нуля й показати вам
повний бак. Якщо відновити його неможливо, бак показує UNKNOWN і повідомляє про
це кожні 60 секунд, а не мовчки показує «повний».

Процедура — у розділі «Калібрування оцінки витрати палива» посібника з
налаштування.

### Виправлено: два варіанти прошивки не збиралися

Збірки H743 без датчиків і standalone взагалі не компілювалися. Обидві
виправлено, і система збірки тепер компілює кожен варіант, щоб це не
повторилося. Прошивку DroneCAN це виправлення не змінює.

---

## H743 DroneCAN v0.5.27 — 2026-08-15

### Нове: логування для визначення напрямку на джерело завад

Фільтр тепер записує все потрібне, щоб визначити, **з якого напрямку** працює
глушилка або спуфер. Він не обчислює пеленг у повітрі й не використовує ці дані
для виявлення спуфінгу — лише пише вимірювання у ваш політний лог, свідомо
відокремлено від логіки захисту.

Після польоту виконайте `python tools/df_analyze.py flight.bin` на лозі FC, щоб
отримати пеленг із точністю приблизно ±20–45°.

Щоб отримати придатну відповідь, треба **пролетіти повне коло** крізь зону
завад. Метод спостерігає, як прийнята потужність завади змінюється з вашим
курсом, тож прямий проліт не дає йому матеріалу — і інструмент правильно
відмовиться відповідати.

Два чесні обмеження: один пеленг дає напрямок, а не позицію — для тріангуляції
потрібні два з рознесених точок. І доки полярність не звірено з відомим
передавачем, вважайте відповідь лінією (пеленг або пеленг+180°), а не
напрямком.

---

## H743 DroneCAN v0.5.26 — 2026-08-14

**Відновлення після глушіння стало значно швидшим.** Якщо ви бачили, як фільтр
залишається в DR1 десятки хвилин після того, як глушіння припинилося — без
жодного спуфінгу — це виправлення саме для вас.

### У чому була проблема

Фільтр скидав ваш GNSS-приймач саме тоді, коли той намагався відновити фікс.

U-blox тримає альманах супутників годинами. Заглушіть його — і щойно глушіння
припиняється, він зазвичай повертає фікс за **секунди**. Але фільтр надсилав
повне скидання приймача приблизно на 50-й секунді кожної події глушіння,
стираючи саме ті дані, які роблять повторний захват швидким, — і повторював це
скидання кожні дві хвилини, поки фікс був відсутній. За слабкого сигналу після
глушіння холодний захват може тривати довше за дві хвилини, тож кожне скидання
знищувало здобуток попереднього.

### Що змінилося

- **Приймач залишають у спокої, поки він працює.** Приймач, який усе ще
  звітує фільтру, займається захватом, а не завис, і більше не скидається.
  Справді непритомний приймач скидається як і раніше. Раз на подію ви
  побачите `GNSS acquiring - reset held`.
- **Звичайний прогрів за слабкого сигналу більше не вважається спуфінгом.**
  У приймача, що відновлюється, усі супутники ненадовго мають однаково низький
  рівень, і перевірка відновлення зараховувала це як атаку.

---

## H743 DroneCAN v0.5.25 — 2026-08-13

Замінює v0.5.24.

Підтримка Septentrio Mosaic-X5 доведена до промислового рівня, а той самий
перегляд виявив дві проблеми, які стосуються **і u-blox теж** — одна з них
потребує одноразової перевірки на вашій платі.

### Перевірте свою плату (однаково для u-blox і Mosaic)

- **Якщо ви коли-небудь завантажували пресет приймача** (`ublox_autoconfig`,
  `manual_ublox_460800` або `mosaic_x5_nmea`), він мовчки вимикав SNR-детектор
  спуфінгу (`SNR_EN=0`) — одну з найсильніших перевірок проти спуфінгу з
  одного передавача, тоді як документація описувала її як активну. Пресети
  виправлено; **зчитайте `SNR_EN` з плати й встановіть `1`**, якщо там 0.
  Значення зберігається на платі, тож саме лише прошивання його не полагодить.
- Пресет налаштувань `field_safe` більше не змінює тип вашого приймача: раніше
  він записував `GNSS_TYPE,0`, що перетворювало плату Mosaic назад на профіль
  u-blox **при наступному вмиканні живлення в полі**.

### Виправлено — Mosaic X5 на SBF

- **Відновлення з DR1 тепер працює.** Докази для відновлення вимагали часового
  вирівнювання, яке дають лише приймачі u-blox, тож будь-яке спрацювання DR1 на
  Mosaic — навіть від легкого удару по антені — лишалося зафіксованим до
  вимкнення живлення, а наземне звільнення ніколи не могло завершитися. Усі
  шляхи відновлення (повернення в польоті, наземне звільнення і сам тригер
  спуфінгу за часом GPS) тепер коректно працюють на SBF.
- Mosaic, який видає і NMEA, і SBF, більше не ризикує мовчки залишитися в
  режимі лише NMEA після старту; SBF перебирає керування за секунди, і
  багатші дані (коваріація, перевірки годинника, рівні сигналу по кожному
  супутнику) справді використовуються.
- Більше немає зникнення GPS за секунди після відновлення: внутрішнє
  пересканування приймача, що має сенс лише для інших типів приймачів, більше
  не запускається на Mosaic одразу після зняття DR1.
- Звичайні підлаштування годинника Mosaic більше не роздувають оцінку
  достовірності спуфінгу; погіршений вивід приймача (кількість супутників із
  прапорцем помилки, відсутні дані геоїда) більше не сприймається на віру.

### Додано

- Фільтр тепер **попереджає, якщо заданий тип приймача суперечить тому, що
  фактично підключено** (`GNSS_TYPE mismatch?`), замість мовчазної відмови, і
  повідомляє, якщо Mosaic працює лише в NMEA зі зниженим покриттям виявлення.
- Зміна `GNSS_TYPE` тепер справді застосовується після перезавантаження — саме
  так, як каже повідомлення підтвердження, — і зчитує збережене значення назад.

### Документація

Таблиці покриття виявлення по приймачах завищували можливості чистого NMEA
(UM980 / Mosaic у режимі NMEA): три сигнали, які потребують швидкості або
даних по кожному супутнику, тепер чесно позначені як недоступні там. Якщо у вас
Mosaic — використовуйте режим SBF: режим NMEA коштує реального покриття.

**Примітка щодо стенда:** виправлення для Mosaic перевірені оглядом коду та
статичними тестами; якщо ви літаєте з Mosaic, спершу виконайте стандартну
стендову перевірку — зняти антену, дочекатися DR1, під'єднати антену,
підтвердити відновлення.

---

## H743 DroneCAN v0.5.24 — 2026-08-13

Замінює версії з v0.5.16 по v0.5.23.

Тема цієї групи випусків — відновлення: DR1 тепер знімається **у полі, без
вимкнення живлення**, на землі та після довгих ділянок без GNSS — і при цьому
кожне зняття все одно вимагає доказів, а не спливлого часу.

### Додано

- **Наземне звільнення: припаркований і роззброєний апарат виходить із DR1
  самостійно.** Коли польотний контролер незалежно засвідчує, що апарат
  припаркований і роззброєний, а фікс, що повернувся, лишається
  самоузгодженим протягом витримки (90 с для тригерів втрати сигналу, 240 с
  для тригерів цілісності, зі зростанням на кожне використання), DR1
  знімається на місці. Кількість звільнень обмежена на цикл живлення, кожне
  супроводжується банером CRITICAL, а випробувальний нагляд миттєво повертає
  DR1, якщо фікс поповз, а апарат не рухався. `SOUTH` ніколи не знімається
  автоматично: фікс у південній півкулі для цього апарата фізично неможливий і
  завжди коштує свідомої людської дії.
- **Повернення в довгому польоті тепер покриває всю місію.** Стеля гейта
  повернення завершувала відновлення після ~1 год 51 хв числення шляху; тепер
  вона покриває повну 8-годинну тривалість, тож ділянка в 70 або 350 км без
  GNSS може завершитися поверненням, коли атака припиниться. Перевірка дрейфу
  годинника теж більше не провалюється жорстко на довгій перерві: її допуск
  зростає з часом, який простояла базова лінія.
- **Чесне переміщення більше не залишає апарат заблокованим.** Перенесення
  припаркованого апарата зі стенда на точку зльоту після наземного звільнення
  повертає DR1 (за задумом — фікс зрушив під нерухомим апаратом), і тепер
  апарат звільняється повторно з нової позиції, замість блокуватися до
  вимкнення живлення.

### Виправлено

- **Плати, підготовлені до v0.5.21, автоматично виправляють збережений
  параметр відновлення.** Пільговий період EKF зберігається на платі, і старі
  плати тримали свої 7 с — достатньо мало, щоб повернути DR1 ще до того, як
  оцінювач польотного контролера встигне збігтися, роблячи відновлення
  фактично неможливим. Прошивка тепер піднімає збережене значення щонайменше
  до 20 с (за замовчуванням 60 с), а повторна підготовка записує значення за
  замовчуванням прямо. Якщо вам колись здавалося, що апарат «не відновлюється,
  скільки не чекай», — найімовірніше, причина була саме в цьому.
- Підготовка більше не встановлює застарілу стелю повернення на нових платах.
- Рядок статусу більше не публікує від'ємний DOP, а звичайний трафік шини
  більше не рахується як помилки CAN.

### Після прошивання

Переналаштовувати нічого: параметри, які ви свідомо змінювали, зберігаються, і
піднімаються лише небезпечні збережені значення. Перевірте на стенді перед
польотом — зніміть антену GNSS, дочекайтеся DR1, під'єднайте її знову й
переконайтеся, що рядок статусу самостійно повертається до DR0.

---

## H743 DroneCAN v0.5.16 — 2026-08-08

Замінює v0.5.13.

### Додано

- **Магнітометр більше не компілюється у складання за замовчуванням.** Апарати,
  які беруть компас від польотного контролера, більше не бачать вузол,
  позначений як несправний через датчик, якого ніколи не було. Плати, де
  магнітометр є, збираються як `weact_mini_h743vitx_dronecan_mag`; плати без
  жодного з датчиків — як `weact_mini_h743vitx_dronecan_nosensors`.
- **Стан виявлення спуфінгу в самому приймачі тепер повідомляється.** У рядку
  статусу з'явився `enXY`, і фільтр попереджає, якщо в приймача вимкнено
  виявлення спуфінгу — раніше це виглядало точно як «спуфінгу не помічено»,
  тоді як три найсильніші перевірки мовчки нічого не робили.

### Виправлено

- Нестабільний датчик швидкості більше не може безмежно роздувати витримку
  відновлення з DR1. Спростовані спроби відновлення й далі коштують часу, але
  штраф тепер спадає, щойно докази перестають суперечити.

### Як змінювати параметри фільтра

Параметри фільтра **не** знаходяться у Full Parameter List Mission Planner. Той
список редагує польотний контролер. Фільтр — це окремий вузол, **system ID 42**,
і записи, введені у список FC, мовчки нікуди не потрапляють.

Використовуйте екран параметрів DroneCAN (SETUP -> Optional Hardware ->
DroneCAN/UAVCAN, `MAVLink - CAN1`, вузол 42 -> Parameters) або новий скрипт:

```
python tools/mission_planner/filter_params.py --port COM25 --list
python tools/mission_planner/filter_params.py --port COM25 --set LOG_MS=2000
```

Записи відхиляються, поки польотний контролер армований, і фільтр про це
повідомляє. `ARM=1` у власному рядку статусу фільтра **не** означає, що FC
армований — це стан прогріву захисту від спуфінгу, і він нормальний.

---

## H743 DroneCAN v0.5.13 — 2026-08-08

Замінює версії з v0.5.7 по v0.5.12 — одноденні ітерації. Прошивайте цю.

### Виправлено — DR1 міг спрацювати, коли все було гаразд

- **Нерухомий або повільний апарат більше не суперечить сам собі й не блокує
  відновлення.** Рядок правдоподібності шляхової швидкості вимагав щонайменше
  8 м/с для відновлення, тож апарат, який увійшов у DR1 нерухомо, записував
  0 м/с як свою опору й далі відмовлявся зніматися назавжди. Саме це давало
  `ev3/3F1p` на деяких апаратах після від'єднання й повторного під'єднання
  антени GPS. У польоті ця ж перевірка спрацьовувала на розбігу й за будь-якого
  зустрічного вітру, достатнього, щоб утримати шляхову швидкість нижче 8 м/с.
  Тепер вона звіряється з власною оцінкою швидкості польотного контролера, а не
  із запам'ятованим GNSS.
- **Апарат, що літає без компаса, більше не входить у DR1 на стоянці.**
  Нерухомий апарат без магнітометра не може завершити вирівнювання курсу EKF,
  тож польотний контролер повідомляв стан, який фільтр читав як спуфінг. Далі
  це підтримувало саме себе, бо саме утримання GNSS і не дає оцінювачу
  вирівнятися. EKF, який ще жодного разу не вирівнювався, тепер вважається
  стартовим станом.
- **Коротка зупинка тунелю CAN більше не коштує хвилин GPS.** Придушення при
  застарілому лінку з польотним контролером лишається миттєвим; фіксація DR1
  тепер чекає 10 с.
- **Один індикатор більше не може самотужки набрати кворум достовірності
  спуфінгу.**

### Змінено

- Стартове вето спуфінгу за поведінкою не змінилося після того, як проміжний
  випуск його ненадовго послабив. Якщо ви прошили v0.5.11 — замініть її.

### Відомі обмеження, сказано прямо

- **DR1 не зніметься на нерухомому стенді, і жодне звільнення цього не
  змінить.** Зняття вимагає незалежного не-GNSS свідка, а стіл його не дає.
  Очікуйте `ev3/3F0p` і перезавантажуйте живлення, а не чекайте.
- **Якщо не встановлено ні датчика швидкості, ні компаса**, відновлення
  потребує сталого набору висоти або сталого розвороту — ідеально підходить
  loiter автопілота. Політ по прямій DR1 не зніме.

---

## Desktop app 2026.08.02.2 — 2026-08-02

### Виправлено

- Кожна SWD command і reconnect прив'язані до serial number єдиного
  enumerated ST-Link. Відсутній, замінений або додатковий probe зупиняє flow
  до наступного access до плати.
- USB DFU повторно enumerate-иться безпосередньо перед кожним erase, firmware
  write та option-byte transition. Зміна device count або exposed serial
  зупиняє операцію замість ризику записати не ту плату.
- Recover Board читає кожний byte physical flash до повідомлення blank:
  256 KiB для F401 і 2 MiB для H743, включно зі staging, saved tuning,
  reserved і metadata regions.
- Firmware та звичайні API responses streamed, size-bounded, декодуються в
  межах limit і закриваються на кожному success/error path.
- App тепер має окремо reviewed firmware-signing public key і відхиляє server
  bundle з іншим ключем. Окремий target-bound Ed25519 signature охоплює кожен
  exact byte personalized bootloader, тому server response не може підмінити
  executable bootloader code.

---

## H743 DroneCAN v0.5.6 — 2026-08-02

### Виправлено

- Коли filtered GNSS output блокується, усі вже queued DroneCAN frames
  відкликаються до можливого відновлення publishing. Firmware скидає FDCAN
  через RCC, очищає libcanard і повторює повну timing/filter/controller-start
  послідовність, поки output залишається fail-closed.

Цей build лишається release candidate до підписання hardware/HIL checklist
для його exact SHA-256.

---

## Desktop app 2026.08.02.1 — 2026-08-02

### Виправлено

- Activation і protected update перевіряють увесь server bundle до будь-якого
  erase: response target/UID, metadata format і plaintext fields, packed
  version, vector table, BLAKE2b app hash, Ed25519 signature, patched
  bootloader keys, UID binding та report token мають збігатися.
- Exact validated bytes зберігаються між RDP reconnect; app ніколи не отримує
  replacement firmware після erase плати.
- Protected USB DFU зупиняється до write, якщо physical UID неможливо прочитати
  й перевірити після зняття RDP. Activation UID більше не підставляється замість
  відсутнього hardware measurement.
- Firmware version selection, tuning-loss/recommission warnings і physical UID
  mismatch failures явно показані в English та Ukrainian flows.
- Кожний destructive flow вимагає точну physical-board фразу
  `F401CC BLACKPILL` або `WEACT H743VI` до hardware access і після кожного
  reconnect/transport change. `--yes` її не обходить; F401 128 KiB та H743
  1 MiB відхиляються до option-byte або erase access.

---

## H743 DroneCAN v0.5.5 / F401 v1.6.26 - 2026-08-02

### Виправлено

- Real GNSS більше не відновлюється з тимчасово disarmed post-DR1
  position/time integrity guards. Посилено invalid altitude, UTC, SNR,
  SEC-SIG, malformed-frame та receiver-reset handling.
- H743 CAN faults відновлюються через bounded retries, а output залишається
  fail-closed. Stuck I2C, tune-journal stalls і runtime watchdog hangs мають
  bounded recovery або reset.
- F401 і H743 production apps перевіряють UID конкретної physical board;
  unprovisioned templates неможливо upload напряму.

### Provisioning і releases

- Desktop/CLI повністю validates downloaded bundle до destructive operation і
  перевіряє physical UID до success.
- New firmware inactive, доки owner не завершить qualification і promotion.
  Revoked, inactive, malformed або storage-tampered binaries не пропонуються
  клієнтам.
- Ці builds лишаються release candidates до підписання hardware/HIL checklist
  для їх exact SHA-256.

## Desktop app 2026.07.23.2 - 2026-07-23

### Додано

- **Recover Board** для H743 тепер доводить справу до кінця, навіть коли SWD
  взагалі не може стерти чип: після спроб із замороженим watchdog та в
  BOOT0-режимі він повторює erase на низькій частоті SWD, а потім проводить
  вас через **USB-C ROM DFU erase** — власний bootloader чипа стирає flash
  внутрішньо на живленні від USB, без SWD і без живлення від ST-Link. Це
  також відновлює плати, чий flash залишився напівстертим (читається як
  нулі) після перерваного оновлення.
- Фінальне повідомлення про помилку тепер пояснює, що чип, який не може
  стерти навіть власний ROM bootloader на стабільному USB-живленні,
  найімовірніше має пошкоджений flash і плату слід замінити.

---

## H743 DroneCAN v0.4.3 - 2026-07-23

### Виправлено

- Прошивка тепер заморожує свій 15-секундний апаратний watchdog щоразу, коли
  debugger або provisioning-додаток зупиняє чип через SWD (DBGMCU freeze bit
  встановлюється під час boot), тож тривалі flash-операції, як-от повний
  erase чипа, більше не можуть бути скинуті посередині власним watchdog
  прошивки. У польоті це ні на що не впливає — заморозка діє лише поки
  debugger тримає core зупиненим.
- Автоматична boot-time міграція параметрів більше не запускає фонові
  flash-записи, поки активна debug-сесія; вона завершується під час
  наступного звичайного boot. Зміни параметрів, які ви робите самі,
  зберігаються як завжди.

---

## Desktop app 2026.07.23.1 - 2026-07-23

### Виправлено

- Збої H743 mass erase (`Mass erase operation failed. Please verify flash
  protection` при RDP уже `0xAA`) спричиняв 15-секундний апаратний watchdog
  встановленої прошивки, який скидав чип посеред erase, а не flash
  protection. Кожен H743 ST-Link erase тепер заморожує цей watchdog на час
  halted debug-сесії (запис `DBGMCU` `DBG_IWDG1` у тому самому виклику
  CubeProgrammer) перед erase.
- Прибрано H743 fallback `-ob unlockchip`: CubeProgrammer підтримує
  `unlockchip` лише на STM32WL, тому на H743 він завжди зазнавав невдачі й
  заповнював log повідомленням `Error: Only STM32WL devices are supported`.
- Шлях "already blank" після невдалого erase тепер завантажує і перевіряє
  кожен записуваний region (bootloader, application, metadata) плюс сектори
  H743 parameter journal замість перевірки шести sentinel words, тож частково
  стертий чип більше не може проскочити до кроку запису.

### Додано

- Керований **BOOT0 power-cycle** recovery для H743: якщо erase все одно не
  вдається, app проводить вас через утримання BOOT0 під час повторного
  підключення живлення, тож чип завантажує свій ROM bootloader замість
  прошивки, і erase виконується взагалі без watchdog. Фінальне повідомлення
  про помилку тепер називає причиною watchdog, а не flash protection.

---

## H743 DroneCAN v0.4.2 - 2026-07-21

### Змінено

- Налаштовано стандартні параметри H743 fixed-wing для літака з крейсерською
  швидкістю близько 120 км/год: `EKF_TRIPMS=500`, `SP_JMP_MPS=200`,
  `SP_ABS_M=400` та `RJ_LOIT_V=0`. Власні значення зберігаються під час
  оновлення; стандартні значення F401 не змінено. Математичні guard-тести
  охоплюють design envelope до 65 м/с (234 км/год), але не замінюють перевірку
  за польотними логами.

### Виправлено

- Перевірка стрибків тепер використовує епохи GNSS, а не час надходження UART,
  тому дублікати та backlog не створюють хибних тривог швидкості. Generic
  втрата EKF використовує налаштований debounce, тоді як явний
  `GPS_GLITCHING` спрацьовує негайно після inhibition. `UNINITIALIZED`
  допускається лише до першого healthy EKF report у FC session; після цього
  startup exemption не відкривається повторно.
- Явний no-fix, зміна приймача та завершення DroneCAN Fix2 в межах однієї епохи
  тепер працюють fail-closed без змішування полів або обходу jump guard.
  Некоректні координати від активного джерела скасовують fix, а зміна джерела
  очищує попередні дані quality/SNR;
  Fix2 UTC timestamp зберігає millisecond precision приймача.
- Boot, DR lock, rejoin і EKF grace таймери коректно працюють після 24,9 діб
  uptime та через 32-bit rollover таймера.

---

## H743 DroneCAN v0.4.1 - 2026-07-21

### Додано

- Додано двосекторний H743 parameter journal із commit-last записом і stable
  name keys, які зберігають unknown values у межах supported schemas.
- F401 runtime sector erase замінено transactional append-only journal; коли
  journal full, persistence відхиляється, а останні committed settings
  зберігаються.

### Змінено

- Production defaults тепер fail closed із live FC heartbeat/EKF evidence,
  EKF-confirmed rejoin, двохвилинним DR1 lock, enabled SNR guard, без forced
  DR1 timeout і з location-redacted status text.
- Parameter writes і resets вимагають fresh, explicitly disarmed FC evidence
  від configured або leased DroneCAN peer.
- Secure H743 app/staging windows мають по 640 KiB. Production bootloader
  перевіряє RDP1 і зберігає anti-rollback compatibility floor v0.4.0; server
  застосовує той самий floor до customer-visible selection paths.

### Виправлено

- Усі private DR geometry, altitude, confidence, EKF і fence gates працюють у
  pass-through mode та протягом optional GNSS blend.
- Malformed, stale, non-finite, out-of-range або wrong-source GNSS, MAVLink і
  DroneCAN safety evidence тепер fail closed. Виправлено heading reversal на
  1 Hz, antimeridian residuals і GetSet DSDL decoding.
- Lease expiry або FC reboot очищує обидва напрями обох MAVLink tunnels, скидає
  всі FC-derived states і повторно запитує повний telemetry set.
- Посилено MS4525/HMC5983 reads, I2C recovery, nonblocking display/USB work і
  non-overlapping `NodeStatus` vendor layout.

---

## H743 DroneCAN v0.4.0 - 2026-07-21

### Додано

- Замість row-only status screen додано професійний темний dashboard для
  вбудованого кольорового TFT ST7735 80 x 160. Він використовує кастомні
  штриховані hero glyphs `OK` / `!!` / `XX`, proportional body typography,
  rounded metric tiles, gradient health rails і segmented activity rails.
- Додано узгоджену animated startup scene, page dots та footer underline, а
  також eased five-frame transitions між Overview, Sensors, Links і System.
- Додано dependency-free pixel-exact browser preview, який генерується тим самим
  portable C++ RGB565 renderer, що й firmware, а також native renderer safety і
  state-transition tests.

### Змінено

- Постійний footer показує GPS publication, DR0/DR1 і DroneCAN node ID. Armed
  state, filter block або FC alert фіксують UI на відповідній safety view, а
  sensor/link warning — на сторінці, що пояснює проблему. Dashboard показує
  `FILTER CHECK / GUARD` до завершення реального startup spoof-guard timer;
  filter/FC faults використовують dedicated alert takeover; page
  sliding вимагає fresh, явно disarmed FC state. `PUB+`, `PUB?` і `PUB-`
  відрізняють recent Fix2, прийнятий у локальну transmit queue,
  allowed-but-idle та blocked/unavailable output; `PUB+` не є FC acknowledgement;
  одночасні filter/FC alerts залишаються видимими.
- Normal USB indication перейменовано на `USB CONFIG`; ROM DFU і надалі вимагає
  `BOOT0` разом із reset або power-up.
- Display transfers виконуються частинами та поступаються GNSS/CAN processing.
  Дані екрана є допоміжною діагностикою і не замінюють FC pre-arm checks,
  sensor calibration чи аналіз flight log.
- Redesign змінює лише presentation. Spoofing gates, DR0/DR1 behavior,
  DroneCAN GPS/sensor publication та обидва MAVLink2 virtual ports не змінені.

---

## H743 DroneCAN v0.3.0 - 2026-07-21

### Додано

- Додано shared 400 kHz I2C2 sensor bus на H743 `PB10` SCL / `PB11` SDA для
  default `4525DO-DS3AI001DP` differential-pressure sensor і genuine HMC5983
  magnetometer.
- Додано native DroneCAN `RawAirData` до 20 Hz і
  `MagneticFieldStrength2` до 25 Hz через наявний CAN transceiver та node ID
  `42`.
- Задокументовано окремий keyed 4-pin 3.3 V sensor connector, бо HD-15 уже
  повністю зайнятий, а також full-part-code, clone, placement, calibration,
  pull-up і bench-test requirements.

### Змінено

- Airspeed і compass publications не залежать від GNSS DR0/DR1 gate та
  залишаються активними разом із NodeStatus і двома MAVLink2 tunnel ports.
- Optional I2C operations виконуються почергово після обробки pending GNSS із
  2 ms core timeout; H743 GNSS RX ring збільшено до 1024 bytes, щоб відсутній
  або stuck sensor не витісняв spoof-filter input processing.

---

## H743 DroneCAN v0.2.0 - 2026-07-21

### Додано

- Додано двонапрямний MAVLink2 OpenIPC camera на H743 `PA10` RX / `PA9` TX
  через стандартний `uavcan.tunnel.Targetted`, port index `0`.
- Додано окремий DroneCAN virtual serial port index `1` для власного MAVLink2
  фільтра та FC telemetry у зворотному напрямку. Збережено heartbeat, status,
  tuning, EKF, barometer, arm-state та rejoin logic.

### Змінено

- Збільшено UART/FDCAN buffers, додано bounded queues і резерв libcanard pool;
  CAN обслуговується між GNSS/display operations, тому camera traffic не
  витісняє native GPS `Fix2/Auxiliary`.
- Обидва MAVLink ports залишаються активними у DR1, а GPS publishing і надалі
  контролюється всіма spoofing-filter gates.

---

## H743 DroneCAN v0.1.11 - 2026-06-24

### Fixed

- Розділено freshness tracking для pseudorange residual і C/N0 temporal
  correlation у `DR_CONF`. Mosaic X5 SBF `MeasEpoch` тепер дає тільки C/N0
  temporal signal, а u-blox-only pseudorange residual score залишається
  вимкненим у Mosaic mode замість використання stale/default value.

---

## H743 DroneCAN v0.1.10 - 2026-06-24

### Added

- Published TDOP from u-blox `NAV-DOP` and Mosaic X5 SBF `DOP` into DroneCAN
  `uavcan.equipment.gnss.Auxiliary` when fresh.
- Added compact Mosaic-only `SBF good/bad` line to the H743 onboard screen.

---

## H743 DroneCAN v0.1.9 - 2026-06-24

### Fixed

- Corrected Mosaic X5 SBF `DOP` mapping: Septentrio block `4001` reports
  PDOP/HDOP/VDOP/TDOP but not GDOP, so H743 DroneCAN no longer reports PDOP as
  GDOP.
- Aligned Mosaic PVT mode mapping with the Septentrio reference; reserved mode
  `9` is no longer reported as PPP.

---

## H743 DroneCAN v0.1.8 - 2026-06-23

### Added

- Added native Septentrio Mosaic X5 SBF parsing to H743 DroneCAN for
  `GNSS_TYPE=2`: `PVTGeodetic`, `DOP`, `ReceiverTime`, `MeasEpoch`,
  `PosCovGeodetic`, and `VelCovGeodetic`.
- Passive GNSS baud scan now counts valid SBF frames as well as NMEA sentences.

---

## Docs/Tools - 2026-06-23

### Changed

- Reserved a separate H743 DroneCAN flash staging region for future
  Mission Planner/AirDroper app DroneCAN firmware updates. Current H743 updates
  still use ST-Link/SWD or USB-C ROM DFU.
- Updated the H743 DroneCAN guide to show the full secure flash layout and to
  clarify that standard DroneCAN firmware update is planned but not active yet.
- Documented and test-guarded the GPS data integrity contract: UART builds
  forward unchanged receiver bytes in DR0, while H743 DroneCAN publishes parsed
  live receiver fix values and never sends synthetic/blended GPS coordinates.

---

## H743 DroneCAN v0.1.7 - 2026-06-23

### Fixed

- Refined H743 DroneCAN `NodeStatus` health again: latched no-fix and
  low-satellite DR1 reasons also keep node health `OK`. Warning health is now
  used only for spoof/fault DR1 reasons, so ArduPilot should stop showing
  `PreArm: DroneCAN: Node 42 unhealthy!`, коли receiver просто ще не має GPS
  fix.

---

## H743 DroneCAN v0.1.6 - 2026-06-23

### Fixed

- Fixed H743 DroneCAN `NodeStatus` health for boot guard and GNSS
  reconfiguration output suppression. This release was superseded by
  `v0.1.7`, which also keeps no-fix and low-satellite DR1 cases from marking
  the node unhealthy.

---

## H743 DroneCAN v0.1.5 - 2026-06-23

### Додано

- Додано direct USB-C MAVLink management port для H743 DroneCAN. У normal app
  mode, без `BOOT0`, Mission Planner може підключитись до H743 USB COM port на
  `115200` і редагувати ті самі spoofing/tuning parameters через
  **CONFIG -> Full Parameter Tree/List**.

### Змінено

- H743 DroneCAN і далі не використовує flight-controller serial port.
  DroneCAN node Params залишаються основним in-aircraft шляхом tuning; USB-C
  MAVLink призначений для прямого bench/service доступу до H743.

---

## H743 DroneCAN v0.1.4 - 2026-06-23

### Додано

- Додано editable H743 spoofing/tuning parameters через Mission Planner
  `DroneCAN/UAVCAN -> node 42 -> Params`. `GPS_TYPE`/`GPS1_TYPE` залишаються
  read-only compatibility rows зі значенням `9`; guard/tune params ідуть після
  них і зберігаються через DroneCAN `Commit Params`.
- Додано DroneCAN `uavcan.protocol.param.ExecuteOpcode` save handling, щоб
  кнопка Mission Planner `Commit Params` записувала змінені H743 parameters у
  flash.
- Додано `UBX_RESET` як DroneCAN one-shot command для u-blox hot start, cold
  start або config reset.

### Змінено

- H743 DroneCAN тепер завантажує і зберігає той самий tuning blob, що й UART
  firmware, але MAVLink-dependent settings залишаються locked off:
  `RJ_REQEKF=0`, `FCGPS_UART=0`, `FCGPS_FWD=0`.

---

## H743 DroneCAN v0.1.3 - 2026-06-23

### Змінено

- WeAct H743 LCD тепер одразу показує boot/progress page перед довшим GNSS
  startup path. Під час receiver autobaud/config екран має показувати
  `GNSS INIT`, а не залишатися чорним до старту main loop.

---

## H743 DroneCAN v0.1.2 - 2026-06-23

### Додано

- Додано мінімальну read-only DroneCAN відповідь
  `uavcan.protocol.param.GetSet` для ArduPilot запитів `GPS_TYPE`/`GPS1_TYPE`.
  Це дозволяє H743 DroneCAN GPS працювати навіть коли на FC увімкнено
  `GPS_AUTO_CONFIG=2`.
- Задокументовано рекомендований ArduPilot setup `GPS_AUTO_CONFIG=1` і
  optional node lock `GPS1_CAN_OVRIDE=42`, якщо на CAN bus є кілька DroneCAN
  GPS nodes.

---

## H743 DroneCAN v0.1.1 - 2026-06-23

### Виправлено

- Виправлено полярність backlight onboard LCD на WeAct H743. Якщо H743
  DroneCAN на `v0.1.0` завантажується, синій LED блимає раз на кілька секунд,
  але екран чорний, оновіть плату до `v0.1.1` через AirDroper GNSS Filter app.
  DroneCAN GPS продовжує працювати навіть без екрана.

---

## Документація/інструменти - 2026-06-06

### Змінено

- Оновлено інсталятор метаданих параметрів Mission Planner: тепер він підтримує
  як сучасні файли `*.apm.pdef.xml`, так і старі кешовані
  `ParameterMetaData.xml`.
- До ZIP-пакета Mission Planner додано `README_UK.md`, щоб українська
  інструкція з налаштування була доступна безпосередньо в пакеті.
- Посилання на ZIP Mission Planner Params повторюється в розділах setup,
  tuning, receiver config, FAQ і troubleshooting, щоб пакет метаданих було
  легше знайти під час відповідного workflow.

---

## Документація/інструменти - 2026-06-05

### Додано

- Опубліковано ZIP метаданих параметрів Mission Planner:
  [gps.airdroper.org/download/mission-planner-mod](https://gps.airdroper.org/download/mission-planner-mod).
  Пакет додає описи, діапазони, одиниці, підписи варіантів і готові `.param`
  presets для параметрів STM32-фільтра.

---

## v1.6.24 - 2026-06-03

Офіційний стабільний реліз, переведений у stable 2026-06-06 після польової
перевірки.

### Змінено

- Періодичні статус-логи тепер надсилають лише один рядок `data=...` і один
  рядок `ARM=... DR=...` за кожний інтервал `LOG_MS`, замість дублювання кожного
  рядка під двома MAVLink-ідентифікаторами.
- Звичайний періодичний діагностичний рядок `fcgps tx=... rx=...` прибрано, щоб
  вкладка Mission Planner Messages залишалася читабельною під час нормальної роботи.

---

## v1.6.23 - 2026-06-02

Офіційний стабільний реліз, переведений у stable 2026-06-03 після польової
перевірки відновлення SNR на u-blox F9P та підтримки Mosaic X5 у пасивному NMEA.

### Додано

- Додано `GNSS_TYPE=2` для приймачів Septentrio Mosaic X5, налаштованих на NMEA.
- Додано інструкцію налаштування Mosaic X5 у документацію конфігурації приймача.

### Змінено

- Режим Mosaic X5 використовує пасивне визначення швидкості NMEA і не надсилає до приймача команди скидання або автоконфігурації. Якщо стан без фікса триває, фільтр лише повторює пасивне сканування швидкості NMEA.

---

## v1.6.22 - 2026-06-02

Тестова прошивка для очищення u-blox autoconfig. На момент релізу v1.6.15
залишалася стабільною версією за замовчуванням на сервері; обирайте
`v1.6.22 (dev)` лише коли підтримка просить перевірити цю збірку.

### Прошивка

- **Autoconfig стартує зі стандартних налаштувань приймача**: у прямому режимі u-blox з
  `UBX_BAUD=0` boot тепер переводить приймач на цільовий baud, очищає/завантажує
  стандартні налаштування приймача, повторно сканує baud, потім застосовує і зберігає
  UBX-профіль фільтра.
- **Ручний baud/gateway режим вимкнений**: якщо `UBX_BAUD>0`, фільтр пропускає
  стартовий шлях очищення/autoconfig і використовує налаштований baud напряму. Це
  зберігає навмисні профілі оператора або виробника.
- **Очікувана UX-зміна**: прямі F9/F10/M9/M10 приймачі мають відновлюватися
  після застарілих збережених налаштувань u-center або vendor-профілів без
  ручного стендового кроку `UBX_RESET=3` перед цим.

---

## v1.6.21 - 2026-06-02

Корекція тестової прошивки для відновлення SNR на u-blox. На момент релізу
v1.6.15 залишалася типовою стабільною версією на сервері. Замінена
`v1.6.22 (dev)`.

### Прошивка

- **Виправлений fast gate для NAV-SAT recovery**: v1.6.20 скоротив таймер
  застарілого SNR, але стара 30-секундна перевірка свіжості NAV-SAT усе ще
  могла блокувати швидкий шлях. v1.6.21 використовує те саме 8-секундне вікно
  для обох перевірок, коли здоровий u-blox fix уже є.
- **Без змін для startup/no-fix поведінки**: no-fix, нуль C/N0 і початкове
  отримання fix усе ще використовують повільніший 30-секундний шлях.

---

## v1.6.20 - 2026-06-02

Тестова прошивка лише для швидшого відновлення SNR на u-blox. На момент релізу
v1.6.15 залишалася типовою стабільною версією на сервері. Замінена
`v1.6.21 (dev)`.

### Прошивка

- **Швидше відновлення періодичного зникнення NAV-SAT**: якщо u-blox приймач
  уже має здоровий fix, а потім NAV-SAT зникає, прошивка тепер заново вмикає
  NAV-SAT приблизно через 8 секунд замість повного 30-секундного вікна
  застарілого SNR.
- **Startup/no-fix поведінка залишається консервативною**: no-fix, нуль C/N0 і
  початкове отримання fix усе ще використовують повільніший шлях, щоб прошивка
  не крутила конфігурацію приймача, поки RF-захоплення нестабільне.
- **SNR-захист залишається безпечним**: застарілий або відсутній SNR досі не
  може сам перевести плату в DR1. Швидше відновлення лише скорочує період
  відображення `SNR=NA`.

---

## v1.6.19 - 2026-06-02

Тестова прошивка лише для відновлення u-blox у стані без фікса. На момент релізу
v1.6.15 залишалася типовою стабільною версією на сервері; обирайте
`v1.6.19 (dev)` лише коли підтримка просить перевірити цю збірку.

### Прошивка

- **Допомога u-blox при нулі супутників до DR1**: коли приймач відповідає, але
  залишається на `SATS=0`, фільтр тепер надсилає cold start і reinit STM32
  приблизно через 2 хвилини. Це працює лише в режимі автоконфігу u-blox і не
  запускається в DR1, raw bridge або FC GPS forward-bypass.
- **Без автоматичного руйнівного очищення конфігурації u-blox**: `UBX_RESET=3`
  залишається ручною командою для стенду/recovery. Прошивка не очищає
  автоматично збережену конфігурацію u-blox у BBR/Flash, бо це може сповільнити
  отримання фікса або видалити навмисно збережений профіль приймача.
- **Ручний резервний спосіб залишається задокументованим**: якщо автоматичне
  відновлення при нулі супутників не повертає захоплення супутників, стендовий fallback
  залишається `UBX_RESET=3` із повним перезапуском живлення. Після автоматичної
  спроби прошивка логує `If stuck: bench UBX_RESET=3`.

---

## v1.6.18 - 2026-06-02

Тестова прошивка лише для стабілізації SNR на u-blox. На момент релізу
v1.6.15 залишалася типовою стабільною версією на сервері; обирайте
`v1.6.18 (dev)` лише коли підтримка просить перевірити цю збірку.

### Прошивка

- **Back-channel FC GPS більше не може змінювати профіль u-blox приймача у
  штатному захищеному режимі**: польові логи показали повторні періоди
  `SNR=NA` зі здоровими позиційними/fix даними та малими приростами `fcgps rx`
  безпосередньо перед зупинкою `NAV-SAT`. Тепер фільтр зчитує та рахує ці
  байти back-channel від FC, але не пропускає їх у приймач, тому
  записи автоконфігу/probe ArduPilot не можуть вимкнути потік `NAV-SAT`, який
  потрібен для SNR.
- **`fcgps rx` у штатному режимі тепер є лічильником зчитаних байтів**: він
  усе ще показує, що польотний контролер надсилає байти по GPS back-channel,
  але ці байти не можуть переконфігурувати приймач. Окремі raw-lab bridge
  збірки залишаються двонаправленими.
- **Діагностику u-blox CFG-GNSS виправлено**: рядок `ubxgnss ... ch.../...`
  тепер читає кількість каналів приймача з правильних полів payload
  `UBX-CFG-GNSS`. Це виправляє хибні діагностичні значення на кшталт `ch60/0`;
  конфігурацію сузір'їв ця зміна не змінює.

---

## Оновлення інструментів - 2026-05-29

Додаткове виправлення recovery для STM32F401 плат, які вже читаються як
`RDP0`, але все ще залишаються у `SPRMOD=1` / PCROP mode.

- **Перевірка статусу прошивки лише за ліцензійним ключем**: настільний застосунок
  тепер має кнопку **Перевірити статус**, яка використовує тільки ліцензійний
  ключ і не торкається ST-Link чи плати. Вона показує зареєстровані плати,
  плати з підтвердженим завершеним прошиванням, зареєстровані плати без
  звіту про прошивання, загальну кількість підтверджених успішних записів,
  типову стабільну прошивку на сервері та час прошивання для кожної плати.
- **Завершене прошивання тепер відстежується окремо від активації**:
  серверна реєстрація все ще відбувається до початку запису на плату, але
  додаток звітує про фізичне завершення лише після фінального запису
  bootloader та RDP lock. Старі активації можуть показуватися як
  зареєстровані без звіту про прошивання, доки їх не оновити версією додатка,
  яка звітує про фінальний успіх; вони показуються як legacy/unknown, а не як
  підтверджені невдалі прошивки.
- **Звіти про статус прошивки тепер автентифіковані**: сервер повертає
  короткочасний report token з кожним ST-Link Activate/Update пакетом, а
  фінальний callback відхиляє відсутні, прострочені, повторно використані або
  невідповідні токени. Для автентифікованих лічильників статусу використовуйте настільний застосунок `2026.05.29.9`
  або новіший.
- **Успішні Activate/Update тепер показують зрозумілий popup**: після
  фінальної точки фізичного успіху настільний застосунок відкриває OK-діалог із версією
  прошивки та UID плати, щоб користувачеві не доводилося читати log для
  підтвердження успішного завершення.
- **Успішний Recover Board тепер показує наступний крок**: після перевірки
  чистого flash і знятого RDP настільний застосунок відкриває OK-діалог із підказкою
  натиснути **Активувати**, щоб провізіонувати відновлену плату.
- **Ліцензії з кількома платами тепер можуть оновлювати вибрану плату**:
  коли на ліцензії зареєстровано кілька плат, настільний застосунок і CLI просять
  оператора ввести UID-short або повний UID цільової плати зі списку сервера
  до будь-якого доступу через ST-Link. Якщо підключена плата ховає фізичний
  UID через RDP1, окреме підтвердження RDP1 erase все одно з'явиться пізніше.
- **Завантаження застосунку з landing page тепер веде на зафіксований published
  EXE**: server більше не залежить від рухомого GitHub `latest` redirect, тому
  public download link не має віддавати старіший cached настільний застосунок після релізу.
- **Підказки power-cycle більше не радять підключати BlackPill USB-C**:
  настільний застосунок, CLI та self-install docs тепер кажуть зняти й повернути живлення
  плати. Якщо плата живиться від ST-Link 3V3, від'єднайте й під'єднайте USB
  ST-Link до ПК; не використовуйте USB-C роз'єм BlackPill.
- **Підпис прошивки тепер відділяє типову стабільну прошивку від вибраних dev-збірок**:
  настільний застосунок показує серверне значення як **Типова стабільна прошивка**
  замість "Server firmware version" / "Latest firmware", тому вибір dev
  прошивки у dropdown більше не виглядає як невідповідність із типовою
  стабільною прошивкою, показаною нижче.
- **Dropdown прошивок тепер позначає перший пункт як типову стабільну прошивку**:
  настільний застосунок показує `vX.Y.Z (stable default)` замість `vX.Y.Z (latest)`,
  а dev-збірки залишаються окремими пунктами `vX.Y.Z (dev)`.
- **License status на landing page використовує таке саме формулювання типової
  стабільної прошивки**: public license checker тепер підписує серверне значення як
  **Типова стабільна прошивка** замість загального "Firmware".
- **Логи активації тепер розділяють серверну реєстрацію і фізичний запис
  плати**: Activate показує, чи UID вже зареєстрований на сервері, чи буде
  зарезервований уперше, а потім окремо повідомляє, що сервер повернув пакет
  прошивки і починається запис на плату. Плата фізично провізіонована лише
  після фінального рядка `Provisioning complete`.
- **Активація тепер записує bootloader останнім і блокує плату в тій самій
  ST-Link сесії**: застосунок спочатку робить mass erase, записує та перевіряє
  application і metadata, поки сектор bootloader ще порожній, а потім записує
  та перевіряє bootloader і застосовує RDP1/BOR/SPRMOD/WRP однією командою
  CubeProgrammer. Це не дає bootloader запуститися і зробити flash нечитабельним
  до завершення перевірки на ПК.
- **Bootloader тепер враховує layout option bytes для F401xD/E**: якщо
  bootloader колись сам має застосувати RDP, він використовує восьмибітну WRP
  маску на STM32F401xD/E замість шестибітної маски F401xB/C.
- **Recovery write-protect для STM32F401xD/E тепер використовує per-sector WRP біти**:
  деякі плати показують `WRP0..WRP7` як окремі option bytes і відхиляють
  packed значення `WRP0=0x3F`. Recover/Update тепер переходить на
  `WRP0=0x1 ... WRP7=0x1` і більше не вважає попередження CubeProgrammer
  "invalid value / unchanged" успіхом.
- **RDP-drop recovery для STM32F401xD/E тепер очищає всі per-sector PCROP біти**:
  коли option bytes показують `WRP0..WRP7`, repair-запис RDP1->RDP0 тепер
  використовує `WRP0=0x0 ... WRP7=0x0` замість packed форми `WRP0=0x00`.
  Це не дає Activate/Recover повторно заблокувати плату з `SPRMOD=1` і
  активним PCROP.
- **Forced PCROP re-arm тепер пише лише RDP1**: Recover Board тимчасово
  повертає RDP1 тільки записом `RDP=0xBB`. Він більше не намагається очищати
  `WRP0` під час кроку RDP0->RDP1, бо STM32F4 дозволяє очищати PCROP/WRP0
  біти лише під час наступного переходу RDP1->RDP0.
- **Recover пропускає недійсний RDP-drop write, якщо RDP уже знято**: якщо
  плата вже у `RDP0`, додаток одразу переходить до перевірки/ремонту SPRMOD,
  замість no-op `RDP=0xAA` транзакції з небезпечним `WRP0=0x00` у RDP0.
- **Recover Board знову використовує OK/Cancel підтвердження**: typed
  `RECOVER` prompt прибрано. Додаток використовує звичайний destructive-action
  confirmation dialog.

---

## Оновлення інструментів — 2026-05-28

Екстрене оновлення recovery для STM32F401 плат, які після невдалих оновлень
залишилися у `SPRMOD=1` / PCROP mode.

- **PCROP salvage sequence змінено під WRP0-семантику F401**: Recover Board
  тепер знімає RDP через `RDP=0xAA` + `SPRMOD=0` + `WRP0=0x00` + `BOR_LEV=3`,
  а після power cycle знімає звичайний sector write protection через
  `WRP0=0x3F`. У базі STM32CubeProgrammer для STM32F401 WRP0 має лише шість
  бітів; коли `SPRMOD=1`, `WRP0=1` означає активний PCROP, тому старе
  all-ones значення могло залишати PCROP вибраним під час спроби очистити
  SPRMOD.
- **Option-byte записи тепер справді атомарні**: критичні зміни
  RDP/SPRMOD/WRP/BOR передаються як одна операція CubeProgrammer `-ob`.
  Повторення прапорців `-ob` може виконати окремі запуски option bytes, де
  `RDP=0xAA` перезапускає чип до застосування SPRMOD/WRP.
- **Виправлено bootloader option-byte mask**: sanitizer у bootloader тепер
  використовує шестибітне поле WRP0 для STM32F401 замість generic 8-bit nWRP
  mask.
- **Додано останній fallback для поганих option bytes**: якщо легальний
  цикл RDP1->RDP0 все ще залишає `SPRMOD=1`, Recover Board один раз пробує
  ST-команду `STM32_Programmer_CLI -ob unlockchip`, просить ще один реальний
  power cycle і лише після повторної невдачі повідомляє про hardware-stuck
  стан чипа.
- **Unlockchip тепер використовує стійкі ST-Link attach режими**: якщо
  стандартний SWD under-reset attach повертає неоднозначне `target not found`
  або lost-connection повідомлення, інструмент продовжує пробувати
  hardware-reset і hotplug режими перед power-cycle та перевіркою.
- **Діагностика option bytes тепер використовує ті самі fallback attach
  режими**: `-ob displ` повторюється з hardware-reset і hotplug режимами перед
  остаточною помилкою, тому recovery не падає лише через нестабільний
  стандартний SWD attach. CLI recovery також проводить option-byte записи через
  спільний timeout wrapper.
- **Перевірка після зняття RDP тепер спочатку читає option bytes**: після
  обов'язкового power cycle під час переходу RDP1->RDP0 Activate/Update і
  Recover Board парсять `RDP` з `-ob displ` перед будь-якою перевіркою через
  читання flash. Це не дає PCROP-блокованому flash у RDP0 виглядати як
  активний RDP1 і дозволяє запустити repair-шлях для SPRMOD/WRP.
- **Початкова перевірка RDP під час update теж спочатку читає option bytes**:
  перед записом прошивки Activate/Update перевіряє `RDP` з option bytes. Плата,
  яка вже читається як `RDP0/SPRMOD1`, тепер одразу переходить у PCROP repair,
  а не в помилковий шлях нового зняття RDP1.
- **CLI flash-операції тепер мають обмежені таймаути**: командний інструмент
  проводить читання UID, flash-проби RDP, читання контрольних слів, mass erase
  і запис flash через той самий timeout wrapper, що й безпечні option-byte
  шляхи. Flash/erase мають довгий таймаут 300 с; probe/read використовують
  короткий connect timeout.
- **Фінальна перевірка RDP у Recover Board тепер спочатку читає option bytes**:
  після фінального mass erase recovery читає `RDP` з option bytes перед
  fallback-перевіркою через flash-read. Це прибирає хибне повідомлення "RDP
  все ще активний", коли ціль уже в RDP0, але flash-read тимчасово
  заблокований або busy.
- **Некоректні option-byte dumps тепер мають безпечний fallback**: якщо
  desktop app або CLI може прочитати option bytes, але рядок `RDP` відсутній
  або не парситься, це більше не рахується як чиста плата. Інструмент
  переходить до flash-read RDP probe і зупиняється, якщо захист усе ще
  виглядає активним.
- **Flash-read проби у desktop app тепер мають обмежені таймаути**: визначення
  сімейства чипа, RDP flash probes, читання UID, читання UID-stub і single-word
  flash readback тепер використовують короткий CubeProgrammer timeout. Це не
  дає нестабільним ST-Link сесіям виглядати як зависання додатка.
- **Перевірка SPRMOD тепер зупиняється без припущень**: desktop app і CLI
  більше не переходять до `WRP0=0x3F` або запису flash, якщо option bytes не
  підтверджують `SPRMOD=0`. Це не дає погіршити стан, якщо PCROP все ще
  зафіксований, а ST-Link reads нестабільні.
- **Activate/Update тепер використовує той самий SPRMOD gate**: якщо `RDP` в
  option bytes відсутній або не читається, але flash-read probe виглядає як
  RDP0, інструмент усе одно перевіряє SPRMOD перед очищенням WRP0 або записом
  firmware.
- **Додано fallback сумісності WRP0/nWRP0**: якщо CubeProgrammer відхиляє
  назву option byte `WRP0`, desktop app і CLI повторюють ту саму операцію з
  `nWRP0`. Це допомагає з різними базами CubeProgrammer і не повторює RDP
  transition після reset цілі.
- **CLI timeout для option bytes тепер збігається з desktop app**: записи
  option bytes у command-line tool використовують задокументований timeout
  180 с, як і GUI.
- **PCROP repair re-arm тепер не чіпає WRP0**: forced recovery записує лише
  `RDP=0xBB` під час тимчасового повернення RDP1. `WRP0=0x00` застосовується
  тільки під час наступного RDP1->RDP0 clear, тобто в дозволеному переході для
  очищення PCROP/WRP0 бітів на STM32F4.
- **Bootloader option-byte writes зупиняються без припущень, якщо SPRMOD
  активний**: якщо плата якимось чином завантажиться з уже зафіксованим
  `SPRMOD=1`, bootloader більше не намагається писати BOR або RDP option
  bytes. Такий стан має ремонтувати Recover Board.
- **Command-line flashing відмовляється працювати з кількома ST-Link**: CLI
  тепер зупиняється до прошивки, якщо підключено більше одного ST-Link adapter,
  як і desktop app, щоб не записати не ту плату.
- **Update тепер перевіряє активацію ліцензії до роботи з RDP**: desktop app
  і CLI викликають `POST /api/v1/lookup-uid` перед ST-Link Update. Якщо
  ліцензія невалідна або не має активованої плати, інструмент зупиняється до
  підключення CubeProgrammer і до старту RDP1 erase. Якщо зареєстровано
  кілька плат, оператор має явно вибрати цільовий UID до доступу до hardware.
- **Activate відмовляється стирати будь-які RDP1-захищені плати**: Activate
  тепер перевіряє ліцензію до доступу до hardware, але все одно не знімає
  RDP1 навіть якщо введена ліцензія ще не має активацій. RDP1 ховає UID, тому
  Activate не може довести до стирання, що підключена плата порожня або
  належить саме цій ліцензії. Для вже активованої плати використовуйте
  Update, а для навмисного стирання і перепровізіонування - Recover Board.
- **Update для захищеної плати тепер вимагає підтвердження оператора перед
  erase**: коли RDP1 блокує читання UID, desktop app показує очікуваний UID
  активації та UID-short, а потім вимагає ввести UID-short перед зняттям RDP.
  CLI вимагає ввести очікуваний UID-short або повний UID перед стартом erase.
  Це не може довести фізичний UID до mass erase, але зупиняє сліпе оновлення
  не тієї захищеної плати.
- **Recover Board знову використовує OK/Cancel підтвердження**: desktop app
  залишає destructive-action confirmation, але більше не вимагає вводити
  `RECOVER`.
- **Retired Phase-C paths тепер fail-closed**: видима кнопка Update
  використовує ST-Link/SWD з v1.6.0, але старі USB-C/Phase-C worker-и для
  update і log download ще залишались у файлі desktop app. Тепер вони одразу
  повертають помилку disabled transport, якщо старий callback колись до них
  дійде, а нижчі Phase-C protocol mutator-и відмовляються від BEGIN/DATA/END
  і log команд до запису будь-яких serial bytes.

---

## Оновлення інструментів — 2026-05-27

Оновлення додатка провізіонування / CLI для плат, які вже мають захист RDP1.
Це зміна на стороні інструментів, а не зміна поведінки прошивки.

- **Безпечніше повторне прошивання захищених плат**: Activate/Update тепер
  обов'язково чекає фізичного перепідключення живлення одразу після зняття
  RDP1 і до будь-якого запису прошивки. Це відповідає recovery-процедурі й
  не дає почати запис, поки контролер flash STM32F4 ще напівзафіксований після
  переходу RDP1->RDP0.
- **Виправлено очищення PCROP/SPRMOD під час оновлення захищених плат**:
  запис зняття RDP тепер одночасно передає `RDP=0xAA` + `SPRMOD=0` +
  WRP-біти. STM32F4 дозволяє очищати SPRMOD лише під час переходу RDP1->RDP0,
  тому додаток більше не намагається очищати SPRMOD після цього і не позначає
  справні плати як hardware-stuck.
- **Повторна спроба працює для плат, уже залишених у RDP0/SPRMOD1**: якщо
  попереднє невдале оновлення залишило плату доступною для читання, але
  заблокованою PCROP, додаток спочатку виконує легальний RDP recycle зі
  SPRMOD і WRP-бітами у тому самому RDP-drop записі, просить power cycle і
  повторює запис прошивки.
- **Менше вікно для brick у CLI**: `gnss_provision.py` більше не виконує
  окремий mass erase перед комбінованим записом прошивки. Він записує повний
  образ в одній операції CubeProgrammer після тієї самої підготовки RDP1.
- **CLI retry має parity з desktop app**: якщо command-line updater знаходить
  плату, яка вже читається, але заблокована старим станом `RDP0/SPRMOD1`, він
  тепер виконує той самий легальний RDP recycle, просить power cycle і один
  раз повторює комбінований запис прошивки.
- **Додано перевірку RDP re-arm**: під час forced PCROP/SPRMOD recovery
  додаток тепер підтверджує, що тимчасове `RDP=0xBB` справді зафіксувалося
  після power cycle, і лише тоді виконує `RDP=0xAA` + `SPRMOD=0`. Якщо ні, він
  зупиняється до недозволеного очищення SPRMOD.
- **PCROP recovery посилено**: додаток тепер перевіряє RDP через option bytes,
  а не через читання flash, бо PCROP може блокувати flash-read навіть при
  RDP0.
- **Уточнено опис Recovery**: Recover Board розблоковує, стирає і перевіряє
  порожній чип. Він не встановлює прошивку; після recovery потрібно виконати
  **Activate** або **Update** з ліцензійним ключем.
- **Виправлено BOR recovery handling**: recovery використовує `BOR_LEV=3`
  (BOR off на STM32F4) під час erase, а фінальне блокування відновлює
  production `RDP=0xBB` + `BOR_LEV=0` тим самим записом option bytes.
- **Менше false update failures**: якщо CubeProgrammer повідомив про успішний
  запис option bytes, але повернув non-zero exit code під час фінального lock,
  додаток тепер вважає lock committed і не показує failed flash.
- **Безпечніше закриття додатка**: desktop-додаток більше не вбиває активну
  операцію Activate, Update або Recover при закритті вікна. Він показує
  попередження і залишає операцію активною, доки не завершаться flash/erase,
  записи option bytes, пауза після erase та діалоги перепідключення живлення.
- **Довші таймаути CubeProgrammer**: операції запису flash і mass erase тепер
  мають таймаут до 300 секунд, а записи option bytes - до 180 секунд. Це
  зменшує ризик перервати нормальне оновлення на повільному ПК або слабкому
  USB-хабі.
- **Readback flash перед RDP1**: після комбінованого запису прошивки додаток
  зчитує контрольні слова з bootloader, application та metadata областей. Якщо
  будь-яка перевірка не проходить, він зупиняється до повторного блокування
  RDP1, тож плата залишається доступною для повторної спроби.
- **Legacy UART update заблоковано**: `gnss-provision update --uart` приховано
  з довідки, і тепер команда завершується до відкриття порту чи запису flash.
  Оновлення підтримуються лише через ST-Link/SWD або кнопку Update у desktop
  app.
- **Оброблено ST-Link USB communication reset під час зняття RDP**: якщо
  CubeProgrammer показує `DEV_USB_COMM_ERR` під час запису `RDP=0xAA`, додаток
  тепер переходить до обов'язкового unplug/replug та перевіряє, чи RDP справді
  знято. Це прибирає false failure до початку запису прошивки.
- **Надійніше перше підключення через ST-Link**: якщо звичайне SWD-підключення
  не вдається, desktop-додаток повторює спробу з hardware-reset і hotplug
  режимами підключення, включно з нижчою швидкістю SWD, та показує корисну
  діагностику CubeProgrammer. Якщо всі режими не підключаються, плата
  недоступна через SWD і треба перевіряти проводи, живлення, reset, адаптер або
  сам MCU.
- **Зрозуміліша підказка при помилці підключення**: якщо всі режими ST-Link не
  підключаються, додаток і CLI тепер радять під'єднати NRST/RST до reset-піна
  ST-Link або утримувати RESET під час старту Update/Recover. CLI використовує
  ті самі reset/hotplug fallback-и підключення, що й додаток.
- **Видима версія desktop-додатка**: додаток показує власну версію у вікні та
  стартовому логі, окремо від списку версій прошивки.
- **Підключення більше не виглядає як зависання**: додаток показує кожний SWD
  режим підключення, який пробує, а кожна спроба обмежена 10 секундами.
- **Швидша перевірка ST-Link адаптера**: додаток тепер перелічує ST-Link
  адаптери без попередньої спроби підключитися до цільової плати, тому
  проблемна плата не може затримати появу логів режимів підключення.

---

## v1.6.17 — 2026-05-26

Оновлення лише прошивки для коректного дотримання DR lock. Ця збірка
зберігає поведінку відновлення SNR для u-blox з v1.6.16 і уточнює таймінги
DR1.

### Прошивка

- **`DR_LOCK_MS` тепер є справжнім мінімальним часом у DR1**: якщо
  `DR1_MAXMS` також встановлено і він спливає раніше за вікно блокування,
  прошивка залишається в DR1 до завершення `DR_LOCK_MS`.
- **Таймінг повторного приєднання чекає завершення блокування**: вікно
  стабільності повторного приєднання і GNSS-blend не стартують, доки активний
  `DR_LOCK_MS`.
- **Блимання статусного LED стало стабільнішим**: завантаження списку
  параметрів у Mission Planner більше не блокує головний цикл, а DR1-патерн
  LED тепер відповідає тому самому стану `DR=`, який видно в логах.

---

## v1.6.16 — 2026-05-21

Тестове `dev`-оновлення таймінгу відновлення SNR для u-blox. На момент релізу
v1.6.15 залишалася типовою стабільною версією на сервері; v1.6.16
прошивається лише коли ви явно обираєте пункт `v1.6.16 (dev)` у застосунку провізії. Змін у
підключенні або параметрах тюнінгу немає.

### Застосунок провізії / сервер

- **Dev-прошивка відокремлена від стабільної**: список прошивок залишає
  `v1.6.15 (stable default)` типовою стабільною прошивкою і показує
  `v1.6.16 (dev)` внизу списку.
- **Вибір dev-збірки прошиває правильний образ**: сервер і оновлений
  застосунок передають окремі поля для відображення та raw-версії, тому оператор бачить
  `v1.6.16 (dev)`, але плата отримує raw-версію прошивки `1.6.16`.

### Прошивка

- **Швидше відновлення, коли NAV-SAT вимикається після старту**: польові логи
  показали здорові `NAV-PVT`/fix дані та `SATS=29`, але `NAV-SAT` зупинився
  після малого back-channel запису з FC GPS і `SNR=NA` тримався до повторного
  увімкнення NAV-SAT шляхом відновлення. Таймер застарілого SNR тепер
  запускається одразу, коли SNR стає застарілим, але прошивка все одно чекає,
  поки застаріє сам NAV-SAT, перед переписуванням конфігурації приймача. Це
  зберігає поведінку v1.6.15 з урахуванням самого потоку NAV-SAT, але скорочує
  типовий час відновлення приблизно з двох вікон застарівання до одного.
- **SNR-захист залишається безпечним щодо хибного спрацювання**: `SNR_EN=1`
  досі не може перевести в DR1 через `SNR=NA` або застарілі SNR-дані.
  Застарілий SNR ігнорується прямим SNR-захистом і оцінкою довіри до спуфінгу.

---

## v1.6.15 — 2026-05-21

Реліз лише прошивки для сумісності та відновлення u-blox. Це публічне
продовження v1.6.12; проміжні тестові збірки 1.6.13/1.6.14 включені в цей
реліз і не показуються як окремі версії прошивки на сервері.

### Прошивка

- **Діагностика u-blox без фікса**: коли `SATS=0` або позиційний фікс
  невалідний, прошивка опитує `UBX-MON-RF`, `UBX-SEC-SIG` і `UBX-CFG-GNSS` та
  логує `ubxpvt ...`, `ubxrf ...`, `ubxsig ...` і `ubxgnss ...` у Mission
  Planner.
  Ці рядки показують прапори фікса NAV-PVT, стан антени/RF, явний стан
  jamming/spoofing, якщо приймач це підтримує, і конфігурацію увімкнених
  GNSS-сузір'їв.
- **Ручна команда відновлення u-blox**: новий віртуальний параметр `UBX_RESET`
  видно у Mission Planner, але він не зберігається у flash-пам'яті. `1`
  запускає hot start, `2` запускає cold start, `3` очищає збережену
  конфігурацію u-blox у BBR/Flash, завантажує стандартні налаштування, перезапускає приймач
  і дає STM32 заново ініціалізувати GNSS.
- **Без автоматичного скидання до заводських налаштувань**: руйнівне очищення
  конфігурації приймача виконується тільки через адресований `PARAM_SET` до
  STM32-фільтра.
- **Зрозуміліші логи стану без фікса**: поле `fix=...` у періодичних логах
  тепер показує тільки вік валідного позиційного фікса. Якщо приймач живий,
  але фікса немає, `fix=...` буде старим, а `nav=...` свіжим.
- **Відновлення SNR для u-blox тепер враховує сам потік NAV-SAT**: прошивка
  заново надсилає конфігурацію NAV-SAT лише коли NAV-SAT кадри відсутні або
  застарілі. Якщо NAV-SAT надходить, але має нуль придатних C/N0, приймач
  перебуває в захопленні супутників або не має придатного RF-сигналу, тож
  прошивка лише логує діагностику і не переписує конфігурацію.
- **Звужений профіль VALSET під час старту**: UART2 NAV-SAT більше не
  записується постійно під час старту. UART2 залишається у шляху відновлення
  тільки в RAM для плат, де NAV-SAT справді відсутній на лінку, який слухає
  фільтр.

---

## v1.6.12 — 2026-05-21

Реліз сумісності приймачів лише для прошивки. Наявні плати оновлюються через
стандартний шлях ST-Link у застосунку провізії.

### Прошивка

- **Виправлення F9P NAV-SAT / SNR**: UBX-парсер тепер приймає великі
  `NAV-SAT` кадри від F9P-класу приймачів з великою кількістю супутників у
  полі зору. Це виправляє логи Mission Planner, де `SATS` і вік фікса були
  здоровими, але `SNR=NA` тримався постійно.
- **Діагностика застарілого SNR**: якщо SNR від u-blox застаріває, періодичні
  повідомлення додають компактний рядок `snrdbg`, щоб підтримка бачила, чи
  `NAV-SAT` відсутній, пошкоджений/не проходить контрольну суму, завеликий,
  або приходить без придатних C/N0.
- **Відновлення застарілого SNR**: команда відновлення заново вмикає NAV-SAT
  через legacy `CFG-MSG` і `CFG-VALSET` на UART1/UART2, що покриває F9/F10
  плати-носії, де активний порт приймача не є UART1.
- **Застарілий SNR пропускається в оцінці довіри**: SNR, pseudorange residual і
  SNR-correlation тепер використовують те саме вікно свіжості, що й статусний
  рядок Mission Planner `SNR=...`.

---

## v1.6.11 — 2026-05-15

Діагностичний реліз лише прошивки. Наявні плати оновлюються через стандартний
шлях ST-Link; змін у підключенні, параметрах тюнінгу або застосунку провізії
немає.

### Прошивка

- **Сирий діагностичний обхід пересилання FC GPS** (`FCGPS_FWD=1`): коли
  увімкнено, фільтр примусово вмикає FC GPS UART і пересилає потік приймача до
  польотного контролера до того, як DR1-захист від спуфінгу, стартова північна
  перевірка, огорожа півкулі, затримка конфігурації UM980 або watchdog
  відновлення стану без фікса зможуть його заблокувати. Використовуйте це
  тільки для стендової діагностики та перевірки проводки; для захищеного
  польоту тримайте `FCGPS_FWD=0`.

---

## v1.6.3 — 2026-04-14

Реліз стабільності та приватності на основі v1.6.2. Без нових параметрів тюнінгу, без змін у підключенні, без дій у полі окрім запуску інструмента провізії.

### Прошивка

- **Запобіжне обмеження лічильника супутників NMEA**: парсер NMEA GGA тепер обмежує поле «супутники у видимості» значенням 255 перед передачею далі. Захист від пошкоджених або невідповідних специфікації речень від багатоконстеляційних приймачів із незвично великою кількістю супутників.
- **Запас сторожового таймера під час конфігурації приймача**: кожен крок запису-та-очікування-ACK для u-blox `CFG-*` тепер перезавантажує незалежний сторожовий таймер на вході. 20-кроковий пакет конфігурації на завантаженні більше не з'їдає бюджет сторожового таймера на повільних приймачах.
- **Надійність журналу спуфінг-подій**: вбудований записувач подій тепер повідомляє, який слот він використав (або явно сигналізує «пропущено»), тож дебаунсований повторний запис не може пошкодити непов'язані події, коли плата виходить з dead-reckoning і записує тривалість тригера заднім числом.

### Завантажувач

- **Запобіжник захисту від відкоту на етапі збірки**: завантажувач тепер провалює збірку, якщо поріг захисту від відкоту відсутній у конфігурації збірки, замість мовчазного значення нуль за замовчуванням (що приймало б будь-яку версію прошивки). Переповнення бітового поля у кодуванні версії також виявляється на етапі збірки.
- **Політика відновлюваності поетапного оновлення задокументована**: обмежена поведінка повторних спроб після збою живлення тепер є явним інваріантом (задокументована, не змінена). Функціональних змін для операторів немає; важливо лише для розробників, які беруть вихідний код.

### Сервер

- **Ліцензійний ключ більше не в URL**: пошук статусу ліцензії має новий варіант `POST /api/v1/license-status`, який приймає ключ у тілі запиту. Форма самообслуговування на головній сторінці використовує новий шлях, тож ключі перестають з'являтися в журналах доступу nginx. Застарілий варіант `GET ?key=…` досі працює для старих клієнтів.
- **IP-адреси аудиту врахуваючи XFF**: адміністративні дії очищення за термінами зберігання та видалення PII тепер записують реальну IP клієнта через `X-Forwarded-For`, а не loopback-адресу зворотного проксі nginx. Рядки аудиту, записані до цього релізу, залишаються як є.
- **Фіксація старої версії прошивки при активації**: `/api/v1/activate` тепер приймає необов'язкове поле `version`. Інструмент провізії використовує це, коли ви обрали щось інше, ніж типова стабільна прошивка, у випадаючому списку версій.

### Інструменти — застосунок AirDroper GNSS Filter

- **Чисте завершення під час провізії**: закриття вікна застосунку під час запису через ST-Link тепер коректно завершує дочірній процес `STM32_Programmer_CLI`, замість того щоб залишати осиротілі процеси, які утримують порт SWD.
- **Попередня перевірка кількох адаптерів при активації**: кнопка Activate тепер відмовляється розпочинати роботу, якщо підключено більше одного ST-Link V2, з тим самим діалогом «від'єднайте інші», який Recovery використовує з v1.6.0. Запобігає переактивації не тієї плати, коли на лабораторному стенді підключено кілька адаптерів.
- **Активації з фіксованою версією**: коли ви обираєте версію, відмінну від типової стабільної, у списку прошивок, Activate тепер надсилає цей вибір на сервер (відповідає тому, як Update уже працював).

### Документація

- **Посібник з відновлення** ([04_recovery.md](https://github.com/AirdroperUA/gnss-filter-user-docs/blob/main/04_recovery.md)): додано діагностику збоїв воріт та рецепти відновлення для відхилення anti-rollback, відхилення UID-прив'язки, збою запису RDP посередині провізії, та ескалації до апаратного блокування. Посилання для розробників; звичайне використання у полі не змінюється.

---

## v1.6.2 — 2026-04-14

Реліз сумісності приймачів та стійкості провізії. Завершує перехід USB-C → ST-Link з v1.6.0.

### Прошивка

- **Автоматична конфігурація NAV-SAT для u-blox F10 / M10**: новіші покоління u-blox (серія F10, серія M10) використовують інтерфейс конфігурації `CFG-VALSET` і не завжди реагують на застарілий увімкнення поточного повідомлення. Фільтр тепер на завантаженні надсилає профіль `CFG-VALSET`, який вмикає `NAV-SAT` на правильному порту з правильною частотою. Сигнали виявлення спуфінгу, що спираються на аналіз SNR та carrier-to-noise по супутниках, тепер працюють одразу на приймачах F10/M10 без попереднього налаштування в u-center. Не впливає на M8/M9 або UM980.

### Інструменти / Провізія

- **Провізія відновлюється після захищених від запису секторів**: якщо стирання флешу зривається через те, що на попередньому образі активний option-byte write-protection (`nWRP`), інструмент провізії тепер автоматично знімає захист і повторює спробу. Раніше такі плати вимагали ручного сеансу в STM32CubeProgrammer.
- **Діалог переживлення тепер блокуючий**: коли плата потребує жорсткого переживлення посередині провізії (наприклад, після зміни option-байтів), діалог тепер блокує процес до підтвердження завершення переживлення. Запобігає гонці, коли наступний запис стартує проти напівпереініціалізованої цілі.
- **USB-C CDC у завантажувачі повністю вимкнено**: `BOOTLOADER_PHASEC_ENABLE=0` тепер постійне. Контакти `PA11/PA12` безумовно доступні для UART GPS польотного контролера (USART6). Ця зміна була анонсована у v1.6.0; v1.6.2 видаляє останні шляхи коду.
- **Рядок USB-C прибрано з застосунку**: старий селектор порту «(USB-C auto-detect)» зник. Activate, Update та Recover використовують шлях SWD через ST-Link V2.

### Документація

- Посібники для користувачів повторно переглянуто та скорочено під тільки-ST-Link-потік. [Посібник самостійної установки](10_self_install.md) та FAQ з оновлення прошивки більше не згадують шлях USB-C.

---

## v1.6.1 — 2026-04-13

Реліз надійності. Патчить три незалежні проблеми, що виявилися у полі після v1.6.0. Без змін у конфігурації.

### Прошивка

- **Передача керування завантажувач → застосунок посилена**: на деяких платах збій валідації прошивки з подальшою повторною спробою міг залишити застосунок зі старим станом NVIC, із заблокованими перериваннями (`PRIMASK=1`) або з реєстром увімкнення тактування `AHB2ENR`, досі налаштованим для USB-периферії завантажувача — симптоми були у вигляді миттєво зависаючої плати зі статус-діодом, що залишається вимкненим після завершення завантажувача. Передача керування тепер явно очищує біти pending/enable NVIC, скидає `AHB2ENR`, очищує `PRIMASK`, щоб переривання були дозволені на старті застосунку, і очищує будь-які защіпнуті прапори збоїв.
- **Відновлено діагностичне перенаправлення GPS** (`FCGPS_FWD=1`): коли параметр `FCGPS_FWD` встановлено у `1`, фільтр вмикає FC GPS UART, сиро пересилає потік GPS до польотного контролера та обходить DR1, стартові північні ворота і захист півкулі. Призначено **лише для діагностичного стендового використання**; у польоті це зводить нанівець саму суть фільтра. Типове значення залишається `0`.

### Інструменти — застосунок AirDroper GNSS Filter

- **Ctrl+V вставка працює при кириличних розкладках клавіатури**: поле ліцензійного ключа раніше ігнорувало Ctrl+V, коли активною розкладкою була українська або російська (keysym «V» під цими розкладками не дорівнює `v`). Прив'язка тепер спрацьовує на фізичному keycode, тож вставка працює незалежно від поточно обраної розкладки.

---

## v1.6.0 — 2026-04-11

Реліз із посиленням безпеки та надійності. Чотири паралельні глибокі перегляди коду (R19–R22) охопили прошивку, сервер і завантажувач. **Без змін у конфігурації — існуючі плати оновлюються на місці та продовжують працювати. Без нових параметрів тюнінгу, без змін у підключенні.**

### Прошивка

- **Посилений таймер активації спуф-захисту**: вікно «стабільний фікс протягом N секунд до активації» тепер вимірюється у реальному часі. Виправляє граничний випадок, коли застарілий GPS-фікс міг передчасно активувати захист.
- **Запобігання затримкам при дампі параметрів MAVLink**: дамп усіх ~62 параметрів тюнінгу до GCS (наприклад Mission Planner) більше не призводить до короткочасного простою спуф-захисту — кожні 8 параметрів дамп віддає керування парсеру GNSS та сторожовому таймеру.
- **Повторна активація захисту після виходу з DR1**: після виходу з DR1 (dead-reckoning) до нормального відстеження спуф-захист тепер заново проходить вікно стабільності на кожному циклі, а не переносить попередній стан активації. Поведінка у звичайній роботі не змінюється — це семантичне очищення, щоб інваріант активації завжди зберігався.
- **Суворіша автентифікація параметрів GCS**: повідомлення `PARAM_SET` тепер відхиляються, якщо MAVLink system ID відправника не збігається з очікуваним автопілотом. Якщо ви використовуєте GCS із нестандартним `SYSID_MYGCS`, перед оновленням перевірте, що він відповідає вашому автопілоту.
- **Захист координат u-blox**: захист від NaN / значень широти або довготи поза діапазоном у пошкоджених кадрах NAV-PVT.
- **Таймінг автобаудрейту UM980**: перезавантаження сторожового таймера під час визначення швидкості приймача. Виправляє рідкісні зависання при завантаженні на повільних UM980.
- **Прапори збірки проти реверс-інжинірингу**: видалені символи, оптимізація часу компонування (LTO), усунення мертвого коду, захист стеку — ускладнюють реверс-інжиніринг готового бінарника.

### Сервер / Інструменти

- **Точно закріплені Python-залежності**: усі серверні залежності тепер закріплені через `==` замість `~=`. Усуває дрейф патч-версій між розгортаннями.
- **Маскування ліцензійних ключів в аудит-логах**: аудит-лог `gnss-license` тепер зберігає лише відбиток (`first4...last4#sha256[:12]`) замість повного ключа. Існуючі записи не зачіпаються; нові записи використовують формат відбитка.
- **Захист від DNS-rebind**: ендпоінт webhook challenge тепер розв'язує та перевіряє цільові імена хостів на стороні сервера.
- **Очищення rate-limiter**: виправлено граничний випадок використання пам'яті у per-IP rate limiter, де IP-адреси з відповіддю 429 могли залишати порожні записи.
- **Примус HTTPS на /health та /api**: прямий HTTP-трафік тепер повертає 403 замість того, щоб проходити рівень застосунку.
- **Виправлення реєстрації пристрою**: посилено `require_owner` на ендпоінті `/register-key` (виправлено баг розбору тіла запиту).

### Завантажувач

- **Видалено оновлення прошивки через USB-C**: завантажувач більше не з'являється у системі як USB CDC-пристрій. Піни PA11/PA12 зарезервовані під GPS UART (USART6) контролера польоту. Усі оновлення прошивки, відновлення та активація тепер виконуються лише через **ST-Link V2 SWD**.
- Внутрішні оновлення паритету з хвилі посилення R19; межа захисту від відкату залишається на v1.5.5, щоб існуючі польові пристрої могли прийняти цей реліз.

### Інструменти

- **Додаток AirDroper GNSS Filter**: видалено пункт порту «(USB-C auto-detect)» та кнопку **Завантажити логи**. Активація, Оновлення та Відновлення тепер виконуються через ST-Link V2, підключений до 4-пінного SWD-роз'єму (3V3, GND, A14/SWCLK, A13/SWDIO).

### Логування

- **Збір логів переміщено на SD-карту контролера польоту**: події виявлення спуфінгу тепер надсилаються як MAVLink-повідомлення **STATUSTEXT** і **NAMED_VALUE_INT**, які ArduPilot записує як dataflash-записи `MSG` / `NVLI` у `.bin`-лог на SD-карті ПК. Бортовий журнал подій і процедура його завантаження через USB більше не існують.

### Документація

- Перероблено розділи «Оновлення прошивки» та «Журнал подій спуфінгу» у [Самостійній установці](#self-install) під ST-Link-only процедуру оновлення та збір логів зі SD-карти.
- Оновлено пункти FAQ щодо оновлення прошивки та завантаження логів.

---

## v1.5.5 — 2026-04-05

### Прошивка

- **Оцінка достовірності спуфінгу**: новий `DR_CONF` (0–100) з 8 зважених сигналів виявлення — аномалії SNR, pseudorange residual, часова кореляція SNR, розворот курсу, зміни GDOP, дрейф часу GPS, невідповідність швидкості та позиції, стрибок тактового зсуву. Бал автоматично адаптується при недоступних сигналах (напр., UM980 використовує ~5 з 8).
- **Виявлення розвороту курсу**: активує DR1 при раптовій зміні напрямку, що не відповідає IMU.
- **Виявлення аномалії часу GPS**: активує DR1 при неочікуваному стрибку часу GPS.
- **Гео-огорожа** (`FENCE_RAD`): активує DR1, якщо позиція виходить за радіус від першого фіксу (за замовчуванням 600 км, макс. 2000 км). Ловить повільний дрейф спуфінгу.
- **Жорстке блокування південної півкулі**: миттєвий DR1 при широті нижче 0°. Тепер налаштовується через параметр `HEMI_EN`.
- **Виявлення стрибку тактового зсуву** (тільки u-blox): використовує NAV-CLOCK для виявлення маніпуляцій з годинником приймача.
- **Невідповідність швидкості та позиції** (тільки u-blox): перехресна перевірка швидкості та дельти позиції.
- **Макс. тривалість DR1** (`DR1_MAXMS`): примусовий вихід з DR1 після налаштовуваного таймауту. Корисно для далеких місій.
- **Оновлення через USB-C**: підключіть USB-C кабель, натисніть RESET — додаткове обладнання не потрібне після першої прошивки.
- **Завантаження логів через USB-C**: логи спуфінгу можна завантажити безпосередньо через USB-C.
- **Виправлення запуску додатка**: виправлено таблицю векторів за адресою 0x0800C000.
- **RDP1 відновлено**: захист від зчитування повернено після налагодження v1.5.4.

### Сервер / Інструменти

- **SpoofEvent v2**: розширений формат подій з оцінкою достовірності та деталізацією тригерів.
- **Експорт KML/GPX**: завантаження подій спуфінгу як KML (Google Earth) або GPX з хмарної панелі.
- **Виявлення аномалій флоту**: панель відмічає незвичайні патерни серед кількох плат.
- **Інструмент прошивки**: режим USB-C auto-detect — оберіть "(USB-C auto-detect)" як порт.

### Документація

- Додано документацію оцінки достовірності з таблицею ваг сигналів.
- Додано таблицю порівняння функцій u-blox та UM980.
- Задокументовано нові тригери DR1 (курс, час, гео-огорожа, тактовий зсув, швидкість-позиція).
- Додано `DR1_MAXMS`, `FENCE_RAD`, `HEMI_EN` до інструкції з тюнінгу.

---

## v1.5.4 — 2026-04-04

### Прошивка

- **Критичне виправлення**: компілятор оптимізував перевірки sentinel-ключів як константи, через що валідація прошивки завжди проходила. Виправлено за допомогою volatile-бар'єрів.
- **Перенесення ініціалізації PLL**: PLL-ініціалізація переміщена перед валідацією додатка для швидшого завантаження.
- **Детальні коди помилок**: додано діагностичні коди BEGIN BAD_METADATA для спрощення налагодження.

---

## v1.5.3 — 2026-04-04

### Прошивка

- **Прив'язка до UID**: прошивка тепер криптографічно прив'язана до унікального апаратного ID плати. Копіювання на іншу плату робить її непрацездатною.
- **Посилення безпеки**: додаткові перевірки цілісності в завантажувачі.

### Сервер / Інструменти

- **Лендінг та документація**: запущено gps.airdroper.org з повною документацією.
- **Десктопний додаток (.exe)**: AirDroper GNSS Filter — інструмент прошивки з GUI.
- **Селектор версій документації**: перегляд документації для конкретних версій прошивки.

---

## v1.5.0 — 2026-04-03

### Прошивка

- **Логування подій SpoofAnalytics**: події спуфінгу зберігаються у flash-пам'яті плати з часовою міткою, позицією, причиною тригера, кількістю супутників та SNR-даними.
- **Завантаження логів**: події можна завантажити на хмарну панель через USB-UART або USB-C.

### Сервер

- **Хмарна панель** (gps.airdroper.org/dashboard): веб-інтерфейс для перегляду подій спуфінгу, треків польоту та стану плат.
- **Карта РЕБ перешкод** (gps.airdroper.org/ew-map): жива глобальна карта GNSS перешкод з ADS-B, морськими AIS, повітряними тривогами, 61 відомою зоною РЕБ, краудсорсинговими звітами, оцінкою ризику маршруту, Telegram сповіщеннями та прогностичною моделлю.
- **Сервер ліцензій**: автоматизоване провізіонування та розповсюдження прошивки.
- **Посилення сервера**: обмеження швидкості запитів, валідація введення, HTTPS.
