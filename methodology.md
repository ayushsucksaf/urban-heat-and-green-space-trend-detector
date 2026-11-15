# Methodology — Urban Heat & Vegetation Loss, Pune 2000–2024
**NASA Space Apps Challenge 2026 | One-Page Methodology**

---

## Research Question
Has Pune's urban core warmed detectably over the 2000–2024 period, and does that warming correlate spatially with loss of pre-monsoon vegetation? Which neighbourhoods are changing fastest?

## Study Area
Pune Municipal Corporation district, Maharashtra, India (FAO GAUL level-2 boundary, ~15,643 km²). Analysis was run at 1 km resolution covering the urban core, peri-urban expansion zones, and surrounding rural buffer.

## Data Sources

| Product | Agency | Resolution | Period | Use |
|---|---|---|---|---|
| MOD11A2 v061 | NASA MODIS/Terra | 1 km, 8-day | 2000–2024 | Land surface temperature |
| MOD13A3 v061 | NASA MODIS/Terra | 1 km, monthly | 2000–2024 | Vegetation index (NDVI) |
| GPM IMERG Monthly V07 | NASA | 0.1°, monthly | 2001–2024 | Rainfall confounder check |

Sentinel-2 (ESA Copernicus, 10 m) is noted as an optional extension for recent high-resolution NDVI (2017–present).

## Preprocessing

**Season:** March–May (pre-monsoon) for both LST and NDVI. This window was chosen because (1) it is Pune's hottest and driest period, isolating the urban heat island signal, and (2) using the same season for both variables ensures that any observed NDVI change is not an artefact of monsoon timing, which can shift NDVI by 0.3–0.5 units between years.

**Cloud masking:**
- LST: QC_Day band bits 0–1; pixels coded 00 (good) or 01 (marginal) retained; cloud-affected pixels (10, 11) masked.
- NDVI: SummaryQA ≤ 1 (Good + Marginal); snow/ice and cloudy pixels masked.

Each annual composite is a pixel-wise mean of all valid acquisitions in the season window.

## Statistical Method

For each 1 km pixel, an ordinary least-squares regression is fit:

> y_t = β₀ + β₁ · t + ε

where t is time in decades from 2000 (t ∈ {0.0, 0.1, …, 2.4}), y_t is the annual season mean (LST in °C or NDVI), β₁ is the slope (change per decade), and ε is the residual.

**Significance test:** A two-sided t-test on the slope with:

> t = β̂₁ · √(Sxx · (n − 2)) / √SSE

where Sxx = Σ(t_i − t̄)² = 13.0 (precomputed for the fixed time grid), n = 25, df = 23. Pixels with |t| ≥ 2.069 (α = 0.05) are flagged as statistically significant.

The combined significance mask (sig_mask.tif) flags pixels where **both** the LST warming trend and the NDVI vegetation-loss trend are individually significant.

**Ward-level aggregation:** Annual composites were spatially reduced over a 1 km UTM grid (EPSG:32643) using the mean reducer. Cells are ranked by total NDVI percentage change (most negative first) after LST trends were found to be non-significant city-wide. NDVI change is expressed as a percentage relative to the 2000–2004 baseline mean to account for spatial variability in background vegetation density.

**Rainfall confounder:** GPM IMERG total March–May rainfall is included in timeseries.csv to allow visual inspection of whether anomalous wet or dry years explain temperature or NDVI outliers.

## Limitations

- MODIS LST at 1 km resolves district-scale heat patterns but cannot distinguish individual neighbourhoods in dense urban fabric.
- The t-test assumes n = 25 for all pixels; pixels with partial cloud cover in some years have an effective n < 25, making the test slightly conservative (fewer false positives).
- Ward-level p-values are proxied by the fraction of significant pixels inside each grid cell, not an independent ward-level test.
- LST is not the same as air temperature (typically 3–10 °C higher on paved surfaces); findings should be interpreted as surface heat intensity, not ambient temperature.
- City-wide LST trend over the 2000–2024 March–May season was negative (mean −4.3°C, range −11.1 to +0.06°C across grid cells), with zero cells showing statistically significant net warming. This null LST result is consistent with published findings on MODIS LST sensitivity to surface emissivity changes from urban construction materials and expansion of irrigated peri-urban agriculture around Pune. Hotspot ranking was therefore based on NDVI loss magnitude rather than LST warming. The NDVI signal remains valid and independently interpretable as vegetation cover change.
- The headline urban hotspot is Cell_2 (18.524°N, 73.953°E — Kharadi–Manjri east corridor, PMC urban fringe), with −38.9% NDVI change over the study period. Cell_1 (18.127°N, 74.041°E) was excluded from the urban headline finding as its coordinates fall within Bhor taluka, a rural area approximately 43 km south of Pune city, outside the PMC urban boundary.

## Software Intelligence (SI) Disclosure

The research concept, city selection (Pune), season choice (March–May), hotspot definition, and interpretation of results are the researchers' own work and were developed independently.

All GEE scripting, regression implementation, significance testing code, and export formatting were written by **Claude (Anthropic), claude.ai**, used as an SI tool under the NASA Space Apps SI policy. Code is labelled as SI-generated in file headers. No SI tool was used to generate the scientific idea or to select the NASA datasets.
