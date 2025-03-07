import os
import numpy as np
from PIL import Image
from datetime import datetime
from utils.message import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "data", "input_images")
REFERENCE_FOLDER = os.path.join(BASE_DIR, "data", "reference_images")

REFERENCE_FOLDER = os.path.abspath(REFERENCE_FOLDER)
INPUT_FOLDER = os.path.abspath(INPUT_FOLDER)


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
            ref_image = Image.open(ref_image_path).convert("L")

            score = compare_images(input_image, ref_image)

            if score > best_score:
                best_score = score
                best_ref_image = ref_image_path

    if best_ref_image:
        print_success(f"Best Image in {flow_type} and {time_of_day} is: {best_ref_image} | Score: {best_score}")
        return best_ref_image
    else:
        print_warning(f"Can not find valid Image in: {ref_path}")

    print_error("Invalid reference image")
    return None


def classify_time_of_day(filename):
    try:
        timestamp = int(filename.split("_")[1].split(".")[0])
        hour = datetime.fromtimestamp(timestamp / 1000).hour
        if 6 <= hour < 18:
            return "day"
        else:
            return "night"

    except Exception as e:
        print_error(e)
        return None


def split_image(image_path):
    image = Image.open(image_path)
    width, height = image.size

    left_image = image.crop((0, 0, width // 2, height))
    right_image = image.crop((width // 2, 0, width, height))

    return left_image, right_image


def compare_images(input_path, ref_path):

    if isinstance(ref_path, str):
        ref_image = Image.open(ref_path).convert("L")
    else:
        ref_image = ref_path.convert("L")

    input_image = input_path.convert("L")
    input_image = input_image.resize(ref_image.size)

    input_image_arr = np.array(input_image)
    ref_image_arr = np.array(ref_image)

    MSE = np.mean((input_image_arr - ref_image_arr) ** 2)
    score = max(100 - MSE / 10, 0)

    return round(score, 2)


def determine_traffic_level(input_image, time_of_day):
    def normalize_scores(score_dict):
        total = sum(score_dict.values())
        return {key: round((value / total) * 100, 2) if total > 0 else 0 for key, value in score_dict.items()}

    left_image, right_image = split_image(input_image)
    scores = {
        "left": {},
        "right": {}
    }

    for level in ["low", "mid", "high"]:
        ref_left = find_reference_image(f"{level}_flow", time_of_day, "left", left_image)
        ref_right = find_reference_image(f"{level}_flow", time_of_day, "right", right_image)

        if ref_left:
            scores["left"][level] = compare_images(left_image, ref_left)

        if ref_right:
            scores["right"][level] = compare_images(right_image, ref_right)

    left_scores = normalize_scores(scores["left"])
    right_scores = normalize_scores(scores["right"])

    left_flow = max(left_scores, key=left_scores.get, default="unknown")
    right_flow = max(right_scores, key=right_scores.get, default="unknown")

    return left_flow, right_flow, left_scores, right_scores


if __name__ == '__main__':
    for filename in os.listdir(INPUT_FOLDER):
        if filename.lower().endswith(".jpg"):
            image_path = os.path.join(INPUT_FOLDER, filename)

            time_of_day = classify_time_of_day(filename)
            if time_of_day in ["day", "night"]:
                print_success("Processing: " + filename + " | Time: " + time_of_day)

                left_flow, right_flow, left_score, right_score = determine_traffic_level(image_path, time_of_day)

                print_warning("Left Lane Flow: " + left_flow + " | " + " Score: " + str(left_score))
                print_warning("Right Lane Flow: " + right_flow + " | " + " Score: " + str(right_score))
