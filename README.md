# brass-orchestration

Скилл (agent skill) для оркестровки и аранжировки медных духовых: создание партитур,
проверка диапазонов, воусинга, дыхания и выносливости валидатором, правка готовых
MusicXML/.mscx, генерация партий, рендер через MuseScore 4.

Формат — [agent skill](https://agentskills.io): точка входа [`SKILL.md`](SKILL.md),
подробные инструкции в `references/`, инструменты в `scripts/`.

## Структура

```
SKILL.md                 — точка входа: окружение, инструменты, workflow A–D
scripts/
  validate_brass.py      — механическая проверка MusicXML: диапазоны, выносливость,
                           дыхание, разрывы фактуры, параллелизмы, транспозиция ключей
  voice_quintet.py       — генератор воусинга квинтета (beam search по правилам валидатора)
  make_parts.py          — партии из партитуры (файл на партию, опционально PDF)
  split_part.py          — одна партия в отдельный файл для быстрого рендера
  compare_scores.py      — сверка аранжировки с исходником (метрики)
  check_delivery.py      — приёмка пакета: пересчёт нот, парность партий, lineage-диф
  imslp_fetch.py         — скачивание public domain с IMSLP в обход JS-заглушки
references/
  brief.md               — рабочий свод: диапазоны, транспозиции, воусинг, выносливость
  sources.md             — путеводитель по источникам (учебники, проверенные ссылки)
  REPERTOIRE.md          — локальный эталонный корпус (59 PDF, public domain)
  source-comparison.md   — как интерпретировать метрики compare_scores.py
  delivery-and-sources.md— сборка пакета «пришли аранжировку и исходники»
  master-surgery.md      — точечная правка готового мастера MusicXML
  mscx-add-part.md       — добавление инструмента в .mscx (MuseScore 4)
```

## Требования

- Python 3.12 + `lxml` (скрипты — чистый Python, lxml/stdlib)
- MuseScore 4 — для рендера PDF/PNG/MIDI через CLI

## Быстрый старт

```bash
# валидация партитуры (rc=1 при жёстких ошибках)
python scripts/validate_brass.py score.musicxml --level pro --json

# воусинг квинтета на аккордовой последовательности
python scripts/voice_quintet.py --prog 'Bb,Eb,F,Bb' --bars 2 --rests 3,6 --out score.musicxml

# распартия и рендер
python scripts/make_parts.py score.musicxml --out parts --pdf
```

Главное правило скилла: партитура сдаётся только после прогона `validate_brass.py` —
сборка без отчёта валидатора считается черновиком.
