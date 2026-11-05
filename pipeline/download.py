"""Preuzimanje ZG3D FGDB datoteka za sve gradske četvrti s data.gov.hr.

URL-ovi se dohvaćaju preko CKAN API-ja pri svakom pokretanju, pa skripta
radi i ako Grad promijeni poveznice. Već preuzete četvrti se preskaču.

    python -m pipeline.download            # sve četvrti
    python -m pipeline.download trnje      # samo odabrane
"""
import json
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

from .config import CKAN_API, DISTRICTS, RAW_ZG3D


def package_show(dataset_id: str) -> dict:
    url = CKAN_API + "package_show?id=" + urllib.parse.quote(dataset_id)
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)["result"]


def resource_url(pkg: dict, formats: tuple[str, ...]) -> str:
    for res in pkg["resources"]:
        if (res.get("format") or "").lower() in formats:
            return res["url"]
    raise RuntimeError(f"Nema resursa {formats} u {pkg['name']}")


def fgdb_url(pkg: dict) -> str:
    return resource_url(pkg, ("fgdb", "gdb"))


def safe_extract(zpath, target) -> None:
    with zipfile.ZipFile(zpath) as z:
        for member in z.namelist():  # zaštita od putanja izvan ciljne mape
            p = (target / member).resolve()
            if not str(p).startswith(str(target.resolve())):
                raise RuntimeError(f"Sumnjiva putanja u arhivi: {member}")
        z.extractall(target)


def ensure_readable(slug: str) -> None:
    """Neki FGDB-ovi imaju sloj tipa 'Unknown ZM' (3000) koji GDAL/pyogrio ne čita.
    Tada preuzmi SHP verziju istog skupa (također sadrži multipatch 3D)."""
    import pyogrio  # lokalni import: download radi i bez GIS paketa

    target = RAW_ZG3D / slug
    meta = json.loads((target / "meta.json").read_text(encoding="utf-8"))
    if meta.get("shp"):
        return
    try:
        pyogrio.read_info(target / meta["gdb"])
        return
    except Exception as e:  # noqa: BLE001
        print(f"[warn] {meta['name']}: FGDB nije čitljiv ({e}), koristim SHP")
    shp_dir = target / "shp"
    if not list(shp_dir.glob("*.shp")):
        shp_dir.mkdir(exist_ok=True)
        url = resource_url(package_show(DISTRICTS[slug][0]), ("shp",))
        zpath = shp_dir / "shp.zip"
        fetch(url, zpath)
        safe_extract(zpath, shp_dir)
        zpath.unlink()
    shp = next(shp_dir.glob("*.shp"))
    meta["shp"] = str(shp.relative_to(target)).replace("\\", "/")
    (target / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def fetch(url: str, path, attempts: int = 4) -> None:
    """Preuzmi datoteku uz ponovne pokušaje (poslužitelj povremeno vrati 500)."""
    req = urllib.request.Request(url, headers={"User-Agent": "datathon-zeleni-krovovi/0.1"})
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=600) as r, open(path, "wb") as f:
                shutil.copyfileobj(r, f)
            return
        except (urllib.error.URLError, TimeoutError) as e:
            if i == attempts - 1:
                raise
            wait = 5 * 2 ** i
            print(f"       pokušaj {i + 1} nije uspio ({e}), čekam {wait} s")
            time.sleep(wait)


def download(slug: str) -> None:
    dataset_id, name = DISTRICTS[slug]
    target = RAW_ZG3D / slug
    marker = target / ".done"
    if marker.exists():
        print(f"[skip] {name}")
        return
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    pkg = package_show(dataset_id)
    url = fgdb_url(pkg)
    zpath = target / "fgdb.zip"
    print(f"[get ] {name}: {url}")
    fetch(url, zpath)

    safe_extract(zpath, target)
    zpath.unlink()
    gdbs = list(target.glob("*.gdb"))
    if len(gdbs) != 1:
        raise RuntimeError(f"Očekivana jedna .gdb mapa u {target}, nađeno {gdbs}")
    (target / "meta.json").write_text(
        json.dumps({"dataset": dataset_id, "name": name, "url": url,
                    "metadata_modified": pkg.get("metadata_modified"),
                    "gdb": gdbs[0].name}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    marker.touch()
    size = sum(p.stat().st_size for p in gdbs[0].rglob("*")) / 1e6
    print(f"[ok  ] {name}: {size:.1f} MB")


def main(argv: list[str]) -> None:
    slugs = argv or list(DISTRICTS)
    for slug in slugs:
        download(slug)
        ensure_readable(slug)


if __name__ == "__main__":
    main(sys.argv[1:])
