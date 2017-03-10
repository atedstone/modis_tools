from glob import glob
import fnmatch

# files = glob('/scratch/MOD09GA.006.raw/*')
# files.sort()

# with open('/scratch/MOD09GA.006.raw/missing.txt', 'w') as log:
# 	for tile in ['h16v02','h15v02']:
# 		for y in range(2000,2017):
# 			print('****' + str(y), file=log)
# 			for doy in range(121,275):
# 				string = '*MOD09GA.A' + str(y) + str(doy).zfill(3) + '.' + tile + '.006.*.hdf'
# 				filtered = fnmatch.filter(files, string)
# 				if len(filtered) == 0:
# 					print(string, file=log)
# 			print('\n', file=log)




files = glob('/media/at15963/TOSHIBA EXT/MOD09GA.006.raw/*')
files.sort()

with open('/media/at15963/TOSHIBA EXT/MOD09GA.006.raw/missing.txt', 'w') as log:
	for y in range(2000,2010):
		print('****' + str(y), file=log)
		for doy in range(121,275):
			string = '*MOD09GA.A' + str(y) + str(doy).zfill(3) + '*h16v02*hdf'
			filtered = fnmatch.filter(files, string)
			if len(filtered) == 0:
				print(string, file=log)
		print('\n', file=log)