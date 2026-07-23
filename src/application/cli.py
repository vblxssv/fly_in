import argparse


class CLI:
    @staticmethod
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()

        parser.add_argument("--map", required=True)
        parser.add_argument("--algorithm",
                            required=True, choices=["dijkstra", "bfs"])
        parser.add_argument("--renderer",
                            required=True, choices=["console", "arcade"])

        return parser.parse_args()
