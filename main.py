from pydantic import ValidationError
from src.application.application import Application
import sys


def main() -> None:
    app = Application(sys.argv[1])
    app.run()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValidationError, ValueError, IndexError) as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted")
