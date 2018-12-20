import os
import numpy as np
from PIL import Image
from tqdm import tqdm


def ReadImage(image_path, idx):
    image = Image.open(image_path)
    pix = image.load()
    n_spectrum = 3
    width = image.size[0]
    height = image.size[1]
    # creat vector
    picture_vector = []
    for chanel in range(n_spectrum):
        for y in range(height):
            for x in range(width):
                picture_vector.append(pix[x, y][chanel])

    picture_vector = np.array(picture_vector).astype('uint8')
    picture_tensor = picture_vector.reshape([n_spectrum, height, width]).transpose(1, 2, 0)
    picture_tensor = picture_tensor.transpose(2, 0, 1)
    return picture_tensor


data_dir = 'data/scenes'
print os.listdir(data_dir)

for idx, img_file in tqdm(enumerate(os.listdir(data_dir))):
    input_image = os.path.join(data_dir, img_file)
    ReadImage(input_image, idx)