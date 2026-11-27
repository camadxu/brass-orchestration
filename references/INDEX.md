# Навигатор по brass-orchestration

Начни здесь, если не знаешь, какой справочник открыть. Для книг и нотных примеров сначала проверь локальную библиотеку; в сеть иди только за проверенным пробелом или по прямому запросу пользователя.

## Маршрут по задаче

| Задача | Открыть | Для чего |
|---|---|---|
| Консультация, фактура, удвоения, баланс, регистр | `references/brief.md`, затем нужную книгу из библиотеки | Краткие рабочие ограничения и первоисточник. |
| Переложение симфонического фрагмента на медные | `references/brief.md` + `references/arrangement-workflow.md`; источники — через `references/library.md` | Разбор функций и распределение по голосам; состав/строй уточнить до записи нот. |
| Большой медный ансамбль проекта (4 трубы, 2–4 валторны, 6–8 тромбонов, 2–3 тубы, ударные) | `references/ensemble-profile.md` + `references/brief.md` | Целевой состав и перечень обязательных уточнений; это не готовая раскладка и не таблица диапазонов. |
| Поиск темы в книгах | `references/library.md` и `scripts/library_lookup.py` | Local-first, OCR-поиск с PDF-страницами и обязательной визуальной сверкой нот/таблиц. |
| Исполнительская проверка трубы, валторны, тромбона, тубы или ударных | `books/online-resources/knowledge/README.md` → нужный конспект; быстрый поиск — `books/online-resources/texts/hugill-pages/_combined-clean.txt`; подробная опись — `books/online-resources/INDEX-2026-11-25.md` | Сверяй практические заметки с локальными основными книгами; не считай веб-текст нормативной таблицей диапазона. |
| Разбор brass scoring и оркестровых примеров | `books/online-resources/cards/tor-extreme-orchestration-brass.md` + `books/online-resources/knowledge/brass-practice-tor.md` | Современные главы о четырёх семействах меди и пример Strauss; текстовые захваты локальны для поиска, ноты/графика не включены. |
| Инструментальные страницы Philharmonia | `books/online-resources/cards/philharmonia-instrument-guides.md` | Проверенные страницы трубы, валторны, тромбона, тубы и ударных; обобщённые сведения, не пределы конкретных исполнителей. |
| RCM: труба, валторна, тромбон | `books/online-resources/cards/rcm-instrument-guidance.md` | Вводное руководство; PDF, поисковое извлечение и конспект локальны, графические диапазоны не проверены. |
| Современный специализированный источник по тубе | `books/online-resources/cards/composers-guide-tuba.md` + `books/online-resources/knowledge/composers-guide-tuba-notes.md` | Авторская выжимка Hynds по регистрам, дыханию и артикуляции; графики диапазонов не транскрибированы. |
| Исторические трактаты Forsyth (1914), Kling/Saenger (1905), Widor/Suddard (1906), Prout I и II (1899 impression) | `books/README.md` и карточки в `books/online-resources/cards/` | Сравнительный контекст, не современные нормы; ноты и таблицы сверять по сканам. |
| Примеры и репертуар для 6–8 тромбонов | `books/online-resources/cards/jay-friedman-trombone-choir.md` + `scores/CATALOG.md` | Каталог хоровых аранжировок, не общая методика; ноты отдельно легально получить и проверить. |
| Проверка переложения по исходной партитуре | `references/source-comparison.md` + `references/validation-and-delivery.md` | Сверка и выпуск результата; не заменяет музыкального суждения. |
| Такт не сходится, нота подписана не тем значением, висящая лига; купюра и проверка стыка | `references/rhythm-and-coupures.md` + `scripts/check_rhythm.py` | Длина такта и написанные значения — вне поля зрения `validate_brass.py`; карта купюры и доказательство стыка. |
| Малая правка MusicXML/MXL | `references/master-surgery.md` | Безопасная локальная правка, сохранение мастера. |
| Добавить партию в MSCX/MSCZ | `references/mscx-add-part.md` | Структурные правила MuseScore. |
| Импорт, гравировка, печать | `references/musescore-import-quirks.md` + `references/validation-and-delivery.md` | Импортные особенности и проверка конечных PDF/партий. |
| Репертуар/образцы | `references/REPERTOIRE.md`, затем `scores/CATALOG.md` в библиотеке | Проверить титул, реальный состав и полноту исходника. |
| Внешние источники и права | `references/sources.md`; для доставки — отдельно `references/delivery-and-sources.md` | Веб дополняет библиотеку, но не заменяет уже имеющуюся книгу; ссылка не доказывает права. |
| Запуск и тесты | `references/environment.md` | Проверенные команды для текущего хоста; на другом хосте пути перепроверить. |

## Карта локальных книг

Корень: `ORCH_LIBRARY`, иначе `~/Documents/orchestration-library`. На текущем Windows-хосте проверенный путь: `C:/Users/IAI/Documents/orchestration-library`. Авторитетные записи и названия — `books/manifest.json`; описание порядка — `books/README.md`.

| ID | Первый выбор для | OCR / указатель страниц |
|---|---|---|
| `rimsky` | Общая оркестровка, группы, медные, гармония, удвоения, tutti | `books/rimsky/rimsky.txt`, `rimsky.pages.json`; оригинал `rimsky.pdf` |
| `anisimov` | Практика духового оркестра и переложение | `books/anisimov/anisimov.txt`, `.pages.json`; оригинал `anisimov.pdf` |
| `malter` | Таблицы диапазонов, аппликатуры, партитурные схемы | `books/malter/malter.txt`, `.pages.json`; оригинал `malter.pdf` |
| `blum` | Дополнительная сверка инструментоведения | `books/blum/blum.txt`, `.pages.json`; оригинал `blum.pdf` |
| `rimsky-principles` | Дополнительные главы/версии Римского-Корсакова | `books/rimsky-principles/`; проверь язык и наличие текстового слоя каждого файла |
| `berlioz` | Дополнительный трактат | `books/berlioz/`; локальный слой может быть только OCR |
| `milyaev` | Дополнительный источник | `books/milyaev/`; сверяй скан и конспект |
| `online-resources` | Дополнительные онлайн-источники и карточки | `books/online-resources/README.md`; manifest может быть историческим, проверь фактический файл |
| Партитуры | Репертуар и образцы | `scores/CATALOG.md`, затем проверка самого файла |

## Все reference-файлы

`arrangement-workflow.md` — рабочий процесс; `brief.md` — исполнительские и нотационные ориентиры; `delivery-and-sources.md` — исторические правила доставки; `ensemble-profile.md` — проектный состав и чеклист уточнений; `environment.md` — среда и тесты; `library.md` — библиотека, OCR, страницы, права; `master-surgery.md` — точечная правка MusicXML; `mscx-add-part.md` — добавление инструмента в MuseScore; `musescore-import-quirks.md` — импорт/экспорт; `REPERTOIRE.md` — репертуар; `rhythm-and-coupures.md` — длина такта, написанные значения, лиги, купюры; `source-comparison.md` — сравнение с источником; `sources.md` — источники; `validation-and-delivery.md` — проверки и сдача.

Не используй reference-файл, которого нет в каталоге скилла. Если путь не разрешается, проверь дерево и сообщи о поломке ссылки; не угадывай.