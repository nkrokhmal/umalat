import os

import click


os.environ["ENVIRONMENT"] = "production"
os.environ["APP_ENVIRONMENT"] = "runtime"

from app.app import create_app, create_manager


@click.command()
@click.option("--test", is_flag=True, default=False, required=False)
@click.option("--debug", is_flag=True, default=False, required=False)
def run_app(test: bool, debug: bool):
    config_name: str = "test" if test else "default"
    app, rq = create_app(config_name=config_name)
    create_manager(app)
    app.run(port=5000, threaded=False, host="0.0.0.0", debug=debug)


if __name__ == "__main__":
    run_app()
