from config import *
from constants import *

#---- Base Components ----#
#region
class TransformComponent:
    """
        Info needed to describe a transformation.
    """


    def __init__(self, position: vec = [0,0,0], eulers: vec = [0,0,0]):
        """
            Create a new TransformComponent.

            Parameters:

                position: the initial position.

                eulers: the initial rotation.
        """

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.matrix = pyrr.matrix44.create_identity(dtype=np.float32)
    
    def update(self) -> None:
        """
            Construct a new transform matrix which corresponds to the
            component's rotation and translation.
        """

        self.matrix = pyrr.matrix44.create_identity(dtype=np.float32)
        self.matrix = pyrr.matrix44.multiply(
            self.matrix,
            pyrr.matrix44.create_from_x_rotation(theta=self.eulers[0], dtype=np.float32)
        )
        self.matrix = pyrr.matrix44.multiply(
            self.matrix,
            pyrr.matrix44.create_from_y_rotation(theta=self.eulers[1], dtype=np.float32)
        )
        self.matrix = pyrr.matrix44.multiply(
           self.matrix,
            pyrr.matrix44.create_from_z_rotation(theta=self.eulers[2], dtype=np.float32)
        )
        self.matrix = pyrr.matrix44.multiply(
            self.matrix,
            pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)
        )

class RenderComponent:
    """
        Needed in order to render a mesh with a material.
    """


    def __init__(self, mesh_type: int, material_type: int):
        """
            Create a new RenderComponent.

            Parameters:

                mesh_type: the type of mesh to render. See constants.py

                material_type: the type of material to render. See constants.py
        """

        self.mesh_type = mesh_type
        self.material_type = material_type

class LightComponent:
    """
        Describes a light.
    """

    def __init__(self, color: vec, strength: float):
        """
            Create a new LightComponent.
        """

        self.color = np.array(color, dtype=np.float32)
        self.strength = strength

class CameraComponent:
    """
        Represents a camera.
    """


    def __init__(self):
        """
            Create a new CameraComponent
        """

        self.forwards = np.zeros(3, dtype = np.float32)

        self.global_up = np.array([0,0,1], dtype=np.float32)

        self.matrix = pyrr.matrix44.create_identity(dtype=np.float32)
    
    def update(self, position: np.ndarray, eulers: np.ndarray) -> None:
        """
            Calculate the lookat matrix of the camera.

            Parameters:

                position: where to look from

                eulers: rotation of camera
        """

        self.forwards[0] = np.cos(eulers[2]) * np.cos(eulers[1])
        self.forwards[1] = np.sin(eulers[2]) * np.cos(eulers[1])
        self.forwards[2] = np.sin(eulers[1])

        right = np.cross(self.forwards, self.global_up)

        up = np.cross(right, self.forwards)

        self.matrix = pyrr.matrix44.create_look_at(
            eye = position,
            target = position + self.forwards,
            up = up, 
            dtype = np.float32
        )
#endregion
#---- Objects ----#
#region
class StaticModel:
    """
        A basic model. Doesn't move or anything.
    """

    def __init__(self, position: vec, mesh_type: int, material_type: int):
        """
            Create a new StaticModel.
        """

        self.transform = TransformComponent(position)
        self.render = RenderComponent(mesh_type, material_type)
        self.transform.update()

class BillBoard:
    """
        A simple object which always faces towards the camera.
    """

    def __init__(self, position: vec, 
                 mesh_type: int, material_type: int):
        """
            Create a new Billboard.
        """

        self.transform = TransformComponent(position)
        self.render = RenderComponent(mesh_type, material_type)
    
    def update(self, target: np.ndarray) -> None:
        """
            Turn to face the given target position.
        """
        
        direction_from_player = self.transform.position - target
        self.transform.eulers[2] = np.arctan2(-direction_from_player[1],
                                              direction_from_player[0])
        dist_2d = math.sqrt(direction_from_player[0] ** 2 + direction_from_player[1] ** 2)
        self.transform.eulers[1] = np.arctan2(direction_from_player[2], 
                                              dist_2d)
        self.transform.update()

class Light:
    """
        It is, get this, a light.
    """


    def __init__(self, position: vec, 
                 color: vec, strength: float, 
                 mesh_type: int, material_type: int):
        """
            Create a new light.
        """

        self.transform = TransformComponent(position)
        self.light = LightComponent(color, strength)
        self.render = RenderComponent(mesh_type, material_type)
    
    def update(self, target: np.ndarray) -> None:
        """
            Turn to face the given target position.
        """
        
        direction_from_player = self.transform.position - target
        self.transform.eulers[2] = np.arctan2(-direction_from_player[1],
                                              direction_from_player[0])
        dist_2d = math.sqrt(direction_from_player[0] ** 2 + direction_from_player[1] ** 2)
        self.transform.eulers[1] = np.arctan2(direction_from_player[2], 
                                              dist_2d)
        self.transform.update()

class Player:


    def __init__(self, position: vec):
        """
            Create a new Player
        """

        self.transform = TransformComponent(position)
        self.camera = CameraComponent()
    
    def update(self):

        self.camera.update(self.transform.position, self.transform.eulers)

class Scene:


    def __init__(self):

        self.lit_objects = []
        self.unlit_objects = []

        self.cubes = [
            StaticModel(
                position = [-5,-6,1],
                mesh_type = CUBE_MESH,
                material_type = WOOD_MATERIAL
            ),
            StaticModel(
                position = [-5,-4,1],
                mesh_type = CUBE_MESH,
                material_type = CLAYBRICK_MATERIAL
            ),
            StaticModel(
                position = [-5,-2,1],
                mesh_type = CUBE_MESH,
                material_type = HOTEL_WALL_MATERIAL
            ),
            StaticModel(
                position = [-5,0,1],
                mesh_type = CUBE_MESH,
                material_type = GLASS_WALL_MATERIAL
            ),
            StaticModel(
                position = [-5,0,1],
                mesh_type = CUBE_MESH,
                material_type = PLASTER_MATERIAL
            ),
            StaticModel(
                position = [-5,0,1],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_BRASS_MATERIAL
            ),
            StaticModel(
                position = [-5,0,1],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_COLD_MATERIAL
            ),
            StaticModel(
                position = [-3,-6,3],
                mesh_type = CUBE_MESH,
                material_type = WOOD_MATERIAL
            ),
            StaticModel(
                position = [-3,-4,3],
                mesh_type = CUBE_MESH,
                material_type = CLAYBRICK_MATERIAL
            ),
            StaticModel(
                position = [-3,-2,3],
                mesh_type = CUBE_MESH,
                material_type = HOTEL_WALL_MATERIAL
            ),
            StaticModel(
                position = [-3,0,3],
                mesh_type = CUBE_MESH,
                material_type = GLASS_WALL_MATERIAL
            ),
            StaticModel(
                position = [-3,0,3],
                mesh_type = CUBE_MESH,
                material_type = PLASTER_MATERIAL
            ),
            StaticModel(
                position = [-3,0,3],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_BRASS_MATERIAL
            ),
            StaticModel(
                position = [-3,0,3],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_COLD_MATERIAL
            ),
            StaticModel(
                position = [-1,-6,5],
                mesh_type = CUBE_MESH,
                material_type = WOOD_MATERIAL
            ),
            StaticModel(
                position = [-1,-4,5],
                mesh_type = CUBE_MESH,
                material_type = CLAYBRICK_MATERIAL
            ),
            StaticModel(
                position = [-1,-2,5],
                mesh_type = CUBE_MESH,
                material_type = HOTEL_WALL_MATERIAL
            ),
            StaticModel(
                position = [-1,0,5],
                mesh_type = CUBE_MESH,
                material_type = GLASS_WALL_MATERIAL
            ),
            StaticModel(
                position = [-1,0,5],
                mesh_type = CUBE_MESH,
                material_type = PLASTER_MATERIAL
            ),
            StaticModel(
                position = [-1,0,5],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_BRASS_MATERIAL
            ),
            StaticModel(
                position = [-1,0,5],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_COLD_MATERIAL
            ),
            StaticModel(
                position = [1,-6,7],
                mesh_type = CUBE_MESH,
                material_type = WOOD_MATERIAL
            ),
            StaticModel(
                position = [1,-4,7],
                mesh_type = CUBE_MESH,
                material_type = CLAYBRICK_MATERIAL
            ),
            StaticModel(
                position = [1,-2,7],
                mesh_type = CUBE_MESH,
                material_type = HOTEL_WALL_MATERIAL
            ),
            StaticModel(
                position = [1,0,7],
                mesh_type = CUBE_MESH,
                material_type = GLASS_WALL_MATERIAL
            ),
            StaticModel(
                position = [1,0,7],
                mesh_type = CUBE_MESH,
                material_type = PLASTER_MATERIAL
            ),
            StaticModel(
                position = [1,0,7],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_BRASS_MATERIAL
            ),
            StaticModel(
                position = [1,0,7],
                mesh_type = CUBE_MESH,
                material_type = MARBLE_COLD_MATERIAL
            )
        ]

        self.medkits = [
            BillBoard(
                position = [3,0,0.5],
                mesh_type = MEDKIT_MESH,
                material_type = MEDKIT_MATERIAL
            )
        ]

        self.smoke_clouds = []
        for _ in range(100):

            x = 10 * (1 - 2 * np.random.random())
            y = 10 * (1 - 2 * np.random.random())
            z = 2 * np.random.random()

        self.containers = [
            StaticModel(
                position = [0,0,0],
                mesh_type = CONTAINER_MESH,
                material_type = CLAYBRICK_MATERIAL
            ),
        ]

        self.lights = [
            Light(
                position = [
                    4.0, 
                    -4.0 + i, 
                    1.0
                ],
                color = [
                    np.random.uniform(low=0.0, high=1.0), 
                    np.random.uniform(low=0.0, high=1.0), 
                    np.random.uniform(low=0.0, high=1.0)
                ],
                strength = 3,
                mesh_type = LIGHT_MESH,
                material_type = LIGHT_MATERIAL
            )
            for i in range(8)
        ]

        self.player = Player(position = [0,0,2])

        for obj in self.cubes:
            self.lit_objects.append(obj)
        
        for obj in self.containers:
            self.lit_objects.append(obj)
        
        for obj in self.lights:
            self.unlit_objects.append(obj)

        for obj in self.medkits:
            self.lit_objects.append(obj)

    def update(self, rate):

        player_position = self.player.transform.position
        
        for medkit in self.medkits:
            medkit.update(player_position)

        for light in self.lights:
            light.update(player_position)
        
        self.player.update()
    
    def move_player(self, dPos):

        dPos = 0.4 * np.array(dPos, dtype = np.float32)
        self.player.transform.position += dPos
    
    def spin_player(self, dTheta, dPhi):

        eulers = self.player.transform.eulers
        eulers[2] += 0.4 * np.radians(dTheta)
        if eulers[2] > 2 * np.pi:
            eulers[2] -= 2 * np.pi
        elif eulers[2] < 0:
            eulers[2] += 2 * np.pi
        
        eulers[1] = min(
            np.radians(89), 
            max(np.radians(-89), eulers[1] + 0.4 * np.radians(dPhi)))