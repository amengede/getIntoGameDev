class Box:

    
    def __init__(self, x, y, l, w):

        self.x = x
        self.y = y
        self.l = l
        self.w = w
    
    def inside(self, other_x, other_y):

        if other_x < self.x:
            return False

        if other_x > (self.x + self.l):
            return False
        
        if other_y < (self.y - self.w):
            return False

        if other_y > self.y:
            return False
        
        return True

class Grid:


    def __init__(self, image_length, image_width, rows, cols):

        self.update(image_length, image_width, rows, cols)
    
    def update(self, image_length, image_width, rows, cols):

        self.image_length = image_length
        self.image_width = image_width
        self.rows = rows
        self.cols = cols

        self.box_length = image_length / cols
        self.box_width = image_width / rows

        self.boxes = []
        for row in range(rows):
            self.boxes.append([])
            for col in range(cols):
                self.boxes[row].append(
                    Box(
                        x = int(col * self.box_length), y = int(row * self.box_width), 
                        l = int(self.box_length), w = int(self.box_width)
                    )
                )
    
    def image_to_grid(self, coord):

        return (int(coord[0] // self.box_length), int(coord[1] // self.box_width))
    
    def grid_to_image(self, coord):

        return (coord[0] * self.box_length, coord[1] * self.box_width)

grid = Grid(
    image_length = 800, image_width = 600,
    rows = 3, cols = 3
)