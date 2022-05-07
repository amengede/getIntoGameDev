from config import *
import control

if __name__ == "__main__":
    initialise_pygame()
    shaders = initialise_opengl()
    framebuffer = create_framebuffer()
    myApp = control.MenuApp(shaders)
    result = CONTINUE
    while(result == CONTINUE):
        result = myApp.mainLoop()
        if result == NEW_GAME:
            myApp.quit()
            myApp = control.GameApp(shaders, framebuffer)
            result = CONTINUE
            continue
        if result == OPEN_MENU:
            myApp.quit()
            myApp = control.MenuApp(shaders)
            result = CONTINUE
            continue
    myApp.quit()
    teardown_program_environment(shaders, framebuffer)