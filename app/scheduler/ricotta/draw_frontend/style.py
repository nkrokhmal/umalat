STYLE = {
    "pouring": {"text": "pouring", "color": "yellow"},
    "heating": {"text": "heating", "color": "orange"},
    "lactic_acid": {"text": "lactic acid", "color": "red"},
    "draw_whey": {"text": "draw whey", "color": "green"},
    "draw_ricotta": {"text": "draw ricotta", "color": "blue"},
    "draw_ricotta_break": {"text": "draw ricotta break", "color": "purple"},
    "salting": {"text": "salting", "color": "pink"},
    "pumping": {"text": "pumping", "color": "brown"},
    "shift": {
        "text": lambda b: f"Смена {b.props['shift_num'] + 1} {b.props['team']}",
        "color": lambda b: ["yellow", "#95B3D7"][b.props["shift_num"]],
    },
    "preparation": {
        "text": "подготовка цеха к работе, проверка оборудования стерилизация оборудования  , вызов микробиолога, отбор анализов, разгон сепаратора",
        "color": "white",
    },
    "template": {"color": "white"},
}
