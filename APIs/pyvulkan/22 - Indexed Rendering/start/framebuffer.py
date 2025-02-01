from config import *
import vklogging

class framebufferInput:


    def __init__(self):

        self.device = None
        self.renderpass = None
        self.swapchainExtent = None

def make_framebuffers(inputChunk, frames):

    for i,frame in enumerate(frames):

        attachments = [frame.image_view,]

        framebufferInfo = VkFramebufferCreateInfo(
            renderPass = inputChunk.renderpass,
            attachmentCount = 1,
            pAttachments = attachments,
            width = inputChunk.swapchainExtent.width,
            height = inputChunk.swapchainExtent.height,
            layers=1
        )

        try:
            frame.framebuffer = vkCreateFramebuffer(
                inputChunk.device, framebufferInfo, None
            )

            vklogging.logger.print(f"Made framebuffer for frame {i}")
            
        except:

            vklogging.logger.print(f"Failed to make framebuffer for frame {i}")
