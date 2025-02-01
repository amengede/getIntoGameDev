from config import *
import vklogging

class DescriptorSetLayoutData:


    def __init__(self):

        self.count = 0
        self.indices = []
        self.types = []
        self.counts = []
        self.stages = []

def make_descriptor_set_layout(device, bindings: DescriptorSetLayoutData):

    layoutBindings = []

    for i in range(bindings.count):

        """
        typedef struct VkDescriptorSetLayoutBinding {
            uint32_t              binding;
            VkDescriptorType      descriptorType;
            uint32_t              descriptorCount;
            VkShaderStageFlags    stageFlags;
            const VkSampler*      pImmutableSamplers;
        } VkDescriptorSetLayoutBinding;
        """
        
        layoutBinding = VkDescriptorSetLayoutBinding(
            binding = bindings.indices[i],
            descriptorType = bindings.types[i],
            descriptorCount = bindings.counts[i],
            stageFlags = bindings.stages[i]
        )

        layoutBindings.append(layoutBinding)
    
    """
    typedef struct VkDescriptorSetLayoutCreateInfo {
        VkStructureType                        sType;
        const void*                            pNext;
        VkDescriptorSetLayoutCreateFlags       flags;
        uint32_t                               bindingCount;
        const VkDescriptorSetLayoutBinding*    pBindings;
    } VkDescriptorSetLayoutCreateInfo;
    """

    layoutInfo = VkDescriptorSetLayoutCreateInfo(
        bindingCount = bindings.count,
        pBindings = layoutBindings
    )

    try:
        return vkCreateDescriptorSetLayout(device, layoutInfo, None)
    except:
        vklogging.logger.print("Failed to create Descriptor Set Layout")
        return None

def make_descriptor_pool(device, size: int, bindings: DescriptorSetLayoutData):

    poolSizes = []
    """
    typedef struct VkDescriptorPoolSize {
        VkDescriptorType    type;
        uint32_t            descriptorCount;
    } VkDescriptorPoolSize;
    """

    for _type in bindings.types:

        poolSize = VkDescriptorPoolSize(
            type = _type,
            descriptorCount = size
        )

        poolSizes.append(poolSize)
    
    """
        typedef struct VkDescriptorPoolCreateInfo {
            VkStructureType                sType;
            const void*                    pNext;
            VkDescriptorPoolCreateFlags    flags;
            uint32_t                       maxSets;
            uint32_t                       poolSizeCount;
            const VkDescriptorPoolSize*    pPoolSizes;
        } VkDescriptorPoolCreateInfo;
    """

    poolInfo = VkDescriptorPoolCreateInfo(
        poolSizeCount = len(poolSizes),
        pPoolSizes = poolSizes,
        maxSets = size
    )

    try:
        return vkCreateDescriptorPool(device, poolInfo, None)
    except:
        vklogging.logger.print("Failed to make descriptor pool")
        return None

def allocate_descriptor_set(device, descriptorPool, descriptorSetLayout):

    """
        typedef struct VkDescriptorSetAllocateInfo {
			VkStructureType                 sType;
			const void*                     pNext;
			VkDescriptorPool                descriptorPool;
			uint32_t                        descriptorSetCount;
			const VkDescriptorSetLayout*    pSetLayouts;
		} VkDescriptorSetAllocateInfo;
    """

    allocationInfo = VkDescriptorSetAllocateInfo(
        descriptorPool = descriptorPool, descriptorSetCount = 1, 
        pSetLayouts = [descriptorSetLayout,]
    )

    try:
        return vkAllocateDescriptorSets(device, allocationInfo)[0]
    except:
        vklogging.logger.print("Failed to allocate a descriptor set")
        return None