from config import *

class Timeline(Generic[T]):
    """
        A simple class for interpolating some variable
        between two values.
    """


    def __init__(self, 
                 value_a: T, value_b: T, 
                 lifetime: float, end_action: int):
        """
            Initialize a timeline.

            Parameters:

                value_a: start value for interpolation

                value_b: end value for interpolation

                lifetime: duration of interpolation, in milliseconds

                end_action: code for action to take on end
        """

        self._value_a = value_a
        self._value_b = value_b
        self._lifetime = lifetime
        self._t = 0
        self._end_action = end_action

    def update(self, time_elapsed: float) -> "Timeline[T] | None":
        """
            Step the timeline forwards.

            Parameters:

                time_elapsed: how far forward to tick (milliseconds)
            
            Returns:

                the current timeline after updating.
        """

        #tick forwards
        self._t += time_elapsed / self._lifetime

        #current timeline is still valid
        if self._t < 1.0:
            return self
        
        #current timeline is over
        match self._end_action:

            case END_ACTION_DESTROY:
                return None

    def get_value(self) -> T:
        """
            Returns the current interpolated value.
        """

        return (1.0 - self._t) * self._value_a + self._t * self._value_b