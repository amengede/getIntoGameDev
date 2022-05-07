from config import *
import scene
import engine

class App:
    """
        Calls high level control functions (handle input, draw scene etc)
    """

    def __init__(self):

        pg.init()
        self.screenWidth = 640
        self.screenHeight = 480
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.set_mode((self.screenWidth, self.screenHeight), pg.OPENGL|pg.DOUBLEBUF)
        pg.mouse.set_pos((self.screenWidth // 2,self.screenHeight // 2))
        pg.mouse.set_visible(False)
        self.graphicsEngine = engine.Engine(self.screenWidth, self.screenHeight)
        self.scene = scene.Scene()

        self.lastTime = pg.time.get_ticks()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.lightCount = 0

        self.mainLoop()
    
    def mainLoop(self):

        running = True
        while (running):
            #events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
                if (event.type == pg.KEYDOWN):
                    if (event.key == pg.K_ESCAPE):
                        running = False
            self.handleKeys()
            self.handleMouse()
            self.scene.update()
            
            #render
            self.graphicsEngine.renderScene(self.scene)

            #timing
            self.calculateFramerate()
        self.quit()
    
    def calculateFramerate(self):

        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = max(1,int(1000.0 * self.numFrames/delta))
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(1,framerate))
            self.graphicsEngine.adaptResolution(framerate)
        self.numFrames += 1
    
    def handleKeys(self):
        """
            handle the current key state
        """

        rate = self.frameTime / 16

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.scene.move_player(0.1 * rate, 0)
        elif keys[pg.K_a]:
            self.scene.move_player(0, -0.1 * rate)
        elif keys[pg.K_s]:
            self.scene.move_player(-0.1 * rate, 0)
        elif keys[pg.K_d]:
            self.scene.move_player(0, 0.1 * rate)
    
    def handleMouse(self):

        (x,y) = pg.mouse.get_pos()
        theta_increment = self.frameTime * 0.05 * ((self.screenWidth // 2) - x)
        phi_increment = self.frameTime * 0.05 * ((self.screenHeight // 2) - y)
        self.scene.spin_player((theta_increment, phi_increment))
        pg.mouse.set_pos((self.screenWidth // 2,self.screenHeight // 2))

    def quit(self):
        #self.graphicsEngine.destroy()
        pg.quit()