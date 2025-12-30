""" A fun game """

from config import *
import control

def main():
    """ Let's get things running! """

    my_app = control.GameApp()
    result = RETURN_ACTION_CONTINUE
    while result == RETURN_ACTION_CONTINUE:
        result = my_app.main_loop()
    my_app.quit()

if __name__ == "__main__":

    main()
