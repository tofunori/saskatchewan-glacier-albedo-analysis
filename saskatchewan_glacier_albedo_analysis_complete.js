// ╔════════════════════════════════════════════════════════════════════════════════════════╗
// ║                    ANALYSE DE L'ÉVOLUTION DE L'ALBÉDO DU GLACIER SASKATCHEWAN          ║
// ║                                      2010 - 2024                                       ║
// ╚════════════════════════════════════════════════════════════════════════════════════════╝

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 1 : INITIALISATION ET CHARGEMENT DES DONNÉES                                  │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 1. Charger l'asset du glacier Saskatchewan
var saskatchewan_glacier = ee.Image('projects/tofunori/assets/Saskatchewan_glacier_2024_updated');
var glacier_mask = saskatchewan_glacier.gt(0);
var glacier_geometry = glacier_mask.reduceToVectors({
  scale: 30,
  maxPixels: 1e6,
  bestEffort: true
}).geometry();

// 2. Définir la période d'analyse complète
var startDate = ee.Date('2010-01-01');
var endDate = ee.Date('2024-12-31');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 2 : FONCTIONS D'ANALYSE                                                       │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 3. Fonction pour calculer l'albédo moyen annuel pendant l'été
function calculateAnnualAlbedo(year) {
  var yearStart = ee.Date.fromYMD(year, 6, 1);  // 1er juin
  var yearEnd = ee.Date.fromYMD(year, 9, 30);   // 30 septembre
  
  // Charger les données MODIS MCD43A3 pour l'été de cette année
  var albedo_collection = ee.ImageCollection('MODIS/061/MCD43A3')
    .filterDate(yearStart, yearEnd)
    .filterBounds(glacier_geometry)
    .select(['Albedo_WSA_shortwave', 'BRDF_Albedo_Band_Mandatory_Quality_shortwave']);
  
  // Filtrer pour garder seulement les pixels de bonne qualité (0 ou 1)
  var quality_filtered = albedo_collection.map(function(img) {
    var quality = img.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave');
    var albedo = img.select('Albedo_WSA_shortwave');
    
    // Masquer les pixels de mauvaise qualité et appliquer le facteur d'échelle
    var good_quality_mask = quality.lte(1);
    var albedo_scaled = albedo.multiply(0.001)
      .updateMask(good_quality_mask)
      .updateMask(glacier_mask);
    
    return albedo_scaled;
  });
  
  // Calculer la moyenne pour l'été
  var summer_mean = quality_filtered.mean();
  
  // Calculer les statistiques
  var stats = summer_mean.reduceRegion({
    reducer: ee.Reducer.mean().combine(
      ee.Reducer.stdDev(), '', true
    ).combine(
      ee.Reducer.percentile([25, 50, 75]), '', true
    ),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    bestEffort: true
  });
  
  return ee.Feature(null, {
    'year': year,
    'albedo_mean': stats.get('Albedo_WSA_shortwave_mean'),
    'albedo_stdDev': stats.get('Albedo_WSA_shortwave_stdDev'),
    'albedo_p25': stats.get('Albedo_WSA_shortwave_p25'),
    'albedo_median': stats.get('Albedo_WSA_shortwave_p50'),
    'albedo_p75': stats.get('Albedo_WSA_shortwave_p75'),
    'n_images': quality_filtered.size()
  });
}

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 3 : CALCUL DES STATISTIQUES ANNUELLES                                         │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 4. Calculer l'albédo pour chaque année
var years = ee.List.sequence(2010, 2024);
var annual_albedo = ee.FeatureCollection(years.map(calculateAnnualAlbedo));

print('Statistiques annuelles de l\'albédo:', annual_albedo);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 4 : VISUALISATION TEMPORELLE                                                  │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 5. Créer un graphique de l'évolution temporelle
var albedoChart = ui.Chart.feature.byFeature(annual_albedo, 'year')
  .setChartType('LineChart')
  .setOptions({
    title: 'Évolution de l\'albédo moyen d\'été (juin-septembre) - Glacier Saskatchewan',
    hAxis: {
      title: 'Année',
      format: '####'
    },
    vAxis: {
      title: 'Albédo',
      viewWindow: {min: 0, max: 1}
    },
    series: {
      0: {targetAxisIndex: 0, type: 'line', color: 'blue', lineWidth: 2, pointSize: 4},
      1: {targetAxisIndex: 0, type: 'line', color: 'red', lineWidth: 1, lineDashStyle: [5, 5]},
      2: {targetAxisIndex: 0, type: 'line', color: 'gray', lineWidth: 1},
      3: {targetAxisIndex: 0, type: 'line', color: 'green', lineWidth: 1},
      4: {targetAxisIndex: 0, type: 'line', color: 'gray', lineWidth: 1}
    },
    interpolateNulls: true,
    height: 400
  });

print(albedoChart);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 5 : ANALYSE DE TENDANCE LINÉAIRE                                              │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 6. Analyser la tendance sur la période
var yearProperty = annual_albedo.aggregate_array('year');
var albedoProperty = annual_albedo.aggregate_array('albedo_mean');

// Créer une liste de features pour la régression
var regression_data = ee.List.sequence(0, years.size().subtract(1)).map(function(i) {
  return ee.Feature(null, {
    'year': ee.List(yearProperty).get(i),
    'albedo': ee.List(albedoProperty).get(i)
  });
});

// Créer une collection et appliquer la régression
var regression_fc = ee.FeatureCollection(regression_data);
var linearFit = regression_fc.reduceColumns({
  reducer: ee.Reducer.linearFit(),
  selectors: ['year', 'albedo']
});

// Extraire les coefficients
var scale = ee.Number(linearFit.get('scale'));
var offset = ee.Number(linearFit.get('offset'));

print('Analyse de tendance linéaire:');
print('Pente (changement d\'albédo par an):', scale);
print('Ordonnée à l\'origine:', offset);
print('R² (coefficient de détermination):', linearFit);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 6 : COMPARAISON ENTRE PÉRIODES                                                │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 7. Créer des cartes de comparaison entre périodes
function getAlbedoPeriodMean(startYear, endYear, label) {
  var periodStart = ee.Date.fromYMD(startYear, 6, 1);
  var periodEnd = ee.Date.fromYMD(endYear, 9, 30);
  
  var albedo_period = ee.ImageCollection('MODIS/061/MCD43A3')
    .filterDate(periodStart, periodEnd)
    .filterBounds(glacier_geometry)
    .map(function(img) {
      var quality = img.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave');
      var albedo = img.select('Albedo_WSA_shortwave');
      var good_quality = quality.lte(1);
      
      return albedo.multiply(0.001)
        .updateMask(good_quality)
        .updateMask(glacier_mask);
    });
  
  return albedo_period.mean().set('label', label);
}

// Comparer deux périodes
var albedo_2010_2014 = getAlbedoPeriodMean(2010, 2014, 'Albédo 2010-2014');
var albedo_2020_2024 = getAlbedoPeriodMean(2020, 2024, 'Albédo 2020-2024');

// Calculer la différence
var albedo_change = albedo_2020_2024.subtract(albedo_2010_2014);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 7 : VISUALISATION CARTOGRAPHIQUE                                              │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 8. Visualisation sur la carte
Map.centerObject(glacier_geometry, 11);
Map.addLayer(glacier_mask.selfMask(), {palette: ['lightblue']}, 'Glacier Saskatchewan', false);

// Paramètres de visualisation pour l'albédo
var albedoVis = {
  min: 0.4,
  max: 0.9,
  palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']
};

Map.addLayer(albedo_2010_2014, albedoVis, 'Albédo moyen 2010-2014');
Map.addLayer(albedo_2020_2024, albedoVis, 'Albédo moyen 2020-2024');

// Visualisation du changement
var changeVis = {
  min: -0.1,
  max: 0.1,
  palette: ['red', 'orange', 'yellow', 'white', 'lightblue', 'blue', 'darkblue']
};
Map.addLayer(albedo_change, changeVis, 'Changement d\'albédo (2020-2024) - (2010-2014)');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 8 : STATISTIQUES DE CHANGEMENT                                                │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 9. Calculer les statistiques de changement
var changeStats = albedo_change.reduceRegion({
  reducer: ee.Reducer.mean().combine(
    ee.Reducer.stdDev(), '', true
  ).combine(
    ee.Reducer.percentile([10, 25, 50, 75, 90]), '', true
  ),
  geometry: glacier_geometry,
  scale: 500,
  maxPixels: 1e9
});

print('Statistiques de changement d\'albédo:', changeStats);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 9 : EXPORT DES DONNÉES                                                        │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 10. Export des résultats en CSV
Export.table.toDrive({
  collection: annual_albedo,
  description: 'Saskatchewan_Glacier_Albedo_Evolution_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'albedo_annual_stats',
  fileFormat: 'CSV'
});

// 11. Export des cartes d'albédo moyen
Export.image.toDrive({
  image: albedo_2010_2014,
  description: 'Saskatchewan_Albedo_2010_2014',
  folder: 'GEE_exports',
  fileNamePrefix: 'albedo_mean_2010_2014',
  scale: 500,
  region: glacier_geometry,
  maxPixels: 1e9
});

Export.image.toDrive({
  image: albedo_2020_2024,
  description: 'Saskatchewan_Albedo_2020_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'albedo_mean_2020_2024',
  scale: 500,
  region: glacier_geometry,
  maxPixels: 1e9
});

Export.image.toDrive({
  image: albedo_change,
  description: 'Saskatchewan_Albedo_Change',
  folder: 'GEE_exports',
  fileNamePrefix: 'albedo_change_2010_2024',
  scale: 500,
  region: glacier_geometry,
  maxPixels: 1e9
});

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 10 : RÉSUMÉ DE L'ANALYSE                                                      │
// └────────────────────────────────────────────────────────────────────────────────────────┘

print('');
print('Analyse terminée !');
print('- Graphique temporel de l\'évolution de l\'albédo créé');
print('- Cartes comparatives entre 2010-2014 et 2020-2024 affichées');
print('- Exports configurés pour les statistiques et les cartes');

// ╔════════════════════════════════════════════════════════════════════════════════════════╗
// ║                       ANALYSE COMPLÉMENTAIRE : QUALITÉ DES PIXELS                      ║
// ╚════════════════════════════════════════════════════════════════════════════════════════╝

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 11 : ANALYSE DE LA DISTRIBUTION QUOTIDIENNE DE QUALITÉ                        │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 13. Graphique de distribution quotidienne de la qualité des pixels (saison de fonte)
print('');
print('=== ANALYSE DE LA QUALITÉ DES PIXELS PAR JOUR (SAISONS DE FONTE 2010-2024) ===');

// Fonction pour analyser la distribution de qualité pour chaque image
function analyzeQualityDistribution(img) {
  var date = img.date();
  var quality = img.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave');
  
  // Créer des masques pour chaque niveau de qualité dans le glacier
  var q0 = quality.eq(0).and(glacier_mask);  // Meilleure qualité
  var q1 = quality.eq(1).and(glacier_mask);  // Bonne qualité
  var q2 = quality.eq(2).and(glacier_mask);  // Qualité moyenne
  var q3 = quality.eq(3).and(glacier_mask);  // Faible qualité
  
  // Compter les pixels pour chaque niveau
  var count_q0 = q0.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9
  }).get(q0.bandNames().get(0));
  
  var count_q1 = q1.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9
  }).get(q1.bandNames().get(0));
  
  var count_q2 = q2.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9
  }).get(q2.bandNames().get(0));
  
  var count_q3 = q3.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9
  }).get(q3.bandNames().get(0));
  
  return ee.Feature(null, {
    'system:time_start': date.millis(),
    'date': date.format('YYYY-MM-dd'),
    'quality_0_best': count_q0,
    'quality_1_good': count_q1,
    'quality_2_moderate': count_q2,
    'quality_3_poor': count_q3,
    'total_pixels': ee.Number(count_q0).add(count_q1).add(count_q2).add(count_q3)
  });
}

// Analyser toute la période 2010-2024 (été seulement pour optimiser)
// Approche simplifiée : utiliser directement filterDate sur toute la période et filtrer les mois
var summerCollection = ee.ImageCollection('MODIS/061/MCD43A3')
  .filterDate('2010-01-01', '2024-12-31')
  .filterBounds(glacier_geometry)
  .filter(ee.Filter.calendarRange(6, 9, 'month')); // Juin à septembre

var qualityDistribution = summerCollection
  .select('BRDF_Albedo_Band_Mandatory_Quality_shortwave')
  .map(analyzeQualityDistribution);

// Créer le graphique en barres empilées
var stackedChart = ui.Chart.feature.byFeature(
    qualityDistribution, 
    'system:time_start', 
    ['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor']
  )
  .setChartType('ColumnChart')
  .setOptions({
    title: 'Distribution quotidienne de la qualité des pixels MODIS - Toutes saisons de fonte 2010-2024 (juin-septembre)',
    hAxis: {
      title: 'Date',
      format: 'yyyy'
    },
    vAxis: {
      title: 'Nombre de pixels'
    },
    colors: ['#2166ac', '#92c5de', '#fddbc7', '#d6604d'], // Bleu foncé à rouge
    isStacked: true,
    bar: {groupWidth: '90%'},
    height: 500,
    legend: {
      position: 'top',
      labels: ['Qualité 0 (Meilleure)', 'Qualité 1 (Bonne)', 'Qualité 2 (Moyenne)', 'Qualité 3 (Faible)']
    }
  });

print(stackedChart);

// Export des données de qualité pour toute la période
Export.table.toDrive({
  collection: qualityDistribution,
  description: 'Saskatchewan_Summer_Quality_Distribution_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'summer_quality_stats_2010_2024',
  fileFormat: 'CSV'
});

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 12 : ANALYSE DE LA COUVERTURE TEMPORELLE                                      │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Calculer le nombre total de pixels dans le masque du glacier
var totalPixelCount = glacier_mask.selfMask().reduceRegion({
  reducer: ee.Reducer.count(),
  geometry: glacier_geometry,
  scale: 500,
  maxPixels: 1e9
});

print('Nombre total de pixels MODIS (500m) dans le masque du glacier:', totalPixelCount);

// Analyser la disponibilité des données sur toute la période
var fullPeriodCollection = ee.ImageCollection('MODIS/061/MCD43A3')
  .filterDate(startDate, endDate)
  .filterBounds(glacier_geometry)
  .select(['Albedo_WSA_shortwave', 'BRDF_Albedo_Band_Mandatory_Quality_shortwave']);

// Compter combien de fois chaque pixel a des données valides
var validDataCount = fullPeriodCollection.map(function(img) {
  var quality = img.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave');
  var validMask = quality.lte(1).and(glacier_mask);
  return validMask;
}).sum();

// Calculer le pourcentage de couverture temporelle pour chaque pixel
var totalDays = fullPeriodCollection.size();
var coveragePercentage = validDataCount.divide(totalDays).multiply(100);

// Statistiques de couverture
var coverageStats = coveragePercentage.reduceRegion({
  reducer: ee.Reducer.percentile([0, 10, 25, 50, 75, 90, 100]).combine(
    ee.Reducer.mean(), '', true
  ).combine(
    ee.Reducer.stdDev(), '', true
  ),
  geometry: glacier_geometry,
  scale: 500,
  maxPixels: 1e9
});

print('Statistiques de couverture temporelle des pixels (%):', coverageStats);

// Visualiser la couverture spatiale
Map.addLayer(
  coveragePercentage.updateMask(glacier_mask),
  {min: 0, max: 50, palette: ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen']},
  'Couverture temporelle des données (%)'
);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 13 : VISUALISATIONS FINALES ET STATISTIQUES                                   │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Créer une visualisation montrant tous les pixels du masque
Map.addLayer(
  glacier_mask.selfMask(),
  {palette: ['white'], opacity: 0.5},
  'Tous les pixels du masque glacier'
);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ VISUALISATION DES PIXELS MODIS COMPLETS DANS LE MASQUE GLACIER                        │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Chercher une image proche du 2018-08-16 dans notre collection
var targetDate = ee.Date('2018-08-16');
var dateRange = 5; // ±5 jours

var nearTargetDate = summerCollection
  .filterDate(targetDate.advance(-dateRange, 'day'), targetDate.advance(dateRange, 'day'))
  .select(['Albedo_WSA_shortwave', 'BRDF_Albedo_Band_Mandatory_Quality_shortwave']);

// Prendre la première image disponible près de cette date
var bestImage = nearTargetDate.first();

print('Images disponibles près du 2018-08-16:', nearTargetDate.size());
print('Image utilisée pour visualisation pixels MODIS:', bestImage.date().format('YYYY-MM-dd'));

// Créer la visualisation avec cette meilleure image
var bestAlbedo = bestImage.select('Albedo_WSA_shortwave').multiply(0.001);
var bestQuality = bestImage.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave');

// Masquer seulement les pixels de mauvaise qualité, garder tous les pixels MODIS complets
var goodQualityMask = bestQuality.lte(1);
var modisPixelsInGlacier = bestAlbedo.updateMask(goodQualityMask);

// Créer une extension du masque glacier pour capturer tous les pixels MODIS qui l'intersectent
var extendedMask = glacier_mask.reduceNeighborhood({
  reducer: ee.Reducer.max(),
  kernel: ee.Kernel.square(250, 'meters'), // 250m de rayon pour capturer pixels 500m
});

var modisPixelsExtended = modisPixelsInGlacier.updateMask(extendedMask);

// Visualiser l'albédo avec pixels MODIS complets
Map.addLayer(
  modisPixelsExtended,
  {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']},
  'Albédo - Pixels MODIS 500m complets (meilleure image)'
);

// Créer les contours des pixels pour voir la grille
var pixelContours = modisPixelsExtended.mask()
  .focal_max(1, 'square', 'pixels')
  .subtract(modisPixelsExtended.mask().focal_min(1, 'square', 'pixels'));

Map.addLayer(
  pixelContours.selfMask(),
  {palette: ['black'], opacity: 0.8},
  'Contours pixels MODIS 500m'
);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ AJOUTER LES CENTROIDES DES PIXELS MODIS UTILISÉS                                      │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Convertir les pixels en points centroides
// Créer une image binaire (0 ou 1) pour reduceToVectors
var binaryMask = modisPixelsExtended.mask().multiply(1).uint8();

var pixelCentroids = binaryMask
  .reduceToVectors({
    geometry: glacier_geometry.buffer(1000), // Buffer pour capturer tous les pixels
    scale: 500,
    geometryType: 'centroid', // Créer des points au centre de chaque pixel
    maxPixels: 1e6,
    bestEffort: true
  });

// Ajouter les centroides comme points
Map.addLayer(
  pixelCentroids,
  {color: 'yellow'},
  'Centroides pixels MODIS utilisés'
);

// Optionnel : Ajouter des points plus visibles
var centroidPoints = pixelCentroids.map(function(feature) {
  return feature.buffer(50); // Buffer de 50m pour rendre les points plus visibles
});

Map.addLayer(
  centroidPoints,
  {color: 'red', fillColor: 'yellow', opacity: 0.8},
  'Centroides pixels MODIS (points agrandis)'
);

print('Nombre de pixels MODIS utilisés (centroides):', pixelCentroids.size());

// Calculer combien de pixels ont au moins une observation valide
var anyValidData = validDataCount.gt(0);
var pixelsWithData = anyValidData.reduceRegion({
  reducer: ee.Reducer.sum(),
  geometry: glacier_geometry,
  scale: 500,
  maxPixels: 1e9
});

print('Nombre de pixels avec au moins une observation valide (2010-2024):', pixelsWithData);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 14 : EXPORT FINAL DE LA CARTE DE COUVERTURE                                   │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Export de la carte de couverture
Export.image.toDrive({
  image: coveragePercentage.updateMask(glacier_mask),
  description: 'Saskatchewan_Data_Coverage_Map',
  folder: 'GEE_exports',
  fileNamePrefix: 'pixel_coverage_percentage',
  scale: 500,
  region: glacier_geometry,
  maxPixels: 1e9
});

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 15 : ANALYSE QUOTIDIENNE AVEC STATISTIQUES D'ALBÉDO                           │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Fonction modifiée pour inclure les statistiques d'albédo quotidiennes
function analyzeQualityAndAlbedoDistribution(img) {
  var date = img.date();
  var quality = img.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave');
  var albedo = img.select('Albedo_WSA_shortwave').multiply(0.001); // Facteur d'échelle
  
  // Masquer les pixels de bonne qualité seulement (≤1) dans le glacier
  var goodQualityMask = quality.lte(1).and(glacier_mask);
  var validAlbedo = albedo.updateMask(goodQualityMask);
  
  // Compter les pixels pour chaque niveau de qualité
  var q0 = quality.eq(0).and(glacier_mask);
  var q1 = quality.eq(1).and(glacier_mask);
  var q2 = quality.eq(2).and(glacier_mask);
  var q3 = quality.eq(3).and(glacier_mask);
  
  var count_q0 = q0.reduceRegion({ reducer: ee.Reducer.sum(), geometry: glacier_geometry, scale: 500, maxPixels: 1e9 }).get(q0.bandNames().get(0));
  var count_q1 = q1.reduceRegion({ reducer: ee.Reducer.sum(), geometry: glacier_geometry, scale: 500, maxPixels: 1e9 }).get(q1.bandNames().get(0));
  var count_q2 = q2.reduceRegion({ reducer: ee.Reducer.sum(), geometry: glacier_geometry, scale: 500, maxPixels: 1e9 }).get(q2.bandNames().get(0));
  var count_q3 = q3.reduceRegion({ reducer: ee.Reducer.sum(), geometry: glacier_geometry, scale: 500, maxPixels: 1e9 }).get(q3.bandNames().get(0));
  
  // Calculer les statistiques d'albédo pour les pixels de bonne qualité
  var albedoStats = validAlbedo.reduceRegion({
    reducer: ee.Reducer.mean().combine(
      ee.Reducer.stdDev(), '', true
    ).combine(
      ee.Reducer.percentile([10, 25, 50, 75, 90]), '', true
    ).combine(
      ee.Reducer.count(), '', true
    ),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9
  });
  
  return ee.Feature(null, {
    'system:time_start': date.millis(),
    'date': date.format('YYYY-MM-dd'),
    'doy': date.getRelative('day', 'year'),
    // Statistiques de qualité
    'quality_0_best': count_q0,
    'quality_1_good': count_q1,
    'quality_2_moderate': count_q2,
    'quality_3_poor': count_q3,
    'total_pixels': ee.Number(count_q0).add(count_q1).add(count_q2).add(count_q3),
    'valid_pixels': ee.Number(count_q0).add(count_q1),
    // Statistiques d'albédo
    'albedo_mean': albedoStats.get('Albedo_WSA_shortwave_mean'),
    'albedo_stdDev': albedoStats.get('Albedo_WSA_shortwave_stdDev'),
    'albedo_p10': albedoStats.get('Albedo_WSA_shortwave_p10'),
    'albedo_p25': albedoStats.get('Albedo_WSA_shortwave_p25'),
    'albedo_median': albedoStats.get('Albedo_WSA_shortwave_p50'),
    'albedo_p75': albedoStats.get('Albedo_WSA_shortwave_p75'),
    'albedo_p90': albedoStats.get('Albedo_WSA_shortwave_p90'),
    'albedo_pixel_count': albedoStats.get('Albedo_WSA_shortwave_count')
  });
}

// Appliquer l'analyse sur toute la période 2010-2024 (étés seulement)
var dailyStats = summerCollection
  .select(['Albedo_WSA_shortwave', 'BRDF_Albedo_Band_Mandatory_Quality_shortwave'])
  .map(analyzeQualityAndAlbedoDistribution);

print('Statistiques quotidiennes d\'albédo et qualité (étés 2010-2024):', dailyStats);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 16 : GRAPHIQUES DE L'ÉVOLUTION QUOTIDIENNE                                    │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Graphique de l'évolution quotidienne de l'albédo moyen
var dailyAlbedoChart = ui.Chart.feature.byFeature(dailyStats, 'system:time_start', 'albedo_mean')
  .setChartType('LineChart')
  .setOptions({
    title: 'Évolution quotidienne de l\'albédo moyen - Glacier Saskatchewan (étés 2010-2024)',
    hAxis: {
      title: 'Date',
      format: 'yyyy'
    },
    vAxis: {
      title: 'Albédo moyen',
      viewWindow: {min: 0.3, max: 0.9}
    },
    series: {
      0: {color: 'blue', lineWidth: 2, pointSize: 3}
    },
    interpolateNulls: false,
    height: 400,
    pointsVisible: true
  });

print(dailyAlbedoChart);

// Graphique avec barres d'erreur (percentiles)
var dailyAlbedoWithError = ui.Chart.feature.byFeature(
    dailyStats, 
    'system:time_start', 
    ['albedo_p25', 'albedo_median', 'albedo_p75']
  )
  .setChartType('LineChart')
  .setOptions({
    title: 'Distribution quotidienne de l\'albédo (P25, médiane, P75) - Étés 2010-2024',
    hAxis: {
      title: 'Date',
      format: 'yyyy'
    },
    vAxis: {
      title: 'Albédo',
      viewWindow: {min: 0.3, max: 0.9}
    },
    series: {
      0: {color: 'lightblue', lineWidth: 1, lineDashStyle: [5, 5]},  // P25
      1: {color: 'blue', lineWidth: 3, pointSize: 4},               // Médiane
      2: {color: 'lightblue', lineWidth: 1, lineDashStyle: [5, 5]}   // P75
    },
    interpolateNulls: false,
    height: 400,
    legend: {
      position: 'top',
      labels: ['Percentile 25', 'Médiane', 'Percentile 75']
    }
  });

print(dailyAlbedoWithError);

// Graphique du nombre de pixels valides par jour
var validPixelsChart = ui.Chart.feature.byFeature(dailyStats, 'system:time_start', 'valid_pixels')
  .setChartType('ColumnChart')
  .setOptions({
    title: 'Nombre de pixels valides par jour (qualité ≤ 1) - Étés 2010-2024',
    hAxis: {
      title: 'Date',
      format: 'yyyy'
    },
    vAxis: {
      title: 'Nombre de pixels valides'
    },
    series: {
      0: {color: 'green'}
    },
    height: 300,
    legend: {position: 'none'}
  });

print(validPixelsChart);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 17 : ANALYSE DE CORRÉLATION ET TENDANCES SAISONNIÈRES                        │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Analyser la relation entre jour julien et albédo
var correlationChart = ui.Chart.feature.byFeature(dailyStats, 'doy', 'albedo_mean')
  .setChartType('ScatterChart')
  .setOptions({
    title: 'Relation entre jour julien et albédo moyen - Étés 2010-2024',
    hAxis: {
      title: 'Jour julien',
      viewWindow: {min: 150, max: 275}
    },
    vAxis: {
      title: 'Albédo moyen',
      viewWindow: {min: 0.3, max: 0.9}
    },
    series: {
      0: {color: 'red', pointSize: 5}
    },
    height: 400,
    trendlines: {
      0: {
        type: 'linear',
        color: 'blue',
        lineWidth: 2,
        opacity: 0.8,
        showR2: true,
        visibleInLegend: true
      }
    }
  });

print(correlationChart);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 18 : EXPORTS DES DONNÉES QUOTIDIENNES                                         │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Export des statistiques quotidiennes complètes pour toute la période
Export.table.toDrive({
  collection: dailyStats,
  description: 'Saskatchewan_Daily_Albedo_Quality_Stats_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'daily_albedo_quality_stats_2010_2024',
  fileFormat: 'CSV'
});

print('');
print('=== RÉSUMÉ DES NOUVELLES ANALYSES ===');
print('✓ Statistiques d\'albédo quotidiennes ajoutées');
print('✓ Graphiques d\'évolution temporelle créés');
print('✓ Analyse de corrélation avec jour julien');
print('✓ Export des données quotidiennes configuré');