// ╔════════════════════════════════════════════════════════════════════════════════════════╗
// ║              ANALYSE DE LA COUVERTURE DE NEIGE PAR FRACTION DE COUVERTURE GLACIER      ║
// ║                           GLACIER SASKATCHEWAN 2010-2024                                ║
// ║                        MODIS MOD10A1.061 NDSI_Snow_Cover                               ║
// ║                     Fichier: MOD10A1_ndsi_snow_cover_fractions.js                      ║
// ╚════════════════════════════════════════════════════════════════════════════════════════╝

// Description : Analyse l'évolution de la couverture de neige (en pourcentage) selon différents 
// seuils de fraction de couverture des pixels MODIS. Le band NDSI_Snow_Cover fournit le 
// pourcentage de couverture de neige (0-100%) pour chaque pixel. Cette analyse permet de
// comprendre la distribution spatiale et temporelle de la neige sur le glacier.

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 1 : CONFIGURATION ET INITIALISATION                                            │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 1. Paramètres configurables
var FRACTION_THRESHOLDS = [0.25, 0.50, 0.75, 0.90]; // Seuils de fraction à analyser
var STUDY_YEARS = ee.List.sequence(2010, 2024);
var SUMMER_START_MONTH = 6;  // Juin
var SUMMER_END_MONTH = 9;    // Septembre

// 2. Charger l'asset du glacier Saskatchewan
var saskatchewan_glacier = ee.Image('projects/tofunori/assets/Saskatchewan_glacier_2024_updated');
var glacier_mask = saskatchewan_glacier.gt(0);
var glacier_geometry = glacier_mask.reduceToVectors({
  scale: 30,
  maxPixels: 1e6,
  bestEffort: true
}).geometry();

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 2 : FONCTIONS DE CALCUL DE FRACTION                                            │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 3. Fonction pour calculer la fraction de couverture glacier dans chaque pixel MODIS
function calculatePixelFraction(modisImage, glacierMask) {
  // Obtenir la projection native de l'image MODIS
  var modisProjection = modisImage.projection();
  
  // Reprojecter directement le masque glacier dans la projection MODIS
  var raster30 = ee.Image.constant(1)
    .updateMask(glacierMask)
    .unmask(0)
    .reproject(modisProjection, null, 30);
  
  // Effectuer l'agrégation DANS la projection MODIS native
  var fraction = raster30
    .reduceResolution({
      reducer: ee.Reducer.mean(),
      maxPixels: 1024
    })
    .reproject(modisProjection, null, 500);
  
  return fraction; // Retourne valeurs 0-1
}

// 4. Fonction pour créer des masques par classes de fraction
function createFractionMasks(fractionImage, thresholds) {
  var masks = {};
  
  // Classe 0-25% : pixels de bordure
  masks['border'] = fractionImage.gt(0).and(fractionImage.lt(thresholds[0]));
  
  // Classe 25-50% : pixels mixtes faible
  masks['mixed_low'] = fractionImage.gte(thresholds[0]).and(fractionImage.lt(thresholds[1]));
  
  // Classe 50-75% : pixels mixtes élevé
  masks['mixed_high'] = fractionImage.gte(thresholds[1]).and(fractionImage.lt(thresholds[2]));
  
  // Classe 75-90% : pixels majoritairement glacier
  masks['mostly_ice'] = fractionImage.gte(thresholds[2]).and(fractionImage.lt(thresholds[3]));
  
  // Classe 90-100% : pixels quasi-purs
  masks['pure_ice'] = fractionImage.gte(thresholds[3]);
  
  return masks;
}

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 3 : FONCTIONS D'ANALYSE DE COUVERTURE DE NEIGE PAR FRACTION                    │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 5. Fonction pour analyser la couverture de neige d'une année selon les fractions
function calculateAnnualSnowCoverByFraction(year) {
  var yearStart = ee.Date.fromYMD(year, SUMMER_START_MONTH, 1);
  var yearEnd = ee.Date.fromYMD(year, SUMMER_END_MONTH, 30);
  
  // Charger les données MODIS MOD10A1 pour cette année
  var snow_collection = ee.ImageCollection('MODIS/061/MOD10A1')
    .filterDate(yearStart, yearEnd)
    .filterBounds(glacier_geometry)
    .select(['NDSI_Snow_Cover', 'NDSI_Snow_Cover_Basic_QA', 'NDSI_Snow_Cover_Class']);
  
  // Traiter chaque image de la collection
  var processed_collection = snow_collection.map(function(img) {
    var quality = img.select('NDSI_Snow_Cover_Basic_QA');
    var snow_cover = img.select('NDSI_Snow_Cover');
    var snow_class = img.select('NDSI_Snow_Cover_Class');
    
    // Filtres de qualité pour MOD10A1: 0=Best, 1=Good, 2=Ok
    // Pour l'analyse annuelle, on est plus strict (seulement Best et Good)
    var good_quality_mask = quality.lte(1);
    
    // Masque pour valeurs valides de couverture de neige (0-100%)
    var valid_snow_mask = snow_cover.lte(100);
    
    // Masque combiné : bonne qualité ET valeurs valides
    var valid_mask = good_quality_mask.and(valid_snow_mask);
    
    // Couverture de neige en pourcentage (déjà 0-100, pas besoin de conversion)
    var snow_cover_pct = snow_cover.updateMask(valid_mask);
    
    // Calculer la fraction de couverture glacier pour cette image
    var fraction = calculatePixelFraction(img, glacier_mask);
    
    // Créer les masques par classe de fraction
    var masks = createFractionMasks(fraction, FRACTION_THRESHOLDS);
    
    // Appliquer chaque masque à la couverture de neige et créer une image multi-bandes
    var masked_snow_covers = [
      snow_cover_pct.updateMask(masks.border).rename('border'),
      snow_cover_pct.updateMask(masks.mixed_low).rename('mixed_low'),
      snow_cover_pct.updateMask(masks.mixed_high).rename('mixed_high'),
      snow_cover_pct.updateMask(masks.mostly_ice).rename('mostly_ice'),
      snow_cover_pct.updateMask(masks.pure_ice).rename('pure_ice')
    ];
    
    return ee.Image.cat(masked_snow_covers);
  });
  
  // Calculer la moyenne annuelle pour chaque classe
  var annual_means = processed_collection.mean();
  
  // Calculer les statistiques pour chaque classe de fraction
  var classNames = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice'];
  
  // Calculer les statistiques pour toutes les bandes
  var all_stats = annual_means.reduceRegion({
    reducer: ee.Reducer.mean().combine(
      ee.Reducer.stdDev(), '', true
    ).combine(
      ee.Reducer.count(), '', true
    ),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    bestEffort: true
  });
  
  // Construire l'objet des propriétés
  var properties = {'year': year};
  
  classNames.forEach(function(className) {
    properties[className + '_mean'] = all_stats.get(className + '_mean');
    properties[className + '_stdDev'] = all_stats.get(className + '_stdDev');
    properties[className + '_count'] = all_stats.get(className + '_count');
  });
  
  return ee.Feature(null, properties);
}

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 4 : CALCUL DES STATISTIQUES ANNUELLES                                         │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 6. Calculer la couverture de neige par fraction pour toutes les années
print('Calcul des statistiques annuelles de couverture de neige par fraction de couverture...');
var annual_snow_cover_by_fraction = ee.FeatureCollection(STUDY_YEARS.map(calculateAnnualSnowCoverByFraction));

print('Statistiques annuelles par classe de fraction (MOD10A1 NDSI Snow Cover %):', annual_snow_cover_by_fraction);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 5 : VISUALISATIONS COMPARATIVES                                               │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 7. Créer des graphiques d'évolution temporelle par classe
var createTemporalChart = function(className, color) {
  var fieldName = className + '_mean';
  return ui.Chart.feature.byFeature(annual_snow_cover_by_fraction, 'year', fieldName)
    .setChartType('LineChart')
    .setOptions({
      title: 'Évolution couverture de neige (%) - Classe: ' + className.replace('_', ' '),
      hAxis: {title: 'Année', format: '####'},
      vAxis: {title: 'Couverture de neige moyenne (%)', viewWindow: {min: 0, max: 100}},
      series: {0: {color: color, lineWidth: 2, pointSize: 4}},
      height: 300
    });
};

// Créer un graphique pour chaque classe
print('');
print('=== GRAPHIQUES PAR CLASSE DE FRACTION (COUVERTURE DE NEIGE %) ===');
print(createTemporalChart('border', 'red'));        // 0-25%
print(createTemporalChart('mixed_low', 'orange'));   // 25-50%
print(createTemporalChart('mixed_high', 'yellow'));  // 50-75%
print(createTemporalChart('mostly_ice', 'lightblue')); // 75-90%
print(createTemporalChart('pure_ice', 'blue'));      // 90-100%

// 8. Graphique comparatif multi-classes
var multiClassChart = ui.Chart.feature.byFeature(
    annual_snow_cover_by_fraction, 
    'year', 
    ['border_mean', 'mixed_low_mean', 'mixed_high_mean', 'mostly_ice_mean', 'pure_ice_mean']
  )
  .setChartType('LineChart')
  .setOptions({
    title: 'Comparaison évolution couverture de neige (%) par classe de fraction (MOD10A1)',
    hAxis: {title: 'Année', format: '####'},
    vAxis: {title: 'Couverture de neige moyenne (%)', viewWindow: {min: 0, max: 100}},
    series: {
      0: {color: 'red', lineWidth: 2, pointSize: 3},      // Border
      1: {color: 'orange', lineWidth: 2, pointSize: 3},   // Mixed low
      2: {color: 'yellow', lineWidth: 2, pointSize: 3},   // Mixed high
      3: {color: 'lightblue', lineWidth: 2, pointSize: 3}, // Mostly ice
      4: {color: 'blue', lineWidth: 2, pointSize: 3}      // Pure ice
    },
    legend: {
      position: 'top',
      labels: ['0-25% (bordure)', '25-50% (mixte bas)', '50-75% (mixte haut)', '75-90% (majoritaire)', '90-100% (pur)']
    },
    height: 500
  });

print('');
print('GRAPHIQUE COMPARATIF MULTI-CLASSES (COUVERTURE DE NEIGE %) :');
print(multiClassChart);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 6 : ANALYSE QUOTIDIENNE PAR FRACTION (OPTIMISÉE POUR MANN-KENDALL)             │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 9. Fonction pour analyser les statistiques quotidiennes de couverture de neige
function analyzeDailySnowCoverByFraction(img) {
  var date = img.date();
  var quality = img.select('NDSI_Snow_Cover_Basic_QA');
  var snow_cover = img.select('NDSI_Snow_Cover');
  var snow_class = img.select('NDSI_Snow_Cover_Class');
  
  // Calculer la fraction de couverture glacier pour cette image
  var fraction = calculatePixelFraction(img, glacier_mask);
  var masks = createFractionMasks(fraction, FRACTION_THRESHOLDS);
  
  // Masques de qualité - utiliser seulement Best (0) et Good (1)
  var goodQualityMask = quality.lte(1);
  var validSnowMask = snow_cover.lte(100);
  
  // Calculer les statistiques pour chaque classe de fraction
  var stats = {};
  var classNames = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice'];
  
  classNames.forEach(function(className) {
    // Combiner masques de qualité, validité et fraction
    var classMask = masks[className].and(goodQualityMask).and(validSnowMask);
    var validSnowCover = snow_cover.updateMask(classMask);
    
    // Calculer les statistiques de couverture de neige
    var classStats = validSnowCover.reduceRegion({
      reducer: ee.Reducer.mean().combine(
        ee.Reducer.median(), '', true
      ).combine(
        ee.Reducer.count(), '', true
      ).combine(
        ee.Reducer.min(), '', true
      ).combine(
        ee.Reducer.max(), '', true
      ),
      geometry: glacier_geometry,
      scale: 500,
      maxPixels: 1e9,
      bestEffort: true
    });
    
    // Compter le nombre total de pixels dans cette classe
    var fractionPixelCount = masks[className].reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: glacier_geometry,
      scale: 500,
      maxPixels: 1e9,
      bestEffort: true
    }).get('constant');
    
    // Compter les pixels avec classe spéciale (nuages, nuit, etc.)
    var specialClassMask = masks[className].and(snow_class.gt(100));
    var specialClassCount = specialClassMask.reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: glacier_geometry,
      scale: 500,
      maxPixels: 1e9,
      bestEffort: true
    }).get('constant');
    
    // Extraire et stocker les statistiques
    var pixelCount = classStats.get('NDSI_Snow_Cover_count');
    
    stats[className + '_mean'] = classStats.get('NDSI_Snow_Cover_mean');
    stats[className + '_median'] = classStats.get('NDSI_Snow_Cover_median');
    stats[className + '_min'] = classStats.get('NDSI_Snow_Cover_min');
    stats[className + '_max'] = classStats.get('NDSI_Snow_Cover_max');
    stats[className + '_pixel_count'] = pixelCount;
    stats[className + '_total_pixels'] = fractionPixelCount;
    stats[className + '_special_class_pixels'] = specialClassCount;
    stats[className + '_data_quality'] = ee.Algorithms.If(
      ee.Algorithms.IsEqual(fractionPixelCount, 0),
      0,
      ee.Number(pixelCount).divide(ee.Number(fractionPixelCount)).multiply(100)
    );
  });
  
  // Calculer les informations temporelles
  var year = date.get('year');
  var doy = date.getRelative('day', 'year').add(1);
  var decimal_year = year.add(doy.divide(365.25));
  
  // Déterminer la saison
  var month = date.get('month');
  var season = ee.Algorithms.If(
    month.lte(7), 'early_summer',
    ee.Algorithms.If(
      month.eq(8), 'mid_summer',
      'late_summer'
    )
  );
  
  // Ajouter les métadonnées
  stats['date'] = date.format('YYYY-MM-dd');
  stats['year'] = year;
  stats['doy'] = doy;
  stats['decimal_year'] = decimal_year;
  stats['season'] = season;
  stats['system:time_start'] = date.millis();
  
  return ee.Feature(null, stats);
}

// 10. Calculer les statistiques quotidiennes pour toute la période
print('');
print('=== CALCUL DES STATISTIQUES QUOTIDIENNES DE COUVERTURE DE NEIGE ===');

var dailySnowCollection = ee.ImageCollection('MODIS/061/MOD10A1')
  .filterDate('2010-01-01', '2024-12-31')
  .filterBounds(glacier_geometry)
  .filter(ee.Filter.calendarRange(SUMMER_START_MONTH, SUMMER_END_MONTH, 'month'))
  .select(['NDSI_Snow_Cover', 'NDSI_Snow_Cover_Basic_QA', 'NDSI_Snow_Cover_Class']);

var dailySnowCoverByFraction = dailySnowCollection.map(analyzeDailySnowCoverByFraction);

print('Statistiques quotidiennes calculées:', dailySnowCoverByFraction.size(), 'jours');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 7 : VISUALISATION CARTOGRAPHIQUE INTERACTIVE                                  │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 11. Interface interactive pour choisir la date de visualisation
print('');
print('=== SÉLECTION DE DATE INTERACTIVE (COUVERTURE DE NEIGE) ===');

// Créer un sélecteur de date
var dateSlider = ui.DateSlider({
  start: '2010-06-01',
  end: '2024-09-30',
  value: '2020-07-15',
  period: 1,
  style: {width: '300px'}
});

var dateLabel = ui.Label('Choisir une date pour la visualisation de couverture de neige:');
var selectedDateLabel = ui.Label('Date sélectionnée: 2020-07-15');

// Fonction pour mettre à jour la visualisation
var updateVisualization = function() {
  var dateRange = dateSlider.getValue();
  var timestamp = dateRange[0];
  var js_date = new Date(timestamp);
  var selected_date = ee.Date(js_date);
  
  var year = js_date.getFullYear();
  var month = js_date.getMonth() + 1;
  var day = js_date.getDate();
  var dateString = year + '-' + 
    (month < 10 ? '0' + month : month) + '-' + 
    (day < 10 ? '0' + day : day);
  
  selectedDateLabel.setValue('Date sélectionnée: ' + dateString);
  
  // Charger l'image MOD10A1 pour la date sélectionnée
  var example_image = ee.ImageCollection('MODIS/061/MOD10A1')
    .filterDate(selected_date, selected_date.advance(5, 'day'))
    .filterBounds(glacier_geometry)
    .select(['NDSI_Snow_Cover', 'NDSI_Snow_Cover_Basic_QA', 'NDSI_Snow_Cover_Class'])
    .first();
  
  var example_fraction = calculatePixelFraction(example_image, glacier_mask);
  var example_masks = createFractionMasks(example_fraction, FRACTION_THRESHOLDS);
  
  // Préparer la couverture de neige pour visualisation
  var example_snow_cover = example_image.select('NDSI_Snow_Cover')
    .updateMask(example_image.select('NDSI_Snow_Cover_Basic_QA').lte(1))  // Seulement Best et Good
    .updateMask(example_image.select('NDSI_Snow_Cover').lte(100))
    .updateMask(example_fraction.gt(0)); // Masquer les pixels sans glacier
  
  // Classes spéciales
  var example_snow_class = example_image.select('NDSI_Snow_Cover_Class');
  
  // Effacer les couches précédentes (sauf la première - masque glacier)
  var layers = Map.layers();
  while (layers.length() > 1) {
    Map.remove(layers.get(layers.length() - 1));
  }
  
  // Ajouter les nouvelles couches
  Map.addLayer(example_fraction.updateMask(example_fraction.gt(0)), 
    {min: 0, max: 1, palette: ['red', 'orange', 'yellow', 'lightblue', 'blue']}, 
    '1. Fraction de couverture glacier - ' + dateString);
  
  Map.addLayer(example_snow_cover, 
    {min: 0, max: 100, palette: ['brown', 'yellow', 'green', 'cyan', 'blue', 'white']}, 
    '2. Couverture de neige (%) - Toutes classes');
  
  // Couverture de neige par classe de fraction
  var snowCoverVis = {min: 0, max: 100, palette: ['brown', 'yellow', 'green', 'cyan', 'blue', 'white']};
  
  Map.addLayer(example_snow_cover.updateMask(example_masks.border), snowCoverVis, 
    '3. Neige 0-25% (bordure)', false);
  Map.addLayer(example_snow_cover.updateMask(example_masks.mixed_low), snowCoverVis, 
    '4. Neige 25-50% (mixte bas)', false);
  Map.addLayer(example_snow_cover.updateMask(example_masks.mixed_high), snowCoverVis, 
    '5. Neige 50-75% (mixte haut)');
  Map.addLayer(example_snow_cover.updateMask(example_masks.mostly_ice), snowCoverVis, 
    '6. Neige 75-90% (majoritaire)');
  Map.addLayer(example_snow_cover.updateMask(example_masks.pure_ice), snowCoverVis, 
    '7. Neige 90-100% (pur)');
  
  // Ajouter les classes spéciales (limitées au glacier)
  Map.addLayer(example_snow_class.updateMask(example_snow_class.eq(250)).updateMask(example_fraction.gt(0)), 
    {palette: ['gray']}, '8. Nuages', false);
  Map.addLayer(example_snow_class.updateMask(example_snow_class.eq(211)).updateMask(example_fraction.gt(0)), 
    {palette: ['black']}, '9. Nuit', false);
};

// Bouton pour mettre à jour
var updateButton = ui.Button({
  label: 'Mettre à jour la carte',
  onClick: updateVisualization,
  style: {width: '200px'}
});

// Panneau de contrôle
var panel = ui.Panel([
  dateLabel,
  dateSlider,
  selectedDateLabel,
  updateButton
], ui.Panel.Layout.flow('vertical'), {
  width: '350px',
  position: 'top-left'
});

Map.add(panel);

// Initialisation de la carte
Map.centerObject(glacier_geometry, 12);
Map.addLayer(glacier_mask.selfMask(), {palette: ['lightgray'], opacity: 0.3}, '0. Masque glacier');

// Charger une image exemple
var example_date = ee.Date('2020-07-15');
var example_image = ee.ImageCollection('MODIS/061/MOD10A1')
  .filterDate(example_date, example_date.advance(5, 'day'))
  .filterBounds(glacier_geometry)
  .select(['NDSI_Snow_Cover', 'NDSI_Snow_Cover_Basic_QA', 'NDSI_Snow_Cover_Class'])
  .first();

var example_fraction = calculatePixelFraction(example_image, glacier_mask);
var example_snow_cover = example_image.select('NDSI_Snow_Cover')
  .updateMask(example_image.select('NDSI_Snow_Cover_Basic_QA').lte(1))  // Seulement Best et Good
  .updateMask(example_image.select('NDSI_Snow_Cover').lte(100))
  .updateMask(example_fraction.gt(0)); // Masquer les pixels sans glacier

Map.addLayer(example_fraction.updateMask(example_fraction.gt(0)), 
  {min: 0, max: 1, palette: ['red', 'orange', 'yellow', 'lightblue', 'blue']}, 
  '1. Fraction de couverture glacier');
Map.addLayer(example_snow_cover, 
  {min: 0, max: 100, palette: ['brown', 'yellow', 'green', 'cyan', 'blue', 'white']}, 
  '2. Couverture de neige (%) - Toutes classes');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 8 : EXPORTS                                                                   │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 12. Export des statistiques annuelles
Export.table.toDrive({
  collection: annual_snow_cover_by_fraction,
  description: 'Saskatchewan_NDSI_Snow_Cover_Annual_Fractions_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_ndsi_annual_fractions_2010_2024',
  fileFormat: 'CSV'
});

// 13. Export des statistiques quotidiennes
Export.table.toDrive({
  collection: dailySnowCoverByFraction,
  description: 'Saskatchewan_NDSI_Snow_Cover_Daily_Stats_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_ndsi_daily_stats_2010_2024',
  fileFormat: 'CSV'
});

// 14. Export de l'image exemple (avec masque glacier appliqué)
Export.image.toDrive({
  image: example_snow_cover,
  description: 'Saskatchewan_NDSI_Snow_Cover_Example_20200715',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_ndsi_example_20200715',
  scale: 500,
  region: glacier_geometry,
  maxPixels: 1e9
});

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 9 : ANALYSE DES CLASSES SPÉCIALES                                             │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 15. Fonction pour analyser la distribution des classes spéciales
function analyzeSpecialClasses(img) {
  var date = img.date();
  var snow_class = img.select('NDSI_Snow_Cover_Class');
  
  // Compter les pixels pour chaque classe spéciale dans le glacier
  var classStats = {};
  var specialClasses = {
    'missing_data': 200,
    'no_decision': 201,
    'night': 211,
    'inland_water': 237,
    'ocean': 239,
    'cloud': 250,
    'detector_saturated': 254
  };
  
  // Calculer le nombre de pixels pour chaque classe
  Object.keys(specialClasses).forEach(function(className) {
    var classValue = specialClasses[className];
    var classMask = snow_class.eq(classValue).and(glacier_mask);
    
    var count = classMask.reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: glacier_geometry,
      scale: 500,
      maxPixels: 1e9,
      bestEffort: true
    }).get('NDSI_Snow_Cover_Class');
    
    classStats[className + '_count'] = count;
  });
  
  // Ajouter les métadonnées temporelles
  classStats['date'] = date.format('YYYY-MM-dd');
  classStats['year'] = date.get('year');
  classStats['doy'] = date.getRelative('day', 'year').add(1);
  classStats['system:time_start'] = date.millis();
  
  return ee.Feature(null, classStats);
}

// Analyser les classes spéciales pour toute la période
var specialClassesAnalysis = dailySnowCollection.map(analyzeSpecialClasses);

// 16. Export de l'analyse des classes spéciales
Export.table.toDrive({
  collection: specialClassesAnalysis,
  description: 'Saskatchewan_NDSI_Special_Classes_Daily_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_special_classes_daily_2010_2024',
  fileFormat: 'CSV'
});

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 10 : RÉSUMÉ ET DOCUMENTATION                                                   │
// └────────────────────────────────────────────────────────────────────────────────────────┘

print('');
print('=== RÉSUMÉ ANALYSE NDSI SNOW COVER (MOD10A1.061) ===');
print('');
print('DATASET ANALYSÉ :');
print('• MOD10A1.061 NDSI_Snow_Cover (MODIS/Terra)');
print('• Résolution: 500m, cadence quotidienne');
print('• Valeurs: 0-100% de couverture de neige par pixel');
print('• Période: 2010-2024 (juin-septembre)');
print('');
print('BANDES UTILISÉES :');
print('• NDSI_Snow_Cover: Pourcentage de neige (0-100)');
print('• NDSI_Snow_Cover_Basic_QA: Qualité (utilise seulement 0=Best, 1=Good)');
print('• NDSI_Snow_Cover_Class: Classifications spéciales');
print('');
print('CLASSES SPÉCIALES DÉTECTÉES :');
print('• 200: Données manquantes');
print('• 201: Pas de décision');
print('• 211: Nuit');
print('• 237: Eau intérieure');
print('• 239: Océan');
print('• 250: Nuage');
print('• 254: Détecteur saturé');
print('');
print('ANALYSES EFFECTUÉES :');
print('• Couverture de neige par fraction de glacier');
print('• Statistiques annuelles et quotidiennes');
print('• Distribution des classes spéciales');
print('• Métriques de qualité des données');
print('');
print('EXPORTS CONFIGURÉS :');
print('• CSV annuel: MOD10A1_ndsi_annual_fractions_2010_2024.csv');
print('• CSV quotidien: MOD10A1_ndsi_daily_stats_2010_2024.csv');
print('• CSV classes: MOD10A1_special_classes_daily_2010_2024.csv');
print('• Image exemple: MOD10A1_ndsi_example_20200715.tif');
print('');
print('STRUCTURE CSV QUOTIDIEN (45+ colonnes) :');
print('• Temporel: date, year, doy, decimal_year, season');
print('• Par classe (5x): _mean, _median, _min, _max, _pixel_count,');
print('  _total_pixels, _special_class_pixels, _data_quality');
print('• Classes: border, mixed_low, mixed_high, mostly_ice, pure_ice');
print('');
print('APPLICATIONS :');
print('• Suivi de l\'accumulation et fonte de neige');
print('• Analyse de la dynamique spatiale de la neige');
print('• Détection des événements météorologiques (nuages)');
print('• Validation des modèles de bilan de masse');
print('• Étude de la ligne de neige transitoire');

// FIN DU SCRIPT