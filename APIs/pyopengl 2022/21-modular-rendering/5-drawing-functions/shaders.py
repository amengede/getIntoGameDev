from config import *
from shader_constants import *
import buffer
import model

def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Create a shader.

        Parameters:

            vertex_filepath: filepath of the vertex source code

            fragment_filepath: filepath of the fragment source code
    """

    with open(vertex_filepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.readlines()

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))

    return shader

class Shader:
    def __init__(self, pipeline_type: int):

        self.uniform_locations = {}

        self.shader = create_shader(
            VERTEX_MODULE_FILENAMES[pipeline_type], 
            FRAGMENT_MODULE_FILENAMES[pipeline_type])

        glUseProgram(self.shader)

        if pipeline_type not in UNIFORM_NAMES:
            return

        for uniform_type, uniform_name in UNIFORM_NAMES[pipeline_type].items():
            self.uniform_locations[uniform_type] =\
                    glGetUniformLocation(self.shader, uniform_name)

    def use(self) -> None:
        glUseProgram(self.shader)

    def bind_mat4(self, uniform_type: int, mat: np.ndarray) -> None:
        glUniformMatrix4fv(self.uniform_locations[uniform_type],
                           1, GL_FALSE, mat)

    def bind_int(self, uniform_type: int, i: int) -> None:
        glUniform1i(self.uniform_locations[uniform_type], i)

    def bind_float(self, uniform_type: int, f: float) -> None:
        glUniform1f(self.uniform_locations[uniform_type], f)

    def bind_vec3(self, uniform_type: int, v: np.ndarray) -> None:
        glUniform3fv(self.uniform_locations[uniform_type], 1, v)

    def bind_vec4(self, uniform_type: int, v: np.ndarray) -> None:
        glUniform4fv(self.uniform_locations[uniform_type], 1, v)

    def destroy(self) -> None:
        glDeleteProgram(self.shader)

