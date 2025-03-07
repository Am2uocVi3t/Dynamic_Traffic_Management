import os
from PIL import Image


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
REFERENCE_FOLDER = os.path.join(BASE_DIR, "data", "reference_images")


def split_and_save(image_path):
    image = Image.open(image_path)
    width, height = image.size

    left_image = image.crop((0, 0, width // 2, height))
    right_image = image.crop((width // 2, 0, width, height))

    left_image.save(image_path.replace(".jpg", "_left.jpg"))
    right_image.save(image_path.replace(".jpg", "_right.jpg"))


def process_reference_images(reference_folder):
    for flow_type in ["low_flow", "mid_flow", "high_flow"]:
        for time_of_day in ["day", "night"]:
            folder_path = os.path.join(reference_folder, flow_type, time_of_day)
            for filename in os.listdir(folder_path):
                if filename.endswith(".jpg"):
                    image_path = os.path.join(folder_path, filename)
                    split_and_save(image_path)


if __name__ == '__main__':
    process_reference_images(REFERENCE_FOLDER)