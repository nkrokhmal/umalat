STYLE = {
    "boiling_num": {"text": "{boiling_id}"},
    "boiling_name": {"text": "{boiling_id}"},
    "pouring": {"color": "#B8CCE4", "text": "3"},  # blue
    "heating": {"color": "red", "text": "нагрев"},
    "waiting": {"color": "white", "text": "ожидание"},
    "adding_lactic_acid": {"color": "yellow", "text": "4"},
    "separation": {"color": "#00B0F0", "text": "сепарирование"},  # blue
    "packing_num": {"color": "#92D050", "text": "{batch_id}"},  # light-green
    "packing": {"color": "#C0504D", "text": "фасовка"},  # brown
    "N": {"color": "#F79646", "text": "Н"},  # orange
    "P": {"color": "#948A54", "text": "П"},  # green-grey
    "salting": {"color": "#92D050", "text": "посолка/нормализация"},  # green
    "cream_cheese_boiling_label1": {"color": "white"},
    "cream_cheese_boiling_label2": {"color": "white"},
    "cooling": {"color": "#F79646", "text": "охлаждение"},  # orange
    "cleaning_separator": {"color": "yellow", "text": "Мойка сепаратора"},
    "cleaning_sourdough_mascarpone": {
        "color": "yellow",
        "text": lambda b: "Мойка заквасочников {}".format(
            ", ".join([f"№{line_num + 1}" for line_num in b.props["line_nums"]])
        ),
    },
    "cleaning_homogenizer": {
        "color": "yellow",
        "text": "Мойка гомогенизатора и фасовочника",
    },
    "cleaning_heat_exchanger": {"color": "yellow", "text": "Мойка теплообменника"},
    "stub": {"visible": False},
}
