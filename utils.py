import os

from config import TEMP_DIR_NAME


def delete_temp_files():
    if os.path.exists(TEMP_DIR_NAME):
        file_names = os.listdir(TEMP_DIR_NAME)

        for file in file_names:
            if file.endswith(".json"):
                full_path = os.path.join(TEMP_DIR_NAME, file)
                delete_old_file_if_exist(full_path)


def delete_old_file_if_exist(path):
    if os.path.exists(path):
        os.remove(path)


def create_temp_if_not_exist():
    if not os.path.exists(TEMP_DIR_NAME):
        os.mkdir(TEMP_DIR_NAME)
