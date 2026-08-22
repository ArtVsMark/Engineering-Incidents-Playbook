# Фрагменты журнала · Changelog fragments

Каждое изменение кладёт сюда **свой файл**, а не строку в общий журнал. Два
файла с разными именами не конфликтуют никогда — поэтому очередь мержа
перестаёт зависеть от порядка ([030](../rules/ru/030-changelog-from-fragments.md)).

Each change drops **its own file** here instead of a line in a shared journal.
Two files with different names never conflict, so the merge queue stops
depending on order.

## Форма · Shape

```
changelog.d/<слаг>.<секция>.md
```

`слаг` — что угодно уникальное, обычно имя ветки. Секция — одна из:

| Секция · Section | Когда · When |
|---|---|
| `added` | появилось новое |
| `changed` | изменилось существующее |
| `fixed` | починено сломанное |
| `removed` | удалено |
| `internal` | не видно снаружи: гейты, скрипты, конвейер |

Внутри — **одна строка текста**, без ведущего `-` и без имени секции: их
подставит сборка.

Inside — **one line of text**, with no leading `-` and no section name: the
build adds those.

## Пример · Example

`changelog.d/attribution-gate.added.md`:

```
Гейт атрибуции: трейлеры соавторства сверяются со списком согласованных имён (#20).
```

## Проверка и сборка · Checking and assembling

```
python scripts/collect_changelog.py --check     # проверить фрагменты
python scripts/collect_changelog.py --preview   # посмотреть, как соберётся
python scripts/collect_changelog.py --collect   # собрать в [Unreleased] и удалить
```

`--check` стоит в конвейере. Пустой фрагмент считается находкой, а не мелочью:
файл, в котором ничего не написано, выглядит сделанной работой.

`--check` runs in CI. An empty fragment is a finding, not a nicety: a file with
nothing in it looks like work that was done.
