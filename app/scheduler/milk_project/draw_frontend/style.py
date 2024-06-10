from loguru import logger


def f(b):
    try:

        # NOTE: SHOULD NOT HAPPEN IN NEWER VERSIONS SINCE 2021.10.21 (# update 2021.10.21)
        return b.props["boiling_model_name"]
    except:
        logger.error("Boiling model name not found")
        return ""


STYLE = {
    "equipment_check": {"color": "#4BACC6", "text": "Проверка"},
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
        "text": f,
    },
    "red": {"color": "red", "text": "Мойка обородувания"},  # yellow
    "pouring_off": {
        "text": "Слив",
        "color": "#70AD47",  # green
    },
}
