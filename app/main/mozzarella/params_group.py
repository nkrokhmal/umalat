from flask import render_template
from .. import main
from ... import db
from ...models import Group


@main.route("/mozzarella/get_group", methods=["GET", "POST"])
def get_group():
    groups = db.session.query(Group).all()
    return render_template(
        "mozzarella/get_group.html", groups=groups, endpoints=".get_group"
    )
