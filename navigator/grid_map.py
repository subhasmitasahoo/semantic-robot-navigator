"""Grid map representation for the semantic robot navigator."""

from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class GridMap:
    width: int
    height: int
    grid: List[List[int]]
    objects: Dict[str, Tuple[int, int]]
    dynamic_obstacles: set = None

    @classmethod
    def empty(cls, width: int, height: int) -> "GridMap":
        return cls(width, height, [[0] * width for _ in range(height)], {})

    def __post_init__(self):
        if self.dynamic_obstacles is None:
            self.dynamic_obstacles = set()

    def set_obstacle(self, x:int, y:int) -> None:
        self.grid[y][x] = 1
    
    def place_object(self, obj:str, x:int, y:int) -> None:
        self.objects[obj] = (x, y)
    
    def is_free(self, x:int, y:int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        if (x, y) in self.dynamic_obstacles:
            return False
        return self.grid[y][x] == 0
    
    def neighbors(self, x: int, y: int):
        """4-connected free neighbors (up, down, left, right)."""
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if self.is_free(nx, ny):
                yield nx, ny


# main
if __name__ == "__main__":
    m = GridMap.empty(5, 5)
    m.set_obstacle(2, 2)
    m.place_object("coffee_machine", 4, 4)
    print(m.is_free(2, 2))   # False
    print(m.is_free(0, 0))   # True
    print(m.objects)         # {'coffee_machine': (4, 4)}