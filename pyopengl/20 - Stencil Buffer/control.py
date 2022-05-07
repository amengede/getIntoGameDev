from config import *
import view
import model
import gui

class GameApp:
    def __init__(self, shaders, framebuffer):

        self.shader3DTextured = shaders[0]
        self.shader3DColored = shaders[1]
        self.shader2DTextured = shaders[2]
        self.shader3DBillboard = shaders[6]
        self.shader3DCubemap = shaders[7]
        self.shader3DLightMap = shaders[8]
        self.shader3DOutline = shaders[9]

        self.multisampleFBO = framebuffer[0]
        self.regularCBMultisampled = framebuffer[1]
        self.brightCBMultisampled = framebuffer[2]
        self.MultisampleDepthStencilBuffer = framebuffer[3]
        self.singlesampleFBO = framebuffer[4]
        self.regularCB = framebuffer[5]
        self.brightCB = framebuffer[6]

        self.shadowMapResolution = 2048
        self.make_shadow_map()

        glEnable(GL_STENCIL_TEST)
        glStencilMask(255)
        #function,reference,reference_mask
        glStencilFunc(GL_EQUAL, 1, 255)
        #action to take on (stencil_test_failure, stencil_pass_depth_failure, stencil_fail_depth_fail)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)

        pg.mouse.set_visible(False)
        self.lastTime = 0
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.lightCount = 0
        self.resetLights()
        self.create_objects()

    def make_shadow_map(self):
        self.depthMapFBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)
        self.depthMap = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depthMap)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self.shadowMapResolution,
            self.shadowMapResolution, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, np.array([1.0,1.0,1.0,1.0], dtype=np.float32))
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depthMap, 0)

    def create_objects(self):
        self.wood_texture = view.Material("gfx/crate")
        monkey_model = view.ObjModel("models", "monkey.obj", self.shader3DTextured, self.wood_texture)
        self.monkey = model.Monkey(np.array([0,0,0],dtype=np.float32), monkey_model)
        self.cube = model.Cube(self.shader3DTextured, self.wood_texture,[1,1,0.5])
        self.player = model.Player([0,0,1.2])
        self.light = model.Light([self.shader3DColored, self.shader3DTextured,self.shader3DBillboard], [0.2, 0.7, 0.8], [1,1.7,1.5], 2, self.lightCount)
        self.lightCount += 1
        self.light2 = model.Light([self.shader3DColored, self.shader3DTextured, self.shader3DBillboard], [0.9, 0.4, 0.0], [0,1.7,0.5], 2, self.lightCount)
        self.lightCount += 1
        self.screen = view.TexturedQuad(0, 0, 2, 2, (self.regularCB, self.brightCB), self.shader2DTextured)
        self.hud_texture = view.SimpleMaterial("gfx/hud")
        self.hud = view.TexturedQuad(0, 0, 2, 2, (self.hud_texture.texture,), self.shader2DTextured)
        self.smokeTexture = view.SimpleMaterial("gfx/smoke")
        self.smoke = view.BillBoard(1,1,self.smokeTexture, self.shader3DBillboard)
        ground_model = view.ObjModel("models", "ground.obj", self.shader3DTextured, self.wood_texture)
        self.ground = model.Ground(np.array([0,0,0],dtype=np.float32), ground_model)
        self.skyBoxTexture = view.CubeMapMaterial("gfx/sky")
        skyBoxModel = view.CubeMapModel(self.shader3DCubemap, 100,100,100,1,1,1, self.skyBoxTexture)
        self.skyBox = model.skyBox(skyBoxModel)

    def resetLights(self):
        glUseProgram(self.shader3DBillboard)
        for i in range(8):
            glUniform1i(glGetUniformLocation(self.shader3DBillboard,f"lights[{i}].enabled"),0)
        glUseProgram(self.shader3DTextured)
        for i in range(8):
            glUniform1i(glGetUniformLocation(self.shader3DTextured,f"lights[{i}].enabled"),0)

    def mainLoop(self):
        result = CONTINUE
        #check events
        for event in pg.event.get():
            if (event.type == pg.KEYDOWN and event.key==pg.K_ESCAPE):
                result = EXIT
            if (event.type == pg.KEYDOWN and event.key==pg.K_m):
                result = OPEN_MENU
        self.handleMouse()
        self.handleKeys()
        #update objects
        self.light.update()
        self.light2.update()
        self.player.update([self.shader3DColored, self.shader3DTextured, self.shader3DBillboard, self.shader3DCubemap, self.shader3DOutline])

        #first pass: capture shadow map
        lightProjection = pyrr.matrix44.create_orthogonal_projection(-10,10,-10,10,1.0,20.0, dtype = np.float32)
        lightPosition = 10 * np.array([1, -0.5, 1], dtype=np.float32)
        lookTarget = np.array([0,0,0],dtype=np.float32)
        globalUp = np.array([0,0,1],dtype=np.float32)
        lightView = pyrr.matrix44.create_look_at(lightPosition, lookTarget, globalUp, dtype=np.float32)
        lightSpaceTransform = pyrr.matrix44.multiply(lightView,lightProjection)
        glUseProgram(self.shader3DLightMap)
        glUniformMatrix4fv(glGetUniformLocation(self.shader3DLightMap,"lightSpaceTransform"),
            1,GL_FALSE, lightSpaceTransform)
        glViewport(0,0,self.shadowMapResolution, self.shadowMapResolution)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depthMapFBO)
        glClear(GL_DEPTH_BUFFER_BIT)
        self.lightRender()

        #second pass: render (3D)
        glViewport(0,0,SCREEN_WIDTH, SCREEN_HEIGHT)
        glBindFramebuffer(GL_FRAMEBUFFER, self.multisampleFBO)
        glDrawBuffers(2, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        glUseProgram(self.shader3DTextured)
        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self.depthMap)
        glUniformMatrix4fv(glGetUniformLocation(self.shader3DTextured,"lightSpaceTransform"),
            1, GL_FALSE, lightSpaceTransform)
        self.renderScene()

        #bounce multisampled frame down to single sampled
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self.multisampleFBO)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.singlesampleFBO)
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        glDrawBuffer(GL_COLOR_ATTACHMENT0)
        glBlitFramebuffer(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, GL_COLOR_BUFFER_BIT, GL_NEAREST)
        glReadBuffer(GL_COLOR_ATTACHMENT1)
        glDrawBuffer(GL_COLOR_ATTACHMENT1)
        glBlitFramebuffer(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, GL_COLOR_BUFFER_BIT, GL_NEAREST)

        #third pass: 2D rendering and post processing
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        self.screen.draw()
        self.hud.draw()
        pg.display.flip()
        #timing
        self.showFrameRate()
        return result
    
    def lightRender(self):
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        self.skyBox.draw(self.player.position)
        glEnable(GL_CULL_FACE)
        self.cube.draw(self.shader3DLightMap)
        self.light.draw(self.shader3DLightMap)
        self.light2.draw(self.shader3DLightMap)
        self.monkey.draw(False, None, self.shader3DLightMap)
        self.ground.draw(self.shader3DLightMap)
    
    def renderScene(self):
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glStencilMask(0)
        self.skyBox.draw(self.player.position)
        glEnable(GL_CULL_FACE)
        self.cube.draw(None)
        self.light.draw(None)
        self.light2.draw(None)
        self.ground.draw(None)
        self.monkey.draw(True, np.array([0,1,0], dtype=np.float32), self.shader3DOutline)
        self.smoke.draw(np.array([-1,0.5,0.5],dtype=np.float32), self.player.position)

    def handleKeys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.player.move(0, 0.0025*self.frameTime)
            return
        if keys[pg.K_a]:
            self.player.move(90, 0.0025*self.frameTime)
            return
        if keys[pg.K_s]:
            self.player.move(180, 0.0025*self.frameTime)
            return
        if keys[pg.K_d]:
            self.player.move(-90, 0.0025*self.frameTime)
            return

    def handleMouse(self):
        (x,y) = pg.mouse.get_pos()
        theta_increment = self.frameTime * 0.05 * (SCREEN_WIDTH / 2 - x)
        phi_increment = self.frameTime * 0.05 * (SCREEN_HEIGHT / 2 - y)
        self.player.increment_direction(theta_increment, phi_increment)
        pg.mouse.set_pos((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

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
        self.wood_texture.destroy()
        self.monkey.destroy()
        self.cube.destroy()
        self.light.destroy()
        self.light2.destroy()
        self.cube.destroy()
        self.screen.destroy()
        self.smoke.destroy()
        self.ground.destroy()
        self.skyBox.destroy()
        glDeleteTextures(1, [self.depthMap,])
        glDeleteFramebuffers(1, [self.depthMapFBO,])

class MenuApp:
    def __init__(self, shaders):
        self.shader2DColored = shaders[3]
        self.shaderText = shaders[4]
        self.particleShader = shaders[5]

        pg.mouse.set_visible(True)
        self.lastTime = 0
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0
        self.create_objects()

    def create_objects(self):

        self.font = view.SimpleMaterial("gfx/font")

        self.textLines = []

        newgame_label = gui.TextLine(self.font, "New Game", self.shaderText, [0.04, 0.04], [-0.15, 0.3], [0,0,0])
        self.textLines.append(newgame_label)
        exit_label = gui.TextLine(self.font, "Exit", self.shaderText, [0.04, 0.04], [-0.15, -0.3], [0,0,0])
        self.textLines.append(exit_label)
        title = gui.TextLine(self.font, "Monke Madness", self.shaderText, [0.08, 0.08], [-0.5, 0.7], [1,0,0])
        self.textLines.append(title)

        self.buttons = []

        newgame_button = gui.Button((0,0.3), (0.4, 0.1), (1, 1, 0), self.shader2DColored)
        newgame_button.clickAction = gui.new_game_click
        newgame_button.label = newgame_label
        self.buttons.append(newgame_button)

        exit_button = gui.Button((0,-0.3), (0.4, 0.1), (1, 1, 0), self.shader2DColored)
        exit_button.clickAction = gui.exit_click
        exit_button.label = exit_label
        self.buttons.append(exit_button)

        createInfo = model.ParticleEmitter2DCreateInfo()
        createInfo.color = (255,255,0)
        createInfo.layer = 1
        createInfo.lifetime = 600
        createInfo.pos = (0,0)
        createInfo.rate = 0.1
        createInfo.shader = self.particleShader
        createInfo.size = 10
        createInfo.velocity_field = velocity_field1
        createInfo.offsetFunction = offset_function1
        self.layer1emitter = model.ParticleEmitter2D(createInfo)
        createInfo.color = (0,0,255)
        createInfo.layer = 2
        createInfo.rate = 0.2
        createInfo.velocity_field = velocity_field2
        createInfo.offsetFunction = offset_function2
        self.layer2emitter = model.ParticleEmitter2D(createInfo)

    def mainLoop(self):
        result = CONTINUE
        #check events
        for event in pg.event.get():
            if (event.type == pg.MOUSEBUTTONDOWN and event.button==1):
                result = self.handleMouseClick()
            if (event.type == pg.KEYDOWN and event.key==pg.K_ESCAPE):
                result = EXIT
        self.handleMouseMove()
        #update
        self.layer1emitter.update()
        self.layer2emitter.update()
        #render
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        self.layer2emitter.draw()
        self.layer1emitter.draw()
        for button in self.buttons:
            button.draw()
        for line in self.textLines:
            line.draw()
        pg.display.flip()

        #timing
        self.showFrameRate()
        return result

    def handleMouseMove(self):
        (x,y) = pg.mouse.get_pos()
        x -= SCREEN_WIDTH / 2
        x /= SCREEN_WIDTH / 2
        y -= SCREEN_HEIGHT / 2
        y /= -SCREEN_HEIGHT / 2

        for button in self.buttons:
            button.handle_mouse_movement((x,y))
    
    def handleMouseClick(self):
        (x,y) = pg.mouse.get_pos()
        x -= SCREEN_WIDTH / 2
        x /= SCREEN_WIDTH / 2
        y -= SCREEN_HEIGHT / 2
        y /= -SCREEN_HEIGHT / 2

        for button in self.buttons:
            result = button.handle_mouse_click((x,y))
            if result != CONTINUE:
                return result
        return CONTINUE

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
        self.layer2emitter.destroy()
        self.layer1emitter.destroy()
        for button in self.buttons:
            button.destroy()
        for line in self.textLines:
            line.destroy()
        self.font.destroy()