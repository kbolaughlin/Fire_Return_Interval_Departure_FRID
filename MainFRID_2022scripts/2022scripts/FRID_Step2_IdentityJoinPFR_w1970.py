# FRID_Step2_IdentityJoinPFR_w1970.py
###Manual Changes Required: 3
###dictZone below can be modified to key vegPth & zone together
###Also should be possible to have year pull from time
# christopherfontenot, 6/13/2022 module copied to FRID directory
# cclark, 4/2021 - Updated FRID (Fire Return Interval Departure) script for Python 3.x
# Runs Identity of Eveg with processed fire layer from first script (..\FRID_2016\Cal_FireProcessing.gdb\WORKING\fire<year>Fin)
# Then runs Eliminate, adds blank PFR fields (PFR;meanRefFRI;minRefFRI;maxRefFRI;medianRefFRI;fireRegimeGrp),
# populates using xwalk table (...frid\workspace\A_FRID_FinalTemplate.gdb\CALVEG_2_FRID)
# Dissolves final layer and calculates -999s for PFR = 'none'
# 5/2020, cclark - added field for 1970 calculations in last step
# 5/2020; per Hugh Safford, all Eveg inputs should be from the same base year - see layers:  N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb
# up until this change, each year was run with the current Eveg

# Import system modules
import sys, string, os, traceback, time, arcpy
### Changed from sys.path.append(r"N:\code\carol_clark\python\modules")
sys.path.append(r"N:\project\frid\modules")
import fire_interval_v2
from time import *

##def message(string):
##    print string
##    arcpy.AddMessage(string)

    
strEQuery = "\"shape_area\" <= 1000" # and \"COVERTYPE\" <> 'WAT'"
intFeaturesPerRound = 200000

#Main Workspace i.e. N:\project\frid\workspace\FRID_<year>"
Workspace = r"D:\frid\workspace\FRID_2022" #<---------------change to this year i.e. if processing fires from 2020, this year will be 2021
print("Main workspace is " + Workspace)
scratchPth = Workspace + "/Scratch" 
if not os.path.exists(scratchPth):
    os.makedirs(scratchPth)
arcpy.ScratchWorkspace = scratchPth

#Cleaned up EVEG layer
#<------choose from list below
## vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\NorthCoastWestEvegForFRID_11"
## vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\NorthCoastEast_EvegForFRID_11"
## vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\NorthCoastMid_EvegForFRID_11"
## vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\NorthInteriorEvegForFRID_11"
## vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\NorthSierraEvegForFRID_11"
## vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\SouthSierraEvegForFRID_11"
## vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\CentralValleyEvegForFRID_11"
## vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\CenCoastClipEvegForFRID_11" 
## vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\SouthCoastEvegForFRID_11"
## vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\SouthInteriorEvegForFRID_11"
vegPth = r"N:\project\frid\workspace\BaseEvegForAllYears\FRID_BaseEveg.gdb\GreatBasinEvegForFRID_11"

veg = os.path.basename(vegPth)
print("veg is "+ vegPth)

#User choice of zone 
zone = "Great Basin" #<--------------------------paste in AOI from dictionary here
print("Working on " + zone + " zone")
dictZone = {'North Coast West':'NCstWest',
    'North Coast East':'NCstEast',
    'North Coast Mid':'NCstMid',
    'North Interior':'NInt',
    'North Sierran':'NSie',
    'South Sierran':'SSie',
    'Central Valley':'CVal',
    'Central Coast':'CCst',
    'South Coast':'SCst',
    'South Interior':'SInt',
    'Great Basin':'GBas'}    

#Set prefix for data and Calveg zone number
AOI = dictZone[zone]
print("AOI is " + AOI)

#Set area for output frid data
workGDB = AOI + "FRID" #NcstWestFRID
workGDBpath = Workspace + "/" + workGDB + ".gdb" #.../FRID_2013/NcstWestFRID.gdb
print("workGDBpath is " + workGDBpath)

#Statewide processed fire polygon input
firePth = Workspace + os.sep + "Cal_FireProcessing.gdb/WORKING" + os.sep + "fire" + str(int(Workspace[-4:]) - 1) + "ElimFin" #N:\project\frid\workspace\FRID_2019\Cal_FireProcessing.gdb\WORKING
print("fire layer is "+ firePth)
fire = os.path.basename(firePth)  #fire2018ElimFin

outVegFire = AOI + "VegFireIden"
outVegFirePth = workGDBpath + "/" + outVegFire #.../FRID_2013/NSieFRID.gdb/NSieVegFireIden
outVegFireS = AOI + "VegFireIdenEx"
outVegFirePthS = workGDBpath + "/" + outVegFireS #.../FRID_2013/NSieFRID.gdb/NSieVegFireIdenEx
outVegFireE = AOI + "VegFireIdenExElim"
outVegFirePthE = workGDBpath + "/" + outVegFireE #.../FRID_2013/NSieFRID.gdb/NSieVegFireIdenExElim
outVegFireD = AOI + "VegFireIdenElDiss_FIN"
outVegFirePthD = workGDBpath + "/" + outVegFireD

#Join table containing PFR attributes
CALVEG_2_FRID = r"N:\project\frid\workspace\A_FRID_FinalTemplate.gdb\CALVEG_2_FRID"
print("PFR join table is " + CALVEG_2_FRID)
                  
timeStart = localtime()
print('process started at: '+ strftime('%a, %d %b %Y %H:%M:%S %Z', timeStart))

try:   

    #******************************************
    #Calculate nulls to -999
    def calculate_nones(input_layer):
        try:
            row, cur2 = None, None
            arcpy.MakeFeatureLayer_management(input_layer, "layer1")
            print("Calculating -999s for RefFRI, PFRID, NPS fields...")
            cur2 = arcpy.UpdateCursor ("layer1", selection2)            
            for row in cur2:
                row.meanRefFRI = -999
                row.minRefFRI = -999
                row.maxRefFRI = -999
                row.medianRefFRI = -999  
                row.fireRegimeGrp = "-999"
                cur2.updateRow(row)
            del row, cur2
        except:
            print("Error in calculating -999s for " + input_layer)
            raise
    #***********************************************

    #***********************************************
    #Calculate year of last fire 0's to -999
    def calculate_YLF (input_layer):
        try:
            row4, cur4 = None, None
            arcpy.MakeFeatureLayer_management(input_layer, "layer2")
            print("Calculating -999s for YLF")
            cur4 = arcpy.UpdateCursor ("layer2", selection3)
            for row4 in cur4:
                row4.YLF = -999
                cur4.updateRow(row4)
            del row4, cur4
        except:
            print("Error in calculating YLFs to -999 for " + input_layer)
            raise
    #***********************************************

    #***********************************************
    #Dissolve final layer
    def dissolve_layer(input_layer, output):  
        try:
            #Dissolve layer to prep for FRID calculator
            dissolve_fields = ["SAF_COVER_TYPE","SRM_COVER_TYPE",\
            "REGIONAL_DOMINANCE_TYPE_1","OS_TREE_DIAMETER_CLASS_1","REGIONAL_DOMINANCE_TYPE_2",\
            "OS_TREE_DIAMETER_CLASS_2","REGIONAL_DOMINANCE_TYPE_3", "COVERTYPE","CON_CFA","HDW_CFA","SHB_CFA","TOTAL_TREE_CFA",\
            "WHRLIFEFORM","WHRTYPE","WHRSIZE","WHRDENSITY","YLF","TSLF","numFires","numFires_1970",\
            "LastFireName","firesLast40","PFR","meanRefFRI","minRefFRI","maxRefFRI","medianRefFRI","fireRegimeGrp"]
            print("Dissolving " + input_layer + "...")
            arcpy.PairwiseDissolve_analysis(input_layer,output, dissolve_fields,"#","MULTI_PART")
        except:
            print("Error Dissolve " + output)
            raise
        
    #***********************************************
        
    #***********************************************
    def elim (input_layer, out_layer, selection):
        try:
            arcpy.MakeFeatureLayer_management(input_layer, "vegfirelayer")                        
            # SelectLayerByAttribute to define features to be eliminated
            arcpy.SelectLayerByAttribute_management("vegfirelayer", "NEW_SELECTION", selection)
            result = arcpy.GetCount_management("vegfirelayer")
            intCountSel = int(result.getOutput(0))
            intSeqRounds = int(intCountSel/intFeaturesPerRound)

            if intCountSel: # if selection returns anything...
                print("Running eliminate on " + str(intCountSel) + " features in " + input_layer)
                if intCountSel > 100000:
                    print("Running sequential eliminate in " + str(intSeqRounds) + " rounds.")
                    fire_interval_v2.sequence_recur_elim(input_layer, out_layer, selection, intSeqRounds)
                    
                else:
                    print("Num features to eliminate less than 100,000, running in one round")
                arcpy.Eliminate_management("vegfirelayer", out_layer, "LENGTH")
            else:
                print("No features to eliminate on " + input_layer)
        except:
            print("Error on eliminate for " + input_layer)
            raise
      #***********************************************

        
      
    #Set up workspace for output ***********************************************
    if not arcpy.Exists(workGDBpath): #.../FRID_2013/NSieFRID.gdb
        print("Creating veg workspace")
        arcpy.CreateFileGDB_management (Workspace, workGDB) #.../FRID_2013 + NSieFRID.gdb
    else:
        print(workGDB + " workspace exists")

    # Check out Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

  
    

    #Identity, Explode, Eliminate***************************
    
    #If Eliminated layer does not exist
    if not arcpy.Exists(outVegFirePthE):
        
        #If Singlepart does not exist  
        if not arcpy.Exists(outVegFirePthS):

            #If Identity does not exist
            if not arcpy.Exists(outVegFirePth):  
                print("Identitying " + veg + " and " + fire + " ....") 
                arcpy.Identity_analysis(vegPth,firePth,outVegFirePth) 
                arcpy.MultipartToSinglepart_management (outVegFirePth, outVegFirePthS)
                elim(outVegFirePthS, outVegFirePthE,strEQuery)
            else:
                print(outVegFire + " exists, exploding and running eliminate")
                arcpy.MultipartToSinglepart_management (outVegFirePth, outVegFirePthS)
                elim(outVegFirePthS, outVegFirePthE,strEQuery)


        else:

            print(outVegFirePthS + " exists, running eliminate")
            elim(outVegFirePthS, outVegFirePthE,strEQuery)           

    else:
        print(outVegFireE + " exists")     


  
    #Join PFR fields to veg/fire layer with dictionary  ***********************************************

    #If fields don't exist, add them    
    if len(arcpy.ListFields(outVegFirePthE, "PFR"))== 0:
        
        fields = [
                  ("meanRefFRI","LONG"),
                  ("minRefFRI","LONG"),
                  ("maxRefFRI","LONG"),
                  ("medianRefFRI","LONG"),
                  ]

        print("Adding fields to " + outVegFirePthE)
        for field in fields:
            if not arcpy.ListFields(outVegFirePthE, field[0]):
                print ("adding " + field[0])
                arcpy.AddField_management(outVegFirePthE, field[0], field[1])
        arcpy.AddField_management(outVegFirePthE, "PFR", "TEXT","", "", "50")
        arcpy.AddField_management(outVegFirePthE, "fireRegimeGrp", "TEXT","", "", "10")

        # Build a dictionary from CALVEG_2_FRID and populate new field values
        sourceFieldsList =  ['CALVEG_Code','PFR','meanRefFRI','minRefFRI','maxRefFRI','medianRefFRI','fireRegimeGrp']
        updateFieldsList = ['REGIONAL_DOMINANCE_TYPE_1','PFR','meanRefFRI','minRefFRI','maxRefFRI','medianRefFRI','fireRegimeGrp']
        print("Building dictionary of unique values")
        valueDict = {r[0]:(r[1:]) for r in arcpy.da.SearchCursor(CALVEG_2_FRID, sourceFieldsList)}  
        print("Transfering unique FRID values from CALVEG_2_FRID table to new feature class")  
        with arcpy.da.UpdateCursor(outVegFirePthE, updateFieldsList) as updateRows:  
            for updateRow in updateRows:  
                # store the Join value of the row being updated in a keyValue variable  
                keyValue = updateRow[0]  
                # verify that the keyValue is in the Dictionary  
                if keyValue in valueDict:  
                    # transfer the values stored under the keyValue from the dictionary to the updated fields.  
                    for n in range (1,len(sourceFieldsList)):  
                        updateRow[n] = valueDict[keyValue][n-1]  
                    updateRows.updateRow(updateRow)  
      
        del valueDict

    else:
        print("CALVEG 2 FRID already joined")



    #Calculate blanks to -999 ***********************************************
        
    selection2 = "\"PFR\" = 'none'"
    selection3 = "\"YLF\" = 0"
    calculate_nones(outVegFirePthE)
    calculate_YLF(outVegFirePthE)

    
    
    #Dissolve on final fields, multipart ***********************************************
    if not arcpy.Exists(outVegFirePthD):
        dissolve_layer(outVegFirePthE, outVegFirePthD)
    else:
        print(outVegFireD + " ready for Step 3 - FRID calculator")


    
    #------------------------------------------------------
    timeEnd = localtime()
    print('______________________________________________________________________')
    print('process started at: '+ strftime('%a, %d %b %Y %H:%M:%S %Z', timeStart))
    print('process ended at: '+ strftime('%a, %d %b %Y %H:%M:%S %Z', timeEnd))


except:  # General non GP errors
    exc_type, exc_value, exc_traceback = sys.exc_info()
    strTrace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print (strTrace)

