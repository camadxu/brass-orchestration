# Оркестровка для медных духовых — путеводитель по источникам

Собрано 12.11.2026. Поиск: Tavily (веб, в т.ч. кириллица) + Firecrawl (веб) + OpenAlex (научные работы) + прямая проверка ссылок.
Tavily с российского IP блокируется (`POST /search` → CloudFront `403`), поэтому запросы идут с VPS в Амстердаме (`ssh nlvps`, доступ в глобальной памяти) — напрямую, без прокси, ответ ~2 с. Локальный Tor-вариант на этой машине не работает (tor не установлен).

Все ссылки ниже, кроме YouTube-видео, проверены HTTP-запросом: `200` — открывается, `403` — живая страница, но с защитой от ботов (открывать в браузере), `архив` — Internet Archive (нужна бесплатная регистрация для выдачи книги).

---

## 0. Если читать только пять вещей

| № | Что | Зачем именно по меди |
|---|-----|----------------------|
| 1 | **Чулаки М. «Инструменты симфонического оркестра»** ([PDF](http://www.choirbgam.by/wp-content/uploads/2011/03/%D0%A7%D1%83%D0%BB%D0%B0%D0%BA%D0%B8-%D0%9C.-%D0%98%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D1%8B-%D1%81%D0%B8%D0%BC%D1%84%D0%BE%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B3%D0%BE-%D0%BE%D1%80%D0%BA%D0%B5%D1%81%D1%82%D1%80%D0%B0.pdf)) | 177 с., коротко и по делу: устройство, диапазоны, приёмы, силовые и тембровые соотношения — ровно то, на чём спотыкаются начинающие оркестраторы |
| 2 | **Рогаль-Левицкий Д. «Современный оркестр», т. 2 «Медные духовые и ударные»** ([PDF, 45 МБ](https://notes.tarakanov.net/katalog/kompozitsii/sovremennii-orkestr/)) | Самый подробный русский справочник по меди: каждый инструмент, регистры, штрихи, сурдины, комбинации |
| 3 | **TOR, «Extreme Orchestration: Brass»** — Don Freund, открытый онлайн-учебник ([введение](https://timbreandorchestration.org/isfee/extreme-orchestration/brass/introduction), [scoring](https://timbreandorchestration.org/isfee/extreme-orchestration/brass/scoring)) | Бесплатно, современно: логика вентилей, частиалы, сурдины двух категорий, глиссандо, разбор `Till Eulenspiegel` |
| 4 | **Adler S. «The Study of Orchestration»** ([изд. Norton](https://wwnorton.com/books/9780393920659)) | ~200 страниц только о меди (гл. 9–11 в 2-м изд.) — эталонный англоязычный курс с аудиопримерами |
| 5 | **Партитуры**: Wagner, R. Strauss, Mahler, Ravel, Stravinsky ([IMSLP](https://imslp.org/)) | Без разбора партитур учебники не работают. Конкретные фрагменты — раздел 7 |

---

## 1. Русскоязычные учебники и пособия

### 1.1. Базовый курс оркестровки / инструментоведения

| Автор, название | Выходные данные | Что даёт по медным | Ссылка |
|---|---|---|---|
| Чулаки М. **Инструменты симфонического оркестра** | учеб. пособие, 177 с. | Диапазоны, регистры, приёмы, баланс групп; отдельные главы о валторне, трубе, тромбоне, тубе | [PDF](http://www.choirbgam.by/wp-content/uploads/2011/03/%D0%A7%D1%83%D0%BB%D0%B0%D0%BA%D0%B8-%D0%9C.-%D0%98%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D1%8B-%D1%81%D0%B8%D0%BC%D1%84%D0%BE%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B3%D0%BE-%D0%BE%D1%80%D0%BA%D0%B5%D1%81%D1%82%D1%80%D0%B0.pdf), [djvu](https://www.klex.ru/3xl) |
| Кожухарь В. И. **Инструментоведение. Симфонический и духовой оркестры** | СПб.: Лань; Планета музыки, 2009, 320 с. | Вузовский учебник: симфонический **и** духовой оркестр, группа медных в обоих составах | [PDF](https://xn--80adfdgmbkefasr2cbaeanr.xn--p1ai/storage/uploads/dokumenty/kozhuhar-v-instrumentovedenie.pdf) |
| Блюм Д. **Краткий курс инструментоведения** | ~686 КБ PDF | Конспект: акустика, история оркестра, группы; быстрый вход в тему | [PDF](https://noty-bratstvo.org/sites/default/files/%D0%9A%D1%80%D0%B0%D1%82%D0%BA%D0%B8%D0%B8%CC%86%20%D0%BA%D1%83%D1%80%D1%81%20%D0%B8%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%BE%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D1%8F-%D0%91%D0%BB%D1%8E%D0%BC.pdf) |
| Римский-Корсаков Н. А. **Основы оркестровки** (под ред. М. Штейнберга, 2 т.) | М.: Музыка, 1982 | Первоисточник русской школы: группы, удвоения, аккорды, комбинации тембров; с партитурными образцами | [т. 1, PDF](https://www.klex.ru/1yr5), [гл. IV на MusicaNeo](https://library.musicaneo.com/ru/sheetmusic/sm-53071_osnovy_orkestrovki_glava_iv.html), [демо-фрагмент PDF](https://azon.market/image/catalog/v_1/products351/3501056/demo.pdf) |
| Зряковский Н. **Общий курс инструментовки** | — | Классический вузовский курс; есть в тематических подборках | [подборка PDF (VK)](https://vk.ru/wall-99339872_1502) |
| Рогаль-Левицкий Д. **Современный оркестр**, 4 т. | М., 1953–1956 | **Т. 2 — медные духовые и ударные.** Максимальная детализация | [все тома, PDF](https://notes.tarakanov.net/katalog/kompozitsii/sovremennii-orkestr/), [описание томов](http://nlib.org.ua/en/pdf/books/7672) |
| Веприк А. **Очерки по вопросам оркестровых стилей** | 2-е изд., М.: Сов. композитор, 1978, 430 с. | Не «как писать ноты», а **как думали оркестраторы**: стилистика групп, история приёмов | [PDF/djvu](https://www.klex.ru/1yqg) |
| Банщиков Г. **Законы функциональной инструментовки** | СПб.: Композитор, 1999, 240 с. | Функции групп и фактурные слои — полезно, чтобы медь не дублировала всех подряд | [PDF/djvu](https://www.klex.ru/1yq8) |
| Геварт Ф. О. **Методический курс оркестровки** | пер. с фр., учеб. пособие | Классический трактат (Gevaert, 19 в.): натуральные валторны и трубы, тромбоны, распределение аккордов; важен как источник «до-вентильной» логики, которая потом перешла в учебники | [PDF](https://e-univers.ru/upload/iblock/bf4/mzxan2vtegvvkgrbltqto319hcd0v9dw.pdf) |
| Фортунатов Ю., Барсова И. **Практическое руководство по чтению симфонических партитур**, вып. 1 | М.: Музыка, 1966, 225 с. | Тренировка чтения партитуры с транспонирующими медными (валторна in F, труба in B) | [PDF](https://www.klex.ru/1yrj) |

### 1.2. Инструментовка для духового оркестра (если нужен не симфонический состав)

| Автор | Что внутри | Ссылка |
|---|---|---|
| Анисимов Б. **Практическое пособие по инструментовке для духового оркестра** | Переиздание работы 1960 г.; состав духового оркестра, медная группа, переложения | [PDF, iodnt.ru](https://iodnt.ru/images/%D0%9F%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%BE%D0%B5%20%D0%BF%D0%BE%D1%81%D0%BE%D0%B1%D0%B8%D0%B5%20%D0%BF%D0%BE%20%D0%B8%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%BE%D0%B2%D0%BA%D0%B5%20%D0%B4%D0%BB%D1%8F%20%D0%B4%D1%83%D1%85%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20%D0%BE%D1%80%D0%BA%D0%B5%D1%81%D1%82%D1%80%D0%B0.pdf), [зеркало](https://noty-bratstvo.org/sites/default/files/%D0%98%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BC%D0%B5%D0%BD%D1%82%D0%BE%D0%B2%D0%BA%D0%B0%20%D0%B4%D0%BB%D1%8F%20%D0%B4%D1%83%D1%85%D0%BE%D0%B2%D0%BE%D0%B3%D0%BE%20-%D0%90%D0%BD%D0%B8%D1%81%D0%B8%D0%BC%D0%BE%D0%B2.pdf) |
| **Хрестоматия по инструментовке для духового оркестра** (Прокофьев-колледж) | Фортепианные примеры для практики инструментовки | [PDF](https://prokofievcollege.ru/upload/iblock/f04/f049d122397b4b0b01cb375fd326ef75.pdf) |
| **Как организовать самодеятельный духовой оркестр** | Практика: составы, распределение партий, репертуар — полезно, если цель не академическая партитура, а рабочий бэнд | [PDF](http://noty-bratstvo.org/sites/default/files/duh-kak-organizovatj-samodeyateljnyy-duhovoy-orkestr.pdf) |

### 1.3. Акустика и исполнительская техника (чтобы понимать пределы)

| Источник | Зачем | Ссылка |
|---|---|---|
| Алдошина И., Приттс Р. **Музыкальная акустика** | Глава об акустике духовых: мундштук, раструб, спектр, атака | [djvu/pdf](https://www.klex.ru/mgh) |
| Диков Б. **Методика обучения игре на духовых инструментах** | Что реально может духовик: дыхание, атака, выносливость, усталость губ | [подборка (VK)](https://vk.ru/wall-99339872_1328) |

> Примечание: на e.lanbook.com многие учебники (Кожухарь, Толмачёв/Дубок, Леонов/Палкина) легально доступны по подписке вуза — если есть доступ, это лучший вариант с полными текстами.

---

## 2. Англоязычные учебники (что читать именно про медь)

| Книга | Издание / доступ | Медные разделы |
|---|---|---|
| **Adler, The Study of Orchestration** | Norton, 4-е изд. 2016; [страница книги](https://wwnorton.com/books/9780393920659) (403 для curl, в браузере ок) | Гл. о меди ~9–11 (в 2-м изд. — 200+ страниц): состав группы, письменный диапазон vs реальный, сурдины, баланс, примеры из репертуара + аудио |
| **Kennan K., Grantham D., The Technique of Orchestration** | 6-е изд., Pearson; 7-е изд. — Routledge/Taylor & Francis | 6-е изд.: гл. 10 «The Brass Section» (~с. 162); 7-е изд.: гл. 9. Плюс гл. «Scoring Chords…» — аккорды в меди |
| **Forsyth C., Orchestration** | 1914, свободно | [PDF, IMSLP](http://conquest.imslp.info/files/imglnks/usimg/9/90/IMSLP107662-PMLP219239-Forsyth-Orchestration1914.pdf); гл. о духовых — история, устройство, замечания практика |
| **Blatter A., Instrumentation and Orchestration** | 2-е изд., 508 с.; [архив](https://archive.org/details/instrumentationo0000blat_u5w6) | Полный обзор каждого инструмента + отдельный раздел о записи для духового оркестра |
| **Berlioz H., Strauss R., Treatise on Instrumentation** | [PDF, IMSLP](http://imslp.info/files/imglnks/usimg/3/30/IMSLP11615-Treatise_on_InstrumentationBerlioz.pdf), [оригинал](https://imslp.org/wiki/Grand_trait%C3%A9_d%27instrumentation_et_d%27orchestration_modernes%2C_Op.10_(Berlioz%2C_Hector)) | Историческая база: натуральные валторны/трубы, сурдины, «характер» инструментов; комментарии Штрауса — уже про современную медь |
| **Rimsky-Korsakov N., Principles of Orchestration** | [IMSLP](https://imslp.org/wiki/Principles_of_Orchestration_(Rimsky-Korsakov,_Nikolay)) | Английская версия «Основ»; удобна для цитирования и параллельного чтения |
| **Del Mar N., Anatomy of the Orchestra** | 1981/1983; [архив](https://archive.org/details/anatomyoforchest0000delm), [оглавление UC Press](https://www.ucpress.edu/book/9780520050624/anatomy-of-the-orchestra) | Гл. III «Horns», гл. IV «The Heavy Brass» — самые въедливые практические замечания (баланс, усталость, сурдины, реальные пределы) |
| **Baines A., Brass Instruments: Their History and Development** | Dover; [архив](https://archive.org/details/brassinstruments0000bain_e6n6) | История и конструкция: почему валторна звучит иначе трубы, эволюция вентилей, сурдин |
| **Newton B., Band Orchestration, vol. 3: Brass** | платный ebook; [оглавление и описание](https://www.bretnewtoncomposer.com/product-page/ebook-band-orchestration-volume-3-brass-1) | Духовой оркестр: натуральная медь, валторны и horn section, Wagner tuben, корнеты и семейство корнетов; логика состава бэнда, а не симфонического оркестра |
| **Miller M., Contemporary Orchestration** | Routledge, 2014; [изд-во](https://www.routledge.com/Contemporary-Orchestration/Miller/p/book/9780415808408) | Современный взгляд, включая кино/медиа-оркестровку: медь в гибридных составах, плотность, слои, работа с семплами vs живой группой |
| **Wagner J., Orchestration: A Practical Handbook** | 1959, свободно | [PDF, archive.org](https://archive.org/details/orchestrationpra00wagn) | Практичный американский учебник середины века: медь по инструментам, готовые схемы аккордов, много нотных примеров |

---

## 3. Онлайн-справочники: диапазоны, сурдины, приёмы

| Ресурс | Что там | Ссылка |
|---|---|---|
| **TOR / ISFEE, Extreme Orchestration — Brass** (Don Freund) | Открытый учебник: Brass Basics (логика вентилей 1-2-3, частиалы, тесситуры), Pitch Inflection (вибрато, тремоло, shake, 3 типа глиссандо), **Mutes Category A и B**, дыхание и артикуляция; раздел scoring с разбором `Till Eulenspiegel` | [введение](https://timbreandorchestration.org/isfee/extreme-orchestration/brass/introduction) · [scoring](https://timbreandorchestration.org/isfee/extreme-orchestration/brass/scoring) · [категория Brass](https://timbreandorchestration.org/isfee/extreme-orchestration/category/Brass) |
| **Orchestration (свободный курс, Google Sites)** — раздел Brass | Последовательный бесплатный курс: Brass section, **Mutes**, отдельные инструменты, «медь как самостоятельная группа», большие составы. Ключевая мысль: медь гетерогенна, валторны и тромбоны перекрываются по диапазону — отсюда неизбежные дубли внутри; полезно упражнение «написать хорал для меди» | [brass as independent section](https://www.orchestrationresources.com/brass/brass-as-an-independent-section) · [mutes](https://www.orchestrationresources.com/brass/mutes) · [brass in the large ensembles](https://www.orchestrationresources.com/brass/brass-in-the-large-ensembles) |
| **Beat Kitchen — Writing for Brass** | Короткий гайд: 4 валторны парами (I/II, III/IV), валторна как «хамелеон» между группами, конический раструб против цилиндрической трубы | [гайд](https://beatkitchen.io/guides/orchestral/08-writing-for-brass) |
| **Hugill A., The Orchestra: A User's Manual** | Мультимедийный справочник: по инструментам (horns, trumpets, trombones, tubas) и по группам; диапазоны/транспозиции, натуральный звукоряд, таблицы нотации, видео музыкантов Philharmonia | [andrewhugill.com/OrchestraManual](https://andrewhugill.com/OrchestraManual/) (403 для curl — открывать в браузере) |
| **Composition Teaching — Instrument Ranges & Transposition** | Сводная таблица: written vs sounding диапазон, транспозиция для каждого инструмента, включая редкие (бас-труба, Wagner tuba) | [страница](https://compositionteaching.com/instrument-ranges) |
| **Orchestral ranges & transposition (mzm.dk, PDF)** | Компактная PDF-шпаргалка по диапазонам и транспозициям — распечатать и держать рядом | [PDF](https://www.mzm.dk/dkdm_info/instrumenter_omfattende_oversigt.pdf) · [Octatone](https://octatone.com/orchestral-ranges-transposition) · [Orchestra Library](https://www.orchestralibrary.com/reftables/rang.html) |
| **Motifkit — Brass Spacing and Voicing** | Как расположить аккорд в меди, чтобы он «звучал»: интервалы между голосами, нижний голос, удвоения | [статья](https://motifkit.com/brass-spacing-voicing) |
| **Soundtrack Academy — Brass Instruments** | Бесплатный обзор меди для композиторов медиа: диапазоны, артикуляции, типичные комбинации | [курс-раздел](https://soundtrack.academy/brass-instruments) |
| **Seraphinoff R. — History of the natural horn** | Как устроена натуральная валторна и что из этого следует для письма (частиалы, hand-stopping) | [статья](https://www.seraphinoff.com/history) |
| **OrchestrationOnline — stopped horn** | Практический диапазон закрытых нот: лучше всего внутри скрипичного стана; выше верхнего G — риск «кикса» | [статья](https://orchestrationonline.com/horns-practical-range-of-stopped-notes/) |
| **OrchestrationOnline — Horns: stopping vs mutes** | Чёткое различие: закрытая рука меняет и высоту, и тембр; сурдина — только тембр | [статья](https://orchestrationonline.com/horns-differences-between-stopping-and-mutes) |
| **OrchestrationOnline — Horn Section Teamwork** | Как четыре валторны делят функцию: мелодия, гармония, бас, «клей»; типичные ошибки распределения | [статья](https://orchestrationonline.com/horn-section-teamwork) |
| **Houghton Horns — Stopped horn** | Разница между *muted* и *stopped*; как это делается физически | [статья](https://houghtonhorns.com/pages/stopped-horn) |
| **Tonebase — Trumpet mutes** | Straight, cup, Harmon, bucket, plunger: звук и применение | [статья](https://brass.tonebase.co/blog/complete-guide-to-playing-mutes-on-a-trumpet) |
| **Wikipedia — Mute (music)** | Сводная таблица сурдин по инструментам | [статья](https://en.wikipedia.org/wiki/Mute_(music)) |
| **Partita.ru — медные духовые** | Русский справочник: состав группы, строи, показатели транспонирования, диапазоны; удобно как быстрый контрольный список | [страница](https://www.partita.ru/instruments/brass.shtml) |
| **James Boldin — Stopped Horn Excerpts** | Оркестровые примеры stopped horn с разбором: где `+` реально нужен, а где композитор перестраховался | [часть 1](https://jamesboldin.com/2011/07/13/stopped-horn-excerpts-part-1) |
| **Dorico forum — brass mutes notation (best practice)** | Как нотировать сурдины: `con sord.` по умолчанию = straight, тип в скобках `con sord. (cup)`, когда писать `senza sord.` | [ветка](https://forums.steinberg.net/t/best-practice-brass-mutes-notation/722582) |
| **Evan Rogers — Big Band Arranging: Mutes** | Сурдины в биг-бэнде: как меняют диапазон и сопротивление, практические ограничения | [статья](https://www.evanrogersmusic.com/blog-contents/big-band-arranging-mutes) |
| **The Idiomatic Orchestra — Dynamics and Balance** | Как удвоение меняет громкость и плотность; почему «два в унисон» ≠ «вдвое громче» | [статья](https://theidiomaticorchestra.net/dynamics-and-balance/) |
| **Evenant — Effective Ways To Orchestrate Brass** | Практическая статья: медь в гармонической фактуре, распределение нот по инструментам | [статья](https://www.evenant.com/articles/effective-ways-to-orchestrate-brass) |
| **Young Composers — Orchestration, Part 2: Brass** | Мастер-класс: валторна как альтовый инструмент, расположение в медном хоре | [мастер-класс](https://www.youngcomposers.com/t11705/orchestration-part-2-brass/) |
| **Sanchez M. — Arranging for Brass** | PDF, базовые правила 4-голосной записи для медного ансамбля | [PDF](https://michaelsanchezmusic.org/wp-content/uploads/2016/07/arranging-for-brass.pdf) |
| **OrchestrationOnline (Thomas Goss)** | 100 Orchestration Tips, 100 MORE Tips, YouTube-курсы, каталог преподавателей | [сайт](https://orchestrationonline.com/) · [100 Tips](https://orchestrationonline.com/product/100-orchestration-tips-2nd-edition/) · [YouTube-курсы](https://orchestrationonline.com/training/youtube-courses/) |

---

## 4. Научные статьи: акустика, техника, восприятие меди

| Работа | Год | Ссылка |
|---|---|---|
| Chon S. H., Huron D., DeVlieger D. **An Exploratory Study of Western Orchestration: Patterns through History** — эмпирика оркестровых решений, в т.ч. медь | 2018 | [DOI](https://doi.org/10.18061/emr.v12i3-4.5773) |
| **Can Orchestration Teaching be improved?** — Вестник СПбГУ, Искусствоведение | 2023 | [DOI](https://doi.org/10.21638/spbu15.2023.401) |
| Pyle R. W. **Pitch Change of the Stopped French Horn** — JASA | 1964 | [DOI](https://doi.org/10.1121/1.2143243) |
| Pyle R. W. **A Computational Model of the Baroque Trumpet and Mute** — Historic Brass Society Journal | 1991 | [DOI](https://doi.org/10.2153/01199100110010) |
| Pyle R. W. **Does a brass instrument's timbre depend on the alloy?** — JASA | 2009 | [DOI](https://doi.org/10.1121/1.4783883) |
| Lembke S.-A. **Timbre blending of wind instruments: acoustics and perception** | 2012 | [OpenAlex](https://api.openalex.org/works?search=Timbre%20blending%20of%20wind%20instruments) |
| Tournemenne R. et al. **Sound simulation-based design optimization of brass wind instruments** — JASA | 2019 | [DOI](https://doi.org/10.1121/1.5111346) |
| Minenko A. **The evolution of the mutes for brass instruments (from Ancient Egypt to present)** | 2022 | [DOI](https://doi.org/10.34064/khnum2-27.08) |
| Armstrong Z. **The Acoustics of Harmon Mutes** | 2016 | [OpenAlex](https://api.openalex.org/works?search=Acoustics%20of%20Harmon%20Mutes) |
| van Dijk N. **Brass Multiphonics in Jazz** | 2009 | [DOI](https://doi.org/10.26686/wgtn.16999489) |
| LoPresto M. **Experimenting with brass musical instruments** — Physics Education | 2003 | [DOI](https://doi.org/10.1088/0031-9120/38/4/302) |

### Русскоязычные статьи (КиберЛенинка, открытый доступ)

| Статья | Год | Ссылка |
|---|---|---|
| Меновщиков Д. М. **Медные духовые инструменты в оркестре Рихарда Вагнера** | 2024 | [cyberleninka](https://cyberleninka.ru/article/n/mednye-duhovye-instrumenty-v-orkestre-riharda-vagnera) |
| Вэйцзя С. **Труба и её разновидности в оркестре Рихарда Вагнера** | 2025 | [cyberleninka](https://cyberleninka.ru/article/n/truba-i-ee-raznovidnosti-v-orkestre-riharda-vagnera) |
| Линь Я. **Опыт создания ансамблево-оркестровой подготовки оркестра медных духовых инструментов** | 2020 | [cyberleninka](https://cyberleninka.ru/article/n/opyt-sozdaniya-i-ansamblevo-orkestrovoy-podgotovki-orkestra-mednyh-duhovyh-instrumentov-uchaschihsya-sredney-shkoly-goroda-chuntsin) |
| Минцзе Л. **Современное состояние обучения игре на медных духовых инструментах в российских музыкальных вузах** | 2025 | [cyberleninka](https://cyberleninka.ru/article/n/sovremennoe-sostoyanie-obucheniya-igre-na-mednyh-duhovyh-instrumentah-v-rossiyskih-muzykalnyh-vuzah) |
| **Ретроспектива подходов к использованию духовых музыкальных инструментов** | — | [cyberleninka](https://cyberleninka.ru/article/n/retrospektiva-podhodov-k-ispolzovaniyu-duhovyh-muzykalnyh-instrumentov) |
| Ерёмин Н. С. **Оркестры духовых музыкальных инструментов в истории России** | 2016 | [cyberleninka](https://cyberleninka.ru/article/n/orkestry-duhovyh-muzykalnyh-instrumentov-v-istorii-rossii) |
| **Характерные особенности оркестрового письма в современной отечественной духовой музыке** | — | [cyberleninka](https://cyberleninka.ru/article/n/harakternye-osobennosti-orkestrovogo-pisma-v-sovremennoy-otechestvennoy-duhovoy-muzyke) |
| **Особенности бытования медных духовых инструментов** (Тюменский ГИК) | — | [esrae.ru](https://timekguki.esrae.ru/ru/40-r420) |
| Прасолова К. **Лекция по инструментоведению** (Гнесинка, методичка) | — | [gnesin.ru](https://www.gnesin.ru/mediateka/metodicheskie_materialy/metodicheskie_posobiya/prasolova_lekziya) |

### Диссертации (полные тексты в открытых репозиториях)

| Работа | Год | Репозиторий |
|---|---|---|
| Hasty P. **Aaron Copland's symphonic use of brass instruments** | 1965 | [OpenAlex](https://api.openalex.org/works?search=Copland%20symphonic%20use%20of%20brass) |
| Ritter D. **The Brass Instruments as Used by Brahms in His Four Symphonies** | 1964 | [OpenAlex](https://api.openalex.org/works?search=Brass%20Instruments%20as%20Used%20by%20Brahms) |
| Moore D. **A History of the Music and Composers for the Brass Ensemble Medium Before the Nineteenth Century** | 1950 | [OpenAlex](https://api.openalex.org/works?search=History%20of%20the%20Music%20and%20Composers%20for%20the%20Brass%20Ensemble) |
| Dillon R. **Five original teaching pieces in contemporary styles for brass instruments** | 1971 | [OpenAlex](https://api.openalex.org/works?search=Five%20original%20teaching%20pieces%20contemporary%20styles%20brass) |
| Stafford J. **Compositional Devices Employed in Scoring for Voice and Brass** | 1970 | [LSU](https://repository.lsu.edu/gradschool_disstheses/1889) |
| Cannon A. **Defining characteristics of the brass music of …** (техника письма для трубы глазами композитора) | 2012 | [PDF, UBC](https://anthonyplog.com/documents/Thesis/ubc_2012_fall_cannon_alexander.pdf) |
| **IHS Thesis Lending Library** — каталог диссертаций по валторне | — | [hornsociety.org](https://www.hornsociety.org/about-the-ihs/thesis-library) |
| **The Treatment of Brass Instruments in the Symphonies of Gustav Mahler** — как именно Малер пишет для меди (диссертация, Rochester) | — | [urresearch.rochester.edu](https://urresearch.rochester.edu/institutionalPublicationPublicView.action?institutionalItemId=38005) |
| **The Evolution of the Orchestral Brass Section from Bach to Beethoven to Berlioz** — история группы и её функций, Miami | — | [scholarship.miami.edu](https://scholarship.miami.edu/esploro/outputs/doctoral/The-Evolution-of-the-Orchestral-Brass/991031455984102976) |
| **Ricardo Matosinhos — список диссертаций по валторне** (сводный, с ResearchGate-ссылками) | — | [список](https://www.ricardomatosinhos.com/index.php/en/horn-stuff/thesis-dissertations) |

> Поиск по научным работам дальше: [OpenAlex](https://api.openalex.org/works?search=brass%20orchestration), [Crossref](https://search.crossref.org/), [КиберЛенинка](https://cyberleninka.ru/search?q=оркестровка%20медных), [eLibrary](https://elibrary.ru/).

---

## 5. Видео (по результатам поиска; YouTube блокирует автоматическую проверку ссылок)

| Видео | Ссылка |
|---|---|
| Thomas Goss — **Orchestration Tip: Brass Section Dynamic Balance** (почему валторны не обязаны всегда дублировать «тяжёлую» медь) | [YouTube](https://www.youtube.com/watch?v=8UEp2VcraM4) |
| **Orchestration 101: Writing for Brass** — базовые стратегии для медной группы | [YouTube](https://www.youtube.com/watch?v=xFEEYzL0lQQ) |
| **How To Compose For Trumpet Mutes** (straight / Harmon / cup) | [YouTube](https://www.youtube.com/watch?v=5tdCcPma41M) |
| **Orchestrating a Brass Melody** — как выбрать инструмент под мелодию | [YouTube](https://www.youtube.com/watch?v=Nby9vB6gtww) |
| Alex Lamy — **The fellowship of the BRASS: ranges, registers and arranging** | [YouTube](https://www.youtube.com/watch?v=0-I-STlLHv8) |
| **Orchestration Book Club: Adler's The Study of Orchestration** — обзор 4-го изд. | [YouTube](https://www.youtube.com/watch?v=V1c27cwdQe8) |
| **Валторна, труба, тромбон, туба: лекция об инструментах симфонического оркестра** (по-русски, про строй, транспозицию и различия) | [YouTube](https://www.youtube.com/watch?v=8yoGpTB-rj0) |
| **Тромбоны, трубы, тубы, валторны. Как свести медь в оркестровке** (рус., прикладной разбор баланса и обработки) | [YouTube](https://www.youtube.com/watch?v=bxKtJTk1yu8) |
| Курсы Thomas Goss на YouTube (каталог) | [orchestrationonline.com](https://orchestrationonline.com/training/youtube-courses/) |

---

## 6. Партитуры для анализа

Скачивать: [IMSLP](https://imslp.org/) (public domain, нужна бесплатная регистрация).

### Что смотреть именно в меди

| Произведение | На что смотреть |
|---|---|
| **Wagner, «Тангейзер» (увертюра), «Тристан», «Кольцо»** | Медный хор как драматургия: 4 валторны + 3 трубы + 3 тромбона + туба; хоралы, «тяжёлая» медь, баланс с деревянными. См. также [статью Меновщикова](https://cyberleninka.ru/article/n/mednye-duhovye-instrumenty-v-orkestre-riharda-vagnera) |
| **R. Strauss, «Till Eulenspiegel»** | Эталон оркестрового остроумия: валторны в унисонах, закрытые ноты, быстрые смены сурдин, соло трубы. Разбор — в [TOR scoring](https://timbreandorchestration.org/isfee/extreme-orchestration/brass/scoring) |
| **Mahler, симфонии 5–7** | Медные tutti, «высокая» труба, валторновые соло, работа с сурдинами |
| **Bruckner, симфонии 7–8** | Хоральная медь, регистровка аккордов, длинное дыхание |
| **Ravel, «Картинки с выставки» (орк. Мусоргского)** | Экономия средств: медь как краска, а не как мощность |
| **Stravinsky, «Весна священная»** | Ритмическая функция меди, экстремальные регистры, артикуляция |
| **Janáček, «Синфониетта»** | 12 труб (в т.ч. фанфарные), медь как самостоятельный слой |
| **Respighi, «Пинии Рима»** | Медные фанфары, пространственное размещение, буцины |
| **Shostakovich, симфонии 5, 8** | Соло трубы, тромбона, тубы; драматургия меди в кульминациях |
| **Copland, «Fanfare for the Common Man»** | Чистый медный хор: 4 валторны, 3 трубы, 3 тромбона, туба — учебник по балансу |
| **Britten, «Serenade for Tenor, Horn and Strings»** | Натуральные частиалы валторны, письмо для солиста |

Категории IMSLP: [Wagner](https://imslp.org/wiki/Category:Wagner,_Richard) · [R. Strauss](https://imslp.org/wiki/Category:Strauss,_Richard) · [Mahler](https://imslp.org/wiki/Category:Mahler,_Gustav) · [Ravel](https://imslp.org/wiki/Category:Ravel,_Maurice) · [Stravinsky](https://imslp.org/wiki/Category:Stravinsky,_Igor) · [Janáček](https://imslp.org/wiki/Category:Jan%C3%A1%C4%8Dek,_Leo%C5%A1) · [Respighi](https://imslp.org/wiki/Category:Respighi,_Ottorino)

---

## 7. Порядок работы на 6 недель

| Неделя | Задача | Материал |
|---|---|---|
| 1 | Понять инструменты | Чулаки (полностью) + TOR Brass introduction |
| 2 | Регистры и пределы | Рогаль-Левицкий, т. 2 (по инструментам) + Hugill (ranges/transpositions) |
| 3 | Сурдины и приёмы | TOR Mutes A/B + Houghton Horns + Tonebase mutes; выписать таблицу «сурдина → эффект → время смены» |
| 4 | Аккорды и баланс в меди | Kennan гл. 10/9 + The Idiomatic Orchestra (balance) + Adler гл. о меди |
| 5 | Анализ партитур | 3–4 фрагмента из раздела 6, переписать медные аккорды в клавир |
| 6 | Практика | Своя пьеса/отрывок: 4 валторны, 3 трубы, 3 тромбона, туба; проверка по чек-листу ниже |

---

## 8. Чек-лист перед сдачей партитуры (медная группа)

- [ ] **Диапазоны**: written vs sounding; валторна in F (звучит квинтой ниже), труба in B (большой секундой ниже), теноровый тромбон — non-transposing, туба — non-transposing.
- [ ] **Тесситура**: не держать 1-ю трубу/валторну на пределе дольше 2–3 тактов; валторна выше C6 — только эпизодически.
- [ ] **Дыхание**: фразы не длиннее 4–6 тактов в `f`; в `pp` на низких нотах расход воздуха больше.
- [ ] **Выносливость**: не давать меди непрерывный `ff` дольше ~30–40 секунд без паузы.
- [ ] **Сурдины**: минимум 10 секунд на смену (по TOR); не менять сурдину посреди быстрой фразы; помечать, какая именно сурдина.
- [ ] **Закрытые ноты валторны**: `+` на каждой ноте или `+` с продолжением линии; помнить о транспозиции на полтона вниз у stopped horn; держать внутри скрипичного стана.
- [ ] **Дублирования**: осознанно — унисон даёт громкость, октава — плотность; не дублировать 1-ю трубу 1-й валторной в высоком регистре.
- [ ] **Баланс**: 3 тромбона + туба легко перекрывают 4 валторны; валторны — «клей» между деревом и тяжёлой медью.
- [ ] **Нотация**: валторны выше труб в партитуре; транспонирующие партии — в правильной тональности; тромбон — басовый/теноровый ключи (не скрипичный без нужды).
- [ ] **Артикуляция**: обозначить, где нужен *sforzando*, где *marcato*, где legato; двойное/тройное staccato — только в умеренном темпе.
- [ ] **Проверка на рояле**: сыграть все медные партии в реальном звучании (транспонировав), а не как написано.

---

## 9. Где искать дальше

- **КиберЛенинка**: `site:cyberleninka.ru оркестровка медных`, `инструментовка духовых`
- **eLibrary.ru**: `оркестровка`, `медные духовые`, фильтр «статьи»
- **OpenAlex API**: `https://api.openalex.org/works?search=brass+orchestration`
- **IMSLP**: партитуры public domain
- **Internet Archive**: старые учебники (Blatter, Del Mar, Baines) — бесплатная регистрация
- **e.lanbook.com**: вузовские учебники по подписке (Кожухарь, Толмачёв/Дубок, Леонов/Палкина)
- **Tavily**: кириллицу ищет заметно лучше Firecrawl (нашёл прямые PDF Кожухаря, Блюма, Анисимова, Геварта). С российского IP `api.tavily.com` отвечает `403` — запускать с VPS (`ssh nlvps '/root/tv.sh'`) или локально через Tor (`bash scripts/tavily.sh "запрос" префикс`).

---

*Служебное: сырые результаты поиска (`data/*.json`, запросы en1–13, ru1–16, tv*, sch*) остались в исходной рабочей папке `brass/` вне этого скилла. Повторный поиск: Tavily — только с VPS (`ssh nlvps`), научные работы — OpenAlex API (`curl https://api.openalex.org/works?search=...`), прямая проверка ссылок — HTTP-запросы с оценкой статуса (200/403/архив).*
