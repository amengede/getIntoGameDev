from config import *

def read_shader_src(filename):

    with open(filename, 'rb') as file:
        code = file.read()

    return code

def create_shader_module(device, filename):

    code = read_shader_src(filename)

    createInfo = VkShaderModuleCreateInfo(
        sType=VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
        codeSize=len(code),
        pCode=code
    )
    return vkCreateShaderModule(
        device = device, pCreateInfo = createInfo, pAllocator = None
    )