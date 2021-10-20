def f(b):
    try:
        return b.props["boiling_model"].name
    except:
        return ""


STYLE = {
    "water_collecting": {
        "color": "#FFFF00",  # yellow
        "text": "Набор воды в машину",
    },
    "mixture_collecting": {
        "color": "#FFC000",  # orange
        "text": "Набор смеси",
    },
    "processing": {
        "color": "#00B0F0",  # blue
        # todo next: fix session bug: sqlalchemy.orm.exc.DetachedInstanceError: Instance <MilkProjectBoiling at 0x7f0b52a93f90> is not bound to a Session; attribute refresh operation cannot proceed
        # "text": lambda b: b.props['boiling_model'].name,
        "text": f,
    },
    "red": {"color": "red"},  # yellow
    "pouring_off": {
        "text": "Слив",
        "color": "#70AD47",  # green
    },
}
