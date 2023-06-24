############################## Imports   ######################################
#region
from config import *
import model
import view
#endregion
############################## Constants ######################################
#region
GLOBAL_X = np.array([1,0,0], dtype=np.float32)
GLOBAL_Y = np.array([0,1,0], dtype=np.float32)
GLOBAL_Z = np.array([0,0,1], dtype=np.float32)
#endregion
##################################### Control #################################
#region
class App:
    """
        The control class.
    """
    __slots__ = (
        "window", "renderer", "scene", "last_time", 
        "current_time", "frames_rendered", "frametime",
        "_keys")


    def __init__(self):
        """
            Initialize the program.
        """

        self._set_up_glfw()

        self._set_up_timer()

        self._set_up_input_systems()

        self._create_assets()

    def _set_up_glfw(self) -> None:
        """
            Initialize and configure GLFW
        """

        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,4)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
        #for uncapped framerate
        glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER,GL_FALSE) 
        self.window = glfw.create_window(
            SCREEN_WIDTH, SCREEN_HEIGHT, "Title", None, None)
        glfw.make_context_current(self.window)
    
    def _set_up_timer(self) -> None:
        """
            Initialize the variables used by the framerate
            timer.
        """

        self.last_time = glfw.get_time()
        self.current_time = 0
        self.frames_rendered = 0
        self.frametime = 0.0
    
    def _set_up_input_systems(self) -> None:
        """
            Configure the mouse and keyboard
        """

        glfw.set_input_mode(
            self.window, 
            GLFW_CONSTANTS.GLFW_CURSOR, 
            GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
        )

        self._keys = {}
        glfw.set_key_callback(self.window, self._key_callback)
    
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
    
    def _create_assets(self) -> None:
        """
            Create all of the assets needed by the program.
        """

        self.renderer = view.GraphicsEngine()
        self.renderer.register_entity(
            PIPELINE_TYPE["STANDARD"], ENTITY_TYPE["CUBE"])
        self.renderer.register_entity(
            PIPELINE_TYPE["EMISSIVE"], ENTITY_TYPE["POINTLIGHT"])

        self.scene = model.Scene()
    
    def run(self) -> None:
        """
            Run the program.
        """

        running = True
        while (running):
            #check events
            if glfw.window_should_close(self.window) \
                or self._keys.get(GLFW_CONSTANTS.GLFW_KEY_ESCAPE, False):
                running = False
            
            self._handle_keys()
            self._handle_mouse()

            glfw.poll_events()

            self.scene.update(self.frametime / 16.67)
            
            self.renderer.render(
                self.scene.player, self.scene.entities, 
                self.scene.entity_counts)

            #timing
            self._calculate_framerate()

    def _handle_keys(self) -> None:
        """
            Takes action based on the keys currently pressed.
        """

        rate = 0.005*self.frametime
        d_pos = np.zeros(3, dtype=np.float32)

        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_W, False):
            d_pos += GLOBAL_X
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_A, False):
            d_pos -= GLOBAL_Y
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_S, False):
            d_pos -= GLOBAL_X
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_D, False):
            d_pos += GLOBAL_Y

        length: float = pyrr.vector.length(d_pos)

        if abs(length) < 0.00001:
            return

        d_pos = rate / length * d_pos

        self.scene.move_player(d_pos)

    def _handle_mouse(self) -> None:
        """
            spin the player based on the mouse movement
        """

        (x,y) = glfw.get_cursor_pos(self.window)
        d_eulers = 0.02 * ((SCREEN_WIDTH / 2) - x) * GLOBAL_Z
        d_eulers += 0.02 * ((SCREEN_HEIGHT / 2) - y) * GLOBAL_Y
        self.scene.spin_player(d_eulers)
        glfw.set_cursor_pos(self.window, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def _calculate_framerate(self) -> None:
        """
            Calculate the framerate and frametime,
            and update the window title.
        """

        self.current_time = glfw.get_time()
        delta = self.current_time - self.last_time
        if (delta >= 1):
            framerate = max(1,int(self.frames_rendered/delta))
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.last_time = self.current_time
            self.frames_rendered = -1
            self.frametime = float(1000.0 / max(1,framerate))
        self.frames_rendered += 1
    
    def quit(self):
        
        self.renderer.destroy()
#endregion
###############################################################################