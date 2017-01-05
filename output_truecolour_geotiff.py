"""

Create a true-colour geotiff from MOD09GA data on MAR grid stored in a netCDF.

For plotting example see kohler_carbon/AGU_plot_snowline.py

@author Andrew Tedstone
@created 2017-01-05

"""

import xarray as xr
import numpy as np
from scipy import interpolate

import mar_raster

mar_proj = mar_raster.proj('10km')

refl = xr.open_dataset('/scratch/MOD09GA.006.SW/MOD09GA.2016.006.reprojb1234q.nc')

date = '2016-07-22'

b01 = refl.sur_refl_b01_1.sel(TIME=date).values
b04 = refl.sur_refl_b04_1.sel(TIME=date).values
b03 = refl.sur_refl_b03_1.sel(TIME=date).values
max_vals = np.array([np.nanmax(b01), np.nanmax(b03), np.nanmax(b04)])
min_vals = np.array([np.nanmin(b01), 
					 np.nanmin(b03), 
					 np.nanmin(b04)])
# This LUT is tuned for the west GrIS margin
refl_values = [min_vals.min(), -0.01, 0.10, 0.45, 0.9, max_vals.max()]
bright = [0, 1, 60, 180, 254, 255]
lut = interpolate.interp1d(refl_values, bright)
b01b = lut(b01)
b03b = lut(b03)    
b04b = lut(b04)
rgb = np.stack((b01b, b04b, b03b), axis=2)

# Create geo transform using limits of grid, nb these may be out by up to the size of a cell
geo_trans = (-586678, 613.9225092250854, 0, 69833.47619047618, 0, -614.5238095237873)
proj4 = mar_raster.grids['10km']['spatial_ref']
tiff = georaster.MultiBandRaster.from_array(np.flipud(rgb).astype('uint16'), geo_trans, proj4)
tiff.save_geotiff('/home/at15963/MOD09GA-RGB-GrIS-SW-20160722.tif', dtype=georaster.gdal.GDT_UInt16)