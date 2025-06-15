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

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 2 : CALCUL DE LA COUVERTURE DES PIXELS                                        │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 3. Fonction pour calculer le pourcentage de couverture de chaque pixel MODIS
function calculatePixelCoverage(modisImage, glacierMask) {
  // Obtenir la projection MODIS
  var modisProjection = modisImage.projection();
  
  // Reprojecter le masque glacier à 30m vers la grille MODIS 500m
  // en calculant la fraction moyenne (0-1) de couverture
  var coverageFraction = glacierMask
    .reduceResolution({
      reducer: ee.Reducer.mean(),
      maxPixels: 1000
    })
    .reproject({
      crs: modisProjection,
      scale: 500
    });
  
  return coverageFraction.multiply(100); // Convertir en pourcentage
}

// Calculer la couverture
var pixelCoverage = calculatePixelCoverage(testImage, glacier_mask);

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

// ┌────────────────────────────────────────────────────────────────────────────────────────┐
// │ SECTION 5 : VISUALISATION                                                             │
// └────────────────────────────────────────────────────────────────────────────────────────┘

// 6. Centrer la carte et ajouter le masque glacier de référence
Map.centerObject(glacier_geometry, 12);
Map.addLayer(glacier_mask.selfMask(), 
  {palette: ['white'], opacity: 0.3}, 
  '0. Masque glacier 30m (référence)', false);

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

// 11. Créer une visualisation côte-à-côte
var comparison = ee.Image.cat([
  threshold_0.multiply(1),
  threshold_50.multiply(2),
  threshold_75.multiply(3)
]).reduce(ee.Reducer.max());

Map.addLayer(comparison.updateMask(comparison), 
  {min: 1, max: 3, palette: ['red', 'yellow', 'green']},
  '9. Comparaison: Rouge=>0%, Jaune=≥50%, Vert=≥75%');

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
        maxPixels: 1000
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

// 13. Créer un histogramme de la distribution des pourcentages de couverture
var histogram = ui.Chart.image.histogram({
  image: pixelCoverage,
  region: glacier_geometry.buffer(1000),
  scale: 500,
  maxBuckets: 20,
  maxPixels: 1e9
})
.setOptions({
  title: 'Distribution des pourcentages de couverture des pixels MODIS',
  hAxis: {title: 'Pourcentage de couverture (%)'},
  vAxis: {title: 'Nombre de pixels'},
  colors: ['blue']
});

print(histogram);

// FIN DU SCRIPT DE TEST