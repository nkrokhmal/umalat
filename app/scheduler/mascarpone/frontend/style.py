def _get_boiling_name(b):
    if b.props["is_cream"]:
        return "производство сливок"
    elif b.props["n"] == 0:
        # return "производство маскарпоне на линии/варка ({boiling_volume} литров)"
        # todo maybe: return number of litres
        return "производство маскарпоне на линии/варка"
    else:
        return "производство маскарпоне на линии/produz. Mascarpone"


STYLE = {
    "boiling_num": {"text": "{batch_id}"},
    "boiling_name": {"text": _get_boiling_name},
    "pouring": {"color": "#B8CCE4", "text": "3"},  # blue
    "heating": {"color": "red", "text": "нагрев"},
    "waiting": {"color": "white", "text": "ожидание"},
    "adding_lactic_acid": {"color": "yellow", "text": "4"},
    "ingredient": {"color": "#C0504D", "text": "внесение ингредиентов"},  # brown
    "pumping_off": {
        "color": "#00B0F0",
        "text": lambda b: "перекачивание в 2 бак"
        if b.props["is_cream"]
        else "сепарирование",
    },  # blue
    "pumping_off_pause": {
        "color": "grey",
    },
    "separation": {"color": "#00B0F0", "text": "сепарирование"},  # blue
    "packing_num": {"color": "#92D050", "text": "{batch_id}"},  # light-green
    "packing": {"color": "#C0504D", "text": "фасовка"},  # brown
    "N": {"color": "#F79646", "text": "Н"},  # orange
    "P": {
        "color": lambda b: "#948A54" if not b.props["is_cream"] else "#F79646",
        "text": "П",
    },  # green-grey or orange
    "salting": {"color": "#92D050", "text": "посолка/нормализация"},  # green
    "cream_cheese_boiling_label1": {
        "color": "white",
        "text": lambda b: "Кремчиз/1000л/бак {}".format(
            ",".join([str(x) for x in b.props["sourdoughs"]])
        ),
    },
    "cream_cheese_boiling_label2": {
        "color": "white",
        "text": "Кремчиз 0,18 кг",
    },
    "cooling": {"color": "#F79646", "text": "охлаждение"},  # orange
    "cleaning_separator": {"color": "yellow", "text": "Мойка сепаратора"},
    "cleaning_sourdough_mascarpone": {
        "color": "yellow",
        "text": lambda b: "Мойка заквасочников {}".format(
            ", ".join([f"№{sn}" for sn in b.props["sourdoughs"]])
        ),
    },
    "cleaning_sourdough_mascarpone_cream_cheese": {
        "color": "yellow",
        "text": lambda b: "Мойка заквасочников {}".format(
            ", ".join([f"№{sn}" for sn in b.props["sourdoughs"]])
        ),
    },
    "cleaning_homogenizer": {
        "color": "yellow",
        "text": "Мойка гомогенизатора и фасовочника",
    },
    "cleaning_heat_exchanger": {"color": "yellow", "text": "Мойка теплообменника"},
    "stub": {"visible": False},
    "preparation": {
        "color": "white",
        "text": "подготовка цеха к работе, проверка оборудования",
    },
    "shift": {
        "color": (149, 179, 215),
        "text": lambda b: f"Смена {b.props['shift_num']}",
    },
}
