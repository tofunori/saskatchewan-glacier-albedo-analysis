// ╔════════════════════════════════════════════════════════════════════════════════════════╗
// ║              ANALYSE DE L'ALBÉDO DE NEIGE PAR FRACTION DE COUVERTURE GLACIER          ║
// ║                           GLACIER SASKATCHEWAN 2010-2024                              ║
// ║                        MODIS MOD10A1.061 Snow_Albedo_Daily_Tile                       ║
// ║                            Fichier: MOD10A1_basic_fractions.js                        ║
// ╚════════════════════════════════════════════════════════════════════════════════════════╝

// Description : Analyse l'évolution de l'albédo de neige selon différents seuils de fraction
// de couverture des pixels MODIS, permettant de distinguer les pixels "purs glacier"
// des pixels mixtes en bordure. Utilise le produit MOD10A1 Snow Albedo Daily Tile
// spécialement conçu pour l'analyse de l'albédo de la neige sur les surfaces glaciaires.

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

// 3. Fonction pour calculer la fraction de couverture (méthode corrigée pour respecter la projection MODIS)
function calculatePixelFraction(modisImage, glacierMask) {
  // Obtenir la projection native de l'image MODIS
  var modisProjection = modisImage.projection();
  
  // Reprojecter directement le masque glacier dans la projection MODIS
  // tout en conservant la résolution fine de 30m
  var raster30 = ee.Image.constant(1)
    .updateMask(glacierMask)
    .unmask(0)
    .reproject(modisProjection, null, 30);
  
  // Effectuer l'agrégation DANS la projection MODIS native
  // pour respecter exactement la grille des pixels MODIS
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
// │ SECTION 3 : FONCTIONS D'ANALYSE D'ALBÉDO DE NEIGE PAR FRACTION                         │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 5. Fonction pour analyser l'albédo de neige d'une année selon les fractions
function calculateAnnualSnowAlbedoByFraction(year) {
  var yearStart = ee.Date.fromYMD(year, SUMMER_START_MONTH, 1);
  var yearEnd = ee.Date.fromYMD(year, SUMMER_END_MONTH, 30);
  
  // Charger les données MODIS MOD10A1 pour cette année (Snow Albedo Daily Tile)
  var snow_albedo_collection = ee.ImageCollection('MODIS/061/MOD10A1')
    .filterDate(yearStart, yearEnd)
    .filterBounds(glacier_geometry)
    .select(['Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA']);
  
  // Traiter chaque image de la collection
  var processed_collection = snow_albedo_collection.map(function(img) {
    var quality = img.select('NDSI_Snow_Cover_Basic_QA');
    var snow_albedo = img.select('Snow_Albedo_Daily_Tile');
    
    // Filtres de qualité pour MOD10A1: 0=Best, 1=Good, 2=Ok
    var good_quality_mask = quality.lte(2);
    
    // Masque pour valeurs valides d'albédo de neige (≤100%)
    var valid_albedo_mask = snow_albedo.lte(100);
    
    // Conversion de pourcentage (1-100) vers décimal (0.01-1.00)
    var albedo_scaled = snow_albedo.divide(100)
      .updateMask(good_quality_mask)
      .updateMask(valid_albedo_mask);
    
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

// 6. Calculer l'albédo de neige par fraction pour toutes les années
print('Calcul des statistiques annuelles d\'albédo de neige par fraction de couverture...');
var annual_snow_albedo_by_fraction = ee.FeatureCollection(STUDY_YEARS.map(calculateAnnualSnowAlbedoByFraction));

print('Statistiques annuelles par classe de fraction (MOD10A1 Snow Albedo):', annual_snow_albedo_by_fraction);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 5 : VISUALISATIONS COMPARATIVES                                               │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 7. Créer des graphiques d'évolution temporelle par classe
var createTemporalChart = function(className, color) {
  var fieldName = className + '_mean';
  return ui.Chart.feature.byFeature(annual_snow_albedo_by_fraction, 'year', fieldName)
    .setChartType('LineChart')
    .setOptions({
      title: 'Évolution albédo de neige - Classe: ' + className.replace('_', ' '),
      hAxis: {title: 'Année', format: '####'},
      vAxis: {title: 'Albédo de neige moyen', viewWindow: {min: 0.3, max: 0.9}},
      series: {0: {color: color, lineWidth: 2, pointSize: 4}},
      height: 300
    });
};

// Créer un graphique pour chaque classe
print('');
print('=== GRAPHIQUES PAR CLASSE DE FRACTION (ALBÉDO DE NEIGE MOD10A1) ===');
print(createTemporalChart('border', 'red'));        // 0-25%
print(createTemporalChart('mixed_low', 'orange'));   // 25-50%
print(createTemporalChart('mixed_high', 'yellow'));  // 50-75%
print(createTemporalChart('mostly_ice', 'lightblue')); // 75-90%
print(createTemporalChart('pure_ice', 'blue'));      // 90-100%

// 8. Graphique comparatif multi-classes
var multiClassChart = ui.Chart.feature.byFeature(
    annual_snow_albedo_by_fraction, 
    'year', 
    ['border_mean', 'mixed_low_mean', 'mixed_high_mean', 'mostly_ice_mean', 'pure_ice_mean']
  )
  .setChartType('LineChart')
  .setOptions({
    title: 'Comparaison évolution albédo de neige par classe de fraction de couverture (MOD10A1)',
    hAxis: {title: 'Année', format: '####'},
    vAxis: {title: 'Albédo de neige moyen', viewWindow: {min: 0.3, max: 0.9}},
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
print('GRAPHIQUE COMPARATIF MULTI-CLASSES (ALBÉDO DE NEIGE MOD10A1) :');
print(multiClassChart);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 6 : ANALYSES DE TENDANCE PAR CLASSE                                            │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 9. Calculer les tendances pour chaque classe
var calculateTrend = function(className) {
  var fieldName = className + '_mean';
  var years = annual_snow_albedo_by_fraction.aggregate_array('year');
  var values = annual_snow_albedo_by_fraction.aggregate_array(fieldName);
  
  var trend_data = ee.List.sequence(0, STUDY_YEARS.size().subtract(1)).map(function(i) {
    return ee.Feature(null, {
      'year': ee.List(years).get(i),
      'albedo': ee.List(values).get(i)
    });
  });
  
  var trend_fc = ee.FeatureCollection(trend_data);
  
  // Calculer la régression linéaire et la corrélation séparément
  var linearFit = trend_fc.reduceColumns({
    reducer: ee.Reducer.linearFit(),
    selectors: ['year', 'albedo']
  });
  
  var correlation = trend_fc.reduceColumns({
    reducer: ee.Reducer.pearsonsCorrelation(),
    selectors: ['year', 'albedo']
  });
  
  return ee.Feature(null, {
    'class': className,
    'slope': linearFit.get('scale'),
    'offset': linearFit.get('offset'),
    'correlation': correlation.get('correlation')
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
print('ANALYSES DE TENDANCE PAR CLASSE (ALBÉDO DE NEIGE MOD10A1) :');
print('(pente = changement d\'albédo de neige par an, correlation = coefficient de corrélation)', trend_analyses);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 7 : VISUALISATION CARTOGRAPHIQUE                                              │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 10. Interface interactive pour choisir la date de visualisation
print('');
print('=== SÉLECTION DE DATE INTERACTIVE (ALBÉDO DE NEIGE MOD10A1) ===');

// Créer un sélecteur de date
var dateSlider = ui.DateSlider({
  start: '2010-06-01',
  end: '2024-09-30',
  value: '2020-07-15',
  period: 1,
  style: {width: '300px'}
});

var dateLabel = ui.Label('Choisir une date pour la visualisation d\'albédo de neige:');
var selectedDateLabel = ui.Label('Date sélectionnée: 2020-07-15');

// Fonction pour mettre à jour la visualisation selon la date choisie
var updateVisualization = function() {
  // dateSlider.getValue() retourne un array [startDate, endDate]
  var dateRange = dateSlider.getValue();
  
  // Prendre la première date (startDate) du range et s'assurer que c'est un Date object
  var timestamp = dateRange[0];
  var js_date = new Date(timestamp);
  
  // Convertir en ee.Date pour les opérations Earth Engine
  var selected_date = ee.Date(js_date);
  
  // Formater la date pour l'affichage (compatible avec GEE)
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
    .select(['Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA'])
    .first();
  
  var example_fraction = calculatePixelFraction(example_image, glacier_mask);
  var example_masks = createFractionMasks(example_fraction, FRACTION_THRESHOLDS);
  
  // Préparer l'albédo de neige pour visualisation
  var example_snow_albedo = example_image.select('Snow_Albedo_Daily_Tile')
    .divide(100)
    .updateMask(example_image.select('NDSI_Snow_Cover_Basic_QA').lte(2))
    .updateMask(example_image.select('Snow_Albedo_Daily_Tile').lte(100));
  
  // Sauvegarder l'état de visibilité des couches existantes
  var layers = Map.layers();
  var layerStates = [];
  
  // Parcourir les couches existantes pour sauvegarder leur état de visibilité
  for (var i = 1; i < layers.length(); i++) { // Commencer à 1 pour ignorer le masque glacier
    var layer = layers.get(i);
    layerStates.push({
      name: layer.getName(),
      visible: layer.getShown()
    });
  }
  
  // Effacer les couches précédentes (sauf la première - masque glacier)
  while (layers.length() > 1) {
    Map.remove(layers.get(layers.length() - 1));
  }
  
  // Définir toutes les nouvelles couches avec leurs données
  var newLayers = [
    {
      name: '1. Fraction de couverture - ' + dateString,
      image: example_fraction.updateMask(example_fraction.gt(0)),
      vis: {min: 0, max: 1, palette: ['red', 'orange', 'yellow', 'lightblue', 'blue']},
      defaultVisible: true
    },
    {
      name: '2. Albédo neige 0-25% (bordure)',
      image: example_snow_albedo.updateMask(example_masks.border),
      vis: {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']},
      defaultVisible: false
    },
    {
      name: '3. Albédo neige 25-50% (mixte bas)',
      image: example_snow_albedo.updateMask(example_masks.mixed_low),
      vis: {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']},
      defaultVisible: false
    },
    {
      name: '4. Albédo neige 50-75% (mixte haut)',
      image: example_snow_albedo.updateMask(example_masks.mixed_high),
      vis: {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']},
      defaultVisible: true
    },
    {
      name: '5. Albédo neige 75-90% (majoritaire)',
      image: example_snow_albedo.updateMask(example_masks.mostly_ice),
      vis: {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']},
      defaultVisible: true
    },
    {
      name: '6. Albédo neige 90-100% (pur)',
      image: example_snow_albedo.updateMask(example_masks.pure_ice),
      vis: {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']},
      defaultVisible: true
    }
  ];
  
  // Ajouter chaque nouvelle couche en préservant l'état de visibilité
  newLayers.forEach(function(layerDef) {
    // Chercher si cette couche était visible dans l'état précédent
    var wasVisible = layerDef.defaultVisible; // Valeur par défaut
    
    // Vérifier l'état précédent (en ignorant la date dans le nom)
    layerStates.forEach(function(state) {
      var baseName = layerDef.name.split(' - ')[0]; // Enlever la partie date
      var stateBaseName = state.name.split(' - ')[0];
      if (baseName === stateBaseName) {
        wasVisible = state.visible;
      }
    });
    
    // Ajouter la couche avec l'état de visibilité préservé
    Map.addLayer(layerDef.image, layerDef.vis, layerDef.name, wasVisible);
  });
};

// Bouton pour mettre à jour la visualisation
var updateButton = ui.Button({
  label: 'Mettre à jour la carte',
  onClick: updateVisualization,
  style: {width: '200px'}
});

// Ajouter les widgets au panneau
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

// Initialisation avec la date par défaut
var example_date = ee.Date('2020-07-15');
var example_image = ee.ImageCollection('MODIS/061/MOD10A1')
  .filterDate(example_date, example_date.advance(5, 'day'))
  .filterBounds(glacier_geometry)
  .select(['Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA'])
  .first();

var example_fraction = calculatePixelFraction(example_image, glacier_mask);
var example_masks = createFractionMasks(example_fraction, FRACTION_THRESHOLDS);

// Préparer l'albédo de neige pour visualisation
var example_snow_albedo = example_image.select('Snow_Albedo_Daily_Tile')
  .divide(100)
  .updateMask(example_image.select('NDSI_Snow_Cover_Basic_QA').lte(2))
  .updateMask(example_image.select('Snow_Albedo_Daily_Tile').lte(100));

// Centrer la carte
Map.centerObject(glacier_geometry, 12);

// Ajouter les couches
Map.addLayer(glacier_mask.selfMask(), {palette: ['lightgray'], opacity: 0.3}, '0. Masque glacier');
Map.addLayer(example_fraction.updateMask(example_fraction.gt(0)), 
  {min: 0, max: 1, palette: ['red', 'orange', 'yellow', 'lightblue', 'blue']}, 
  '1. Fraction de couverture');

// Paramètres d'albédo de neige
var snowAlbedoVis = {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']};

// Ajouter l'albédo de neige pour chaque classe
Map.addLayer(example_snow_albedo.updateMask(example_masks.border), snowAlbedoVis, '2. Albédo neige 0-25% (bordure)', false);
Map.addLayer(example_snow_albedo.updateMask(example_masks.mixed_low), snowAlbedoVis, '3. Albédo neige 25-50% (mixte bas)', false);
Map.addLayer(example_snow_albedo.updateMask(example_masks.mixed_high), snowAlbedoVis, '4. Albédo neige 50-75% (mixte haut)');
Map.addLayer(example_snow_albedo.updateMask(example_masks.mostly_ice), snowAlbedoVis, '5. Albédo neige 75-90% (majoritaire)');
Map.addLayer(example_snow_albedo.updateMask(example_masks.pure_ice), snowAlbedoVis, '6. Albédo neige 90-100% (pur)');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 8 : EXPORTS                                                                   │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 11. Export des statistiques par fraction (albédo de neige)
Export.table.toDrive({
  collection: annual_snow_albedo_by_fraction,
  description: 'Saskatchewan_Snow_Albedo_By_Fraction_MOD10A1_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_annual_fractions_2010_2024',
  fileFormat: 'CSV'
});

// 12. Export des analyses de tendance (albédo de neige)
Export.table.toDrive({
  collection: trend_analyses,
  description: 'Saskatchewan_Snow_Albedo_Trends_By_Fraction_MOD10A1',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_trends_fractions_2010_2024',
  fileFormat: 'CSV'
});

// 13. Export de la carte de fraction d'exemple
Export.image.toDrive({
  image: example_fraction,
  description: 'Saskatchewan_Fraction_Map_Snow_Albedo_MOD10A1',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_maps_fractions_example',
  scale: 500,
  region: glacier_geometry,
  maxPixels: 1e9
});

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 9 : ANALYSE QUOTIDIENNE PAR FRACTION DE COUVERTURE (ALBÉDO DE NEIGE)           │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 14. Fonction pour analyser les statistiques quotidiennes d'albédo de neige par fraction (optimisée pour Mann-Kendall)
function analyzeDailySnowAlbedoByFraction(img) {
  var date = img.date();
  var quality = img.select('NDSI_Snow_Cover_Basic_QA');
  var snow_albedo = img.select('Snow_Albedo_Daily_Tile').divide(100);
  
  // Calculer la fraction de couverture pour cette image
  var fraction = calculatePixelFraction(img, glacier_mask);
  var masks = createFractionMasks(fraction, FRACTION_THRESHOLDS);
  
  // Masques de qualité pour MOD10A1: 0=Best, 1=Good, 2=Ok
  var goodQualityMask = quality.lte(2);
  var validAlbedoMask = img.select('Snow_Albedo_Daily_Tile').lte(100);
  
  // Calculer les statistiques pour chaque classe de fraction
  var stats = {};
  var classNames = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice'];
  var totalValidPixels = 0;
  
  classNames.forEach(function(className) {
    // Combiner masques de qualité, validité et fraction
    var classMask = masks[className].and(goodQualityMask).and(validAlbedoMask);
    var validSnowAlbedo = snow_albedo.updateMask(classMask);
    
    // Calculer les statistiques d'albédo de neige streamlinées pour cette classe
    var classStats = validSnowAlbedo.reduceRegion({
      reducer: ee.Reducer.mean().combine(
        ee.Reducer.median(), '', true
      ).combine(
        ee.Reducer.count(), '', true
      ),
      geometry: glacier_geometry,
      scale: 500,
      maxPixels: 1e9,
      bestEffort: true
    });
    
    // Calculer le nombre total de pixels dans cette classe (avec fraction > 0)
    var fractionPixelCount = masks[className].reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: glacier_geometry,
      scale: 500,
      maxPixels: 1e9,
      bestEffort: true
    }).get('constant');
    
    // Calculer les statistiques essentielles
    var pixelCount = classStats.get('Snow_Albedo_Daily_Tile_count');
    
    // Stocker les statistiques optimisées pour Mann-Kendall
    stats[className + '_mean'] = classStats.get('Snow_Albedo_Daily_Tile_mean');
    stats[className + '_median'] = classStats.get('Snow_Albedo_Daily_Tile_median');
    stats[className + '_pixel_count'] = pixelCount;
    stats[className + '_data_quality'] = ee.Algorithms.If(
      ee.Algorithms.IsEqual(fractionPixelCount, 0),
      0,
      ee.Number(pixelCount).divide(ee.Number(fractionPixelCount)).multiply(100)
    );
  });
  
  // Calculer les informations temporelles pour analyse de tendance
  var year = date.get('year');
  var doy = date.getRelative('day', 'year').add(1); // DOY commence à 1
  var decimal_year = year.add(doy.divide(365.25));
  
  // Déterminer la saison pour analyse saisonnière Mann-Kendall
  var month = date.get('month');
  var season = ee.Algorithms.If(
    month.lte(7), 'early_summer',  // Juin-Juillet
    ee.Algorithms.If(
      month.eq(8), 'mid_summer',   // Août
      'late_summer'                // Septembre
    )
  );
  
  // Calculer le total des pixels valides pour seuil qualité
  var totalValid = ee.Number(stats['border_pixel_count']).add(
    ee.Number(stats['mixed_low_pixel_count'])).add(
    ee.Number(stats['mixed_high_pixel_count'])).add(
    ee.Number(stats['mostly_ice_pixel_count'])).add(
    ee.Number(stats['pure_ice_pixel_count']));
  
  // Ajouter les informations temporelles et de qualité
  stats['date'] = date.format('YYYY-MM-dd');
  stats['year'] = year;
  stats['doy'] = doy;
  stats['decimal_year'] = decimal_year;
  stats['season'] = season;
  stats['total_valid_pixels'] = totalValid;
  stats['min_pixels_threshold'] = totalValid.gte(10); // Seuil minimum pour analyse fiable
  stats['system:time_start'] = date.millis();
  
  return ee.Feature(null, stats);
}

// 15. Calculer les statistiques quotidiennes d'albédo de neige pour toute la période d'étude
print('');
print('=== CALCUL DES STATISTIQUES QUOTIDIENNES D\'ALBÉDO DE NEIGE PAR FRACTION (MOD10A1) ===');
print('Traitement des données quotidiennes MOD10A1 2010-2024 (juin-septembre)...');

// Charger la collection complète MOD10A1 pour l'analyse quotidienne
var dailySnowCollection = ee.ImageCollection('MODIS/061/MOD10A1')
  .filterDate('2010-01-01', '2024-12-31')
  .filterBounds(glacier_geometry)
  .filter(ee.Filter.calendarRange(SUMMER_START_MONTH, SUMMER_END_MONTH, 'month'))
  .select(['Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA']);

// Appliquer l'analyse quotidienne d'albédo de neige
var dailySnowAlbedoByFraction = dailySnowCollection.map(analyzeDailySnowAlbedoByFraction);

print('Statistiques quotidiennes d\'albédo de neige par fraction calculées:', dailySnowAlbedoByFraction.size(), 'jours');

// 16. Créer un graphique de l'évolution quotidienne par classe principale (Mann-Kendall ready)
var dailySnowChart = ui.Chart.feature.byFeature(
    dailySnowAlbedoByFraction, 
    'decimal_year', 
    ['border_mean', 'mixed_high_mean', 'mostly_ice_mean', 'pure_ice_mean']
  )
  .setChartType('LineChart')
  .setOptions({
    title: 'Évolution quotidienne albédo de neige par fraction - MOD10A1 optimisé Mann-Kendall (2010-2024)',
    hAxis: {title: 'Année (décimale)', format: '#.##'},
    vAxis: {title: 'Albédo de neige moyen', viewWindow: {min: 0.3, max: 0.9}},
    series: {
      0: {color: 'red', lineWidth: 1, pointSize: 2},      // Border
      1: {color: 'orange', lineWidth: 1, pointSize: 2},   // Mixed high
      2: {color: 'lightblue', lineWidth: 2, pointSize: 2}, // Mostly ice
      3: {color: 'blue', lineWidth: 2, pointSize: 3}      // Pure ice
    },
    legend: {
      position: 'top',
      labels: ['0-25% (bordure)', '50-75% (mixte haut)', '75-90% (majoritaire)', '90-100% (pur)']
    },
    height: 400,
    interpolateNulls: false
  });

print('');
print('GRAPHIQUE D\'ÉVOLUTION QUOTIDIENNE (ALBÉDO DE NEIGE MOD10A1) :');
print(dailySnowChart);

// 17. Export des statistiques quotidiennes d'albédo de neige par fraction (optimisé Mann-Kendall)
Export.table.toDrive({
  collection: dailySnowAlbedoByFraction,
  description: 'Saskatchewan_MOD10A1_Daily_Stats_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_snow_daily_stats_2010_2024',
  fileFormat: 'CSV'
});

print('');
print('EXPORT CONFIGURÉ POUR MANN-KENDALL & SEN\'S SLOPE (ALBÉDO DE NEIGE MOD10A1) :');
print('✓ Fichier: MOD10A1_snow_daily_stats_2010_2024.csv');
print('✓ Contenu: Statistiques quotidiennes d\'albédo de neige optimisées pour analyse de tendance');
print('✓ Dataset: MOD10A1.061 Snow_Albedo_Daily_Tile');
print('✓ Période: Étés 2010-2024 (juin-septembre)');
print('✓ Variables par classe: mean, median, pixel_count, data_quality');
print('✓ Variables temporelles: date, year, doy, decimal_year, season');
print('✓ Qualité des données: total_valid_pixels, min_pixels_threshold');
print('');
print('STRUCTURE CSV EXACTE (35 colonnes) :');
print('date, year, doy, decimal_year, season,');
print('border_mean, border_median, border_pixel_count, border_data_quality,');
print('mixed_low_mean, mixed_low_median, mixed_low_pixel_count, mixed_low_data_quality,');
print('mixed_high_mean, mixed_high_median, mixed_high_pixel_count, mixed_high_data_quality,');
print('mostly_ice_mean, mostly_ice_median, mostly_ice_pixel_count, mostly_ice_data_quality,');
print('pure_ice_mean, pure_ice_median, pure_ice_pixel_count, pure_ice_data_quality,');
print('total_valid_pixels, min_pixels_threshold, system:time_start');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 10 : ANALYSE DE LA DISTRIBUTION QUOTIDIENNE DE QUALITÉ GLOBALE (MOD10A1)       │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 18. Graphique de distribution quotidienne de la qualité des pixels MOD10A1 (saison de fonte)
print('');
print('=== ANALYSE DE LA QUALITÉ DES PIXELS MOD10A1 PAR JOUR (SAISONS DE FONTE 2010-2024) ===');

// Fonction pour analyser la distribution de qualité globale MOD10A1 pour chaque image
function analyzeSnowQualityDistribution(img) {
  var date = img.date();
  var quality = img.select('NDSI_Snow_Cover_Basic_QA');
  
  // Créer des masques pour chaque niveau de qualité MOD10A1 dans le glacier
  var q0 = quality.eq(0).and(glacier_mask);  // Best quality
  var q1 = quality.eq(1).and(glacier_mask);  // Good quality
  var q2 = quality.eq(2).and(glacier_mask);  // Ok quality
  var q_other = quality.gt(2).and(glacier_mask);  // Night/Ocean/Other
  
  // Compter les pixels pour chaque niveau de qualité de manière optimisée
  var qualityStats = ee.Image.cat([q0, q1, q2, q_other]).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    bestEffort: true
  });
  
  // Extraire les comptages
  var count_q0 = qualityStats.get('NDSI_Snow_Cover_Basic_QA');
  var count_q1 = qualityStats.get('NDSI_Snow_Cover_Basic_QA_1');
  var count_q2 = qualityStats.get('NDSI_Snow_Cover_Basic_QA_2');
  var count_other = qualityStats.get('NDSI_Snow_Cover_Basic_QA_3');
  
  return ee.Feature(null, {
    'system:time_start': date.millis(),
    'date': date.format('YYYY-MM-dd'),
    'quality_0_best': count_q0,
    'quality_1_good': count_q1,
    'quality_2_ok': count_q2,
    'quality_other_night_ocean': count_other,
    'total_pixels': ee.Number(count_q0).add(count_q1).add(count_q2).add(count_other)
  });
}

// Analyser toute la période 2010-2024 (été seulement pour optimiser)
print('Calcul de la distribution de qualité globale MOD10A1...');
var globalSnowQualityDistribution = dailySnowCollection
  .select('NDSI_Snow_Cover_Basic_QA')
  .map(analyzeSnowQualityDistribution);

print('Distribution de qualité globale MOD10A1 calculée pour:', globalSnowQualityDistribution.size(), 'images');

// Filtrer pour une année spécifique (exemple : 2020) pour le graphique détaillé
var singleYearSnowQuality = globalSnowQualityDistribution.filter(ee.Filter.calendarRange(2020, 2020, 'year'));

// Créer un graphique simplifié pour éviter les erreurs de format de date
var qualityChart2020 = ui.Chart.feature.groups(
    singleYearSnowQuality,
    'date',
    'quality_0_best',
    'quality_0_best'
  )
  .setChartType('LineChart')
  .setOptions({
    title: 'Évolution qualité MOD10A1 (Qualité Best) - Saison de fonte 2020',
    hAxis: {title: 'Date'},
    vAxis: {title: 'Nombre de pixels qualité Best'},
    colors: ['#2166ac'],
    lineWidth: 2,
    pointSize: 3,
    height: 400
  });

// Alternative : Graphique en barres empilées corrigé
var globalSnowStackedChart = ui.Chart.feature.byFeature(
    singleYearSnowQuality,
    'system:time_start',  // Utiliser le timestamp au lieu de 'date'
    ['quality_0_best', 'quality_1_good', 'quality_2_ok', 'quality_other_night_ocean']
  )
  .setChartType('ColumnChart')
  .setOptions({
    title: 'Distribution quotidienne de la qualité des pixels MOD10A1 Snow Albedo - Saison de fonte 2020',
    hAxis: {
      title: 'Date',
      format: 'MM/dd'
    },
    vAxis: {title: 'Nombre de pixels'},
    colors: ['#2166ac', '#92c5de', '#fddbc7', '#d6604d'],
    isStacked: true,
    height: 500,
    legend: {
      position: 'top',
      labels: ['Qualité 0 (Best)', 'Qualité 1 (Good)', 'Qualité 2 (Ok)', 'Autre (Night/Ocean)']
    }
  });

print('');
print('GRAPHIQUE DE QUALITÉ GLOBALE MOD10A1 :');
print(globalSnowStackedChart);

// Export de l'analyse de qualité globale MOD10A1
Export.table.toDrive({
  collection: globalSnowQualityDistribution,
  description: 'Saskatchewan_Snow_Quality_Distribution_MOD10A1_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_quality_daily_2010_2024',
  fileFormat: 'CSV'
});

print('');
print('EXPORT QUALITÉ GLOBALE MOD10A1 CONFIGURÉ :');
print('✓ Fichier: snow_quality_distribution_daily_mod10a1_2010_2024.csv');
print('✓ Variables: quality_0_best, quality_1_good, quality_2_ok, quality_other_night_ocean');
print('✓ Métriques: total_pixels');
print('✓ Utilité: Vue d\'ensemble de la qualité MOD10A1 sur tout le glacier');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 11 : RÉSUMÉ ET INTERPRÉTATION (ALBÉDO DE NEIGE MOD10A1)                        │
// └────────────────────────────────────────────────────────────────────────────────────────┘

print('');
print('=== RÉSUMÉ ANALYSE PAR FRACTION - ALBÉDO DE NEIGE MOD10A1 OPTIMISÉE MANN-KENDALL ===');
print('');
print('DATASET UTILISÉ :');
print('• MOD10A1.061 Snow_Albedo_Daily_Tile (MODIS/Terra)');
print('• Résolution: 500m, cadence quotidienne');
print('• Spécialisé pour l\'albédo de neige sur surfaces glaciaires');
print('• Qualité: NDSI_Snow_Cover_Basic_QA (0=Best, 1=Good, 2=Ok)');
print('');
print('CLASSES ANALYSÉES :');
print('• 0-25% : Pixels de bordure (faible couverture glacier)');
print('• 25-50% : Pixels mixtes faible (transition)');
print('• 50-75% : Pixels mixtes élevé (majoritairement glacier)');
print('• 75-90% : Pixels majoritairement glacier');
print('• 90-100% : Pixels quasi-purs glacier');
print('');
print('AMÉLIORATIONS MOD10A1 vs MCD43A3 :');
print('• Spécialisé pour albédo de neige (vs albédo général)');
print('• Cadence quotidienne (vs composite 16 jours)');
print('• Algorithme optimisé pour surfaces neigeuses');
print('• Meilleure détection des conditions de neige fraîche');
print('• Qualité simplifiée mais robuste (3 niveaux principaux)');
print('');
print('STATISTIQUES OPTIMISÉES POUR ANALYSE DE TENDANCE :');
print('• Variables principales: mean, median (par classe)');
print('• Métriques qualité: pixel_count, data_quality (par classe)');
print('• Variables temporelles: date, year, doy, decimal_year, season');
print('• Seuils qualité: total_valid_pixels, min_pixels_threshold');
print('');
print('ANALYSES STATISTIQUES SUPPORTÉES :');
print('• Test Mann-Kendall (tendance monotone)');
print('• Pente de Sen (magnitude du changement)');
print('• Mann-Kendall saisonnier (early/mid/late summer)');
print('• Filtrage par seuil de qualité (≥10 pixels)');
print('• Analyse par classe de pureté');
print('');
print('EXPORTS GÉNÉRÉS :');
print('• Statistiques annuelles par fraction (MOD10A1)');
print('• Analyses de tendance par classe (MOD10A1)');
print('• CSV quotidien optimisé Mann-Kendall (MOD10A1)');
print('• CSV qualité globale quotidienne MOD10A1');
print('• Cartes de fraction d\'exemple (albédo de neige)');
print('');
print('APPLICATIONS SPÉCIFIQUES ALBÉDO DE NEIGE :');
print('• Suivi de l\'évolution saisonnière de l\'albédo glaciaire');
print('• Détection des événements de fonte/regel');
print('• Analyse des patterns d\'accumulation de neige');
print('• Validation des modèles énergétiques glaciaires');
print('• Comparaison avec observations in-situ d\'albédo');
print('• Études climatiques sur les glaciers de montagne');
print('• Évaluation de la réponse glaciaire au changement climatique');

// FIN DU SCRIPT MODIFIÉ POUR MOD10A1 SNOW ALBEDO