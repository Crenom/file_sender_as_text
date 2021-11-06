import requests
from engine import encoder_decoder, files_and_folders
from json import dumps
import os
from time import sleep
from requests_ntlm import HttpNtlmAuth
import configparser

input_folder = "input"
output_folder = "output"

# создание папок
files_and_folders.create_folder_if_not_exist(output_folder)
files_and_folders.create_folder_if_not_exist(input_folder)

config = configparser.ConfigParser()
config.read('config.ini')


def __read_in_chunks__(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def send_file_to_server(file_name, link):
    full_file_name = os.path.join(input_folder, file_name)

    chunk_size = 102400  # на сколько байт бьём файл
    # посчитаем сколько всего частей файла
    chunks = 0
    with open(full_file_name, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            chunks += 1  # всего частей файла

    # бьём файл на части и отсылаем
    with open(full_file_name, 'rb') as f:
        part = 1

        for chunk in __read_in_chunks__(f, chunk_size):
            byte_content = chunk
            base64_string = encoder_decoder.byte_content_to_base64_string(byte_content)
            raw_data = {
                "file_name": file_name,
                "part": part,
                "max": chunks,
                "value": base64_string
            }
            json_data = dumps(raw_data, indent=2)
            result_status = requests.post(link, json=json_data).status_code
            print(f'{part}/{chunks} {result_status}')
            part += 1


def get_request_with_ntlm():
    domain = config['NTLM']['Domain']
    login = config['NTLM']['Login']
    password = config['NTLM']['Password']

    try:
        requests.get('http://ya.ru',
                     auth=HttpNtlmAuth(domain + '\\' + login, password),
                     verify=False)
    except Exception:
        print('exception on response with ntlm')


def __get_part_of_part__(file_name, link, part):
    i = 1
    status_code = 200
    base64_string = ''
    while status_code != 404:
        part_of_part_link = f'{link}/get/{file_name}/{part}/{i}'
        response = requests.get(part_of_part_link, verify=False)
        status_code = response.status_code

        if status_code == 404:
            break

        base64_string += response.text
        print(f'{str(part)}.{i} - {file_name}')
        i += 1

    return base64_string


def get_file_from_server(file_name, link):
    # получаем сколько всего частей в файле
    response = requests.get(link + '/get/' + file_name, verify=False)
    while response.status_code != 200:
        print(f'error: status_code = {response.status_code}')
        sleep(5)
        get_request_with_ntlm()
        response = requests.get(link + '/get/' + file_name, verify=False)
    chunks = response.json()

    # получаем файл по частям
    full_file_name = os.path.join(output_folder, file_name)
    base64_string = ''
    for i in range(int(chunks)):
        part = i + 1
        part_link = f'{link}/get/{file_name}/{part}'
        response = requests.get(part_link, verify=False)
        status_code = response.status_code

        if status_code == 200:
            base64_string = response.text

        while status_code != 200:
            print(f'error: file_name={file_name}, part={part}, status_code={response.status_code}')
            sleep(3)
            get_request_with_ntlm()
            sleep(2)
            response = requests.get(part_link, verify=False)
            status_code = response.status_code
            if status_code == 403:
                base64_string = __get_part_of_part__(file_name, link, part)
                status_code = 200

        if status_code == 200:
            byte_content = encoder_decoder.base64_string_to_byte_content(base64_string)
            if part == 1:
                with open(full_file_name, "wb") as file:
                    file.write(byte_content)
            else:
                with open(full_file_name, "ab") as file:
                    file.write(byte_content)

            print(f'{part}/{chunks} - {file_name}')
        else:
            print(f'part={part}, response status code ="' + str(response.status_code) + '"')


if __name__ == "__main__":
    server = config['DEFAULT']['ServerAddress']
    # f_list = [  # 'm1.rar',
    #     'erdnt.7z'
    # ]
    # for file_n in f_list:
    #     print(f'started - {file_n}')
    #     get_file_from_server(file_n, server)
    #     print(f'fineshed - {file_n}')
    #     sleep(1)
    # print('123')

    # send_file_to_server('bbb.rar', server)
    # part_of_part = __get_part_of_part__('aaa.rar', server, 31)
    get_file_from_server('aaa.rar', server)
    print('123')