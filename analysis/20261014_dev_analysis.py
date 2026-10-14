import pandas as pd
import scipy.ndimage as ndi
import skimage
from oic_toolkit.display import merge_images

# from oic_toolkit.display import merge_images
from shared import core

img = core.read_image_from_slide("../data/dataset01/260493.svs")

sub_img = img[0:9500, 0:13500]

sub_img = ndi.median_filter(sub_img, size=3)

# Identify the adipose tissue
adipose_mask = sub_img > 240

adipose_mask = skimage.segmentation.clear_border(adipose_mask)

adipose_mask = skimage.morphology.remove_small_holes(adipose_mask, max_size=150)
adipose_mask = skimage.morphology.remove_small_objects(adipose_mask, max_size=500)

overlay = skimage.segmentation.mark_boundaries(sub_img, adipose_mask, color=(1, 0, 1))

# Create output labels
labels = skimage.measure.label(adipose_mask)

# Measure and export data to CSV
data = skimage.measure.regionprops_table(labels, properties=("area",))

df = pd.DataFrame(data)
df.to_csv("test.csv", index=False)

# Create output image
merged = merge_images(
    sub_img, skimage.color.label2rgb(labels, bg_color="black"), mode="blend"
)

skimage.io.imsave("test_overlay.png", merged)
