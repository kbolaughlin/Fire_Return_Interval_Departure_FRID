# -*- coding: cp1252 -*-
### Manual Changes Required: 6, potentially 7
### TO DO - Metadata should be auto-updated

# FRID_Step3_CalcFields_w1970.py
# cclark, 4/2021 - Updated FRID (Fire Return Interval Departure) script for Python 3.x
# calculates FRID fields for final layer
# 5/2020 - add calculations for using base year of 1970 - keeping 1908 start year as well
import sys, string, os, traceback, arcpy, time
from time import *
import datetime

##def message(string):
##    print string
##    arcpy.AddMessage(string)

print("Starting FRID calculator...")

#Input veg/fire feature class from FRIDFinalStep2.py
forest_burn_layer = r"D:\frid\workspace\FRID_2022\SIntFRID.gdb\SIntVegFireIdenElDiss_FIN" #------CHANGE
## forest_burn_layer = r"D:\frid\workspace\FRID_2022\NIntFRID.gdb\NIntVegFireIdenElDiss_FIN"
## forest_burn_layer = r"D:\frid\workspace\FRID_2022\CCstFRID.gdb\CCstVegFireIdenElDiss_FIN"
## forest_burn_layer = r"D:\frid\workspace\FRID_2022\NSieFRID.gdb\NSieVegFireIdenElDiss_FIN"
## forest_burn_layer = r"D:\frid\workspace\FRID_2022\SSieFRID.gdb\SSieVegFireIdenElDiss_FIN"
## forest_burn_layer = r"D:\frid\workspace\FRID_2022\CValFRID.gdb\CValVegFireIdenElDiss_FIN"
## forest_burn_layer = r"D:\frid\workspace\FRID_2022\GBasFRID.gdb\GBasVegFireIdenElDiss_FIN"
## forest_burn_layer = r"D:\frid\workspace\FRID_2022\SCstFRID.gdb\SCstVegFireIdenElDiss_FIN"
## forest_burn_layer = r"D:\frid\workspace\FRID_2022\NCstEastFRID.gdb\NCstEastVegFireIdenElDiss_FIN"
## forest_burn_layer = r"D:\frid\workspace\FRID_2022\NCstMidFRID.gdb\NCstMidVegFireIdenElDiss_FIN"
## forest_burn_layer = r"D:\frid\workspace\FRID_2022\NCstWestFRID.gdb\NCstWestVegFireIdenElDiss_FIN"

#current fire year (ie last year in dataset)
current_year = 2021 #<----------------------------------------------------------------CHANGE
current_year_1970 = 1970 #added 5/2020 (don't change)

#The number of years in the fire record (e.g., 2019-1908=112 years inclusive)
num_yrs = (int(current_year) - 1908) + 1
#e.g., 2019-1970=50 years inclusive
num_yrs_1970 = (int(current_year) - 1970) + 1 #added 5/2020 - don't change

#final output folder
finFolderPath = r"D:\frid\workspace\FRID_2022\Final_FRID_outputs" #<-------------------------CHANGE
#final output file geodatabase
finName = "SouthInterior" #<------------------------------------------------------CHANGE
suffix = ""  #<-----------------------------------------------------------------------CHANGE
## finGDB = "FRID_" + finName + (str(current_year)[2:]) +  "_1_" + suffix + ".gdb" #<----------use this line for layers with East, Mid or West such as North Coast
finGDB = "FRID_" + finName + (str(current_year)[2:]) +  "_1" + ".gdb" #<-------comment out when layers have suffix such as North Coast

#Choices
##    SouthInterior
##    NorthInterior
##    CentralCoast
##    NorthSierra
##    SouthSierra
##    CentralValley
##    GreatBasin
##    SouthCoast
##    NorthCoast, suffix East
##    NorthCoast, suffix Mid
##    NorthCoast, suffix West
finFC = finGDB[:-4] #FRID_NorthCoast12_1_West
finGDBpath = finFolderPath + "/" + finGDB + "/" + finFC 

#Blank template for final layer
finTemplate = r"N:\project\frid\workspace\A_FRID_FinalTemplate.gdb\FinalFRID_Template_2020v2" #<---------this should not change unless requested


#****************************************************************************
timeStart = localtime()
now = datetime.datetime.now()  

try:
    # make dir for GDBs
    if not os.path.exists(finFolderPath):
        os.mkdir(finFolderPath)
    #make gdb    
    if not arcpy.Exists(finFolderPath + "/" + finGDB):
        print("Creating final gdb called " + finGDB)
        arcpy.CreateFileGDB_management (finFolderPath, finGDB, "10.0")
    else:
        print(finGDB + " exists")

    print("num_yrs is " + str(num_yrs))
    
    if not arcpy.Exists(finGDBpath):
        print("Working on " + forest_burn_layer)

        print("Adding fields if don't exist...")
        #adding currentFRI now... moved from script 1 script 3 - not needed sooner
        if not arcpy.ListFields(forest_burn_layer, "currentFRI"):
            arcpy.AddField_management(forest_burn_layer, "currentFRI", "SHORT")
            
        if not arcpy.ListFields(forest_burn_layer, "minPFRID"):
            arcpy.AddField_management(forest_burn_layer, "minPFRID", "float")
        if not arcpy.ListFields(forest_burn_layer, "medianPFRID"):
            arcpy.AddField_management(forest_burn_layer, "medianPFRID", "float")#Added 4/2011
        if not arcpy.ListFields(forest_burn_layer, "meanPFRID"):
            arcpy.AddField_management(forest_burn_layer, "meanPFRID", "float")
        if not arcpy.ListFields(forest_burn_layer, "maxPFRID"):
            arcpy.AddField_management(forest_burn_layer, "maxPFRID", "float")
        if not arcpy.ListFields(forest_burn_layer, "meanCC_FRI"):                        
            arcpy.AddField_management(forest_burn_layer, "meanCC_FRI", "LONG")
        if not arcpy.ListFields(forest_burn_layer, "NPS_FRID"):                                
            arcpy.AddField_management(forest_burn_layer, "NPS_FRID", "float")
        if not arcpy.ListFields(forest_burn_layer, "NPS_FRID_Index"):                                
            arcpy.AddField_management(forest_burn_layer, "NPS_FRID_Index", "text", "#","#", "10")

        #added 5/2020    
        if not arcpy.ListFields(forest_burn_layer, "currentFRI_1970"):
            arcpy.AddField_management(forest_burn_layer, "currentFRI_1970", "LONG")
##        if not arcpy.ListFields(forest_burn_layer, "minPFRID_1970"):
##            arcpy.AddField_management(forest_burn_layer, "minPFRID_1970", "float")
##        if not arcpy.ListFields(forest_burn_layer, "medianPFRID_1970"):
##            arcpy.AddField_management(forest_burn_layer, "medianPFRID_1970", "float")#Added 4/2011
        if not arcpy.ListFields(forest_burn_layer, "meanPFRID_1970"):
            arcpy.AddField_management(forest_burn_layer, "meanPFRID_1970", "float")
##        if not arcpy.ListFields(forest_burn_layer, "maxPFRID_1970"):
##            arcpy.AddField_management(forest_burn_layer, "maxPFRID_1970", "float")
        if not arcpy.ListFields(forest_burn_layer, "meanCC_FRI_1970"):                        
            arcpy.AddField_management(forest_burn_layer, "meanCC_FRI_1970", "LONG")

        #should not be any other class calculated for NPS than this one per Hugh


 #****************************************************************************
        #Calculate current FRI, mean, min, max, median PfRID, condition class back to 1908
            
        print("Calculating values from meanRefFRI back to 1908")
        meanRefFRI_list = ["numFires", "meanRefFRI", "currentFRI", "meanPFRID", "meanCC_FRI"]
        with arcpy.da.UpdateCursor(forest_burn_layer, meanRefFRI_list) as rows:          
            for row in rows:
                nb = int(row[0])
                
                #change nulls to zero
                if (row[0] == None): #numFires
                    row[0] = 0
                    rows.updateRow(row)
                
                if (row[1] == None): #meanRefFRI
                    row[1] = 0
                    rows.updateRow(row)
                    
                RFRI = int(row[1]) #meanRefFRI
                fRFRI = float(RFRI) 
                #Set CFRI (Current FRI) equal to num_yrs (which is (int(current_year) - 1908) + 1) / number of fires + 1
                CFRI = num_yrs/(nb+1) #104/(0+1) = 104 = currentFRI
                row[2] = CFRI
                fCFRI = float(CFRI)
                
                if (RFRI == -999): #if meanRefFRI  = -999
                    meanPFRID = -999
                elif (CFRI < RFRI): #if currentFRI < meanRefFRI
                    meanPFRID = -(1 - fCFRI/fRFRI) # FRI HAS DECREASED
                elif (CFRI > RFRI): 
                    meanPFRID = 1 - fRFRI/fCFRI    # FRI HAS INCREASED
                else:
                    meanPFRID = 0    # IDENTITY produces no data, so CFRI == RFRI == 0
                row[3] = meanPFRID  #meanPFRID
                
                if (meanPFRID == -999):
                    meanCC_FRI = "-999"
                elif (meanPFRID < -.66):
                    meanCC_FRI = "-3"
                elif (meanPFRID < -.33):
                    meanCC_FRI = "-2"
                elif (meanPFRID < 0):
                    meanCC_FRI = "-1"
                elif (meanPFRID < .33):
                    meanCC_FRI = "1"
                elif (meanPFRID < .66):
                    meanCC_FRI = "2"
                elif (meanPFRID < 1):
                    meanCC_FRI = "3"
                elif (meanPFRID == 1):
                    meanCC_FRI = print("PFR is null, did not join to Dom1")
                else:
                    meanCC_FRI = print("meanCC_FRI is NULL. Check and fix...")                    
                row[4] = meanCC_FRI
                
                rows.updateRow(row)


              
        print("Calculating values from minRefFRI")
        minRefFRI_list = ["numFires", "minRefFRI", "currentFRI", "minPFRID"]
        with arcpy.da.UpdateCursor(forest_burn_layer, minRefFRI_list) as rows:          
            for row in rows:                 
                nb = int(row[0])
                                   
                #set null minRefFRI to 0
                if (row[1] == None):
                    row[1] = int("0")
                    rows.updateRow(row)
                                   
                RFRI = int(row[1])
                fRFRI = float(RFRI)
                CFRI = num_yrs/(nb+1)
                row[2] = CFRI
                fCFRI = float(CFRI)

                if (RFRI == -999):
                    minPFRID = -999
                elif (CFRI < RFRI):
                    minPFRID = -(1 - fCFRI/fRFRI) # FRI HAS DECREASED
                elif (CFRI > RFRI):
                    minPFRID = 1 - fRFRI/fCFRI    # FRI HAS INCREASED
                else:
                    minPFRID = 0    # IDENTITY produces no data, so CFRI == RFRI == 0
                row[3] = minPFRID 
                rows.updateRow(row)
            

        print("Calculating values from maxRefFRI")
        maxRefFRI_list = ["numFires", "maxRefFRI", "currentFRI", "maxPFRID"]
        with arcpy.da.UpdateCursor(forest_burn_layer, maxRefFRI_list) as rows:          
            for row in rows:                 
                nb = int(row[0])

                if (row[1] == None):
                    row[1] = int("0")
                    rows.updateRow(row)
                    
                RFRI = int(row[1])
                fRFRI = float(RFRI)
                CFRI = num_yrs/(nb+1)
                row[2] = CFRI
                fCFRI = float(CFRI)

                if (RFRI == -999): maxPFRID = -999
                elif (CFRI < RFRI):
                    maxPFRID = -(1 - fCFRI/fRFRI) # FRI HAS DECREASED
                elif (CFRI > RFRI):
                    maxPFRID = 1 - fRFRI/fCFRI    # FRI HAS INCREASED
                else:
                    maxPFRID = 0    # IDENTITY produces no data, so CFRI == RFRI == 0
                row[3] = maxPFRID
                rows.updateRow(row)
            

        print("Calculating values from medianRefFRI")
        medianRefFRI_list = ["numFires", "medianRefFRI", "currentFRI", "medianPFRID"]
        with arcpy.da.UpdateCursor(forest_burn_layer, medianRefFRI_list) as rows:          
            for row in rows:                 
                nb = int(row[0])
                if (row[1] == None):
                    row[1] = int("0")
                    rows.updateRow(row)

                RFRI = int(row[1]) #medianRefFRI
                fRFRI = float(RFRI)
                CFRI = num_yrs/(nb+1) #112/(numFires +1)
                row[2] = CFRI #currentFRI
                fCFRI = float(CFRI)

                if (RFRI == -999):
                    medPFRID = -999
                elif (CFRI < RFRI): #if currentFRI < medianRefFRI:
                    medPFRID = -(1 - fCFRI/fRFRI) # medianPFRID = -( 1 - float(currentFRI)/medianRefFRI)  i.e.  FRI HAS DECREASED
                elif (CFRI > RFRI): #if currentFRI > medianRefFRI:
                    medPFRID = 1 - fRFRI/fCFRI    # medianPFRID =  1 - float(medianRefFRI)/currentFRI   i.e. FRI HAS INCREASED
                else:
                    medPFRID = 0    # IDENTITY produces no data, so CFRI == RFRI == 0
                row[3] = medPFRID
                rows.updateRow(row)

#****************************************************************************
        #added 5/2020
        # Calculate current FRI, mean PfRID, condition class back to 1970
            
        print("Calculating values from meanRefFRI back to 1970")
        meanRefFRI_list_1970 = ["numFires_1970", "meanRefFRI", "currentFRI_1970", "meanPFRID_1970", "meanCC_FRI_1970"]
        with arcpy.da.UpdateCursor(forest_burn_layer, meanRefFRI_list_1970) as rows:          
            for row in rows:
                nb = int(row[0])
                
                #change nulls to zero
                if (row[0] == None): #numFires
                    row[0] = 0
                    rows.updateRow(row)
                
                if (row[1] == None): #meanRefFRI
                    row[1] = 0
                    rows.updateRow(row)
                    
                RFRI = int(row[1]) #meanRefFRI
                fRFRI = float(RFRI) 
                #Set CFRI (Current FRI) equal to number of years divided by number of fires plus 1
                CFRI = num_yrs_1970/(nb+1) #50/(0+1) = 50 = currentFRI
                row[2] = CFRI
                fCFRI = float(CFRI)
                
                if (RFRI == -999): #if meanRefFRI  = -999
                    meanPFRID = -999 
                elif (CFRI < RFRI): #if currentFRI < meanRefFRI 
                    meanPFRID = -(1 - fCFRI/fRFRI) # FRI HAS DECREASED     -1(1 - 50/133)
                elif (CFRI > RFRI): #if currentFRI > meanRefFRI
                    meanPFRID = 1 - fRFRI/fCFRI    # FRI HAS INCREASED 1 - 35/50
                else:
                    meanPFRID = 0    # IDENTITY produces no data, so CFRI == RFRI == 0
                row[3] = meanPFRID  #meanPFRID
                
                if (meanPFRID == -999):
                    meanCC_FRI = "-999"
                elif (meanPFRID < -.66):
                    meanCC_FRI = "-3"
                elif (meanPFRID < -.33):
                    meanCC_FRI = "-2"
                elif (meanPFRID < 0):
                    meanCC_FRI = "-1"
                elif (meanPFRID < .33):
                    meanCC_FRI = "1"
                elif (meanPFRID < .66):
                    meanCC_FRI = "2"
                elif (meanPFRID < 1):
                    meanCC_FRI = "3"
                elif (meanPFRID == 1):
                    meanCC_FRI = print("PFR is null, did not join to Dom1")
                else:
                    meanCC_FRI = print("meanCC_FRI_1970 is NULL. Check and fix...")
                    
                row[4] = meanCC_FRI
                
                rows.updateRow(row)

##        From Hugh Safford, 6/9/2020

##        I’ve done some thinking about the 1970-based data, and they will be easy to misinterpret.
##        Please remove the median, min, and max PFRID calcs based on 1970 from the dataset.
##        I.e. let’s only include the mean PFRID from the 1970 data.


##        #Calculate reference FRI back to 1970
##              
##        print("Calculating values from minRefFRI for 1970")
##        minRefFRI_list_1970 = ["numFires_1970", "minRefFRI", "currentFRI_1970", "minPFRID_1970"]
##        with arcpy.da.UpdateCursor(forest_burn_layer, minRefFRI_list_1970) as rows:          
##            for row in rows:                 
##                nb = int(row[0])
##                                   
##                #set null minRefFRI to 0
##                if (row[1] == None):
##                    row[1] = 0
##                    rows.updateRow(row)
##                                   
##                RFRI = int(row[1])
##                fRFRI = float(RFRI)
##                CFRI = num_yrs_1970/(nb+1)
##                row[2] = CFRI
##                fCFRI = float(CFRI)
##
##                if (RFRI == -999):
##                    minPFRID = -999
##                elif (CFRI < RFRI):
##                    minPFRID = -(1 - fCFRI/fRFRI) # FRI HAS DECREASED
##                elif (CFRI > RFRI):
##                    minPFRID = 1 - fRFRI/fCFRI    # FRI HAS INCREASED
##                else:
##                    minPFRID = 0    # IDENTITY produces no data, so CFRI == RFRI == 0
##                row[3] = minPFRID 
##                rows.updateRow(row)
##            
##
##        print("Calculating values from maxRefFRI for 1970")
##        maxRefFRI_list_1970 = ["numFires_1970", "maxRefFRI", "currentFRI_1970", "maxPFRID_1970"]
##        with arcpy.da.UpdateCursor(forest_burn_layer, maxRefFRI_list_1970) as rows:          
##            for row in rows:                 
##                nb = int(row[0])
##
##                if (row[1] == None):
##                    row[1] = int("0")
##                    rows.updateRow(row)
##                    
##                RFRI = int(row[1])
##                fRFRI = float(RFRI)
##                CFRI = num_yrs_1970/(nb+1)
##                row[2] = CFRI
##                fCFRI = float(CFRI)
##
##                if (RFRI == -999): maxPFRID = -999
##                elif (CFRI < RFRI):
##                    maxPFRID = -(1 - fCFRI/fRFRI) # FRI HAS DECREASED
##                elif (CFRI > RFRI):
##                    maxPFRID = 1 - fRFRI/fCFRI    # FRI HAS INCREASED
##                else:
##                    maxPFRID = 0    # IDENTITY produces no data, so CFRI == RFRI == 0
##                row[3] = maxPFRID
##                rows.updateRow(row)
##            
##
##        print("Calculating values from medianRefFRI for 1970")
##        medianRefFRI_list_1970 = ["numFires_1970", "medianRefFRI", "currentFRI_1970", "medianPFRID_1970"]
##        with arcpy.da.UpdateCursor(forest_burn_layer, medianRefFRI_list_1970) as rows:          
##            for row in rows:                 
##                nb = int(row[0])
##                if (row[1] == None):
##                    row[1] = int("0")
##                    rows.updateRow(row)
##
##                RFRI = int(row[1]) #medianRefFRI
##                fRFRI = float(RFRI) 
##                CFRI = num_yrs_1970/(nb+1) #112/(numFires +1)
##                row[2] = CFRI #currentFRI_1970
##                fCFRI = float(CFRI)
##
##                if (RFRI == -999):
##                    medPFRID = -999
##                elif (CFRI < RFRI): #if currentFRI_1970 < medianRefFRI:
##                    medPFRID = -(1 - fCFRI/fRFRI) # medianPFRID_1970 = -( 1 - medianRefFRI/medianRefFRI)  i.e.  FRI HAS DECREASED
##                elif (CFRI > RFRI): #if currentFRI > medianRefFRI:
##                    medPFRID = 1 - fRFRI/fCFRI    # medianPFRID_1970 =  1 - medianRefFRI/currentFRI   i.e. FRI HAS INCREASED
##                else:
##                    medPFRID = 0    # IDENTITY produces no data, so CFRI == RFRI == 0
##                row[3] = medPFRID
##                rows.updateRow(row)
##            

    #****************************************************************************
        #TSLF (time since last fire) comes from fire history - if no fire occurred, TSLF will not
        # be burned into the final layer, hence it's value for areas of non-fire will be zero and need
        # to be manually calculated to <current year> - <first year>  (i.e. (2012 - 1908) = 104) 


        tslf = int(current_year) - 1908
        print("Calculating selected values for TSLF to " + str(tslf))
        fields = ["numFires", "TSLF"]
        with arcpy.da.UpdateCursor(forest_burn_layer, fields) as rows:
            for row in rows:
                if (row[0] == 0):
                    row[1] = str(tslf)
                rows.updateRow(row)
            


    #****************************************************************************
        # National Park Service calculations
        # For the 1970 calculations for NPS Index per Hugh:  this will not change, since it only refers to the most
        # recent fire and hence the date of 1970 is meaningless

        print("Calculating NPS fields")
        fields = ["PFR", "NPS_FRID", "NPS_FRID_Index", "meanRefFRI", "TSLF"]
        with arcpy.da.UpdateCursor(forest_burn_layer, fields) as rows:
            for row in rows:
                if (row[0] == "none"):
                    row[1] = -999
                    row[2] = "-999"
                else:
                    row[1] = float(row[3] - row[4]) / row[3]
                    #rest of NPS_FRID_Index calculated later
                rows.updateRow(row)


    #****************************************************************************
        #Set percent FRID to zero where needed for years back to 1908
        #For areas dominated by PFRs with a mean (and min, med, max) reference FRI greater than or equal to the number of years
        # in the fire record <num_yrs>, and that have not burned in the period
        # of historical record considered in this analysis (i.e. since 1908), the FRID is assumed to equal zero.
                                
        refFRI_list = ["meanRefFRI","minRefFRI", "maxRefFRI", "medianRefFRI", "currentFRI", "meanPFRID", "meanCC_FRI","NPS_FRID", "minPFRID", "maxPFRID", "medianPFRID"]

        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list) as rows:          
            for row in rows:
                num_rec = num_yrs
                meanR = row[0] #meanRefFRI
                curF = row[4] #currentFRI
                meanFD = row[5] #meanPFRID
                if (meanR >= num_rec and curF >= num_rec):  #if meanRefFRI >= num_yrs and currentFRI >= num_yrs
                    meanFD = 0
                row[5] = meanFD #meanPFRID
                rows.updateRow(row)
        

        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list) as rows:          
            for row in rows:
                num_rec = num_yrs
                minR = row[1] #minRefFRI
                curF = row[4]#currentFRI
                minFD = row[8] #minPFRID
                if (minR >= num_rec and curF >= num_rec):
                    minFD = 0
                row[8] = minFD #minPFRID
                rows.updateRow(row)


        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list) as rows:          
            for row in rows:
                num_rec = num_yrs
                maxR = row[2]
                curF = row[4]
                maxFD = row[9]
                if (maxR >= num_rec and curF >= num_rec):
                    maxFD = 0
                row[9] = maxFD #maxPFRID
                rows.updateRow(row)

        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list) as rows:          
            for row in rows:
                num_rec = num_yrs
                medR = row[3]
                curF = row[4]
                medFD = row[10]
                if (medR >= num_rec and curF >= num_rec):
                    medFD = 0
                row[10] = medFD #medPFRID
                rows.updateRow(row)    


        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list) as rows:          
            for row in rows:
                num_rec = num_yrs
                meanR = row[0]
                curF = row[4]
                meanCC = row[6]
                if (meanR >= num_rec and curF >= num_rec): #if meanRefFRI >= num_yrs and currentFRI >= num_yrs
                    meanCC = 1 #meanCC_FRI
                row[6] = meanCC
                rows.updateRow(row)
                
                      
        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list) as rows:          
            for row in rows:
                num_rec = num_yrs
                meanR = row[0]
                curF = row[4]
                meanF = row[7]
                if (meanR >= num_rec and curF >= num_rec): #if meanRefFRI >= num_yrs and currentFRI >= num_yrs)
                    meanF = 1
                row[7] = meanF #NPS_FRID
                rows.updateRow(row)


    #****************************************************************************
        #Set percent FRID to zero where needed for years back to 1970
        #For areas dominated by PFRs with a mean (and min, med, max) reference FRI greater than or equal to the number of years
        # in the fire record <num_yrs_1970>, and that have not burned in the period
        # of historical record considered in this analysis (i.e. since 1970), the FRID is assumed to equal zero.
                                
        refFRI_list_1970 = ["meanRefFRI","minRefFRI", "maxRefFRI", "medianRefFRI", "currentFRI_1970", "meanPFRID_1970", "meanCC_FRI_1970","NPS_FRID"] #, "minPFRID_1970", "maxPFRID_1970", "medianPFRID_1970"]

        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list_1970) as rows:          
            for row in rows:
                num_rec = num_yrs_1970
                meanR = row[0] #meanRefFRI
                curF = row[4] #currentFRI_1970
                meanFD = row[5] #meanPFRID_1970
                if (meanR >= num_rec and curF >= num_rec):  #if meanRefFRI >= num_yrs_1970 and currentFRI_1970 >= num_yrs_1970
                    meanFD = 0
                row[5] = meanFD #meanPFRID_1970
                rows.updateRow(row)
        

##        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list_1970) as rows:          
##            for row in rows:
##                num_rec = num_yrs_1970
##                minR = row[1] #minRefFRI
##                curF = row[4]#currentFRI_1970
##                minFD = row[8] #minPFRID_1970
##                if (minR >= num_rec and curF >= num_rec):
##                    minFD = 0
##                row[8] = minFD #minPFRID_1970
##                rows.updateRow(row)
##
##
##        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list_1970) as rows:          
##            for row in rows:
##                num_rec = num_yrs_1970
##                maxR = row[2]
##                curF = row[4]
##                maxFD = row[9]
##                if (maxR >= num_rec and curF >= num_rec):
##                    maxFD = 0
##                row[9] = maxFD #maxPFRID_1970
##                rows.updateRow(row)
##
##        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list_1970) as rows:          
##            for row in rows:
##                num_rec = num_yrs_1970
##                medR = row[3]
##                curF = row[4]
##                medFD = row[10]
##                if (medR >= num_rec and curF >= num_rec):
##                    medFD = 0
##                row[10] = medFD #medPFRID_1970
##                rows.updateRow(row)    


        with arcpy.da.UpdateCursor(forest_burn_layer, refFRI_list_1970) as rows:          
            for row in rows:
                num_rec = num_yrs_1970
                meanR = row[0]
                curF = row[4]
                meanCC = row[6]
                if (meanR >= num_rec and curF >= num_rec): #if meanRefFRI >= num_yrs_1970 and currentFRI_1970 >= num_yrs_1970
                    meanCC = 1 #meanCC_FRI_1970
                row[6] = meanCC
                rows.updateRow(row)
                


    #****************************************************************************
        #NPS class calculations

        print("Calculating NPS mean class values...")
        NPS_list = ["NPS_FRID",  "NPS_FRID_Index"]
        with arcpy.da.UpdateCursor(forest_burn_layer, NPS_list) as rows:          
            for row in rows:          
                
                if (row[0] <= -5 and row[0] > -999):          
                    row[1] = "Ext"             

                elif (row[0] > -5 and row[0] <= -2):           
                    row[1] = "Hi"
                   
                elif (row[0] > -2 and row[0] <= 0):         
                    row[1] = "Mod"

                elif (row[0] > 0):            
                    row[1] = "Low"

                rows.updateRow(row)
                
    #****************************************************************************
        #Round fields to percentages
        print("Changing 1908 FrqDep fields to percent..")
        Pfrid_list = ["PFR", "meanPFRID","minPFRID", "maxPFRID", "medianPFRID"]
        with arcpy.da.UpdateCursor(forest_burn_layer, Pfrid_list) as rows:          
            for row in rows:
                if (row[0] != "none"):
                    row[1] = row[1] * 100
                    row[2] = row[2] * 100
                    row[3] = row[3] * 100
                    row[4] = row[4] * 100
                rows.updateRow(row)



        print("Changing 1970 FrqDep fields to percent..")
        Pfrid_list_1970 = ["PFR", "meanPFRID_1970"] #,"minPFRID_1970", "maxPFRID_1970", "medianPFRID_1970"]
        with arcpy.da.UpdateCursor(forest_burn_layer, Pfrid_list_1970) as rows:          
            for row in rows:
                if (row[0] != "none"):
                    row[1] = row[1] * 100
##                    row[2] = row[2] * 100
##                    row[3] = row[3] * 100
##                    row[4] = row[4] * 100
                rows.updateRow(row)

        #*******************************************************
        #Append to final template
      
        print("Copying " + finTemplate + " to " + os.path.split(finGDBpath)[0])
        arcpy.Copy_management (finTemplate, finGDBpath)


    else:
        print(finGDBpath + " exists.")

    #***************************************************************************
    #Append to final FRID template to <FRID_<year>/Final_FRID_outputs folder
    result = arcpy.GetCount_management(finGDBpath)
    count = int(result.getOutput(0))
    if count == 0:
        print("Appending " + forest_burn_layer + " to " + finGDBpath)
        arcpy.Append_management (forest_burn_layer, finGDBpath, "NO_TEST")

    print("Rounding fields...")
    Pfrid_list = ["PFR", "meanPFRID","minPFRID", "maxPFRID", "medianPFRID", "NPS_FRID"]
    with arcpy.da.UpdateCursor(finGDBpath, Pfrid_list) as rows:          
        for row in rows:
            if (row[0] != "none"):
                #print ("rounding")
                row[1] = round(row[1], 2)
                row[2] = round(row[2], 2)
                row[3] = round(row[3], 2)
                row[4] = round(row[4], 2)
                row[5] = round(row[5], 2)

            rows.updateRow(row)
            
    Pfrid_list_1970 = ["PFR", "meanPFRID_1970"] #,"minPFRID_1970", "maxPFRID_1970", "medianPFRID_1970"]
    with arcpy.da.UpdateCursor(finGDBpath, Pfrid_list_1970) as rows:          
        for row in rows:
            if (row[0] != "none"):
                #print ("rounding")
                row[1] = round(row[1], 2)
##                row[2] = round(row[2], 2)
##                row[3] = round(row[3], 2)
##                row[4] = round(row[4], 2)

            rows.updateRow(row)
            
    

    print("All done! Final output is " + finGDBpath)

    timeEnd = localtime()
    print('______________________________________________________________________')
    print('process started at: '+ strftime('%a, %d %b %Y %H:%M:%S %Z', timeStart))
    print('process ended at: '+ strftime('%a, %d %b %Y %H:%M:%S %Z', timeEnd))

    later = datetime.datetime.now() 
    elapsed = later - now  
    print ("elapsed time: " + str(elapsed))
             
except:  # General non GP errors
    exc_type, exc_value, exc_traceback = sys.exc_info()
    strTrace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print (strTrace)


