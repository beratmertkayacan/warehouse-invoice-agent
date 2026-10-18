import uvicorn

from app.config import load_settings
from app.main import app


def main() -> None:
    uvicorn.run(app, host="127.0.0.1", port=load_settings().port)


if __name__ == "__main__":
    main()
