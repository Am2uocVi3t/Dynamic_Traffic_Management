import cv2
import numpy as np
from utils.message import *

point_part_2 = np.array([(445, 285), (80, 0), (510, 0), (510, 283)], np.int32)
point_part_1 = np.array([(476, 286), (87, 2), (2, 1), (2, 285)], np.int32)


def split_image(image_path):
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    if width == 512:
        image = cv2.imread(image_path)
        if image is None:
            print_error(f"Error: Could not load image {image_path}")
            return None, None

        mask1 = np.zeros(image.shape[:2], dtype=np.uint8)
        mask2 = np.zeros(image.shape[:2], dtype=np.uint8)

        cv2.fillPoly(mask1, [point_part_1], 255)
        cv2.fillPoly(mask2, [point_part_2], 255)

        left_image = cv2.bitwise_and(image, image, mask=mask1)
        right_image = cv2.bitwise_and(image, image, mask=mask2)

        return left_image, right_image
