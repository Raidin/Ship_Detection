import numpy as np
import os

from matplotlib import pyplot as plt
from keras.models import model_from_json
from tqdm import tqdm
from PIL import Image
# Feature scaling import
# [0-1] Scaling
from sklearn.preprocessing import minmax_scale

def CropImage(img, x, y):
    area_study = np.arange(3 * 80 * 80).reshape(3, 80, 80).astype('float64')
    for i in range(80):
        for j in range(80):
            area_study[0][i][j] = img[0][y + i][x + j]
            area_study[1][i][j] = img[1][y + i][x + j]
            area_study[2][i][j] = img[2][y + i][x + j]

    area_study = area_study.reshape([-1, 3, 80, 80])
    area_study = area_study.transpose([0, 2, 3, 1])

    # area_study = area_study / 255.0
    # sys.stdout.write('\rX:{0} Y:{1}  '.format(x, y))
    return area_study

def CheckNearWindow(x, y, s, coordinates):
    result = True
    for e in coordinates:
        if x + s > e[0][0] and x - s < e[0][0] and y + s > e[0][1] and y - s < e[0][1]:
            result = False
    return result

# Before Display Detection Box Method
def DisplayBox(img, x, y, acc, thickness=1):
    # Left
    for i in range(80):
        for th in range(thickness):
            img[0][y + i][x - th] = 255
            img[1][y + i][x - th] = 0
            img[2][y + i][x - th] = 0

    # Right
    for i in range(80):
        for th in range(thickness):
            img[0][y + i][x + th + 80] = 255
            img[1][y + i][x + th + 80] = 0
            img[2][y + i][x + th + 80] = 0

    # Top
    for i in range(80):
        for th in range(thickness):
            img[0][y - th][x + i] = 255
            img[1][y - th][x + i] = 0
            img[2][y - th][x + i] = 0

    # Bottom
    for i in range(80):
        for th in range(thickness):
            img[0][y + th + 80][x + i] = 255
            img[1][y + th + 80][x + i] = 0
            img[2][y + th + 80][x + i] = 0

def LoadModel():
    # Load Network Model
    # network_arch = 'defaultNet'
    network_arch = 'AlexNet'
    json_file = open("model/{}/network_model.json".format(network_arch), "r")
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)

    # Load Trained Weight
    model.load_weights("model/{}/trained_weight.h5".format(network_arch))
    print("Loaded model from disk")

    return model

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

    picture_vector = np.array(picture_vector).astype('float64')
    picture_vector = minmax_scale(picture_vector, feature_range=(0, 1), axis=0)

    # Shape :: channel x hegith x widht
    picture_tensor = picture_vector.reshape([n_spectrum, height, width])

    return width, height, picture_tensor

def main():
    # Load Network Model
    model = LoadModel()

    data_dir = 'data/scenes'
    print os.listdir(data_dir)

    # Test Image list Load
    for idx, img_file in tqdm(enumerate(os.listdir(data_dir))):
        input_image = os.path.join(data_dir, img_file)
        width, height, picture_tensor = ReadImage(input_image, idx)

        # Window Sliding Stride
        step = 10
        # Predict Information List(X, Y Coordinate and Probability Value)
        coordinates = []

        # Window Sliding Processing Logic
        for y in tqdm(range(int((height - (80 - step)) / step))):
            for x in range(int((width - (80 - step)) / step)):
                area = CropImage(picture_tensor, x * step, y * step)
                result = model.predict(area)
                if result[0][1] > 0.95 and CheckNearWindow(x * step, y * step, 88, coordinates):
                    coordinates.append([[x * step, y * step], result])
                    # print 'Probability :: ', result[0][1]
                    if 0:
                        area = np.squeeze(area, axis=0)
                        plt.imshow(area)
                        plt.title('Probability :: {}'.format(result[0][1]))
                        plt.show()

        # display detection box
        picture_tensor = picture_tensor.transpose(1, 2, 0)
        plt.cla()
        plt.figure(figsize=(30, 30))
        plt.imshow(picture_tensor)
        for e in coordinates:
            # DisplayBox(picture_tensor, e[0][0], e[0][1], e[1][0][1])
            rect = plt.Rectangle((e[0][0], e[0][1]), 80, 80, fill=False, edgecolor=(1, 0, 0), linewidth=2.5)
            plt.gca().add_patch(rect)
            plt.gca().text(e[0][0], e[0][1], 'prob ::  {:.3f}'.format(e[1][0][1]),
                                bbox=dict(facecolor=(1, 0, 0), alpha=0.5), fontsize=9, color='white')

        plt.savefig('result/{}_image.png'.format(idx))


if __name__ == '__main__':
    main()
