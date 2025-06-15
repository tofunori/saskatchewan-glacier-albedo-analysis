// ╔════════════════════════════════════════════════════════════════════════════════════════╗
// ║              ANALYSE DE L'ALBÉDO PAR FRACTION DE COUVERTURE GLACIER                    ║
// ║                           GLACIER SASKATCHEWAN 2010-2024                              ║
// ╚════════════════════════════════════════════════════════════════════════════════════════╝

// Description : Analyse l'évolution de l'albédo selon différents seuils de fraction
// de couverture des pixels MODIS, permettant de distinguer les pixels "purs glacier"
// des pixels mixtes en bordure.

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

// 3. Fonction pour calculer la fraction de couverture (méthode testée et fonctionnelle)
function calculatePixelFraction(modisImage, glacierMask) {
  // Méthode inspirée du script Python fonctionnel
  var raster30 = ee.Image.constant(1)
    .updateMask(glacierMask)
    .unmask(0)
    .reproject('EPSG:4326', null, 30);
  
  var fraction = raster30
    .reduceResolution({
      reducer: ee.Reducer.mean(),
      maxPixels: 1024
    })
    .reproject(modisImage.projection());
  
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
// │ SECTION 3 : FONCTIONS D'ANALYSE D'ALBÉDO PAR FRACTION                                  │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 5. Fonction pour analyser l'albédo d'une année selon les fractions
function calculateAnnualAlbedoByFraction(year) {
  var yearStart = ee.Date.fromYMD(year, SUMMER_START_MONTH, 1);
  var yearEnd = ee.Date.fromYMD(year, SUMMER_END_MONTH, 30);
  
  // Charger les données MODIS pour cette année
  var albedo_collection = ee.ImageCollection('MODIS/061/MCD43A3')
    .filterDate(yearStart, yearEnd)
    .filterBounds(glacier_geometry)
    .select(['Albedo_WSA_shortwave', 'BRDF_Albedo_Band_Mandatory_Quality_shortwave']);
  
  // Traiter chaque image de la collection
  var processed_collection = albedo_collection.map(function(img) {
    var quality = img.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave');
    var albedo = img.select('Albedo_WSA_shortwave');
    var good_quality_mask = quality.lte(1);
    var albedo_scaled = albedo.multiply(0.001).updateMask(good_quality_mask);
    
    // Calculer la fraction pour cette image
    var fraction = calculatePixelFraction(img, glacier_mask);
    
    // Créer les masques par classe de fraction
    var masks = createFractionMasks(fraction, FRACTION_THRESHOLDS);
    
    // Appliquer chaque masque à l'albédo et créer une image multi-bandes
    var masked_albedos = [
      albedo_scaled.updateMask(masks.border).rename('border'),
      albedo_scaled.updateMask(masks.mixed_low).rename('mixed_low'),
      albedo_scaled.updateMask(masks.mixed_high).rename('mixed_high'),
      albedo_scaled.updateMask(masks.mostly_ice).rename('mostly_ice'),
      albedo_scaled.updateMask(masks.pure_ice).rename('pure_ice')
    ];
    
    return ee.Image.cat(masked_albedos);
  });
  
  // Calculer la moyenne annuelle pour chaque classe
  var annual_means = processed_collection.mean();
  
  // Calculer les statistiques pour chaque classe de fraction
  var classNames = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice'];
  
  // Calculer les statistiques pour toutes les bandes en une fois
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

// 6. Calculer l'albédo par fraction pour toutes les années
print('Calcul des statistiques annuelles par fraction de couverture...');
var annual_albedo_by_fraction = ee.FeatureCollection(STUDY_YEARS.map(calculateAnnualAlbedoByFraction));

print('Statistiques annuelles par classe de fraction:', annual_albedo_by_fraction);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 5 : VISUALISATIONS COMPARATIVES                                               │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 7. Créer des graphiques d'évolution temporelle par classe
var createTemporalChart = function(className, color) {
  var fieldName = className + '_mean';
  return ui.Chart.feature.byFeature(annual_albedo_by_fraction, 'year', fieldName)
    .setChartType('LineChart')
    .setOptions({
      title: 'Évolution albédo - Classe: ' + className.replace('_', ' '),
      hAxis: {title: 'Année', format: '####'},
      vAxis: {title: 'Albédo moyen', viewWindow: {min: 0.3, max: 0.9}},
      series: {0: {color: color, lineWidth: 2, pointSize: 4}},
      height: 300
    });
};

// Créer un graphique pour chaque classe
print('');
print('=== GRAPHIQUES PAR CLASSE DE FRACTION ===');
print(createTemporalChart('border', 'red'));        // 0-25%
print(createTemporalChart('mixed_low', 'orange'));   // 25-50%
print(createTemporalChart('mixed_high', 'yellow'));  // 50-75%
print(createTemporalChart('mostly_ice', 'lightblue')); // 75-90%
print(createTemporalChart('pure_ice', 'blue'));      // 90-100%

// 8. Graphique comparatif multi-classes
var multiClassChart = ui.Chart.feature.byFeature(
    annual_albedo_by_fraction, 
    'year', 
    ['border_mean', 'mixed_low_mean', 'mixed_high_mean', 'mostly_ice_mean', 'pure_ice_mean']
  )
  .setChartType('LineChart')
  .setOptions({
    title: 'Comparaison évolution albédo par classe de fraction de couverture',
    hAxis: {title: 'Année', format: '####'},
    vAxis: {title: 'Albédo moyen', viewWindow: {min: 0.3, max: 0.9}},
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
print('GRAPHIQUE COMPARATIF MULTI-CLASSES :');
print(multiClassChart);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 6 : ANALYSES DE TENDANCE PAR CLASSE                                            │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 9. Calculer les tendances pour chaque classe
var calculateTrend = function(className) {
  var fieldName = className + '_mean';
  var years = annual_albedo_by_fraction.aggregate_array('year');
  var values = annual_albedo_by_fraction.aggregate_array(fieldName);
  
  var trend_data = ee.List.sequence(0, STUDY_YEARS.size().subtract(1)).map(function(i) {
    return ee.Feature(null, {
      'year': ee.List(years).get(i),
      'albedo': ee.List(values).get(i)
    });
  });
  
  var trend_fc = ee.FeatureCollection(trend_data);
  var linearFit = trend_fc.reduceColumns({
    reducer: ee.Reducer.linearFit(),
    selectors: ['year', 'albedo']
  });
  
  return ee.Feature(null, {
    'class': className,
    'slope': linearFit.get('scale'),
    'offset': linearFit.get('offset'),
    'r2': linearFit.get('pearsonCorrelation')
  });
};

var trend_analyses = ee.FeatureCollection([
  calculateTrend('border'),
  calculateTrend('mixed_low'),
  calculateTrend('mixed_high'),
  calculateTrend('mostly_ice'),
  calculateTrend('pure_ice')
]);

print('');
print('ANALYSES DE TENDANCE PAR CLASSE :');
print('(pente = changement d\'albédo par an)', trend_analyses);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 7 : VISUALISATION CARTOGRAPHIQUE                                              │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 10. Créer des cartes d'exemple pour une année (2020)
var example_year = 2020;
var example_date = ee.Date.fromYMD(example_year, 7, 15); // Mi-juillet

var example_image = ee.ImageCollection('MODIS/061/MCD43A3')
  .filterDate(example_date, example_date.advance(5, 'day'))
  .filterBounds(glacier_geometry)
  .select(['Albedo_WSA_shortwave', 'BRDF_Albedo_Band_Mandatory_Quality_shortwave'])
  .first();

var example_fraction = calculatePixelFraction(example_image, glacier_mask);
var example_masks = createFractionMasks(example_fraction, FRACTION_THRESHOLDS);

// Préparer l'albédo pour visualisation
var example_albedo = example_image.select('Albedo_WSA_shortwave')
  .multiply(0.001)
  .updateMask(example_image.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave').lte(1));

// Centrer la carte
Map.centerObject(glacier_geometry, 12);

// Ajouter les couches
Map.addLayer(glacier_mask.selfMask(), {palette: ['lightgray'], opacity: 0.3}, '0. Masque glacier');
Map.addLayer(example_fraction.updateMask(example_fraction.gt(0)), 
  {min: 0, max: 1, palette: ['red', 'orange', 'yellow', 'lightblue', 'blue']}, 
  '1. Fraction de couverture');

// Paramètres d'albédo
var albedoVis = {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']};

// Ajouter l'albédo pour chaque classe
Map.addLayer(example_albedo.updateMask(example_masks.border), albedoVis, '2. Albédo 0-25% (bordure)', false);
Map.addLayer(example_albedo.updateMask(example_masks.mixed_low), albedoVis, '3. Albédo 25-50% (mixte bas)', false);
Map.addLayer(example_albedo.updateMask(example_masks.mixed_high), albedoVis, '4. Albédo 50-75% (mixte haut)');
Map.addLayer(example_albedo.updateMask(example_masks.mostly_ice), albedoVis, '5. Albédo 75-90% (majoritaire)');
Map.addLayer(example_albedo.updateMask(example_masks.pure_ice), albedoVis, '6. Albédo 90-100% (pur)');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 8 : EXPORTS                                                                   │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 11. Export des statistiques par fraction
Export.table.toDrive({
  collection: annual_albedo_by_fraction,
  description: 'Saskatchewan_Albedo_By_Fraction_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'albedo_by_fraction_annual',
  fileFormat: 'CSV'
});

// 12. Export des analyses de tendance
Export.table.toDrive({
  collection: trend_analyses,
  description: 'Saskatchewan_Albedo_Trends_By_Fraction',
  folder: 'GEE_exports',
  fileNamePrefix: 'albedo_trends_by_fraction',
  fileFormat: 'CSV'
});

// 13. Export de la carte de fraction d'exemple
Export.image.toDrive({
  image: example_fraction,
  description: 'Saskatchewan_Fraction_Map_Example',
  folder: 'GEE_exports',
  fileNamePrefix: 'fraction_map_' + example_year,
  scale: 500,
  region: glacier_geometry,
  maxPixels: 1e9
});

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 9 : RÉSUMÉ ET INTERPRÉTATION                                                  │
// └────────────────────────────────────────────────────────────────────────────────────────┘

print('');
print('=== RÉSUMÉ DE L\'ANALYSE PAR FRACTION ===');
print('');
print('CLASSES ANALYSÉES :');
print('• 0-25% : Pixels de bordure (faible couverture glacier)');
print('• 25-50% : Pixels mixtes faible (transition)');
print('• 50-75% : Pixels mixtes élevé (majoritairement glacier)');
print('• 75-90% : Pixels majoritairement glacier');
print('• 90-100% : Pixels quasi-purs glacier');
print('');
print('ANALYSES DISPONIBLES :');
print('• Évolution temporelle par classe');
print('• Tendances linéaires par niveau de pureté');
print('• Comparaison entre pixels purs vs mixtes');
print('• Impact du choix de seuil sur les résultats');
print('');
print('APPLICATIONS :');
print('• Optimisation des seuils de couverture');
print('• Compréhension des biais de bordure');
print('• Analyses plus robustes de l\'évolution glaciaire');

// FIN DU SCRIPT