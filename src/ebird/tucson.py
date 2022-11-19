"""
Tucson Ebird Sightings
"""
from src.ebird.ebird import EbirdApi

TUCSON_COORDS = (32.225535, -110.914929)
TUCSON_RADIUS = 30 # km
DAYS_BACK = 10


req = {
    "lat": TUCSON_COORDS[0],
    "lon": TUCSON_COORDS[1],
    "region": "Pima",
    "radius": TUCSON_RADIUS,
    "days": DAYS_BACK,
    "notable": "0",
    "species": ''
}
ebird = EbirdApi(req)
for loc in ebird.locSpecies.locations:
    x = l
