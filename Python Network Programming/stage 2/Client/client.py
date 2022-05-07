import pygame as pg
import socket
import select

#--------------------- model -------------------------------------------------#



#--------------------- view  -------------------------------------------------#

class Label:


    def __init__(self, text, font):
        self.text = text
        self.font = font
    
    def draw(self, surface, x, y, color):
        surface.blit(self.font.render(self.text, True, color), (x - 8, y - 15))

class Rectangle:
    

    def __init__(self, topLeft, size):
        self.rect = (topLeft[0], topLeft[1], size[0], size[1])

    def hasMouse(self):
        (x,y) = pg.mouse.get_pos()
        left = self.rect[0]
        right = self.rect[0] + self.rect[2]
        up = self.rect[1]
        down = self.rect[1] + self.rect[3]
        return x > left and x < right and y > up and y < down
    
    def draw(self, surface, color):
        pg.draw.rect(surface, color, self.rect)

class Button:
    

    def __init__(self, panel, text, onColor, offColor):
        self.panel = panel
        self.text = text
        self.onColor = onColor
        self.offColor = offColor
    
    def hasMouse(self):
        
        return self.panel.hasMouse()

    def draw(self, surface):
        panelColor = self.offColor
        textColor = self.onColor
        if self.hasMouse():
            panelColor = self.onColor
            textColor = self.offColor
        self.panel.draw(surface, panelColor)
        self.text.draw(surface, self.panel.rect[0] + 15, self.panel.rect[1] + 15, textColor)

class InputField:


    def __init__(self, text, panel):

        self.text = text
        self.panel = panel
        self.ready = False
        self.active = False
    
    def hasMouse(self):
        
        return self.panel.hasMouse()
    
    def handleKeyPress(self, event):

        if event.key == pg.K_RETURN:
            self.ready = True
        if event.key == pg.K_BACKSPACE:
            self.text.text = self.text.text[:-1]
        else:
            self.text.text += pg.key.name(event.key)

    def draw(self, surface, panelColor, textColor):

        if self.active:
            temp = panelColor
            panelColor = textColor
            textColor = temp
        self.panel.draw(surface, panelColor)
        self.text.draw(surface, self.panel.rect[0] + 15, self.panel.rect[1] + 15, textColor)

class ViewController:
    

    def __init__(self):
        self.screen = pg.display.set_mode((800, 600))
        self.palette = {
            "teal": (41, 127, 135),
            "yellow": (246, 209, 103),
            "light-yellow": (255, 247, 174),
            "red": (223, 46, 46)
        }
        self.font = pg.font.SysFont("arial", 24)
    
    def shouldAdvance(self, controller):

        #override this
        pass

    def getNextViewController(self):
        
        #override this
        pass

    def handleClick(self):
        
        #override this
        pass

    def handleButtonPress(self, event):
        
        #override this
        pass
    
    def drawScreen(self):

        #override this
        pass

class ServerSelect(ViewController):


    def __init__(self):

        super().__init__()

        self.screen = pg.display.set_mode((400,200))
        self.IPLabel = Label("IP: 192.168.1.107", self.font)

        portLabel = Label("Port: ", self.font)
        portPanel = Rectangle((100,100), (150,32))
        self.portField = InputField(portLabel, portPanel)

        submitLabel = Label("Connect", self.font)
        submitPanel = Rectangle((100,150), (100,32))
        self.submitButton = Button(submitPanel, submitLabel, self.palette["yellow"], self.palette["red"])

        self.ready = False

    def handleClick(self):
        
        self.portField.active = self.portField.hasMouse()

        if self.submitButton.hasMouse():
            self.ready = True
    
    def handleButtonPress(self, event):
        
        if self.portField.active:
            self.portField.handleKeyPress(event)
    
    def shouldAdvance(self, controller):

        if self.ready:
            portNumber = int(self.portField.text.text.split(": ")[1])
            controller.socket.connect(("192.168.1.107", portNumber))
            return True
        return False
    
    def getNextViewController(self):
        
        return ClientLogin()
    
    def drawScreen(self):
        
        self.screen.fill(self.palette["teal"])

        self.IPLabel.draw(self.screen, 100, 50, self.palette["light-yellow"])
        self.portField.draw(self.screen, self.palette["yellow"], self.palette["red"])
        self.submitButton.draw(self.screen)

        pg.display.update()
    
class ClientLogin(ViewController):


    def __init__(self):

        super().__init__()

        self.screen = pg.display.set_mode((400,400))

        nameLabel = Label("Username: ", self.font)
        namePanel = Rectangle((100,200), (200,32))
        self.nameField = InputField(nameLabel, namePanel)

        submitLabel = Label("Login", self.font)
        submitPanel = Rectangle((100,350), (100,32))
        self.submitButton = Button(submitPanel, submitLabel, self.palette["yellow"], self.palette["red"])

        self.ready = False

    def handleClick(self):
        
        self.nameField.active = self.nameField.hasMouse()

        if self.submitButton.hasMouse():
            self.ready = True
    
    def handleButtonPress(self, event):
        
        if self.nameField.active:
            self.nameField.handleKeyPress(event)
    
    def shouldAdvance(self, controller):

        if self.ready:
            message = "name:" + self.nameField.text.text.split(": ")[1]
            controller.socket.send(message.encode())
            print(f"Sent message \"{message}\"\n")
            response = controller.socket.recv(4096).decode()
            print(f"Got response\"{response}\"\n")
            if response == "available":
                controller.name = self.nameField.text.text.split(": ")[1]
                return True
        return False
    
    def getNextViewController(self):
        
        return self
    
    def drawScreen(self):
        
        self.screen.fill(self.palette["teal"])

        self.nameField.draw(self.screen, self.palette["yellow"], self.palette["red"])
        self.submitButton.draw(self.screen)

        pg.display.update()

class ChatRoom(ViewController):


    pass

#--------------------- control -----------------------------------------------#

class Client:

    def __init__(self):
        pg.init()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.viewController = ServerSelect()

    def run(self):

        running = True
        while running:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.KEYDOWN:
                    self.viewController.handleButtonPress(event)
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.viewController.handleClick()
            
            if self.viewController.shouldAdvance(self):
                self.viewController = self.viewController.getNextViewController()
            
            self.viewController.drawScreen()

    def exit(self):
        pass

#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    client = Client()
    client.run()
    client.exit()