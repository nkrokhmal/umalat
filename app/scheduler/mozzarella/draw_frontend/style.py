_shift_colors = {1: (149, 179, 215), 2: "yellow", 3: (0, 176, 240)}
STYLE = {
    "termizator": {"text": "{boiling_id} налив", "bold": True},
    "pouring_name": {"text": "{boiling_label}"},
    "pouring_and_fermenting": {
        "text": "налив/внесение\nзакваски",
        "color": (255, 192, 0),
    },  # orange color
    "soldification": {"text": "схватка", "color": "yellow"},
    "cutting": {"text": "резка/обсушка", "color": "#92d050"},  # light green color
    "pumping_out": {"text": "откачка", "color": "#add8e6"},  # light blue color
    "pouring_off": {"text": "слив", "color": "red"},
    "drenator": {"text": "чеддеризация"},
    "melting_label": {"text": "{boiling_id}", "bold": True},
    "melting_name": {"text": "{form_factor_label}"},
    "serving": {"color": "orange", "text": "подача и вымешивание"},
    "melting_process": {
        "color": "orange",
        "text": "плавление/формирование",
    },
    # 'cooling': {'text': 'охлаж <{size}[0] * 5> мин'},
    "cooling": {"text": "охлаждение"},
    "packing_label": {"text": "{boiling_id}", "bold": True},
    "packing_name": {"text": "{group_form_factor_label}"},
    "packing_brand": {"color": "#f2dcdb", "text": "{brand_label}"},  # pink color
    "packing_configuration": {"color": "red"},
    "packing_process": {"color": "#f2dcdb"},
    "salting": {"color": (0, 176, 240), "text": "посолка"},  # light-blue color
    "cleaning": {
        "color": "yellow",
        "text": lambda b: "Полная мойка" if b.props["cleaning_type"] == "full" else "Короткая мойка",
    },
    "multihead_cleaning": {"color": "yellow", "text": "Мойка мультиголовы"},
    "template": {"visible": True},
    "time": {"visible": True},
    "stub": {"visible": False},
    "shift": {
        "color": lambda b: _shift_colors[b.props["shift_num"]],
        "text": lambda b: f"Смена {b.props['shift_num']}",
        "font_size": 16,
        "bold": True,
    },
    # - Rubber
    "rubber_packing_group": {"text": lambda b: f"{b.props['sku'].name} - {b.props['kg']} кг"},
    "rubber_packing": {"text": lambda b: f"{b.props['sku'].name} - {b.props['sku'].packing_speed}/ч"},
    "rubber_preparation": {
        "text": "подготовка мультиголовы (мойка, дезинфекция) + терка FAM (мойка, дезинфекция)",
        "color": "#E1EFDA",
    },
    "rubber_refurbishment": {
        "text": "переностройка терки (ножей) FAM",
        "color": "#E1EFDA",
    },
    "rubber_refurbishment_and_cleaning": {
        "text": "переностройка, мойка терки (ножей) FAM",
        "color": "#E1EFDA",
    },
    "rubber_cleaning": {
        "text": "мойка мультиголовы, терки FAM",
        "color": "#E1EFDA",
    },
    "rubber_long_switch": {
        "text": "замена газа и пленки",
        "color": "red",
        "font_size": 4,
    },
    "rubber_short_switch": {
        "text": "",
        "color": "red",
    },
}
