# MODIS Tools

Currently a couple of fairly basic tools here, based around a common template file that sets the paramters used for the tools. Run both tools with the same template file.

The tools scale to allow processing of the whole MODIS time series, disk space permitting.

Use `jgomezdans/get_modis` to download MODIS data.


## stitch_warp_modis_l2.py

For specified Level-2 MODIS tiles, stitch them together and then warp into a specified target projection, extent and resolution. Outputs a GeoTiff per band of data.


## modisgtiff2nc.py

Designed to be run following `stitch_warp_modis_l2.py`. Collates GeoTiffs for each band of data then saves them to annual netCDF files. 