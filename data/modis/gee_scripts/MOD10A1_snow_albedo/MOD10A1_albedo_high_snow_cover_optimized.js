// ╔════════════════════════════════════════════════════════════════════════════════════════╗
// ║          ANALYSE D'ALBÉDO OPTIMISÉE POUR COUVERTURE DE NEIGE ÉLEVÉE                    ║
// ║                           GLACIER SASKATCHEWAN 2010-2024                                ║
// ║                 MODIS MOD10A1.061 - Filtrage par NDSI Snow Cover                       ║
// ║                  Fichier: MOD10A1_albedo_high_snow_cover_optimized.js                  ║
// ╚════════════════════════════════════════════════════════════════════════════════════════╝

// Description : Version optimisée du script d'analyse albédo avec double filtrage.
// Corrections des bugs, optimisations de performance, et améliorations interface.
// Analyse l'albédo de neige avec filtrage : couverture de neige >50% ET fraction glacier >75%.

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 1 : CONFIGURATION ET INITIALISATION                                            │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 1. Paramètres configurables
var NDSI_SNOW_THRESHOLD = 0; // Minimum NDSI Snow Cover threshold (index 0-100, not percentage)
var GLACIER_FRACTION_THRESHOLD = 75; // Seuil minimal de fraction glacier dans le pixel (%)
var MIN_PIXEL_THRESHOLD = 10; // Nombre minimum de pixels requis pour fiabilité statistique
var FRACTION_THRESHOLDS = [0.25, 0.50, 0.75, 0.90]; // Seuils de fraction glacier pour classes
var STUDY_YEARS = ee.List([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]);
var SUMMER_START_MONTH = 7;  // Juillet (peak melt season)
var SUMMER_END_MONTH = 9;    // Septembre
var USE_PEAK_MELT_ONLY = true; // Si true, utilise juillet-septembre au lieu de juin-septembre

// Class names for glacier fraction categories
var FRACTION_CLASS_NAMES = ['border', 'mixed_low', 'mixed_high', 'mostly_ice', 'pure_ice'];
var ANNUAL_CLASS_NAMES = ['border_high_snow', 'mixed_low_high_snow', 'mixed_high_high_snow', 
                          'mostly_ice_high_snow', 'pure_ice_high_snow'];

// 2. Charger l'asset du glacier Saskatchewan
// ⚠️ LIMITATION SCIENTIFIQUE IMPORTANTE :
// Ce script utilise un masque glaciaire statique de 2024 pour toute la période 2010-2024.
// Les changements de géométrie glaciaire au cours de cette période ne sont PAS pris en compte.
// Cela peut introduire des biais dans l'analyse temporelle, particulièrement pour les années
// les plus éloignées de 2024. Les tendances à long terme doivent être interprétées avec 
// cette limitation en considération.
var saskatchewan_glacier = ee.Image('projects/tofunori/assets/Saskatchewan_glacier_2024_updated');
var glacier_mask = saskatchewan_glacier.gt(0);
var glacier_geometry = glacier_mask.reduceToVectors({
  scale: 30,
  maxPixels: 1e6,
  tileScale: 2
}).geometry();

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 2 : CALCUL STATIQUE DE LA FRACTION GLACIER (OPTIMISATION)                      │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 3. Calculer la fraction glacier une seule fois (optimisation performance)
print('Computing static glacier fraction...');

// Obtenir une projection MODIS de référence
var modis_reference = ee.ImageCollection('MODIS/061/MOD10A1')
  .filterDate('2020-01-01', '2020-01-02')
  .first();
var modis_projection = modis_reference.projection();

// Calculer la fraction glacier globale une seule fois
var raster30 = ee.Image.constant(1)
  .updateMask(glacier_mask)
  .unmask(0)
  .reproject(modis_projection, null, 30);

var STATIC_GLACIER_FRACTION = raster30
  .reduceResolution({
    reducer: ee.Reducer.mean(),
    maxPixels: 1024
  })
  .reproject(modis_projection, null, 500);

print('Glacier fraction computed. Min/Max:', 
  STATIC_GLACIER_FRACTION.reduceRegion({
    reducer: ee.Reducer.minMax(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    tileScale: 2
  }));

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 3 : FONCTIONS OPTIMISÉES                                                       │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 4. Helper function for padding binary strings (GEE compatible)
function padBinary(num, length) {
  var binary = num.toString(2);
  var padding = '';
  for (var i = binary.length; i < length; i++) {
    padding += '0';
  }
  return padding + binary;
}

// 5. Fonction optimisée pour créer masques de fraction (version simplifiée fiable)
function createFractionMasks(fractionImage, thresholds) {
  var masks = {};
  masks['border'] = fractionImage.gt(0).and(fractionImage.lt(thresholds[0]));
  masks['mixed_low'] = fractionImage.gte(thresholds[0]).and(fractionImage.lt(thresholds[1]));
  masks['mixed_high'] = fractionImage.gte(thresholds[1]).and(fractionImage.lt(thresholds[2]));
  masks['mostly_ice'] = fractionImage.gte(thresholds[2]).and(fractionImage.lt(thresholds[3]));
  masks['pure_ice'] = fractionImage.gte(thresholds[3]);
  return masks;
}

// 5. Fonctions pour filtrage qualité complet basé sur documentation officielle GEE
function getBasicQAMask(img, level) {
  var basicQA = img.select('NDSI_Snow_Cover_Basic_QA');
  
  // Valeurs officielles GEE MOD10A1.061:
  // 0: Best quality, 1: Good quality, 2: OK quality, 3: Poor quality
  // 211: Night, 239: Ocean
  
  var qualityMask;
  switch(level) {
    case 'best': qualityMask = basicQA.eq(0); break;
    case 'good': qualityMask = basicQA.lte(1); break;  // DEFAULT
    case 'ok': qualityMask = basicQA.lte(2); break;
    case 'all': qualityMask = basicQA.lte(3); break;
    default: qualityMask = basicQA.lte(1); // Default to good
  }
  
  // Toujours exclure nuit et océan
  var excludeMask = basicQA.neq(211).and(basicQA.neq(239));
  
  return qualityMask.and(excludeMask);
}

// QA bit mapping for metadata-driven processing
var QA_BIT_MAPPING = [
  {flag: 'excludeInlandWater', bit: 0, mask: 1, desc: 'Inland water'},
  {flag: 'excludeVisibleScreenFail', bit: 1, mask: 2, desc: 'Low visible screen failure'},
  {flag: 'excludeNDSIScreenFail', bit: 2, mask: 4, desc: 'Low NDSI screen failure'},
  {flag: 'excludeTempHeightFail', bit: 3, mask: 8, desc: 'Temperature/height screen failure'},
  {flag: 'excludeSWIRAnomaly', bit: 4, mask: 16, desc: 'Shortwave IR reflectance anomaly'},
  {flag: 'excludeProbablyCloudy', bit: 5, mask: 32, desc: 'Probably cloudy (v6.1 cloud detection)'},
  {flag: 'excludeProbablyClear', bit: 6, mask: 64, desc: 'Probably clear (v6.1 cloud detection)'},
  {flag: 'excludeHighSolarZenith', bit: 7, mask: 128, desc: 'Solar zenith >70°'}
];

function getAlgorithmFlagsMask(img, flags) {
  var algFlags = img.select('NDSI_Snow_Cover_Algorithm_Flags_QA').uint8();
  var mask = ee.Image(1);
  
  // Metadata-driven QA bit processing
  QA_BIT_MAPPING.forEach(function(mapping) {
    if (flags[mapping.flag]) {
      mask = mask.and(algFlags.bitwiseAnd(mapping.mask).eq(0));
    }
  });
  
  return mask;
}

// Helper function to create current QA mask from UI state
function createCurrentQAMask(img) {
  var basicLevel = basicQASelect.getValue();
  var flagConfig = {
    excludeInlandWater: flagCheckboxes.inlandWater.getValue(),
    excludeVisibleScreenFail: flagCheckboxes.visibleScreenFail.getValue(),
    excludeNDSIScreenFail: flagCheckboxes.ndsiScreenFail.getValue(),
    excludeTempHeightFail: flagCheckboxes.tempHeightFail.getValue(),
    excludeSWIRAnomaly: flagCheckboxes.swirAnomaly.getValue(),
    excludeProbablyCloudy: flagCheckboxes.probablyCloudy.getValue(),
    excludeProbablyClear: flagCheckboxes.probablyClear.getValue(),
    excludeHighSolarZenith: flagCheckboxes.highSolarZenith.getValue()
  };
  
  return getBasicQAMask(img, basicLevel).and(getAlgorithmFlagsMask(img, flagConfig));
}

function createComprehensiveQualityMask(img, qaConfig) {
  // Fonction principale combinant Basic QA et Algorithm Flags
  var basicMask = getBasicQAMask(img, qaConfig.basicLevel || 'good');
  var flagsMask = getAlgorithmFlagsMask(img, qaConfig);
  
  return basicMask.and(flagsMask);
}

// Fonction de compatibilité pour code existant
function createQualityMask(qualityBand) {
  // Maintient compatibilité avec code existant (Basic QA level ≤ 1)
  return qualityBand.bitwiseAnd(0x3).lte(1);
}

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 4 : ANALYSE ANNUELLE OPTIMISÉE                                                │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 6. Fonction pour analyser l'albédo annuel avec optimisations
function calculateAnnualAlbedoHighSnowCoverOptimized(year) {
  var yearStart = ee.Date.fromYMD(year, USE_PEAK_MELT_ONLY ? 7 : SUMMER_START_MONTH, 1);
  var yearEnd = ee.Date.fromYMD(year, SUMMER_END_MONTH, 30);
  
  // Charger MOD10A1 avec clip pour réduire zone de calcul (incluant Algorithm_Flags_QA)
  var mod10a1_collection = ee.ImageCollection('MODIS/061/MOD10A1')
    .filterDate(yearStart, yearEnd)
    .filterBounds(glacier_geometry)
    .select(['NDSI_Snow_Cover', 'Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA', 'NDSI_Snow_Cover_Algorithm_Flags_QA'])
    .map(function(img) { return img.clip(glacier_geometry); });
  
  // Traiter chaque image avec fraction statique
  var processed_collection = mod10a1_collection.map(function(img) {
    var snow_cover = img.select('NDSI_Snow_Cover');
    var snow_albedo = img.select('Snow_Albedo_Daily_Tile');
    var quality = img.select('NDSI_Snow_Cover_Basic_QA');
    
    // Masques de qualité améliorés
    var good_quality_mask = createQualityMask(quality);
    var high_ndsi_mask = snow_cover.gte(NDSI_SNOW_THRESHOLD); // NDSI index ≥ threshold
    var high_glacier_fraction_mask = STATIC_GLACIER_FRACTION.gte(GLACIER_FRACTION_THRESHOLD / 100);
    var valid_albedo_mask = snow_albedo.lte(100);
    
    // Masque combiné
    var combined_mask = good_quality_mask
      .and(high_ndsi_mask)
      .and(high_glacier_fraction_mask)
      .and(valid_albedo_mask);
    
    // Conversion albédo avec nom cohérent
    var albedo_scaled = snow_albedo.divide(100)
      .updateMask(combined_mask)
      .rename('albedo'); // Nom cohérent pour reduceRegion
    
    // Créer les masques par classe de fraction (approche fiable)
    var masks = createFractionMasks(STATIC_GLACIER_FRACTION, FRACTION_THRESHOLDS);
    
    // Appliquer les masques de fraction à l'albédo
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
  
  // Séparer les statistiques d'albédo et de comptage de pixels
  var albedo_means = processed_collection.select(ANNUAL_CLASS_NAMES).mean();
  var pixel_count_total = processed_collection.select('high_snow_pixel_count').sum();
  
  // Calculer les statistiques d'albédo pour chaque classe
  var all_stats = albedo_means.reduceRegion({
    reducer: ee.Reducer.mean().combine(
      ee.Reducer.stdDev(), '', true
    ).combine(
      ee.Reducer.count(), '', true
    ),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    tileScale: 4 // Remplace bestEffort
  });
  
  // Calculer le nombre total de pixels filtrés (correctement)
  var filtered_pixel_stats = pixel_count_total.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    tileScale: 4
  });
  
  // Construire les propriétés avec validation MIN_PIXEL_THRESHOLD
  var total_pixels = filtered_pixel_stats.get('high_snow_pixel_count');
  var sufficient_pixels = ee.Number(total_pixels).gte(MIN_PIXEL_THRESHOLD);
  
  var properties = {
    'year': year,
    'ndsi_snow_threshold': NDSI_SNOW_THRESHOLD,
    'glacier_fraction_threshold': GLACIER_FRACTION_THRESHOLD,
    'min_pixel_threshold': MIN_PIXEL_THRESHOLD,
    'peak_melt_only': USE_PEAK_MELT_ONLY,
    'total_filtered_pixels': total_pixels,
    'sufficient_pixels': sufficient_pixels
  };
  
  ANNUAL_CLASS_NAMES.forEach(function(className) {
    // Appliquer MIN_PIXEL_THRESHOLD validation pour chaque classe
    var class_count = all_stats.get(className + '_count');
    var class_sufficient = ee.Number(class_count).gte(MIN_PIXEL_THRESHOLD);
    
    properties[className + '_mean'] = ee.Algorithms.If(class_sufficient, all_stats.get(className + '_mean'), null);
    properties[className + '_stdDev'] = ee.Algorithms.If(class_sufficient, all_stats.get(className + '_stdDev'), null);
    properties[className + '_count'] = class_count;
    properties[className + '_sufficient_pixels'] = class_sufficient;
  });
  
  return ee.Feature(null, properties);
}

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 5 : ANALYSE QUOTIDIENNE OPTIMISÉE                                             │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 7. Fonction pour analyser l'albédo quotidien optimisée
function analyzeDailyAlbedoHighSnowCoverOptimized(img) {
  var date = img.date();
  var snow_cover = img.select('NDSI_Snow_Cover');
  var snow_albedo = img.select('Snow_Albedo_Daily_Tile');
  var quality = img.select('NDSI_Snow_Cover_Basic_QA');
  
  // Masques avec fonction qualité améliorée
  var good_quality_mask = createQualityMask(quality);
  var high_ndsi_mask = snow_cover.gte(NDSI_SNOW_THRESHOLD); // NDSI index ≥ threshold
  var high_glacier_fraction_mask = STATIC_GLACIER_FRACTION.gte(GLACIER_FRACTION_THRESHOLD / 100);
  var valid_albedo_mask = snow_albedo.lte(100);
  var combined_mask = good_quality_mask
    .and(high_ndsi_mask)
    .and(high_glacier_fraction_mask)
    .and(valid_albedo_mask);
  
  // Albédo filtré avec nom cohérent
  var albedo_scaled = snow_albedo.divide(100).updateMask(combined_mask).rename('albedo');
  
  // Masques par classe de fraction
  var masks = createFractionMasks(STATIC_GLACIER_FRACTION, FRACTION_THRESHOLDS);
  
  // Calculer les statistiques pour chaque classe
  var class_results = {};
  
  FRACTION_CLASS_NAMES.forEach(function(className) {
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
      tileScale: 4
    });
    
    // Appliquer MIN_PIXEL_THRESHOLD validation pour chaque classe
    var class_count = classStats.get('albedo_count');
    var class_sufficient = ee.Number(class_count).gte(MIN_PIXEL_THRESHOLD);
    
    class_results[className + '_mean'] = ee.Algorithms.If(class_sufficient, classStats.get('albedo_mean'), null);
    class_results[className + '_median'] = ee.Algorithms.If(class_sufficient, classStats.get('albedo_median'), null);
    class_results[className + '_pixel_count'] = class_count;
    class_results[className + '_sufficient_pixels'] = class_sufficient;
  });
  
  // Compter pixels totaux filtrés avec gestion d'erreur
  var total_filtered = combined_mask.rename('pixel_count')
    .updateMask(STATIC_GLACIER_FRACTION.gt(0))
    .reduceRegion({
      reducer: ee.Reducer.sum(),
      geometry: glacier_geometry,
      scale: 500,
      maxPixels: 1e9,
      tileScale: 4
    }).get('pixel_count'); // Nom correct de la bande
  
  // Validation null avec fallback
  total_filtered = ee.Algorithms.If(
    ee.Algorithms.IsEqual(total_filtered, null),
    0,
    total_filtered
  );
  
  // Métadonnées temporelles
  var year = date.get('year');
  var doy = date.getRelative('day', 'year').add(1);
  
  // Combiner toutes les statistiques avec validation MIN_PIXEL_THRESHOLD
  var sufficient_total_pixels = ee.Number(total_filtered).gte(MIN_PIXEL_THRESHOLD);
  
  var final_stats = {
    'date': date.format('YYYY-MM-dd'),
    'year': year,
    'doy': doy,
    'decimal_year': year.add(doy.divide(365.25)),
    'total_filtered_pixels': total_filtered,
    'sufficient_total_pixels': sufficient_total_pixels,
    'min_pixel_threshold': MIN_PIXEL_THRESHOLD,
    'ndsi_snow_threshold': NDSI_SNOW_THRESHOLD,
    'glacier_fraction_threshold': GLACIER_FRACTION_THRESHOLD,
    'system:time_start': date.millis()
  };
  
  // Ajouter les résultats de classe
  Object.keys(class_results).forEach(function(key) {
    final_stats[key] = class_results[key];
  });
  
  return ee.Feature(null, final_stats);
}

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 6 : CALCUL DES STATISTIQUES                                                   │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 8. Calculer pour toutes les années
print('Computing optimized annual statistics...');
var annual_albedo_high_snow = ee.FeatureCollection(STUDY_YEARS.map(calculateAnnualAlbedoHighSnowCoverOptimized));

print('Annual statistics (optimized):', annual_albedo_high_snow);

// 9. Calculer les statistiques quotidiennes
print('Computing optimized daily statistics...');
var dailyCollection = ee.ImageCollection('MODIS/061/MOD10A1')
  .filterDate('2010-01-01', '2024-12-31')
  .filterBounds(glacier_geometry)
  .filter(ee.Filter.calendarRange(USE_PEAK_MELT_ONLY ? 7 : SUMMER_START_MONTH, SUMMER_END_MONTH, 'month'))
  .select(['NDSI_Snow_Cover', 'Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA', 'NDSI_Snow_Cover_Algorithm_Flags_QA'])
  .map(function(img) { return img.clip(glacier_geometry); });

var dailyAlbedoHighSnow = dailyCollection.map(analyzeDailyAlbedoHighSnowCoverOptimized);

print('Number of days analyzed:', dailyAlbedoHighSnow.size());

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 7 : INTERFACE INTERACTIVE OPTIMISÉE                                           │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 10. Interface interactive avec améliorations
print('Optimized interactive interface...');

// Variables globales pour les données de base
var currentImage = null;
var baseSnowCover = null;
var baseAlbedo = null;
var baseQuality = null;
var baseAlgorithmFlags = null;

// Créer un sélecteur de date
var dateSlider = ui.DateSlider({
  start: '2010-07-01',
  end: '2024-09-30',
  value: '2023-08-07',
  period: 1,
  style: {width: '300px'}
});

// Helper function to create uniform sliders
var createSlider = function(min, max, value, step) {
  return ui.Slider({
    min: min,
    max: max,
    value: value,
    step: step,
    style: {width: '300px'}
  });
};

// Sliders pour les filtres (using factory function)
var ndsiSlider = createSlider(0, 100, NDSI_SNOW_THRESHOLD, 5);
var glacierFractionSlider = createSlider(0, 100, GLACIER_FRACTION_THRESHOLD, 5);
var minPixelSlider = createSlider(0, 100, MIN_PIXEL_THRESHOLD, 1);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION: CONTROLS QA COMPLETS (basés sur documentation officielle GEE)                │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Basic QA Level Selector
var basicQASelect = ui.Select({
  items: [
    {label: 'Best quality only (0)', value: 'best'},
    {label: 'Good quality+ (0-1)', value: 'good'},     // DEFAULT selon votre demande
    {label: 'OK quality+ (0-2)', value: 'ok'},
    {label: 'All quality levels (0-3)', value: 'all'}
  ],
  value: 'good',  // Default to 1 (good quality) as requested
  placeholder: 'Basic Quality Level',
  style: {width: '300px'},
  onChange: updateQAFiltering
});

// Algorithm Flags Checkboxes (dynamic generation from metadata)
var flagMeta = [
  {key: 'inlandWater', bit: 0, label: 'Bit 0: Inland water', def: false},
  {key: 'visibleScreenFail', bit: 1, label: 'Bit 1: Low visible screen', def: true},
  {key: 'ndsiScreenFail', bit: 2, label: 'Bit 2: Low NDSI screen', def: true},
  {key: 'tempHeightFail', bit: 3, label: 'Bit 3: Temperature/height screen', def: true},
  {key: 'swirAnomaly', bit: 4, label: 'Bit 4: Shortwave IR reflectance', def: false},
  {key: 'probablyCloudy', bit: 5, label: 'Bit 5: Probably cloudy (v6.1)', def: true},
  {key: 'probablyClear', bit: 6, label: 'Bit 6: Probably clear (v6.1)', def: false},
  {key: 'highSolarZenith', bit: 7, label: 'Bit 7: Solar zenith screen', def: true}
];

var flagCheckboxes = {};
flagMeta.forEach(function(m) {
  flagCheckboxes[m.key] = ui.Checkbox({
    label: m.label,
    value: m.def,
    onChange: updateQAFiltering,
    style: {fontSize: '11px'}
  });
});

// Dynamic labels
var dateLabel = ui.Label('Date selection and optimized filtering parameters:');
var selectedDateLabel = ui.Label('Selected date: 2020-07-15');
var ndsiLabel = ui.Label('NDSI Snow Cover threshold: ' + NDSI_SNOW_THRESHOLD + ' (index 0-100)');
var glacierFractionLabel = ui.Label('Glacier fraction threshold: ' + GLACIER_FRACTION_THRESHOLD + '%');
var minPixelLabel = ui.Label('Minimum pixels: OFF (no filter)');
var statsLabel = ui.Label('Statistics: Waiting...');
var qaBasicLabel = ui.Label('Basic quality level: Good+ (0-1)', {fontSize: '11px'});
var qaStatsLabel = ui.Label('QA Retention: Calculating...', {fontSize: '11px'});

// Reload button for filter testing
var reloadButton = ui.Button({
  label: '🔄 Reload',
  onClick: function() {
    updateFiltering();
  },
  style: {width: '100px'}
});

// Fonction pour charger les données de base
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
  
  // Charger l'image MOD10A1 avec clip (incluant Algorithm_Flags_QA)
  // Note: 5-day window used for data availability in case selected date has no data
  currentImage = ee.ImageCollection('MODIS/061/MOD10A1')
    .filterDate(selected_date, selected_date.advance(5, 'day'))
    .filterBounds(glacier_geometry)
    .select(['NDSI_Snow_Cover', 'Snow_Albedo_Daily_Tile', 'NDSI_Snow_Cover_Basic_QA', 'NDSI_Snow_Cover_Algorithm_Flags_QA'])
    .first()
    .clip(glacier_geometry);
  
  // Préparer les données de base
  baseSnowCover = currentImage.select('NDSI_Snow_Cover');
  baseAlbedo = currentImage.select('Snow_Albedo_Daily_Tile').divide(100);
  baseQuality = currentImage.select('NDSI_Snow_Cover_Basic_QA');
  baseAlgorithmFlags = currentImage.select('NDSI_Snow_Cover_Algorithm_Flags_QA');
  
  // Mettre à jour l'affichage
  updateFiltering();
};

// Fonction pour mettre à jour le filtrage avec palette adaptative
var updateFiltering = function() {
  if (!currentImage) return;
  
  var ndsiThreshold = ndsiSlider.getValue();
  var glacierThreshold = glacierFractionSlider.getValue();
  var minPixelThreshold = minPixelSlider.getValue();
  
  // Mettre à jour les labels
  ndsiLabel.setValue('NDSI Snow Cover threshold: ' + ndsiThreshold + ' (index 0-100)');
  glacierFractionLabel.setValue('Glacier fraction threshold: ' + glacierThreshold + '%');
  
  if (minPixelThreshold === 0) {
    minPixelLabel.setValue('Minimum pixels: OFF (no filter)');
  } else {
    minPixelLabel.setValue('Minimum pixels: ' + minPixelThreshold);
  }
  
  // Créer les masques avec qualité compréhensive
  var basicQALevel = basicQASelect ? basicQASelect.getValue() : 'good';
  var basicMask = getBasicQAMask(currentImage, basicQALevel);
  var flagMask = getAlgorithmFlagsMask(currentImage, {
    excludeInlandWater: flagCheckboxes.inlandWater.getValue(),
    excludeVisibleScreenFail: flagCheckboxes.visibleScreenFail.getValue(),
    excludeNDSIScreenFail: flagCheckboxes.ndsiScreenFail.getValue(),
    excludeTempHeightFail: flagCheckboxes.tempHeightFail.getValue(),
    excludeSWIRAnomaly: flagCheckboxes.swirAnomaly.getValue(),
    // Removed: excludeProbablyCloudy (Bit 5 is Spare)
    // Removed: excludeProbablyNotClear (Bit 6 is Spare)
    excludeHighSolarZenith: flagCheckboxes.highSolarZenith.getValue()
  });
  var good_quality = basicMask.and(flagMask);
  var high_ndsi = baseSnowCover.gte(ndsiThreshold);
  var high_glacier_fraction = STATIC_GLACIER_FRACTION.gte(glacierThreshold / 100);
  var valid_albedo = currentImage.select('Snow_Albedo_Daily_Tile').lte(100);
  
  // Albédo filtré avec renommage pour cohérence
  var filtered_albedo = baseAlbedo
    .updateMask(good_quality)
    .updateMask(high_ndsi)
    .updateMask(high_glacier_fraction)
    .updateMask(valid_albedo)
    .rename('filtered_albedo');
  
  // Calculer min/max pour palette adaptative
  var albedoRange = filtered_albedo.reduceRegion({
    reducer: ee.Reducer.minMax(),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    tileScale: 2
  });
  
  // Effacer les couches précédentes (sauf masque glacier)
  var layers = Map.layers();
  while (layers.length() > 1) {
    Map.remove(layers.get(layers.length() - 1));
  }
  
  // Palette simple et distincte pour tous les layers
  var simplePalette = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue'];
  
  // Ajouter la couche de fraction glacier pour l'inspecteur
  Map.addLayer(STATIC_GLACIER_FRACTION.multiply(100), 
    {min: 0, max: 100, palette: simplePalette}, 
    'Fraction glacier (%)', false);
    
  // Ajouter les couches QA pour l'inspecteur (visible dans inspector)
  Map.addLayer(baseQuality, 
    {min: 0, max: 3, palette: ['green', 'yellow', 'orange', 'red']}, 
    'Basic QA (0=Best, 1=Good, 2=OK, 3=Poor)', false);
    
  Map.addLayer(baseAlgorithmFlags, 
    {min: 0, max: 255, palette: ['black', 'blue', 'cyan', 'green', 'yellow', 'orange', 'red', 'white']}, 
    'Algorithm Flags QA (0-255)', false);
    
  // Ajout d'une couche composite QA avec cloud flags pour inspection
  var qaComposite = ee.Image([
    baseQuality.rename('Basic_QA'),
    baseAlgorithmFlags.rename('Algorithm_Flags'), 
    baseSnowCover.rename('NDSI_Snow_Cover'),
    baseAlgorithmFlags.bitwiseAnd(32).divide(32).rename('Probably_Cloudy'),
    baseAlgorithmFlags.bitwiseAnd(64).divide(64).rename('Probably_Clear')
  ]);
  
  Map.addLayer(qaComposite, {}, 'QA Composite (Click pour inspecter)', false);
  
  // Ajouter la couche NDSI Snow Cover pour l'inspecteur
  Map.addLayer(baseSnowCover, 
    {min: 0, max: 100, palette: simplePalette}, 
    'NDSI Snow Cover (0-100)', false);
  
  // Ajouter la couche d'albédo avec palette adaptative
  albedoRange.evaluate(function(range) {
    var minVal = range['filtered_albedo_min'] || 0.4;
    var maxVal = range['filtered_albedo_max'] || 0.9;
    
    Map.addLayer(filtered_albedo, 
      {min: minVal, max: maxVal, palette: simplePalette}, 
      'Filtered Albedo (NDSI>' + ndsiThreshold + ', G>' + glacierThreshold + '%)');
  }, function(error) {
    // Error handling for tile processing issues
    print('Error computing adaptive palette:', error);
    // Add layer with default palette as fallback
    Map.addLayer(filtered_albedo, 
      {min: 0.4, max: 0.9, palette: simplePalette}, 
      'Filtered Albedo (NDSI>' + ndsiThreshold + ', G>' + glacierThreshold + '%) - Default');
  });
  
  // Calculer et afficher les statistiques avec validation pixels minimum
  var dayStats = filtered_albedo.reduceRegion({
    reducer: ee.Reducer.mean().combine(ee.Reducer.count(), '', true),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    tileScale: 2
  });
  
  dayStats.evaluate(function(stats) {
    var meanAlbedo = stats['filtered_albedo_mean'];
    var pixelCount = stats['filtered_albedo_count'] || 0;
    
    var statsText = 'Statistiques temps réel (optimisées):\n';
    
    // Validation pixels minimum avec gestion null
    var pixelThresholdMet = (minPixelThreshold === 0 || pixelCount >= minPixelThreshold);
    
    if (meanAlbedo !== null && pixelCount > 0 && pixelThresholdMet) {
      statsText += '• Mean albedo: ' + meanAlbedo.toFixed(3) + '\n';
      statsText += '• Qualified pixels: ' + pixelCount + '\n';
      statsText += '• NDSI ≥' + ndsiThreshold + ' AND Glacier ≥' + glacierThreshold + '%';
      if (minPixelThreshold > 0) {
        statsText += '\n• Pixel threshold (≥' + minPixelThreshold + '): ✓';
      }
    } else if (meanAlbedo !== null && pixelCount > 0 && !pixelThresholdMet) {
      statsText += '• Pixels found: ' + pixelCount + '\n';
      statsText += '• Required threshold: ≥' + minPixelThreshold + ' pixels\n';
      statsText += '• ❌ Not enough qualified pixels';
    } else {
      statsText += '• No qualified pixels (meanAlbedo=' + meanAlbedo + ')\n';
      statsText += '• Try reducing thresholds';
    }
    
    statsLabel.setValue(statsText);
  });
};

// Fonction pour mettre à jour le filtrage QA
var updateQAFiltering = function() {
  // Mettre à jour le label QA de base
  var basicQALevel = basicQASelect.getValue();
  var basicLevelText = {
    'best': 'Best only (0)',
    'good': 'Good+ (0-1)', 
    'ok': 'OK+ (0-2)',
    'all': 'All levels (0-3)'
  };
  qaBasicLabel.setValue('Niveau qualité de base: ' + basicLevelText[basicQALevel]);
  
  // Calculer statistiques de rétention QA si nous avons des données
  if (currentImage && baseQuality && baseAlgorithmFlags) {
    // Compter pixels total dans glacier
    var totalPixels = glacier_mask.selfMask().reduceRegion({
      reducer: ee.Reducer.count(),
      geometry: glacier_geometry,
      scale: 500,
      maxPixels: 1e9,
      tileScale: 2
    });
    
    // Compter pixels retenus avec QA actuel
    var combinedQAMask = createCurrentQAMask(currentImage);
    var retainedPixels = combinedQAMask.selfMask().reduceRegion({
      reducer: ee.Reducer.count(),
      geometry: glacier_geometry,
      scale: 500,
      maxPixels: 1e9,
      tileScale: 2
    });
    
    // Calculer pourcentage de rétention
    ee.Number(totalPixels.get('constant')).getInfo(function(total) {
      ee.Number(retainedPixels.get('constant')).getInfo(function(retained) {
        if (total && retained) {
          var percentage = Math.round((retained / total) * 100);
          qaStatsLabel.setValue('Rétention pixels QA: ' + retained + '/' + total + ' (' + percentage + '%)');
        } else {
          qaStatsLabel.setValue('Rétention pixels QA: Calcul...');
        }
      });
    });
  }
  
  // Déclencher la mise à jour de l'affichage principal
  updateFiltering();
};

// Callbacks pour les sliders
ndsiSlider.onChange(updateFiltering);
glacierFractionSlider.onChange(updateFiltering);
minPixelSlider.onChange(updateFiltering);

// Boutons
var loadDataButton = ui.Button({
  label: 'Load selected date',
  onClick: loadBaseData,
  style: {width: '200px'}
});

var exportParamsButton = ui.Button({
  label: 'Export optimized parameters',
  onClick: function() {
    var ndsiVal = ndsiSlider.getValue();
    var glacierVal = glacierFractionSlider.getValue();
    var pixelVal = minPixelSlider.getValue();
    print('Optimal parameters found:');
    print('• NDSI Snow Cover threshold: ' + ndsiVal + ' (index 0-100)');
    print('• Glacier fraction threshold: ' + glacierVal + '%');
    print('• Minimum pixels: ' + (pixelVal === 0 ? 'OFF (disabled)' : pixelVal));
    print('• Period: ' + (USE_PEAK_MELT_ONLY ? 'July-September (peak melt)' : 'June-September'));
    print('• Code: NDSI_SNOW_THRESHOLD = ' + ndsiVal + '; GLACIER_FRACTION_THRESHOLD = ' + glacierVal + '; MIN_PIXEL_THRESHOLD = ' + pixelVal + ';');
  },
  style: {width: '200px'}
});

// Panneau principal de contrôle (gauche) - Contrôles de base
var mainPanel = ui.Panel([
  dateLabel,
  dateSlider,
  selectedDateLabel,
  loadDataButton,
  reloadButton,
  ui.Label(''),
  ui.Label('PARAMÈTRES DE FILTRAGE OPTIMISÉS:', {fontWeight: 'bold'}),
  ndsiLabel,
  ndsiSlider,
  glacierFractionLabel,
  glacierFractionSlider,
  minPixelLabel,
  minPixelSlider,
  ui.Label(''),
  statsLabel,
  ui.Label(''),
  exportParamsButton
], ui.Panel.Layout.flow('vertical'), {
  width: '380px',
  position: 'top-left'
});

// QA Panel (right) - Quality control details  
var qaPanel = ui.Panel([
  ui.Label('QUALITY CONTROLS (QA)', {fontWeight: 'bold', color: 'blue', fontSize: '14px'}),
  ui.Label('────────────────────────────────', {color: 'blue', fontSize: '10px'}),
  ui.Label(''),
  ui.Label('Basic QA Level:', {fontWeight: 'bold', fontSize: '12px'}),
  qaBasicLabel,
  basicQASelect,
  ui.Label(''),
  ui.Label('Algorithm Flags (Valid Bits Only):', {fontSize: '12px', fontWeight: 'bold'}),
  ui.Label('Check to EXCLUDE pixels:', {fontSize: '10px', color: 'gray'}),
  flagCheckboxes.inlandWater,           // Bit 0
  flagCheckboxes.visibleScreenFail,     // Bit 1
  flagCheckboxes.ndsiScreenFail,        // Bit 2
  flagCheckboxes.tempHeightFail,        // Bit 3
  flagCheckboxes.swirAnomaly,           // Bit 4
  flagCheckboxes.probablyCloudy,        // Bit 5
  flagCheckboxes.probablyClear,         // Bit 6
  flagCheckboxes.highSolarZenith,       // Bit 7
  ui.Label(''),
  qaStatsLabel
], ui.Panel.Layout.flow('vertical'), {
  width: '350px',
  position: 'top-right'
});

Map.add(mainPanel);
Map.add(qaPanel);

// Initialisation de la carte
Map.centerObject(glacier_geometry, 12);
Map.addLayer(glacier_mask.selfMask(), {palette: ['orange'], opacity: 0.5}, 'Saskatchewan Glacier Mask');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ INSPECTEUR QA INTÉGRÉ                                                                  │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// Activer l'inspecteur avec valeurs QA
Map.onClick(function(coords) {
  if (!currentImage || !baseQuality || !baseAlgorithmFlags) {
    print('First click "Load selected date"');
    return;
  }
  
  var point = ee.Geometry.Point([coords.lon, coords.lat]);
  
  // Extraire toutes les valeurs aux coordonnées cliquées
  var values = currentImage.sample(point, 500).first();
  
  values.getInfo(function(result) {
    if (result && result.properties) {
      var props = result.properties;
      
      // Informations de base
      print('═══ QA INSPECTOR - Position: ' + coords.lon.toFixed(4) + ', ' + coords.lat.toFixed(4) + ' ═══');
      print('📅 Selected date: ' + selectedDateLabel.getValue().split(': ')[1]);
      
      // Valeurs des bandes principales
      print('🌨️ NDSI Snow Cover: ' + (props.NDSI_Snow_Cover || 'No data') + ' (index 0-100)');
      print('❄️ Snow Albedo: ' + (props.Snow_Albedo_Daily_Tile || 'No data') + ' (raw values 0-100)');
      
      // QA de base avec décodage
      var basicQA = props.NDSI_Snow_Cover_Basic_QA;
      var basicQAText = 'Unknown';
      if (basicQA !== undefined) {
        switch(basicQA) {
          case 0: basicQAText = 'Best quality'; break;
          case 1: basicQAText = 'Good quality'; break;
          case 2: basicQAText = 'OK quality'; break;
          case 3: basicQAText = 'Poor quality'; break;
          case 211: basicQAText = 'Night (no data)'; break;
          case 239: basicQAText = 'Ocean'; break;
          default: basicQAText = 'Unknown (' + basicQA + ')';
        }
      }
      print('🏷️ Basic QA: ' + basicQA + ' → ' + basicQAText);
      
      // Algorithm Flags avec décodage bit par bit détaillé
      var algFlags = props.NDSI_Snow_Cover_Algorithm_Flags_QA;
      if (algFlags !== undefined) {
        print('🔍 Algorithm Flags: ' + algFlags + ' (binaire: ' + padBinary(algFlags, 8) + ')');
        print('┌─ Analyse détaillée des flags ─┐');
        
        // Bit 0 - Inland Water
        var inlandWater = (algFlags & 1);
        print('│ Bit 0 - Eau continentale: ' + (inlandWater ? 'DÉTECTÉ 💧' : 'NON 🏔️'));
        if (inlandWater) print('│   Impact: Pixel sur eau, non-glaciaire');
        
        // Bit 1 - Visible Screen Fail  
        var visibleFail = (algFlags & 2);
        print('│ Bit 1 - Échec écran visible: ' + (visibleFail ? 'ÉCHEC ❌' : 'OK ✅'));
        if (visibleFail) print('│   Impact: CRITIQUE - Données visible corrompues');
        
        // Bit 2 - NDSI Screen Fail
        var ndsiFail = (algFlags & 4);
        print('│ Bit 2 - Échec écran NDSI: ' + (ndsiFail ? 'ÉCHEC ❌' : 'OK ✅'));
        if (ndsiFail) print('│   Impact: CRITIQUE - NDSI non-fiable');
        
        // Bit 3 - Temperature/Height Screen Fail
        var tempHeightFail = (algFlags & 8);
        print('│ Bit 3 - Échec temp/altitude: ' + (tempHeightFail ? 'ÉCHEC ❌' : 'OK ✅'));
        if (tempHeightFail) print('│   Impact: IMPORTANT - Conditions atypiques');
        
        // Bit 4 - SWIR Anomaly
        var swirAnomaly = (algFlags & 16);
        print('│ Bit 4 - Anomalie SWIR: ' + (swirAnomaly ? 'DÉTECTÉ ⚠️' : 'NON 📡'));
        if (swirAnomaly) print('│   Impact: OPTIONNEL - Peut affecter précision');
        
        // Bit 5 - Probably Cloudy (NOUVEAU v6.1)
        var probablyCloudy = (algFlags & 32);
        print('│ Bit 5 - Probablement nuageux: ' + (probablyCloudy ? 'OUI ☁️' : 'NON ☀️'));
        if (probablyCloudy) print('│   Impact: CRITIQUE - Cloud masking v6.1');
        
        // Bit 6 - Probably Clear (NOUVEAU v6.1)
        var probablyClear = (algFlags & 64);
        print('│ Bit 6 - Probablement clair: ' + (probablyClear ? 'OUI ☀️' : 'NON ☁️'));
        if (probablyClear) print('│   Impact: OPTIMAL - Clear sky v6.1');
        
        // Bit 7 - High Solar Zenith
        var highSolarZenith = (algFlags & 128);
        print('│ Bit 7 - Angle solaire >70°: ' + (highSolarZenith ? 'OUI ☀️' : 'NON 🌅'));
        if (highSolarZenith) print('│   Impact: IMPORTANT - Éclairage faible');
        
        print('└─────────────────────────────────┘');
        
        // Recommandations automatiques avec cloud flags v6.1
        var criticalFlags = visibleFail || ndsiFail || probablyCloudy;
        var importantFlags = tempHeightFail || highSolarZenith;
        var optionalFlags = swirAnomaly || inlandWater;
        var excellentConditions = probablyClear && !criticalFlags && !importantFlags;
        
        if (criticalFlags) {
          print('⚠️ RECOMMANDATION: Pixel CRITIQUE - Éviter pour analyses');
          if (probablyCloudy) print('   💡 Raison: Probablement nuageux (cloud mask v6.1)');
        } else if (excellentConditions) {
          print('🌟 RECOMMANDATION: Pixel EXCELLENT - Ciel clair v6.1!');
        } else if (importantFlags) {
          print('⚡ RECOMMANDATION: Pixel ACCEPTABLE avec réserves');
        } else if (optionalFlags) {
          print('✅ RECOMMANDATION: Pixel BON avec flags mineurs');
        } else {
          print('✅ RECOMMANDATION: Pixel BON - Pas de flags critiques');
        }
      } else {
        print('🔍 Algorithm Flags: No data');
      }
      
      // Fraction glacier à ce pixel
      var glacierFractionValue = STATIC_GLACIER_FRACTION.sample(point, 500).first();
      glacierFractionValue.getInfo(function(fracResult) {
        if (fracResult && fracResult.properties && fracResult.properties.constant !== undefined) {
          var fraction = (fracResult.properties.constant * 100).toFixed(1);
          print('🏔️ Fraction glacier: ' + fraction + '%');
          
          // État du filtrage actuel
          var basicQALevel = basicQASelect.getValue();
          var passesBasicQA = false;
          switch(basicQALevel) {
            case 'best': passesBasicQA = basicQA === 0; break;
            case 'good': passesBasicQA = basicQA <= 1; break;
            case 'ok': passesBasicQA = basicQA <= 2; break;
            case 'all': passesBasicQA = basicQA <= 3; break;
          }
          passesBasicQA = passesBasicQA && basicQA !== 211 && basicQA !== 239;
          
          var passesFlags = true;
          if (algFlags !== undefined) {
            if (flagCheckboxes.inlandWater.getValue() && (algFlags & 1)) passesFlags = false;
            if (flagCheckboxes.visibleScreenFail.getValue() && (algFlags & 2)) passesFlags = false;
            if (flagCheckboxes.ndsiScreenFail.getValue() && (algFlags & 4)) passesFlags = false;
            if (flagCheckboxes.tempHeightFail.getValue() && (algFlags & 8)) passesFlags = false;
            if (flagCheckboxes.swirAnomaly.getValue() && (algFlags & 16)) passesFlags = false;
            if (flagCheckboxes.probablyCloudy.getValue() && (algFlags & 32)) passesFlags = false;
            if (flagCheckboxes.probablyClear.getValue() && (algFlags & 64)) passesFlags = false;
            if (flagCheckboxes.highSolarZenith.getValue() && (algFlags & 128)) passesFlags = false;
          }
          
          print('✅ Passe filtres QA: ' + (passesBasicQA && passesFlags ? 'OUI' : 'NON'));
          print('  • Basic QA (' + basicQALevel + '): ' + (passesBasicQA ? 'PASS' : 'FAIL'));
          print('  • Algorithm Flags: ' + (passesFlags ? 'PASS' : 'FAIL'));
          print('═══════════════════════════════════════════════════════');
        }
      });
    } else {
      print('Aucune donnée disponible à cette position.');
    }
  });
});

// Instructions mises à jour avec QA et cloud flags v6.1
var instructionsLabel = ui.Label({
  value: 'Instructions (Cloud Detection v6.1):\n' +
         '📅 PANNEAU GAUCHE - Contrôles principaux:\n' +
         '1. Sélectionnez une date avec le calendrier\n' +
         '2. Cliquez "Charger date sélectionnée"\n' +
         '3. Ajustez les sliders de filtrage\n' +
         '\n☁️ PANNEAU DROITE - QA + Cloud Detection:\n' +
         '4. Ajustez le niveau QA (défaut: Good+)\n' +
         '5. NOUVEAU: Cloud flags v6.1 disponibles!\n' +
         '6. Observez la rétention pixels en temps réel\n' +
         '\n🎯 INSPECTEUR DOUBLE:\n' +
         '7. Console: Cliquez carte pour analyse détaillée\n' +
         '8. Inspector: Activez couches QA pour valeurs',
  style: {
    fontSize: '11px',
    color: 'gray',
    whiteSpace: 'pre'
  }
});

mainPanel.add(ui.Label(''));
mainPanel.add(instructionsLabel);

// Chargement automatique sans hack computeValue
print('Chargement automatique de la date par défaut...');
loadBaseData();

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 8 : EXPORTS OPTIMISÉS                                                         │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 11. Export des statistiques annuelles
Export.table.toDrive({
  collection: annual_albedo_high_snow,
  description: 'Saskatchewan_Albedo_High_Snow_Optimized_Annual_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_albedo_high_snow_optimized_annual_2010_2024',
  fileFormat: 'CSV'
});

// 12. Export des statistiques quotidiennes
Export.table.toDrive({
  collection: dailyAlbedoHighSnow,
  description: 'Saskatchewan_Albedo_High_Snow_Optimized_Daily_2010_2024',
  folder: 'GEE_exports',
  fileNamePrefix: 'MOD10A1_albedo_high_snow_optimized_daily_2010_2024',
  fileFormat: 'CSV'
});

// Note: Export image défaillant supprimé (variables non définies corrigées)

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 9 : ANALYSE COMPARATIVE AVEC CORRECTION BUGS                                  │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 13. Fonction pour comparer avec albédo non filtré (bugs corrigés)
function compareWithUnfilteredAlbedoSafe(img) {
  var date = img.date();
  var snow_cover = img.select('NDSI_Snow_Cover');
  var snow_albedo = img.select('Snow_Albedo_Daily_Tile').divide(100);
  var quality = img.select('NDSI_Snow_Cover_Basic_QA');
  
  // Limiter aux pixels glacier
  var glacier_pixels = STATIC_GLACIER_FRACTION.gt(0);
  
  // Masque de base avec qualité améliorée
  var base_mask = createQualityMask(quality).and(img.select('Snow_Albedo_Daily_Tile').lte(100));
  
  // Masque avec double filtrage
  var double_filter_mask = base_mask
    .and(snow_cover.gte(NDSI_SNOW_THRESHOLD))
    .and(STATIC_GLACIER_FRACTION.gte(GLACIER_FRACTION_THRESHOLD / 100));
  
  // Albédo non filtré et filtré avec noms cohérents
  var unfiltered_albedo = snow_albedo.updateMask(base_mask).updateMask(glacier_pixels).rename('unfiltered_albedo');
  var filtered_albedo = snow_albedo.updateMask(double_filter_mask).updateMask(glacier_pixels).rename('filtered_albedo');
  
  // Statistiques avec gestion d'erreur
  var unfiltered_stats = unfiltered_albedo.reduceRegion({
    reducer: ee.Reducer.mean().combine(ee.Reducer.count(), '', true),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    tileScale: 2
  });
  
  var filtered_stats = filtered_albedo.reduceRegion({
    reducer: ee.Reducer.mean().combine(ee.Reducer.count(), '', true),
    geometry: glacier_geometry,
    scale: 500,
    maxPixels: 1e9,
    tileScale: 2
  });
  
  // Récupération sécurisée des valeurs avec conversion client-side appropriée
  var filtered_mean = filtered_stats.get('filtered_albedo_mean');
  var unfiltered_mean = unfiltered_stats.get('unfiltered_albedo_mean');
  var filtered_count = filtered_stats.get('filtered_albedo_count');
  var unfiltered_count = unfiltered_stats.get('unfiltered_albedo_count');
  
  // Calcul de différence sécurisé - approche simple sans null checking
  var difference = ee.Algorithms.If(
    filtered_mean,
    ee.Algorithms.If(
      unfiltered_mean,
      ee.Number(filtered_mean).subtract(ee.Number(unfiltered_mean)),
      null
    ),
    null
  );
  
  // Calcul des métadonnées temporelles
  var year = date.get('year');
  var doy = date.getRelative('day', 'year').add(1);
  var decimal_year = year.add(doy.divide(365.25));
  
  return ee.Feature(null, {
    'system:time_start': date.millis(),
    'date': date.format('YYYY-MM-dd'),
    'year': year,
    'doy': doy,
    'decimal_year': decimal_year,
    'unfiltered_mean': unfiltered_mean,
    'unfiltered_count': unfiltered_count,
    'filtered_mean': filtered_mean,
    'filtered_count': filtered_count,
    'difference': difference,
    'has_high_snow': ee.Algorithms.If(
      ee.Algorithms.IsEqual(filtered_mean, null),
      0,
      1
    )
  });
}

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION: VALIDATION PLOTS (STREAMLINED)                                               │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 1. Data Coverage Quality Plot - Shows data availability over time
var coverageChart = ui.Chart.feature.byFeature(dailyAlbedoHighSnow, 'system:time_start', 'total_filtered_pixels')
  .setChartType('LineChart')
  .setOptions({
    title: 'MOD10A1 Daily Data Coverage (High Snow + Glacier >75%)',
    hAxis: {title: 'Date', format: 'yyyy'},
    vAxis: {title: 'Valid Pixels Count'},
    colors: ['blue'],
    height: 300,
    pointSize: 3,
    lineWidth: 1
  });

// 2. Annual Trend Summary Plot - Core scientific validation
var trendChart = ui.Chart.feature.byFeature(annual_albedo_high_snow, 'year', 'pure_ice_high_snow_mean')
  .setChartType('LineChart')
  .setOptions({
    title: 'Pure Ice Albedo Trend (>90% glacier fraction)',
    hAxis: {title: 'Year'},
    vAxis: {title: 'Mean Albedo', viewWindow: {min: 0.2, max: 0.9}},
    trendlines: {0: {type: 'linear', color: 'red', opacity: 0.8}},
    colors: ['blue'],
    pointSize: 5,
    lineWidth: 2,
    height: 350
  });

print('');
print('=== VALIDATION PLOTS (STREAMLINED) ===');
print(coverageChart);
print(trendChart);

// FIN DU SCRIPT OPTIMISÉ