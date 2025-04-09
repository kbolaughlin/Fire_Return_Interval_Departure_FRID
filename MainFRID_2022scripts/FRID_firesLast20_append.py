# Import system modules
import sys, string, os, arcpy, traceback, time
from os.path import isdir, join, normpath, split, exists
import fire_interval_v2 as fire


#To calculate number of fires in last 20 yrs

def calculate_fields(datasrc,years_processed):
    try:

        print("Calculating new fire fields: " + datasrc)
        #fields = ["numFires", "numFires_1970","TSLF", "YLF", "firesLast40","firesLast20"]

        listFields = [field.name for field in arcpy.ListFields(datasrc)]

        with arcpy.da.UpdateCursor(datasrc, listFields) as rows:
            for row in rows:
                oid = row[0]
                print ("working on OBJECTID" + str(oid))
                num20 = 0 #- number of fires in last 20 years
                for proc_year in years_processed:
                    #get value of this year's year (i.e. 2016)
                    fld = "yr" + str(proc_year)
                    #print ("working on " + fld + "....")
                    rowIndex = listFields.index(fld) #find this field's row index
                    #print( "rowIndex is " + str(rowIndex))                           
                    try:
                        val = row[rowIndex]
                        #print("val is " + str(val) + " for " + fld )                       
                    except:
                        print("Failed to get value of: " + fld)
                        raise

                    if (val != 0): #if value in yr field is not 0
                        num20 = num20 + 1
                            

                row[listFields.index("firesLast20")] = num20
                rows.updateRow(row)

    except:
        print('Cursor Calculations failure: ' + datasrc)
        raise


try:


    datasrc = r"N:\project\frid\workspace\FRID_2021\AddendumNumYrsLast20.gdb\fire2020ElimExp_update"
    #Add new fields
    if not arcpy.ListFields(datasrc, "firesLast20"):
        print ("adding firesLast20")
        arcpy.AddField_management(datasrc, "firesLast20", "SHORT")

    years_processed = []
    for i in range(2000, 2021):
        years_processed.append(str(i))
        
    calculate_fields(datasrc, years_processed)
    
    lstLegFields = ['YLF','TSLF','numFires', 'numFires_1970','LastFireName','firesLast40', 'firesLast20']
    if not arcpy.Exists(strPathFCdiss):
        print("final dissolve....")
        arcpy.Dissolve_management(datasrc,datasrc + "_diss",lstLegFields, "", "MULTI_PART")

except:  # General non GP errors
    exc_type, exc_value, exc_traceback = sys.exc_info()
    strTrace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(strTrace)



