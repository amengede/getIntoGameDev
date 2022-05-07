import app

if __name__ == "__main__":
    gameApp = app.App()

    running = True
    while running:
        running = gameApp.mainLoop()