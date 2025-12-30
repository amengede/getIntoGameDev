from config import *
import events

class Entity:
    """
        An entity is a drawable object with a position
        and direction which can update.
    """

    def __init__(self, position: list[float], entity_type: int):
        """
            Create an entity at the given position.

            Parameters:

                position: the initial position of the Entity.

                entity_type: code indicating the type of the Entity.
        """

        self._position = np.array(position,dtype=np.float32)
        self._theta = 0
        self._type = entity_type
    
    def get_position(self) -> np.ndarray:
        """
            Returns the Entity's position.
        """

        return self._position
    
    def set_position(self, new_position: np.ndarray) -> None:
        """
            Set the position of the Entity.
        """

        self._position = new_position
    
    def get_direction(self) -> float:
        """
            Returns the Entity's direction.
        """

        return self._theta
    
    def set_direction(self, new_direction: float) -> None:
        """
            Set the direction of the Entity.
        """

        self._theta = new_direction
    
    def get_type(self) -> int:
        """
            Returns the Entity's type code.
        """

        return self._type

    def move_direction(self, direction: float, amount: float) -> None:
        """
            Move the Entity (calculated based on direction).

            Parameters:

                direction: the direction offset (away from forwards) to move

                amount: how far to move
        """

        walk_direction = np.radians((-direction + self._theta) % 360)
        dx = np.cos(walk_direction,dtype=np.float32)
        dy = -np.sin(walk_direction,dtype=np.float32)
        velocity = amount * np.array([dx, dy, 0.0], dtype = np.float32)

        self.move_velocity(velocity)
    
    def move_velocity(self, velocity: vec3) -> None:
        """
            Move the Entity (by adding some vector).

            Parameters:

                velocity: the vector to add to position
        """

        self._position += velocity
    
    def get_model_transform(self) -> np.ndarray:
        """
            Returns the Entity's model transform.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = pyrr.matrix44.create_from_translation(
                vec = self._position, dtype = np.float32)
        )

        return model_transform
    
    def update(self, rate: float) -> None:
        """
            Virtual method, update the Entity.

            Parameters:

                rate: the framerate correction factor.
        """

        pass

class Camera(Entity):
    """
        An entity which also has a frame of reference and can
        make a view transform.
    """

    _ARM_NEAR = np.array([-5.0, -2.0, 1.8], np.float32)
    _ARM_FAR = np.array([-10.0,  0.0, 3.6], np.float32)

    def __init__(self):

        self._theta = 0.0
        self._phi = 0.0

        self._forward = np.array([0, 0, 0],dtype=np.float32)
        self._right = np.array([0, 0, 0],dtype=np.float32)
        self._up = np.array([0, 0, 0],dtype=np.float32)
        self._global_up = np.array([0, 0, 1], dtype=np.float32)
        self._target: Entity = None
        self._arm = Camera._ARM_FAR
        self._zoom: events.Timeline[np.ndarray] = None
    
    def _recalculate_frame_of_reference(self) -> None:
        """
            Recalculate the camera's forwards, right and up vectors.
        """

        if self._target is None:
            print("Error! Target not set!")
            return
        
        #Get a matrix which will position an arm onto the player
        
        target_to_camera_transform = pyrr.matrix44.create_from_y_rotation(
                theta = np.radians(self._phi),
                dtype = np.float32
            )

        target_to_camera_transform = pyrr.matrix44.multiply(
            m1 = target_to_camera_transform,
            m2 = pyrr.matrix44.create_from_z_rotation(
                theta = np.radians(self._theta),
                dtype = np.float32
            )
        )
        target_pos = self._target.get_position()
        target_to_camera_transform = pyrr.matrix44.multiply(
            m1 = target_to_camera_transform,
            m2 = pyrr.matrix44.create_from_translation(
                vec = target_pos, dtype = np.float32)
        )

        #get the camera's position
        pos = pyrr.matrix44.multiply(
            m1 = pyrr.vector4.create_from_vector3(
                vector = self._arm, 
                w = 1.0, dtype = np.float32),
            m2 = target_to_camera_transform
        )
        self._position,_ = pyrr.vector3.create_from_vector4(
            vector = pos, 
            dtype = np.float32)
        
        #get the look target
        pos = pyrr.matrix44.multiply(
            m1 = pyrr.vector4.create(
                0.0, 
                self._arm[1], 
                target_pos[2], 
                1.0, dtype = np.float32),
            m2 = target_to_camera_transform
        )
        target_pos,_ = pyrr.vector3.create_from_vector4(
            vector = pos, 
            dtype = np.float32)
        
        self._forward = pyrr.vector.normalize(target_pos - self._position)
        
        self._right = pyrr.vector.normalize(
            pyrr.vector3.cross(self._global_up,self._forward))
        self._up = pyrr.vector.normalize(
            pyrr.vector3.cross(self._forward,self._right))
        
    def get_frame_of_reference(self) -> tuple[np.ndarray]:
        """
            Get the Camera's forward, right and up vectors
        """

        return (self._forward, self._right, self._up)
    
    def set_follow_target(self, target: Entity) -> None:
        """
            Set the camera's target.

            Parameters:

                target: the Entity to watch.
        """

        self._target = target

    def get_view_transform(self) -> np.ndarray:
        """
            Returns the Camera's view transform.
        """

        return pyrr.matrix44.create_look_at(
            eye = self._position, target = self._position + self._forward,
            up = self._up, dtype=np.float32
        )

    def spin(self, dTheta: float, dPhi: float) -> None:
        """
            Move the camera according to its frame of reference.
        """

        self._theta = (self._theta + dTheta) % 360
        self._phi = min(45, max(-45, self._phi + dPhi))
        self._target.set_direction(self._theta)

    def update(self, frame_time: float) -> None:
        """
            Update the Camera.

            Parameters:

                frame_time: time since last update, in milliseconds.
        """

        if self._zoom is not None:
            self._arm = self._zoom.get_value()
            self._zoom = self._zoom.update(frame_time)
        self._recalculate_frame_of_reference()

    def zoom_in(self) -> None:
        """
            Zoom the camera in.
        """

        self._zoom = events.Timeline[np.ndarray](
            self._arm, Camera._ARM_NEAR, 1000, END_ACTION_DESTROY)
    
    def zoom_out(self) -> None:
        """
            Zoom the camera out.
        """

        self._zoom = events.Timeline[np.ndarray](
            self._arm, Camera._ARM_FAR, 1000, END_ACTION_DESTROY)
    
class Scene:
    """
        Manages all objects and their interactions.
    """


    def __init__(self):
        """
            Create the scene.
        """

        self._create_objects()

    def _create_objects(self) -> None:
        """
            Create all the objects in teh scene.
        """
        
        self._player = Entity(
            position = [100,100,0.9], 
            entity_type = OBJECT_TYPE_PLAYER)
        
        self._camera = Camera()
        self._camera.set_follow_target(self._player)
        
        self._renderables: dict[int, list[Entity]] = {
            OBJECT_TYPE_PLAYER: [self._player],
            OBJECT_TYPE_GROUND: [
                Entity(position=[0,0,0], entity_type=OBJECT_TYPE_GROUND)
            ]
        }
    
    def get_renderables(self) -> dict[int, list[Entity]]:
        """
            Returns the scene's renderable objects
        """

        return self._renderables
    
    def get_camera(self) -> Camera:
        """
            Returns the scene's camera
        """

        return self._camera

    def move_player(self, direction: float, amount: float) -> None:
        """
            Move the player.

            Parameters:

                direction: direction offset for the player, away from forwards

                amount: how far to move the player
        """

        self._player.move_direction(direction, amount)
    
    def spin_camera(self, dTheta: float, dPhi: float) -> None:
        """
            Spin the camera.
        """

        self._camera.spin(dTheta, dPhi)
    
    def update(self, frame_time: float) -> None:
        """
            Update the scene.

            Parameters:

                frame_time: time since last update, in milliseconds.
        """

        self._camera.update(frame_time)
    
    def zoom_camera(self, near: bool) -> None:
        """
            Set the camera zoom.

            Parameters:

                near: whether to zoom in (True) or out (False)
        """

        if near:
            self._camera.zoom_in()
        else:
            self._camera.zoom_out()