#
# exports FRID Attributes after masking & snapping to ACCEL
#
#
### Next iterations:
### - save each att to different directories in turn
### - import requested FRID Attributes list from a csv or xlsx
### - overwrite if an autolck exists (crash/unfinished condition indicator)
### - - Using time last written to as an indicator?
#


##Do you need to Change Me?
strTargetYear = '21'


import os
import arcpy
import traceback
from arcpy.sa import *
from datetime import datetime

dtmStartTime = datetime.now()
strCurrentTime = datetime.now().strftime('%H:%M:%S')
print('')
print(f'Start Time = {strCurrentTime}')
print('')

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
strInputPath = r'C:\Users\cclar\Documents\RRK\FRID_working\FRID_Polygons_RSL'
strOutputPath = os.path.join(strPath,'1_Attributes')

lstAllDirs = next(os.walk(strInputPath))[1] #gets only directories

lstToKeep = [
                #'CentralValley',
                #'SouthCoast',
                #'SouthInterior',
                #'SouthSierra',
                'CentralCoast',
                'NorthCoast'
                #'SouthInterior'
             ]

lstFRIDAttributes = [
                        #remember to adjust commas!

                        #DONE:
                        'TSLF',
                        'currentFRI',
                        'currentFRI_1970',
                        'meanPFRID',
                        'meanPFRID_1970',
                        #'maxPFRID',
                        #'medianPFRID',
                        #'minPFRID',
                        'meanCC_FRI'
                        #'meanCC_FRI_1970'
                        #'YLF',
                        #'LastFireName',
                        #'numFires',
                        #'numFires_1970',
                        #'firesLast40',
                        #'PFR',
                        #'fireRegimeGrp',
                        #'meanRefFRI'
                        #'medianRefFRI',
                        #'minRefFRI',
                        #'maxRefFRI',
                        #'meanCC_FRI',
                        #'meanCC_FRI_1970',
                        #'NPS_FRID',
                        #'NPS_FRID_Index',

                        #remember to adjust commas!
                   ]

strCurrentTime = datetime.now().strftime('%H:%M:%S')
print(f'Loop Start Time = {strCurrentTime}')

# filter all dirs for just dirs to keep
lstTargetGDBs = [r for r in lstAllDirs if any(s in r for s in lstToKeep)]

try:
        for strEachFRIDAttribute in lstFRIDAttributes:
                print(f'\n\nProcessing {strEachFRIDAttribute}...')
                strCurrentTime = datetime.now().strftime('%H:%M:%S')
                print(f'FRIDAtts Time = {strCurrentTime}\n\n')
                for strEachGDB in lstTargetGDBs:
                        strInputFCName = strEachGDB.replace('.gdb','')
                        strInputFeatureClass = os.path.join(strInputPath, strEachGDB, strInputFCName)
                        strOutputFCTemp = strInputFCName.replace('FRID_','').replace('_1','')
                        strOutputFCName = f'{strEachFRIDAttribute}_{strOutputFCTemp}.tif'
                        strCurrentTime = datetime.now().strftime('%H:%M:%S')
                        strOutputRaster = os.path.join(strOutputPath, strOutputFCName)
                        strCurrentTime = datetime.now().strftime('%H:%M:%S')
                        print(f'Begin Time = {strCurrentTime}')
                        print(f'working on {strOutputFCName}')
                        if os.path.exists(strOutputRaster):
                                print(f'{strOutputRaster} exists, skipping.')
                        else:
                                arcpy.env.extent = r'C:\Users\cclar\Documents\RRK\boundary\RRK_CenCoast.tif'
                                arcpy.conversion.PolygonToRaster(strInputFeatureClass, strEachFRIDAttribute, strOutputRaster,
                                                 cell_assignment='CELL_CENTER', cellsize=intCellSize,
                                                 priority_field=None, build_rat='BUILD')

        print('*********************************\n*********************************\n*********************************\n'
              '\n\tFRID_Attributes is ... \n\tD\n\tO\n\tN\n\tE\n\n'
              '*********************************\n*********************************\n*********************************\n')

except:  # General non GP errors
        strCurrentTime = datetime.now().strftime('%H:%M:%S')
        print(f'Crash Time = {strCurrentTime}')
        exc_type, exc_value, exc_traceback = sys.exc_info()
        strTrace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(strTrace)

strCurrentTime = datetime.now().strftime('%H:%M:%S')
print(f'End Time = {strCurrentTime}\n')
