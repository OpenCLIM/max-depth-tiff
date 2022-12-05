import os
import rasterio as rio
from citycatio import output
from rasterio.plot import show
import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from rasterio.fill import fillnodata
from matplotlib.colors import ListedColormap
from glob import glob

# Set up paths
data_path = os.getenv('DATA_PATH', '/data')
inputs_path = os.path.join(data_path, 'inputs')
outputs_path = os.path.join(data_path, 'outputs')
print('Original method:', outputs_path)
outputs_path_ = data_path + '/' + 'outputs'
print('Alt method:', outputs_path_)
if not os.path.exists(outputs_path):
     os.mkdir(outputs_path_)

# Create geotiff
geotiff_path = os.path.join(outputs_path, 'max_depth.tif')
netcdf_path = os.path.join(outputs_path, 'R1C1_SurfaceMaps.nc')

archive = glob(inputs_path + "/**/*.csv", recursive = True)

for i in range(0,len(archive)):
    file_path = os.path.splitext(archive[i])
    filename=file_path[0].split("\\")
    output.to_geotiff(os.path.join(inputs_path, filename[-1] + '.csv'), geotiff_path, srid=27700)

# Create depth map
print('Creating depth maps')
with rio.open(geotiff_path) as ds:
    print('Opened geotiff')
    f, ax = plt.subplots()

    cmap = ListedColormap(['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c',
                           '#08306b', 'black'])
    cmap.set_bad(color='lightgrey')
    cmap.colorbar_extend = 'max'

    im = show(ds, ax=ax, cmap=cmap, vmin=0, vmax=1).get_images()[0]

    ax.set_xticks([])
    ax.set_yticks([])

    ax.add_artist(ScaleBar(1, frameon=False))
    f.colorbar(im, label='Water Depth (m)')
    print('Saving max_depth.png')

    #f.savefig(os.path.join('/data/outputs/max_depth.png'), dpi=200, bbox_inches='tight')

    # Create interpolated GeoTIFF
    print('Doing interpolated image')
    with rio.open(os.path.join(outputs_path, 'max_depth_interpolated.tif'), 'w', **ds.profile) as dst:
        dst.write(fillnodata(ds.read(1), mask=ds.read_masks(1)), 1)

print('Completed')