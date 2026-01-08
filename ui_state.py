from pydantic import BaseModel

# TODO: Implement checkable

class UINode:
    
    def __init__(self, clickable : bool, bounds: list[int]):
        self.clickable = clickable
        self.bounds = bounds
        self.center = self.__get_center()

    def __get_center(self) -> tuple[int, int]:
        """        
        self.bounds: [x left, x right, y top, y bottom]
        :return: x and y center coors in pixels
        :rtype: tuple[int, int]
        """

        return (
            self.bounds[0] + ((self.bounds[1] - self.bounds[0]) // 2),
            self.bounds[3] + ((self.bounds[3] - self.bounds[2]) // 2)
        )
    
class UIState(BaseModel):
    pass