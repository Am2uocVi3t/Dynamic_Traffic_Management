import os
from PIL import Image
from utils.message import *

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
REFERENCE_FOLDER = os.path.join(BASE_DIR, "data", "reference_images")


def split_and_save(image_path, time_of_day):
    image = Image.open(image_path)
    width, height = image.size

    if width == 512:
        left_image = image.crop((0, 0, width // 2, height))
        right_image = image.crop((width // 2, 0, width, height))

        base_name = os.path.basename(image_path).split("_")[1].split(".")[0]

        left_path = os.path.join(os.path.dirname(image_path), f"{base_name}_{time_of_day}_left.jpg")
        right_path = os.path.join(os.path.dirname(image_path), f"{base_name}_{time_of_day}_right.jpg")

        left_image.save(left_path)
        right_image.save(right_path)

        os.remove(image_path)
        print_success(f"Success: {image_path} -> {left_path}, {right_path}")
        print_success(f"Removed: {image_path}")
    else:
        print_warning(f"{image_path} is not 512x288")


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
