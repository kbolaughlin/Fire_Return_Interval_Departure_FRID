
#############################################################
#                                                           #
#                                                           #
#       This currently fails for NPS_FRID_INDEX.            #
#                                                           #
#                                                           #
#############################################################

import os
import arcpy
import traceback
from arcpy.sa import *

arcpy.CheckOutExtension('Spatial')

#environment variables
F3_env = r'C:\Users\cclar\Documents\RRK\boundary\RRK_CenCoast.tif'
intCellSize = 30

#environments
arcpy.env.outputCoordinateSystem = F3_env
arcpy.env.snapRaster = F3_env
arcpy.env.cellSize = intCellSize
arcpy.env.mask = r'C:\Users\cclar\Documents\RRK\boundary\RRK_CenCoast.tif'
arcpy.env.compression = "LZW"
arcpy.env.overwriteOutput = True
arcpy.env.resamplingMethod = 'NEAREST'
arcpy.env.pyramid = 'PYRAMIDS -1 NEAREST'
arcpy.env.scratchWorkspace = r'C:\Users\cclar\Documents\RRK\scratch'
arcpy.env.extent = r'C:\Users\cclar\Documents\RRK\boundary\RRK_CenCoast.tif'
############

strPath =  r'C:\Users\cclar\Documents\RRK\FRID_working\scripting_runs2'
strInputPath = os.path.join(strPath,'2_NoData')
strOutputPath = os.path.join(strPath,'3_Mosaic')
lstFRIDAttributes = [
##                        'YLF',
                          'TSLF',
##                        'LastFireName',
##                        'numFires',
##                        'numFires_1970',
##                        'firesLast40',
##                        'PFR',
##                        'fireRegimeGrp',
                          'currentFRI',
                          'currentFRI_1970',
##                        'meanRefFRI',
##                        'medianRefFRI',
##                        'minRefFRI',
##                        'maxRefFRI',
                          'meanPFRID',
                          'meanPFRID_1970',
##                        'medianPFRID',
##                        'minPFRID',
##                        'maxPFRID',
                          'meanCC_FRI'
                          #'meanCC_FRI_1970'
##                        'NPS_FRID',
##                        'NPS_FRID_Index' #CURRENTLY A FAIL CONDITION
                    ]

lstAllFiles = os.listdir(strInputPath)

dctAllTifsByAttributes = {}
for strAttribute in lstFRIDAttributes:
    dctAllTifsByAttributes[strAttribute] = []

lstAllTifs = []
lstAllAttributes = []

for strFile in lstAllFiles:
    if strFile.lower().endswith('.tif'):
        print (f'{strFile} added to list...')
        lstAllTifs.append(strFile)
        #strAttribute = '_'.join(strFile.split('_')[:-3]) #<--------------FOR GAP FILES 
        strAttribute = '_'.join(strFile.split('_')[:-1]) #<--------------FOR NORMALLY NAMED FILES
        lstAllAttributes.append(strAttribute)
        dctAllTifsByAttributes[strAttribute] += [strFile]

lstAllAttributes = list(set(lstAllAttributes)) #get all unique values in list

for strEachAttribute in lstAllAttributes:
    if '1970' in strEachAttribute:
        lstDisco = ['1970']
        lstDanceFloor = dctAllTifsByAttributes[strEachAttribute]
        dctAllTifsByAttributes[strEachAttribute] = [attribute for attribute in lstDanceFloor if any(sub in attribute for sub in lstDisco)]
        #This removes files that don't have 1970 in them
#print(dctAllTifsByAttributes)

try:
    for strEachAttribute in lstAllAttributes:
        print(f'\nWorking on {strEachAttribute}...')
        lstCurrentTifs = dctAllTifsByAttributes[strEachAttribute]
        lstCurrentAttributeTifs = []
        if len(lstCurrentTifs) != 0:
            print (lstCurrentTifs)
            for strTif in lstCurrentTifs:
                lstCurrentAttributeTifs.append(Raster(os.path.join(strInputPath, strTif)))
            if not os.path.exists(os.path.join(strOutputPath, f'3_CenCst_{strEachAttribute}.tif')):
                print ('creating ' + f'3_CenCst_{strEachAttribute}.tif')
                arcpy.management.MosaicToNewRaster(lstCurrentAttributeTifs, strOutputPath, f'3_CenCst_{strEachAttribute}.tif',
                pixel_type='32_BIT_FLOAT',cellsize=30,number_of_bands=1,
                mosaic_method='MAXIMUM')

    print('*********************************\n*********************************\n*********************************'
          '\n\tFrom_Mosaic_To_CenCst is...\n\n\tD\n\tO\n\tN\n\tE\n\n'
          '*********************************\n*********************************\n*********************************\n')

except:  # General non GP errors
    exc_type, exc_value, exc_traceback = sys.exc_info()
    strTrace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(strTrace)

