// ╔════════════════════════════════════════════════════════════════════════════════════════╗
// ║              ANALYSE D'ALBÉDO POUR COUVERTURE DE NEIGE ÉLEVÉE (>90%)                   ║
// ║                           GLACIER SASKATCHEWAN 2010-2024                                ║
// ║                 MODIS MOD10A1.061 - Filtrage par NDSI Snow Cover                       ║
// ║                     Fichier: MOD10A1_albedo_high_snow_cover.js                         ║
// ╚════════════════════════════════════════════════════════════════════════════════════════╝

// Description : Analyse l'albédo de neige avec double filtrage : couverture de neige >50% 
// ET fraction glacier dans le pixel >75%. Cette approche permet de sélectionner les pixels 
// à dominance neigeuse ET majoritairement composés de glacier. Utilise le produit MOD10A1 
// qui fournit à la fois le pourcentage de couverture de neige (NDSI_Snow_Cover) et l'albédo 
// de neige (Snow_Albedo_Daily_Tile), combiné au calcul de fraction glacier par pixel.

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 1 : CONFIGURATION ET INITIALISATION                                            │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 1. Paramètres configurables
var SNOW_COVER_THRESHOLD = 50; // Seuil minimal de couverture de neige (%)
var GLACIER_FRACTION_THRESHOLD = 75; // Seuil minimal de fraction glacier dans le pixel (%)
var FRACTION_THRESHOLDS = [0.25, 0.50, 0.75, 0.90]; // Seuils de fraction glacier pour classes
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
  var modisProjection = modisImage.projection();
  
  var raster30 = ee.Image.constant(1)
    .updateMask(glacierMask)
    .unmask(0)
    .reproject(modisProjection, null, 30);
  
  var fraction = raster30
    .reduceResolution({
      reducer: ee.Reducer.mean(),
      maxPixels: 1024
    })
    .reproject(modisProjection, null, 500);
  
  return fraction;
}

// 4. Fonction pour créer des masques par classes de fraction
function createFractionMasks(fractionImage, thresholds) {
  var masks = {};
  masks['border'] = fractionImage.gt(0).and(fractionImage.lt(thresholds[0]));
  masks['mixed_low'] = fractionImage.gte(thresholds[0]).and(fractionImage.lt(thresholds[1]));
  masks['mixed_high'] = fractionImage.gte(thresholds[1]).and(fractionImage.lt(thresholds[2]));
  masks['mostly_ice'] = fractionImage.gte(thresholds[2]).and(fractionImage.lt(thresholds[3]));
  masks['pure_ice'] = fractionImage.gte(thresholds[3]);
  return masks;
}

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 3 : ANALYSE D'ALBÉDO AVEC FILTRE DE COUVERTURE DE NEIGE                        │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 5. Fonction pour analyser l'albédo annuel avec filtre de couverture de neige
function calculateAnnualAlbedoHighSnowCover(year) {
  var yearStart = ee.Date.fromYMD(year, SUMMER_START_MONTH, 1);
  var yearEnd = ee.Date.fromYMD(year, SUMMER_END_MONTH, 30);
  
  // Charger MOD10A1 avec tous les bands nécessaires
  var mod10a1_collection = ee.ImageCollection('MODIS/061/MOD10A1')
    .filterDate(yearStart, yearEnd)
    .filterBounds(glacier_geometry)
    .select(['NDSI_Snow_Cover', 'Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA']);
  
  // Traiter chaque image
  var processed_collection = mod10a1_collection.map(function(img) {
    var snow_cover = img.select('NDSI_Snow_Cover');
    var snow_albedo = img.select('Snow_Albedo_Daily_Tile');
    var quality = img.select('NDSI_Snow_Cover_Basic_QA');
    
    // Masques de qualité stricts (seulement Best=0 et Good=1)
    var good_quality_mask = quality.lte(1);
    
    // Calculer la fraction glacier pour cette image
    var fraction = calculatePixelFraction(img, glacier_mask);
    
    // Masque pour couverture de neige élevée (≥50%)
    var high_snow_cover_mask = snow_cover.gte(SNOW_COVER_THRESHOLD);
    
    // Masque pour fraction glacier élevée (≥75%)
    var high_glacier_fraction_mask = fraction.gte(GLACIER_FRACTION_THRESHOLD / 100);
    
    // Masque pour valeurs valides d'albédo (≤100%)
    var valid_albedo_mask = snow_albedo.lte(100);
    
    // Masque combiné : bonne qualité ET haute couverture neige ET haute fraction glacier ET albédo valide
    var combined_mask = good_quality_mask
      .and(high_snow_cover_mask)
      .and(high_glacier_fraction_mask)
      .and(valid_albedo_mask);
    
    // Conversion albédo de pourcentage vers décimal
    var albedo_scaled = snow_albedo.divide(100)
      .updateMask(combined_mask);
    
    // Créer les masques par classe de fraction
    var masks = createFractionMasks(fraction, FRACTION_THRESHOLDS);
    
    // Appliquer les masques de fraction
    var masked_albedos = [
      albedo_scaled.updateMask(masks.border).rename('border_high_snow'),
      albedo_scaled.updateMask(masks.mixed_low).rename('mixed_low_high_snow'),
      albedo_scaled.updateMask(masks.mixed_high).rename('mixed_high_high_snow'),
      albedo_scaled.updateMask(masks.mostly_ice).rename('mostly_ice_high_snow'),
      albedo_scaled.updateMask(masks.pure_ice).rename('pure_ice_high_snow')
    ];
    
    // Ajouter une bande pour compter les pixels avec haute couverture de neige
    var high_snow_count = combined_mask.rename('high_snow_pixel_count');
    
    return ee.Image.cat(masked_albedos.concat([high_snow_count]));
  });
  
  // Calculer les moyennes annuelles
  var annual_means = processed_collection.mean();
  
  // Calculer les statistiques
  var classNames = ['border_high_snow', 'mixed_low_high_snow', 'mixed_high_high_snow', 
                    'mostly_ice_high_snow', 'pure_ice_high_snow'];
  
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
  
  // Calculer aussi le nombre moyen de pixels haute neige
  var high_snow_stats = annual_means.select('high_snow_pixel_count').reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    bestEffort: true
  });
  
  // Construire les propriétés
  var properties = {
    'year': year,
    'snow_cover_threshold': SNOW_COVER_THRESHOLD,
    'glacier_fraction_threshold': GLACIER_FRACTION_THRESHOLD,
    'total_filtered_pixels': high_snow_stats.get('high_snow_pixel_count')
  };
  
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

// 6. Calculer pour toutes les années
print('Calcul des statistiques d\'albédo pour couverture de neige >' + SNOW_COVER_THRESHOLD + '%...');
var annual_albedo_high_snow = ee.FeatureCollection(STUDY_YEARS.map(calculateAnnualAlbedoHighSnowCover));

print('Statistiques annuelles (neige >' + SNOW_COVER_THRESHOLD + '%):', annual_albedo_high_snow);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 5 : VISUALISATIONS                                                            │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 7. Graphique d'évolution temporelle
var temporalChart = ui.Chart.feature.byFeature(
    annual_albedo_high_snow, 
    'year', 
    ['border_high_snow_mean', 'mixed_low_high_snow_mean', 'mixed_high_high_snow_mean', 
     'mostly_ice_high_snow_mean', 'pure_ice_high_snow_mean']
  )
  .setChartType('LineChart')
  .setOptions({
    title: 'Évolution albédo de neige (couverture >50%) par classe de fraction',
    hAxis: {title: 'Année', format: '####'},
    vAxis: {title: 'Albédo moyen', viewWindow: {min: 0.4, max: 0.9}},
    series: {
      0: {color: 'red', lineWidth: 2, pointSize: 3},
      1: {color: 'orange', lineWidth: 2, pointSize: 3},
      2: {color: 'yellow', lineWidth: 2, pointSize: 3},
      3: {color: 'lightblue', lineWidth: 2, pointSize: 3},
      4: {color: 'blue', lineWidth: 2, pointSize: 3}
    },
    legend: {
      position: 'top',
      labels: ['Bordure', 'Mixte bas', 'Mixte haut', 'Majoritaire', 'Pur']
    },
    height: 500
  });

print('');
print('GRAPHIQUE TEMPOREL (ALBÉDO NEIGE PURE):');
print(temporalChart);

// 8. Graphique du nombre de pixels haute neige
var pixelCountChart = ui.Chart.feature.byFeature(
    annual_albedo_high_snow, 
    'year', 
    'total_high_snow_pixels'
  )
  .setChartType('ColumnChart')
  .setOptions({
    title: 'Nombre de pixels avec couverture de neige >50% par année',
    hAxis: {title: 'Année', format: '####'},
    vAxis: {title: 'Nombre de pixels'},
    colors: ['steelblue'],
    height: 300
  });

print('');
print('ÉVOLUTION DU NOMBRE DE PIXELS HAUTE NEIGE:');
print(pixelCountChart);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 6 : ANALYSE QUOTIDIENNE AVEC FILTRE NEIGE                                     │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 9. Fonction pour l'analyse quotidienne
function analyzeDailyAlbedoHighSnowCover(img) {
  var date = img.date();
  var snow_cover = img.select('NDSI_Snow_Cover');
  var snow_albedo = img.select('Snow_Albedo_Daily_Tile');
  var quality = img.select('NDSI_Snow_Cover_Basic_QA');
  
  // Fraction glacier
  var fraction = calculatePixelFraction(img, glacier_mask);
  
  // Masques
  var good_quality_mask = quality.lte(1);
  var high_snow_cover_mask = snow_cover.gte(SNOW_COVER_THRESHOLD);
  var high_glacier_fraction_mask = fraction.gte(GLACIER_FRACTION_THRESHOLD / 100);
  var valid_albedo_mask = snow_albedo.lte(100);
  var combined_mask = good_quality_mask
    .and(high_snow_cover_mask)
    .and(high_glacier_fraction_mask)
    .and(valid_albedo_mask);
  
  // Albédo filtré
  var albedo_scaled = snow_albedo.divide(100).updateMask(combined_mask);
  
  // Masques par classe de fraction
  var masks = createFractionMasks(fraction, FRACTION_THRESHOLDS);
  
  // Calculer les statistiques par classe
  var stats = {};
  var classNames = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice'];
  
  classNames.forEach(function(className) {
    var classMask = masks[className];
    var validAlbedo = albedo_scaled.updateMask(classMask);
    
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
    
    stats[className + '_mean'] = classStats.get('Snow_Albedo_Daily_Tile_mean');
    stats[className + '_median'] = classStats.get('Snow_Albedo_Daily_Tile_median');
    stats[className + '_pixel_count'] = classStats.get('Snow_Albedo_Daily_Tile_count');
  });
  
  // Compter pixels totaux haute neige
  var total_high_snow = combined_mask.updateMask(fraction.gt(0)).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    bestEffort: true
  }).get('constant');
  
  // Ajouter métadonnées temporelles
  var year = date.get('year');
  var doy = date.getRelative('day', 'year').add(1);
  
  stats['date'] = date.format('YYYY-MM-dd');
  stats['year'] = year;
  stats['doy'] = doy;
  stats['decimal_year'] = year.add(doy.divide(365.25));
  stats['total_filtered_pixels'] = total_high_snow;
  stats['snow_cover_threshold'] = SNOW_COVER_THRESHOLD;
  stats['glacier_fraction_threshold'] = GLACIER_FRACTION_THRESHOLD;
  stats['system:time_start'] = date.millis();
  
  return ee.Feature(null, stats);
}

// 10. Calculer les statistiques quotidiennes
print('');
print('=== CALCUL DES STATISTIQUES QUOTIDIENNES (NEIGE >' + SNOW_COVER_THRESHOLD + '%) ===');

var dailyCollection = ee.ImageCollection('MODIS/061/MOD10A1')
  .filterDate('2010-01-01', '2024-12-31')
  .filterBounds(glacier_geometry)
  .filter(ee.Filter.calendarRange(SUMMER_START_MONTH, SUMMER_END_MONTH, 'month'))
  .select(['NDSI_Snow_Cover', 'Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA']);

var dailyAlbedoHighSnow = dailyCollection.map(analyzeDailyAlbedoHighSnowCover);

print('Nombre de jours analysés:', dailyAlbedoHighSnow.size());

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 7 : VISUALISATION CARTOGRAPHIQUE INTERACTIVE                                  │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 11. Interface interactive pour choisir la date de visualisation
print('');
print('=== SÉLECTION DE DATE INTERACTIVE (ALBÉDO NEIGE >50%) ===');

// Créer un sélecteur de date
var dateSlider = ui.DateSlider({
  start: '2010-06-01',
  end: '2024-09-30',
  value: '2020-07-15',
  period: 1,
  style: {width: '300px'}
});

var dateLabel = ui.Label('Visualisation albédo (neige >' + SNOW_COVER_THRESHOLD + '% ET glacier >' + GLACIER_FRACTION_THRESHOLD + '%):');
var selectedDateLabel = ui.Label('Date sélectionnée: 2020-07-15');

// Fonction pour mettre à jour la visualisation selon la date choisie
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
    .select(['NDSI_Snow_Cover', 'Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA'])
    .first();
  
  var example_snow_cover = example_image.select('NDSI_Snow_Cover');
  var example_albedo = example_image.select('Snow_Albedo_Daily_Tile').divide(100);
  var example_quality = example_image.select('NDSI_Snow_Cover_Basic_QA');
  var example_fraction = calculatePixelFraction(example_image, glacier_mask);
  
  // Masques
  var good_quality = example_quality.lte(1);
  var high_snow = example_snow_cover.gte(SNOW_COVER_THRESHOLD);
  var high_glacier_fraction = example_fraction.gte(GLACIER_FRACTION_THRESHOLD / 100);
  var valid_albedo = example_image.select('Snow_Albedo_Daily_Tile').lte(100);
  
  // Albédo filtré (double critère)
  var filtered_albedo = example_albedo
    .updateMask(good_quality)
    .updateMask(high_snow)
    .updateMask(high_glacier_fraction)
    .updateMask(valid_albedo);
  
  // Effacer les couches précédentes (sauf la première - masque glacier)
  var layers = Map.layers();
  while (layers.length() > 1) {
    Map.remove(layers.get(layers.length() - 1));
  }
  
  // Ajouter les nouvelles couches
  Map.addLayer(example_fraction.updateMask(example_fraction.gt(0)), 
    {min: 0, max: 1, palette: ['red', 'orange', 'yellow', 'lightblue', 'blue']}, 
    '1. Fraction glacier - ' + dateString);
  Map.addLayer(example_snow_cover.updateMask(example_fraction.gt(0)), 
    {min: 0, max: 100, palette: ['brown', 'yellow', 'green', 'cyan', 'blue', 'white']}, 
    '2. Couverture de neige (%)');
  Map.addLayer(high_snow.updateMask(example_fraction.gt(0)), 
    {palette: ['black', 'white']}, 
    '3. Masque neige >' + SNOW_COVER_THRESHOLD + '%');
  Map.addLayer(high_glacier_fraction.updateMask(example_fraction.gt(0)), 
    {palette: ['black', 'cyan']}, 
    '4. Masque glacier >' + GLACIER_FRACTION_THRESHOLD + '%');
  Map.addLayer(filtered_albedo, 
    {min: 0.4, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']}, 
    '5. Albédo filtré (double critère)');
  
  // Calculer et afficher les statistiques du jour
  var dayStats = filtered_albedo.reduceRegion({
    reducer: ee.Reducer.mean().combine(ee.Reducer.count(), '', true),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    bestEffort: true
  });
  
  dayStats.evaluate(function(stats) {
    var meanAlbedo = stats.Snow_Albedo_Daily_Tile_mean;
    var pixelCount = stats.Snow_Albedo_Daily_Tile_count;
    
    var statsText = 'Statistiques du ' + dateString + ':\n';
    if (meanAlbedo !== null) {
      statsText += '• Albédo moyen (double critère): ' + 
                   (meanAlbedo ? meanAlbedo.toFixed(3) : 'N/A') + '\n';
      statsText += '• Nombre de pixels: ' + (pixelCount || 0) + '\n';
      statsText += '• Critères: neige >' + SNOW_COVER_THRESHOLD + '% ET glacier >' + GLACIER_FRACTION_THRESHOLD + '%';
    } else {
      statsText += '• Aucun pixel répondant aux deux critères\n';
      statsText += '• Neige >' + SNOW_COVER_THRESHOLD + '% ET glacier >' + GLACIER_FRACTION_THRESHOLD + '%';
    }
    
    statsLabel.setValue(statsText);
  });
};

// Label pour afficher les statistiques
var statsLabel = ui.Label('Statistiques: En attente...');

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
  updateButton,
  ui.Label(''),  // Espace
  statsLabel
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
  .select(['NDSI_Snow_Cover', 'Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA'])
  .first();

// Initialisation de la carte avec la date par défaut
var example_snow_cover = example_image.select('NDSI_Snow_Cover');
var example_albedo = example_image.select('Snow_Albedo_Daily_Tile').divide(100);
var example_quality = example_image.select('NDSI_Snow_Cover_Basic_QA');
var example_fraction = calculatePixelFraction(example_image, glacier_mask);

// Masques
var good_quality = example_quality.lte(1);
var high_snow = example_snow_cover.gte(SNOW_COVER_THRESHOLD);
var high_glacier_fraction = example_fraction.gte(GLACIER_FRACTION_THRESHOLD / 100);
var valid_albedo = example_image.select('Snow_Albedo_Daily_Tile').lte(100);

// Albédo filtré (double critère)
var filtered_albedo = example_albedo
  .updateMask(good_quality)
  .updateMask(high_snow)
  .updateMask(high_glacier_fraction)
  .updateMask(valid_albedo);

// Initialisation de la visualisation
Map.centerObject(glacier_geometry, 12);
Map.addLayer(glacier_mask.selfMask(), {palette: ['lightgray'], opacity: 0.3}, '0. Masque glacier');
Map.addLayer(example_fraction.updateMask(example_fraction.gt(0)), 
  {min: 0, max: 1, palette: ['red', 'orange', 'yellow', 'lightblue', 'blue']}, 
  '1. Fraction glacier');
Map.addLayer(example_snow_cover.updateMask(example_fraction.gt(0)), 
  {min: 0, max: 100, palette: ['brown', 'yellow', 'green', 'cyan', 'blue', 'white']}, 
  '2. Couverture de neige (%)');
Map.addLayer(high_snow.updateMask(example_fraction.gt(0)), 
  {palette: ['black', 'white']}, 
  '3. Masque neige >' + SNOW_COVER_THRESHOLD + '%');
Map.addLayer(high_glacier_fraction.updateMask(example_fraction.gt(0)), 
  {palette: ['black', 'cyan']}, 
  '4. Masque glacier >' + GLACIER_FRACTION_THRESHOLD + '%');
Map.addLayer(filtered_albedo, 
  {min: 0.4, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']}, 
  '5. Albédo filtré (double critère)');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 8 : EXPORTS                                                                   │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 12. Export des statistiques annuelles
Export.table.toDrive({
  collection: annual_albedo_high_snow,
  description: 'Saskatchewan_Albedo_High_Snow_Cover_Annual_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_albedo_high_snow_annual_2010_2024',
  fileFormat: 'CSV'
});

// 13. Export des statistiques quotidiennes
Export.table.toDrive({
  collection: dailyAlbedoHighSnow,
  description: 'Saskatchewan_Albedo_High_Snow_Cover_Daily_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_albedo_high_snow_daily_2010_2024',
  fileFormat: 'CSV'
});

// 14. Export de l'exemple cartographique
Export.image.toDrive({
  image: ee.Image.cat([
    example_snow_cover.rename('snow_cover_pct'),
    filtered_albedo.rename('albedo_filtered'),
    high_snow.rename('high_snow_mask')
  ]),
  description: 'Saskatchewan_High_Snow_Example_20200715',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_high_snow_example_20200715',
  scale: 500,
  region: glacier_geometry,
  maxPixels: 1e9
});

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 9 : ANALYSE COMPARATIVE AVEC/SANS FILTRE                                      │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 15. Fonction pour comparer avec albédo non filtré
function compareWithUnfilteredAlbedo(img) {
  var date = img.date();
  var snow_cover = img.select('NDSI_Snow_Cover');
  var snow_albedo = img.select('Snow_Albedo_Daily_Tile').divide(100);
  var quality = img.select('NDSI_Snow_Cover_Basic_QA');
  
  // Masque de base (qualité + valide)
  var base_mask = quality.lte(1).and(img.select('Snow_Albedo_Daily_Tile').lte(100));
  
  // Masque haute neige
  var high_snow_mask = base_mask.and(snow_cover.gte(SNOW_COVER_THRESHOLD));
  
  // Fraction glacier pour limiter à la zone du glacier
  var fraction = calculatePixelFraction(img, glacier_mask);
  var glacier_pixels = fraction.gt(0);
  
  // Albédo non filtré (tous pixels valides dans le glacier)
  var unfiltered_albedo = snow_albedo.updateMask(base_mask).updateMask(glacier_pixels);
  
  // Albédo filtré (seulement haute neige)
  var filtered_albedo = snow_albedo.updateMask(high_snow_mask).updateMask(glacier_pixels);
  
  // Statistiques
  var unfiltered_stats = unfiltered_albedo.reduceRegion({
    reducer: ee.Reducer.mean().combine(ee.Reducer.count(), '', true),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    bestEffort: true
  });
  
  var filtered_stats = filtered_albedo.reduceRegion({
    reducer: ee.Reducer.mean().combine(ee.Reducer.count(), '', true),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    bestEffort: true
  });
  
  // Gérer les cas où il n'y a pas de pixels haute neige
  var filtered_mean = filtered_stats.get('Snow_Albedo_Daily_Tile_mean');
  var unfiltered_mean = unfiltered_stats.get('Snow_Albedo_Daily_Tile_mean');
  
  // Calculer la différence seulement si les deux valeurs existent
  var difference = ee.Algorithms.If(
    ee.Algorithms.IsEqual(filtered_mean, null),
    null,  // Si pas de pixels haute neige, différence = null
    ee.Number(filtered_mean).subtract(ee.Number(unfiltered_mean))
  );
  
  return ee.Feature(null, {
    'date': date.format('YYYY-MM-dd'),
    'year': date.get('year'),
    'unfiltered_mean': unfiltered_mean,
    'unfiltered_count': unfiltered_stats.get('Snow_Albedo_Daily_Tile_count'),
    'filtered_mean': filtered_mean,
    'filtered_count': filtered_stats.get('Snow_Albedo_Daily_Tile_count'),
    'difference': difference,
    'has_high_snow': ee.Algorithms.If(
      ee.Algorithms.IsEqual(filtered_mean, null),
      0,  // Pas de pixels haute neige
      1   // A des pixels haute neige
    )
  });
}

// Calculer la comparaison pour une année exemple
var comparison_2020 = dailyCollection
  .filterDate('2020-06-01', '2020-09-30')
  .map(compareWithUnfilteredAlbedo);

// Graphique comparatif
var comparisonChart = ui.Chart.feature.byFeature(
    comparison_2020,
    'date',
    ['unfiltered_mean', 'filtered_mean']
  )
  .setChartType('LineChart')
  .setOptions({
    title: 'Comparaison albédo avec/sans filtre de couverture de neige (2020)',
    hAxis: {title: 'Date'},
    vAxis: {title: 'Albédo moyen', viewWindow: {min: 0.3, max: 0.9}},
    series: {
      0: {color: 'gray', lineWidth: 2, lineDashStyle: [4, 4]},
      1: {color: 'blue', lineWidth: 3}
    },
    legend: {
      position: 'top',
      labels: ['Sans filtre (tous pixels)', 'Avec filtre (neige >90%)']
    },
    height: 400
  });

print('');
print('COMPARAISON AVEC/SANS FILTRE (2020):');
print(comparisonChart);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 10 : RÉSUMÉ ET DOCUMENTATION                                                   │
// └────────────────────────────────────────────────────────────────────────────────────────┘

print('');
print('=== RÉSUMÉ ANALYSE ALBÉDO AVEC FILTRE COUVERTURE DE NEIGE ===');
print('');
print('MÉTHODOLOGIE :');
print('• Filtre NDSI_Snow_Cover ≥ ' + SNOW_COVER_THRESHOLD + '%');
print('• Qualité : seulement Best (0) et Good (1)');
print('• Période : Étés 2010-2024 (juin-septembre)');
print('• Dataset : MOD10A1.061 (MODIS/Terra)');
print('');
print('JUSTIFICATION SCIENTIFIQUE :');
print('• Sélectionne les pixels à dominance neigeuse');
print('• Élimine les surfaces majoritairement non-neigeuses');
print('• Réduit la variabilité due aux surfaces faiblement enneigées');
print('• Permet une analyse focalisée sur les zones enneigées');
print('');
print('AVANTAGES :');
print('• Signal d\'albédo de zones enneigées');
print('• Meilleure disponibilité de données vs seuil 90%');
print('• Réduction du bruit des surfaces non-neigeuses');
print('• Équilibre entre qualité et quantité de données');
print('');
print('LIMITATIONS :');
print('• Inclut encore des surfaces partiellement neigeuses');
print('• Moins strict que le seuil 90% pour neige pure');
print('• Sensible au seuil choisi (50%)');
print('• Peut inclure des conditions de neige variable');
print('');
print('EXPORTS CONFIGURÉS :');
print('• CSV annuel : Moyennes par classe de fraction');
print('• CSV quotidien : Statistiques détaillées pour Mann-Kendall');
print('• Images : Exemples de masquage et résultats');
print('');
print('APPLICATIONS :');
print('• Études de l\'albédo de neige fraîche');
print('• Analyse des rétroactions neige-climat');
print('• Validation de modèles énergétiques glaciaires');
print('• Détection de changements dans les propriétés de la neige');

// FIN DU SCRIPT