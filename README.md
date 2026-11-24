# brass-orchestration

Agent skill для оркестровки меди, переложений, сверки MusicXML/MuseScore и выпуска партий. Точка входа — [SKILL.md](SKILL.md). Методика отделяет музыкальное проектирование, сверку источника, исполнительскую применимость и печатную приёмку.

**PASS анализатора не доказывает музыкальное качество или готовность партий.** Не переписывать авторскую музыку ради нулевого счётчика предупреждений.

## Руководства

- [brief.md](references/brief.md) — регистры, транспозиция, дыхание, фактура.
- [arrangement-workflow.md](references/arrangement-workflow.md) — от задания до согласованного мастера.
- [validation-and-delivery.md](references/validation-and-delivery.md) — ограничения скриптов и приёмка партий/PDF.
- [environment.md](references/environment.md) — проверенные Windows-команды и самотест.
- [library.md](references/library.md), [REPERTOIRE.md](references/REPERTOIRE.md) — работа с источниками и локальной библиотекой.

Другие справочники охватывают точечную правку мастера, добавление инструмента, импорт и сравнение с источником.

## Проверка

Python 3.12+; legacy MusicXML-инструментам нужен lxml, рендеру — MuseScore. Каталогизатор использует только stdlib. Не устанавливать зависимости в runtime Hermes.

```bash
python -m unittest discover -s scripts/tests -v
python scripts/library_catalog.py --root /path/to/orchestration-library --check
python scripts/validate_brass.py --write-demo demo.musicxml
python scripts/validate_brass.py demo.musicxml --level amateur --json
```

Демо намеренно содержит **2 ошибки и 9 предупреждений**, ожидаемый rc=1. Создание партий: `python scripts/make_parts.py score.musicxml --out parts`; PDF рендерить явным путём MuseScore и проверять после последней правки. Для `--pdf` читать ограничения в environment.md, на Windows указывать `--mscore`.

Каталогизатор: `--write` обновляет технические поля, сохраняя ручные метаданные по пути; `--render` строит `scores/CATALOG.md`; `--check` ничего не записывает и дополнительно сверяет PDF-хеши с `books/manifest.json`. Не обновлять эталон для сокрытия неизвестного расхождения.

## Установка и библиотека

На машине владельца канон — `C:/Users/IAI/.agents/skills/brass-orchestration`; Hermes подключает его через `skills.external_dirs`. Этот репозиторий — зеркало методики и кода. На другом хосте настроить путь к своей копии и проверить загрузку skill_view; не переносить Windows-пути буквально.

Библиотека отдельно: `ORCH_LIBRARY` или `~/Documents/orchestration-library`. Книги, OCR, сетевые тексты и партитуры в репозиторий не входят. Наличие на IMSLP/WIMA не означает public domain конкретного переложения или редакции; права проверяются отдельно.
