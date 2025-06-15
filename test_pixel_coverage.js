// ╔════════════════════════════════════════════════════════════════════════════════════════╗
// ║                   TEST SCRIPT : ANALYSE DE COUVERTURE DES PIXELS MODIS                 ║
// ║                              GLACIER SASKATCHEWAN                                      ║
// ╚════════════════════════════════════════════════════════════════════════════════════════╝

// Description : Ce script teste différents seuils de couverture pour les pixels MODIS
// afin de déterminer quels pixels inclure dans l'analyse d'albédo

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 1 : INITIALISATION                                                             │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 1. Charger le masque du glacier
var saskatchewan_glacier = ee.Image('projects/tofunori/assets/Saskatchewan_glacier_2024_updated');
var glacier_mask = saskatchewan_glacier.gt(0);
var glacier_geometry = glacier_mask.reduceToVectors({
  scale: 30,
  maxPixels: 1e6,
  bestEffort: true
}).geometry();

// 2. Définir une date de test (été 2018 avec bonne couverture)
var testDate = '2018-08-15';
var testImage = ee.ImageCollection('MODIS/061/MCD43A3')
  .filterDate(testDate, ee.Date(testDate).advance(1, 'day'))
  .filterBounds(glacier_geometry)
  .select(['Albedo_WSA_shortwave', 'BRDF_Albedo_Band_Mandatory_Quality_shortwave'])
  .first();

print('Image de test:', testDate);
print('Projection de l\'image MODIS:', testImage.projection());
print('Date exacte de l\'image:', testImage.date().format('YYYY-MM-dd'));

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 2 : CALCUL DE LA COUVERTURE DES PIXELS                                        │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 3. Fonction pour calculer le pourcentage de couverture de chaque pixel MODIS
function calculatePixelCoverage(modisImage, glacierMask) {
  // Méthode directe : utiliser une zone plus large pour capturer les pixels partiels
  
  // Créer une grille de pixels MODIS en reprojetant une image constante
  var modisReference = ee.Image.pixelLonLat()
    .reproject(modisImage.projection().atScale(500));
  
  // Pour chaque pixel MODIS, calculer quelle fraction est couverte par le glacier
  // Utiliser une approche par convolution pour simuler l'intersection
  var kernel = ee.Kernel.square({
    radius: 250,  // 250m = demi-pixel MODIS
    units: 'meters'
  });
  
  // Appliquer la convolution pour calculer la couverture moyenne dans chaque pixel MODIS
  var coverageFraction = glacierMask.float()
    .convolve(kernel.normalize())
    .reproject({
      crs: modisImage.projection(),
      scale: 500
    });
  
  // Alternative plus simple : moyenner directement à 500m avec un kernel approprié
  var simpleCoverage = glacierMask.float()
    .reduceNeighborhood({
      reducer: ee.Reducer.mean(),
      kernel: ee.Kernel.square(500, 'meters'),
      skipMasked: false
    })
    .reproject({
      crs: modisImage.projection(),
      scale: 500
    });
  
  return simpleCoverage.multiply(100).clamp(0, 100); // Convertir en pourcentage
}

// Calculer la couverture
var pixelCoverage = calculatePixelCoverage(testImage, glacier_mask);

// Debug : vérifier les statistiques de couverture
var coverageStats = pixelCoverage.reduceRegion({
  reducer: ee.Reducer.minMax().combine(ee.Reducer.mean(), '', true),
  geometry: glacier_geometry.buffer(1000),
  scale: 500,
  maxPixels: 1e9
});

print('');
print('STATISTIQUES DE COUVERTURE :');
print('Min-Max couverture (%):', coverageStats);

// Compter combien de pixels ont différents niveaux de couverture
var counts = ee.Dictionary({
  'pixels_0-25%': pixelCoverage.gte(0).and(pixelCoverage.lt(25)),
  'pixels_25-50%': pixelCoverage.gte(25).and(pixelCoverage.lt(50)),
  'pixels_50-75%': pixelCoverage.gte(50).and(pixelCoverage.lt(75)),
  'pixels_75-100%': pixelCoverage.gte(75).and(pixelCoverage.lte(100))
}).map(function(key, mask) {
  return ee.Image(mask).reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry.buffer(1000),
    scale: 500,
    maxPixels: 1e9
  }).get(ee.Image(mask).bandNames().get(0));
});

print('Distribution par tranches:', counts);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 3 : CRÉER DES MASQUES POUR DIFFÉRENTS SEUILS                                  │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 4. Créer des masques pour différents seuils de couverture
var threshold_0 = pixelCoverage.gt(0);      // Tout pixel qui touche le glacier
var threshold_25 = pixelCoverage.gte(25);   // ≥25% de couverture
var threshold_50 = pixelCoverage.gte(50);   // ≥50% de couverture (seuil proposé)
var threshold_75 = pixelCoverage.gte(75);   // ≥75% de couverture
var threshold_100 = pixelCoverage.eq(100);  // 100% de couverture

// Appliquer ces masques à l'image d'albédo
var albedo = testImage.select('Albedo_WSA_shortwave').multiply(0.001);
var quality = testImage.select('BRDF_Albedo_Band_Mandatory_Quality_shortwave');
var goodQuality = quality.lte(1);

var albedo_all = albedo.updateMask(goodQuality).updateMask(threshold_0);
var albedo_25 = albedo.updateMask(goodQuality).updateMask(threshold_25);
var albedo_50 = albedo.updateMask(goodQuality).updateMask(threshold_50);
var albedo_75 = albedo.updateMask(goodQuality).updateMask(threshold_75);
var albedo_100 = albedo.updateMask(goodQuality).updateMask(threshold_100);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 4 : STATISTIQUES DE COUVERTURE                                                │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 5. Calculer le nombre de pixels pour chaque seuil
function countPixels(mask, label) {
  var count = mask.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry.buffer(1000),
    scale: 500,
    maxPixels: 1e9
  });
  return ee.Feature(null, {
    'threshold': label,
    'pixel_count': count.get(mask.bandNames().get(0))
  });
}

var pixelStats = ee.FeatureCollection([
  countPixels(threshold_0, '> 0%'),
  countPixels(threshold_25, '≥ 25%'),
  countPixels(threshold_50, '≥ 50%'),
  countPixels(threshold_75, '≥ 75%'),
  countPixels(threshold_100, '= 100%')
]);

print('Nombre de pixels MODIS par seuil de couverture:', pixelStats);

// Debug: afficher les valeurs numériques
print('');
print('DÉTAIL DES STATISTIQUES :');
pixelStats.evaluate(function(result) {
  result.features.forEach(function(feature) {
    print(feature.properties.threshold + ': ' + feature.properties.pixel_count + ' pixels');
  });
});

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 5 : VISUALISATION                                                             │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 6. Centrer la carte et ajouter le masque glacier de référence
Map.centerObject(glacier_geometry, 12);
Map.addLayer(glacier_mask.selfMask(), 
  {palette: ['lightblue'], opacity: 0.8}, 
  '0. Masque glacier 30m (référence)');

// 7. Visualiser la carte de pourcentage de couverture
Map.addLayer(pixelCoverage.updateMask(pixelCoverage.gt(0)), 
  {min: 0, max: 100, palette: ['red', 'orange', 'yellow', 'lightgreen', 'green', 'darkgreen']}, 
  '1. Pourcentage de couverture par pixel MODIS');

// 8. Paramètres de visualisation pour l'albédo
var albedoVis = {
  min: 0.3,
  max: 0.9,
  palette: ['darkblue', 'blue', 'cyan', 'yellow', 'orange', 'red']
};

// 9. Ajouter les couches d'albédo pour chaque seuil
Map.addLayer(albedo_all, albedoVis, '2. Albédo - Tous pixels (>0%)', false);
Map.addLayer(albedo_25, albedoVis, '3. Albédo - Seuil ≥25%', false);
Map.addLayer(albedo_50, albedoVis, '4. Albédo - Seuil ≥50% (PROPOSÉ)');
Map.addLayer(albedo_75, albedoVis, '5. Albédo - Seuil ≥75%', false);
Map.addLayer(albedo_100, albedoVis, '6. Albédo - Seuil 100%', false);

// 10. Visualiser les contours des pixels pour chaque seuil
function createContours(mask, color, name) {
  var contours = mask.selfMask()
    .focal_max(1, 'square', 'pixels')
    .subtract(mask.selfMask().focal_min(1, 'square', 'pixels'));
  Map.addLayer(contours.selfMask(), {palette: [color]}, name, false);
}

createContours(threshold_0, 'gray', '7. Contours - Tous pixels');
createContours(threshold_50, 'blue', '8. Contours - Seuil ≥50%');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 6 : COMPARAISON VISUELLE DES MÉTHODES                                         │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 11. Créer une visualisation côte-à-côte avec des couleurs distinctes
var comparison = ee.Image(0)
  .where(threshold_0.and(threshold_50.not()), 1)  // Pixels >0% mais <50%
  .where(threshold_50.and(threshold_75.not()), 2) // Pixels ≥50% mais <75%
  .where(threshold_75, 3);                        // Pixels ≥75%

Map.addLayer(comparison.updateMask(comparison.gt(0)), 
  {min: 1, max: 3, palette: ['red', 'yellow', 'green']},
  '9. Comparaison: Rouge=0-50%, Jaune=50-75%, Vert=≥75%');

// Ajouter aussi les pixels exclus par chaque seuil
var excluded_50 = threshold_0.and(threshold_50.not());
var excluded_75 = threshold_50.and(threshold_75.not());

Map.addLayer(excluded_50.selfMask(), 
  {palette: ['orange'], opacity: 0.7},
  '10. Pixels exclus par seuil 50%', false);

Map.addLayer(excluded_75.selfMask(), 
  {palette: ['purple'], opacity: 0.7},
  '11. Pixels exclus par seuil 75%', false);

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 7 : EXEMPLE D'IMPLÉMENTATION POUR LE CODE PRINCIPAL                            │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 12. Fonction pour appliquer le seuil de couverture à une collection
function applyPoverageThreshold(imageCollection, glacierMask, threshold) {
  return imageCollection.map(function(img) {
    // Calculer la couverture pour cette image
    var coverage = glacierMask
      .reduceResolution({
        reducer: ee.Reducer.mean(),
        maxPixels: 65000  // Augmenter la limite pour accommoder le ratio 30m->500m
      })
      .reproject({
        crs: img.projection(),
        scale: 500
      });
    
    // Créer le masque basé sur le seuil
    var coverageMask = coverage.gte(threshold);
    
    // Appliquer le masque
    return img.updateMask(coverageMask);
  });
}

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 8 : RÉSUMÉ ET RECOMMANDATIONS                                                 │
// └────────────────────────────────────────────────────────────────────────────────────────┘

print('');
print('=== RÉSUMÉ DE L\'ANALYSE ===');
print('');
print('RECOMMANDATION : Utiliser un seuil de 50% de couverture');
print('Raisons :');
print('- Élimine les pixels de bordure avec peu de glacier');
print('- Conserve suffisamment de pixels pour une analyse robuste');
print('- Réduit le bruit causé par les terrains adjacents');
print('- Standard dans la littérature scientifique');
print('');
print('Pour implémenter dans le code principal :');
print('1. Calculer la fraction de couverture avec reduceResolution');
print('2. Appliquer un masque basé sur le seuil (≥0.5)');
print('3. Utiliser ce masque pour toutes les analyses');

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 9 : GRAPHIQUE DE DISTRIBUTION DES COUVERTURES                                 │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 13. Créer un histogramme avec des buckets fixes pour éviter l'erreur toFixed
print('');
print('HISTOGRAMME DES COUVERTURES :');

// Utiliser des buckets prédéfinis pour éviter l'erreur toFixed
var buckets = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];

// Compter manuellement les pixels dans chaque bucket
var bucketCounts = buckets.slice(0, -1).map(function(lower, i) {
  var upper = buckets[i + 1];
  var mask = pixelCoverage.gte(lower).and(pixelCoverage.lt(upper));
  if (i === buckets.length - 2) { // Dernier bucket inclut 100%
    mask = pixelCoverage.gte(lower).and(pixelCoverage.lte(upper));
  }
  
  var count = mask.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: glacier_geometry.buffer(1000),
    scale: 500,
    maxPixels: 1e9
  });
  
  return ee.Feature(null, {
    'range': lower + '-' + upper + '%',
    'count': count.get('constant'),
    'lower': lower
  });
});

var bucketCollection = ee.FeatureCollection(bucketCounts);
print('Distribution détaillée par tranches de 10%:', bucketCollection);

// Créer un graphique simple
var simpleChart = ui.Chart.feature.byFeature(bucketCollection, 'lower', 'count')
  .setChartType('ColumnChart')
  .setOptions({
    title: 'Distribution des pourcentages de couverture',
    hAxis: {title: 'Pourcentage de couverture (%)'},
    vAxis: {title: 'Nombre de pixels'},
    colors: ['blue']
  });

print(simpleChart);

// FIN DU SCRIPT DE TEST