# Fire Return Interval Departure(FRID)

## MainFRID_2022scripts
This series of scripts creates a Fire Return Interval Departure (FRID) spatial vector layer (available at https://www.fs.usda.gov/detail/r5/landmanagement/gis/?cid=stelprdb5361974) consisting of information compiled about fire return intervals for major vegetation types on the 18 National Forests in California and adjacent land jurisdictions. Comparisons are made between pre-Euroamerican settlement and contemporary fire return intervals (FRIs). Current departures from the pre-Euroamerican settlement FRIs are calculated based on mean, median, minimum, and maximum FRI values. This map is a project of the USFS Pacific Southwest Region Ecology Program.
 
Script 1 takes fire perimeters and prescribed burns,  downloaded from the  California Department of Forestry and Fire Protection's Fire and Resource Assessment Program (FRAP) (GIS Mapping and Data Analytics | CAL FIRE)  and "flattens out" the overlapping data through a series of unions, leaving only the latest fire polygon for any spot on the ground.
 
Script 2, takes US Forest Service Existing Vegetation (EVEG) polygons from the time period of 2011 (https://www.fs.usda.gov/detail/r5/landmanagement/resourcemanagement/?cid=stelprdb5365219) which uses the CALVEG classification,  and integrates these into the fire polygons, then joining pre-settlement fire regime (PFR) vegetation groups (Van de Water and Safford 2011) and their associated fields.
 
Script 3 calculates the following FRID fields:
meanPFRID – mean percent FRID
medianPFRID – median percent FRID
minPFRID – minimum percent FRID
maxPFRID – maximum percent FRID
meanCC_FRI – classes from the meanPFRID field
NPS_FRID – National Park Service FRID
NPS_FRID_Index - National Park Service FRID index
 
Citation:  Safford, H.D., K. van de Water, and C. Clark. 2020. California Fire Return Interval Departure (FRID) map, 2019 version. USDA Forest Service, Pacific Southwest Region, Sacramento and Vallejo, CA
 
## RRK_Raster_FRID_scripts
This set of scripts dissolves the following FRID fields from the polygon layer into standalone rasters for use in the Regional Resource Kit (https://caregionalresourcekits.org/clm.html#fire_dyn ).
- TSLF
- currentFRI
- currentFRI_1970
- meanPFRID
- meanPFRID_1970
- maxPFRID
- medianPFRID
- minPFRID
- meanCC_FRI