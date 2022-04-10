import ujson
from pathlib import Path
from app.config import Config
from app.factory import create_app


if __name__ == '__main__':
    config_path = str(Path(__file__).parents[0] / 'config.json')
    with open(config_path) as file:
        loaded_config = ujson.load(file)
    app = create_app(loaded_config)
    app.run(**Config.current.sanic)
