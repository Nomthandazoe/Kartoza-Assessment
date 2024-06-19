import os
from osgeo import gdal, ogr

# Setting the environment variable to enable DLL path for GDAL on Python >= 3.8
os.environ['USE_PATH_FOR_GDAL_PYTHON'] = 'YES'


def remove_spikes(polygon, angle_threshold, distance_threshold):
    # Logic to remove spikes from the polygon
    polygon.SimplifyPreserveTopology(angle_threshold, distance_threshold)


def main():
    gdal.UseExceptions()

    # Input and Output file paths
    input_file = "ProspectiveDevelopers/spiky-polygons.gpkg"
    output_file = "ProspectiveDevelopers/output.gpkg"

    # Open input GeoPackage dataset
    file = gdal.OpenEx(input_file, gdal.OF_VECTOR)
    if file is None:
        print(f"Failed to open GeoPackage file: {input_file}")
        return 1

    polygon_layer = file.GetLayer(1)  

    # Create an output GeoPackage dataset
    driver = gdal.GetDriverByName("GPKG")
    polygon_output_ds = driver.Create(output_file, 0, 0, 0, gdal.GDT_Unknown)
    if polygon_output_ds is None:
        print(f"Failed to create output GeoPackage file: {output_file}")
        file = None
        return 1

    # Copy the spatial reference system (SRS) from input dataset to the output data
    polygon_srs = polygon_layer.GetSpatialRef()
    polygon_output_ds.SetSpatialRef(polygon_srs)

    # Create a layer in the output dataset
    po_output_layer = polygon_output_ds.CreateLayer("cleaned_polygons", polygon_srs, ogr.wkbPolygon)

    # Define angle and distance thresholds for spike removal
    angle_threshold = 1.0  # degrees
    distance_threshold = 100000.0  # meters

    # Iterate through features (polygons) in the input layer
    polygon_layer.ResetReading()
    for polygon_feature in polygon_layer:
        polygon_geometry = polygon_feature.GetGeometryRef()
        if polygon_geometry is not None and polygon_geometry.GetGeometryType() == ogr.wkbPolygon:
            po_polygon = polygon_geometry.Clone()

            # Remove spikes from the polygon
            remove_spikes(po_polygon, angle_threshold, distance_threshold)

            # Create a new feature in the output layer with the cleaned polygon
            po_output_feature = ogr.Feature(po_output_layer.GetLayerDefn())
            po_output_feature.SetGeometry(po_polygon)
            if po_output_layer.CreateFeature(po_output_feature) != ogr.OGRERR_NONE:
                print("Failed to create feature in output layer.")
                file = None
                polygon_output_ds = None
                return 1

            po_output_feature = None

    # Cleanup
    file = None
    polygon_output_ds = None

    print(f"Spike removal completed. Output saved to: {output_file}")
    return 0


if __name__ == "__main__":
    main()
