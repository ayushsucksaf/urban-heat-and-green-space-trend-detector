# Methodology: Vegetation Change in Pune, 2000-2024

NASA Space Apps Challenge 2026, Earth System Trend Detective.

## Question

Where is Pune losing vegetation, and is the loss concentrated in the urban expansion zone while the wider district stays green?

## Study area

Pune district, Maharashtra (about 15,600 km2, FAO GAUL level-2 boundary), analysed at 1 km. It includes the city, farmland, and the edge of the Western Ghats. The district-wide numbers cover all of it. "Urban" hotspots are cells within 15 km of central Pune (18.52 N, 73.86 E).

## Data

| Product | Source | Resolution | Period | Use |
|---|---|---|---|---|
| MOD13A3 v061 (NDVI) | NASA MODIS Terra | 1 km, monthly | 2000-2024 | Main analysis |
| GPM IMERG Monthly V07 | NASA | 0.1 degree, monthly | 2001-2024 | March-May rainfall column in timeseries.csv, for checking wet and dry years. Not used in any reported result. |
| MOD11A2 v061 (LST) | NASA MODIS Terra | 1 km, 8-day | 2000-2024 | Analysed, then excluded (see below) |

All processing was done in Google Earth Engine. The app's basemaps (Esri, OpenStreetMap contributors) are for context only.

## Method

1. **Season.** March to May for every year. Using one fixed pre-monsoon window avoids monsoon timing swamping the signal.
2. **Quality filter.** MOD13A3 SummaryQA of 0 or 1 (good or marginal) kept. Cloudy and snow pixels removed.
3. **Annual value.** Mean of valid observations in the window, per pixel.
4. **Trend.** For each pixel, ordinary least squares of NDVI against time in decades (25 years, 2000 to 2024). The slope is the NDVI change per decade and is the map layer. A two-sided t-test on the slope (23 degrees of freedom, |t| of 2.069 or more for 5 percent) was used to flag significant pixels.
5. **Hotspots.** Annual composites were averaged over a 1 km UTM grid (EPSG:32643). Each cell's NDVI change is expressed as a percent of its 2000-2004 baseline mean, so sparse and dense areas can be compared. Cells are ranked from most negative.
6. **Urban filter.** The top five cells were checked by location. Cells 2, 4 and 5 are in east Pune near Kharadi and Manjri. Cell 1 (Bhor taluka, about 43 km south) and cell 3 (Junnar/Ambegaon, rural north) were excluded as non-urban.
7. **Time series.** District-wide mean March-May NDVI per year.

## Results

- District mean NDVI rose from about 0.28 in 2000 to about 0.36 in 2024. The district as a whole got greener.
- The three east Pune hotspots lost vegetation over the same period: -38.9 percent, -36.0 percent and -35.8 percent against their 2000-2004 baseline.
- The two rural cells excluded from the headline had similar losses (-39.9 and -37.3 percent), so large vegetation loss is not unique to the city.

## What was left out: land surface temperature

We also fitted per-pixel trends for March-May land surface temperature. The result was cooling almost everywhere. The district mean fell by about 1.8 C per decade, and nearly every pixel was negative, with the summer mean dropping from roughly 44 C to 40 C. That is the opposite of what an expanding city should show, and it does not match general reporting of warming in the region.

We did not find the cause. Possible explanations include changes in valid-observation counts across years, quality-flag handling, or sensor effects, but we did not test any of them. Because we could not validate it, we did not report any temperature result and the app does not display it. The urban heat question remains open for this project.

The significance mask file (`sig_mask.tif`) came out of the same pipeline, flags most pixels in the district, and does not match its intended definition. It is not used in the app or in any result above. The significance columns in `hotspots.csv` are likewise not relied on.

## Limitations

- 1 km pixels cover about one square kilometre each, so cells are not neighborhoods and names are approximate.
- NDVI loss is not proof of construction. Crop cycles, irrigation and farmland abandonment on the city fringe can look similar. The link to IT-park and housing growth in Kharadi and Manjri is consistent with what is known about the area, but we did not test it. High-resolution imagery would be the next check.
- Pre-monsoon NDVI depends on rainfall. Rainfall is in the data file for eyeballing but was not controlled for.
- The regression ignores year-to-year correlation, so significance is probably optimistic.
- The percent-change definition follows the Earth Engine script. Check the baseline and end windows there before quoting exact figures.

## Use of Super Intelligence (SI)

Claude (Anthropic) suggested the project concept, the city and the season during brainstorming, and the team accepted them. Claude wrote the Earth Engine scripts, the analysis and data-prep code, the web page, and drafts of the documentation, and it flagged the temperature problem during review. The team directed the work and decided to drop the temperature analysis and focus on vegetation loss. Code files are labelled as AI-generated. No AI-generated images, audio or video are used.