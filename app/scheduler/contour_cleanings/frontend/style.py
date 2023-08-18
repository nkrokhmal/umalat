from app.scheduler.time import *


STYLE = {
    "cleaning": {
        "color": "white",
        "text": lambda b: b.props["label"] + f" ({cast_time(b.size[0])[3:]})",
    },
}
