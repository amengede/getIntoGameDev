from config import *

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

    def move_direction(self, direction: float, amount: float) -> vec3:
        """
            Move the Entity (calculated based on direction).

            Parameters:

                direction: the direction offset (away from forwards) to move

                amount: how far to move
            
            Returns:

                Returns the Entity's velocity.
        """

        walk_direction = np.radians((direction + self._theta) % 360)
        dx = np.cos(walk_direction,dtype=np.float32)
        dy = np.sin(walk_direction,dtype=np.float32)
        velocity = amount * np.array([dx, dy, 0.0], dtype = np.float32)

        self.move_velocity(velocity)
        return velocity
    
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

    def __init__(self, position: list[float]):

        super().__init__(position=position, entity_type=OBJECT_TYPE_CAMERA)

        self._forward = np.array([0, 0, 0],dtype=np.float32)
        self._right = np.array([0, 0, 0],dtype=np.float32)
        self._up = np.array([0, 0, 0],dtype=np.float32)
        self._global_up = np.array([0, 0, 1], dtype=np.float32)
        self._target: Entity = None
    
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
        
        if self._target is None:
            self._forward = pyrr.vector.normalize(-self._position)
        else:
            self._forward = pyrr.vector.normalize(
                self._target.get_position() - self._position)
        
        self._right = pyrr.vector.normalize(
            pyrr.vector3.cross(self._global_up,self._forward))
        self._up = pyrr.vector.normalize(
            pyrr.vector3.cross(self._forward,self._right))

        return pyrr.matrix44.create_look_at(
            eye = self._position, target = self._position + self._forward, 
            up = self._up, dtype=np.float32
        )

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
            position = [0,0,0.9], 
            entity_type = OBJECT_TYPE_PLAYER)
        
        self._camera = Camera(position = [-7.2,0,3.6])
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

        velocity = self._player.move_direction(direction, amount)
        self._camera.move_velocity(velocity)