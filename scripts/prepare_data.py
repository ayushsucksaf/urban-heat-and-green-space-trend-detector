"""
prepare_data.py - turns the GeoTIFF trend rasters into map-ready PNG overlays.

AI-generated code (Claude, Anthropic), disclosed per NASA Space Apps SI policy.

Needs only numpy, pillow, pandas (+ openpyxl for .xlsx). No rasterio / GDAL.
Run from the project root:   python scripts/prepare_data.py
Re-run it any time you replace the files in data/.
"""
import base64
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT / "docs"
OUT = SITE / "overlays"
OUT.mkdir(parents=True, exist_ok=True)
PUNE_CENTRE = (18.52, 73.86)  # used only to flag hotspots inside the urban area
URBAN_KM = 15
UPSCALE = 4  # nearest-neighbour upscale so the 1 km cells look crisp on the map

# colour ramps: (position 0..1, RGB)
RAMPS = {
    "lst": [(0.0, (49, 104, 176)), (0.5, (247, 247, 247)), (1.0, (200, 40, 40))],
    "ndvi": [(0.0, (140, 81, 10)), (0.5, (245, 245, 230)), (1.0, (27, 120, 55))],
}


def read_geotiff(path):
    """Read a single-band GeoTIFF with Pillow and pull bounds from its GeoTIFF tags."""
    im = Image.open(path)
    arr = np.array(im, dtype="float64")
    arr[np.abs(arr) > 1e30] = np.nan  # treat huge fill values as nodata
    px, py = im.tag_v2[33550][:2]  # ModelPixelScale
    tie = im.tag_v2[33922]  # ModelTiepoint
    west, north = tie[3], tie[4]
    h, w = arr.shape
    bounds = {"west": west, "north": north, "east": west + px * w, "south": north - py * h}
    return arr, bounds


def colorize(arr, ramp, vmin, vmax, alpha=205):
    t = np.nan_to_num(np.clip((arr - vmin) / (vmax - vmin), 0, 1), nan=0.5)
    pos = [p for p, _ in ramp]
    rgb = np.stack([np.interp(t, pos, [c[i] for _, c in ramp]) for i in range(3)], axis=-1)
    a = np.where(np.isnan(arr), 0, alpha)
    return np.dstack([rgb, a]).astype("uint8")


def save_png(rgba, name):
    img = Image.fromarray(rgba, "RGBA")
    img = img.resize((img.width * UPSCALE, img.height * UPSCALE), Image.NEAREST)
    img.save(OUT / name)


def main():
    meta = {}

    for key, fname in [("lst", "lst_trend.tif"), ("ndvi", "ndvi_trend.tif")]:
        arr, bounds = read_geotiff(DATA / fname)
        lim = float(np.nanpercentile(np.abs(arr), 98))  # symmetric around 0
        save_png(colorize(arr, RAMPS[key], -lim, lim), f"{key}_trend.png")
        meta[key] = {
            "bounds": bounds,
            "vmin": -lim,
            "vmax": lim,
            "mean": float(np.nanmean(arr)),
            "valid_pixels": int(np.sum(~np.isnan(arr))),
        }
        meta["bounds"] = bounds
        print(f"{key}: bounds={bounds}  mean trend={meta[key]['mean']:.3f}")

    sig, _ = read_geotiff(DATA / "sig_mask.tif")
    sig_rgba = np.zeros((*sig.shape, 4), dtype="uint8")
    sig_rgba[sig == 1] = (20, 20, 20, 110)
    save_png(sig_rgba, "sig_mask.png")

    # clean the Earth Engine CSV export (drops system:index and .geo columns)
    ts = pd.read_csv(DATA / "timeseries.csv")
    ts = ts[[c for c in ["year", "lst_summer_c", "ndvi_mean", "rain_mm"] if c in ts.columns]]
    ts.to_csv(DATA / "timeseries_clean.csv", index=False)

    # hotspots: accept .xlsx or .csv
    xlsx, csv = DATA / "hotspots.xlsx", DATA / "hotspots.csv"
    if xlsx.exists():
        pd.read_excel(xlsx).to_csv(csv, index=False)
    print(f"hotspots rows: {len(pd.read_csv(csv))}")

    # one JS file the web page loads (works from file:// and static hosting)
    ndvi, b = read_geotiff(DATA / "ndvi_trend.tif")
    grid = np.where(np.isnan(ndvi), None, np.round(ndvi * 1000)).tolist()
    hs = pd.read_csv(csv)
    km = np.hypot((hs.centroid_lat - PUNE_CENTRE[0]) * 111, (hs.centroid_lon - PUNE_CENTRE[1]) * 105)
    hs["urban"] = km < URBAN_KM
    keep = ["rank", "neighborhood", "ndvi_change_pct", "centroid_lat", "centroid_lon", "urban"]
    data = {
        "overlay": "data:image/png;base64," + base64.b64encode((OUT / "ndvi_trend.png").read_bytes()).decode(),
        "bounds": b, "vmax": meta["ndvi"]["vmax"], "rows": ndvi.shape[0], "cols": ndvi.shape[1],
        "grid": grid, "ts": ts.to_dict("records"),
        "hotspots": hs[keep].to_dict("records"),
        "finding": json.loads((DATA / "finding.json").read_text()),
    }
    (SITE / "data.js").write_text("window.DATA = " + json.dumps(data) + ";")
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2))
    print("Done. Site data written to", SITE)


if __name__ == "__main__":
    main()