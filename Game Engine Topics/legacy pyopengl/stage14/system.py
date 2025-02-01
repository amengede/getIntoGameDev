from constants import *

class State:

    def update(self, frametime: float) -> int:

        return STATE_NO_CHANGE
    
    def enter(self) -> None:

        pass

    def exit(self) -> None:

        pass

class System:

    def __init__(self):

        self.states: dict[int, State] = {}
        self.state: State = None
    
    def update(self, frametime: float) -> int:

        return self.state.update(frametime)
    
    def change_state(self, new_state: int) -> None:

        if new_state not in self.states:
            return

        if self.state:
            self.state.exit()
        self.state = self.states[new_state]
        self.state.enter()
