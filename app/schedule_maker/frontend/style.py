STYLE = {
    'cheese_maker': {'beg_time': '01:00'},
    'boiling': {'beg_time': '01:00'},

    'termizator': {'text': '{boiling_id} налив', 'bold': True},
    'pouring_name': {'text': '{boiling_label}'},
    'pouring_and_fermenting': {'text': 'налив/внесение\nзакваски', 'color': (255, 192, 0)},  # orange color
    'soldification': {'text': 'схватка', 'color': 'yellow'},
    'cutting': {'text': 'резка/обсушка', 'color': '#92d050'},  # light green color
    'pouring_off': {'text': 'слив', 'color': 'red'},

    'drenator': {'text': 'чеддеризация'},

    'melting': {'beg_time': '07:00'},
    'packing': {'beg_time': '07:00'},
    'melting_label': {'text': '{boiling_id}', 'bold': True},
    'melting_name': {'text': '{form_factor_label}'},
    'serving': {'color': 'orange', 'text': 'подача и вымешивание'},

    'melting_process': {'color': 'orange', 'text': lambda b: 'плавление {speed} кг/ч' if b.props['boiling_type'] == 'water' else 'плавление/формирование'},

    # 'cooling': {'text': 'охлаж <{size}[0] * 5> мин'},
    'cooling': {'text': 'охлаждение'},

    # 'packing_and_preconfiguration': {'beg_time': '07:00'},
    'packing_label': {'text': '{boiling_id}', 'bold': True},
    'packing_name': {'text': '{form_factor_label}'},
    'packing_brand': {'color': '#f2dcdb', 'text': '{brand_label}'},  # pink color
    'packing_configuration': {'color': 'red'},

    'salting': {'color': (0, 176, 240), 'text': 'посолка'},  # light-blue color

    'cleaning': {'beg_time': '01:00',
                 'color': 'yellow',
                 'text': lambda b: 'полная мойка термизатора' if b.props['cleaning_type'] == 'full' else 'короткая мойка\nтермизатора'},

    'template': {'visible': True},
    'time': {'visible': True},
    'stub': {'visible': False}
}
