from config import *
import control

def main():
    window = initialize_glfw()
    myApp = control.GameApp(window)
    result = RETURN_ACTION_CONTINUE
    while(result == RETURN_ACTION_CONTINUE):
        result = myApp.mainLoop()
    myApp.quit()

if __name__ == "__main__":

    main()