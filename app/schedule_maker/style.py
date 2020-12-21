def load_style():
    base_style = {
        'cheese_maker': {'beg_time': '01:00'},
        'boiling': {'beg_time': '01:00'},
        'termizator': {'text': '{block_front_id} налив'},
        'soldification': {'text': 'схватка', 'color': 'yellow'},
        'cutting': {'text': 'резка/обсушка', 'color': '#92d050'}, # light green color
        'pouring_off': {'text': 'слив', 'color': 'red'},
        'drenator': {'text': 'чеддеризация'},
        # 'melting_process': {'color': 'orange', 'text': lambda b: '{form_factor_label}'},
        'melting_process': {'color': 'orange', 'text': lambda b: 'плавление'},
        'cooling': {'text': 'охлаждение'},
        'salting': {'color': (0, 176, 240), 'text': 'посолка'},  # light-blue color
        'packing_process': {'color': '#f2dcdb', 'text': '{brand_label}'},
        'configuration': {'color': 'red'},
        'pouring_name': {'text': '{boiling_label}'},
        'pouring_and_fermenting': {'text': 'налив/внесение\nзакваски', 'color': (255, 192, 0)}, # orange color
        'meltings_low': {'beg_time': '07:00'},
        'coolings': {'beg_time': '07:00'},
        'packings': {'beg_time': '07:00'},
        'configurations': {'beg_time': '07:00'},
        'serving': {'text': '{block_front_id} подача'},
        'melting_label': {'text': '{form_factor_label}'},
        # 'cooling1': {'text': 'охлаж1 <{size} * 5> мин'},
        # 'packing_team': {'beg_time': '07:00'},
        # 'packing_label': {'text': '{block_num}'},
        # 'packing_brand': {'text': '{brand_label}'},

        # 'cleaning': {'beg_time': '01:00'},
        # 'full_cleaning': {'color': 'yellow', 'text': 'полная мойка термизатора', 'h': 2},
        # 'short_cleaning': {'color': 'yellow', 'text': 'короткая мойка\nтермизатора', 'h': 2},
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
