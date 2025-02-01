from config import *
import model
import view

class Editor(QMainWindow):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("Map Maker")
        self.create_menu()

        self.reset_state()
        self.build_layout()
        self.build_and_connect_widgets()
    
    def reset_state(self):

        self.zoom_factor = 0.125
        self.current_brush = OBJECT_TYPE_PLAYER
        self.objects : list[model.GameObject] = []
        self.selected_object : model.GameObject | None = None
        self.mouse_mode = MOUSE_MODE_NEW

    def build_layout(self):

        layout = QVBoxLayout()
        self.top_frame = QHBoxLayout()
        self.middle_frame = QHBoxLayout()

        self.tools_frame = QVBoxLayout()
        self.main_view = view.MainView(self)
        self.detail_frame = QVBoxLayout()

        self.middle_frame.addLayout(self.tools_frame)
        self.middle_frame.addWidget(self.main_view, alignment=Qt.AlignmentFlag.AlignTop)
        self.middle_frame.addLayout(self.detail_frame)
        

        layout.addLayout(self.top_frame)
        layout.addLayout(self.middle_frame)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def build_and_connect_widgets(self):

        self.build_top_widgets()
        self.build_tool_widgets()
        self.build_detail_widgets()
    
    def build_top_widgets(self):

        frame = QFrame()
        group = QHBoxLayout()
        label = QLabel("Zoom:")
        group.addWidget(label)
        button = view.Button("in")
        button.released.connect(lambda: self.modify_zoom(1.25))
        group.addWidget(button)
        button = view.Button("out")
        button.released.connect(lambda: self.modify_zoom(0.75))
        group.addWidget(button)
        frame.setLayout(group)

        frame.setStyleSheet("QFrame {"
                                "border-width: 1;"
                                "border-radius: 3;"
                                "border-style: solid;"
                                "border-color: rgb(128,128,128);}")

        self.top_frame.addWidget(frame, alignment=Qt.AlignmentFlag.AlignTop)
    
    def modify_zoom(self, factor: float):

        self.zoom_factor *= factor
        self.redraw()

    def redraw(self):

        self.main_view.repaint()

    def build_tool_widgets(self):

        mouse_options = QComboBox()
        mouse_options.addItems(["select", "edit", "new"])
        mouse_options.setCurrentIndex(self.mouse_mode)
        mouse_options.currentIndexChanged.connect(self.set_mouse_mode)
        self.tools_frame.addWidget(mouse_options, alignment=Qt.AlignmentFlag.AlignTop)
    
    def set_mouse_mode(self, new_mode: int):

        self.mouse_mode = new_mode

    def build_detail_widgets(self):

        self.brush_view = view.BrushView(self)
        self.detail_frame.addWidget(self.brush_view)
        self.detail_frame.insertStretch(-1, 1)

    def click(self, pos: QPoint, event: QMouseEvent):

        world_pos = self.main_view.screen_to_world(pos)
        world_pos_snapped = QPointF(0.5 * int((world_pos.x() - 0.5) * 2),
                                    0.5 * int((world_pos.y() - 0.5) * 2))
        x = world_pos_snapped.x()
        y = world_pos_snapped.y()
        
        object_under_click = self.object_at_pos(world_pos)
        
        if event.button() == Qt.MouseButton.LeftButton:

            if self.mouse_mode == MOUSE_MODE_NEW and object_under_click is None:
                w,h = OBJECT_SIZES[self.current_brush]
                self.selected_object = model.GameObject(QRectF(x, y, w, h), self.current_brush)
                self.objects.append(self.selected_object)
            elif self.mouse_mode == MOUSE_MODE_SELECT:
                self.selected_object = object_under_click
            elif self.mouse_mode == MOUSE_MODE_EDIT\
                and self.selected_object is not None:

                w,h = OBJECT_SIZES[self.selected_object._type]
                self.selected_object.rect = QRectF(x,y,w,h)
        else:

            if object_under_click is not None:
                self.objects.remove(object_under_click)
            object_under_click = None
        self.redraw()
    
    def object_at_pos(self, world_pos: QPointF) -> model.GameObject | None:

        for obj in self.objects:

            if obj.rect.contains(world_pos):
                return obj
        return None

    def create_menu(self):

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        new_button = QAction("New", self)
        new_button.triggered.connect(self.new)
        file_menu.addAction(new_button)

        save_button = QAction("Save", self)
        save_button.triggered.connect(self.save)
        file_menu.addAction(save_button)

        load_button = QAction("Load", self)
        load_button.triggered.connect(self.load)
        file_menu.addAction(load_button)

    def new(self):

        self.reset_state()
        self.redraw()
    
    def save(self):

        filename = QFileDialog.getSaveFileName(self)
        if len(filename[0]) <= 0:
            return
        
        filename = filename[0]

        with open(filename, "w") as file:
            for obj in self.objects:
                rect = obj.rect
                x = rect.x()
                y = rect.y()
                name = OBJECT_NAMES[obj._type]
                file.write(f"{name} {x} {y}\n")

    def load(self):

        self.reset_state()

        filename = QFileDialog.getOpenFileName(self)
        if len(filename[0]) <= 0:
            return
        
        filename = filename[0]

        with open(filename, "r") as file:
            for line in file.readlines():
                line = line.rstrip()
                arguments = line.split(" ")
                _type = OBJECT_CODES[arguments[0]]
                x = float(arguments[1])
                y = float(arguments[2])
                w,h = OBJECT_SIZES[_type]
                self.objects.append(model.GameObject(QRectF(x, y, w, h), _type))
        self.redraw()
        
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = Editor()
    window.show()

    app.exec()