import os


def create_folder_if_not_exist(folder_name):
    isExist = os.path.exists(folder_name)
    if not isExist:
        os.makedirs(folder_name)
