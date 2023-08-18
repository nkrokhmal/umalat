from app.scheduler.time import cast_time


STYLE = {
    "cleaning": {
        "color": "white",
        "text": lambda b: b.props["label"] + f" ({cast_time(b.size[0])[3:]})",
    },
}
