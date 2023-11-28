import pygame as pg
from OpenGL.GL import *

class App:
    """
        For now, the app will be handling everything.
        Later on we'll break it into subcomponents.
    """


    def __init__(self):
        """ Initialise the program """
        
        self._set_up_pygame()
        
        self._set_up_timer()

        self._set_up_opengl()
    
    def _set_up_pygame(self) -> None:
        """
            Initialize and configure pygame.
        """

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((640,480), pg.OPENGL|pg.DOUBLEBUF)
    
    def _set_up_timer(self) -> None:
        """
            Set up the app's timer.
        """

        self.clock = pg.time.Clock()

    def _set_up_opengl(self) -> None:
        """
            Configure any desired OpenGL options
        """

        glClearColor(0.1, 0.2, 0.2, 1)

    def run(self) -> None:
        """ Run the app """

        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT)
            pg.display.flip()

            #timing
            self.clock.tick(60)

    def quit(self) -> None:
        """ cleanup the app, run exit code """
        pg.quit()

if __name__ == "__main__":
    myApp = App()
    myApp.run()
    myApp.quit()