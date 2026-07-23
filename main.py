from src.application import Application, CLI
from pydantic import ValidationError


def main() -> None:
    app = Application(CLI.parse_args())
    app.run()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValidationError, ValueError,
            IndexError, AttributeError) as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nInterrupted")
