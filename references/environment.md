# Окружение и проверяемые команды

## Windows 11 — проверено 28.11.2026 (базовые команды 24.11.2026)

Python `C:/Users/IAI/AppData/Local/Programs/Python/Python312/python.exe`: 3.12.10, lxml 6.1.3; `import pymupdf` работает. Не путать с python3 Hermes (другой интерпретатор). MuseScore `C:/Program Files/MuseScore 4/bin/MuseScore4.exe`: `--version` → 4.7.4; экспорт демо MusicXML в PDF выполнен реально. На другом хосте проверить пути заново. Пакеты не устанавливать в runtime Hermes.

```bash
PY='C:/Users/IAI/AppData/Local/Programs/Python/Python312/python.exe'
SK='C:/Users/IAI/.agents/skills/brass-orchestration'
MS='C:/Program Files/MuseScore 4/bin/MuseScore4.exe'
"$PY" -c 'import sys,lxml,pymupdf; print(sys.version); print(lxml.__version__); print(pymupdf.__file__)'
"$MS" --version
"$PY" "$SK/scripts/library_catalog.py" --root C:/Users/IAI/Documents/orchestration-library --check
```

В Bash цитировать пробелы; native-программы получают пути `C:/...`, не `/c/...`. Рабочие файлы — в проекте, временные — в scratch Hermes. Не называть скрипты `json.py`, `inspect.py`, `xml.py`.

## Самотест

В новом рабочем каталоге, не в библиотеке:

```bash
"$PY" "$SK/scripts/validate_brass.py" --write-demo demo.musicxml
"$PY" "$SK/scripts/validate_brass.py" demo.musicxml --level amateur --json
```

Ожидание: rc=1, ровно 2 errors и 9 warnings. Это намеренно плохая фикстура, не музыка для исполнения. Текстовый режим печатает REJECT; JSON не содержит отдельного поля verdict. Не ставить `&&` после ожидаемого rc=1 для следующей проверки. Сохранять stdout и код возврата отдельно; не подавлять любые ошибки через `|| true`.

```bash
"$PY" -m unittest discover -s "$SK/scripts/tests" -v
"$PY" -c "import pathlib,py_compile; [py_compile.compile(str(p),doraise=True) for p in pathlib.Path(r'$SK/scripts').rglob('*.py')]"
```

`py_compile` создаёт `__pycache__`: не включать в коммит/зеркало. Негативные тесты — только на временных фикстурах. Каталогизатор поддерживает Python 3.12+: не использовать `ntpath.isreserved`, появившийся лишь в 3.13. Прогонять тесты именно документированным интерпретатором, а не только более новым runtime Hermes. На Windows тест реального symlink может быть skipped из-за WinError 1314; это ограничение тестирования указывать отдельно, а не считать подтверждением защиты на настоящей ссылке. Реальный junction проверять отдельной временной фикстурой: он доступен без привилегии symlink. Проверять также junction в предках корня до resolve и исключения генерируемых файлов с другим регистром имени; иначе каталог способен включить собственный хеш.

Ритм (проверено 28.11.2026): тестов 24, один skipped; `"$PY" "$SK/scripts/check_rhythm.py" demo.musicxml` на демо выше даёт `0 issue(s)` и `RESULT PASS`.

## Генерация и печать

```bash
"$PY" "$SK/scripts/voice_quintet.py" --prog 'Bb,Eb,F,Bb' --bars 2 --rests 3,6 --out score.musicxml
"$PY" "$SK/scripts/validate_brass.py" score.musicxml --level amateur --json
"$MS" -o score.pdf score.musicxml
"$MS" -o score.png score.musicxml
"$PY" "$SK/scripts/make_parts.py" score.musicxml --out parts
```

Для PDF партий на Windows предпочитать явный цикл MuseScore по полученным MusicXML. Legacy `make_parts.py --pdf` по умолчанию ищет `mscore3`, его обёртка ставит `TMPDIR=/tmp`. Если используется `--pdf`, передать `--mscore "$MS"` и проверить PDF независимо в новом выходном каталоге: существующий старый PDF может ложно засчитаться успешным. Логику legacy-скриптов при обновлении методики не менять.

MuseScore поддерживает MusicXML и собственные форматы; не утверждать «только 4.x». Поддержку конкретного старого формата проверять на копии. PDF не является редактируемым нотным источником этого конвейера; OMR — отдельный процесс со сверкой.

## Подключение к Hermes без копии

Канон — `.agents/skills/brass-orchestration`. Штатный `skills.external_dirs` может указывать прямо на каталог одного скилла. Перед изменением прочитать текущее значение и добавить путь, не затереть другие. Менять через `hermes config set`; затем `skill_view(name='brass-orchestration')` должен вернуть канонический skill_dir. Не подключать весь каталог или чужой профиль ради одного скилла.
