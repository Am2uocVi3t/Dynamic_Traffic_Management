import os
import numpy as np

import utils.split_image
from utils.message import *
import cv2

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
REFERENCE_FOLDER = os.path.join(BASE_DIR, "data", "reference_images")


point_part_2 = np.array([(445, 285), (80, 0), (510, 0), (510, 283)], np.int32)
point_part_1 = np.array([(476, 286), (87, 2), (2, 1), (2, 285)], np.int32)


def split_and_save(image_path, time_of_day):
    part_1, part_2 = utils.split_image.split_image(image_path)
    base_name = os.path.basename(image_path).split("_")[1].split(".")[0]

    left_path = os.path.join(os.path.dirname(image_path), f"{base_name}_{time_of_day}_left.jpg")
    right_path = os.path.join(os.path.dirname(image_path), f"{base_name}_{time_of_day}_right.jpg")

    # Lưu ảnh bằng OpenCV
    cv2.imwrite(left_path, part_1)
    cv2.imwrite(right_path, part_2)

    # Xóa ảnh gốc
    os.remove(image_path)
    print_success(f"Success: {image_path} -> {left_path}, {right_path}")
    print_success(f"Removed: {image_path}")


def process_reference_images(reference_folder):
    for flow_type in ["low_flow", "mid_flow", "high_flow"]:
        for time_of_day in ["day", "night"]:
            folder_path = os.path.join(reference_folder, flow_type, time_of_day)
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.endswith(".jpg") and "left" not in filename and "right" not in filename:
                        image_path = os.path.join(folder_path, filename)
                        split_and_save(image_path, time_of_day)


if __name__ == '__main__':
    process_reference_images(REFERENCE_FOLDER)
