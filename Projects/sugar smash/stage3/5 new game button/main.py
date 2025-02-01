import app

if __name__ == "__main__":
    gameApp = app.App()

    result = app.App.CONTINUE
    while result == app.App.CONTINUE:
        result = gameApp.mainLoop()
        if result == app.App.NEWGAME:
            gameApp = app.App()
            result = app.App.CONTINUE