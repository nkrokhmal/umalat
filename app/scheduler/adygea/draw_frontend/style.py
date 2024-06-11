STYLE = {
    "boiling_num": {"text": "{boiling_id}"},
    "boiling_name": {
        "text": lambda b: "{} {} {}".format(
            b.props["group_name"],
            b.props["boiling_model"].weight_netto if b.props["group_name"] != "Халуми" else "",
            str(b.props["boiling_model"].percent) + "%" if b.props["group_name"] != "Халуми" else "",
        )
    },
    "collecting": {"color": "red", "text": "набор"},
    "coagulation": {
        "color": "yellow",
        "text": lambda b: "коагуляция и сбор белка" if b.props["group_name"] != "Халуми" else "варка 30 кг",
    },
    "pouring_off": {
        "color": "#92D050",
        "text": lambda b: "слив" if b.props["group_name"] != "Халуми" else "извлечение",
    },  # green
    "serum_collection": {"text": "набор сыворотки", "font_size": 8},
    "cleaning": {
        "color": "#DAEEF3",
        "text": "мойка оборудования и цеха",
        "font_size": 12,
    },  # blue
    "preparation": {
        "color": "red",
        "text": "подготовка и мойка оборудования",
        "font_size": 12,
    },  # blue
    "lunch": {
        "color": "#DAEEF3",
        "text": "обед",
        "font_size": 12,
    },  # blue
}
