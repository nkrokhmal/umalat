STYLE = {
    "pouring": {"text": "прием", "color": "yellow"},
    "salting": {"text": "посолка", "color": "#92D050"},
    "pumping": {"text": "П", "color": "#948A54"},
    "analysis": {"text": "анализ", "color": "white"},
    "packing": {"text": "фасовка", "color": "#C0504D"},
    "separation": {"text": lambda b: f'Сепарирование {b.props["group"]}', "color": "#00B0F0"},
    "heating": {"text": "нагрев", "color": "#F79646"},
    "ingredient": {"text": "ингредиенты", "color": "#92D050"},
    "cleaning": {"text": lambda b: f'Мойка {b.props["cleaning_object"]}', "color": "yellow"},
    "separator_acceleration": {"text": "разгон сепаратора", "color": "#C4D79B"},
    "boiling_header": {"text": lambda b: f"Варки {b.props['group']}", "color": "white"},
    # "boiling_num": {"text": "{boiling_id}"},
    # "boiling_name": {"text": "{boiling_label}"},
    # "heating": {"color": "yellow"},
    # "delay": {"color": "red"},
    # "protein_harvest": {"color": "#00B0F0"},  # blue
    # "abandon": {"color": "#00B050"},  # green
    # "pumping_out": {"color": "#9ECBDB"},  # blue
    # "stub": {"visible": False},
    # "preparation": {"color": "#00B0F0", "text": "1"},  # blue
    # "analysis": {"color": "#00B0F0", "text": "2"},  # blue
    # "pumping": {"color": "#00B0F0", "text": "3"},  # blue
    # "packing_num": {"color": "#FFC000", "text": "{boiling_id}"},  # orange
    # "packing": {"color": "#FFC000", "text": "{brand_label}"},  # orange
    # "bath_cleaning_1": {"color": "#4F81BD"},  # blue
    # "bath_cleaning_2": {"color": "#C0504D"},  # red
    # "bath_cleaning_3": {"color": "#4F81BD"},  # blue
    # "bath_cleaning_4": {"color": "#FCD5B4"},  # beige
    # "bath_cleaning_5": {"color": "#4F81BD"},  # blue
    # "container_cleaning_1": {"color": "yellow", "text": "Мойка бака №1"},
    # "container_cleaning_2": {"color": "yellow", "text": "Мойка бака №2"},
    # "container_cleaning_3": {"color": "yellow", "text": "Мойка бака №3 + фасовочник"},
    # "shift": {
    #     "color": (149, 179, 215),
    #     "text": lambda b: f"Смена {b.props['shift_num']}",
    # },
}
