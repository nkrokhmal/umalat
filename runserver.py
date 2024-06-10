# - Set environment

import os

from typing import Literal


# used to set config name (see config.py)
os.environ["ENVIRONMENT"] = "production"

"""
- runtime: normal runtime
- test: test runtime
- parallel: parallel runtime in mozzarella, where we have multiple processes running in parallel. In this case we need to create external database connections for each process
"""
os.environ["APP_ENVIRONMENT"]: Literal["runtime", "test", "parallel"] = "runtime"

# - Imports

import click

from utils_ak.loguru import configure_loguru

from app.app import create_app, create_manager


# - Configure loguru

configure_loguru()

# - Set up app


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


# - Run app

if __name__ == "__main__":
    run_app()
