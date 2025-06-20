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
var MIN_PIXEL_THRESHOLD = 0; // Nombre minimum de pixels requis (0 = désactivé)
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
  
  // Calculer aussi le nombre moyen de pixels filtrés
  var filtered_pixel_stats = annual_means.select('high_snow_pixel_count').reduceRegion({
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
    'total_filtered_pixels': filtered_pixel_stats.get('high_snow_pixel_count')
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
print('Calcul des statistiques d\'albédo avec double filtrage (neige >' + SNOW_COVER_THRESHOLD + '% ET glacier >' + GLACIER_FRACTION_THRESHOLD + '%)...');
var annual_albedo_high_snow = ee.FeatureCollection(STUDY_YEARS.map(calculateAnnualAlbedoHighSnowCover));

print('Statistiques annuelles (double filtrage):', annual_albedo_high_snow);

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
    title: 'Évolution albédo de neige (double filtrage) par classe de fraction',
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
print('GRAPHIQUE TEMPOREL (ALBÉDO DOUBLE FILTRAGE):');
print(temporalChart);

// 8. Graphique du nombre de pixels filtrés
var pixelCountChart = ui.Chart.feature.byFeature(
    annual_albedo_high_snow, 
    'year', 
    'total_filtered_pixels'
  )
  .setChartType('ColumnChart')
  .setOptions({
    title: 'Nombre de pixels filtrés (double critère) par année',
    hAxis: {title: 'Année', format: '####'},
    vAxis: {title: 'Nombre de pixels'},
    colors: ['steelblue'],
    height: 300
  });

print('');
print('ÉVOLUTION DU NOMBRE DE PIXELS FILTRÉS:');
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
  
  // Compter pixels totaux filtrés
  var total_filtered = combined_mask.updateMask(fraction.gt(0)).reduceRegion({
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
  stats['total_filtered_pixels'] = total_filtered;
  stats['snow_cover_threshold'] = SNOW_COVER_THRESHOLD;
  stats['glacier_fraction_threshold'] = GLACIER_FRACTION_THRESHOLD;
  stats['system:time_start'] = date.millis();
  
  return ee.Feature(null, stats);
}

// 10. Calculer les statistiques quotidiennes
print('');
print('=== CALCUL DES STATISTIQUES QUOTIDIENNES (DOUBLE FILTRAGE) ===');

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

// 11. Interface interactive avec sliders pour filtres dynamiques
print('');
print('=== INTERFACE INTERACTIVE AVEC SLIDERS DE FILTRAGE ===');

// Variables globales pour les données de base
var currentImage = null;
var baseSnowCover = null;
var baseAlbedo = null;
var baseQuality = null;
var baseFraction = null;

// Créer un sélecteur de date
var dateSlider = ui.DateSlider({
  start: '2010-06-01',
  end: '2024-09-30',
  value: '2020-07-15',
  period: 1,
  style: {width: '300px'}
});

// Sliders pour les filtres
var snowCoverSlider = ui.Slider({
  min: 0,
  max: 100,
  value: SNOW_COVER_THRESHOLD,
  step: 5,
  style: {width: '300px'}
});

var glacierFractionSlider = ui.Slider({
  min: 0,
  max: 100,
  value: GLACIER_FRACTION_THRESHOLD,
  step: 5,
  style: {width: '300px'}
});

var minPixelSlider = ui.Slider({
  min: 0,
  max: 100,
  value: MIN_PIXEL_THRESHOLD,
  step: 1,
  style: {width: '300px'}
});

// Labels dynamiques
var dateLabel = ui.Label('Sélection de date et paramètres de filtrage:');
var selectedDateLabel = ui.Label('Date sélectionnée: 2020-07-15');
var snowCoverLabel = ui.Label('Seuil couverture de neige: ' + SNOW_COVER_THRESHOLD + '%');
var glacierFractionLabel = ui.Label('Seuil fraction glacier: ' + GLACIER_FRACTION_THRESHOLD + '%');
var minPixelLabel = ui.Label('Pixels minimum: OFF (pas de filtre)');
var statsLabel = ui.Label('Statistiques: En attente...');

// Fonction pour charger les données de base pour une date
var loadBaseData = function() {
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
  currentImage = ee.ImageCollection('MODIS/061/MOD10A1')
    .filterDate(selected_date, selected_date.advance(5, 'day'))
    .filterBounds(glacier_geometry)
    .select(['NDSI_Snow_Cover', 'Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA'])
    .first();
  
  // Préparer les données de base
  baseSnowCover = currentImage.select('NDSI_Snow_Cover');
  baseAlbedo = currentImage.select('Snow_Albedo_Daily_Tile').divide(100);
  baseQuality = currentImage.select('NDSI_Snow_Cover_Basic_QA');
  baseFraction = calculatePixelFraction(currentImage, glacier_mask);
  
  // Mettre à jour l'affichage avec les paramètres actuels
  updateFiltering();
};

// Fonction pour mettre à jour le filtrage selon les sliders
var updateFiltering = function() {
  if (!currentImage) return;
  
  // Récupérer les valeurs des sliders
  var snowThreshold = snowCoverSlider.getValue();
  var glacierThreshold = glacierFractionSlider.getValue();
  var minPixelThreshold = minPixelSlider.getValue();
  
  // Mettre à jour les labels
  snowCoverLabel.setValue('Seuil couverture de neige: ' + snowThreshold + '%');
  glacierFractionLabel.setValue('Seuil fraction glacier: ' + glacierThreshold + '%');
  
  if (minPixelThreshold === 0) {
    minPixelLabel.setValue('Pixels minimum: OFF (pas de filtre)');
  } else {
    minPixelLabel.setValue('Pixels minimum: ' + minPixelThreshold);
  }
  
  // Créer les masques avec les nouveaux seuils
  var good_quality = baseQuality.lte(1);
  var high_snow = baseSnowCover.gte(snowThreshold);
  var high_glacier_fraction = baseFraction.gte(glacierThreshold / 100);
  var valid_albedo = currentImage.select('Snow_Albedo_Daily_Tile').lte(100);
  
  // Albédo filtré
  var filtered_albedo = baseAlbedo
    .updateMask(good_quality)
    .updateMask(high_snow)
    .updateMask(high_glacier_fraction)
    .updateMask(valid_albedo);
  
  // Effacer les couches précédentes (sauf la première - masque glacier)
  var layers = Map.layers();
  while (layers.length() > 1) {
    Map.remove(layers.get(layers.length() - 1));
  }
  
  // Ajouter la couche de fraction glacier pour l'inspecteur
  Map.addLayer(baseFraction.multiply(100), 
    {min: 0, max: 100, palette: ['red', 'orange', 'yellow', 'lightblue', 'blue']}, 
    'Fraction glacier (%)', false);
  
  // Ajouter uniquement la couche d'albédo filtré
  Map.addLayer(filtered_albedo, 
    {min: 0.4, max: 0.9, palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']}, 
    'Albédo filtré (N>' + snowThreshold + '%, G>' + glacierThreshold + '%)');
  
  // Calculer et afficher les statistiques
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
    
    var statsText = 'Statistiques temps réel:\n';
    
    // Vérifier le seuil de pixels minimum si activé
    var pixelThresholdMet = (minPixelThreshold === 0 || pixelCount >= minPixelThreshold);
    
    if (meanAlbedo !== null && pixelCount > 0 && pixelThresholdMet) {
      statsText += '• Albédo moyen: ' + meanAlbedo.toFixed(3) + '\n';
      statsText += '• Pixels qualifiés: ' + pixelCount + '\n';
      statsText += '• Neige ≥' + snowThreshold + '% ET Glacier ≥' + glacierThreshold + '%';
      if (minPixelThreshold > 0) {
        statsText += '\n• Seuil pixels (≥' + minPixelThreshold + '): ✓';
      }
    } else if (meanAlbedo !== null && pixelCount > 0 && !pixelThresholdMet) {
      statsText += '• Pixels trouvés: ' + pixelCount + '\n';
      statsText += '• Seuil requis: ≥' + minPixelThreshold + ' pixels\n';
      statsText += '• ❌ Pas assez de pixels qualifiés';
    } else {
      statsText += '• Aucun pixel qualifié\n';
      statsText += '• Essayez de réduire les seuils';
    }
    
    statsLabel.setValue(statsText);
  });
};

// Callbacks pour les sliders
snowCoverSlider.onChange(updateFiltering);
glacierFractionSlider.onChange(updateFiltering);
minPixelSlider.onChange(updateFiltering);

// Boutons
var loadDataButton = ui.Button({
  label: 'Charger date sélectionnée',
  onClick: loadBaseData,
  style: {width: '200px'}
});

var exportParamsButton = ui.Button({
  label: 'Exporter paramètres',
  onClick: function() {
    var snowVal = snowCoverSlider.getValue();
    var glacierVal = glacierFractionSlider.getValue();
    var pixelVal = minPixelSlider.getValue();
    print('Paramètres optimaux trouvés:');
    print('• Seuil couverture neige: ' + snowVal + '%');
    print('• Seuil fraction glacier: ' + glacierVal + '%');
    print('• Pixels minimum: ' + (pixelVal === 0 ? 'OFF (désactivé)' : pixelVal));
    print('• Code pour script: SNOW_COVER_THRESHOLD = ' + snowVal + '; GLACIER_FRACTION_THRESHOLD = ' + glacierVal + '; MIN_PIXEL_THRESHOLD = ' + pixelVal + ';');
  },
  style: {width: '200px'}
});

// Ajouter les widgets au panneau
var panel = ui.Panel([
  dateLabel,
  dateSlider,
  selectedDateLabel,
  loadDataButton,
  ui.Label(''),  // Espace
  ui.Label('PARAMÈTRES DE FILTRAGE:', {fontWeight: 'bold'}),
  snowCoverLabel,
  snowCoverSlider,
  glacierFractionLabel,
  glacierFractionSlider,
  minPixelLabel,
  minPixelSlider,
  ui.Label(''),  // Espace
  statsLabel,
  ui.Label(''),  // Espace
  exportParamsButton
], ui.Panel.Layout.flow('vertical'), {
  width: '380px',
  position: 'top-left'
});

Map.add(panel);

// Initialisation de la carte
Map.centerObject(glacier_geometry, 12);
Map.addLayer(glacier_mask.selfMask(), {palette: ['lightgray'], opacity: 0.3}, 'Masque glacier Saskatchewan');

// Message d'instructions
var instructionsLabel = ui.Label({
  value: 'Instructions:\n' +
         '1. Sélectionnez une date avec le calendrier\n' +
         '2. Cliquez "Charger date sélectionnée"\n' +
         '3. Ajustez les sliders pour explorer les filtres\n' +
         '4. Utilisez l\'inspecteur pour voir la fraction glacier\n' +
         '5. Les statistiques se mettent à jour automatiquement\n' +
         '6. Exportez les paramètres optimaux si besoin',
  style: {
    fontSize: '12px',
    color: 'gray',
    whiteSpace: 'pre'
  }
});

// Ajouter les instructions à la fin du panneau
panel.add(ui.Label(''));
panel.add(instructionsLabel);

// Chargement automatique de la date par défaut
print('Chargement de la date par défaut...');
// Lancer l'initialisation après un délai pour que l'interface soit prête
ee.data.computeValue(ee.Number(1), function() {
  loadBaseData();
});

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
  
  // Fraction glacier pour limiter à la zone du glacier
  var fraction = calculatePixelFraction(img, glacier_mask);
  var glacier_pixels = fraction.gt(0);
  
  // Masque de base (qualité + valide)
  var base_mask = quality.lte(1).and(img.select('Snow_Albedo_Daily_Tile').lte(100));
  
  // Masque avec double filtrage
  var double_filter_mask = base_mask
    .and(snow_cover.gte(SNOW_COVER_THRESHOLD))
    .and(fraction.gte(GLACIER_FRACTION_THRESHOLD / 100));
  
  // Albédo non filtré (tous pixels valides dans le glacier)
  var unfiltered_albedo = snow_albedo.updateMask(base_mask).updateMask(glacier_pixels);
  
  // Albédo filtré (double critère)
  var filtered_albedo = snow_albedo.updateMask(double_filter_mask).updateMask(glacier_pixels);
  
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
print('=== RÉSUMÉ ANALYSE ALBÉDO AVEC DOUBLE FILTRAGE ===');
print('');
print('MÉTHODOLOGIE :');
print('• Double filtre: NDSI_Snow_Cover ≥ ' + SNOW_COVER_THRESHOLD + '% ET Fraction_Glacier ≥ ' + GLACIER_FRACTION_THRESHOLD + '%');
print('• Qualité : seulement Best (0) et Good (1)');
print('• Période : Étés 2010-2024 (juin-septembre)');
print('• Dataset : MOD10A1.061 (MODIS/Terra)');
print('');
print('JUSTIFICATION SCIENTIFIQUE :');
print('• Sélectionne les pixels à dominance neigeuse ET majoritairement glacier');
print('• Élimine les surfaces peu enneigées ET les pixels de bordure glacier');
print('• Réduit la variabilité due aux surfaces mixtes non-représentatives');
print('• Analyse très focalisée sur les zones glacier bien enneigées');
print('');
print('AVANTAGES :');
print('• Signal d\'albédo très homogène (double sélection)');
print('• Élimination efficace des pixels mixtes non-représentatifs');
print('• Réduction maximale du bruit spatial');
print('• Focus sur les zones glacier centrales bien enneigées');
print('• Contrôle précis de la qualité spatiale des données');
print('');
print('LIMITATIONS :');
print('• Nombre plus réduit de pixels analysés (double critère)');
print('• Biais vers les zones centrales du glacier');
print('• Peut exclure des transitions importantes en bordure');
print('• Sensible aux deux seuils choisis (' + SNOW_COVER_THRESHOLD + '% et ' + GLACIER_FRACTION_THRESHOLD + '%)');
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