import argparse


class CLI:
    @staticmethod
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()

        parser.add_argument("--map", required=True)

        parser.add_argument("--logger",
                            required=True, choices=["file", "console"])

        return parser.parse_args()
