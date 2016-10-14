#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: at15963
# @Date:   2016-04-19 12:57:45
# @Last Modified by:   Andrew Tedstone
# @Last Modified time: 2016-10-13 11:41:58

"""

This script mosaics several spatially contiguous MODIS sinusoidal tiles, 
reprojects the mosaic onto a specified grid in GeoTIFF format.

Usage:
	stitch_warp_modis_l2.py <template_file>

Create a parameter template file in the standard Python format, i.e.:

[Params]
tiles=h16v02,h15v02
cleanup=True
...

Inspired by jgomezdans.github.io/stitching-modis-burned-area-datasets.html.

"""

import subprocess
from glob import glob
import os
import logging
import datetime as dt
import configparser
import sys

config = configparser.ConfigParser()
config.read_file(open(sys.argv[1]))

# Arguments
tiles = config.get('Params','tiles').split(',')
tiles = [t.strip() for t in tiles]

bands = config.get('Params','bands').split(',')
bands = [b.strip() for b in bands]

year_start = int(config.get('Params','year_start'))
year_end = int(config.get('Params','year_end'))
st = int(config.get('Params','day_start'))
en = int(config.get('Params','day_end'))
product = config.get('Params','product')
version = config.get('Params','version')
input_path = config.get('Params','input_path')
output_path = config.get('Params','output_path')
out_label = config.get('Params','out_label')
grid_name = config.get('Params','grid_name')
cleanup = config.get('Params','cleanup')
grid = config.get('Params','grid')
overwrite = config.getboolean('Params','overwrite')


# Move to output directory
os.chdir(output_path)

# Set up logging
log_out = output_path + out_label + '.txt'
logging.basicConfig(filename=log_out, level=logging.INFO, format='%(message)s')
logging.info("\n\n" + dt.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p") +
        ": BEGINNING NEW PROCESSING BATCH")

# Iterate by year
for y in range(year_start, year_end):

	print('**** ' + str(y))

	# Iterate through season of daily gridded MODIS acquisitions
	for d in range(st,en+1):

		# Pad julian day to three digits (MODIS filename format)
		d =  str(d).zfill(3)	

		for b in bands:

			# Generate name of mosaiced output file
			mosaic_outfile = product + '.' + 'A' + str(y) + d + '.' + version + '.' + b + '.' + out_label + '.tif'
			
			# Check if file already generated
			if os.path.exists(mosaic_outfile) and overwrite == False:
				logging.info(str(y) + d + ': ' + b + ': band TIF already exists, skipping')
				continue

			# Generate VRTs
			vrtfiles = ''
			count = 0
			for t in tiles:
				fn = glob(input_path + product + '.A' + str(y) + d + '.' + t + '.' + version + '.*.hdf')

				# Check that tile file is available
				try:
					fn = fn[0]
				except IndexError:
					logging.error(str(y) + d + ': ' + b + ': tile ' + t + ' not available.')
					continue

				infile = 'HDF4_EOS:EOS_GRID:"' + fn + '":' + grid_name + ':' + b
				outfile = product + '.' + 'A' + str(y) + d + '.' + t + '.' + b + '.vrt'
				vrtfiles += ' ' + outfile
				cmd = 'gdal_translate -of VRT ' + infile + ' ' + outfile 
				
				print('** CMD ** ' + cmd)
				p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
					stderr=subprocess.PIPE,	shell=True)
				(stdout,stderr) = p.communicate()
				p.wait()
				if p.returncode != 0:
					logging.error(str(y) + d + ': ' + b + ': gdal_translate failed: ' + str(stderr))
					continue

				count += 1


			# Sanity-check number of tiles available
			if count < len(tiles):
				logging.error(str(y) + d + ': ' + b + ': not all tiles present.')
				continue


			# Mosaic and warp for this day
			cmd = 'gdalwarp -of GTiff ' + grid + ' ' + vrtfiles + ' ' + mosaic_outfile
			
			print('** CMD ** ' + cmd)
			p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
				stderr=subprocess.PIPE,	shell=True)
			(stdout,stderr) = p.communicate()
			p.wait()
			if p.returncode != 0:
				logging.error(str(y) + d + ': ' + b + ': gdalwarp failed: ' + str(stderr))
				continue


			# Remove VRT files
			if cleanup == 'True':
				for f in glob('*.vrt'):
					os.remove(f)