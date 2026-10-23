<p align="center">
  <img src="https://raw.githubusercontent.com/olivierouellet/Degel/main/assets/icon.svg" alt="Logo de Dégel" width="128" height="128">
</p>

<h1 align="center">Dégel</h1>

<p align="center">La période de dégel au Québec dans Home Assistant · Québec’s spring thaw period in Home Assistant</p>

<p align="center"><b><a href="#français">Français</a> · <a href="#english">English</a></b></p>

---

## Français

Chaque printemps, Transports Québec réduit les charges permises des véhicules lourds pendant la **période de dégel**. Les dates varient selon la zone (1, 2 et 3) et peuvent être devancées ou retardées selon la météo. Dégel les suit pour vous dans Home Assistant et vous permet d’**afficher une carte seulement pendant le dégel et autour de celui-ci**.

Le projet comporte deux parties :

| Partie | Dépôt | Rôle |
|---|---|---|
| **Intégration Dégel** (`degel`) | ce dépôt | Choisissez une ou plusieurs zones (celle de votre domicile est proposée). Crée un capteur *Saison de dégel* pour la visibilité des cartes, et pour chaque zone un capteur de période et ses dates de début et de fin. |
| **Dégel-Carte** | [Dégel-Carte](https://github.com/olivierouellet/Degel-Carte) | Une carte de tableau de bord : l’état de chaque zone, le compte à rebours, une ligne du temps et les liens vers Transports Québec. En français et en anglais. |

### Fonctionnalités

- **Configuration dans l’interface** : *Paramètres → Appareils et services → Ajouter une intégration → Dégel*. Cochez une zone ou une combinaison de zones. Si l’emplacement de votre domicile est dans une zone, elle est déjà cochée.
- **Jours avant et après** (14 et 7 par défaut) : la fenêtre pendant laquelle le capteur *Saison de dégel* est allumé.
- **Changer les zones ou les jours plus tard** avec *Configurer*. Les capteurs des zones retirées sont supprimés; le capteur *Saison de dégel* garde son identifiant.
- Les dates sont vérifiées toutes les 6 heures, et les capteurs changent d’état à la minute près du début et de la fin, sans attendre la prochaine vérification. Si le service est injoignable, les dernières dates connues sont conservées.
- Interface en français et en anglais.

### Capteurs

Les identifiants dépendent de la langue de Home Assistant au moment de l’ajout. En français :

| Entité | État | Détails |
|---|---|---|
| `binary_sensor.degel_saison_de_degel` | allumé du nombre de *jours avant* le début de la première période suivie jusqu’au nombre de *jours après* la fin de la dernière | Attributs : `thaw_zones` (zone, nom, début, fin, état), `active_zones`, `days_before`, `days_after`, `season_start`, `season_end`. C’est le capteur que lit la carte. |
| `binary_sensor.degel_periode_de_degel_zone_1` | allumé pendant la période de dégel de la zone | Attributs : `start`, `end`, `name`, `status` (`upcoming`, `active`, `ended`). |
| `sensor.degel_debut_du_degel_zone_1` | horodatage du début (00 h 01) | |
| `sensor.degel_fin_du_degel_zone_1` | horodatage de la fin (23 h 59) | |

En anglais : `binary_sensor.degel_thaw_season`, `binary_sensor.degel_zone_1_thaw_period`, `sensor.degel_zone_1_thaw_start`, `sensor.degel_zone_1_thaw_end`.

### Afficher une carte seulement autour du dégel

**N’importe quelle carte** : dans l’onglet *Visibilité* de la carte, ajoutez une condition *État de l’entité* sur *Saison de dégel* = *Allumé*. En YAML :

```yaml
visibility:
  - condition: state
    entity: binary_sensor.degel_saison_de_degel
    state: "on"
```

**Dégel-Carte** a aussi son option *Masquer la carte hors de la saison de dégel*.

### Installation

**Avec HACS (recommandé)**

[![Ouvrir votre instance Home Assistant et ce dépôt dans HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=olivierouellet&repository=Degel&category=integration)

1. Dans Home Assistant, ouvrez **HACS** → **⋮** (en haut à droite) → **Dépôts personnalisés**.
2. Dépôt : `https://github.com/olivierouellet/Degel`, type : **Intégration**, puis **Ajouter**. (Le bouton ci-dessus fait les étapes 1 et 2 pour vous.)
3. Cherchez **Dégel**, ouvrez-la et cliquez sur **Télécharger**.
4. Redémarrez Home Assistant.
5. Ajoutez l’intégration : *Paramètres → Appareils et services → Ajouter une intégration → Dégel*.

**Manuellement** : copiez `custom_components/degel` dans le dossier `config/custom_components/` de Home Assistant, redémarrez, puis ajoutez l’intégration comme à l’étape 5.

**La carte** : installez [Dégel-Carte](https://github.com/olivierouellet/Degel-Carte) de la même façon, comme dépôt personnalisé HACS de type **Dashboard**.

### Et les limites de charge?

Le jeu de données [Limite de charge](https://www.donneesquebec.ca/recherche/fr/dataset/limite-de-charge) (ponts et structures à charge limitée toute l’année) n’est offert qu’en consultation (carte et WMS, licence CC BY-ND), sans dates. Dégel ne l’importe donc pas; Dégel-Carte peut afficher un lien vers sa carte.

### Développement

- Tests : `uv venv && uv pip install -r requirements_test.txt`, puis `pytest` (Python 3.13). Ils utilisent des réponses enregistrées du service dans `tests/fixtures`.
- Style : `ruff check` et `ruff format`.
- L’icône est dans `custom_components/degel/brand/` (Home Assistant 2026.3 ou plus récent l’affiche). Sa source est `assets/icon.svg`; après l’avoir modifiée, exportez `icon@2x.png` en 512 × 512 et `icon.png` en 256 × 256.
- Voir [CONTRIBUTING.md](CONTRIBUTING.md).

Données : [Zone de dégel](https://www.donneesquebec.ca/recherche/dataset/zone-de-degel), ministère des Transports et de la Mobilité durable du Québec, sur Données Québec (CC BY 4.0). Les dates officielles sont celles de la [page de la période de dégel](https://www.transports.gouv.qc.ca/fr/entreprises-partenaires/ent-camionnage/degel/Pages/Periode-de-degel.aspx) et des arrêtés publiés à la *Gazette officielle du Québec*. Dégel n’est pas affilié au gouvernement du Québec.

---

## English

Every spring, Transports Québec lowers the allowed loads of heavy vehicles during the **thaw period** (*période de dégel*). The dates differ by zone (1, 2 and 3) and can be moved earlier or later with the weather. Dégel follows them for you in Home Assistant and lets you **show a card only during and around the thaw**.

It has two parts:

| Part | Repository | What it does |
|---|---|---|
| **Dégel integration** (`degel`) | this one | Pick one or more zones (your home’s zone is suggested). Creates a *Thaw season* sensor for card visibility, and for each zone a period sensor and its start and end dates. |
| **Dégel-Carte** | [Dégel-Carte](https://github.com/olivierouellet/Degel-Carte#english) | A dashboard card: each zone’s status, a countdown, a timeline and links to Transports Québec. In French and English. |

### Features

- **Set up from the UI**: *Settings → Devices & services → Add integration → Dégel*. Tick one zone or any combination. When your home location is in a zone, it is already ticked.
- **Days before and after** (14 and 7 by default): the window during which the *Thaw season* sensor is on.
- **Change the zones or the days later** under *Configure*. Sensors of removed zones are deleted; the *Thaw season* sensor keeps its ID.
- Dates are checked every 6 hours, and the sensors change state at the minute a period starts or ends, without waiting for the next check. If the service can’t be reached, the last known dates are kept.
- Interface in French and English.

### Sensors

Entity IDs depend on Home Assistant’s language when the integration is added. In English:

| Entity | State | Details |
|---|---|---|
| `binary_sensor.degel_thaw_season` | on from *days before* the first followed period starts until *days after* the last one ends | Attributes: `thaw_zones` (zone, name, start, end, status), `active_zones`, `days_before`, `days_after`, `season_start`, `season_end`. The card reads this sensor. |
| `binary_sensor.degel_zone_1_thaw_period` | on during the zone’s thaw period | Attributes: `start`, `end`, `name`, `status` (`upcoming`, `active`, `ended`). |
| `sensor.degel_zone_1_thaw_start` | timestamp of the start (00:01) | |
| `sensor.degel_zone_1_thaw_end` | timestamp of the end (23:59) | |

In French: `binary_sensor.degel_saison_de_degel`, `binary_sensor.degel_periode_de_degel_zone_1`, `sensor.degel_debut_du_degel_zone_1`, `sensor.degel_fin_du_degel_zone_1`.

### Show a card only around the thaw

**Any card**: in the card’s *Visibility* tab, add an *Entity state* condition on *Thaw season* = *On*. In YAML:

```yaml
visibility:
  - condition: state
    entity: binary_sensor.degel_thaw_season
    state: "on"
```

**Dégel-Carte** also has a *Hide the card outside the thaw season* option.

### Installation

**With HACS (recommended)**

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=olivierouellet&repository=Degel&category=integration)

1. In Home Assistant, open **HACS** → **⋮** (top right) → **Custom repositories**.
2. Repository: `https://github.com/olivierouellet/Degel`, type: **Integration**, then **Add**. (The button above does steps 1 and 2 for you.)
3. Search for **Dégel**, open it and click **Download**.
4. Restart Home Assistant.
5. Add the integration: *Settings → Devices & services → Add integration → Dégel*.

**Manually:** copy `custom_components/degel` into your Home Assistant `config/custom_components/` folder, restart, and add the integration as in step 5.

**The card:** install [Dégel-Carte](https://github.com/olivierouellet/Degel-Carte#english) the same way, as a HACS custom repository of type **Dashboard**.

### What about load limits?

The [Limite de charge](https://www.donneesquebec.ca/recherche/fr/dataset/limite-de-charge) dataset (bridges and structures with a year-round load limit) is offered for viewing only (map and WMS, CC BY-ND licence), with no dates. Dégel doesn’t import it; Dégel-Carte can show a link to its map.

### Development

- Tests: `uv venv && uv pip install -r requirements_test.txt`, then `pytest` (Python 3.13). They use recorded service responses in `tests/fixtures`.
- Style: `ruff check` and `ruff format`.
- The icon lives in `custom_components/degel/brand/` (Home Assistant 2026.3 or later shows it). Its source is `assets/icon.svg`; after editing it, export `icon@2x.png` at 512×512 and `icon.png` at 256×256.
- See [CONTRIBUTING.md](CONTRIBUTING.md).

Data: [Zone de dégel](https://www.donneesquebec.ca/recherche/dataset/zone-de-degel), Québec Ministère des Transports et de la Mobilité durable, on Données Québec (CC BY 4.0). The official dates are those on the [thaw period page](https://www.transports.gouv.qc.ca/fr/entreprises-partenaires/ent-camionnage/degel/Pages/Periode-de-degel.aspx) and in the orders published in the *Gazette officielle du Québec*. Dégel is not affiliated with the Government of Québec.
