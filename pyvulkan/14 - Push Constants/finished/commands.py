from config import *
import queue_families
import frame

class commandPoolInputChunk:


    def __init__(self):

        self.device = None
        self.physicalDevice = None
        self.surface = None
        self.instance = None

class commandbufferInputChunk:


    def __init__(self):

        self.device = None
        self.commandPool = None
        self.frames = None

def make_command_pool(inputChunk, debug):

    queueFamilyIndices = queue_families.find_queue_families(
        device = inputChunk.physicalDevice,
        instance = inputChunk.instance,
        surface = inputChunk.surface,
        debug = debug
    )

    poolInfo = VkCommandPoolCreateInfo(
        queueFamilyIndex=queueFamilyIndices.graphicsFamily,
        flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT
    )

    try:
        commandPool = vkCreateCommandPool(
            inputChunk.device, poolInfo, None
        )

        if debug:
            print(f"Created command pool")
        
        return commandPool
    except:
        if debug:
            print(f"Failed to create command pool")
        
        return None

def make_command_buffers(inputChunk, debug):

    allocInfo = VkCommandBufferAllocateInfo(
        commandPool = inputChunk.commandPool,
        level = VK_COMMAND_BUFFER_LEVEL_PRIMARY,
        commandBufferCount = 1
    )

    #Make a command buffer for each frame
    for i,frame in enumerate(inputChunk.frames):

        try:
            frame.commandbuffer = vkAllocateCommandBuffers(inputChunk.device, allocInfo)[0]

            if debug:
                print(f"Allocated command buffer for frame {i}")
        except:
            if debug:
                print(f"Failed to allocate command buffer for frame {i}")
    
    try:
        commandbuffer = vkAllocateCommandBuffers(inputChunk.device, allocInfo)[0]

        if debug:
            print(f"Allocated main command buffer")
        
        return commandbuffer
    except:
        if debug:
            print(f"Failed to allocate main command buffer")
        
        return None