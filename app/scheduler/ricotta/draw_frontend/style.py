STYLE = {
    "boiling_preparation": {"text": lambda b: str(int(b.props["absolute_batch_id"])), "color": "white"},
    "pouring": {"text": lambda b: f"Набор сыворотки {int(b.props['whey_kg'])}кг", "color": "#00B050"},
    "heating": {"text": "Нагрев до 90 градусов", "color": "#E26B0A"},
    "lactic_acid": {"text": "Молочная кислота/выдерживание", "color": "#00B0F0"},
    "heating_short": {"text": "", "color": "red"},
    "draw_whey": {"text": "Слив сыворотки", "color": "#FFC000"},
    "dray_ricotta": {
        "text": lambda b: f"Слив рикотты {int(b.props['output_kg'])}кг п/ф",
        "color": "#948A54",
        "font_size": 9,
    },
    "manual_cleaning": {"text": "Ручная мойка лишатричи", "color": "#92D050"},
    "draw_ricotta_break": {"text": "", "color": "white"},
    "salting": {"text": "Посолка/анализ", "color": "#D9D9D9"},
    "ingredient": {"text": "Внесение ингедиентов", "color": "yellow"},
    "pumping": {"text": "Перекачивание", "color": "#00B050"},
    "packing": {"text": lambda b: b.props["label"], "color": "#FFC000"},
    "packing_header": {"text": lambda b: str(int(b.props["absolute_batch_id"])), "color": "#FFC000"},
    "cleaning": {
        "text": lambda b: {
            "floculator": f"Мойка флокулятора №{b.props['floculator_num']}",
            "drenator": "Мойка дренатора",
            "lishat_richi": "Мойка 1-го и 2-го бакол лишатричи + Бертоли",
            "buffer_tank": "Мойка буферного танка и Фасовочника Ильпра",
        }[b.props["cleaning_object"]],
        "color": "#92D050",
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
}
