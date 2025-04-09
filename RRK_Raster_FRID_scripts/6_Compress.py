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

strPath =  r'C:\Users\cclar\Documents\RRK\FRID_working\scripting_runs_AllCenCoast'
strInputPath = os.path.join(strPath,'7_999_removal')
strOutputPath = os.path.join(strPath,'8_CompressAgain')

lstAllFiles = os.listdir(strInputPath)

lstAllTifs = []
for strFile in lstAllFiles:
    if strFile.lower().endswith('.tif'):
        print (f'{strFile} added to list...')
        lstAllTifs.append(strFile)

strCurrentTime = datetime.now().strftime('%H:%M:%S')
print(f'Loop Start Time = {strCurrentTime}')

try:
    for strEachTif in lstAllTifs:
        strInputRaster = os.path.join(strInputPath, strEachTif)
        strOutputRaster = os.path.join(strOutputPath, f'{strEachTif}')
        if os.path.exists(strOutputRaster):
            print(f'{strOutputRaster} exists, skipping...')
        else:
            strCurrentTime = datetime.now().strftime('%H:%M:%S')
            print(f'{strEachTif} LZW Start Time = {strCurrentTime}')
            arcpy.CopyRaster_management(strInputRaster, strOutputRaster)
        
    print('*********************************\n*********************************\n*********************************'
          '\n\t COMPRESS_LZW is...\n\n\tD\n\tO\n\tN\n\tE\n\n'
          '*********************************\n*********************************\n*********************************\n')

except:  # General non GP errors
    exc_type, exc_value, exc_traceback = sys.exc_info()
    strTrace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(strTrace)

#% Ending Block
dtmEndTime = datetime.now()
strCurrentTime = datetime.now().strftime('%H:%M:%S')
print(f'End Time = {strCurrentTime}')
dtdTotalTime = dtmEndTime - dtmStartTime
strTotalTime = str(dtdTotalTime)
print(f'\n\nTotal Time: {strTotalTime}')
