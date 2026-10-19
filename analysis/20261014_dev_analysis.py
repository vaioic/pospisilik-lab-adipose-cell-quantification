from shared import core

core.process_slide(
    "../data/dataset01/260493.svs",
    "../processed/2026-10-15 Dev",
    min_cell_size=1000,
    max_cell_size=None,
    roi=(5000, 9500, 9000, 13500),
)

# import scipy.ndimage as ndi
# import skimage
# from oic_toolkit.display import merge_images

# # from oic_toolkit.display import merge_images
# from shared import core

# img = core.read_image_from_slide("../data/dataset01/260493.svs")

# sub_img = img[5000:9500, 9000:13500]

# sub_img = ndi.median_filter(sub_img, size=3)

# # Identify the adipose tissue
# adipose_mask = sub_img > 240

# adipose_mask = skimage.segmentation.clear_border(adipose_mask)

# adipose_mask = skimage.morphology.remove_small_holes(adipose_mask, max_size=150)
# adipose_mask = skimage.morphology.remove_small_objects(adipose_mask, max_size=500)

# adipose_mask_large = skimage.morphology.remove_small_objects(
#     adipose_mask, max_size=50000
# )

# adipose_mask = adipose_mask ^ adipose_mask_large

# # Create output labels
# labels = skimage.measure.label(adipose_mask)

# # # Measure and export data to CSV
# # data = skimage.measure.regionprops_table(labels, properties=("area",))

# # import pandas as pd
# # df = pd.DataFrame(data)
# # df.to_csv("test.csv", index=False)

# # Create output image

# # Downsample the images
# ds_sub_img = skimage.transform.rescale(sub_img, 0.25)
# ds_labels = skimage.transform.rescale(
#     labels, 0.25, order=0, anti_aliasing=False, preserve_range=True
# )

# merged = merge_images(
#     ds_sub_img, skimage.color.label2rgb(ds_labels, bg_color="black"), mode="blend"
# )

# from matplotlib import pyplot as plt

# plt.imshow(merged)
# plt.show()

# # skimage.io.imsave("test_overlay.png", merged)
