#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Andrew Tedstone
# @Date:   2016-05-10 17:27:28
# @Last Modified by:   Andrew Tedstone
# @Last Modified time: 2016-10-05 17:36:42
"""
Uses same parameter template file as stitch_warp_modis_l2.py

Usage:
	modis_margrid2netcdf.py <template_file>

Returns:
	Nothing

"""

import os
import numpy as np
import logging
import pandas as pd
import xarray as xr
import calendar
import datetime as dt
import configparser
import sys

import georaster

config = configparser.ConfigParser()
config.read_file(open(sys.argv[1]))

# Arguments
bands = config.get('Params','bands').split(',')
bands = [b.strip() for b in bands]

year_start = int(config.get('Params','year_start'))
year_end = int(config.get('Params','year_end'))
st = int(config.get('Params','day_start'))
en = int(config.get('Params','day_end'))
if calendar.isleap(year_start):
	# If we don't do this and the script is asked to start on a leap year
	# then it will fail if no file available for the specified st
	st += 1
	en += 1
product = config.get('Params','product')
version = config.get('Params','version')
# Contains outputs of stitch_warp_modis_l2, and we'll save the netCDF there too
io_path = config.get('Params','output_path')
out_label = config.get('Params','out_label')
grid_name = config.get('Params','grid_name')
cleanup = config.get('Params','cleanup')
overwrite = bool(config.get('Params','overwrite'))

def int_or_float(s):
    try:
        return int(s)
    except ValueError:
    	try:
        	return float(s)
    	except:
    		return None

missing_values = config.get('Params','missing_value').split(',')
missing_values = [int_or_float(b.strip()) for b in missing_values]

scale_factors = config.get('Params','scale_factor').split(',')
scale_factors = [int_or_float(b.strip()) for b in scale_factors]

# Move to output directory
os.chdir(io_path)

## Spatial coordinates
# Load up a geotiff to retrieve grid
infile = product + '.' + 'A' + str(year_start) + str(st).zfill(3) + '.' + version + '.' + bands[0] + '.' + out_label + '.tif'
im = georaster.SingleBandRaster(infile)
nx = im.nx
ny = im.ny
x,y = im.coordinates()
# Coordinates returned by georaster are centre-of-pixel, set to lowerleft
x = x[1,:]
x = x - (im.xres / 2)
y = y[:,1]
# Reverse y coordinate order - !!important!! otherwise slicing doesn't work properly
y = y[::-1]
y = y + (im.yres / 2)

# Iterate by year
for yr in range(year_start, year_end):

	print(yr)

	## Temporal coordinates
	start_date = dt.datetime.strptime(str(yr) + ' ' + str(st), '%Y %j').strftime('%Y-%m-%d')
	times = pd.date_range(start_date, periods=en-st)
	coords = {'Y':y, 'X':x, 'TIME':times}

	# Deal with each band as a separate DataArray in turn
	data_arrays = {}
	to_clean = []
	for b,s_f,m_v in zip(bands,scale_factors,missing_values):

		print(b)

		if m_v == None:
			m_v = np.nan

		print(m_v)
		# Iterate through season of daily gridded MODIS acquisitions
		di = 0
		data = np.zeros((en-st, ny, nx))
		for d in range(st, en):

			# Pad julian day to three digits (MODIS filename format)
			d =  str(d).zfill(3)

			# Read in file
			infile = product + '.' + 'A' + str(yr) + d + '.' + version + '.' + b + '.' + out_label + '.tif'
			to_clean.append(infile)
			# First close the last file that was open
			im = None
			try:
				im = georaster.SingleBandRaster(infile)
				dtype = im.r.dtype
			except RuntimeError:
				print(d + ' missing')
				# Data on this day missing, skip it
				data[di,:,:] = m_v
				di += 1
				continue

			# Save to numpy array
			# Very memory intensive!
			data[di,:,:] = np.flipud(im.r)

			di += 1

		# Convert to data array
		# Get dtype from the last band image that was opened
		da = xr.DataArray(data.astype(dtype), coords=[times, y, x], dims=['TIME', 'Y', 'X'],
			encoding={'dtype':dtype})

		#Add mask_and_scale parameters if specified
		if s_f:
			print('adding scaling factor...')
			da.attrs['scale_factor'] = s_f
		if m_v:
			print('adding missing value...')
			da.attrs['missing_value'] = m_v

		# Save data array
		# There's probably a less memory-intensive way of doing this...
		data_arrays[b] = da

		# Close last image link
		im = None

	# Create Dataset and save to netCDF
	ds = xr.Dataset(data_arrays)
	ds.to_netcdf(io_path + product + '.' + str(yr) + '.' + version + '.' + out_label + '.nc')
	ds = None

	# Do cleanup after annual netCDF file written.
	if cleanup == 'True':
		for f in to_clean:
			try:
				os.remove(f)
			except FileNotFoundError:
				pass



