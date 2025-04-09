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
projectRaster = r'C:\Users\cclar\Documents\RRK\boundary\RRK_CenCoast.tif'
intCellSize = 30

#environments
arcpy.env.outputCoordinateSystem = projectRaster
arcpy.env.snapRaster = projectRaster
arcpy.env.cellSize = intCellSize
arcpy.env.mask = projectRaster
arcpy.env.compression = "LZW"
arcpy.env.overwriteOutput = True
arcpy.env.resamplingMethod = 'NEAREST'
arcpy.env.pyramid = 'PYRAMIDS -1 NEAREST'
arcpy.env.scratchWorkspace = r'C:\Users\cclar\Documents\RRK\scratch'
############

strPath =  r'C:\Users\cclar\Documents\RRK\FRID_working\scripting_runs_AllCenCoast\6_Compressed'
strInputPath = strPath
strOutputPath = r'C:\Users\cclar\Documents\RRK\FRID_working\scripting_runs_AllCenCoast\7_999_removal'

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
        #strOutputRaster = os.path.join(strOutputPath, strEachTif.replace('.tif','.tif'))
        #strOutputRaster = os.path.join(strOutputPath, strEachTif.replace('.tif','_compressed.tif'))
        strOutputRaster = os.path.join(strOutputPath, os.path.basename(strInputRaster))
        if os.path.exists(strOutputRaster):
            print(f'{strOutputRaster} exists, skipping...')
        else:
            strCurrentTime = datetime.now().strftime('%H:%M:%S')
            #print('Copying ' + f'{strEachTif} LZW Start Time = {strCurrentTime}')
            #arcpy.CopyRaster_management(strInputRaster, strOutputRaster)
            print('Removing 999s from ' + f'{strEachTif}')
            rasOutput = ExtractByAttributes(strInputRaster, "Value > -999")
            rasOutput.save (strOutputRaster)


            #######################################################################
##        if os.path.exists(strInputRaster):
##            if os.path.exists(strOutputRaster):
##                print ("Renaming " + strInputRaster)
##                strBigRaster = os.path.basename(strInputRaster.replace('.tif' ,'_uncompressed.tif',))
##                strBigPath = os.path.join(strOutputPath, strBigRaster)
##                arcpy.management.Rename(strInputRaster, strBigPath)
##                print ("Renaming " + strOutputRaster + " to " + strInputRaster)
##                arcpy.management.Rename(strOutputRaster, strInputRaster)

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
