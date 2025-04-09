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
#arcpy.env.mask = r'C:\Users\cclar\Documents\RRK\boundary\RRK_CenCoast.tif'
arcpy.env.compression = "LZW"
arcpy.env.overwriteOutput = True
arcpy.env.resamplingMethod = 'NEAREST'
arcpy.env.pyramid = 'PYRAMIDS -1 NEAREST'
arcpy.env.scratchWorkspace = r'C:\Users\cclar\Documents\RRK\scratch'
#arcpy.env.extent = r'C:\Users\cclar\Documents\RRK\boundary\RRK_CenCoast.tif'
############

strPath =  r'C:\Users\cclar\Documents\RRK\FRID_working\scripting_runs2'
strInputPath = os.path.join(strPath,'1_Attributes')
strOutputPath = os.path.join(strPath,'2_NoData')

lstAllFiles = os.listdir(strInputPath)

lstAllTifs = []
for strFile in lstAllFiles:
    if strFile.lower().endswith('.tif'):
        print (f'{strFile} added to list...')
        lstAllTifs.append(strFile)
    else:
        #print (f'ignoring {strFile}...')
        pass

strCurrentTime = datetime.now().strftime('%H:%M:%S')
print(f'Loop Start Time = {strCurrentTime}')

try:
    for strEachTif in lstAllTifs:
        strInputRaster = os.path.join(strInputPath, strEachTif)
        rasInput = Raster(strInputRaster)
        strOutputRaster = os.path.join(strOutputPath, strEachTif)
        if os.path.exists(strOutputRaster):
            print(f'{strOutputRaster} exists, skipping...')
        else:
            strCurrentTime = datetime.now().strftime('%H:%M:%S')
            print(f'{strEachTif} Nulls To -999 Start Time = {strCurrentTime}')
            rasOutput = Con(IsNull(rasInput),-999,rasInput)
            rasOutput.save(strOutputRaster)

    print('*********************************\n*********************************\n*********************************'
          '\n\tCLEAR_NoData_ToNull is...\n\n\tD\n\tO\n\tN\n\tE\n\n'
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
