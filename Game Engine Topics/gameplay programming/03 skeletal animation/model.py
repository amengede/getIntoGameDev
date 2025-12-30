""" Model classes: Game objects and their interactions. """
from config import *
import events
#region constants
ANIMATION_TYPE_DEFAULT = 0
ANIMATION_TYPE_RUN = 1
ANIMATION_TYPE_RUN_AIM = 2
ANIMATION_TYPE_RUN_SHOOT = 3
ANIMATION_TYPE_STAND = 4
ANIMATION_TYPE_STAND_AIM = 5
ANIMATION_TYPE_STAND_SHOOT = 6

ANIMATION_CODE_LOOKUP = {
    OBJECT_TYPE_PLAYER: {
        "Default": ANIMATION_TYPE_DEFAULT,
        "Run": ANIMATION_TYPE_RUN,
        "Run Aim": ANIMATION_TYPE_RUN_AIM,
        "Run Shoot": ANIMATION_TYPE_RUN_SHOOT,
        "Stand": ANIMATION_TYPE_STAND,
        "Stand Aim": ANIMATION_TYPE_STAND_AIM,
        "Stand Shoot": ANIMATION_TYPE_STAND_SHOOT,
    },
}

ANIMATION_TARGET_SCALE = 0
ANIMATION_TARGET_ROTATION = 1
ANIMATION_TARGET_POS = 2
#endregion
#region helper functions
def load_animations_from_gltf(filename: str,
            object_type: int) -> dict[int, "AnimationComponent"]:
    """
        Load animation data from a gltf file.
    """

    with open(filename, "r") as file:
        data = json.load(file)
        animation_descriptions = data["animations"]
        accessor_descriptions = data["accessors"]
        buffer_views = data["bufferViews"]
        buffer_data = data["buffers"][0]["uri"]
        header, _, buffer_data = buffer_data.partition(",")
        buffer_data = base64.b64decode(buffer_data)
        animation_codes = ANIMATION_CODE_LOOKUP[object_type]
        skin_description = data["skins"][0]
        joint_indices = skin_description["joints"]
        return make_animations(animation_codes,
                                animation_descriptions,
                                accessor_descriptions,
                                buffer_views, buffer_data,
                                joint_indices)

def make_animations(animation_codes: dict[str, int],
                    animation_descriptions: list[dict[str, any]],
                    accessor_descriptions: list[dict[str, any]],
                    buffer_views: list[dict[str, any]],
                    buffer_data: bytes, joint_indices: list[int]) -> dict[int, "AnimationComponent"]:
    """
        Load all of the animations from the given data.

        Parameters:

            animation_codes: look-up table for animation names

            animation_descriptions: describes the animations to load

            accessor_descriptions: all the attribute accessors in the file

            buffer_views: all the buffer views in the file

            buffer_data: the raw binary data where info is stored
    """

    animations = {}
    for animation_description in animation_descriptions:

        channels = make_animation_channels(animation_description, joint_indices)

        samplers = make_animation_samplers(animation_description,
                                            accessor_descriptions,
                                            buffer_views, buffer_data)

        animation_type = animation_codes[animation_description["name"]]
        timestamp_index = animation_description["samplers"][0]["input"]
        timestamps = get_value_list_from_accessor(
            accessor_descriptions[timestamp_index], buffer_views, buffer_data)
        animations[animation_type] = AnimationComponent(timestamps, channels, samplers)

    return animations

def make_animation_channels(animation_description: dict[str, any],
                            joint_indices: list[int]) -> list["AnimationChannel"]:
    """ Create all of the described animation channels """

    channels: list[AnimationChannel] = []
    has_animation = {}
    for channel_description in animation_description["channels"]:
        sampler_index = channel_description["sampler"]
        bone_index = joint_indices.index(channel_description["target"]["node"])
        has_animation[bone_index] = True
        target_attribute = channel_description["target"]["path"]
        target = ANIMATION_TARGET_SCALE
        if target_attribute == "rotation":
            target = ANIMATION_TARGET_ROTATION
        if target_attribute == "translation":
            target = ANIMATION_TARGET_POS
        channels.append(AnimationChannel(sampler_index, bone_index, target))

    return channels

def make_animation_samplers(animation_description: dict[str, any],
                            accessor_descriptions: dict[str, any],
                            buffer_views: dict[str, any],
                            buffer_data: bytes) -> list["AnimationSampler"]:
    """ Make the value samplers for the given animation description """

    samplers: list[AnimationSampler] = []
    for sampler_description in animation_description["samplers"]:
        value_index = sampler_description["output"]
        values = get_value_list_from_accessor(
            accessor_descriptions[value_index],
            buffer_views, buffer_data)
        samplers.append(AnimationSampler(values))
    return samplers

def load_skeleton_from_gltf(filename: str) -> "Skeleton":
    """
        Load node data from a gltf file.
    """

    with open(filename, "r") as file:
        data = json.load(file)
        accessor_descriptions = data["accessors"]
        buffer_views = data["bufferViews"]
        buffer_data = data["buffers"][0]["uri"]
        header, _, buffer_data = buffer_data.partition(",")
        buffer_data = base64.b64decode(buffer_data)
        scene_description = data["scenes"][0]
        root_bone_index = scene_description["nodes"][0]
        node_descriptions = data["nodes"]
        skin_description = data["skins"][0]
        inverse_bind_index = skin_description["inverseBindMatrices"]
        joint_indices = skin_description["joints"]
        inverse_bind_accessor = accessor_descriptions[inverse_bind_index]
        inverse_bind_matrices = get_value_list_from_accessor(
            inverse_bind_accessor, buffer_views, buffer_data)

        bones = []
        for i,joint_index in enumerate(joint_indices):
            node_description = node_descriptions[joint_index]
            rotation = [0, 0, 0, 1] if "rotation" not in node_description\
                else node_description["rotation"]
            scale = [1, 1, 1] if "scale" not in node_description\
                else node_description["scale"]
            translation = [0, 0, 0] if "translation" not in node_description\
                else node_description["translation"]
            children = [] if "children" not in node_description else\
                [joint_indices.index(j) for j in node_description["children"]]
            bones.append(Bone(rotation, scale, translation, children,
                                inverse_bind_matrices[i]))

        return Skeleton(bones)
#endregion
#region components
class TransformComponent:
    """ A tranformation """

    def __init__(self, position: tuple[float] = (0, 0, 0),
                eulers: tuple[float] = (0,0,0)):
        """
            Initialize a new TransformComponent
        """

        self._position = np.array(position, dtype = np.float32)
        self._eulers = np.array(eulers, dtype = np.float32)

    def get_model_transform(self) -> np.ndarray:
        """
            Get the component's model to world transform
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

        eulers = np.radians(self._eulers)

        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = pyrr.matrix44.create_from_x_rotation(
                theta = eulers[0], dtype = np.float32)
        )

        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = pyrr.matrix44.create_from_y_rotation(
                theta = eulers[1], dtype = np.float32)
        )

        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = pyrr.matrix44.create_from_z_rotation(
                theta = eulers[2], dtype = np.float32)
        )

        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = pyrr.matrix44.create_from_translation(
                vec = self._position, dtype = np.float32)
        )

        return model_transform

    def move_direction(self, direction: float, amount: float) -> None:
        """
            Move the Entity (calculated based on direction).

            Parameters:

                direction: the direction offset (away from forwards) to move

                amount: how far to move
        """

        walk_direction = np.radians((-direction + self._eulers[2]) % 360)
        dx = np.cos(walk_direction,dtype=np.float32)
        dy = -np.sin(walk_direction,dtype=np.float32)
        velocity = amount * np.array([dx, dy, 0.0], dtype = np.float32)

        self._position += velocity

    def move_by(self, amount: np.ndarray) -> None:
        """
            Move the Entity
        """

        self._position += amount

    def spin(self, d_eulers: tuple[float],
            constraints: tuple[float] = (-89, 89)) -> None:
        """
            Move the camera according to its frame of reference.
        """

        self._eulers[2] = (self._eulers[2]+ d_eulers[2]) % 360
        self._eulers[1] = min(constraints[1], max(constraints[0], self._eulers[1] + d_eulers[1]))

    def get_position(self) -> np.ndarray:
        """ Get the position """
        return self._position

    def get_eulers(self) -> np.ndarray:
        """ Get the eulers """
        return self._eulers

class CameraComponent:
    """
        A frame of reference.
    """

    _GLOBAL_UP = np.array((0, 0, 1), dtype = np.float32)

    def __init__(self):

        self._forward = np.array([0, 0, 0],dtype=np.float32)
        self._right = np.array([0, 0, 0],dtype=np.float32)
        self._up = np.array([0, 0, 0],dtype=np.float32)

    def update_cross_product(self, eulers: np.ndarray) -> None:
        """
            Recalculate the camera's forwards, right and up vectors.
        """

        eulers = np.radians(eulers)
        c_yaw = np.cos(eulers[2])
        s_yaw = np.sin(eulers[2])
        c_pitch = np.cos(eulers[1])
        s_pitch = np.sin(eulers[1])

        self._forward[0] = c_yaw * c_pitch
        self._forward[1] = s_yaw * c_pitch
        self._forward[2] = s_pitch

        self._right = pyrr.vector.normalize(
            pyrr.vector3.cross(self._GLOBAL_UP,self._forward))
        self._up = pyrr.vector.normalize(
            pyrr.vector3.cross(self._forward,self._right))

    def update_mat_mul(self, transform: np.ndarray) -> None:
        """
            Recalculate the camera's forwards, right and up vectors.
        """

        vec = np.array((0, -1, 0, 0), dtype = np.float32)
        vec = pyrr.matrix44.multiply(
            m1 = vec,
            m2 = transform)

        for i in range(3):
            self._right[i] = vec[i]

        vec[0] = 0
        vec[1] = 0
        vec[2] = 1
        vec[3] = 0
        vec = pyrr.matrix44.multiply(
            m1 = vec,
            m2 = transform)

        for i in range(3):
            self._up[i] = vec[i]

        vec[0] = 1
        vec[1] = 0
        vec[2] = 0
        vec[3] = 0
        vec = pyrr.matrix44.multiply(
            m1 = vec,
            m2 = transform)

        for i in range(3):
            self._forward[i] = vec[i]

    def get_view_transform(self, pos: np.ndarray) -> np.ndarray:
        """
            Returns the Camera's view transform.
        """

        return np.array((
                (self._right[0], self._up[0], -self._forward[0], 0.),
                (self._right[1], self._up[1], -self._forward[1], 0.),
                (self._right[2], self._up[2], -self._forward[2], 0.),
                (-np.dot(self._right, pos), -np.dot(self._up, pos),
                    np.dot(self._forward, pos), 1.0)),
                dtype=np.float32)

    def get_frame_of_reference(self) -> np.ndarray:
        """
            Get basis vectors representing the camera's rotation.
        """

        return (self._right, self._up, self._forward)

class SocketComponent:
    """
        A position onto which other components can be placed.
    """

    _ARM_NEAR = np.array([-5.0, -2.0, 0], np.float32)
    _ARM_FAR = np.array([-10.0,  0.0, 0], np.float32)

    def __init__(self, eulers: tuple[float] = (0,0,0)):

        self._transform_component = TransformComponent(eulers=eulers)

        self._offset = SocketComponent._ARM_FAR
        self._zoom: events.Timeline[np.ndarray] = None

    def get_rotation_matrix(self) -> np.ndarray:
        """
            Get the socket's rotation matrix
        """

        # Rotation of socket
        return self._transform_component.get_model_transform()

    def get_position(self) -> np.ndarray:
        """
            Get the socket's position
        """

        # Rotation of socket
        rotation_transform = self._transform_component.get_model_transform()

        # Position of socket
        pos = pyrr.matrix44.multiply(
            m1 = pyrr.vector4.create_from_vector3(
                vector = self._offset, w = 1.0, dtype = np.float32),
            m2 = rotation_transform
        )
        pos,_ = pyrr.vector3.create_from_vector4(
            vector = pos,
            dtype = np.float32)

        return pos

    def spin(self, d_eulers: list[float], constraints: tuple[float] = (-89, 89)) -> None:
        """
            Spin by the given amount.
        """

        self._transform_component.spin(d_eulers, constraints)

    def update(self, frametime: float) -> None:
        """
            Update the Camera.

            Parameters:

                frametime: time since last update, in milliseconds.
        """

        if self._zoom is not None:
            self._offset = self._zoom.get_value()
            self._zoom = self._zoom.update(frametime)

    def zoom_in(self) -> None:
        """
            Zoom the camera in.
        """

        self._zoom = events.Timeline[np.ndarray](
            self._offset, SocketComponent._ARM_NEAR, 1000, END_ACTION_DESTROY)

    def zoom_out(self) -> None:
        """
            Zoom the camera out.
        """

        self._zoom = events.Timeline[np.ndarray](
            self._offset, SocketComponent._ARM_FAR, 1000, END_ACTION_DESTROY)

class PhysicsComponent:
    """ Physics stuff """


    def __init__(self):
        self._gravity = np.array([0,0,-0.02], dtype=np.float32)
        self._velocity = np.array([0,0,0], dtype=np.float32)

    def update(self, frametime: float) -> np.ndarray:
        """
            Updates the state, returns the amount of movement to apply.
        """

        rate = frametime / 16.67
        self._velocity += rate * self._gravity

        return rate * self._velocity

    def hit_ground(self) -> None:
        """
            The object has hit the ground, reset it.
        """

        self._velocity[2] = 0.0

    def get_velocity(self) -> np.ndarray:
        """ Get the velocity """
        return self._velocity

class Bone:
    """ A bone """


    def __init__(self,
                rotation: tuple[float],
                scale: tuple[float],
                translation: tuple[float], 
                child_indices: list[int],
                inverse_bind_matrix: np.ndarray):

        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)
        self.translation = np.array(
            (translation[0], translation[1], translation[2], 1), dtype=np.float32)
        self.child_indices = child_indices

        self.inverse_bind_matrix = inverse_bind_matrix

    def get_transform(self) -> np.ndarray:

        transform = pyrr.matrix44.multiply(
            m1 = pyrr.matrix44.create_from_scale(self.scale, dtype=np.float32),
            m2 = pyrr.matrix44.create_from_quaternion(self.rotation, dtype=np.float32).T)
        transform = pyrr.matrix44.multiply(
            m1 = transform,
            m2 = pyrr.matrix44.create_from_translation(self.translation, dtype=np.float32))
        return transform

class Skeleton:
    """ Manages a group of bones """


    def __init__(self, bones: list[Bone]):

        self.bones = bones
        self.transforms = [pyrr.matrix44.create_identity(dtype=np.float32) for _ in range(len(bones))]

        #parent lookup: for a given bone, what is its parent?
        self._parent_index_lookup = {}
        for i,bone in enumerate(bones):
            for child_index in bone.child_indices:
                self._parent_index_lookup[child_index] = i

    def get_bone_transforms(self) -> list[np.ndarray]:
        """
            Get the set of transformations of all bones.
        """

        # For each bone, calculate its local transform and then get out of
        # the bone's local space
        for i, bone in enumerate(self.bones):
            transform = bone.get_transform()
            self.transforms[i] = transform

            parent_index = -1 if i not in self._parent_index_lookup\
                else self._parent_index_lookup[i]

            # no parent: we're done with this bone
            if parent_index < 0:
                continue

            self.transforms[i] = pyrr.matrix44.multiply(
                m1 = self.transforms[i],
                m2 = self.transforms[parent_index])

        # finally, pre-multiply the bone's inverse bind matrix
        # this needs to be done after the hiearchies are calculated
        for i, bone in enumerate(self.bones):
            self.transforms[i] = pyrr.matrix44.multiply(
                m1 = bone.inverse_bind_matrix,
                m2 = self.transforms[i])

        return self.transforms

class AnimationChannel:
    """ Animates an attribute of a bone """


    def __init__(self, sampler_index: int, bone_index: int, target: int):
        self.sampler_index = sampler_index
        self.bone_index = bone_index
        self.target = target

class AnimationSampler:
    """ Interpolates a collection of values """


    def __init__(self, values: list[np.ndarray]):
        self.values = values

    def lerp(self, index_a: int, index_b: int, alpha: float) -> np.ndarray:
        """ Linearly interpolate from the given index to the next """

        return (1.0 - alpha) * self.values[index_a] + alpha * self.values[index_b]

    def quat_slerp(self, index_a: int, index_b: int, alpha: float) -> np.ndarray:
        """ Linearly interpolate from the given index to the next """

        q1 = self.values[index_a]
        q2 = self.values[index_b]

        dot = np.dot(q1, q2)

        if dot < 0.0:
            dot = -dot
            q3 = -q2
        else:
            q3 = q2

        if dot < 0.95:
            angle = np.arccos(dot)
            res = (q1 * np.sin(angle * (1 - alpha)) + q3 * np.sin(angle * alpha)) / np.sin(angle)
        else:
            res = (1.0 - alpha) * q1 + alpha * q3

        return res

class AnimationComponent:
    """
        An animation, holds the keyframes for an animation and can be used to rig a
        skeleton.
    """


    def __init__(self,
                    timestamps: list[float],
                    channels: list[AnimationChannel],
                    samplers: list[AnimationSampler]):
        """
            Initialize a new animation.

            Parameters:

                timestamps: times at which to keyframes apply (in seconds)

                channels: transform actions to apply at each keyframe

                samplers: numeric values to interpolate between keyframes
        """
        self._timestamps = np.array(timestamps, dtype=np.float32)
        self._channels = channels
        self._samplers = samplers

    def has_overrun(self, t: float) -> bool:
        """ Returns whether the animation has run overtime """
        return t > self._timestamps[-1]

    def get_duration(self) -> float:
        """ Returns the animation's duration, in seconds """
        return self._timestamps[-1]

    def skin(self, skeleton: Skeleton, t: float) -> None:
        """
            Calculate the bone transforms for the given skeleton at the given time
            value (in seconds)
        """

        index_a, index_b, alpha = self._get_interpolation_data(t)
        #print(index_a, index_b, alpha)
        for channel in self._channels:
            sampler = self._samplers[channel.sampler_index]
            bone = skeleton.bones[channel.bone_index]
            if channel.target == ANIMATION_TARGET_ROTATION:
                bone.rotation = sampler.quat_slerp(index_a, index_b, alpha)
            if channel.target == ANIMATION_TARGET_SCALE:
                bone.scale = sampler.lerp(index_a, index_b, alpha)
            if channel.target == ANIMATION_TARGET_POS:
                bone.translation = sampler.lerp(index_a, index_b, alpha)

    def _get_interpolation_data(self, t: float) -> tuple[int, int, float]:
        """
            Work out which span the given time value is on, and how far it is
            across that span.

            returns: index_a, index_b, alpha
        """

        # get into the appropriate range
        duration = self._timestamps[-1]
        while t > duration:
            t -= duration

        index_a = -1
        searching = True
        while searching:

            searching = t > self._timestamps[index_a + 1]
            if searching:
                index_a += 1

        index_a = index_a % len(self._timestamps)
        index_b = (index_a + 1) % len(self._timestamps)

        time_a = self._timestamps[index_a]
        time_b = self._timestamps[index_b]
        # loop around
        if time_a > time_b:
            t += duration
            time_b += duration
        if time_a == time_b:
            t -= duration
            index_a = (index_a + 1) % len(self._timestamps)
            index_b = (index_b + 1) % len(self._timestamps)
            time_a = self._timestamps[index_a]
            time_b = self._timestamps[index_b]

        return (index_a, index_b, (t - time_a) / (time_b - time_a))
#endregion
#region game objects
class Player:
    """
        A player
    """

    def __init__(self, position: list[float],
                animations: dict[int, AnimationComponent],
                filename: str):
        """
            Initialize a new player

            Parameters:

                position: position of the player

                animations: Animation components holding
                            player's animations
                
                filename: filename pointing to player's model,
                        so they can build their skeleton
        """

        self._transform_component = TransformComponent(position, eulers = (-90, 0, 90))
        self._camera_component = CameraComponent()
        self._arm_component = SocketComponent(eulers=(0,0,0))
        self._physics_component = PhysicsComponent()
        self._animation_components = animations
        self._skeleton_component = load_skeleton_from_gltf(filename)
        self._animation_code = ANIMATION_TYPE_RUN_SHOOT
        pyrr.quaternion.slerp
        self._animation_t = 0.0

        self._jumps = 0

    def get_frame_of_reference(self) -> tuple[np.ndarray]:
        """
            Get the Camera's forward, right and up vectors
        """

        return self._camera_component.get_frame_of_reference()

    def get_view_transform(self) -> np.ndarray:
        """
            Returns the Camera's view transform.
        """

        camera_pos = self._arm_component.get_position() +\
            self._transform_component.get_position()
        return self._camera_component.get_view_transform(camera_pos)

    def spin_camera_arm(self, d_eulers: list[float]) -> None:
        """
            Move the camera arm.
        """

        self._arm_component.spin(d_eulers, constraints = (-45, 45))

    def update(self, frametime: float) -> None:
        """
            Update the Camera.

            Parameters:

                frametime: time since last update, in milliseconds.
        """

        self._arm_component.update(frametime)
        rotation_matrix = self._arm_component.get_rotation_matrix()
        self._camera_component.update_mat_mul(rotation_matrix)

        velocity = self._physics_component.update(frametime)

        position = self._transform_component.get_position()

        #apply velocity
        position += velocity

        #ground check
        if position[2] <= 0.9:
            self._physics_component.hit_ground()
            position[2] = 0.9
            self._jumps = 0

        #animation
        self._animation_t += 0.0005 * frametime
        animation_component = self._animation_components[self._animation_code]
        if animation_component.has_overrun(self._animation_t):
            self._animation_t -= animation_component.get_duration()
        animation_component.skin(self._skeleton_component, self._animation_t)

    def move(self, amount: np.ndarray) -> None:
        """
            Move the Entity (calculated based on direction).

            Parameters:

                direction: the direction offset (away from forwards) to move

                amount: how far to move
        """

        direction_vectors = self._camera_component.get_frame_of_reference()
        movement = direction_vectors[0] * amount[0] +\
            direction_vectors[1] * amount[1] +\
            direction_vectors[2] * amount[2]

        self._transform_component.move_by(movement)

    def spin(self, d_eulers: list[float]) -> None:
        """ Spin the player """

        self._transform_component.spin(d_eulers)

    def jump(self) -> None:
        """
            Make the camera jump.
        """

        if self._jumps < 4:
            self._jumps += 1
            self._physics_component.get_velocity()[2] += 0.8

    def zoom_in(self) -> None:
        """
            Zoom the camera in.
        """

        self._arm_component.zoom_in()

    def zoom_out(self) -> None:
        """
            Zoom the camera out.
        """

        self._arm_component.zoom_out()

class Entity:
    """
        An entity is a drawable object with a position
        and direction which can update.
    """

    def __init__(self, position: list[float]):
        """
            Create an entity at the given position.

            Parameters:

                position: the initial position of the Entity.

                entity_type: code indicating the type of the Entity.
        """

        self._transform_component = TransformComponent(position = position)
#endregion
class Scene():
    """
        Manages all objects and their interactions.
    """


    def __init__(self):
        """
            Create the scene.
        """

        self._create_objects()
        self._event_queue: list[events.Event] = []

    def _create_objects(self) -> None:
        """
            Create all the objects in teh scene.
        """
        filename = "models/Revy.gltf"
        animations = load_animations_from_gltf(filename, OBJECT_TYPE_PLAYER)
        self._player = Player(
            position = [100,100,0.9],
            animations = animations,
            filename = filename)

        self._renderables: dict[int, list[Entity]] = {
            OBJECT_TYPE_PLAYER: [self._player],
            OBJECT_TYPE_GROUND: [
                Entity(position=[0,0,0])
            ]
        }

    def get_event_queue(self) -> list[events.Event]:
        """
            Returns a handle to the scene's event queue.
        """

        return self._event_queue

    def get_renderables(self) -> dict[int, list[Entity]]:
        """
            Returns the scene's renderable objects
        """

        return self._renderables

    def get_camera(self) -> Player:
        """
            Returns the scene's camera
        """

        return self._player

    def move_player(self, amount: np.ndarray) -> None:
        """
            Move the player by the given amount in the camera's (right, up, forwards)
            vectors
        """

        self._player.move(amount)

    def spin_camera(self, d_eulers: list[float]) -> None:
        """
            Spin the camera.
        """

        self._player.spin_camera_arm(d_eulers)

    def update(self, frametime: float) -> None:
        """
            Update the scene.

            Parameters:

                frametime: time since last update, in milliseconds.
        """

        self._handle_events()
        self._player.update(frametime)

    def _handle_events(self) -> None:
        """
            flush the event queue, handing relevant
            events.
        """

        for _ in range(len(self._event_queue)):
            event = self._event_queue.pop(0)
            if event.get_type() == events.JUMP:
                self._player.jump()

    def zoom_camera(self, near: bool) -> None:
        """
            Set the camera zoom.

            Parameters:

                near: whether to zoom in (True) or out (False)
        """

        if near:
            self._player.zoom_in()
        else:
            self._player.zoom_out()
