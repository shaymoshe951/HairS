from PIL import Image

from auto1111_if import *

# Debug
drawing_mask_img = Image.open("C:/Users/Lab/Downloads/drawing_mask.png")
hair_img = Image.open("C:/Users/Lab/Downloads/hair_only.png")
cur_img = Image.open("C:/Users/Lab/Downloads/background_image.png")

modified_image = adding_hair_modification(VersImage.from_image(cur_img),
                                          VersImage.from_image(hair_img),
                                          VersImage.from_image(drawing_mask_img))

modified_image.image.show()
print("Done")
