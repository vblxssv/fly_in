from src.parser.parser import Parser
from pydantic import ValidationError
from src.models.factory import GraphFactory
from src.models.graph import Graph


class Application:
    def __init__(self, map_path: str) -> None:
        self.map_path: str = map_path

    def run(self) -> None:
        try:
            content = Parser.parse(self.map_path)
            graph: Graph = GraphFactory.create(content)
            print(graph)

        except (OSError, ValidationError) as e:
            print(f"Config error: {e}")
            return
        except ValueError as e:
            print(f"Validation error: {e}")
