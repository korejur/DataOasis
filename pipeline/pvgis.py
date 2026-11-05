"""Tablica specifičnog prinosa FN sustava (kWh/kWp/god) za Zagreb iz PVGIS-a.

PVGIS (JRC, Europska komisija) daje prinos za zadani nagib i orijentaciju
modula. Umjesto upita za svaku od ~milijun krovnih ploha, jednom dohvatimo
mrežu nagib x azimut i kasnije interpoliramo.

Konvencija azimuta u projektu: 0 = sjever, 90 = istok, 180 = jug, 270 = zapad.
PVGIS koristi `aspect`: 0 = jug, 90 = zapad, -90 = istok  ->  aspect = az - 180.

    python -m pipeline.pvgis
"""
import json
import time
import urllib.parse
import urllib.request

import numpy as np

from .config import PARAMS, PVGIS_LAT, PVGIS_LON, REFERENCE

API = "https://re.jrc.ec.europa.eu/api/v5_3/PVcalc"
OUT = REFERENCE / "pvgis_zagreb.json"
TILTS = list(range(0, 91, 5))
AZIMUTHS = list(range(0, 360, 15))


def query(tilt: float, azimuth: float) -> float:
    params = {
        "lat": PVGIS_LAT, "lon": PVGIS_LON, "peakpower": 1,
        "loss": PARAMS["pv_system_loss_pct"], "angle": tilt,
        "aspect": ((azimuth - 180 + 180) % 360) - 180, "outputformat": "json",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                d = json.load(r)
            return float(d["outputs"]["totals"]["fixed"]["E_y"])
        except Exception:
            if i == 3:
                raise
            time.sleep(2 * (i + 1))


def main() -> None:
    grid = np.zeros((len(TILTS), len(AZIMUTHS)))
    flat = query(0, 180)
    for i, t in enumerate(TILTS):
        for j, a in enumerate(AZIMUTHS):
            grid[i, j] = flat if t == 0 else query(t, a)
            time.sleep(0.07)  # PVGIS dopušta do 30 upita/s
        print(f"nagib {t:2d}°: min {grid[i].min():6.0f}  max {grid[i].max():6.0f} kWh/kWp")
    REFERENCE.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": "PVGIS v5.3 PVcalc, JRC European Commission",
        "lat": PVGIS_LAT, "lon": PVGIS_LON, "loss_pct": PARAMS["pv_system_loss_pct"],
        "tilts": TILTS, "azimuths": AZIMUTHS, "yield_kwh_kwp": grid.round(1).tolist(),
    }, indent=1), encoding="utf-8")
    i, j = np.unravel_index(grid.argmax(), grid.shape)
    print(f"Optimum: nagib {TILTS[i]}°, azimut {AZIMUTHS[j]}° -> {grid[i, j]:.0f} kWh/kWp")
    print("Spremljeno:", OUT)


def load_interpolator():
    """Vrati funkciju yield(tilt, azimuth) s bilinearnom interpolacijom."""
    d = json.loads(OUT.read_text(encoding="utf-8"))
    T = np.array(d["tilts"], float)
    A = np.array(d["azimuths"] + [360], float)
    G = np.array(d["yield_kwh_kwp"], float)
    G = np.hstack([G, G[:, :1]])  # zatvori krug azimuta

    def f(tilt, az):
        tilt = np.clip(np.asarray(tilt, float), T[0], T[-1])
        az = np.nan_to_num(np.asarray(az, float), nan=180.0) % 360
        ti = np.clip(np.searchsorted(T, tilt) - 1, 0, len(T) - 2)
        ai = np.clip(np.searchsorted(A, az) - 1, 0, len(A) - 2)
        wt = (tilt - T[ti]) / (T[ti + 1] - T[ti])
        wa = (az - A[ai]) / (A[ai + 1] - A[ai])
        return ((1 - wt) * (1 - wa) * G[ti, ai] + wt * (1 - wa) * G[ti + 1, ai]
                + (1 - wt) * wa * G[ti, ai + 1] + wt * wa * G[ti + 1, ai + 1])

    return f


if __name__ == "__main__":
    main()
