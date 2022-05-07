import pygame as pg
import socket
import select

#--------------------- model -------------------------------------------------#

class Client:


    def __init__(self, name, connection):
        self.name = name
        self.connection = connection
        self.next = None

class ClientList:


    def __init__(self):
        self.head = None
    
    def add(self, name, connection):

        newClient = Client(name, connection)

        #do we have an empty list?
        if self.head is None:
            self.head = newClient
        
        else:
            newClient.next = self.head
            self.head = newClient
    
    def nameAvailable(self, name):

        client = self.head

        while client is not None:

            if client.name == name:
                return False
            
            client = client.next
        
        return True

    def getByConnection(self, connection):

        client = self.head

        while client is not None:

            if client.connection == connection:
                return client
            
            client = client.next
        
        return None

class Message:


    def __init__(self, text):
        self.text = text
        self.next = None

class MessageList:


    def __init__(self):
        self.head = None
    
    def add(self, text):

        newMessage = Message(text)

        #do we have an empty list?
        if self.head is None:
            self.head = newMessage
        
        else:
            newMessage.next = self.head
            self.head = newMessage

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
    
    def draw(self, surface, color):
        pg.draw.rect(surface, color, self.rect)

class Button:
    

    def __init__(self, panel, text, onColor, offColor):
        self.panel = panel
        self.text = text
        self.onColor = onColor
        self.offColor = offColor
    
    def hasMouse(self):
        (x,y) = pg.mouse.get_pos()
        left = self.panel.rect[0]
        right = self.panel.rect[0] + self.panel.rect[2]
        up = self.panel.rect[1]
        down = self.panel.rect[1] + self.panel.rect[3]
        return x > left and x < right and y > up and y < down

    def draw(self, surface):
        panelColor = self.offColor
        textColor = self.onColor
        if self.hasMouse():
            panelColor = self.onColor
            textColor = self.offColor
        self.panel.draw(surface, panelColor)
        self.text.draw(surface, self.panel.rect[0] + 15, self.panel.rect[1] + 15, textColor)

class ViewController:
    

    def __init__(self, port):
        self.screen = pg.display.set_mode((800, 600))
        self.palette = {
            "teal": (41, 127, 135),
            "yellow": (246, 209, 103),
            "light-yellow": (255, 247, 174),
            "red": (223, 46, 46)
        }
        self.font = pg.font.SysFont("arial", 24)

        self.clientBox = Rectangle((50, 40), (600, 400))

        self.quitButton = Button(
            panel = Rectangle((100, 500), (200, 32)),
            text = Label("Shut Down Server", self.font),
            onColor = self.palette["red"],
            offColor = self.palette["light-yellow"]
        )
        
        self.clientLabel = Label("...", self.font)
        self.portLabel = Label(f"Listening on port {port}", self.font)
    
    def shouldExit(self):
        return self.quitButton.hasMouse()
    
    def drawScreen(self, clientList):
        self.screen.fill(self.palette["teal"])
        self.clientBox.draw(self.screen, self.palette["yellow"])

        client = clientList.head
        y = 50
        while client is not None:
            self.clientLabel.text = client.name
            self.clientLabel.draw(self.screen, 100, y + 25, self.palette["red"])
            y += 50
            client = client.next
        
        self.portLabel.draw(self.screen, 300, 20, self.palette["light-yellow"])
        self.quitButton.draw(self.screen)
        pg.display.update()

#--------------------- control -----------------------------------------------#

class Server:

    def __init__(self):
        pg.init()

        #ipconfig on command prompt
        self.host = "192.168.1.107"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(0)
        self.socket.bind((self.host, 0))
        self.port = self.socket.getsockname()[1]

        self.viewController = ViewController(self.port)
        self.clientList = ClientList()

    def run(self):

        self.socket.listen()
        inputs = [self.socket]
        outputs = []
        clientNumber = 0
        running = True
        while running:

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    running = not self.viewController.shouldExit()
            
            readable, writeable, exceptional = select.select(inputs, outputs, inputs, 0.1)
            messageBuffer = MessageList()
            for s in readable:
                if s is self.socket:
                    #listen on server
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    inputs.append(connection)
                    self.clientList.add(f"Client{clientNumber}", connection)
                    clientNumber += 1
                else:
                    #client connection
                    message = s.recv(4096).decode()
                    if message:
                        print(f"Got message \"{message}\"\n")
                        if message.split(":")[0] == "name":
                            if self.clientList.nameAvailable(message.split(":")[1]):
                                client = self.clientList.getByConnection(s)
                                client.name = message.split(":")[1]
                                response = "available".encode()
                            else:
                                response = "taken".encode()
                            s.send(response)
                        elif message.split(":")[0] == "message":
                            splitMessage = message.split(":")
                            #message:bob:hello
                            messageBuffer.add(f"message:{splitMessage[1]}:{splitMessage[2]}")
                            client = self.clientList.head
                            while client is not None:
                                if client.connection not in writeable:
                                    writeable.append(client.connection)
                                client = client.next
            
            for s in writeable:
                messageEntry = messageBuffer.head
                message = ""
                while messageEntry is not None:
                    message += f"{messageEntry.text}\n"
                    messageEntry = messageEntry.next
                message = message.encode()

                if s is not self.socket:
                    s.send(message)

            self.viewController.drawScreen(self.clientList)

    def exit(self):
        pass

#-----------------------------------------------------------------------------#

if __name__ == "__main__":
    server = Server()
    server.run()
    server.exit()