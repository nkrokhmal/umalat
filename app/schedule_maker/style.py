def load_style():
    base_style = {
        'pouring': {'beg_time': '01:00'},
        'termizator': {'text': '{block_num} налив', 'bold': True},
        'pouring_name': {'text': '{boiling_label}'},
        'pouring_and_fermenting': {'text': 'налив/внесение\nзакваски', 'color': (255, 192, 0)}, # orange color
        'soldification': {'text': 'схватка', 'color': 'yellow'},
        'cutting': {'text': 'резка/обсушка', 'color': '#92d050'}, # light green color
        'pouring_off': {'text': 'слив', 'color': 'red'},
        'melting': {'beg_time': '07:00'},
        'melting_label': {'text': '{block_num}', 'bold': True},
        'melting_name': {'text': '{form_factor_label}'},
        'serving': {'color': 'orange', 'text': 'подача и вымешивание'},
        'melting_process': {'color': 'orange', 'text': lambda b: 'плавление {speed} кг/ч' if b.props['boiling_type'] == 'water' else 'плавление/формирование'},
        'cooling1': {'text': 'охлаж1 <{size} * 5> мин'},
        'cooling2': {'text': 'охлаж2 <{size} * 5> мин'},
        'packing_and_preconfiguration': {'beg_time': '07:00'},
        'packing_label': {'text': '{block_num}', 'bold': True},
        'packing_name': {'text': '{form_factor_label}'},
        'packing_brand': {'color': '#f2dcdb', 'text': '{brand_label}'}, # pink color
        'configuration': {'color': 'red'},
        'salting': {'color': (0, 176, 240), 'text': 'посолка'}, # light-blue color
        'cleaning': {'beg_time': '01:00'},
        'full_cleaning': {'color': 'yellow', 'text': 'полная мойка термизатора', 'h': 2},
        'short_cleaning': {'color': 'yellow', 'text': 'короткая мойка\nтермизатора', 'h': 2},
        'template': {'visible': True},
        'time': {'visible': True}
    }

    styles = [base_style]

    style = {}
    for s in styles:
        for k, v in s.items():
            if k not in style:
                style[k] = v
            else:
                style[k].update(v)
    return style
