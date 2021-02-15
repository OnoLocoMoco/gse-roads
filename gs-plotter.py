import geopandas as gpd
import matplotlib.pyplot as plt


## export a quick map of our shapefile, with gsenm roads subset and bounds
#import the shape files


def plot_map(new_feature):
    bounds = gpd.read_file('gsenm-bounds/gsenm-bounds.shp')
    roads = gpd.read_file('roads/GSENM_roads.shp')


    new_layer = gpd.read_file(new_feature)

    #set up the plot
    fig, ax = plt.subplots(figsize=(8,8))
    ax.set_aspect('equal')

    #plot the shape files
    bounds.plot(ax=ax, color='white', edgecolor='brown', linewidth=2);
    roads.plot(ax=ax, color='gray');
    new_layer.plot(ax=ax, linewidth =2, color="blue")

    #save the plot
    plt.suptitle("Grand Staircase Escalante")
    plt.title("Feature in the '{}' shapefile".format(new_feature), fontsize=12)
    plt.axis('off')
    plt.savefig('output/gsenm-plot', dpi=72)


#plot_map('output/conditions.shp')
