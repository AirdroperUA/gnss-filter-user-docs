# Користувацька документація

> Де купити плату: [GPS Spoofing Filter](https://airdroper.org/products/gps-spoofing-filter)

Англійська версія: `docs/user/README.md`.

Важливо: параметри STM32-фільтра змінюються у Mission Planner:
- `Config/Tuning` -> `Full Parameter List`
- оберіть систему STM32 (`SYSID 42`)
- `Refresh Params` -> змініть значення -> `Write Params`
- на завантаженому MAVLink-лінку запис може потребувати 1-2 спроби; завжди робіть `Refresh Params` для підтвердження

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
5. `05_operation.md` - поведінка під час роботи (DR0/DR1, блокування GNSS, імпульс події).
6. `06_tuning.md` - параметри тюнінгу та робота через Mission Planner.
7. `07_cheat_sheet.md` - коротка довідка для швидких перевірок.
8. `08_lab_validation.md` - безпечна лабораторна валідація перед реальними польотами.
9. `09_receiver_config.md` - конфігурація GNSS-приймача для u-blox, UM980 та Mosaic X5 (профілі, налаштування GPS-типу ArduPilot).
10. `10_self_install.md` - самостійна установка прошивки на чисту плату BlackPill за допомогою ліцензійного ключа.
11. `11_faq.md` - часті запитання щодо роботи фільтра, апаратного забезпечення, налаштування та ліцензування.
12. `12_video_tutorials.md` - бібліотека YouTube-уроків з прев'ю, вбудованими плеєрами та пов'язаними інструкціями.
13. `CHANGELOG.md` - повна історія версій прошивки та примітки до релізів.
