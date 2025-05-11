from abc import abstractmethod, ABC
class Latch(ABC):

    @abstractmethod
    def change_state(self, state: bool): pass

    @abstractmethod
    def get_state(self): pass

class ControlLatch(Latch, ABC):
    @abstractmethod
    def bind_ctrl(self, log_el): pass

class LogicalElement(ABC):

    def __init__(self, ctrl_latch: ControlLatch):
        ctrl_latch.bind_ctrl(self)

    @abstractmethod
    def perform_change(self): pass

