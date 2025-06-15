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
print('ANALYSES DE TENDANCE PAR CLASSE :');
print('(pente = changement d\'albédo par an, correlation = coefficient de corrélation)', trend_analyses);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 7 : VISUALISATION CARTOGRAPHIQUE                                              │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 10. Interface interactive pour choisir la date de visualisation
print('');
print('=== SÉLECTION DE DATE INTERACTIVE ===');

// Créer un sélecteur de date
var dateSlider = ui.DateSlider({
  start: '2010-06-01',
  end: '2024-09-30',
  value: '2020-07-15',
  period: 1,
  style: {width: '300px'}
});

var dateLabel = ui.Label('Choisir une date pour la visualisation:');
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
  
  // Charger l'image pour la date sélectionnée
  var example_image = ee.ImageCollection('MODIS/061/MCD43A3')
    .filterDate(selected_date, selected_date.advance(5, 'day'))
    .filterBounds(glacier_geometry)
    .select(['Albedo_WSA_shortwave', 'BRDF_Albedo_Band_Mandatory_Quality_shortwave'])
    .first();
  
  var example_fraction = calculatePixelFraction(example_image, glacier_mask);
  var example_masks = createFractionMasks(example_fraction, FRACTION_THRESHOLDS);
  
  // Préparer l'albédo pour visualisation
  var example_albedo = example_image.select('Albedo_WSA_shortwave')
    .multiply(0.001)
    .updateMask(example_image.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave').lte(1));
  
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
      name: '2. Albédo 0-25% (bordure)',
      image: example_albedo.updateMask(example_masks.border),
      vis: {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']},
      defaultVisible: false
    },
    {
      name: '3. Albédo 25-50% (mixte bas)',
      image: example_albedo.updateMask(example_masks.mixed_low),
      vis: {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']},
      defaultVisible: false
    },
    {
      name: '4. Albédo 50-75% (mixte haut)',
      image: example_albedo.updateMask(example_masks.mixed_high),
      vis: {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']},
      defaultVisible: true
    },
    {
      name: '5. Albédo 75-90% (majoritaire)',
      image: example_albedo.updateMask(example_masks.mostly_ice),
      vis: {min: 0.3, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']},
      defaultVisible: true
    },
    {
      name: '6. Albédo 90-100% (pur)',
      image: example_albedo.updateMask(example_masks.pure_ice),
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
  fileNamePrefix: 'fraction_map_2020',
  scale: 500,
  region: glacier_geometry,
  maxPixels: 1e9
});

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 9 : ANALYSE QUOTIDIENNE PAR FRACTION DE COUVERTURE                            │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 14. Fonction pour analyser les statistiques quotidiennes par fraction (optimisée pour Mann-Kendall)
function analyzeDailyAlbedoByFraction(img) {
  var date = img.date();
  var quality = img.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave');
  var albedo = img.select('Albedo_WSA_shortwave').multiply(0.001);
  
  // Calculer la fraction de couverture pour cette image
  var fraction = calculatePixelFraction(img, glacier_mask);
  var masks = createFractionMasks(fraction, FRACTION_THRESHOLDS);
  
  // Masque de qualité générale
  var goodQualityMask = quality.lte(1);
  
  // Calculer les statistiques pour chaque classe de fraction
  var stats = {};
  var classNames = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice'];
  var totalValidPixels = 0;
  
  classNames.forEach(function(className) {
    // Combiner masque de qualité et masque de fraction
    var classMask = masks[className].and(goodQualityMask);
    var validAlbedo = albedo.updateMask(classMask);
    
    // Calculer les statistiques d'albédo streamlinées pour cette classe
    var classStats = validAlbedo.reduceRegion({
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
    var pixelCount = classStats.get('Albedo_WSA_shortwave_count');
    
    // Stocker les statistiques optimisées pour Mann-Kendall
    stats[className + '_mean'] = classStats.get('Albedo_WSA_shortwave_mean');
    stats[className + '_median'] = classStats.get('Albedo_WSA_shortwave_median');
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

// 15. Calculer les statistiques quotidiennes pour toute la période d'étude
print('');
print('=== CALCUL DES STATISTIQUES QUOTIDIENNES PAR FRACTION ===');
print('Traitement des données quotidiennes 2010-2024 (juin-septembre)...');

// Charger la collection complète pour l'analyse quotidienne
var dailyCollection = ee.ImageCollection('MODIS/061/MCD43A3')
  .filterDate('2010-01-01', '2024-12-31')
  .filterBounds(glacier_geometry)
  .filter(ee.Filter.calendarRange(SUMMER_START_MONTH, SUMMER_END_MONTH, 'month'))
  .select(['Albedo_WSA_shortwave', 'BRDF_Albedo_Band_Mandatory_Quality_shortwave']);

// Appliquer l'analyse quotidienne
var dailyAlbedoByFraction = dailyCollection.map(analyzeDailyAlbedoByFraction);

print('Statistiques quotidiennes par fraction calculées:', dailyAlbedoByFraction.size(), 'jours');

// 16. Créer un graphique de l'évolution quotidienne par classe principale (Mann-Kendall ready)
var dailyChart = ui.Chart.feature.byFeature(
    dailyAlbedoByFraction, 
    'system:time_start', 
    ['border_mean', 'mixed_high_mean', 'mostly_ice_mean', 'pure_ice_mean']
  )
  .setChartType('LineChart')
  .setOptions({
    title: 'Évolution quotidienne albédo par fraction - Données optimisées Mann-Kendall (2010-2024)',
    hAxis: {title: 'Date', format: 'yyyy'},
    vAxis: {title: 'Albédo moyen', viewWindow: {min: 0.3, max: 0.9}},
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
print('GRAPHIQUE D\'ÉVOLUTION QUOTIDIENNE :');
print(dailyChart);

// 17. Export des statistiques quotidiennes par fraction (optimisé Mann-Kendall)
Export.table.toDrive({
  collection: dailyAlbedoByFraction,
  description: 'Saskatchewan_Daily_Albedo_MannKendall_Ready_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'daily_albedo_mann_kendall_ready_2010_2024',
  fileFormat: 'CSV'
});

print('');
print('EXPORT CONFIGURÉ POUR MANN-KENDALL & SEN\'S SLOPE :');
print('✓ Fichier: daily_albedo_mann_kendall_ready_2010_2024.csv');
print('✓ Contenu: Statistiques quotidiennes optimisées pour analyse de tendance');
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
// │ SECTION 10 : ANALYSE DE LA DISTRIBUTION QUOTIDIENNE DE QUALITÉ GLOBALE                │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 18. Graphique de distribution quotidienne de la qualité des pixels (saison de fonte)
print('');
print('=== ANALYSE DE LA QUALITÉ DES PIXELS PAR JOUR (SAISONS DE FONTE 2010-2024) ===');

// Fonction pour analyser la distribution de qualité globale pour chaque image
function analyzeQualityDistribution(img) {
  var date = img.date();
  var quality = img.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave');
  
  // Créer des masques pour chaque niveau de qualité dans le glacier
  var q0 = quality.eq(0).and(glacier_mask);  // Meilleure qualité
  var q1 = quality.eq(1).and(glacier_mask);  // Bonne qualité
  var q2 = quality.eq(2).and(glacier_mask);  // Qualité moyenne
  var q3 = quality.eq(3).and(glacier_mask);  // Faible qualité
  
  // Compter les pixels pour chaque niveau de qualité de manière optimisée
  var qualityStats = ee.Image.cat([q0, q1, q2, q3]).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    bestEffort: true
  });
  
  // Extraire les comptages
  var count_q0 = qualityStats.get('BRDF_Albedo_Band_Mandatory_Quality_shortwave');
  var count_q1 = qualityStats.get('BRDF_Albedo_Band_Mandatory_Quality_shortwave_1');
  var count_q2 = qualityStats.get('BRDF_Albedo_Band_Mandatory_Quality_shortwave_2');
  var count_q3 = qualityStats.get('BRDF_Albedo_Band_Mandatory_Quality_shortwave_3');
  
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
print('Calcul de la distribution de qualité globale...');
var globalQualityDistribution = dailyCollection
  .select('BRDF_Albedo_Band_Mandatory_Quality_shortwave')
  .map(analyzeQualityDistribution);

print('Distribution de qualité globale calculée pour:', globalQualityDistribution.size(), 'images');

// Créer le graphique en barres empilées
var globalStackedChart = ui.Chart.feature.byFeature(
    globalQualityDistribution, 
    'system:time_start', 
    ['quality_0_best', 'quality_1_good', 'quality_2_moderate', 'quality_3_poor']
  )
  .setChartType('ColumnChart')
  .setOptions({
    title: 'Distribution quotidienne de la qualité des pixels MODIS - Glacier entier (2010-2024)',
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

print('');
print('GRAPHIQUE DE QUALITÉ GLOBALE :');
print(globalStackedChart);

// Export de l'analyse de qualité globale
Export.table.toDrive({
  collection: globalQualityDistribution,
  description: 'Saskatchewan_Global_Quality_Distribution_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'global_quality_distribution_daily_2010_2024',
  fileFormat: 'CSV'
});

print('');
print('EXPORT QUALITÉ GLOBALE CONFIGURÉ :');
print('✓ Fichier: global_quality_distribution_daily_2010_2024.csv');
print('✓ Variables: quality_0_best, quality_1_good, quality_2_moderate, quality_3_poor');
print('✓ Métriques: total_pixels');
print('✓ Utilité: Vue d\'ensemble de la qualité sur tout le glacier');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 11 : RÉSUMÉ ET INTERPRÉTATION                                                 │
// └────────────────────────────────────────────────────────────────────────────────────────┘

print('');
print('=== RÉSUMÉ ANALYSE PAR FRACTION - OPTIMISÉE MANN-KENDALL ===');
print('');
print('CLASSES ANALYSÉES :');
print('• 0-25% : Pixels de bordure (faible couverture glacier)');
print('• 25-50% : Pixels mixtes faible (transition)');
print('• 50-75% : Pixels mixtes élevé (majoritairement glacier)');
print('• 75-90% : Pixels majoritairement glacier');
print('• 90-100% : Pixels quasi-purs glacier');
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
print('• Statistiques annuelles par fraction');
print('• Analyses de tendance par classe');
print('• CSV quotidien optimisé Mann-Kendall');
print('• CSV qualité globale quotidienne (NOUVEAU!)');
print('• Cartes de fraction d\'exemple');
print('');
print('APPLICATIONS STATISTIQUES :');
print('• Tests de tendance robustes (non-paramétriques)');
print('• Analyse de qualité des données temporelle');
print('• Détection de points de changement');
print('• Analyses saisonnières de variabilité');
print('• Comparaison tendances entre classes de pureté');
print('• Validation statistique des changements glaciaires');
print('• Évaluation fiabilité des données MODIS');

// FIN DU SCRIPT