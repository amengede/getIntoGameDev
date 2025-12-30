from config import *

class SwapChainFrame:


    def __init__(self):
        
        self.image = None
        self.image_view = None
        self.framebuffer = None
        self.commandbuffer = None
        self.inFlight = None
        self.imageAvailable = None
        self.renderFinished = None