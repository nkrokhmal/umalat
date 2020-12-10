def load_style(mode='prod'):
    base_style = {
        'pouring': {'beg_time': '01:00'},
        'termizator': {'text': '{block_num} налив'},
        'pouring_name': {'text': '{boiling_label}'},
        'pouring_and_fermenting': {'text': 'налив/внесение\nзакваски', 'color': (255, 192, 0)}, # orange color
        'soldification': {'text': 'схватка', 'color': 'yellow'},
        'cutting': {'text': 'резка/обсушка', 'color': '#92d050'}, # light green color
        'pouring_off': {'text': 'слив', 'color': 'red'},
        'melting': {'beg_time': '07:00'},
        'melting_label': {'text': '{block_num}'},
        'melting_name': {'text': '{form_factor_label}'},
        'serving': {'color': 'orange', 'text': 'подача и вымешивание'},
        'melting_process': {'color': 'orange', 'text': lambda b: 'плавление/формирование {speed} кг/ч' if b.props['boiling_type'] == 'water' else 'плавление/формирование'},
        'cooling1': {'text': 'охлаж1 <{size} * 5> мин'},
        'cooling2': {'text': 'охлаж2 <{size} * 5> мин'},
        'packing_and_preconfiguration': {'beg_time': '07:00'},
        'packing_label': {'text': '{block_num}'},
        'packing_name': {'text': '{form_factor_label}'},
        'packing_brand': {'color': '#f2dcdb', 'text': '{brand_label}'}, # pink color
        'configuration': {'color': 'red'},
        'salting': {'color': (0, 176, 240), 'text': 'посолка'}, # light-blue color
        'cleaning': {'beg_time': '01:00', 'h': 2},
        'full_cleaning': {'color': 'yellow', 'text': 'полная мойка термизатора'},
        'short_cleaning': {'color': 'yellow', 'text': 'короткая мойка\nтермизатора'},
    }

    row_style_dev = {
        'pouring': {'y': lambda b: {'0': 1, '1': 3, '2': 5, '3': 7}[b.props['pouring_line']]},
        'melting': {'y': lambda b: 9 if b.props['boiling_type'] == 'water' else {'0': 15, '1': 18, '2': 21, '3': 24}[b.props['melting_line']]},
        'packing_and_preconfiguration': {'y': lambda b: 13 if b.props['boiling_type'] == 'water' else 27},
        'cleaning': {'y': 29}
    }

    row_style_prod = {
        'pouring': {'y': lambda b: {'0': 6, '1': 9, '2': 15, '3': 18}[b.props['pouring_line']]},
        'melting': {'y': lambda b: 24 if b.props['boiling_type'] == 'water' else {'0': 33, '1': 36, '2': 39, '3': 42}[b.props['melting_line']]},
        'packing_and_preconfiguration': {'y': lambda b: 29 if b.props['boiling_type'] == 'water' else 46},
        'cleaning': {'y': 12}
    }

    row_style = row_style_dev if mode == 'dev' else row_style_prod

    styles = [base_style, row_style]

    style = {}
    for s in styles:
        for k, v in s.items():
            if k not in style:
                style[k] = v
            else:
                style[k].update(v)
    return style
