'''
Program:    DifferenceVolumeCalculation.py
Programmer: Mohit Francis
Date:       27 April 2023
Purpose:    GISY 6044 - Difference of DEM Volume and Zonal Statistics Geoprocessing Script Tool
            Calculates the difference between two DEMs, multiplies the resulting DEM by the cell area (0.25m * 0.25m) to calculate the difference in volume,
            and calculates zonal statistics for the entire study area, the three zones, the AOIs, and all combined.
'''



##----------- Setup



## Import libraries.
import arcpy
from arcpy.ia import *
from arcpy.sa import *

## Check out the ArcGIS Image Analyst and Spatial Analyst extension licenses.
arcpy.CheckOutExtension("ImageAnalyst")
arcpy.CheckOutExtension("Spatial")

## Set-up work space variables based on user specified inputs (Defaults are set to the workspaces on my SSD).
currWS = arcpy.GetParameterAsText(0)
currGDB = arcpy.GetParameterAsText(1)

## Activate overwrite mode to overwrite all settings, created feature classes, and exported rasters and tables.
arcpy.env.overwriteOutput = True

## Set current ArcGIS workspace where output and reads will occur.
arcpy.env.workspace = currWS

## Set Snap Raster environment to align all rasters with the specified raster DEM (June 01 L1) since the June 01 Orthophoto was used to draw boundaries.
arcpy.env.snapRaster = "D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/ClippedRasters.gdb/c20220601_CJ_L1Lidar_Nadir_25cmDEM_Min_noVF_clipped"



##----------- Raster Calculator (Difference of DEM)



## Set local variables for RasterCalculator(Minus).
in_raster1 = arcpy.GetParameterAsText(2)
in_raster2 = arcpy.GetParameterAsText(3)
minus_raster_name = arcpy.GetParameterAsText(4) + '.tif'

## Set variables for Extract by Mask function.

## Execute RasterCalculator(Minus) function.
output_minus_raster = RasterCalculator([in_raster1, in_raster2],["x", "y"],"x-y","FirstOf","FirstOf")

## Extract cells only within Study Area.
extracted_minus_raster = arcpy.sa.ExtractByMask(output_minus_raster, "D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/VectorData.gdb/BoundarySoilZonesAOI")

## Save the output to specified folder as TIFF with user specified name and to specified file geodatabase with specified name.
extracted_minus_raster.save('D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/ExportedData/Rasters/MinusDEMs/' + minus_raster_name)
#extracted_minus_raster.save('D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/ExportedData/Rasters/MinusDEMs/MinusRasters.gdb' + minus_raster_name)



##----------- Raster Calculator (Volume)



## Set variables for RasterCalculator(Volume).
volume_constant = 0.0625 # 0.25 * 0.25 = 0.0625
volume_raster_name = arcpy.GetParameterAsText(5) + '.tif'

## Execute RasterCalculator(MinusRaster*0.0625) function.
output_volume_raster = RasterCalculator([output_minus_raster, volume_constant],["x", "y"],"x*y","FirstOf","FirstOf")

## Extract cells only within Study Area.
extracted_volume_raster = arcpy.sa.ExtractByMask(output_volume_raster, "D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/VectorData.gdb/BoundarySoilZonesAOI")

## Save the output to specified folder as TIFF with user specified name.
extracted_volume_raster.save("D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/ExportedData/Rasters/VolumeDEMs/Differences" + volume_raster_name)
#extracted_volume_raster.save('D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/ExportedData/Rasters/MinusDEMs/DifferenceVolumeRasters.gdb' + volume_raster_name)



##----------- Zonal Statistics (Whole Study Area)



## Set local variables for Whole Study Area Zonal Statistics Calculation
in_zone_data = "D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/VectorData.gdb/Boundary"
zone_field = "Name"
in_value_raster = extracted_volume_raster
out_table = arcpy.GetParameterAsText(6)
study_area_stats = out_table + '.csv'
percentile_values = [0,10,20,25,30,40,50,60,68,70,75,80,90,95,99,100]

## Calculate all statistics types for the study area
out = arcpy.ia.ZonalStatisticsAsTable(in_zone_data,zone_field,in_value_raster,out_table,'DATA','ALL','CURRENT_SLICE',percentile_values,'AUTO_DETECT')


## Export table as CSV and save to specified folder with user entered name.
arcpy.conversion.TableToTable(out,r'D:\NSCC_COGS\Winter\GISY6044_AppliedGeomaticsResearchProject\Procedure\DEMWork\ExportedData\Tables\ZonalStatistics\Differences\StudyArea', study_area_stats)



##----------- Zonal Statistics (Beach, Bank, Upper Bank Zones)



## Set local variables for Zones Zonal Statistics Calculation
in_zone_data = "D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/VectorData.gdb/BoundaryAOI"
zone_field = "FullName"
in_value_raster = extracted_volume_raster
out_table = arcpy.GetParameterAsText(7)
zone_stats = out_table + '.csv'
percentile_values = [0,10,20,25,30,40,50,60,68,70,75,80,90,95,99,100]

## Calculate all statistics types for the zones.
out = arcpy.ia.ZonalStatisticsAsTable(in_zone_data,zone_field,in_value_raster,out_table,'DATA','ALL','CURRENT_SLICE',percentile_values,'AUTO_DETECT')

## Export table as CSV and save to specified folder with user entered name.
arcpy.conversion.TableToTable(out,r'D:\NSCC_COGS\Winter\GISY6044_AppliedGeomaticsResearchProject\Procedure\DEMWork\ExportedData\Tables\ZonalStatistics\Differences\Zones', zone_stats)



##----------- Zonal Statistics (Sand, Channel, Rock Armour, Clay, Glacial Till, Bedrock Cliff AOIs)



## Set local variables for AOI Zonal Statistics Calculation
in_zone_data = "D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/VectorData.gdb/BoundarySoilZones"
zone_field = "FullName"
in_value_raster = extracted_volume_raster
out_table = arcpy.GetParameterAsText(8)
aoi_stats = out_table + '.csv'
percentile_values = [0,10,20,25,30,40,50,60,68,70,75,80,90,95,99,100]

## Calculate all statistics types for the AOIs
out = arcpy.ia.ZonalStatisticsAsTable(in_zone_data,zone_field,in_value_raster,out_table,'DATA','ALL','CURRENT_SLICE',percentile_values,'AUTO_DETECT')

## Export table as CSV and save to specified folder with user entered name.
arcpy.conversion.TableToTable(out,r'D:\NSCC_COGS\Winter\GISY6044_AppliedGeomaticsResearchProject\Procedure\DEMWork\ExportedData\Tables\ZonalStatistics\Differences\AOI', aoi_stats)



##----------- Zonal Statistics (Intersect of all zones and AOIs within study area)



## Set local variables for Combined Zonal Statistics Calculation
in_zone_data = "D:/NSCC_COGS/Winter/GISY6044_AppliedGeomaticsResearchProject/Procedure/DEMWork/VectorData.gdb/BoundarySoilZonesAOI"
zone_field = "FullName"
in_value_raster = extracted_volume_raster
out_table = arcpy.GetParameterAsText(9)
all_stats = out_table + '.csv'
percentile_values = [0,10,20,25,30,40,50,60,68,70,75,80,90,95,99,100]

## Calculate all statistics types for the intersected area
out = arcpy.ia.ZonalStatisticsAsTable(in_zone_data,zone_field,in_value_raster,out_table,'DATA','ALL','CURRENT_SLICE',percentile_values,'AUTO_DETECT')

## Export table as CSV and save to specified folder with user entered name.
arcpy.conversion.TableToTable(out,r'D:\NSCC_COGS\Winter\GISY6044_AppliedGeomaticsResearchProject\Procedure\DEMWork\ExportedData\Tables\ZonalStatistics\Differences\Combined', all_stats)



##----------- End



## Return the ArcGIS Image Analyst and Spatial Analyst extension licenses
arcpy.CheckInExtension("ImageAnalyst")
arcpy.CheckInExtension("Spatial")