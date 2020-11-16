# Jay Maxwell
# CRP 456 - Iowa State University - Fall 2020
# Python 3.6.10
# Final Project
# 
# Grand Staircase Escalante Road Conditions
#
# This script will scrape a National Park Service web page and reteive
# rood conditions for several dirt and gravel background roads in and
# around Grand Staircase Escalante National Monument in Southern Utah.
#
# After scraping the data, the script will join the data on a subset of 
# utah roads in a subdirectory of the project folder. A resulting shapefile
# consisting of roads listed on the webpage, their current conditions, and
# respective geometry is created and placed in an outputs sub directory

## TO DO:

## 2)  TRY / CATCH STATEMENT FOR SOMETHING.



#external libraries
import geopandas as gpd
import arcpy
import pandas as pd
import matplotlib.pyplot as plt
from urllib.request import urlopen
from bs4 import BeautifulSoup


#input
#html = "gsenm.html"  # local copy for testing
url ="https://www.nps.gov/glca/learn/news/road-conditions.htm"
out_dir = "output/"
infc = "roads/gsenm_road_10mi_buffer.shp"
infcFields = ["SHAPE@","FULLNAME", "CARTOCODE", "DOT_CLASS"]

#arcpy env settings
sr = arcpy.Describe(infc).spatialReference
arcpy.env.outputCoordinateSystem = sr
arcpy.env.overwriteOutput = True

# this function takes the lowercase road as on the website (sometimes misspelled)
# and will switch it to match the road name actually found in the utah GIS roads file
def web_to_gis(x):
    switcher = {
        # ROADS TO THE EAST
        'Burr Trail' : 'BURR TRAIL RD',
        'Hole in the Rock':'HOLE IN THE ROCK RD',
        'Notom-Bullfrog':"NOTOM RD",
        'Wolverine Loop':'WOLVERINE LOOP RD',
        'Cedar Wash':'CEDAR WASH RD',
        'Spencer Flat':'SPENCER FLAT RD',
        ## roads to central
        'Left Hand Collet':'LEFT HAND COLLET CANYON RD',
        #'SMOKEY MOUNTAIN RD',
        #'ALVEY WASH',
        'Croton':'CROTAN RD',
        'Smoky Hollow':'SMOKEY HOLLOW RD',
        'Smokey Hollow':'SMOKEY HOLLOW RD',
        # ROADS TO THE WEST
        'Cottonwood':'COTTONWOOD CANYON',
        'Skutumpah':'SKUTUMPAH RD',
        'Glendale Bench':'GLENDALE BENCH',
        'Paria Movie Set':'PARIA MOVIE RD',
        'House Rock Valley':'HOUSE ROCK VALLEY',
        'White House':'WHITE HOUSE RD',
        ## ROADS TO THE NORTH
        ## a number of these roads don't match. more research needed
        "Hells Backbone": "HELLS BACKBONE RD"
    }
    return switcher.get(x,'oops')   # if we can't match a road, it gets the oops label



# this functions scrapes and parses the url
def scrape_and_parse(u):
    print("Retrieving data from web...")
    html = urlopen(url)
    soup = BeautifulSoup(html, 'lxml')
    #extract table data
    print("Parsing html...")
    table = soup.find('tbody')
    output_rows = []
    for table_row in table.findAll('tr'):
        data = table_row.findAll('p')
        output_row = []
        if (len(data)>3):
            for column in data:
                output_row.append(column.text)
            output_rows.append(output_row)
    #print(output_rows)
    return output_rows

data = scrape_and_parse(url)

#begin data frame creation
# new headers for columns
column_headers = ['road_name','date','clearance','comments']
# create datafram, use column_headers as the column names
df = pd.DataFrame(data)
df.columns = column_headers

# make a new df without the extraneous name date comments columns
df2 = df[df.road_name != 'Name'].copy()
df2.reset_index(drop=True, inplace=True)


clearance_list = {'2WD':0, '2WD High Clearance':1, '2WD, 4WD':2, '2WD, 4WD High Clearance':3, '4WD':4, '4WD High Clearance':5,'Impassable':6, '2WD, 4WD HighClearance':3}
#print(clearance_list)


road_rating = []
for row in df2['clearance']:
    road_rating.append(clearance_list[row])
df2['road_rating']=road_rating



tempdf = df2['road_name'].apply(web_to_gis)
df2['gis'] = tempdf
#print(df2)
final_df=df2[df2['gis']!='oops']    # here is where we ignore oops roads we can't find
#print(final_df)




print("Creating new featureClass...")
## create an empy feature class with all the proper validated field names   "POLYLINE"
newFC = arcpy.CreateFeatureclass_management(out_dir, "conditions.shp", 'POLYLINE')

#field validation
validFIPS = arcpy.ValidateFieldName("FIPS_road")
validRoadName = arcpy.ValidateFieldName("FULLNAME")
validComments = arcpy.ValidateFieldName("comments")
validDate = arcpy.ValidateFieldName("last_updated")
validClearance = arcpy.ValidateFieldName("clearance")
validRating = arcpy.ValidateFieldName("rating")
validCarto = arcpy.ValidateFieldName("CARTOCODE")
validDotClass = arcpy.ValidateFieldName("DOT_CLASS")


#add fields to new featureclass
arcpy.AddField_management(newFC, validRoadName ,"TEXT")
arcpy.AddField_management(newFC, validCarto, "TEXT")
arcpy.AddField_management(newFC, validDotClass, "TEXT")
arcpy.AddField_management(newFC, validComments ,"TEXT")
arcpy.AddField_management(newFC, validDate ,"TEXT")
arcpy.AddField_management(newFC, validClearance,"TEXT")
arcpy.AddField_management(newFC, validRating ,"LONG")

                          

#insert cursor for featureclass
#insert = arcpy.da.InsertCursor(newFC, [validRoadName, validDate, validClearance, validComments, validRating])

insert = arcpy.da.InsertCursor(newFC, ['SHAPE@', validRoadName, validCarto, validDotClass, validComments, validDate, validClearance, validRating])

# Enter for loop for each row on our utah roads shapefile
print("Populating feature Class...")
for inrow in arcpy.da.SearchCursor(infc, infcFields):
    shape = inrow[0]
    full_name = inrow[1]
    carto = inrow[2]
    dotclass = inrow[3]
    for row in final_df.iterrows():
        row_list=[]
        if full_name == row[1][5]:
            comment = row[1][3]
            clearance = row[1][2]
            rating = row[1][4]
            last_update = row[1][4]
            row_list = [shape, full_name, carto, dotclass, comment, last_update, clearance, rating]
            #print(row_list)
            insert.insertRow(row_list)

del insert


## export a quick map of our shapefile, with gsenm roads subset and bounds
#import the shape files
bounds = gpd.read_file('gsenm-bounds/gsenm-bounds.shp')
roads = gpd.read_file('roads/GSENM_roads.shp')
conditions = gpd.read_file('output/conditions.shp')

#set up the plot
fig, ax = plt.subplots(figsize=(8,8))
ax.set_aspect('equal')

#plot the shape files
bounds.plot(ax=ax, color='white', edgecolor='brown', linewidth=2);
roads.plot(ax=ax, color='gray');
conditions.plot(ax=ax, linewidth =2, color="blue")

#save the plot
plt.title("Roads in the conditions shapefile", fontsize=12)
plt.axis('off')
plt.savefig('output/gsenm-roads.png', dpi=72)
