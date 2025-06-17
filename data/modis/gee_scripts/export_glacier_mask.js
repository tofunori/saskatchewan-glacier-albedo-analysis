// Export Saskatchewan Glacier mask from Google Earth Engine for use with modis-tools
// Run this in Google Earth Engine Code Editor to export your glacier mask

// Load your existing glacier mask (as Image)
var glacier_image = ee.Image('projects/tofunori/assets/Saskatchewan_glacier_2024_updated');

// Convert image to feature collection by vectorizing
// Assuming your mask has values > 0 for glacier areas
var glacier_mask = glacier_image.select(0).gt(0).selfMask()
  .reduceToVectors({
    geometry: glacier_image.geometry(),
    scale: 30,
    geometryType: 'polygon',
    eightConnected: false,
    maxPixels: 1e9
  });

// Get the geometry bounds for centering the map
var bounds = glacier_mask.geometry().bounds();
var center = bounds.centroid(1); // Add error margin of 1 meter

// Center the map
Map.centerObject(center, 12);

// Add the glacier mask to the map
Map.addLayer(glacier_mask, {color: 'red', strokeWidth: 2}, 'Saskatchewan Glacier Mask');

// Print information about the mask
print('🏔️ Saskatchewan Glacier Mask Information:');
print('Number of features:', glacier_mask.size());
print('Bounds:', bounds.coordinates());
print('Area (sq km):', glacier_mask.geometry().area(1).divide(1000000));

// Export as GeoJSON for use with Python modis-tools
Export.table.toDrive({
  collection: glacier_mask,
  description: 'saskatchewan_glacier_mask',
  folder: 'MODIS_Downloads',
  fileFormat: 'GeoJSON'
});

// Also export as Shapefile (alternative format)
Export.table.toDrive({
  collection: glacier_mask, 
  description: 'saskatchewan_glacier_shapefile',
  folder: 'MODIS_Downloads',
  fileFormat: 'SHP'
});

print('📤 Export tasks created:');
print('1. saskatchewan_glacier_mask.geojson - For precise spatial filtering');
print('2. saskatchewan_glacier_shapefile.shp - Alternative format');
print('');
print('🐍 After download, use with Python modis-tools:');
print('downloader = SaskatchewanGlacierModisDownloader(');
print('    username="your_username",');
print('    password="your_password",');
print('    glacier_mask_path="saskatchewan_glacier_mask.geojson"');
print(')');

// Show a simple comparison of bounding box vs precise geometry
var bbox = bounds;
var bbox_feature = ee.Feature(bbox, {type: 'bounding_box'});

Map.addLayer(bbox_feature, 
  {color: 'blue', fillColor: 'blue', strokeWidth: 2, fillOpacity: 0.1}, 
  'Bounding Box (less precise)');

// Calculate area difference (with error margins)
var glacier_area = glacier_mask.geometry().area(1);
var bbox_area = bbox.area(1);
var area_ratio = glacier_area.divide(bbox_area).multiply(100);

print('📊 Spatial Filtering Comparison:');
print('Glacier area (sq km):', glacier_area.divide(1000000));
print('Bounding box area (sq km):', bbox_area.divide(1000000));
print('Glacier coverage of bbox (%):', area_ratio);
print('');
print('💡 Using glacier mask vs bounding box:');
print('✅ More precise spatial filtering');
print('✅ Fewer unnecessary downloads');
print('✅ Better data efficiency');