#statically load vulkan library
from vulkan import *

"""
 Statically linking the prebuilt header from the lunarg sdk will load
 most functions, but not all.
 
 Functions can also be dynamically loaded, using the call
 
 PFN_vkVoidFunction vkGetInstanceProcAddr(
    VkInstance                                  instance,
    string                                      pName);

 or

 PFN_vkVoidFunction vkGetDeviceProcAddr(
	VkDevice                                    device,
	string                                      pName);

	We will look at this later, once we've created an instance and device.
"""

import glfw
import glfw.GLFW as GLFW_CONSTANTS