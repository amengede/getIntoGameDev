"""
TODO: Install libraries!
If you haven't already, run the following commands:

pip install PyOpenGL PyOpenGL_accelerate
pip install numpy
pip install pyrr
pip install pygame
"""

#TODO: import pygame, give it the alias "pg"
import pygame as pg
#TODO: import everything from OpenGL.GL
from OpenGL.GL import *

#This tutorial series is going to be Object-Oriented.
class App:


    def __init__(self):
        """ Initialise the program """
        pg.init()
        """
            Task: tell Pygame which sort of OpenGL to run!
                Version: 3.3
                Profile: Core
        """
        major_version = 3 #Pygame uses the pg.GL_CONTEXT_MAJOR_VERSION flag
        minor_version = 3
        profile = 0         #TODO: ctrl+click on pg.GL_CONTEXT_PROFILE_MASK to
                            #search it and find a suitable value for profile.
        pg.display.gl_set_attribute()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    profile)
        
        self.screen_size = (640, 480)
        pg.display.set_mode(self.screen_size, pg.OPENGL|pg.DOUBLEBUF)
        """
            Here we use the pg.OPENGL flag to tell pygame we want our program 
            to use OpenGL, we also tell it to use a double buffered presentation mode.
        """
        self.clock = pg.time.Clock() #For controlling the frame rate of the game.
        
        """
            Task: Set the r,g,b,a values that OpenGL should refresh the screen
            with.

            hint: this is done by calling glClearColor
        """
        
        self.mainLoop()

    def mainLoop(self) -> None:
        """ Run the app """

        running = True
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
            #refresh screen
            """
                Task: Tell OpenGL to clear the color buffer

                hint: call glClear
            """
            
            pg.display.flip()

            #timing
            self.clock.tick(60)
        self.quit()

    def quit(self) -> None:
        """ cleanup the app, run exit code """
        pg.quit()

#This is the program-entry point. This if statement will be triggered
# when the file is run, but not if it's imported by another file.
if __name__ == "__main__":
    myApp = App()