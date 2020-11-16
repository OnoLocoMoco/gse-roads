# try to build a new map

import geopandas as gpd
import matplotlib.pyplot as plt




#bounds = gpd.read_file('gsenm-bounds/gsenm-bounds.shp')
roads = gpd.read_file('roads/GSENM_roads.shp')
#conditions = gpd.read_file('output/conditions.shp')






fig, ax = plt.subplots(figsize=(8,8))

ax.set_aspect('equal')

#bounds.plot(ax=ax, color='white', edgecolor='brown', linewidth=2);
roads.plot(ax=ax, color='gray');
#conditions.plot(ax=ax, linewidth =2, color="blue")
#plt.title(
#    "bounds", fontsize=12)
plt.axis('off')
plt.savefig('gsenm-roads.png', dpi=72)
#plt.show()
