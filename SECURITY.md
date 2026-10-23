# Sécurité · Security Policy

**[Français](#français) · [English](#english)**

---

## Français

### Signaler une vulnérabilité

**N’ouvrez pas d’issue publique.** Signalez-la en privé par GitHub :

* [Signaler une vulnérabilité](https://github.com/olivierouellet/Degel/security/advisories/new)
  dans l’onglet **Security** du dépôt, visible seulement par le responsable, ou
* écrivez directement à [@olivierouellet](https://github.com/olivierouellet).

Utile à inclure : la version, ce qu’il faut pour exploiter le problème, et une façon de le reproduire.

C’est un projet à un seul responsable, fait sur son temps libre. Comptez un accusé de réception
d’ici deux semaines; vous saurez où en est la correction. Vous serez crédité dans les notes de
version si vous le souhaitez.

### Versions prises en charge

| Version | Prise en charge |
| --- | --- |
| Dernière version publiée | ✅ |
| `main` | ✅ Les correctifs y arrivent d’abord |
| Versions antérieures | ❌ Mettez à jour avec HACS |

### Surface d’attaque

* L’intégration fait une seule sorte de requête : un GET vers le service WFS de Transports Québec (`ws.mapserver.transports.gouv.qc.ca`), sans clé ni donnée personnelle. Seule la recherche de zone à la configuration envoie une position : celle du domicile de Home Assistant, avec la précision que vous avez saisie.
* Le fichier reçu est traité comme du texte non fiable : seuls des nombres et des dates en sont extraits; le nom de la zone n’est qu’un attribut.

---

## English

### Reporting a vulnerability

**Don't open a public issue.** Report privately through GitHub:

* [Report a vulnerability](https://github.com/olivierouellet/Degel/security/advisories/new)
  from the repository's **Security** tab, visible only to the maintainer, or
* contact [@olivierouellet](https://github.com/olivierouellet) directly.

Useful to include: the version, what an attacker needs, and a way to reproduce it.

This is a one-maintainer, spare-time project. Expect acknowledgement within 2 weeks, and you'll
be told where the fix stands. Credit in the release notes if you'd like it.

### Supported versions

| Version | Supported |
| --- | --- |
| Latest release | ✅ |
| `main` | ✅ Fixes land here first |
| Earlier releases | ❌ Update through HACS |

### Attack surface

* The integration makes one kind of request: a GET to Transports Québec’s WFS service (`ws.mapserver.transports.gouv.qc.ca`), with no key and no personal data. Only the zone lookup during setup sends a position: your Home Assistant home location, as precise as you entered it.
* The file it receives is treated as untrusted text: only numbers and dates are taken from it; the zone name is just an attribute.
