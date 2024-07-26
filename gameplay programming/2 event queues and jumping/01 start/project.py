from config import *
import control

def main():
    
    myApp = control.GameApp()
    result = RETURN_ACTION_CONTINUE
    while(result == RETURN_ACTION_CONTINUE):
        result = myApp.main_loop()
    myApp.quit()

if __name__ == "__main__":

    main()