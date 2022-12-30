from config import *

def get_pos_color_binding_description():
    """
        Get the input binding description for a
        (vec2 pos, vec3 color) vertex format
    """

    """
    typedef struct VkVertexInputBindingDescription {
        uint32_t             binding;
        uint32_t             stride;
        VkVertexInputRate    inputRate;
    } VkVertexInputBindingDescription;
    """

    return VkVertexInputBindingDescription(
        binding = 0, stride = 20, inputRate = VK_VERTEX_INPUT_RATE_VERTEX
    )

def get_pos_color_attribute_descriptions():
    """
        Get the attribute descriptions for a
        (vec2 pos, vec3 color) vertex format
    """

    """
    typedef struct VkVertexInputAttributeDescription {
        uint32_t    location;
        uint32_t    binding;
        VkFormat    format;
        uint32_t    offset;
    } VkVertexInputAttributeDescription;
    """

    return (
        VkVertexInputAttributeDescription(
            binding = 0, location = 0,
            format = VK_FORMAT_R32G32_SFLOAT,
            offset = 0
        ),
        VkVertexInputAttributeDescription(
            binding = 0, location = 1,
            format = VK_FORMAT_R32G32B32_SFLOAT,
            offset = 8
        )
    )