"""Constants for the Dégel integration."""

from datetime import timedelta
from zoneinfo import ZoneInfo

DOMAIN = "degel"

CONF_ZONES = "zones"
CONF_DAYS_BEFORE = "days_before"
CONF_DAYS_AFTER = "days_after"

ZONES = (1, 2, 3)
DEFAULT_ZONES = [1]
DEFAULT_DAYS_BEFORE = 14
DEFAULT_DAYS_AFTER = 7
MAX_DAYS = 60

# Dates are announced a few days ahead and move with the weather, so check often.
FETCH_INTERVAL = timedelta(hours=6)

# The published dates and times are Québec local time.
QUEBEC_TZ = ZoneInfo("America/Toronto")

ATTRIBUTION = "Données Québec, Transports et Mobilité durable Québec (CC BY 4.0)"
INFO_URL = (
    "https://www.transports.gouv.qc.ca/fr/entreprises-partenaires/ent-camionnage/degel/Pages/Periode-de-degel.aspx"
)
