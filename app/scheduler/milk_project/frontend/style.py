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
        # "text": lambda b: b.props['boiling_model'].name,
        "text": f,
    },
    "red": {"color": "red"},  # yellow
    "pouring_off": {
        "text": "Слив",
        "color": "#70AD47",  # green
    },
}
