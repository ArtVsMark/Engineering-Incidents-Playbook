# Плагин `catalogue` · The `catalogue` plugin

> **Читатель:** подключающийся — как поставить навыки работы с каталогом в свой проект, закрепить их версию и предложить свой навык.

Навыки для проектов, подключённых к каталогу: окно проекта зовёт их, когда
отвечает каталогу, а не когда разбирает свои инциденты. Держит плагин каталог;
сделать и доработать навык может любой проект, а принимает его каталог — тем же
каналом, что и правило.

Skills for projects connected to the catalogue: the project's session calls
them while answering the catalogue. The catalogue holds the plugin; any project
may write or improve a skill, and the catalogue admits it through the same
channel as a rule.

## Навыки · Skills

| Навык | Когда звать |
|---|---|
| `answer-a-rule` | проект пишет или правит запись в `.rules/bindings.json`: разбирает входящие, подключается, перечитывает ответы после подъёма номера контракта |

Вызов — `/catalogue:answer-a-rule` или словами: окно решает само по описанию
навыка. Список один и сверяется с деревом `scripts/check_skills.py` — тем же
гейтом, что навыки окна каталога.

Call it as `/catalogue:answer-a-rule`, or in words: the session decides from the
skill's description. The list is checked against the tree by the same gate as
the catalogue's own skills.

## Как поставить · How to install

Витрина называется `incidents-playbook`, лежит в корне этого репозитория и
отдаёт один плагин, `catalogue`. В `.claude/settings.json` проекта:

```json
{
  "extraKnownMarketplaces": {
    "incidents-playbook": {
      "source": {
        "source": "github",
        "repo": "ArtVsMark/Engineering-Incidents-Playbook",
        "ref": "vX.Y.Z"
      }
    }
  },
  "enabledPlugins": {
    "catalogue@incidents-playbook": true
  }
}
```

Или руками: `/plugin marketplace add ArtVsMark/Engineering-Incidents-Playbook#vX.Y.Z`,
затем `/plugin install catalogue@incidents-playbook`.

The marketplace is `incidents-playbook`, at the root of this repository, with
one plugin, `catalogue`. Put the block above in the project's
`.claude/settings.json`, or add it by hand with the two commands.

**`ref` — релизный тег каталога, а не ветка.** Подключаться к движущейся
ветке значит получать чужую правку навыка в своё окно без изменения у себя —
та же причина, по которой каталог советует закреплять тегом действие
«входящие» ([контракт](../../export/README.md), раздел «Что каталог отдаёт
помимо правил»). Плагин появился после выпуска `v1.2.0`: в этом и более ранних
тегах витрины нет.

**`ref` is a catalogue release tag, not a branch.** A moving branch would push
someone else's edit of a skill into your session with no change on your side.
The plugin appeared after `v1.2.0`; that tag and earlier ones have no
marketplace.

## Как назвать навык плагина в ответе · Naming a plugin skill in your answer

Правило, которое у проекта держит навык этого плагина, отвечает полем `skill`
так же, как навык зовётся: `"skill": "catalogue:answer-a-rule"` (контракт
ответа с 1.7). Адрес `.claude/skills/<имя>` здесь солгал бы: в дереве проекта
навыка нет, он приходит плагином. Такой адрес указывает на дерево каталога, и
каталог сверяет его сам.

A rule held by a skill of this plugin answers `"skill": "catalogue:answer-a-rule"`
— the way it is invoked (answer contract 1.7). The address points into the
catalogue's tree, so the catalogue can check it.

## Версия плагина · The plugin version

Поля `version` у плагина нет намеренно, и `claude plugin validate` об этом
предупреждает. Без поля площадка записывает версией коммит витрины — замер 25
сентября: `d08f87974c17`, следующий коммит доехал обновлением как
`1a44b1c2bf01`. Вписанная версия, которую забыли поднять, держит всех
поставивших на старом тексте: кеш ключуется версией. Поднимать её здесь
некому, поэтому её выводит коммит, а вписанную отвергает
`scripts/check_plugins.py`.

There is deliberately no `version` field. Without it the platform records the
marketplace commit as the version, and each new commit arrives as an update. A
written version nobody bumps would keep every installation on stale text; the
gate rejects one.

## Чего плагин не умеет · What it cannot do

**В облачных окнах (claude.ai/code) плагин из настроек репозитория не
загружается** — облачная сессия не читает ни плагинов, поставленных на своей
машине, ни включённых в `.claude/settings.json`. Там навык доступен только
плагином, который раздаёт организация. Окна самого каталога читают свои навыки
с диска и плагина не ставят.

**Cloud sessions (claude.ai/code) do not load it** from repository settings or
from a local install; only organisation-managed plugins reach them.

## Как предложить или доработать навык · How to propose or improve a skill

Тем же `.rules/proposals.json`, которым проект предлагает правило, — с полем
`kind: skill`, путём к `SKILL.md` у себя и полным коммитом, на котором его
читать. Доработка называет навык, который дорабатывает (`amends`), и тег
каталога, от которого шла (`base`). Поля и ответ каталога — в
[контракте](../../export/README.md), раздел «Навык вместо правила».

Through the same `.rules/proposals.json`: `kind: skill`, the path to your `SKILL.md`
and the full commit to read it at; an improvement names the skill (`amends`) and
the catalogue tag it started from (`base`). Fields and the catalogue's answer
are in the contract, section "A skill instead of a rule".

**Почему навыки плагина лежат здесь, а не в `.claude/skills/`.** У них другой
читатель. Навыки окна каталога ссылаются на пути его дерева — скрипты, записи,
журнал, — и у потребителя этих путей нет. Навыки плагина уходят к потребителю
и ссылаются только на адреса, которые у него открываются (076). Форма у тех и
других одна — заготовка каталога, — и сверяет её один гейт.
