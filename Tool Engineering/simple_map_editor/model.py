from config import *

class GameObject:


    def __init__(self, rect: QRectF, _type: int):

        self.rect = rect
        self._type = _type