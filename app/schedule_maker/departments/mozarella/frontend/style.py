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
        "text": lambda b: "плавление {speed} кг/ч"
        if b.props["boiling_type"] == "water"
        else "плавление/формирование",
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
        # 'text': lambda b: 'полная мойка термизатора' if b.props['cleaning_type'] == 'full' else 'короткая мойка\nтермизатора'
    },
    "multihead_cleaning": {"color": "yellow", "text": "Мойка мультиголовы"},
    "template": {"visible": True},
    "time": {"visible": True},
    "stub": {"visible": False},
}
