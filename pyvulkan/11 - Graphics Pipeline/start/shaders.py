from config import *

def read_shader_src(filename):

    with open(filename, 'rb') as file:
        code = file.read()

    return code