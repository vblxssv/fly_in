from pydantic import ValidationError
from src.models.factory import GraphFactory


class Application:
    def __init__(self, map_path: str) -> None:
        self.map_path: str = map_path

    def run(self) -> None:
        try:
            graph = GraphFactory.load_from_file(self.map_path)
            print(graph)
        except (OSError, ValidationError) as e:
            print(f"Config error: {e}")
            return
        except ValueError as e:
            print(f"Validation error: {e}")
