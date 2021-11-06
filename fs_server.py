import json
import os
import linecache
import re

from flask import Flask, request, jsonify

from engine import encoder_decoder

# https://flask-russian-docs.readthedocs.io/ru/latest/quickstart.html
# http://blog.luisrei.com/articles/flaskrest.html

app = Flask(__name__)
output_folder = "output"  # сюда попадает файл
input_folder = "input"  # отсюда берём файлы для передачи
tmp_folder = "tmp"  # сюда конвертируются файлы в base64

chunk_size = 102400  # на сколько байт бьём файл


@app.route('/', methods=['POST'])
def upload_file_to_server():
    if request.headers['Content-Type'] == 'application/json':
        try:
            json_data = json.loads(request.json)
            file_name = json_data["file_name"]
            part = json_data["part"]
            byte_content = encoder_decoder.base64_string_to_byte_content(json_data["value"])

            full_file_name = os.path.join(output_folder, file_name)
            if part == 1:
                with open(full_file_name, "wb") as file:
                    file.write(byte_content)
            else:
                with open(full_file_name, "ab") as file:
                    file.write(byte_content)
            return "JSON Message: " + json.dumps(request.json)
        except Exception as e:
            return "Exception " + str(e)

    else:
        return "415 Unsupported Media Type", 415


# Получение списка файлов из папки input
@app.route('/get', methods=['GET'])
def get_filenames():
    onlyfiles = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
    return jsonify(onlyfiles), 200


# получение количества частей файла и сохранение приобразованного файла в tmp дирректории
@app.route('/get/<file_name>', methods=['GET'])
def get_chunks(file_name):
    try:
        full_file_name = os.path.join(input_folder, file_name)
        full_tmp_file_name = os.path.join(tmp_folder, file_name + '.tmp')

        with open(full_tmp_file_name, 'w') as tmp_f:
            # считаем кол-во частей
            chunks = 0
            with open(full_file_name, 'rb') as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    chunks += 1  # всего частей файла

                    # сохраняем часть в tmp
                    part = encoder_decoder.byte_content_to_base64_string(data)
                    tmp_f.write(part + '\n')

        return jsonify(chunks), 200
    except Exception as e:
        return str(e), 500


# Получение части файла кодированного в base64
@app.route('/get/<file_name>/<int:part>', methods=['GET'])
def get_file_part(file_name, part):
    try:
        full_tmp_file_name = os.path.join(tmp_folder, file_name + '.tmp')

        base64_part = re.sub('\n$', '', linecache.getline(full_tmp_file_name, int(part)))
        if base64_part == '':
            return 'part not found', 404
        return base64_part, 200
    except Exception as e:
        return str(e), 500


# Получение части от части файла, которая кодирована в base64
@app.route('/get/<file_name>/<int:part>/<int:part_part>', methods=['GET'])
def get_part_of_part(file_name, part, part_part):
    part_size = 1000
    try:
        file_part = get_file_part(file_name, part)[0]

        prev_part_part = (part_part - 1) * part_size
        part_of_part = file_part[prev_part_part: part_part * part_size]
        if part_of_part == '':
            return 'part not found', 404
        return part_of_part, 200
    except Exception as e:
        str(e), 500


@app.route('/test', methods=['GET'])
def test():
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
