import os
import numpy as np
from PIL import Image
from utils.message import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "data", "input_images")
REFERENCE_FOLDER = os.path.join(BASE_DIR, "data", "reference_images")

REFERENCE_FOLDER = os.path.abspath(REFERENCE_FOLDER)
INPUT_FOLDER = os.path.abspath(INPUT_FOLDER)


def split_image(image_path):
    image = Image.open(image_path)
    width, height = image.size

    left_lane_path = "left_image.jpg"
    right_lane_path = "right_image.jpg"

    image.crop((0, 0, width // 2, height)).save(left_lane_path)
    image.crop((width // 2, 0, width, height)).save(right_lane_path)

    return left_lane_path, right_lane_path


def compare_images(input_path, ref_path):
    input_image = Image.open(input_path).convert("L")
    ref_image = Image.open(ref_path).convert("L")

    input_image = input_image.resize(ref_image.size)

    input_image_arr = np.array(input_image)
    ref_image_arr = np.array(ref_image)

    MSE = np.mean((input_image_arr - ref_image_arr) ** 2)
    score = max(100 - MSE / 10, 0)

    return round(score, 2)


def determine_traffic_level(input_image):
    def normalize_scores(score_dict):
        total = sum(score_dict.values())
        return {key: round((value / total) * 100, 2) if total > 0 else 0 for key, value in score_dict.items()}

    reference_images = {
        "low": os.path.join(REFERENCE_FOLDER, "low_flow.jpg"),
        "mid": os.path.join(REFERENCE_FOLDER, "mid_flow.jpg"),
        "high": os.path.join(REFERENCE_FOLDER, "high_flow.jpg")
    }

    left_image, right_image = split_image(input_image)
    scores = {"left": {}, "right": {}}

    for level, ref_image in reference_images.items():
        if os.path.exists(ref_image):
            scores["left"][level] = compare_images(left_image, ref_image)
            scores["right"][level] = compare_images(right_image, ref_image)  # code so sánh bức ảnh input và ảnh mẫu

    left_scores = normalize_scores(scores["left"])
    right_scores = normalize_scores(scores["right"])

    left_flow = max(left_scores, key=left_scores.get)
    right_flow = max(right_scores, key=right_scores.get)

    return left_flow, right_flow, left_scores, right_scores


if __name__ == '__main__':
    input_image = os.path.abspath(os.path.join(INPUT_FOLDER, "input_image.jpg"))  # Cần thêm tên đường dẫn file ảnh input

    if not os.path.exists(input_image):
        print_error("Error input image")
    else:

        left_flow, right_flow, left_score, right_score = determine_traffic_level(input_image)
        print_warning("Left Lane Flow: " + left_flow.upper())
        print_warning("Left Lane Score: " + str(left_score))
        print_warning("Right Lane Score: " + right_flow.upper())
        print_warning("Right Lane Score: " + str(right_score))
