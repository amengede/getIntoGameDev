from config import *
import model

class Button(QPushButton):

    
    def __init__(self, label: str, checkable: bool = False):

        super().__init__(label)
        self.setCheckable(checkable)

class BrushView(QWidget):


    def __init__(self, parent):

        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        label = QLabel("Object")
        selector = QComboBox()
        self.object_types = [
            OBJECT_TYPE_PLAYER,
            OBJECT_TYPE_MONSTER,
            OBJECT_TYPE_BLOCK,
            OBJECT_TYPE_COIN
        ]
        selector.addItems(["Player", "Monster", "Block", "Coin"])
        selector.setCurrentIndex(parent.current_brush)
        selector.currentIndexChanged.connect(self.index_changed)
        self.layout.addWidget(label)
        self.layout.addWidget(selector)
        self.parent = parent

    def index_changed(self, new_brush: int):

        self.parent.current_brush = new_brush

class MainView(QWidget):


    def __init__(self, parent):

        super().__init__()
        self.setFixedSize(QSize(MAIN_WINDOW_WIDTH, MAIN_WINDOW_HEIGHT))
        self.width = MAIN_WINDOW_WIDTH
        self.height = MAIN_WINDOW_HEIGHT

        self.color = QColor(64, 128, 192)

        self.parent = parent
        self.camera_pos = QPointF(0.0, 0.0)

        self.cursor_world_pos = QPointF()
        self.cursor_world_pos_snapped = QPointF()

        self.move_icons = {
            CAMERA_MOVE_LEFT: {
                "dst_rect": QRect(544, 416, 32, 32),
                "pixmap": QPixmap("gfx/left-arrow.png", "png"),
                "src_rect": QRect(0,0,512,512)
            },
            CAMERA_MOVE_RIGHT: {
                "dst_rect": QRect(608, 416, 32, 32),
                "pixmap": QPixmap("gfx/right-arrow.png", "png"),
                "src_rect": QRect(0,0,512,512)
            },
            CAMERA_MOVE_UP: {
                "dst_rect": QRect(576, 384, 32, 32),
                "pixmap": QPixmap("gfx/up-arrow.png", "png"),
                "src_rect": QRect(0,0,512,512)
            },
            CAMERA_MOVE_DOWN: {
                "dst_rect": QRect(576, 448, 32, 32),
                "pixmap": QPixmap("gfx/down-arrow.png", "png"),
                "src_rect": QRect(0,0,512,512)
            },
        }

        self.setMouseTracking(True)

    def mouseMoveEvent(self, event: QMouseEvent):
        
        self.cursor_world_pos = self.screen_to_world(event.pos())
        self.cursor_world_pos_snapped = QPointF(
            0.5 * int((self.cursor_world_pos.x() - 0.5) * 2),
            0.5 * int((self.cursor_world_pos.y() - 0.5) * 2))
        self.repaint()
    
    def mousePressEvent(self, event: QMouseEvent):

        screen_pos = event.pos()
        for movement, icon in self.move_icons.items():
            rect: QRect = icon["dst_rect"]
            if rect.contains(screen_pos):
                self.move_camera(movement)
                self.parent.redraw()
                return

        screen_pos = event.pos()
        self.parent.click(screen_pos, event)
    
    def move_camera(self, movement: int):

        dx = 0.0
        dy = 0.0
        zoom_factor = 1.0 / self.parent.zoom_factor

        if movement == CAMERA_MOVE_LEFT:
            dx = -0.1 * zoom_factor
        elif movement == CAMERA_MOVE_RIGHT:
            dx = 0.1 * zoom_factor
        elif movement == CAMERA_MOVE_UP:
            dy = 0.1 * zoom_factor
        elif movement == CAMERA_MOVE_DOWN:
            dy = -0.1 * zoom_factor
        
        self.camera_pos.setX(self.camera_pos.x() + dx)
        self.camera_pos.setY(self.camera_pos.y() + dy)
    
    def screen_to_world(self, pos: QPoint) -> QPointF:

        screen_rect = self.rect()
        width = screen_rect.width() / 2
        height = screen_rect.height() / 2
        zoom_factor = self.parent.zoom_factor

        x = float(pos.x() - width) / (zoom_factor * width) + self.camera_pos.x()
        y = -float(pos.y() - height) / (zoom_factor * width) + self.camera_pos.y()

        return QPointF(x,y)
    
    def world_to_screen(self, pos: QPointF) -> QPoint:

        screen_rect = self.rect()
        width = screen_rect.width() / 2
        height = screen_rect.height() / 2
        zoom_factor = self.parent.zoom_factor

        x = pos.x() - self.camera_pos.x()
        y = pos.y() - self.camera_pos.y()

        x = int(x * (zoom_factor * width) + width)
        y = int(y * -(zoom_factor * width) + height)

        return QPoint(x,y)
    
    def paintEvent(self, event: QPaintEvent):

        rect = event.rect()
        painter = QPainter(self)
        painter.fillRect(rect, self.color)
        painter.setPen(QColor("black"))

        #Grid
        if self.parent.zoom_factor > 0.03125:
            world_x = self.camera_pos.x() - 1.0 / self.parent.zoom_factor
            world_x = 0.5 * int(2 * world_x)
            screen_x = self.world_to_screen(QPointF(world_x, 0)).x()
            while screen_x < MAIN_WINDOW_WIDTH:
                point_a = QPoint(screen_x, 0)
                point_b = QPoint(screen_x, MAIN_WINDOW_HEIGHT)
                painter.drawLine(point_a, point_b)
                world_x += 0.5
                screen_x = self.world_to_screen(QPointF(world_x, 0)).x()
            
            world_y = self.camera_pos.y() + 1.0 / self.parent.zoom_factor
            world_y = 0.5 * int(2 * world_y)
            screen_y = self.world_to_screen(QPointF(0, world_y)).y()
            while screen_y < MAIN_WINDOW_HEIGHT:
                point_a = QPoint(0, screen_y)
                point_b = QPoint(MAIN_WINDOW_WIDTH, screen_y)
                painter.drawLine(point_a, point_b)
                world_y -= 0.5
                screen_y = self.world_to_screen(QPointF(0, world_y)).y()


        #Objects
        objects: list[model.GameObject] = self.parent.objects
        selected_object: model.GameObject = self.parent.selected_object
        for obj in objects:

            _type = obj._type
            top_left = self.world_to_screen(obj.rect.topLeft())
            bottom_right = self.world_to_screen(obj.rect.bottomRight())
            color = OBJECT_COLORS[_type]
            hover = self.parent.mouse_mode == MOUSE_MODE_SELECT\
                and obj.rect.contains(self.cursor_world_pos)
            if hover or obj is selected_object:
                color = QColor("orange")
            screen_rect = QRect(top_left, bottom_right)
            painter.fillRect(screen_rect, color)
            if self.parent.zoom_factor > 0.08:
                painter.drawText(top_left, OBJECT_NAMES[_type])
            painter.drawRect(screen_rect)
        
        #Mouse Preview
        new = self.parent.mouse_mode == MOUSE_MODE_NEW
        edit = self.parent.mouse_mode == MOUSE_MODE_EDIT \
            and self.parent.selected_object is not None
        if new or edit:

            x = self.cursor_world_pos_snapped.x()
            y = self.cursor_world_pos_snapped.y()
            _type = self.parent.current_brush if new \
                else self.parent.selected_object._type
            w,h = OBJECT_SIZES[_type]

            top_left = self.world_to_screen(QPointF(x,y))
            bottom_right = self.world_to_screen(QPointF(x + w, y + h))
            screen_rect = QRect(top_left, bottom_right)
            color = OBJECT_COLORS[_type]
            alpha_color = QColor(color.red(), color.green(), color.blue(), 128)
            painter.fillRect(screen_rect, alpha_color)
            painter.drawRect(screen_rect)


        #Icons
        for icon in self.move_icons.values():
            painter.drawPixmap(icon["dst_rect"], icon["pixmap"], icon["src_rect"])