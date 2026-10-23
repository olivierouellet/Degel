# Contribuer · Contributing

**[Français](#français) · [English](#english)**

---

## Français

Merci de votre intérêt! En participant, vous acceptez le [code de conduite](CODE_OF_CONDUCT.md). Vous utilisez l’IA? Lisez la [politique sur l’IA](AI_POLICY.md).
Les issues et les demandes de tirage sont bienvenues en français ou en anglais.

### Installation

```bash
uv venv --python 3.13
uv pip install -r requirements_test.txt
pytest
ruff check && ruff format --check
```

Les tests n’appellent jamais le vrai service : ils utilisent des réponses enregistrées dans
`tests/fixtures/`. Pour en enregistrer une nouvelle :

```bash
curl -o tests/fixtures/zone_degel.csv "https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:zone_degel&outputformat=csv"
```

### Conventions

* **Le français d’abord.** Toute documentation est bilingue, avec la section française en premier.
* **Textes de l’interface** : `strings.json` (anglais), copié tel quel dans `translations/en.json`, et
  `translations/fr.json`. Un test vérifie que les trois ont les mêmes clés.
* **Commits** : `[Sujet] Ce qui a changé`, un sujet par commit (par exemple `[Integration]`, `[Docs]`, `[Tooling]`).
* **Les dates restent celles de Transports Québec.** Dégel ne devine ni ne corrige les dates publiées.

---

## English

Thanks for your interest! By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md). Using AI tools? Read the [AI policy](AI_POLICY.md).
Issues and pull requests are welcome in French or English.

### Setup

```bash
uv venv --python 3.13
uv pip install -r requirements_test.txt
pytest
ruff check && ruff format --check
```

Tests never call the real service: they use responses recorded in `tests/fixtures/`. To record a
new one:

```bash
curl -o tests/fixtures/zone_degel.csv "https://ws.mapserver.transports.gouv.qc.ca/swtq?service=wfs&version=2.0.0&request=getfeature&typename=ms:zone_degel&outputformat=csv"
```

### Conventions

* **French first.** All documentation is bilingual, with the French section first.
* **Interface text**: `strings.json` (English), copied as is to `translations/en.json`, and
  `translations/fr.json`. A test checks that all three have the same keys.
* **Commits**: `[Topic] What changed`, one topic each (for example `[Integration]`, `[Docs]`, `[Tooling]`).
* **The dates stay Transports Québec's.** Dégel never guesses or corrects the published dates.
