# FRID_Step1_PrepFiresPoly_w1970.py
### Manual Changes Required: 2
## VERY IMPORTANT!!! ******THIS SCRIPT RUNS EXTREMELY SLOW IF YOU TRY TO READ/WRITE FROM SERVER
## TO NAS. BEST TO COPY DATA TO LOCAL DRIVE ON SERVER AND READ/WRITE TO THERE.

# Updated FRID (Fire Return Interval Departure) script (#1) cclark 4/27/21 for Python 3.x
# This script takes fire perimeters and prescribed burns (fire<yr>_1.zip) downloaded from
# Calfire's FRAP site (be sure to copy it to FRID_<year> folder)
# and "flattens out" the overlapping data, leaving only the
# latest fire polygon for any spot on the ground
# It also adds FRID fields and dissolves final layer
#  This script intended to be run from Python IDLE Shell
# changed parser for Calculate field from VB to PYTHON to allow running on 64bit - also had to fix syntax on field names from
# [NAME] to !NAME!
# 6/2019 - Add eliminate to final fire layer of slivers less than 500 sq meters before dissolve
#5/2020 - Add fields and calculations per Hugh:  FRID metrics calculated since 1970 in order to compare changes over the last
# 50 years, since 1970 is when the National Park Service and some USFS wilderness areas began to allow naturally ignited fire to burn
# Unless you need to start script over where it left off, look for this line and change start_midway to equal 0

# Import system modules
import sys, string, os, arcpy, traceback, time
from os.path import isdir, join, normpath, split, exists
import fire_interval_v2 as fire
#import RSL_util
from time import *

##def message(string):
##    #print string
##    print (string) # for Python 3.x
##    arcpy.AddMessage(string)

# Local variables:
#Workspace = r"N:\project\frid\workspace"
Workspace = r"D:\frid\workspace" #<-----------------------------------CHANGED TO SPEED UP PROCESSING


#Earliest recorded fire year i.e. 1908
styearInput = "1908"
# National Park Service and some USFS wilderness areas began to allow naturally ignited fire to burn in 1970s
styearInput_1970 = "1970"
num = int(styearInput)
num_1970 = int(styearInput_1970)
print ("Beginning year is " + str(num) + " and " + str(num_1970))

#Current year
edyearInput = "2021" ##<-----------------------------------------CHANGE TO CURRENT FIRES
num2 = int(edyearInput)
print ("Ending year is " + str(num2))
#To calculate number of fires in last 40 yrs
yrsAgo = int(edyearInput) - 40
print("year used to calculate 'number of fires in last 40 yrs' is " +  str(yrsAgo))

timeStart = localtime()

#####################################################################

#FUNCTIONS

# ----------------------------------------------------------------------------
# Cleanup name fields
# ----------------------------------------------------------------------------
def cleanup(strin):
    lst2remove = ["'",
                  '"']
    for item in lst2remove:
        if type(strin) == type(None):
            strin = ""
        else:
            strin = strin.replace(item, "")
            strin = strin.strip()
    return strin
#---------------------------------------------------------
#  Make directory
# ----------------------------------------------------------------------------
def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    print ("creating directory: " + newdir)
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

# ----------------------------------------------------------------------------
#  Get Min Value
# ----------------------------------------------------------------------------
def get_min_year(datasrc):
    print('sourcing minimum year')
    #try:
    #rows = arcpy.SearchCursor(datasrc)
    with arcpy.da.SearchCursor(datasrc, "YEAR_") as rows:
        minval = 3000
        cnt = 0
        try:
            for row in rows:

    #                cnt += 1
    #                if cnt < 10:
    #                    print "Name: %s,# Year: %s, GIS Acres: %i" % (row.FIRE_LABEL, row.YEAR_, row.GIS_ACRES)
    ##            if ((minval > int(row.YEAR_)) and (int(row.YEAR_) >= minimum_year)):
    ##                minval = int(row.YEAR_)
                if minval > int(row[0]) and int(row[0]) >= minimum_year:
                    minval = int(row[0])
                    #print(minval)

            print('finished minimum year loop')

        except:
            print("Error getting minimum year - some records in " + datasrc + " may not have YEAR - check and delete")
            raise
        print("Minimum Year is: %i" % (minval))
        del row, rows
        return minval


# ----------------------------------------------------------------------------
#  is it a fire year?
# ----------------------------------------------------------------------------
def is_fire_year(datasrc, test_year):

    try:
        found = 0
        with arcpy.da.SearchCursor(datasrc, "YEAR_") as rows:            
            for row in rows:
                if str(test_year) == row[0]:
                    found = 1
                    break
        return found

    except:
        print("Error determining fire year")
        raise

# ----------------------------------------------------------------------------
#  Export to Shapefile
#    input_layer: layer to be exported (with selection in place)
#    output_layer: stub for new layer, which includes location
# ----------------------------------------------------------------------------
def export_shapefile(input_layer, output_layer):
    try:
        arcpy.CopyFeatures_management (input_layer, output_layer)
        print ("finished copyfeatures: " + input_layer + "to " + output_layer)
    except:
        print("Error CopyFeatures")
        raise

# ----------------------------------------------------------------------------
#  Create Temporary Fire Year Layer by selecting all fires for current year
# ----------------------------------------------------------------------------
def get_temp_fire_year(feature_layer_fires, current_year):

    try:
        if (is_input_shapefile): #THESE LOOK REVERSED TO ME, BUT IT WORKS...SO OK
             sql = ' [YEAR_] = \'' + str(current_year) + "' "
        else:
            sql = "\"YEAR_\" = '" + str(current_year) + "'"

        arcpy.SelectLayerByAttribute_management (feature_layer_fires, "NEW_SELECTION", sql)
        #print "finished SelectLayerByAttribute: " + feature_layer_fires + sql
        fire_year = "sfy" + str(current_year)
        if arcpy.Exists(fire_year):
            arcpy.Delete_management(fire_year)
    except:
        print("Error in the SelectLayerByAttribute step")
        raise

    export_shapefile(feature_layer_fires, fire_year)
    return fire_year
# ----------------------------------------------------------------------------
#  Union on the current year single file
# ----------------------------------------------------------------------------
def union_single(datasrc, current_year):
    try:

        if (is_output_shapefile):
                union_input = datasrc + ".shp"
        else:
                union_input = datasrc
        sfyu = datasrc + "u"

# HAD TO INTRODUCE A WHOLE NEW SET OF TEMPORARY FILES, ALL START WITH "sf".  THESE
# DEAL WITH THE ISSUE OF POLYGONS FROM A SINGLE YEAR OVERLAPPING
        #print "Processing Single Year Union: " + union_input
        arcpy.Union_analysis(union_input, sfyu, "NO_FID", ".001 meter", "GAPS")
        return sfyu

    except:
        print('First Union failure: ' + sfyu)
        raise
# ----------------------------------------------------------------------------
#LIST FIELDS: Lists fields and field properties for inputValue
# ----------------------------------------------------------------------------
def list_fields(inputValue, wildCard, fieldType):
##        '"""Lists fields (and selected properties) for inputValue"""
    if arcpy.Exists(inputValue) == 1:
        fieldList = arcpy.ListFields(inputValue, wildCard, fieldType)
        for field in fieldList:
#FORMATTING INFO: NAME = 50 spaces, TYPE = 15 spaces, LENGTH = 15 spaces, SCALE = 15 spaces, PRECISION = 15 spaces
            #print "NAME                                              " + "TYPE           " + "LENGTH         " + "SCALE          " + "PRECISION      "
            #print "-" * 100
            try:
                print (str(field.name)[0:50] + " "*(50-len(field.name)) \
                      + str(field.type)[0:15] + " "*(15-len(str(field.type))) \
                      + str(field.length)[0:15] + " "*(15-len(str(field.length))) \
                      + str(field.scale)[0:15] + " "*(15-len(str(field.scale))) \
                      + str(field.precision)[0:15] + " "*(15-len(str(field.precision))))
            except:
                print("ERROR: CAN'T ACCESS INFORMATION FOR " + field + "!")

        return 1
    else:
         print("ERROR: " + inputValue + " does not exist!")
         return 0

# ----------------------------------------------------------------------------
#  Update the shape_area field
# ----------------------------------------------------------------------------
def calc_shape_area(calc_input):
    #print( "calculating FIRE_AREA")
    try:
        aExpression = "float(!shape.area@squaremeters!)"
##        print( calc_input)
##        print("ShapeFieldName: \n" + str(gp.describe(calc_input).ShapeFieldName)
##        if ok:
##            print( "listed fields")
##        else:
##            print("did not list fields")
    except:
        print('fail aExpression in calc_shape_area')
    try:
        arcpy.CalculateField_management (calc_input,"FIRE_AREA",aExpression,"PYTHON")
    except:
        print('Calc. FIRE_AREA failure: ' + calc_input)
        raise
# ----------------------------------------------------------------------------
#  Dissolve the single fire year file on the SHAPE_AREA field and retain the year and label.
#  The label retained is the last one read by the code as it processes overlapping polygons.
#  This was arbitrary.
# ----------------------------------------------------------------------------
def dissolve_single(dissolve_input, current_year):
    try:
        if (is_output_shapefile):
            sfyd = "sfy" + str(current_year) +"d.shp"
        else:
            sfyd = "sfy" + str(current_year) +"d"

        #arcpy.Dissolve_management(dissolve_input, sfyd, "FIRE_AREA", "FIRE_LABEL LAST", "SINGLE_PART")
        arcpy.PairwiseDissolve_analysis(dissolve_input, sfyd, "FIRE_AREA", "FIRE_LABEL LAST", "SINGLE_PART")
        return sfyd
    except:
        print("Dissolve Single Year failure: " + sfyd)
        raise

# ----------------------------------------------------------------------------)


#  Setup Environement
# ----------------------------------------------------------------------------
def setup_environment():
    try:
# Setup Workspace
# _mkdir(strFinalFireW) #temp exclusion
        arcpy.env.workspace = strFinalFireW
        arcpy.env.scratchWorkspace = strFinalFireW
#       gp.XYResolution = "0.1"
#       gp.XYTolerance = "5"
        print("Workspace: " + (arcpy.env.workspace))
        print( "Fire Data: %s" % (input_fire_data))

# make a feature layer from shapefile for processing
        if arcpy.Exists("allfires_lyr"):
            arcpy.Delete_management ("allfires_lyr")
        fl_fires = "allfires_lyr"                
        if not arcpy.Exists(fl_fires):
           arcpy.MakeFeatureLayer_management(input_fire_data, fl_fires)
           
           
           print("created Feature Layer of allfires")

        return fl_fires
    except:
        print("Error Setting up Environment")
        raise

# ----------------------------------------------------------------------------
#  Repair Geometry
# ----------------------------------------------------------------------------
def repair_geometry(datasrc):
    try:
        if (is_output_shapefile):
            datasource = datasrc + ".shp"
        else:
            datasource = datasrc

        #print( "Repairing Geometry: " + datasource)
        arcpy.RepairGeometry_management(datasource)
    except:
        print("Unable to Repair Geometry: " + datasrc)
        raise

# ----------------------------------------------------------------------------
#  Add field to datasource given fieldname and data type
# ----------------------------------------------------------------------------
def add_field(datasrc, fieldname, type):
    try:
        if (is_output_shapefile):
            datasource = datasrc + ".shp"
        else:
            datasource = datasrc
        #print( "Adding Field: " + fieldname + " to " + datasource)
        arcpy.AddField_management(datasource, fieldname, type)

    except:
        print("Add field failure: " + fieldname + " to " + datasource)
        raise

# ----------------------------------------------------------------------------
#  Use CalculateField to fill in yearly values
# ----------------------------------------------------------------------------
def fill_field(datasrc, fieldname, filling, codetype):
    try:
        if (is_output_shapefile):
            datasource = datasrc + ".shp"
        else:
            datasource = datasrc

        #print( "Calculating Field: " + fieldname + " in " + datasource)

        arcpy.CalculateField_management(datasource, fieldname, filling, codetype, "")

    except:
        print('fill_Field failure: ' + datasource)
        raise

# ----------------------------------------------------------------------------
#  Dissolve datasource based on fieldname
#  Dissolves the whole new shapefile into one feature based on yr####
# ----------------------------------------------------------------------------
def dissolve_layer(datasrc, disfields):
    # print( disfields)
    try:
        if (is_output_shapefile):
            fyd = datasrc + "d.shp"
            datasource = datasrc + ".shp"
        else:
            fyd = datasrc + "d"
            datasource = datasrc

        print( "Dissolving Year: " + fyd)
        #arcpy.Dissolve_management(datasource, fyd, disfields, "", "SINGLE_PART")
        arcpy.PairwiseDissolve_analysis(datasource, fyd, disfields, "", "SINGLE_PART")
        return (datasrc + "d")

    except:
        print('Dissolve failure: ' + fyd)
        raise

# ----------------------------------------------------------------------------
#  Union fires from previous years
#  Note: this routine handles the naming of the layer names to union
# ----------------------------------------------------------------------------
def union_fires(current_year, previous_year, first_pass):
    try:
        if (first_pass):
            if (is_output_shapefile):
                shp_union = "sfy" + str(current_year) + "dd.shp"
            else:
                shp_union = "sfy" + str(current_year) + "dd"
        else:
            if (is_output_shapefile):
                shp_union = "fy" + str((previous_year)) + "u.shp;" + "sfy" + str(current_year) + "dd.shp"
            else:
                shp_union = "fy" + str((previous_year)) + "u;" + "sfy" + str(current_year) + "dd"

        fyu = "fy" + str(current_year) + "u"
        #print("Processing Union: " + shp_union)
        arcpy.Union_analysis(shp_union, fyu, "NO_FID", ".001 meter", "GAPS")
        return fyu

    except:
        print('Union failure: ' + fyu)
        raise

# ----------------------------------------------------------------------------
#   Multipart to Singlepart
# ----------------------------------------------------------------------------
def multi_to_single(datasrc, current_year):
    try:
        if (is_output_shapefile):
            final_layer = "fire" + str(current_year) + ".shp"
            datasource = datasrc + ".shp"
        else:
            final_layer = "fire" + str(current_year)
            datasource = datasrc

        if arcpy.Exists(final_layer):
            arcpy.Delete_management(final_layer)

        #print("Processing Multipart To Singlepart: " + final_layer)
            
        arcpy.MultipartToSinglepart_management(datasource, final_layer)
        return ("fire" + str(current_year))

    except:
        print('MultipartToSinglepart failure: ' + final_layer)
        raise

# ----------------------------------------------------------------------------
#   Delete Temporary Layers
# ----------------------------------------------------------------------------
def cleanup_temporary(years_processed):
    try:
        for proc_year in years_processed:
            print("Deleting temporary fire layers: " + str(proc_year))
            if (is_output_shapefile):
                fy = "fy" + str(proc_year) + ".shp"
                fyd = "fy" + str(proc_year) + "d.shp"
                fyu = "fy" + str(proc_year) + "u.shp"
                sfy = "sfy" + str(proc_year) + ".shp"
                sfyd = "sfy" + str(proc_year) + "d.shp"
                sfydd = "sfy" + str(proc_year) + "dd.shp"
                sfyu = "sfy" + str(proc_year) + "u.shp"
            else:
                fy = "fy" + str(proc_year)
                fyd = "fy" + str(proc_year) + "d"
                fyu = "fy" + str(proc_year) + "u"
                sfy = "sfy" + str(proc_year)
                sfyd = "sfy" + str(proc_year) + "d"
                sfydd = "sfy" + str(proc_year) + "dd"
                sfyu = "sfy" + str(proc_year) + "u"

            if arcpy.Exists(fy):
                arcpy.Delete_management(fy)
            if arcpy.Exists(fyd):
                arcpy.Delete_management(fyd)
            if arcpy.Exists(fyu):
                arcpy.Delete_management(fyu)
            if arcpy.Exists(sfy):
                arcpy.Delete_management(sfy)
            if arcpy.Exists(sfyd):
                arcpy.Delete_management(sfyd)
            if arcpy.Exists(sfydd):
                arcpy.Delete_management(sfydd)
            if arcpy.Exists(sfyu):
                arcpy.Delete_management(sfyu)
    except:
        print('Cleanup failure in year: ' + proc_year)
        raise

# ----------------------------------------------------------------------------
#  Calculate:
#    YLF - OLD NAME:  ylb - 'year of last burn'
#    TSLF - OLD NAME: yslb - 'years since last burn'
#    numFires - OLD NAME: nb - 'number of years burned'
#    currentFRI - OLD NAME: CFRI - 'current fire return interval'
# ----------------------------------------------------------------------------



def calculate_fields(datasrc, current_year, years_processed, backdate_year, yrsAgo):
    try:
        if (is_output_shapefile):
            datasource = datasrc + ".shp"
        else:
            datasource = datasrc

        print("Calculating new fire fields: " + datasrc)
        #fields = ["numFires", "numFires_1970","TSLF", "YLF", "firesLast40"]

        listFields = [field.name for field in arcpy.ListFields(datasource)]
        #['OBJECTID', 'Shape', 'nm1908', 'yr1908', 'ORIG_FID', 'Shape_Length', 'Shape_Area', 'YLF', 'TSLF',
        #'numFires', 'numFires_1970', 'firesLast40', 'LastFireName']

        with arcpy.da.UpdateCursor(datasource, listFields) as rows:
            for row in rows:
                ylb = 0 #year of last burn
                nb = 0 #number of burns
                #added 5/2020
                nb1970 = 0 #number of burns since 1970                
                #added 6/2019 
                num40 = 0 #- number of fires in last 40 years
                for proc_year in years_processed:
                    #get value of this year's year (i.e. 2016)
                    fld = "yr" + str(proc_year)                     
                    rowIndex = listFields.index(fld) #find this field's row index
                    #print( "rowIndex is " + str(rowIndex))                           
                    try:
                        val = row[rowIndex]
                        #print("val is " + str(val) + " for " + fld )                       
                    except:
                        print("Failed to get value of: " + fld)
                        raise

                    if (val != 0): #if value in yr2016 field is not 0
                        # if this is the last year to be processed
                        #if datasrc[-4:] == edyearInput:
                            
                        #if this row has a burn, and the year is greater than the year 40 yrs ago (i.e. 2008 >  1978),
                        #add it to the count of number of fires in lasts 40 years
                        if (val > yrsAgo):
                            num40 = num40 + 1
                        
                        #if that value is greater than year of last burn, make it the year of last burn
                        if (val > ylb):                            
                            ylb = val
                            #print("For year " + str(val) + " YLF is " + str(ylb))
                        #since this row has a burn (val != 0), add it to count for TOTAL number of burns for this poly
                        nb = nb + 1
                        #print("For year " + str(val) + " numFires is " + str(nb))

                        #if this row has a burn >= 1970, add it to the count for total number of burns since 1970
                        if (val >1969):
                            nb1970 = nb1970 + 1
                            #print( "For year " + str(val) + " numFires_1970 is " + str(nb1970))

                        #print("For year " + str(val) + " numFires is " + str(nb)
                        
                #fields = ["numFires", "numFires_1970","TSLF", "YLF",  "firesLast40"]
                #print("proc_year is " + str(proc_year))
                row[listFields.index("numFires")] = nb
                row[listFields.index("numFires_1970")] = nb1970
                row[listFields.index("TSLF")] = current_year - ylb #2012 - 2012 = 0
                row[listFields.index("YLF")] = ylb
                #print("YLF is " +  str(ylb))
##                row[listFields.index("currentFRI")] = (current_year - backdate_year)/(nb + 1)
##                print( "currentFRI is " + str(current_year) + "-" + str(backdate_year) + "/" + str(nb) + "+" + str(1))
##                if current_year > 1969:
##                    row[listFields.index("currentFRI_1970")] = (current_year - num_1970)/(nb1970 + 1)
##                else:
##                    row[listFields.index("currentFRI_1970")] = None                    
                row[listFields.index("firesLast40")] = num40
                rows.updateRow(row)

    except:
        print('Cursor Calculations failure: ' + datasrc)
        raise
# ----------------------------------------------------------------------------
# Populate labels
# ----------------------------------------------------------------------------
def populate_label(datasrc):
    try:
        if (is_output_shapefile):
            datasource = datasrc + ".shp"
        else:
            datasource = datasrc

        #print("Populating Label Field: " + datasrc)

        listFields = [field.name for field in arcpy.ListFields(datasource)]
        with arcpy.da.UpdateCursor(datasource, listFields) as rows:
            for row in rows:                
                year_val = row[listFields.index("YLF")]
                fld = "nm" + str(year_val)
                rowIndex = listFields.index(fld)
                #print("rowIndex for " + fld + " is " + str(rowIndex))
                name_val = str(row[rowIndex])
                #print( "name_val is " + name_val)
                fireIndex = listFields.index("LastFireName")
                row[fireIndex] = name_val
                rows.updateRow(row)


    except:
        print('Label populating failure: ' + datasrc)
        raise




#***********************************************
def elim (input_layer, out_layer, selection):
    print("Jumping to elim function")
    try:
        arcpy.MakeFeatureLayer_management(input_layer, "firelayer")                        
        # SelectLayerByAttribute to define features to be eliminated
        arcpy.SelectLayerByAttribute_management("firelayer", "NEW_SELECTION", selection)
        result = arcpy.GetCount_management("firelayer")
        intCountSel = int(result.getOutput(0))
        intSeqRounds = int(intCountSel/intFeaturesPerRound)

        if intCountSel: # if selection returns anything...
            print("Running eliminate on " + str(intCountSel) + " features in " + input_layer)
            if intCountSel > 15000:
                print("Running sequential eliminate in " + str(intSeqRounds) + " rounds.")
                fire.sequence_recur_elim(input_layer, out_layer, selection, intSeqRounds)
                
            else:
                print("Num features to eliminate less than 15,000, running in one round")
                arcpy.Eliminate_management("firelayer", out_layer, "LENGTH")
        else:
            print("No features to eliminate on " + input_layer)
    except:
        print("Error on eliminate for " + input_layer)
        raise


#####################################################################
    #END OF FUNCTIONS
#####################################################################

    
try:
    #Create workspaces 
    
    #Current year's workspace
    strPath = Workspace + "/FRID_" + str(num2 + 1) #N:\project\frid\workspace/FRID_2020  
    # make dir for GDB
    if not os.path.exists(strPath):
    # make if not found
           os.mkdir(strPath)

    
    # Create FIRE workspaces and gdb    
    strFireGDB = "Cal_FireProcessing.gdb" 
    strFireWorking = strPath + "/" + strFireGDB  #N:\project\frid\workspace/FRID_2016/Cal_FireProcessing.gdb
    strFinalFireW = strFireWorking + "/" + "WORKING/" #N:\project\frid\workspace/FRID_2016/Cal_FireProcessing.gdb/WORKING

    outFireRX = "RxBurns"
    outFireWild = "WildFire"
    outFireAll = "AllFires"

    strFieldRX = "RX"
    strFieldWild = "FIRE_LABEL"
    strFieldTmpYr = "temp_YEAR"

    strRxMerge = strFinalFireW + outFireRX
    strWFMerge = strFinalFireW + outFireWild
    strALLFire = strFinalFireW + outFireAll

    CalfireGDB = strPath + "/fire" + edyearInput[2:4] + "_1.gdb"
    firep = CalfireGDB + os.sep + "firep" + edyearInput[2:4] + "_1"

    
    #CHECK FOR EXISTENCE OF CURRENT FIRE GDB FROM CALFIRE

    if arcpy.Exists (CalfireGDB):
        print(CalfireGDB + " exists")
    else:
        raise Exception ("Calfire GDB does not exist")


    # Process: Create Fire File GDB...
    if not arcpy.Exists(strFireWorking): #N:\project\frid\workspace/FRID_2016/Cal_FireProcessing.gdb
        #print("\t" + "Making Fire Processing and Final Data GDB")
        arcpy.CreateFileGDB_management(strPath, strFireGDB)


    # Get Spatial Reference for feature dataset from firep<yr>_1
    prjInfo = firep
    sr = arcpy.CreateSpatialReference_management("#", prjInfo, "", "", "", "", "0")

    # Process: Create FeatureDatasets...
    if not arcpy.Exists(strFinalFireW): #N:\project\frid\workspace/FRID_2016/Cal_FireProcessing.gdb/WORKING/
        print("Making " + strFireWorking + " WORKING feature dataset")
        arcpy.CreateFeatureDataset_management(strFireWorking, "WORKING", sr)
            

    #Check for existence of preprocessed fire layer
    CalFires_Layer = strPath + "/" + "Cal_AllFires.shp" #N:\project\frid\workspace/FRID_2016/Cal_AllFires.shp
    if  arcpy.Exists(CalFires_Layer):
        print(CalFires_Layer + " exists")
    else:
        print(CalFires_Layer + " does NOT exist")

        #Set variables for FRAP's fire data
        arcpy.env.workspace  = strPath
        wksps = arcpy.ListWorkspaces("fire*", "FileGDB")
        for wksp in wksps:
            arcpy.env.workspace = wksp
            fcs = arcpy.ListFeatureClasses()
            for fc in fcs:
                if "firep" in fc:
                    strFirePIn = fc
                else:
                    strRXBurnIn = fc

        #attribute(s) being cleaned (semicolon separated string)
        
        attr = "FIRE_NAME"
        attr2 = "YEAR_"

        #********************************************************
        print("cleaning up " + attr + " and " + attr2 + "....")        
        rows = arcpy.UpdateCursor(wksp + "/" + strFirePIn,"","",attr)
        for row in rows:

            for field in attr.split(";"):
                row.setValue(field, cleanup(row.getValue(field)))            
            rows.updateRow(row)
        del row, rows

        
        rows = arcpy.UpdateCursor(wksp + "/" + strFirePIn,"","",attr2)
        for row in rows:

            for field in attr2.split(";"):
                row.setValue(field, cleanup(row.getValue(field)))            
            rows.updateRow(row)
        del row, rows

        
        attr3 = "TREATMENT_NAME"
        #********************************************************
        print("cleaning up " + attr3 + " and " + attr2 + "....")
        rows = arcpy.UpdateCursor(wksp + "/" + strRXBurnIn,"","",attr3)
        for row in rows:

            for field in attr3.split(";"):
                row.setValue(field, cleanup(row.getValue(field)))            
            rows.updateRow(row)
        del row, rows

        rows = arcpy.UpdateCursor(wksp + "/" + strRXBurnIn,"","",attr2)
        for row in rows:

            for field in attr2.split(";"):
                row.setValue(field, cleanup(row.getValue(field)))            
            rows.updateRow(row)
        del row, rows

        #********************************************************

        
        # Process: Feature Class to Feature Class...
        if not arcpy.Exists(strRxMerge): #N:\project\frid\workspace/FRID_2016/Cal_FireProcessing.gdb/WORKING/RxBurns
            print("\t\t" + "Copying " + strRXBurnIn + " to " + strRxMerge)
            arcpy.FeatureClassToFeatureClass_conversion(wksp + "/" + strRXBurnIn, strFinalFireW, outFireRX, "")
        if not arcpy.Exists(strWFMerge):#N:\project\frid\workspace/FRID_2016/Cal_FireProcessing.gdb/WORKING/Wildfire
            print("\t\t" + "Copying " + strFirePIn + " to " + strWFMerge)             
            arcpy.FeatureClassToFeatureClass_conversion(wksp + "/" + strFirePIn, strFinalFireW, outFireWild, "")
        
        # Process the Prescribed Burns........
        arcpy.env.workspace = strFinalFireW #N:\project\frid\workspace/FRID_2016/Cal_FireProcessing.gdb/WORKING/

        # Process: Add Field and Calc Field
        print("\t\t\t\t\t  Processing Prescribed Fire Layer......")
        print("\t\t\t\t\t\t Adding and populating fields \n\t ")
        arcpy.AddField_management(outFireRX, strFieldRX, "TEXT", "2", "", "", "", "NULLABLE", "NON_REQUIRED", "" )
        arcpy.CalculateField_management(outFireRX, strFieldRX, "1", "PYTHON", "")

        #6/2019 - MADE FIELD LENGTH 100 INSTEAD OF 50 TO ELIMINATE CALCULATION ERRORS
        arcpy.AddField_management(outFireRX, strFieldWild, "TEXT", "", "", "100", "", "NULLABLE", "NON_REQUIRED", "" )
        
        #arcpy.CalculateField_management(outFireRX, strFieldWild, "\"RX \" + [TREATMENT_NAME]", "VB", "")
        #6/2019 Changed to PYTHON and changed syntax to allow for 64bit processing
        arcpy.CalculateField_management(outFireRX, strFieldWild, '"RX " + !TREATMENT_NAME!', "PYTHON", "")


        #arcpy.MakeFeatureLayer_management(outFireRX, "outFireLayerRX", "\"YEAR_\" < '0'")
        arcpy.MakeFeatureLayer_management(outFireRX, "outFireLayerRX", "\"YEAR_\" IS NULL  or  \"YEAR_\" < '0'")
        arcpy.CalculateField_management("outFirelayerRX", "YEAR_", "99", "PYTHON")
        arcpy.SelectLayerByAttribute_management("outFirelayerRX", "CLEAR_SELECTION", "")

        # Process the Wildfires........
        print("\t\t\t\t\t\t  Processing WildFire Layer...........")
        print("\t\t\t\t\t\t\t Adding and populating fields \n\t ")
        arcpy.MakeFeatureLayer_management(outFireWild, "WFLayer")
        arcpy.AddField_management("WFLayer", "temp_YEAR", "TEXT", "", "", "4", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management("WFLayer", "temp_YEAR", "!YEAR_!", "PYTHON", "")
        arcpy.SelectLayerByAttribute_management("WFLayer", "NEW_SELECTION", "\"temp_YEAR\" IS NULL OR \"temp_YEAR\"=''")
        arcpy.CalculateField_management("WFLayer", "temp_YEAR", "!YEAR_!", "PYTHON", "")
        #arcpy.CalculateField_management("WFLayer", "YEAR_", "\"99\"", "PYTHON", "")
        arcpy.SelectLayerByAttribute_management("WFLayer", "CLEAR_SELECTION", "")
        arcpy.AddField_management("WFLayer", "FIRE_LABEL", "TEXT", "", "", "100", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management("WFLayer", "FIRE_LABEL", "!FIRE_NAME!", "PYTHON", "")
        arcpy.SelectLayerByAttribute_management("WFLayer", "NEW_SELECTION", "\"FIRE_LABEL\" =''")
        arcpy.CalculateField_management("WFLayer", "FIRE_LABEL", "\"UNNAMED FIRE\"", "PYTHON", "")
        arcpy.SelectLayerByAttribute_management("WFLayer", "CLEAR_SELECTION", "")
        arcpy.DeleteField_management("WFLayer", "temp_YEAR")

        #Merge Rx and WildFires together
        print("Merging Rx and WildFires Data into a single FeatureClass......")
        # Process: Merge...
        arcpy.Merge_management(strRxMerge + ";" + strWFMerge, strFinalFireW + "/Cal_AllFires")
        arcpy.FeatureClassToShapefile_conversion(strFinalFireW + "Cal_AllFires", strPath)




    ######################################################################
        
    # "Flatten out" fires

    input_fire_data = CalFires_Layer 


    # Set Minimum and Maximum Years to process
    minimum_year =  num
    maximum_year =  num2 + 1


    ### if Geodatabase, set this value to 0, otherwise 1
    is_input_shapefile = 0
    is_output_shapefile = 0


    # Reinitialize every how many years:
    gpreinit = 25

    # the way this works, it does not process the maximum year selected, so we add
    # a year to the user-selected maximum

    # These variables allow for start in the middle of the processing period   
    # provided you have the previous year's union file fyYYYYu.shp
    # 0 = start from beginning, 1 = start at continue_year
    start_midway = 0  # <-----------------------------------CHANGE HERE IF NECESSARY -----------------------------!!!!!!!!!!!!!!
    continue_year = 2008

    # this should be the first year you processed in the original run, before it crashed
    if (start_midway):
        backdate_year = 1908
    else:
        backdate_year = minimum_year

   
    # ****************************************************************************
    #   Main - Start program
    # ****************************************************************************

    #Check for existence of final unioned fire layer (fire2018)        
    if not arcpy.Exists(strFinalFireW + "fire" +  str(edyearInput)):  
        print(strFinalFireW + "fire" +  str(edyearInput) + " does not Exist, processing fires...")

        #Search for input minimum year existence in Cal_Allfires.shp
        existsList = []
        with arcpy.da.SearchCursor(input_fire_data, "Year_" ) as cur:
            for row in cur:
                existsList.append(row[0])
        if styearInput in existsList:
            print(styearInput + " exists")
        else:
            print(styearInput + " does not exist in " + input_fire_data + "....needs to be added manually...stopping")
            sys.exit()

        
        print("Starting fire section...")
        print("starting at " + strftime('%a, %d %b %Y %H:%M:%S %Z', timeStart))

        
        fl_fires = setup_environment()
        min_year = get_min_year(input_fire_data)
        #min_year = minimum_year
        print("min_year is " + str(min_year))

        #max_year = get_max_year(input_fire_data)
        max_year = maximum_year
        print("max_year is " + str(max_year))
        prev_year = min_year - 1
        years_processed = []

        # allow to start in the middle of a predefined range if processing already completed
        # this fills the "years_processed" array with all previous year values and sets the
        # prev_year variable to correct value
        if (start_midway):  #if "start_midway = 1 or true"
            for cur_year in range(min_year, continue_year):
                if is_fire_year(input_fire_data, cur_year):
                    years_processed.append(cur_year)
                    prev_year = cur_year
            min_year = continue_year
            print("min_year is changed to " + str(min_year))


    # Main Fire Year Loop

        for cur_year in range(min_year, max_year):            

            # Only process years where there have been fires
            if is_fire_year(input_fire_data, cur_year):
                print("** Processing Year: " + str(cur_year) + " with union, dissolves, repair & calculates **")
                years_processed.append(cur_year)

                # Select and Export current year fire perims
                # sfy is the single year file
                sfy = get_temp_fire_year(fl_fires, cur_year)
                print("finished export: " + sfy)

                # Union current year fire perims alone
                # union it to itself to double the overlaps within a year
                sfyu = union_single(sfy, cur_year)
                print("finished one year union" + str(cur_year))

                # Create new field: FIRE_AREA
                add_field(sfyu, "FIRE_AREA", "double")

                # Calculate FIRE_AREA
                calc_shape_area(sfyu)
                print("finished calculate shape_area" + str(cur_year))

                # Dissolve by FIRE_AREA
                # this gets rid of the overlapping polygons within a year, we save the last fire name only
                sfyd = dissolve_single(sfyu, cur_year)
                print("finished first dissolve (on shape area) to eliminate overlapping polygons in a single year: " + str(cur_year))

                # Add current year fire name field
                nm_fld = "nm" + str(cur_year)
                add_field(sfyd, nm_fld, "text")
                print("name field added for " + sfyd)

                # Fill fire name field
                fill_field(sfyd, nm_fld,"!LAST_FIRE_LABEL!", "PYTHON")
                print("name field filled for " + sfyd)

                # Dissolve by nm_fld
                dfield = nm_fld
                #print("dissolving by: " + dfield)
                fyd = dissolve_layer(sfyd, dfield)
                print("finished second dissolve: " + fyd)

                # Add year field
                yr_fld = "yr" + str(cur_year)
                add_field(fyd, yr_fld, "short")
                print("year field added for " + fyd)

                # Fill year field
                fill_field(fyd, yr_fld, cur_year, "PYTHON")
                print("year field filled for " + fyd)

                # Repair Geometry
                repair_geometry(fyd)
                print("finished repair geometry: " + fyd)

                # Union with previous year
                if (prev_year < minimum_year):
                    fyu = union_fires(cur_year, prev_year, 1)
                else:
                    fyu = union_fires(cur_year, prev_year, 0)
                print("finished union of current year and previous years: " + fyu)

                # Multipart to Singlepart
                fire_year_layer = multi_to_single(fyu, cur_year)
                #print("finished multipart to singlepart: " + str(fire_year_layer))
                    
                # AddFields
                add_field(fire_year_layer, "YLF", "SHORT")# year of last burn
                add_field(fire_year_layer, "TSLF", "SHORT") # years since last burn
                add_field(fire_year_layer, "numFires", "SHORT")
                add_field(fire_year_layer, "numFires_1970", "SHORT")
                #add_field(fire_year_layer, "currentFRI", "float")
                #add_field(fire_year_layer, "currentFRI_1970", "float")
                add_field(fire_year_layer, "firesLast40", "SHORT")
                print("added a bunch of fields: " + str(fire_year_layer))

                # calculate ylb (yr last burn), yslb (yrs since last burn), nb(number of burns), CFRI (current FRI)
                # if fire layer is latest (i.e. fire2018), calculate number of fires in last 40 years
                calculate_fields(fire_year_layer, cur_year, years_processed, backdate_year, yrsAgo)
                print("calculated YLF, TSLF, numFires, numFires_1970, firesLast40: " + str(fire_year_layer))

                # Add a label field and populate with the most recent fire name
                add_field(fire_year_layer, "LastFireName", "TEXT")
                # print( "label field added to " + str(fire_year_layer))
                populate_label(fire_year_layer)
                # print( "populated label field: " + str(fire_year_layer))

                print("finished processing " + str(cur_year))

                prev_year = cur_year
                
        cleanup_temporary(years_processed)
        print("Main() completed without exception")
            

        num2 = edyearInput
        final_layer = "fire" +  str(edyearInput)
        print("Fire processing has been completed")

    else:
        print(strFinalFireW + "fire" +  str(edyearInput) + " exists")



        
#####################################################################
    ### Eliminate slivers

    
    strEQuery = "Shape_Area <500"
    intFeaturesPerRound = 15000
    scratchPth = r"N:\users\carol_clark\Scratch\Scratch.gdb" 

    fireIn = strFinalFireW + "fire" +  str(edyearInput)
    fireElim = strFinalFireW + "fire" +  str(edyearInput) + "Elim"

    if not arcpy.Exists (fireElim):
        print("running eliminates")
        elim(fireIn, fireElim, strEQuery)
    else:
        print(fireElim + " exists")

    if not arcpy.Exists (fireElim + "Exp"):
        print("Exploding " + fireElim)
        arcpy.MultipartToSinglepart_management (fireElim, fireElim + "Exp")
        arcpy.RepairGeometry_management (fireElim + "Exp")
    else:
        print(fireElim + "Exp + exists")
        
#####################################################################
    ### f on final fields

    strFCdiss = "fire" +  str(edyearInput) + "ElimFin"
    strPathFCdiss = strFinalFireW + strFCdiss #N:\project\frid\workspace/FRID_2016/Cal_FireProcessing.gdb/WORKING/fire2018ElimFin
    print("final output is " + strPathFCdiss)

    #lstLegFields = ['YLF','TSLF','numFires', 'numFires_1970','currentFRI', 'currentFRI_1970','LastFireName','firesLast40']
    lstLegFields = ['YLF','TSLF','numFires', 'numFires_1970','LastFireName','firesLast40']
    if not arcpy.Exists(strPathFCdiss):
        print("final dissolve....")
        #arcpy.Dissolve_management(fireElim + "Exp",strPathFCdiss,lstLegFields, "", "MULTI_PART")
        arcpy.PairwiseDissolve_analysis(fireElim + "Exp",strPathFCdiss,lstLegFields, "", "MULTI_PART")
        

    else:
        print(strPathFCdiss + " is complete")

    print("FRID processing complete! See final layer:  " + strPathFCdiss)

    timeEnd = localtime()
    print('______________________________________________________________________')
    print('process started at: '+ strftime('%a, %d %b %Y %H:%M:%S %Z', timeStart))
    print('process ended at: '+ strftime('%a, %d %b %Y %H:%M:%S %Z', timeEnd))

    


except:  # General non GP errors
    exc_type, exc_value, exc_traceback = sys.exc_info()
    strTrace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(strTrace)



