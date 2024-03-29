import os

import click

from utils_ak.loguru import configure_loguru


os.environ["ENVIRONMENT"] = "production"
os.environ["APP_ENVIRONMENT"] = "runtime"

from app.app import create_app, create_manager


configure_loguru()


@click.command()
@click.option("--test", is_flag=True, default=False, required=False)
@click.option("--debug", is_flag=True, default=False, required=False)
def run_app(test: bool, debug: bool):
    config_name: str = "test" if test else "default"
    port = 7001 if debug else 5000
    threaded = not debug
    app, rq = create_app(config_name=config_name)
    create_manager(app)
    app.run(port=port, threaded=threaded, host="0.0.0.0", debug=debug)


if __name__ == "__main__":
    run_app()
