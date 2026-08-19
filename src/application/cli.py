import argparse


class CLI:
    """Define and parse the application's command-line interface."""

    @staticmethod
    def parse_args() -> argparse.Namespace:
        """Parse required map and logger options from the command line."""
        parser = argparse.ArgumentParser()

        parser.add_argument("--map", required=True)

        parser.add_argument("--logger",
                            required=True, choices=["file", "console"])

        return parser.parse_args()
