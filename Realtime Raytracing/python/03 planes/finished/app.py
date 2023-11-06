from config import *
import engine
import scene

class App:
    """
        Calls high level control functions (handle input, draw scene etc)
    """

    def __init__(self):

        self.screenWidth = 800
        self.screenHeight = 600
        self.setupPygame()

        self.graphicsEngine = engine.Engine(self.screenWidth, self.screenHeight)
        self.scene = scene.Scene()

        self.setupTimer()

        self.mainLoop()
    
    def setupPygame(self) -> None:
        """ Set up pygame. """

        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.screenWidth, self.screenHeight), pg.OPENGL|pg.DOUBLEBUF)
    
    def setupTimer(self) -> None:
        """
            set up the framerate timer
        """

        self.lastTime = pg.time.get_ticks()
        self.currentTime = pg.time.get_ticks()
        self.numFrames = 0
        self.frameTime = 0
    
    def mainLoop(self) -> None:
        """ Run the program """

        running = True
        while (running):
            #events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
                if (event.type == pg.KEYDOWN):
                    if (event.key == pg.K_ESCAPE):
                        running = False
            
            #render
            self.graphicsEngine.renderScene(self.scene)

            #timing
            self.calculateFramerate()
        self.quit()
    
    def calculateFramerate(self) -> None:
        """
            Calculate the framerate of the program.
        """

        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = max(1,int(1000.0 * self.numFrames/delta))
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(1,framerate))
        self.numFrames += 1

    def quit(self) -> None:
        """
            For some reason, the graphics engine's destructor throws weird errors.
        """
        #self.graphicsEngine.destroy()
        pg.quit()