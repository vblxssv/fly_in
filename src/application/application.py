from src.input import Parser, Content
from src.simulation_engine import Engine
from src.renderer import ArcadeRenderer
from typing import List

import argparse




class Application:
    def __init__(self, args: argparse.Namespace) -> None:

        content: Content = Parser.parse(args.map)
        print(content.nb_drones)

    def run(self) -> None:
        print("bebebe bababab")
