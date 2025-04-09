#    this version for script tools using arcpy geoprocessor object

import arcpy, os, traceback, sys, string, time
from arcpy import env

def getForestID(For):
    dictForest = {'Angeles':['01','ANF'],
                  'Cleveland':['02','CNF'],
                  'Eldorado':['03','ENF'],
                  'Inyo':['04','INF'],
                  'Klamath':['05','KNF'],
                  'Lassen':['06','LNF'],
                  'Six Rivers':['10','SRF'],
                  'Modoc':['09','MDF'],
                  'Mendocino':['08','MNF'],
                  'Plumas':['11','PNF'],
                  'San Bernardino':['12','BDF'],
                  'Los Padres':['07','LPF'],
                  'Lake Tahoe Basin':['19','TMU'],
                  'Tahoe':['17','TNF'],
                  'Sequoia':['13','SQF'],
                  'Shasta Trinity':['14','SHF'],
                  'Sierra':['15','SNF'],
                  'Stanislaus':['16','STF'],
                  'North Coast':['NCoast','NCoast'],
                  'North Interior':['NInterior','NInterior'],
                  'North East':['NEast','NEast'],
                  'North Sierran West':['NSierranWest','NSierranWest'],
                  'North Sierran':['NSierran','NSierran'],
                  'South Sierran':['SSierran','SSierran'],
                  'South Sierran West':['SSierranWest','SSierranWest'],
                  'South Sierran West 1':['SSierranWest1','SSierranWest1'],
                  'South Sierran West 2':['SSierranWest2','SSierranWest2'],                  
                  'South Sierran East':['SSierranEast','SSierranEast'],
                  'Central Valley':['CValley','CValley'],
                  'Central Coast':['CCoast','CCoast'],
                  'South Coast':['SCoast','SCoast'],
                  'South Coast West':['SCoast_West','SCoast_West'],
                  'South Coast East':['SCoast_East','SCoast_East'],
                  'South Coast North':['SCoast_North','SCoast_North'],
                  'South Interior':['SInterior','SInterior'],
                  'Great Basin':['GBasin','GBasin'],
                  'Sequoia Kings Canyon':['SEKI','SEKI'],
                  'Yosemite':['Yosemite','Yosemite'],
                  'Tile 38':['Tile38','Tile38'],
                  'Misc':['Misc','Misc'],
                  'Toiyabe':['21','TOI'],}
    return dictForest[For]

def getZoneID(zone):
    dictZone = {'North Coast':['1','NCstZone'],
                  'North Interior':['2','NIntZone'],
                  'North Sierra':['3','NSierZone'],
                  'South Sierra':['4','SSierZone'],
                  'Central Valley':['5','CValZone'],
                  'Central Coast':['6','CCstZone'],
                  'South Coast':['7','SCstZone'],
                  'South Interior':['8','SIntZone'],
                  'Great Basin':['9','GBasZone'],}

    return dictZone[zone]



def formatPath(input_string):
    """ function to correct backslash issue in paths """
    
    lstReplace = [["\a","/a"],
                  ["\b","/b"],
                  ["\f","/f"],
                  ["\n","/n"],
                  ["\r","/r"],
                  ["\t","/t"],
                  ["\v","/v"],
                  ["\\","/"]]

    # replce each type of escape
    for old, new in lstReplace:
        input_string = input_string.replace(old, new)

    return input_string

def splitPath(strPathFC):
    """ function to separate path and FC variables and determine GDB vs. MDB
        usage:
            isFileGDB, strFC, strFCPath, strTPath = RSL_util.splitPath(strPathFC)
        where:
            isFileGDB = 1 or 0 int,
            strFC =  feature class name,
            strFCPath = feature class worskpace,
            strTPath = workspace for tables = strFCPath w/o feature dataset"""

    try:
        if ".gdb" in strPathFC:
            isFileGDB = True
            intind = strPathFC.index(".gdb")
        elif ".mdb" in strPathFC:
            isFileGDB = False
            intind = strPathFC.index(".mdb")
        else:
            return "", "", "", ""
        
        # set path and fc name
        strFC = strPathFC[intind + 5:]
        strFCPath = strPathFC[:intind + 4]
        strTPath = strPathFC[:intind + 4]
        # if fc in in feature dataset, then account for
        intind2 = strFC.find("/")
        if intind2 != -1:
            strFCPath = strFCPath + "/" + strFC[:intind2]
            strFC = strFC[intind2 + 1:]
            
        return isFileGDB, strFC, strFCPath, strTPath
    
    except:
        raise Exception ("SplitPathError" + str(sys.exc_type)+ ": " + str(sys.exc_value))

def elapsed_time(t0):
    """ funcion to return a string of format 'hh:mm:ss', representing time elapsed between t0 and funcion call, rounded to nearest second"""
    from time import time
    from string import zfill
    seconds = int(round(time() - t0))
    h,rsecs = divmod(seconds,3600)
    m,s = divmod(rsecs,60)
    return zfill(h, 2) + ":" + zfill(m, 2) + ":" + zfill(s, 2)
    


def recur_elim(strPathFC, strPathOutFC, strEQuery):
    print("Jumping to recur_elim function")
    """ function to recursively eliminate a feature class until all possible selected features have been removed
    """
    try:
        strPathFC = formatPath(strPathFC)
        strPathOutFC = formatPath(strPathOutFC)
        isFileGDB, strInFC, strPath, strTPath = splitPath(strPathFC)
        isFileGDB, strOutFC, strPath, strTPath = splitPath(strPathOutFC)
        
        arcpy.env.workspace = strPath

        booloverwite = arcpy.env.overwriteOutput
        arcpy.env.overwriteOutput = True
        print("Eliminating " + strEQuery + " in " + strInFC)
        
        lstfcs = []
        lstfcs.append(strInFC)
        i = 0
        result = arcpy.GetCount_management(strInFC)
        intCount1 = int(result.getOutput(0))
        intCount2 = 0

            
        # while there are still polys that may be eliminated...
        while intCount2 < intCount1:
            i += 1
            arcpy.MakeFeatureLayer_management (lstfcs[-1],"e_layer",)
            arcpy.SelectLayerByAttribute_management ("e_layer", "NEW_SELECTION", strEQuery)
            result = arcpy.GetCount_management("e_layer")
            intCountSel = int(result.getOutput(0))
            if intCountSel: # if selection returns anything...
                print("\telim " + str(i) + ":")
                print("\t\t" + str(intCountSel) + " records selected")
                # append output name to list
                lstfcs.append(strInFC + "_e" + str(i))
                # and elim
                arcpy.Eliminate_management("e_layer", lstfcs[-1], "LENGTH")
                #print("Repairing geometry on " + lstfcs[-1] + "...")
                #arcpy.RepairGeometry_management(lstfcs[-1])
                # reset counts for loop
                result = arcpy.GetCount_management(lstfcs[-2])
                intCount1 = int(result.getOutput(0))
                result = arcpy.GetCount_management(lstfcs[-1])
                intCount2 = int(result.getOutput(0)) 
                print("\t\t" + str(intCount1-intCount2) + " segs removed")
                print("\t\t" + str(intCount2) + " segs remain\n")
            else:
                break

        # if no features were selected to begin with then raise error or set boolean
        if len(lstfcs) == 1:
            print("No features to be eliminated")
            return 0

        else:
            if intCountSel:
                print("Whole selection cannot be eliminated")
            else:
                print("Whole selection eliminated successfully")
            for fc in lstfcs[1:-1]:
                # delete intermediates
                print("Deleting " + fc)
                arcpy.Delete_management(fc)

            # rename to final FC and set boolean
            print("lstfcs[-1] is " + lstfcs[-1])
            print("strOutFC is " + strOutFC)
            arcpy.Rename_management(lstfcs[-1],strOutFC)
            return 1

        arcpy.env.overwriteOutput = booloverwite

    except:
        raise

def resel_recur_elim(strPathInFC, strElimFCex, strEQuery):
    print("Jumping to resel_recur_elim function")
    # function to preemptively reselect only those adjacent features that
    # are possible eliminate targets   
    try:
        strPathInFC = formatPath(strPathInFC)
        strElimFCex = formatPath(strElimFCex)
        isFileGDB, strInFC, strPath, strTPath = splitPath(strPathInFC)
        isOFileGDB, strOutFC, strOPath, strOTPath = splitPath(strElimFCex)
        strReselFC = strPath + "/tempReselFC"
        strElimFC = strPath + "/tempElimFC"
        strPathOutFC = strPath + "/tempUpdate"
        
##        booloverwite = arcpy.env.overwriteOutput
##        arcpy.env.overwriteOutput = True
        #-------------------------------------------------
        #Debugging
        print("strPathInFC is " + repr(strPathInFC))
        print("strPathOutFC is " + repr(strPathOutFC))
        print("strElimFCex is " + repr(strElimFCex))
        print("strReselFC is " + repr(strReselFC))
        print("strElimFC is " + repr(strElimFC))
        #-------------------------------------------------
        
        print("Eliminating: " + strPathInFC + "\n\t   to: " + strElimFCex)
        arcpy.MakeFeatureLayer_management (strPathInFC,"mmulayer",strEQuery)
        arcpy.MakeFeatureLayer_management (strPathInFC, "searchlayer")
        print("Selecting features adjacent to selection set")
        arcpy.SelectLayerByLocation_management("searchlayer", "INTERSECT", "mmulayer")
        
        print("Reselecting adjacent features to create: " + strReselFC)
        arcpy.CopyFeatures_management("searchlayer", strReselFC)
        print("Eliminating features to create: " + strElimFC)
        recur_elim(strReselFC, strElimFC, strEQuery)

        print("Updating eliminated features to create: " + strPathOutFC)
        arcpy.Update_analysis(strPathInFC, strElimFC, strPathOutFC)
        print("Exploding " + strPathOutFC + " to " + strElimFCex)
        arcpy.MultipartToSinglepart_management(strPathOutFC, strElimFCex)

        #arcpy.env.overwriteOutput = booloverwite
                
        print("Deleting intermediate features: " + strPathOutFC)
        arcpy.Delete_management(strPathOutFC)        
        print("Deleting intermediate features: " + strReselFC)
        arcpy.Delete_management(strReselFC)
        print("Deleting intermediate features: " + strElimFC)
        arcpy.Delete_management(strElimFC)
        
    except:
        raise




#***********************************************
def elim (input_layer, out_layer, selection):
    print("Jumping to elim function")
    try:
        arcpy.MakeFeatureLayer_management(input_layer, "vegfirelayer")                        
        # SelectLayerByAttribute to define features to be eliminated
        arcpy.SelectLayerByAttribute_management("vegfirelayer", "NEW_SELECTION", selection)
        result = arcpy.GetCount_management("vegfirelayer")
        intCountSel = int(result.getOutput(0))
        intSeqRounds = intCountSel/intFeaturesPerRound 

        if intCountSel: # if selection returns anything...
            print("Running eliminate on " + str(intCountSel) + " features in " + input_layer)
            if intCountSel > 100000:
                print("Running sequential eliminate in " + str(intSeqRounds) + " rounds.")
                sequence_recur_elim(input_layer, out_layer, selection, intSeqRounds)
                
            else:
                print("Num features to eliminate less than 100,000, running in one round")
                arcpy.Eliminate_management("vegfirelayer", out_layer, "LENGTH")
        else:
            print("No features to eliminate on " + input_layer)
    except:
        print("Error on eliminate for " + input_layer)
        raise
#***********************************************


def sequence_recur_elim(strPathFC, strPathOutFC, strEQuery, introunds):
    print("Jumping to sequence_recur_elim function")
    """ function to sequentially increase area of features to be eliminated in order to improve stability
        
    """

    try:
        strPathFC = formatPath(strPathFC)
        strPathOutFC = formatPath(strPathOutFC)
        isFileGDB, strInFC, strPath, strTPath = splitPath(strPathFC)
        isOFileGDB, strOutFC, strOPath, strOTPath = splitPath(strPathOutFC)
        print(arcpy.GetCount_management(strPathFC).getOutput(0)) 
        print( "making area list")
        arcpy.MakeFeatureLayer_management(strPathFC, "layer", strEQuery)
        #print( "here")
        
        #Account for no features in Query
        if arcpy.GetCount_management("layer").getOutput(0) == "0":
            print( "No features to eliminate, renaming layer to output...")
            arcpy.Rename_management(strPathFC,strPathOutFC)
            
        else:
            rows = arcpy.SearchCursor("layer")
            row = rows.next()            
            lstAreas = []
            i=0
            while row:
                #val = int(float(row.Shape_Area))
                val = float(row.Shape_Area)
                lstAreas.append(val)
                row = rows.next()
                
            intcount = len(lstAreas)
            lstAreas.sort()
            print(str(intcount))
            
            strPathSeqInFC = strPathFC
                
            for i in range(1,introunds):
                print ("i is " + str(i))
                strPathSeqOutFC = strPath + "/tempElimSeq_" + str(i)
                intIndex = int(intcount * i / introunds)
                print ("intIndex is " + str(intIndex))
                fltArea = lstAreas[intIndex]
                strEQuerySub = '"Shape_Area" < ' + str(fltArea)
                print("---------------------------------------------------")
                print("round " + str(i) + ": eliminating " + strEQuerySub)
                #print( "round " + str(i) + ": eliminating " + strEQuerySub)
                resel_recur_elim(strPathSeqInFC, strPathSeqOutFC, strEQuerySub)
                if strPathSeqInFC != strPathFC:
                    print("deleting: " + strPathSeqInFC)
                    arcpy.Delete_management(strPathSeqInFC)
                strPathSeqInFC = strPathSeqOutFC
                
            print("---------------------------------------------------")
            print("final round: eliminating " + strEQuery)
            #print( "final round: eliminating " + strEQuerySub)
            resel_recur_elim(strPathSeqInFC, strPathOutFC, strEQuery)
                          
            if strPathSeqInFC != strPathFC:
                print("deleting: " + strPathSeqInFC)
                arcpy.Delete_management(strPathSeqInFC)
    except:
        raise


                  
try:
    
    BoolDebugging = False
    if BoolDebugging:
        import sys, traceback
##        import arcgisscripting as arc
##        gp = arc.create()

        strPathFC = arcpy.GetParameterAsText(0)
        strPathOutFC = arcpy.GetParameterAsText(1)
        strEQuery = arcpy.GetParameterAsText(2)
        introunds = int(arcpy.GetParameterAsText(3))
        
        sequence_recur_elim(strPathFC, strPathOutFC, strEQuery, introunds)
        
except:
    # get the traceback object
    tb = sys.exc_info()[2]
    # tbinfo contains the line number that the code failed on and the code from that line
    tbinfo = traceback.format_tb(tb)[0]
    # concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERROR Traceback Info:\n  " + tbinfo + "\n    " + str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
    # generate a message string for any geoprocessing tool errors
    msgs = "GP ERRORS:\n\t" + arcpy.GetMessages(2) + "\n"
    # return arcpy messages for use with a script tool
    arcpy.AddError(msgs)
    arcpy.AddError(pymsg)
