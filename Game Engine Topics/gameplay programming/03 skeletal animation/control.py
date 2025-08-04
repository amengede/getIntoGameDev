from config import *
import events
import model
import view

UPDATE_INTERVAL = 5
DRAW_INTERVAL = 16.67

class GameApp(events.Observable):
    """
        Main program.
    """


    def __init__(self):
        """
            Initialize the app.
        """

        super().__init__()

        self._set_up_glfw()

        self._make_assets()

        self._set_up_input_systems()

        self._set_up_timer()

    def _set_up_glfw(self) -> None:
        """
            Initialize glfw.
        """

        glfw.init()
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,4
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,5
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE
        )
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, 
            GLFW_CONSTANTS.GLFW_TRUE
        )
        #glfw.window_hint(
        #    GLFW_CONSTANTS.GLFW_DOUBLEBUFFER, False
        #)
        self._window = glfw.create_window(
            SCREEN_WIDTH, SCREEN_HEIGHT, 
            "Title", None, None
        )
        glfw.make_context_current(self._window)

    def _make_assets(self) -> None:
        """
            Make the game objects (renderer and scene)
        """

        self._renderer = view.GameRenderer(self._window)

        self._scene = model.Scene()
        self.add_observer(self._scene.get_event_queue())

    def _set_up_input_systems(self) -> None:
        """
            Configure the mouse and keyboard
        """

        glfw.set_input_mode(
            self._window, 
            GLFW_CONSTANTS.GLFW_CURSOR, 
            GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
        )

        self._keys = {}
        glfw.set_key_callback(self._window, self._key_callback)

        glfw.set_mouse_button_callback(self._window, self._mouse_click_callback)

    def _key_callback(self, window, key, scancode, action, mods) -> None:
        """
            Handle a key event.

            Parameters:

                window: the window on which the keypress occurred.

                key: the key which was pressed

                scancode: scancode of the key

                action: action of the key event

                mods: modifiers applied to the event
        """

        state = False
        match action:
            case GLFW_CONSTANTS.GLFW_PRESS:
                state = True
            case GLFW_CONSTANTS.GLFW_RELEASE:
                state = False
            case _:
                return

        self._keys[key] = state

        if key == GLFW_CONSTANTS.GLFW_KEY_SPACE \
            and action == GLFW_CONSTANTS.GLFW_PRESS:
            self._publish(events.Event(events.JUMP))

    def _mouse_click_callback(self, window, button, action, mods) -> None:
        """
            Handle a mouse click event.

            Parameters:

                window: the window on which the click occurred.

                button: the mouse button which was pressed

                action: action of the click event

                mods: modifiers applied to the event
        """

        if action != GLFW_CONSTANTS.GLFW_PRESS:
            return
        
        if button == GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_RIGHT:
            self._scene.zoom_camera(True)
        elif button == GLFW_CONSTANTS.GLFW_MOUSE_BUTTON_LEFT:
            self._scene.zoom_camera(False)

    def _set_up_timer(self) -> None:
        """
            Set up the variables needed to measure the framerate
        """

        self._last_time = glfw.get_time()
        self._current_time = glfw.get_time()
        self._num_frames = 0
        self._frame_time = 0
        self._time_since_last_update = 0
        self._time_since_last_draw = 0

    def main_loop(self) -> None:
        """
            Runs the main loop.
        """

        result = RETURN_ACTION_CONTINUE
        while result == RETURN_ACTION_CONTINUE:
            #check events
            if glfw.window_should_close(self._window) \
                or self._keys.get(GLFW_CONSTANTS.GLFW_KEY_ESCAPE, False):
                result = RETURN_ACTION_EXIT
                break

            self._handle_keys()
            self._handle_mouse()

            glfw.poll_events()

            #update
            self._scene.update(self._frame_time)

            #render
            self._renderer.render(
                camera = self._scene.get_camera(),
                renderables = self._scene.get_renderables())

            #timing
            self._show_frame_rate()

        return result

    def _handle_keys(self) -> None:
        """
            Update the state of the game based on currently pressed keys
        """

        amount = np.zeros(3, np.float32)

        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_W, False):
            # forwards
            amount[2] += 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_A, False):
            # left
            amount[0] -= 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_S, False):
            # backwards
            amount[2] -= 1
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_D, False):
            # right
            amount[0] += 1

        if pyrr.vector.length(amount) < 0.1:
            return

        rate = 0.0025*self._frame_time
        amount = rate * pyrr.vector.normalise(amount)

        self._scene.move_player(amount)

    def _handle_mouse(self) -> None:
        """
            Handle mouse movement.
        """

        (x,y) = glfw.get_cursor_pos(self._window)
        sensitivity = 0.4
        right_amount = -sensitivity * ((SCREEN_WIDTH / 2) - x)
        up_amount = sensitivity * ((SCREEN_HEIGHT / 2) - y)
        self._scene.spin_camera([0, up_amount, right_amount])
        glfw.set_cursor_pos(
            self._window, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def _show_frame_rate(self) -> None:
        """
            Calculate the framerate and update the window title 
            if a second has passed.
        """

        self._current_time = glfw.get_time()
        delta = self._current_time - self._last_time
        if (delta >= 1):
            frame_rate = int(self._num_frames/delta)
            glfw.set_window_title(self._window, f"Running at {frame_rate} fps.")
            self._last_time = self._current_time
            self._num_frames = -1
            self._frame_time = float(1000.0 / max(60,frame_rate))
        self._num_frames += 1

    def quit(self) -> None:
        """
            End the game.
        """
        
        #self._renderer.destroy()
        glfw.terminate()