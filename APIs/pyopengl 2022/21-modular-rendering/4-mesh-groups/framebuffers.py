from config import *

class Framebuffer:
    """
    Describes a collection of attachments for rendering.
    """

    def __init__(self, width: int, height: int, offscreen: bool = True):
        """
        Initialise a new Framebuffer.

        Parameters:

            width: requested width

            height: requested height

            offscreen: whether to render to an offscreen surface
        """

        if offscreen:
            self.FBO = glGenFramebuffers(1)
        else:
            self.FBO = 0

        self.color_attachments: list[int] = []
        self.depth_stencil_attachment = None
        self.width = width
        self.height = height

    def add_color_attachment(self) -> None:
        """
            Build a color attachment and add it as a render target.
        """

        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

        attachment = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, attachment)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,
            self.width, self.height,
            0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER,
                               GL_COLOR_ATTACHMENT0 + len(self.color_attachments),
                               GL_TEXTURE_2D, attachment, 0)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        self.color_attachments.append(attachment)

    def add_depth_stencil_attachment(self) -> None:
        """
            Build and add a depth/stencil buffer.
            Every framebuffer should have at most one depth/stencil attachment
        """

        if not self.depth_stencil_attachment is None:
            glDeleteRenderbuffers(1, (self.depth_stencil_attachment,))

        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)
        self.depth_stencil_attachment = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_stencil_attachment)
        glRenderbufferStorage(
            GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, self.width, self.height)
        glBindRenderbuffer(GL_RENDERBUFFER,0)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT,
                                  GL_RENDERBUFFER, self.depth_stencil_attachment)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def draw_to(self) -> None:

        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

    def read_from(self) -> None:

        for i,attachment in enumerate(self.color_attachments):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, attachment)

    def destroy(self) -> None:

        glDeleteFramebuffers(1, (self.FBO,))
        glDeleteTextures(len(self.color_attachments), self.color_attachments)
        glDeleteRenderbuffers(1, (self.depth_stencil_attachment,))

