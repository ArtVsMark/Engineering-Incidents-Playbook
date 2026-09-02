# Витринные артефакты · Showcase assets

> **Читатель:** участник — как собираются витринные картинки.

## `social-preview.html` → `social-preview.png`

Превью для соцсетей: 1280×640, грузится руками в Settings → General → Social
preview. Загрузка — единственная операция, недостижимая из окна: у токена нет
прав на репозиторий как объект ([#57](https://github.com/ArtVsMark/Engineering-Incidents-Playbook/issues/57)).

Исходник лежит рядом с производным, потому что иначе следующая правка начнётся
с вопроса «чем это вообще делали» ([118](../rules/ru/118-keep-the-source-next-to-the-derived.md)).

Пересобрать:

```
chromium --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=1280,640 \
  --screenshot=assets/social-preview.png \
  "file://$PWD/assets/social-preview.html"
```

**Числа правил на картинке нет намеренно.** Её не пересобирает ни один прогон,
поэтому число устарело бы молча, а превью выглядело бы свежим — ровно
[127](../rules/ru/127-a-number-in-prose-needs-a-guarded-marker.md). Дешевле всего
это обходится отсутствием числа, а не ещё одним механизмом.

The source sits next to the derived artefact; the rule count is deliberately
absent, because nothing rebuilds this image and a stale number would look fresh.
