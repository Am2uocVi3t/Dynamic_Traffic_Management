import os
import cv2
import numpy as np
from datetime import datetime

import utils.split_image
from utils.message import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "data", "input_images")
REFERENCE_FOLDER = os.path.join(BASE_DIR, "data", "reference_images")

REFERENCE_FOLDER = os.path.abspath(REFERENCE_FOLDER)
INPUT_FOLDER = os.path.abspath(INPUT_FOLDER)

point_part_2 = np.array([(445, 285), (80, 0), (510, 0), (510, 283)], np.int32)
point_part_1 = np.array([(476, 286), (87, 2), (2, 1), (2, 285)], np.int32)


def find_reference_image(flow_type, time_of_day, lane, input_image):
    ref_path = os.path.join(REFERENCE_FOLDER, flow_type, time_of_day)

    if not os.path.exists(ref_path):
        print_error("Reference folder not found: " + ref_path)
        return None

    best_score = -float("inf")
    best_ref_image = None

    for filename in os.listdir(ref_path):
        if filename.endswith(".jpg") and lane in filename:
            ref_image_path = os.path.join(ref_path, filename)
            ref_image = cv2.imread(ref_image_path, cv2.IMREAD_GRAYSCALE)

            if ref_image is None:
                continue

            score = compare_images(input_image, ref_image)

            if score > best_score:
                best_score = score
                best_ref_image = ref_image_path

    if best_ref_image:
        return best_ref_image
    else:
        print_warning(f"Cannot find valid Image in: {ref_path}")
        return None


def classify_time_of_day(filename):
    try:
        timestamp = int(filename.split("_")[1].split(".")[0])
        hour = datetime.fromtimestamp(timestamp / 1000).hour
        return "day" if 6 <= hour < 18 else "night"
    except Exception as e:
        print_error(e)
        return None


def compare_images(input_image, ref_image):
    if input_image is None or ref_image is None:
        return 0

    input_gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    ref_gray = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)

    ref_gray = cv2.resize(ref_gray, (input_gray.shape[1], input_gray.shape[0]))

    MSE = np.mean((input_gray - ref_gray) ** 2)
    score = max(100 - MSE, 0)
    return round(score, 2)


def determine_traffic_level(image_path, time_of_day):
    left_image, right_image = utils.split_image.split_image(image_path)

    if left_image is None or right_image is None:
        return "error", "error", {}, {}

    scores = {"left": {}, "right": {}}

    for level in ["low", "mid", "high"]:
        ref_left = find_reference_image(f"{level}_flow", time_of_day, "left", left_image)
        ref_right = find_reference_image(f"{level}_flow", time_of_day, "right", right_image)

        if ref_left and os.path.exists(ref_left):
            ref_left_image = cv2.imread(ref_left, cv2.IMREAD_GRAYSCALE)
            scores["left"][level] = compare_images(left_image, ref_left_image)

        if ref_right and os.path.exists(ref_right):
            ref_right_image = cv2.imread(ref_right, cv2.IMREAD_GRAYSCALE)
            scores["right"][level] = compare_images(right_image, ref_right_image)

    left_flow = max(scores["left"], key=scores["left"].get, default="unknown")
    right_flow = max(scores["right"], key=scores["right"].get, default="unknown")

    print(left_flow, right_flow, scores["left"], scores["right"])
    return left_flow, right_flow, scores["left"], scores["right"]


if __name__ == '__main__':
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith(".jpg"):
            image_path = os.path.join(INPUT_FOLDER, filename)
            time_of_day = classify_time_of_day(filename)

            if time_of_day in ["day", "night"]:
                print_success(f"Processing: {filename} | Time: {time_of_day}")
                left_flow, right_flow, left_score, right_score = determine_traffic_level(image_path, time_of_day)
                print_warning(f"Left Lane Flow: {left_flow} | Score: {left_score}")
                print_warning(f"Right Lane Flow: {right_flow} | Score: {right_score}")
