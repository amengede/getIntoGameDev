from config import *
import model
import view

class GameApp:

    def __init__(self):

        self.renderer = view.GameRenderer()

        self.scene = model.Scene()

        pg.mouse.set_visible(False)

        self.lastTime = 0
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0

    def mainLoop(self):

        result = RETURN_ACTION_CONTINUE
        while result == RETURN_ACTION_CONTINUE:
            #check events
            for event in pg.event.get():
                if (event.type == pg.KEYDOWN and event.key==pg.K_ESCAPE):
                    result = RETURN_ACTION_EXIT
            self.handleKeys()
            self.handleMouse()

            #update objects
            self.scene.update(self.frameTime / 16.6)

            #render
            self.renderer.render(self.scene)

            #timing
            self.showFrameRate()

        return result

    def handleKeys(self):

        keys = pg.key.get_pressed()

        if keys[pg.K_w]:
            self.scene.move_player(direction = 0, amount = 0.005*self.frameTime)
        elif keys[pg.K_a]:
            self.scene.move_player(direction = 90, amount = 0.005*self.frameTime)
        elif keys[pg.K_s]:
            self.scene.move_player(direction = 180, amount = 0.005*self.frameTime)
        elif keys[pg.K_d]:
            self.scene.move_player(direction = -90, amount = 0.005*self.frameTime)
    
    def handleMouse(self):

        (x,y) = pg.mouse.get_pos()
        rate = self.frameTime / 16.6
        right_amount = -0.1 * rate * ((SCREEN_WIDTH / 2) - x)
        up_amount = -0.1 * rate * ((SCREEN_HEIGHT / 2) - y)
        self.scene.strafe_camera(right_amount, up_amount)
        pg.mouse.set_pos((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    def showFrameRate(self):

        self.currentTime = pg.time.get_ticks()
        delta = self.currentTime - self.lastTime
        if (delta >= 1000):
            framerate = int(1000.0 * self.numFrames/delta)
            pg.display.set_caption(f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(60,framerate))
        self.numFrames += 1

    def quit(self):
        
        self.renderer.destroy()