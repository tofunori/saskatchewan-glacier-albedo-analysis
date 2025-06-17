```
Remote Sensing of Environment 267 (2021) 112732
```

Available online 13 October 2021  
0034-4257/© 2021 Elsevier Inc. All rights reserved.

## The influence of forest fire aerosol and air temperature on glacier albedo,

## western North America

## Scott N. Williamson

```
a,*
```

## , Brian Menounos

```
a,b
```

a _Geography Earth and Environmental Sciences and Natural Resources and Environmental Studies Institute, University of Northern British Columbia, Prince George,_

_British Columbia V2N 4Z9, Canada_  
b _Hakai Institute, Campbell River, British Columbia, Canada_

ARTICLE INFO

Editor: Menghua Wang

_Keywords:_  
Albedo  
Forest fire aerosols  
Mountain glaciers  
MODIS  
ERA5 temperature

```
ABSTRACT
```

```
Over the past decade, western North America glaciers experienced strong mass loss. Regional mass loss during
the ablation season is influenced by air temperature, but the importance of other factors such as changes in
surface albedo remains uncertain. We examine changes in surface albedo for 17 glaciated regions of western
North America as documented in a 20-year record (2000 to 2019) of MODIS daily snow albedo (MOD10A1).
Trend analysis reveals that albedo declined for 4% to 81% of the albedo grid cells, and the largest negative trends
were situated south of 60◦N and in the provinces of British Columbia and Alberta. Sen’s slope estimates indicate
that 15 of 17 regions showed a decline of which the majority of the largest declines occurred within 100 m of
glacier median elevation, suggesting that these declines are driven by a rise of the transient snowline. For most
regions, albedo correlates strongly to temperature, and albedo trend in the Chugach region of Alaska, the South
Coast, Southern Interior and Central and Southern Rockies of Canada show a significant relationship to aerosols
optical depth. Temperature is approximately 2 – 6 times more predictive of the variation in albedo than AOD for
the majority of regions, except the Southern Interior and Southern Rockies where albedo shows a greater
dependence on AOD. Investigation of broadband albedo (MCD43A3) for snow grid cells above glacier median
elevation in the Central and Southern Rockies shows that declines in the visible and near infrared portions of the
spectrum are linked to the presence of forest fire generated aerosols. The results of this study indicate that glacier
surface mass balance experiences a regional dependence on forest fire generated light absorbing particles.
```

**1\. Introduction**

Over the past several decades glaciers in western North American  
have collectively lost mass, but notable, regional differences exist  
(Hugonnet et al., 2021; Menounos et al., 2019; Yang et al., 2020; Zemp  
et al., 2019; Berthier et al., 2010; Schiefer et al., 2007). Zemp et al.  
(2019) found that between 2006 and 2016, Alaskan glaciers lost 73 ±  
17 Gt yr^1 whereas the rest of western North America lost 12 ±6 Gt  
yr^1. Air temperature and albedo (the unitless ratio of reflected to  
incident shortwave solar radiation) strongly influence glacier mass  
balance during the ablation season (e.g., Box et al., 2012). Satellite  
derived average melt season albedo has shown to be a good indicator of  
equilibrium line altitude (ELA) and glacier surface mass balance (SMB)  
for many mountain glaciers (De Ruyter de Wildt et al., 2002; Greuell  
et al., 2007; Calluy et al., 2005; Williamson et al., 2020a; Zhang, et al.,  
2021). In addition, the use of glacier area-median elevation has been

```
shown to approximate the ELA (Braithwaite and Raper, 2009).
Prior to the onset of spring melt, broadband albedo for alpine glaciers
is, on average, about 0.80 (e.g., Marshall and Miller, 2020), and can
exceed 0.9 when covered with freshly-deposited dry snow (Cuffey and
Paterson, 2010). Snow cover is usually maintained above a glacier’s
median elevation (accumulation area) throughout the summer melt
period. Snow grain metamorphosis, weathering and roughening de-
creases the accumulation area albedo to ~0.5 (Wiscombe and Warren,
1980). Below a glacier’s median elevation (ablation area), bare glacier
ice is typically present during the summer with an albedo of ~0.34–0.
(Cuffey and Paterson, 2010) for ice areas. Albedo between 0.5 and 0.
has been observed for clean bare ice on the Greenland Ice Sheet, how-
ever (Bøggild et al., 2010).
Glacier snow and ice albedo can be reduced by the direct deposition
of light absorbing particles. These particles are deposited directly or
indirectly as a component of liquid or solid precipitation. Albedo
```

```
* Corresponding author.
E-mail address: snw@ualberta.ca (S.N. Williamson).
```

```
Contents lists available at ScienceDirect
```

## Remote Sensing of Environment

```
journal homepage: http://www.elsevier.com/locate/rse
```

https://doi.org/10.1016/j.rse.2021.  
Received 1 April 2021; Received in revised form 15 September 2021; Accepted 2 October 2021

reduction is also mediated by optically thin snow covering a dark  
background, such as rock or soil. Surface albedo values for bare ice can  
be lowered (as low as in the range of 0.06 to 0.21) if dust, liquid water or  
rock debris accumulates in sufficient quantities on the surface (Cuffey  
and Paterson, 2010; Skiles and Painter, 2017). Glacier snow and ice can  
also have their surface albedo decreased, and melt rates enhanced, by  
the presence of algae (Williamson et al., 2020), forest fire generated  
black carbon (BC) (Thomas et al., 2017; Gleason et al., 2019) and dust  
(Skiles and Painter, 2017). Light absorbing particles tend to accumulate  
at the snow and ice surface as a result of melt (Flanner et al., 2007;  
Schmale et al., 2017). The absorption of sunlight by BC particles warms  
snow, which further reduces the albedo due to an increase in snow grain  
size (Warren and Wiscombe, 1980; Hadley and Kirchstetter, 2012). In  
the Rocky Mountains of Colorado, the dust concentration (in the range  
of 0.02–6.0 mg g^1 ) in snow has a larger control over broadband albedo  
than grain size of the snow/firn (Skiles and Painter, 2017) when dust  
concentrations are orders of magnitude larger than those of black car-  
bon. In the Juneau Ice fields, Nagorski et al. (2019) found that in July,  
the aged snow surface concentration of dust and black carbon was  
substantially larger than in June and that dust contributed more to  
enhanced melt than did black carbon. Analysis of an ice core from South  
Cascade Glacier, Washington State, USA, indicates that dust is typically  
the most important factor in summer albedo reduction except for the  
years where black carbon deposition is above normal due to forest fire  
activity (Kaspari et al., 2020). Alternatively, Rahimi et al. (2020)

```
showed that BC has a larger influence on snow melt across the Rockies
than dust does. Analysis of an ice core, from Combatant Col. on Mount
Waddington in the British Columbia southern Coastal mountains, that
spans the years 1973–2010, shows that black carbon has a larger con-
centration range (0 to 23.94 ppb) than dust (0 to 0.68 ppb) and the
annual minima values for black carbon are larger than those for dust
(Neff et al., 2012). Zhang, et al. (2021) showed that glaciers on the Ti-
betan Plateau melted by up to an additional 15% because of albedo
reduction caused by BC.
Aerosol optical depth (AOD) has been linked to forest fire smoke
(Barnaba et al., 2011) and to black carbon deposition on glaciers
(Thomas et al., 2017). Aerosol optical depth is a dimensionless number
that expresses the amount of solar radiation that is absorbed or scattered
```

## by particles in the atmosphere. AOD at a wavelength of 0.55 μm, has

```
been used to identify the influence of light absorbing particles on snow
albedo (Qian et al., 2015; Skiles et al., 2018). Black carbon aerosol
generated by Canadian wildfires during the summer of 2013 has been
detected in snow pits on the Greenland Ice Sheet (Thomas et al., 2017).
The forest fire aerosols were detected by the Aqua satellite carrying the
Moderate Resolution Imaging Spectroradiometer (MODIS) and the
Cloud-Aerosol Lidar with Orthogonal Polarization (CALIPSO) instru-
ment while in transit between Canada and Greenland. The MODIS Aqua
MYD08_D3 product (Platnick et al., 2015) was used to identify the 550
nm aerosol optical depth over North America and Greenland using a
spatial resolution of 1◦latitude and longitude. MODIS Daily 550 nm
```

**Fig. 1.** The glaciated regions of western North America contained in the Randolf Glacier Inventory zones 1 and 2 were delineated into 17 regions. The small glaciers  
in California and the glaciers furthest west on the Aleutian Islands have been omitted. Details regarding the regions are found in Table 1.

## (0.55 μm) AOD maps from late July show daily values greater than 0.

over Canadian fires and a smoke plume with AOD ~ 0.4 over the Davis  
Strait, west of Greenland (Thomas et al., 2017). The black carbon was  
deposited during the summer of 2013 and presented concentrations of  
2.8 to 43 ng g^1 , of which any concentrations above 3 ng g^1 were  
correlated with NH 4 concentrations, which indicate a forest fire source  
(Polashenski et al., 2015). The black carbon layer of the above con-  
centration was sufficient to reduce surface albedo by as much as 1% to  
2%. These albedo declines are derived from radiative transfer modelling,  
and fit well with observations (Polashenski et al., 2015). Black carbon  
concentrations of 3–30 ng g^1 can reduce the albedo of the visible  
portion of the spectrum by 0–2% and broadband albedo by 0–1%, in  
cold fine grain snow (Warren, 2013). When snow begins to melt, the  
albedo reduction in the visible spectrum increases to 1–6% and re-  
ductions in broadband albedo are in the range of 0–3% (Warren, 2013).  
Typical values for black carbon concentrations found in undisturbed  
high latitude Northern Hemisphere snow ranges between 3 and 30 ng  
g^1 (Warren, 2013). The amount of surface concentrated BC on a glacier  
surface where the snow has been completely melted and only ice re-  
mains can be an order of magnitude larger (Schmale et al., 2017).  
Over the last decade, forest fires in western Canada have increased in  
size, severity and duration (Hanes et al., 2018). In British Columbia, for  
example, forest fires in 2017 and 2018 burned ~ three times the amount  
of area than the next largest annual burned area between 2000 and

2019.  The 2000 to 2019 average annual area burned in British Columbia  
    was 196,104 km^2 ±306,705 km^2 (one standard deviation). Between  
    2015 and 2019 the annual amount of area burned in British Columbia  
    compared to the average was 120%, 40%, 526%, 535% and 11%.  
    Anomalies in air temperature and forest fire severity are positively  
    correlated which confounds the ability to attribute changes in glacier  
    albedo and mass balance to temperature in the absence of forest fire  
    smoke.  
    The primary motivation of our study is to assess whether albedo has

```
changed for glaciated regions of western North America over the last 20
years. We then determine factors that could explain these trends. Spe-
cifically, we aim to:
```

1.  Identify trends of glacier surface albedos in the end of melt season  
    (August) during the period 2000–2019;
2.  Assess the relation between summer average air temperature and  
    summer average AOD (forest fire generated) to end of melt season  
    albedo using multiple linear regression (MLR) and dominance anal-  
    ysis (DA); and
3.  Examine the broadband albedo in conjunction with transport and  
    dispersion modelling for regions showing a differential influence  
    from fire generated aerosols.  
    **2\. Study area**

```
The location and extent of Western North America glaciers arises
from the interplay of high mountains and proximity to the Pacific Ocean.
The Pacific regions experience substantially more summer and winter
precipitation than the interior regions. Glaciers range in elevation from
6190 m (ice-clad Denali Peak) to sea level, with over 2000 m difference
in the median elevation of glaciated regions. The study area extends
from north of the Arctic circle to southern Wyoming (Fig. 1, Table 1). We
explore changes in albedo within glacierized regions of western North
America bounded by the Randolf Glacier Inventory - RGI (Pfeffer et al.,
2014) zones 01 and 02. We subdivided RGI 01 and RGI 02 into 17
distinct regions modifying regional boundaries described elsewhere
(Schiefer et al., 2007 Clarke et al., 2015; Berthier et al., 2010; Menounos
et al., 2019; Yang et al., 2020). Our regions represent a compromise
between representing diverse glacierized terrain that spans broad re-
gions and the need to contain enough MODIS grid cells that cover gla-
cierized terrain. The glaciers in California are too small, for example,
and hence, were excluded from this study. The Aleutian Island glaciers
west of Fox Islands (53.14◦N, 168.62◦W) were also excluded because of
their small extent. We divide the remaining glaciers into two groups that
represent glaciers in maritime (Pacific) and interior (Rockies) locations.
```

**3\. Data & methods**

```
3.1.Snow albedo
```

```
The albedo data used in our study originates from the MODIS sensor
on the Terra and Aqua satellite platforms, MOD10A1, MYD10A1 and
MCD43A3, collection 6. Terra (Aqua) is in a near-polar sun synchronous
descending (ascending) orbit and acquires data with the MODIS sensor
```

## over a spectral range of 0.459 μm to 14.385 μm in 36 spectral bands.

```
Equatorial overpass time for Terra is approximately 10:30 local time,
whereas Aqua crosses the equator at 13:30. MODIS Snow albedo
(MOD10A1 and MYD10A1) is produced following the algorithm
described in Klein and Stroeve (2002). An anisotropic function corrects
for scattering effects from snow in non-forested regions. Slope and
aspect used in the correction is derived from the Global 30 Arcsecond
(GTOPO30) digital elevation model (DEM). Daily snow albedo is pro-
duced in 500 m grid cells for cloud-free conditions from the best single
daily observation, which is determined by an algorithm that ingests
illumination and satellite view angles, in addition to cloud mask and
fractional snow cover (Hall et al., 2002). MODIS Aqua Collection Six
includes the Quantitative Image Restoration (Gladkova et al., 2011)
technique that restores band 6 data (1628–1652 nm) to scientific qual-
ity. MODIS Terra and Aqua daily snow albedo is stored as unsigned 8-bit.
Cloud cover and other ancillary data are assigned values between 101
and 254. We analyzed the MODIS basic Quality Assessment (QA) for
each albedo grid cell and retained only high quality data for subsequent
analysis. Terra data from 2000 to 2019 exist with the exception of days
of year (doy) 219–230 in 2000 (middle of August). Aqua includes data
from July 2002 to the end of 2019 with 10 days missing between doy
```

**Table 1**  
The 17 glaciated regions considered in this study. The region number corre-  
sponds to those in Fig. 1. Median elevation was calculated from USGS bare earth  
digital elevation resampled to 500 m grid cells that intersected each region.  
Polygons are individual glaciers as defined in RGI 01 and RGI 02.

```
Region
Number
```

```
Region
Name
```

```
Area
(km^2 )
```

```
Polygons Median
Elevation
(m)
```

```
MODIS
Albedo
Grids Cells
August
1 St. Elias,
Wrangle
```

```
43,854.96 5011 1794.8 223,
```

```
2 Alaska
Range
```

```
11,305.92 3166 1661.7 61,
```

```
3 Chugach 11,801.96 2326 1287.7 62,
4 Aleutians 1391.97 326 1138.0 7071
5 North Slope 329.73 461 1852.7 2435
6 North Coast 15,503.83 5401 1623.6 75,
7 Central
Coast
```

```
1509.74 1938 1664.1 7255
```

```
8 South Coast 7050.05 3471 2043.9 29,
9 Vancouver
Island
```

```
11.41 32 1599.6 55
```

```
10 NWT/Yukon
Interior
```

```
525.19 571 2080.8 3545
```

```
11 Northern
Interior
```

```
520.59 719 1899.3 2616
```

```
12 Southern
Interior
```

```
1882.53 1705 2414.0 8098
```

```
13 Northern
Rockies
```

```
403.11 414 2223.4 2042
```

```
14 Central
Rockies
```

```
408.04 325 2336.2 1824
```

```
15 Southern
Rockies
```

```
1308.65 938 2633.5 5671
```

```
16 US Coast 405.87 563 2010.5 1876
17 US Interior 65.36 115 3324.4 496
```

209 and 220 in 2003. The last three days of July and the first seven days  
of August 2002 are also missing from the Aqua albedo data.  
MODIS broadband albedo (MCD43A3) for seven discrete bands be-  
tween 459 nm and 2155 nm was used to build broadband profiles of

```
snow and ice across five years that varied between high and low
amounts of aerosol optical depths. MODIS broadband albedo, MCD43A
version 6, is produced from data originating from both Aqua and Terra
platforms. MCD43A3, produced at 500 m (m) resolution, uses 16 days of
Terra and Aqua MODIS data, temporally weighted to the ninth day, to
produce a daily product. A white-sky albedo (bi-hemispherical reflec-
tance) and black-sky albedo (directional hemispherical reflectance) are
produced for local solar noon. Both albedo products are produced in the
visible and near infrared (VNIR) and short-wave infrared (SWIR) por-
tions of the spectrum, which corresponds to MODIS bands 1 through 7.
Simplified, quality layers for the albedo products are also provided for
the MODIS MCD43A3 data. All albedo (snow and spectral) data were
processed using the MODIS Reprojection Tool to produce images in
North American Equidistant Conic in the NAD 1983 datum.
Others evaluated the accuracy of MOD10A1 and MCD43A3 collec-
tion 5 albedo through comparison with field measurements. On the
Greenland Ice Sheet Stroeve et al. (2006) found the comparison between
MOD10A1 and MCD43A3 to be within ±7%. In the St. Elias Mountains,
a variety of glaciated terrain was found to be within ±6% (Williamson
et al., 2016) with little difference expressed between black-sky, white-
sky and snow albedo. Ryan et al. (2017) found that surface-based albedo
measurements made on the Greenland Ice Sheet overestimate MOD10A
(Collection 6) albedo by up to 10% for bare ice surfaces during the
summer melt season. This overestimation is because meteorological
station footprints poorly represent within grid cell albedo variability,
due to the under-sampling of meltwater. Sensor degradation is a likely
source of MODIS Terra albedo values being too low (Polashenski et al.,
2015; Casey et al., 2017) and the resulting albedo trends obtained for the
Greenland Ice Sheet of 0.01 decade^1 are close to the sensor calibration
limit. Sensor degradation issues found in the collection 5 albedo data
have been corrected in collection 6 (Casey et al., 2017).
```

```
3.2.Aerosol optical depth
```

```
MODIS Terra (MOD08_M3) and Aqua (MYD08_M3) monthly global
aerosol product (mean of daily mean corrected optical depths over land
```

## at 0.55 μm - layer 37) were used to identify the amount of forest fire

```
generated aerosol. This monthly average aerosol product has a spatial
resolution of 1◦latitude by 1◦longitude. MODIS Terra data is available
from February 1, 2000 to present, and MODIS Aqua data is available
from July 1, 2002 to present. All grid cells that covered the 17 glaciated
regions were retained for analysis and were averaged to determine a
single monthly aerosol optical depth for each region. The MODIS Aqua
and MODIS Terra aerosol data for each region were averaged. The
average difference between Aqua and Terra aerosol values for the five
regions in British Columbia over the course of the study period ranged
between approximately 5 – 15%. The grid cell that covered the highest
elevation portion of the St. Elias Mountains contained no aerosol optical
depth data over the period of study.
```

```
3.3.ERA5 land 2 m air temperature
```

```
Summer temperature represents a major potential driver of albedo
change. The lack of long term and widely distributed monitoring sta-
tions at glacier elevation in western Canada (Hik and Williamson, 2019)
prevents the use of environmental variables collected at discrete loca-
tions. Instead, two metre air temperature was obtained from the ERA
Land reanalysis product (Mu ̃noz Sabater, 2019). We used the monthly
average ERA5 Land air temperature produced at 9 km grids (https://c
limate.copernicus.eu/climate-reanalysis). The ERA5 Land grids that
cover the glaciated area with the 17 regions, for the months of June, July
and August, were aggregated into averages for each of the 17 regions.
```

```
3.4.Methods
```

```
MODIS Terra MOD10A1 daily snow albedo originating within the
```

**Fig. 2.** Comparison of MODIS daily snow albedo, version 6, captured by Terra  
and Aqua satellites between 2003 and 2019. The points are the monthly av-  
erages of all available albedo data for each of the Central and South Coast,  
Southern Interior, Central and Southern Rockies. Panel A shows the linear  
regression of the pooled data. Panel B shows the MODIS albedo difference  
between Terra and Aqua (MOD - MYD). The slopes of the ensemble time series  
and time series by individual region are all negative, but none are statistically  
significant at the _p <_ 0.05 level. This result suggests that MODIS Terra albedo  
trends likely conservative estimates of albedo decline as Aqua albedo has  
declined more than that from Terra. The differences by region span 0.0012 to  
0.046% a^1. The ensemble difference is 0.018% a^1. (For interpretation of  
the references to colour in this figure legend, the reader is referred to the web  
version of this article.)

month of August were averaged for each grid cell inside of RGI 1 and 2  
glacier outlines. The average albedo excluded cloud cover and daily  
values that were flagged as poor quality. The glaciated regions in  
western North America can have glaciers in deeply incised valleys where  
shadowing by steep rock walls will cause an artificial albedo reduction  
for the shadowed MODIS grid cells. Clouds and dry snow can display a  
similar albedo but are difficult to differentiate with satellite reflectance  
(Stillinger et al., 2019). To reduce bias due to misclassified clouds and  
snow, we compared the MODIS daily albedo product against the typical  
ranges for glacier snow and ice albedo (Cuffey and Paterson, 2010).  
Albedo values _\>_ 0.99 for snow or glacier ice and were excluded and al-  
bedo values _<_ 0.05 were considered influenced by shadow and were  
excluded. Monthly albedo was also aggregated by an equal weighted  
average for each of the 17 regions. The 500 m MODIS albedo grid cells

```
within the RGI glacier outlines were assigned elevations from the USGS
bare earth digital elevation model which was resampled by cubic
convolution to the MODIS 500 m grid cells spacing from the native 90 m.
Each albedo grid cell was also assigned the median elevation from the
intersecting RGI glacier polygon. MODIS Aqua albedo data for five of the
17 regions in British Columbia was processed and aggregated using the
same method as Terra albedo and was used as an independent check on
MODIS Terra trends.
The non-parametric Mann-Kendall correlation estimate and p -value
for the 20 year albedo time series was calculated for each glaciated grid
cell and for the aggregated region (Hipel and McLeod, 1994). The Sen’s
slope estimate and p -value was calculated at the native MODIS grid cell
spacing of 500 m and for each region (Sen, 1968). The minimum number
of values in the time series required for the Mann-Kendall analysis was
```

**Fig. 3.** Anomaly plots for Albedo, ERA temperature and AOD, where individual years are subtracted from the 20 year average for each region. August average  
MOD10A1 albedo 2000 to 2019 time series (Panel A) for the 17 regions using all grid cells. Panel B displays the June, July and August average ERA5 Land 2 m air  
temperature time series. Panel C displays the June, July and August average MODIS aerosol optical depth time series.

set to four; Sen’s analysis required an unbroken time series, which  
constitutes a data reduction of approximately 20%. We calculated the  
Mann-Kendall slope estimate and _p_ -values for the 17 regions. Our  
analysis aims to determine the effect of aerosol load on grid cells that are  
not subject to the influence of rock debris or glacier wasting commonly  
found in the ablation area. To evaluate the importance of transient

```
snowline change on affecting changes in albedo, we completed addi-
tional trend analysis for areas that lie 100 m below, within or above
(100 m) the median elevation of a given glacier. Trends were calculated
for albedo grid cells in three groups: 100 m below glacier median
elevation, ±100 m of median elevation and 100 m above glacier median
elevation. Trends for these three groups were further subdivided into
pure snow and ice and edge effected. We define grid cells that are
exclusively snow and ice as those which are completely surrounded by
albedo grid cells, thus removing any edge effects.
Multiple linear regression of August albedo versus June, July and
August (JJA) average ERA5 2 m air temperature plus MODIS JJA
average aerosol optical depth was conducted by region to determine if
forest fire generated aerosols have an influence on glacier albedo. Re-
gressions were conducted exclusively for grid cells that were identified
as being without edge effects in order to minimise albedo decline related
to snow and ice area reductions. Ordinary least squares (OLS) regression
is predicated on the model residuals being normally distributed and
displaying constant variance (homoscedasticity). The normal distribu-
tion of the residuals is evaluated with a Shapiro-Wilk test and changes in
variance are evaluated with a Breusch-Pagan test. Outlier residuals,
which might unduly influence an OLS, are evaluated graphically with
Cook’s Distance. Dominance Analysis (Azen and Budescu, 2003) is used
to evaluate the importance of each independent variable in the multiple
regression. If residuals failed any of the tests for a region, albedo was
subjected to a log10 or inverse transformation.
The Central and Southern rocky mountains (Fig. 1) were identified as
locations where AOD might have an above average influence on glacier
albedo because of the frequent and large forest fires in the interior of
British Columbia and the predominant westerly air flow. We use this
subset of the study area to analyse MCD43A3 broadband albedo data in
relation to forest fire proximity using the transport and dispersion
modelling using the HYSPLIT trajectory model (https://www.ready.
noaa.gov/HYSPLIT_traj.php) (Stein et al., 2015). Others used the HYS-
PLIT model to track forest fire generated aerosols (Barnaba et al., 2011).
```

**Fig. 4.** August normalised amount of albedo grid cells which are not statisti-  
cally significant (ns), statistically significant displaying a negative trend (sn)  
and statistically significant displaying a positive correlation (sp) to the 2000 to  
2019 time series. Statistical significance is determined using the Mann-Kendall  
test with a _p_ -value of _<_ 0.05.

**Table 2**  
August Sen’s slope (% a^1 ) estimate of MODIS average regional albedo. Bold  
values indicate slope estimates are statistically significant at the _p <_ 0.05 level.  
Average albedo is computed using all valid albedo values within a region. Edge  
effects include grid cells which are not completely surrounded by other grid  
cells. Snow and ice grid cells are completely surrounded by MODIS Grid cells.  
These two classifications were further categorised as 100 m below the glacier’s  
median elevation ( _<_ Median), within 100 m of the median elevation (Median) or  
100 m above the glacier’s median elevation ( _\>_ Median). Areas 9 and 17 (Van-  
couver Island and the United States Rockies) did not contain un-interrupted  
snow and ice grid cells.

```
Region Edge Effects Snow &amp; Ice
&gt; Median Median &lt; Median &gt; Median Median &lt; Median
1 0.28 ¡0.45 ¡0.26 0.16 ¡0.36 0.
2 0.20 0.47 0.23 0.11 0.53 ¡0.
3 0.25 ¡0.61 ¡0.39 0.08 ¡0.36 0.
4 0.08 0.25 0.24 0.00 0.21 0.
5 0.24 0.06 0.07 0.08 0.07 ¡0.
6 ¡0.51 ¡0.71 ¡0.59 ¡0.27 ¡0.71 ¡0.
7 ¡0.44 ¡0.47 ¡0.42 ¡0.45 ¡0.57 ¡0.
8 ¡0.42 0.48 ¡0.44 ¡0.35 ¡0.54 0.
9 0.40 0.42 0.36 NA NA NA
10 0.46 0.45 0.25 0.54 ¡0.68 ¡0.
11 ¡0.76 ¡0.79 ¡0.52 ¡0.90 ¡1.26 ¡0.
12 0.29 ¡0.31 ¡0.23 ¡0.42 0.53 0.
13 0.49 0.53 0.45 0.51 0.67 ¡0.
14 ¡0.43 ¡0.57 ¡0.36 ¡0.53 ¡0.85 0.
15 0.25 ¡0.34 0.22 0.21 0.36 0.
16 0.13 0.11 0.09 0.22 0.14 0.
17 0.18 0.15 0.12 NA NA NA
```

```
Fig. 5. Annual area of forest fires compared to JJA average aerosol optical
depth displayed as log10. The two regions in the southern United States have
been omitted. The area burned includes for the northern regions (regions 1 – 6)
is the sum of Alaska and Yukon, where the remaining regions use the forest fire
area burned for British Columbia. The extreme values for AOD, which are &gt; 0.3,
typically occur when the burned area is greater than 10,000 km^2.
```

Air parcel trajectories were modelled using three simultaneous ensem-  
bles every 12 h in the forward direction using North American Regional  
Reanalysis meteorology for the month of August 2015. The ensemble  
trajectories were converted to polygons and displayed at 80% opacity  
which produces a darker colour for overlapping trajectory polygons.  
Broadband albedo (MCD43A3) was used to analyse the potential influ-  
ence of AOD on glacier albedo. The MCD43A3 broadband albedo data  
was filtered for the number of surrounding grid cells and by relation to  
glacier median elevation as was done for MOD10A1. Investigation of the  
simplified quality layer indicates that ~10% of the valid albedo values  
were the highest quality full BRDF inversions and the remainder was the  
magnitude BRDF inversions (Schaaf et al., 2002). The data reduction  
caused by the full BRDF inversion eliminated data entirely in some re-  
gions. The analysis of MCD43A3 was conducted using all of the full and  
magnitude BRDF inversions for black-sky albedo.

**4\. Results**

_4.1.Albedo validation_

Albedo from Aqua and Terra MODIS sensors strongly correlate with a  
root mean squared error (RMSE) of 0.97% (Fig. 2) for five of the 17  
regions in the Study area. When regressed against year, the percent  
difference per year (Terra minus Aqua) is 0.0012 to 0.046% a^1 with  
a mean difference of 0.018% a^1 , indicating that Aqua albedo is  
declining faster than that from Terra. The regressions were not statisti-  
cally significant, indicating that calibration drift of the MODIS sensor on  
the Terra platform is negligible in relation to the MOD10A1 product.

```
4.2.Regional changes
```

```
We present anomalies of August albedo, JJA ERA temperature and
JJA AOD subtracted from a region’s average value. Glacier albedo for
the 17 regions declined over the study period (Fig. 3A), and these de-
clines are characterized by large inter-annual variability. JJA average
ERA 5 Land 2 m air temperature aggregated by region shows pro-
nounced inter-annual variability (Fig. 3B). An increase in air tempera-
ture occurred for most regions, but the average temperature varies
depending on latitude, elevation and proximity to the Pacific Ocean. The
JJA-averaged time series of Terra and Aqua averaged MODIS aerosol
optical depth aggregated by region ranges from 0.09 and 0.22 for years
with little forest fire activity (Fig. 3C). During years of heightened fire
activity monthly aerosol optical depth values reaches 0.4 to 0.9, which
elevated the JJA AOD averages to greater than 0.2. Trends in albedo
vary in sign and significance ( p &lt; 0.05) for the different regions (Figs. 1
and 4). We also evaluated albedo change for pure snow and ice grid cells
unaffected by marginal retreat along the edges of glaciers (Table 2).
These changes in albedo are largely negative and range between 0.19 to
1.26% a^1 , and eight regions showed statistically significant declines.
The negative trends were 10 to 100 times larger than the slope of the
MODIS Terra minus Aqua validation curve.
```

```
4.3.Albedo relationship with forest fires, AOD and air temperature
```

```
The relation between area burned and JJA AOD is non-linear (Fig. 5).
Glacier albedos in Alaska were compared to Alaska forest fire area;
glacier albedo in the Yukon and NWT were compared to the sum of
forest fire areas from Alaska and the Yukon; glacier albedo in British
Columbia and Alberta were compared to British Columbia forest fire
```

**Table 3**  
Multiple linear regression correlation coefficients and slope estimates for August average albedo and JJA averages of temperature plus aerosol optical depth for snow  
and ice grid cells in three elevation classifications, 100 m above median elevation, within 100 m of median elevation and less than 100 below median elevation.  
Estimates with a _p_ -value of less than 0.05 are indicated in bold. Regions 10 and 17 contained no interior cells (i.e., those surrounded by other albedo grid cells) and  
subsequently removed from analysis. Dominance Analysis (DA) shows the correlation coefficient for temperature and AOD for each region. Regions 4 and 6 albedo data  
were transformed by log 10 to make the regression residuals normally distributed, with the exception of region 6 greater than median, which was transformed using an  
inverse function. NA values represent regions where regression residuals could not be transformed to a normal distribution.

```
Region Variable &gt; Median Median &lt; Median
Adj R^2 Estimate DA R^2 Adj R^2 Estimate DA R^2 Adj R^2 Estimate DA R^2
1 t 0.72 ¡3.08 0.54 0.64 ¡3.96 0.51 0.51 ¡2.99 0.
aod 2.13 0.21 0.40 0.17 1.52 0.
2 t 0.76 ¡2.86 0.47 0.53 ¡3.98 0.39 0.45 ¡2.33 0.
aod 18.26 0.32 9.52 0.19 0.55 0.
3 t 0.85 ¡1.52 0.47 0.65 ¡1.63 0.39 0.18 2.01 0.
aod ¡20.38 0.39 ¡20.34 0.3 2.61 0.
4* t 0.14 0.12 0.22 0.12 0.13 0.19 0.07 2.13 0.
aod 0.33 0.01 0.90 0.02 35.83 0.
5 t NA NA NA 0.7 ¡5.88 0.7 0.003 0.31 0.
aod NA NA 26.83 0.02 28.32 0.
6* t 0.36  0.15 0.4 0.31 0.21 0.31 0.53 ¡3.51 0.
aod 0.47 0.04 0.27 0.07 6.08 0.
7 t 0.6 ¡2.39 0.53 0.62 ¡2.89 0.56 0.69 ¡4.52 0.
aod 14.45 0.11 14.87 0.1 20.22 0.
8 t 0.78 ¡1.91 0.59 0.7 ¡2.89 0.58 0.08 1.00 0.
aod 11.27 0.22 10.15 0.15 32.48 0.
10 t 0.62 ¡5.88 0.58 0.74 ¡8.79 0.69 0.36 ¡5.06 0.
aod 1.03 0.09 7.27 0.08 15.41 0.
11 t NA NA NA 0.65 ¡6.86 0.54 0.5 ¡3.84 0.
aod NA NA 45.96 0.15 9.35 0.
12 t 0.77 ¡1.92 0.36 0.73 ¡2.36 0.36 0.18 1.95 0.
aod ¡35.84 0.43 ¡40.26 0.39 56.21 0.
13 t 0.7 ¡5.91 0.63 0.68 ¡6.55 0.57 0.44 ¡4.86 0.
aod 4.59 0.1 20.33 0.14 9.38 0.
14 t 0.72 ¡3.23 0.41 0.65 ¡4.04 0.39 0.54 ¡2.66 0.
aod ¡30.62 0.34 ¡35.21 0.3 21.16 0.
15 t 0.62 0.96 0.13 0.65 0.03 0.19 0.12 1.33 0.
aod ¡63.89 0.53 ¡65.54 0.5 24.41 0.
16 t 0.56 ¡2.53 0.53 0.45 ¡2.93 0.45 0.06 1.01 0.
aod 0.61 0.08 5.02 0.06 17.38 0.
```

areas. There is a notable increase in AOD for forest fire areas larger than  
~10,000 km^2 (Fig. 5). Typical JJA average aerosol optical depths are  
_<_ 0.2 (Figs. 3C and 5), and severe forest fire years (forest fire area _\>_  
10,000 km^2 ) display JJA AOD values _\>_ 0.4, with a monthly value  
sometimes exceeding 0.8. Forest fire data including area burned for  
Alaska was obtained from the Alaska Wildland Fire Information page  
(https://akfireinfo.com/) and for Canada from the Canadian Wildland  
Fire Information System (https://cwfis.cfs.nrcan.gc.ca/).  
Multiple linear regressions for August albedo versus average June,  
July and August (JJA) temperature +JJA average AOD for snow and ice  
grid cells shows statistically significant correlations to temperature for  
most regions and the southern coast and interior regions of British  
Columbia and Alberta; the Chugach region of Alaska show statistically  
significant correlations to aerosol optical depth (Table 3). The strong  
correlation coefficients indicate that for 13 of the 15 regions, 45% to  
78% of the albedo time series variation in pure snow and ice grid cells at  
the glacier median elevation is described by the combination of AOD  
and temperatures. Dominance analysis of the multiple regression for  
each region indicates that temperature is approximately 2 – 6 times more  
predictive of albedo variation than is AOD. The Southern Interior and  
Southern Rockies are anomalies in that these regions show a greater  
dependence on AOD than on temperature.  
We present a special case where we employ a natural experiment to  
attribute forest fire generated aerosol to glacier albedo decline (Figs. 6-  
8). Fig. 6 shows the annual area of forest fires (British Columbia total)  
compared to JJA average aerosol optical depth for the Central Rockies  
(CR) and Southern Rockies (SR) for the years 2015, 2016 and 2018. Over  
the two regions, 2018 (2016) displayed high (low) AOD and forest area  
burned. There is a large difference in AOD between years and between  
regions in 2015. In 2015 the CR region displayed a background level of  
_<_ 0.2, and the SR region showed an elevated AOD value. The elevated

```
2015 JJA average AOD value in the SR is the result of high August AOD
(0.54), where June and July remained near or below 0.2.
In August 2015 forest fires in British Columbia were burning in the
south of the province ~300 km south of the centroid of the Southern
Rockies and in close proximity to the Pacific Ocean approximately 150
km north west of Vancouver, British Columbia. The fires close to the
Pacific were suppressed by the second last week of August, which the
others in the south east burned into the autumn. Air parcel trajectory
tracking using the Hysplit model for the month of August 2015 with
origin for the south east fires (49◦N; 117◦W) and Pacific fires (50◦N;
123 ◦W) shows that the majority of air parcels traversed the Southern
Rockies but not the Central Rockies (Fig. 7). This result indicates that the
elevated AOD value in the Southern Rockies is consistent with forest fire
smoke.
We also analyzed the black-sky broadband albedo (MCD43A3) for
the years 2015, 2016 and 2018 for the Central and Southern Rockies
(Fig. 8). Broadband albedo shows declines in the visible region of the
spectrum during the large forest fire year of 2018. In the Central Rockies
the years with low AOD (2015 &amp; 2016) values show the highest albedo
in the visible portion of the spectrum. In the Southern Rockies the
highest albedo in the visible portion of the spectrum was in 2016, and
the 2015 and 2018 visible albedo was reduced by 20%. The 2015 JJA
average temperature for the CR was 10.1 ±1.0 ◦C (one standard devi-
ation) and was 10.2 ±1.0 ◦C for the SR. The August average temperature
of the SR was 0.5 ◦C higher than the CR.
```

**5\. Discussion**

```
Analysis of the collection six MODIS Terra albedo time series
required comparison to the MODIS Aqua albedo to determine if cali-
bration drift identified in collection five is occurring (Polashenski et al.,
2015; Casey et al., 2017). Our results indicate that MODIS Terra albedo
trends are conservative estimates of albedo decline compared to those
derived from MODIS Aqua. The comparison of albedo data collected by
MODIS Aqua and Terra is complicated by differences in view angles,
solar zenith angles and diurnal changes in albedo that is not necessarily
symmetrical around solar noon (Manninen et al., 2020) and the relative
calibration differences between MODIS sensors. MODIS snow albedo
processing includes adjustment for slope aspect and solar zenith angle
using a global digital elevation model (Klein and Stroeve, 2002).
Detecting trends in MODIS albedo at the regional-to-glacier scale is
hampered by several factors that relate the nature of glaciers undergoing
rapid area and mass loss. Glacier area is declining at different rates
regionally. The use of static glacier outlines provided by the RGI outlines
could also introduce errors to edge effected albedo because low albedo
ground previously covered by ice emerges at different rates throughout
the study area. The result is a lowering of surface albedo, which is in-
dependent of the snow and ice albedo reduction associated with a
forcing from temperature increase or forest fire aerosol deposition. The
use of MODIS albedo grid cells completely surrounded by other MODIS
albedo grid cells should largely mitigate the edge effects on albedo
trends. This filtering technique reduces the number of grid cells avail-
able for analysis and omits two areas (Vancouver Island and the US
Rockies) because no grid cells are present which are completely sur-
rounded by other MODIS snow and ice grid cells.
Temperature-mediated snow grain size change and aerosol deposi-
tion (dust and black carbon) are expected to be the primary drivers for a
reduction of snow albedo over glaciers (e.g., Cuffey and Paterson, 2010).
The influence of dust or black carbon in albedo reduction has been
shown to have a regional dependence (Skiles and Painter, 2017;
Nagorski et al., 2019; Kaspari et al., 2020; Rahimi et al., 2020), however,
when high levels of aerosolized black carbon are deposited on glaciers
these tend to be the most influential in albedo reduction. The analysis of
the glacier area above median elevation for each of the 17 regions
provides some insight into the drivers of albedo change. The observed
albedo decline in the majority of regions correlates with increasing
```

**Fig. 6.** Annual area of forest fires compared to JJA average aerosol optical  
depth displayed as log 10. The Central Rockies (CR) and Southern Rockies (SR)  
regions are compared to the amount of annual area burned by wildfires in the  
Province of British Columbia. The years 2015, 2016 and 2018 have been spe-  
cifically identified for comparison to broadband albedo (MCD43A3). There is a  
large difference in AOD values in 2015, where the CR region displays a back-  
ground level of _<_ 0.2 and the SR region shows elevated AOD values. The  
elevated 2015 JJA average AOD value is the result of high August AOD, where  
June and July remained near or below 0.2.

summer temperatures. There is a broad range of absolute temperature  
values depending on the elevation, latitude and proximity to the Pacific  
Ocean, however. For example, between the years 2000 and 2017 Wil-  
liamson et al. (2020b) found no trend in the summer albedo at high  
elevation in the St. Elias Mountains ( _\>_ 5000 m asl). Although air tem-  
perature is rapidly increasing at high elevation, the absolute tempera-  
ture is below 15 ◦C which limits the amount of snow crystal  
roughening and melting (e.g., Libbrecht, 2005) and explains the flat  
albedo trend. The lack of statistically significant albedo change above  
the median elevation in the St. Elias, Wrangles and the Alaska Range is  
therefore expected.  
Light absorbing particles reduce the spectral albedo of snow in the  
visible and near infrared portions of the electromagnetic spectrum  
(Warren, 2013; Petzold et al., 2013). Black sky albedo for the Central  
and Southern Rockies decreases in the VNIR for years with large burned  
areas and high AOD values (Fig. 8). The magnitude of the decline in  
VNIR is consistent with the surface presence of black carbon (Warren,  
2013; Hadley and Kirchstetter, 2012). An increase in grain size often  
coincides with an increase in temperature due to temperature-related  
snow metamorphism and these changes can decrease albedo in the  
visible and NIR portions of the spectrum by up to 10% (e.g., Adolph  
et al., 2017). Diffuse beam albedo declines in the visible portion of the  
spectrum, especially for coarse-grained snow (Warren and Wiscombe,  
1980), are more dependent on snow impurities than grain size (Gardner  
and Sharp, 2010), however. The influence of aerosol deposition is not

```
uniformly distributed in the study region. VNIR albedo for the Central
Rockies is lower and varies less compared to the Southern Rockies,
where the large difference in VNIR albedo clearly discriminates between
extreme and negligible fire years (Fig. 8).
The largest negative trends in August albedo are found within 100 m
of the median elevation. The most parsimonious explanation for this
trend is a coincident rise in the transient snow line over the period
2000 – 2019. Any increase in snowline over the historical average is a
strong indicator of negative surface mass balance (e.g., Braithwaite,
1984). An example of the spatial trends of Sen’s slope estimates is pro-
vided for the Klinaklini Glacier in the Southern Coast Mountains, British
Columbia (Fig. 9A). The grid cells with the largest slope declines are 50
m to 200 m below the glacier’s median elevation. Landsat images of the
Klinaklini Glacier are shown panel B (August 27, 2002 - Landsat 5) and
panel C (August 7, 2018 - Landsat 8). The high elevation snow and low
elevation glacier ice both show albedo declines.
Our findings are consistent with the increasing negative mass bal-
ance measurements that have been recorded for many locations within
the study area (Menounos et al., 2019; Yang et al., 2020; Zemp et al.,
2019; Berthier et al., 2010; Schiefer et al., 2007; Hugonnet et al., 2021).
Shifts in the upper level atmospheric circulation have been shown to
influence glacier mass balance in western North America (Menounos
et al., 2019). The increase in albedo, both regionally and at the grid cell
level, for the US Rockies (region 17 of this study) is consistent with the
neutral-to-slightly positive glacier mass balance within the US Glacier
```

```
Fig. 7. Hysplit ensemble air parcel trajectories generated for the
month of August 2015, every 12 h from two points. The simulations
originate from the point (49◦N; 117◦W) which is between the two
largest forest fires burning in British Columbia in August. The
second point (50◦N; 123◦W) is close to the Pacific Ocean and the
two fires in this area burned until the middle of August. The tra-
jectories that intersect either the Central or Southern Rockies were
retained. The Southern Rockies are extensively covered by the
trajectories where the Central Rockies glaciers are much less tra-
versed. These simulations suggest or (imply) that the elevated AOD
values in the SR originate from the forest fires burning in southern
British Columbia in August.
```

National Park over the period 2010–2019 (Menounos et al., 2019).  
Additionally, this region consistently showed the lowest AOD values.  
Our regression analysis indicates that both temperature and AOD have a  
stronger effect on albedo above the median elevation than for those at or  
below for most regions. Only 56% to 85% of the albedo variation is  
described by temperature and AOD for 13 of the 15 regions above the  
median elevation. The imperfect description of albedo variation is likely  
the result of other influential factors such as summer snowfall. Albedo  
was poorly correlated to temperature and AOD for the glaciers in the  
Aleution Islands, indicating the albedo dynamics for this region is  
largely distinct from the rest of the study area. Dominance analysis in-  
dicates that the majority of variation in albedo is determined by tem-  
perature for most regions. The exception is the Southern Rockies, where  
AOD is considerably better able to predict albedo than is temperature.  
Glacier surfaces experience both fire and non-fire aerosol deposition,  
where dust is typically the major albedo reducing aerosol (Skiles and  
Painter, 2017). The exception is for severe fire years where above  
average black carbon aerosols are deposited (Kaspari et al., 2020;  
Marshall and Miller, 2020). The deposition rates of black carbon aero-  
sols are likely controlled by a suite of factors which include the eleva-  
tion, absolute temperature, predominant wind direction, proximity to

```
fire and aerosol load. The total amount of forest area burned regionally
predicts the amount of area burned at tree-line (Cansler et al., 2017),
which is typically the nearest aerosol and ash source to most mountain
glaciers. In Greenland there is little evidence for a large aerosol effect
caused by Canadian forest fire smoke aerosol deposition, even though
high daily AOD concentrations (e.g., &gt; 0.8) have been measured (e.g.,
Thomas et al., 2017; Polashenski et al., 2015). Elevated black carbon
concentrations compared to dust concentrations from the Combatant
Col ice core were attributed to the close proximity of forest fires and the
major urban area of Vancouver, Canada, which is 280 km from the ice
core site (Neff et al., 2012). Ash generation depends on the area burned,
fuel type and combustion completeness and deposition and is typically
heterogeneous in space and time (Bodí et al., 2014). An ice core
extracted from Mount Snow Dome, in the Canadian Rockies, and a
nearby ice cliff, both display a 1971 forest fire ash layer in the summer
melt layer (Donald et al., 1999). In-situ meteorological observation of
albedo in the upper portion of the ablation area on Haig Glacier (Ca-
nadian Rockies) shows the mean June, July and August albedo was 0.
```

## ±0.07 (± 1 σ) over the 2002 to 2017 period (Marshall and Miller, 2020).

```
During years of intense regional wildfire activity (such as large fires in
Alberta, Canada, in 2003 and 2017) the albedo of the debris-covered ice
declined from 0.21 ±0.06 to ~0.12. Within this context, the results
presented here suggest that proximity to forest fire and the area burned
both play an important role in determining the magnitude of the effect of
forest fire generated aerosols on glacier albedo. The heterogeneous na-
ture of forest fire particle deposition is consistent with the regional MLR
results, despite most regions experiencing elevated AOD periodically
throughout the study period. Identifying the influence of forest fire
aerosols on albedo change for glaciers requires a coordinated effort to
collect spectral albedo at different spatial scales in relation to field
sampling of black carbon and dust deposition at and around snowline.
The analysis conducted here predicts that short ice cores collected in the
accumulation zones throughout western North America will display a
geographic and elevation pattern of black carbon deposition. The strong
correlation between AOD and albedo decline for the Southern and
Central Rockies and Southern Interior and the Chugach region of Alaska
suggests that annual layers with substantially larger concentrations of
forest fire generated black carbon should be present when compared to
other regions in western North America. Layers should be particularly
evident in the Southern Rockies. Black carbon concentrations of 30 ng
g^1 of can reduce albedo by 2% and black carbon can be concentrated at
the surface in anomalously warm years with high AOD values (Warren,
2013). The &gt; 10% VNIR broadband albedo declines recorded for the
southern Rockies in 2017 and 2018 relative to years with much lower
fire activity should yield ice cores that contain aerosol layers that could
be as large as 150 ng g^1 of black carbon. However, the additive effect
on albedo decline resulting from temperature mediated snow grain in-
crease and black carbon and dust deposition makes a precise prediction
of ice core concentrations of black carbon from surface albedo difficult
(Warren and Wiscombe, 1980), especially because dust and black car-
bon are often found together on a glacier’s surface (e.g., Marshall and
Miller, 2020).
Wildfires are predicted to become larger and more frequent as a
consequence of projected temperature increase in western North
America (Flannigan et al., 2006; Soja et al., 2007). One of the conse-
quences of increased forest fire activity will be more frequent black
carbon aerosol loading on western North American glaciers, particularly
in south western Canada. The more frequent aerosol loading will in-
crease glacier melt and accelerate their decline.
```

**6\. Conclusions**

```
Over the period 2000–2019 the end of melt season albedo for glaciers
in western North America declined by 4 to 81%. Reduction in surface
albedo is primarily attributed to an increase in air temperature, but al-
bedo is also lowered for some regions during years characterized by
```

**Fig. 8.** MCD43A3 black-sky spectral albedo average over the last two weeks of  
August for the years 2015, 2016 and 2018. Albedo grid cells were selected from  
areas greater than 100 m above median elevation of a given glacier and sur-  
rounded by other MODIS grid cells. These selection criteria minimise contam-  
ination of snow grid cells by edge effect and debris cover. Comparison of Fig. 6  
shows that the highest AOD values occur in 2017 (JJA average values of ~0.  
and August values as high as ~0.8), which are the two years of the largest  
amount of area burned in British Columbia. The highest albedo values ( _\>_ 0.6)  
in the visible and near infrared portion of the spectrum occurred in 2016, when  
AOD values were low (JJA averages of _<_ 0.2). The SR and CR show a large  
difference in 2015 albedo, which corresponds to a difference in AOD values.  
Points are plotted for the middle value of the seven MODIS band widths.

pronounced wildfire activity. The importance of wildfire is illustrated by  
the negative relation between glacier albedo in the Chugach region of  
Alaska, the South Coast, Southern Interior and Central and Southern  
Rockies of Canada and aerosol optical depth, a strong proxy for black  
carbon deposition originating during the summer wildfire season. These  
results indicate a complex response of glacier mass balance to climate  
forcing with important feedback effects that will likely exacerbate mass  
loss for some regions in western North America in the decades ahead.

**Declaration of Competing Interest**

```
The authors declare no conflicting interests.
```

**Acknowledgements**

Financial and logistical support for this project was provided by the  
Tula Foundation and the National Sciences and Engineering Research  
Council of Canada and the Canada Research Chairs Program.

```
References
```

```
Adolph, A.C., Albert, M.R., Lazarcik, J., Dibb, J.E., Amante, J.M., Price, A., 2017.
Dominance of grain size impacts on seasonal snow albedo at open sites in New
Hampshire. J. Geophys. Res. Atmos. 122, 121–139.
Azen, R., Budescu, D.V., 2003. The dominance analysis approach for comparing
predictors in multiple regression. Psychol. Methods 8 (2), 129–148. https://doi.org/
10.1037/1082-989X.8.2.129.
Barnaba, F., Angelini, F., Curci, G., Gobbi, G.P., 2011. An important fingerprint of
wildfires on the European aerosol load. Atmos. Chem. Phys. 11, 10487–10501.
https://doi.org/10.5194/acp-11-10487-2011.
Berthier, E., Schiefer, E., Clarke, G., et al., 2010. Contribution of Alaskan glaciers to sea-
level rise derived from satellite imagery. Nature Geosci. 3, 92–95. https://doi.org/
10.1038/ngeo737.
Bodí, M.B., Martin, D.A., Balfour, V.N., Santín, C., Doerr, S.H., Pereira, P., Cerd`a, A.,
Mataix-Solera, J., 2014. Wildland fire ash: production, composition and eco-hydro-
geomorphic effects. Earth Sci. Rev. 130, 103–127.
Bøggild, C.E., Brandt, R.E., Brown, K.J., Warren, S.G., 2010. The ablation zone in
northeast Greenland: ice types, albedos and impurities. J. Glaciol. 56, 101–113.
Box, J.E., Fettweis, X., Stroeve, J.C., Tedesco, M., Hall, D.K., Steffen, K., 2012. Greenland
ice sheet albedo feedback: thermodynamics and atmospheric drivers. Cryosphere 6,
821 – 839. https://doi.org/10.5194/tc-6-821-2012.
Braithwaite, R.J., 1984. Can the mass balance of a glacier be estimated from its
equilibrium-line altitude? J. Glaciol. 30, 364–368.
Braithwaite, R., Raper, S., 2009. Estimating equilibrium-line altitude (ELA) from glacier
inventory data. Ann. Glaciol. 50 (53), 127–132. https://doi.org/10.3189/
172756410790595930.
```

**Fig. 9.** Spatial trends in Sen’s slope estimates for the Klinaklini Glacier (51.5◦N, 125.6◦W) in the Southern Coast Mountains (Region 8), British Columbia (Panel A).  
The non-parametric slope estimates are for the MOD10A1 albedo at 500 m grid cell spacing for the month of August between 2000 and 2019. Panel B shows a Landsat  
5 image from August 27, 2002 and panel C shows a Landsat 8 image from August 7, 2018. The largest declines in albedo slope in panel A are clearly related to upward  
movement of the August snow line.

Calluy, G.H.K., Bj ̈ornsson, H., Greuell, J.W., Oerlemans, J., 2005. Estimating the mass  
balance of Vatnaj ̈okull from NOAA-AVHRR imagery. Ann. Glaciol. 42, 118–124.  
Cansler, C.A., McKenzie, D., Halpern, C.B., 2017. Area burned in alpine treeline ecotones  
reflects region-wide trends. Int. J. Wildland Fire 25 (12), 1209–1220. https://doi.  
org/10.1071/WF16025.  
Casey, K.A., Polashenski, C.M., Chen, J., Tedesco, M., 2017. Impact of MODIS sensor  
calibration updates on Greenland ice sheet surface reflectance and albedo trends.  
Cryosphere 11, 1781–1795.  
Clarke, G., Jarosch, A., Anslow, F., et al., 2015. Projected deglaciation of western Canada  
in the twenty-first century. Nat. Geosci. 8, 372–377. https://doi.org/10.1038/  
ngeo2407.  
Cuffey, K.M., Paterson, W.S.B., 2010. The Physics of Glaciers, 4 th ed. Elsevier Science.  
De Ruyter de Wildt, M.S., Oerlemans, J., Bj ̈ornsson, H., 2002. A method for monitoring  
glacier mass balance using satellite albedo measurements: application to Vatnajokull ̈  
(Iceland). J. Glaciol. 48 (161), 267–278.  
Donald, D.B., Syrgiannis, J., Crosley, R.W., Holdsworth, G., Muir, D.C.G., Rosenberg, B.,  
Sole, A., Schindler, D.W., 1999. Environ\_.\_ Sci. Technol. 33, 1794–1798.  
Flanner, M.G., Zender, C.S., Randerson, J.T., Rasch, P.J., 2007. Present-day climate  
forcing and response from black carbon in snow. J. Geophys. Res. 112 (D11) https://  
doi.org/10.1029/2006JD008003.  
Flannigan, M.D., Stocks, B.J., Weber, M.G., 2006. Fire regimes and climatic change in  
Canadian forests. In: Veblen, T.T., et al. (Eds.), Fire and Climatic Change in  
Temperate Ecosystems of the Western Americas, vol. 160. Springer, New York,  
pp. 97–119.  
Gardner, A.S., Sharp, M.J., 2010. A review of snow and ice albedo and the development  
of a new physically based broadband albedo parameterization. J. Geophys. Res. 115,  
F01009 https://doi.org/10.1029/2009JF001444.  
Gladkova, I., Grossberg, M.D., Shahriar, F., Bonev, G., Romanov, P., 2011. Quantitative  
restoration for MODIS band 6 on Aqua. IEEE Trans. Geosci. Remote Sens. 50,  
2409 – 2416.  
Gleason, K.E., McConnell, J.R., Arienzo, M.M., Chellman, N., Calvin, W.M., 2019. Four-  
fold increase in solar forcing on snow in western US burned forests since 1999. Nat.  
Commun. 10 (1), 1–8.  
Greuell, W., Kohler, J., Obleitner, F., Glowacki, P., Melvold, K., Bernsen, E.,  
Oerlemans, J., 2007. Assessment of interannual variations in the surface mass  
balance of 18 Svalbard glaciers from the moderate resolution imaging  
spectroradiometer/Terra albedo product. J. Geophys. Res. 112 (D07105) https://  
doi.org/10.1029/2006JD007245.  
Hadley, O.L., Kirchstetter, T.W., 2012. Black carbon reduction of snow albedo. Nat. Clim.  
Chang. 2, 437–440.  
Hall, D.K., Riggs, G.A., Salomonson, V.V., DiGirolamo, N.E., Bayd, K.J., 2002. MODIS  
snow-cover products. Remote Sens. Environ. 83, 181–194.  
Hanes, C.C., Wang, X., Jain, P., Parisien, M.-A., Little, J.M., Flannigan, M.D., 2018. Fire-  
regime changes in Canada over the last half century. Can. J. For. Res. 49 (3),  
256 – 269. https://doi.org/10.1139/cjfr-2018-0293.  
Hik, D.S., Williamson, S.N., 2019. Need for mountain weather stations climbs. Science  
366 (6469), 1083.  
Hipel, K.W., McLeod, A.I., 1994. Time Series Modelling of Water Resources and  
Environmen-tal Systems. Elsevier Science, New York.  
Hugonnet, R., McNabb, R., Berthier, E., Menounos, B., Nuth, C., Girod, L., Farinotti, D.,  
Huss, M., Dussaillant, I., Brun, F., K ̈a ̈ab, A., 2021. Accelerated global glacier mass  
loss in the early twenty-first century. Nature 592, 726–731.  
Kaspari, S.D., Pittenger, D., Jenk, T.M., Morgenstern, U., Schwikowski, M., Buenning, N.,  
Stott, L., 2020. Twentieth century black carbon and dust deposition on South  
Cascade Glacier, Washington State, USA, as reconstructed from a 158-m-long ice  
core. J. Geophys. Res.-Atmos. 125 https://doi.org/10.1029/2019JD  
e2019JD031126.  
Klein, A.G., Stroeve, J., 2002. Development and validation of a snow albedo algorithm  
for the MODIS instrument. Ann. Glaciol. 34, 45–52.  
Libbrecht, K.G., 2005. The physics of snow crystals. Rep. Prog. Phys. 68, 855–895.  
Manninen, T., J ̈a ̈askel ̈ainen, E., Riihel ̈a, A., 2020. Diurnal black-sky surface albedo  
parameterization of snow. J. Appl. Meteorol. Climatol. 59, 1415–1428. https://doi.  
org/10.1175/JAMC-D-20-0036.1.  
Marshall, S.J., Miller, K., 2020. Seasonal and interannual variability of melt-season  
albedo at Haig glacier, Canadian Rocky Mountains. Cryosphere 14 (3249–3267),

Menounos, B., Hugonnet, R., Shean, D., Gardner, A., Howat, I., Berthier, E., Pelto, B.,  
Tennant, C., Shea, J., Myoung-Jong, Noh, Brun, F., Dehecq, A., 2019. Heterogeneous  
changes in Western North American glaciers linked to decadal variability in zonal  
wind strength. Geophys. Res. Lett. 46, 1 (200-209).  
Mu ̃noz Sabater, J., 2019. ERA5-Land monthly averaged data from 1981 to present. In:  
Copernicus Climate Change Service (C3S) Climate Data Store (CDS). https://doi.org/  
10.24381/cds.68d2bb30 ( _<_ January 2, 2021 _\>_ ).  
Nagorski, S.A., Kaspari, S.D., Hood, E., Fellman, J.B., Skiles, S.M.K., 2019. Radiative  
forcing by dust and black carbon on the Juneau Icefield, Alaska. J. Geophys. Res.  
Atmos. 124, 3943–3959.  
Neff, P., Steig, E., Clark, D., McConnell, J., Pettit, E., Menounos, B., 2012. Ice-core net  
snow accumulation and seasonal snow chemistry at a temperate-glacier site: mount  
Waddington, Southwest British Columbia, Canada. J. Glaciol. 58 (212), 1165–1175.  
https://doi.org/10.3189/2012JoG12J078.  
Petzold, A., Ogren, J.A., Fiebig, M., Laj, P., Li, S.-M., Bal-tensperger, U., Holzer-Popp, T.,  
Kinne, S., Pappalardo, G., Sug-imoto, N., Wehrli, C., Wiedensohler, A., Zhang, X.-Y.,

2013.  Recommendations for reporting “black carbon” measurements. Atmos. Chem.  
    Phys. 13, 8365–8379. https://doi.org/10.5194/acp-13-8365-2013.  
    Pfeffer, W., Arendt, A., Bliss, A., Bolch, T., Cogley, J., Gardner, A., Sharp, M., 2014. The  
    Randolph glacier inventory: a globally complete inventory of glaciers. J. Glaciol. 60  
    (221), 537–552. https://doi.org/10.3189/2014JoG13J176.  
    Platnick, S., et al., 2015. Greenbelt, MD, USA, \[online\]. Available: [http://dx.doi.](http://dx.doi./)  
    org/10.5067/MODIS/MOD06\_L2.006.  
    Polashenski, C.M., Dibb, J.E., Flanner, M.G., Chen, J.Y., Courville, Z.R., Lai, A.M., et al.,
2014.  Neither dust nor black carbon causing apparent albedo decline in Greenland’s  
    dry snow zone implications for MODIS C5 surface reflectance. Geophys. Res. Lett.  
    42, 9319–9327.  
    Qian, Y., Yasunari, T.J., Doherty, S.J., Flanner, M.G., Lau, W.K.M., Ming, J., et al., 2015.  
    Light-absorbing particles in snow and ice: measurement and modeling of climatic  
    and hydrological impact. Adv. Atmos. Sci. https://doi.org/10.1007/s00376-014-  
    0010-0.  
    Rahimi, S., Liu, X., Zhao, C., Lu, Z., Lebo, Z.J., 2020. Examining the atmospheric  
    radiative and snow-darkening effects of black carbon and dust across the Rocky  
    Mountains of the United States using WRF-Chem. Atmos. Chem. Phys. 20 (18),  
    10911 – 10935.  
    Ryan, J.C., Hubbard, A., Irvine-Fynn, T.D., Doyle, S.H., Cook, J.M., Stibal, M., Box, J.E.,
2015.  How robust are in situ observations for validating satellite-derived albedo over  
    the dark zone of the Greenland Ice Sheet? Geophys. Res. Lett. 34, 6218–6225.  
    Schaaf, C.B., Gao, F., Stahler, A.H., Lucht, W., Li, X., Tsang, T., et al., 2002. First  
    operational BRDF, albedo and Nadir reflectance products from MODIS. Remote Sens.  
    Environ. 83, 135–148.  
    Schiefer, E., Menounos, B., Wheate, R., 2007. Recent volume loss of British Columbian  
    glaciers, Canada. Geophys. Res. Lett. 34, L16503 https://doi.org/10.1029/  
    2007GL030780.  
    Schmale, J., Flanner, M., Kang, S., Sprenger, M., Zhang, Q., Guo, J., Li, Y.,  
    Schwikowski, M., Farinotti, D., 2017. Modulation of snow reflectance and snowmelt  
    from Central Asian glaciers by anthropogenic black carbon. Sci. Rep. 7, 40501.  
    https://doi.org/10.1038/srep40501.  
    Sen, P.K., 1968. Estimates of the regression coefficient based on Kendall’s tau. J. Am.  
    Stat. Assoc. 63, 1379–1389.  
    Skiles, S.M., Painter, T., 2017. Daily evolution in dust and black carbon content, snow  
    grain size, and snow albedo during snowmelt, Rocky Mountains, Colorado.  
    J. Glaciol. 63 (237), 118–132.  
    Skiles, S.M.K., Flanner, M., Cook, J.M., Dumont, M., Painter, T.H., 2018. Radiative  
    forcing by light-absorbing particles in snow. Nat. Clim. Chang. 8, 964–971. https://  
    doi.org/10.1038/s41558-018-0296-5.  
    Soja, A.J., Tchebakova, N.M., French, N.H., Flannigan, M.D., Shugart, H.H., Stocks, B.J.,  
    Sukhinin, A.I., Parfenova, E., Chapin, F.S., Stackhouse, P.W., 2007. Climate-induced  
    boreal forest change: predictions versus current observations. Glob. Planet. Chang.  
    56 (3), 274–296.  
    Stein, A.F., Draxler, R.R., Rolph, G.D., Stunder, B.J.B., Cohen, M.D., Ngan, F., 2015.  
    NOAA’s HYSPLIT atmospheric transport and dispersion modeling system. Bull.  
    Amer. Meteor. Soc. 96, 2059–2077. https://doi.org/10.1175/BAMS-D-14-00110.1.  
    Stillinger, T., Roberts, D.A., Collar, N.M., Dozier, J., 2019. Cloud masking for Landsat 8  
    and MODIS Terra over snow-covered terrain: error analysis and spectral similarity  
    between snow and cloud. Water Resour. Res. 55, 6169–6184. https://doi.org/  
    10.1029/2019WR024932.  
    Stroeve, J., Box, J.E., Haran, T., 2006. Evaluation of the MODIS (MO10A1) daily snow  
    albedo product over the Greenland ice sheet. Remote Sens. Environ. 105, 155e171.  
    Thomas, J.L., et al., 2017. Quantifying black carbon deposition over the Greenland ice  
    sheet from forest fires in Canada. Geophys. Res. Lett. 44, 7965–7974. https://doi.  
    org/10.1002/2017GL073701.  
    Warren, S.G., 2013. Can black carbon in snow be detected by remote sensing?  
    J. Geophys. Res. 118 (2), 779–786. https://doi.org/10.1029/2012JD018476.  
    Warren, S.G., Wiscombe, W.J., 1980. A model for the spectral albedo of snow. II: snow  
    containing atmospheric aerosols. J. Atmos. Sci. 37, 2734–2745. https://doi.org/  
    10.1175/1520-0469(1980)037.  
    Williamson, S.N., Copland, L., Hik, D.S., 2016. The accuracy of satellite-derived albedo  
    for northern alpine and glaciated land covers. Polar Sci. 10, 262–269.  
    Williamson, C.J., et al., 2020. Algal photophysiology drives darkening and melt of the  
    Greenland ice sheet. Proc. Natl. Acad. Sci. 117, 5694–5705. https://doi.org/  
    10.1073/pnas.1918412117.  
    Williamson, S.N., Copland, L., Thomson, L., Burgess, D., 2020a. Comparing simple  
    albedo scaling methods for estimating Arctic glacier mass balance. Remote Sens.  
    Environ. 246, 1–14. https://doi.org/10.1016/j.rse.2020.111858.  
    Williamson, S.N., Zdanowicz, C., Anslow, F.S., Clarke, G.K., et al., 2020b. Evidence for  
    elevation-dependent warming in the St. Elias Mountains, Yukon, Canada. J. Clim. 33,  
    3253 – 3269. https://doi.org/10.1175/jcli-d-19-0405.1.  
    Wiscombe, W.J., Warren, S.G., 1980. A model for the spectral albedo of snow. I: pure  
    snow. J. Atmos. Sci. 37, 2712–2733.  
    Yang, R., Hock, R., Kang, S., Shangguan, D., Guo, W., 2020. Glacier mass and area  
    changes on the Kenai Peninsula, Alaska, 1986 – 2016. J. Glaciol. 1 – 15. https://doi.  
    org/10.1017/jog.2020.32.  
    Zemp, M., Huss, M., Thibert, E., et al., 2019. Global glacier mass changes and their  
    contributions to sea-level rise from 1961 to 2016. Nature 568, 382–386. https://doi.  
    org/10.1038/s41586-019-1071-0.  
    Zhang, et al., 2021. Albedo reduction as an important driver for glacier melting in  
    Tibetan Plateau and its surrounding areas. Earth Sci. Rev. 220, 103735.