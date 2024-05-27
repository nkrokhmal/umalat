def boiling_header_text(b):
    if b.props["semifinished_group"] == "cream":
        return f"Сливки {int(b.props['percent'])}% {int(b.props['total_input_kg'])}кг"
    elif b.props["semifinished_group"] == "cream_cheese":
        litres = int(sum(boiling.props["input_kg"] for boiling in b.props["boilings"]))
        return f"Кремчиз/{litres}л партия {b.props['absolute_batch_id']}"
    elif b.props["semifinished_group"] == "robiola":
        litres = int(sum(boiling.props["input_kg"] for boiling in b.props["boilings"]))
        return f"Робиола/{litres}л партия {b.props['absolute_batch_id']}"
    elif b.props["semifinished_group"] == "cottage_cheese":
        litres = int(sum(boiling.props["input_kg"] for boiling in b.props["boilings"]))
        return f"Творожный/{litres}л партия {b.props['absolute_batch_id']}"
    elif b.props["semifinished_group"] == "mascarpone":
        litres = int(sum(boiling.props["input_kg"] for boiling in b.props["boilings"]))
        return f"Производство маскарпоне {litres}кг партия {b.props['absolute_batch_id']}"


def pouring_text(b):
    if b.props["semifinished_group"] == "cream":
        return f"Прием {int(b.props['total_input_kg'])}кг"
    elif b.props["semifinished_group"] in ["cream_cheese", "robiola", "cottage_cheese"]:
        return f"Прием п/ф {int(b.props['kg'])} кг"
    elif b.props["semifinished_group"] == "mascarpone":
        return f"Прием п/ф {int(b.props['kg'])} кг"
    else:
        # should not happen
        return "Прием"


def cleaning_text(b):
    if b.props["cleaning_object"] == "pasteurizer":
        return "Мойка пастеризатора"
    elif b.props["cleaning_object"] == "separator":
        return "Мойка сепаратора"
    elif b.props["cleaning_object"] == "tubs":
        return "Мойка 1-го и 2-го бака лишатричи+гомогенизатора"
    elif b.props["cleaning_object"] == "heat_exchanger":
        return "Мойка теплообменника"
    elif b.props["cleaning_object"] == "cream_cheese_tub":
        return "Мойка бака"
    elif b.props["cleaning_object"] == "buffer_tank_and_packer":
        return "Мойка буферного танка и фасовочника"
    else:
        # should not happen
        return "Мойка"


STYLE = {
    "pouring": {"text": pouring_text, "color": "yellow"},
    "salting": {"text": "посолка/нормализация/анализ", "color": "#92D050"},
    "pumping": {"text": "П", "color": "#948A54"},
    "analysis": {"text": "анализ", "color": "white"},
    "packing": {"text": lambda b: f"{b.props['sku_name']}", "color": "#C0504D", "font_size": 8},
    "packing_switch": {"text": "Ф", "color": "grey"},
    "separation": {"text": lambda b: f"Сепарирование {int(b.props['input_kg'])}кг", "color": "#00B0F0"},
    "heating": {"text": "Н", "color": "#F79646"},
    "ingredient": {"text": "добавка/нагре/перемешивание/анализ", "color": "#92D050"},
    "cleaning": {"text": cleaning_text, "color": "yellow"},
    "separator_acceleration": {"text": "разгон сепаратора", "color": "#C4D79B"},
    "boiling_header": {
        "text": boiling_header_text,
        "color": "white",
    },
    "pouring_cream": {
        "text": lambda b: f"Прием сливок {1000 * len(b.props['boilings'])} кг/заквашивание/подача на сепаратор с аппаратного танка сливок",
        "color": "#B8CCE4",
    },
    "shift": {
        "text": lambda b: f"Смена {b.props['shift_num'] + 1} {b.props['team']}",
        "color": lambda b: ["yellow", "#95B3D7"][b.props["shift_num"]],
    },
    "preparation": {
        "text": "подготовка цеха к работе, проверка оборудования стерилизация оборудования  , вызов микробиолога, отбор анализов, разгон сепаратора",
        "color": "white",
    },
    "template": {"color": "white"},
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
