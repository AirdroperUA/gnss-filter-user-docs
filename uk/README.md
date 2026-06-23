# Користувацька документація

> Де купити плату: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

Англійська версія: `docs/user/README.md`.

Важливо: параметри STM32-фільтра змінюються у Mission Planner:
- `Config/Tuning` -> `Full Parameter List`
- оберіть систему STM32 (`SYSID 42`)
- `Refresh Params` -> змініть значення -> `Write Params`
- на завантаженому MAVLink-лінку запис може потребувати 1-2 спроби; завжди робіть `Refresh Params` для підтвердження
- Необов'язково, але рекомендовано: встановіть [AirDroper Mission Planner Params](https://gps.airdroper.org/download/mission-planner-mod), щоб Mission Planner показував описи, діапазони, одиниці та підписи варіантів.

H743 DroneCAN note: H743 DroneCAN firmware не має F401-style Mission Planner
MAVLink parameters через flight-controller serial link. У firmware `v0.1.4+`
параметри змінюються через Mission Planner
`DroneCAN/UAVCAN -> node 42 -> Params`; у firmware `v0.1.5+` також можна
підключити Mission Planner напряму до H743 USB-C COM port на `115200`. GPS
публікується як native DroneCAN GPS. Див. окремий guide:
[WeAct H743 DroneCAN](13_h743_dronecan.md), включно з HD-15 D-sub box pinout
для FC CAN, живлення бокса, GNSS UART/power та optional DR1 status.

Для штатного польоту на платі має бути встановлена звичайна робоча збірка.

Перезавантаження не потрібне після кожної зміни параметра.
- Для `GNSS_TYPE` та `UBX_BAUD` потрібен reboot STM32 (`NRST` або повне вимкнення/увімкнення).
- Більшість інших параметрів застосовуються одразу.

## Відеоуроки

<div style="display: grid; grid-template-columns: minmax(180px, 300px) minmax(240px, 1fr); gap: 16px; align-items: center; margin: 16px 0 24px;">
  <a href="12_video_tutorials.md#flash-new-board" aria-label="Відкрити відеоурок про прошивку нової плати через Windows-додаток">
    <img src="https://i.ytimg.com/vi/vXlP-tu7s1k/hqdefault.jpg" alt="Прев'ю відео: прошивка нової плати через Windows-додаток" width="300" loading="lazy">
  </a>
  <div>
    <strong>Прошивка нової плати через Windows-додаток</strong>
    <p>Подивіться повний процес активації та прошивки чистої STM32-плати через Windows <code>.exe</code>-додаток AirDroper GNSS Filter.</p>
    <p><a href="12_video_tutorials.md#flash-new-board">Відкрити сторінку уроку</a> або <a href="https://youtu.be/vXlP-tu7s1k">дивитися на YouTube</a>.</p>
  </div>
</div>

<div style="display: grid; grid-template-columns: minmax(180px, 300px) minmax(240px, 1fr); gap: 16px; align-items: center; margin: 16px 0 24px;">
  <a href="12_video_tutorials.md#stlink-pinout" aria-label="Відкрити відеоурок про підключення ST-Link і пін-аут плати">
    <img src="https://i.ytimg.com/vi/bOzFh70B66g/hqdefault.jpg" alt="Прев'ю відео: підключення ST-Link і пін-аут плати" width="300" loading="lazy">
  </a>
  <div>
    <strong>Підключення ST-Link і пін-аут плати</strong>
    <p>Апаратний огляд прошивки: підключення ST-Link, пін-аут плати та фізична підготовка перед роботою у Windows-додатку.</p>
    <p><a href="12_video_tutorials.md#stlink-pinout">Відкрити сторінку уроку</a> або <a href="https://youtube.com/shorts/bOzFh70B66g">дивитися на YouTube</a>.</p>
  </div>
</div>

<div style="display: grid; grid-template-columns: minmax(180px, 300px) minmax(240px, 1fr); gap: 16px; align-items: center; margin: 16px 0 24px;">
  <a href="12_video_tutorials.md#wiring" aria-label="Відкрити відеоурок про загальне підключення">
    <img src="https://i.ytimg.com/vi/ARGg_KQceoU/hqdefault.jpg" alt="Прев'ю відео: загальний огляд підключення" width="300" loading="lazy">
  </a>
  <div>
    <strong>Загальний огляд підключення</strong>
    <p>Почніть звідси для короткого візуального огляду підключення STM32, GNSS-приймача та польотного контролера.</p>
    <p><a href="12_video_tutorials.md#wiring">Відкрити сторінку уроку</a> або <a href="https://youtube.com/shorts/ARGg_KQceoU">дивитися на YouTube</a>.</p>
  </div>
</div>

1. `01_device_overview.md` - загальний опис роботи пристрою та приклади тригерів.
2. `02_wiring.md` - фізичне підключення STM32, GNSS-приймача та FC.
3. `03_wiring_debug.md` - діагностика проблем підключення GNSS/GPS/MAVLink.
4. `04_setup_and_flash.md` - налаштування та конфігурація UART на FC.
5. `04_recovery.md` - коротка сторінка відновлення та дані для звернення в підтримку.
6. `05_operation.md` - поведінка під час роботи (DR0/DR1, блокування GNSS, імпульс події).
7. `06_tuning.md` - параметри тюнінгу та робота через Mission Planner.
8. `07_cheat_sheet.md` - коротка довідка для швидких перевірок.
9. `08_lab_validation.md` - безпечна лабораторна валідація перед реальними польотами.
10. `09_receiver_config.md` - конфігурація GNSS-приймача для u-blox, UM980 та Mosaic X5 (профілі, налаштування GPS-типу ArduPilot).
11. `10_self_install.md` - самостійна установка прошивки на чисту плату BlackPill за допомогою ліцензійного ключа.
12. `11_faq.md` - часті запитання щодо роботи фільтра, апаратного забезпечення, налаштування та ліцензування.
13. `12_video_tutorials.md` - бібліотека YouTube-уроків з прев'ю, вбудованими плеєрами та пов'язаними інструкціями.
14. `13_h743_dronecan.md` - guide для WeAct H743 DroneCAN: wiring, HD-15 D-sub box pinout, flashing, FC setup, display, validation.
15. `CHANGELOG.md` - повна історія версій прошивки та примітки до релізів.
