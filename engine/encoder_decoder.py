from base64 import b64encode, b64decode

ENCODING = 'utf-8'


# https://stackoverflow.com/questions/37225035/serialize-in-json-a-base64-encoded-data

def byte_content_to_base64_string(byte_content):
    # base64 encode data
    # output: bytes
    base64_bytes = b64encode(byte_content)

    # decode these bytes to text
    # output: string (in utf-8)
    base64_string = base64_bytes.decode(ENCODING)

    return base64_string


def base64_string_to_byte_content(base64_string):
    base64_bytes = base64_string.encode(ENCODING)
    byte_content = b64decode(base64_bytes)

    return byte_content
