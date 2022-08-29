STYLE = {
    "preparation": {
        "color": "#70AD47",
        "text": "Подготовка цеха к работе, обмывка/обработка",
    },  # green
    "separator_runaway": {
        "color": "#00B0F0",
        "text": "анализы/разгон сепаратора",
    },  # blue
    "pasteurization_1": {
        "color": "#FF0000",
        "text": lambda b: f"пастеризация и сепарирование {str(b.props['boiling_model'].percent)}%",
    },  # red
    "pasteurization_2": {
        "color": "#FFFF00",
        "text": lambda b: "{} литров".format(b.props["boiling_model"].line.boiling_volume),
    },  # yellow
    "increasing_temperature": {
        "color": "#00B0F0",
        "text": lambda b: f"набор tC через маслообразователь, анализ/нормализация {str(b.props['boiling_model'].percent)}%",
    },
    "packing": {
        "color": "#00B050",
        "text": lambda b: f"фасовка V{str(b.props['boiling_model'].weight_netto)} кг, {str(b.props['boiling_model'].line.output_kg)}кг",
    },  # green
    "displacement": {"color": "#FFC000", "text": "вытеснение"},  # orange
    "cleaning": {
        "color": "white",
        "text": "мойка оборудования/уборка цеха/маркировка продукции",
    },
    "cooling": {
        "color": "white",
        "text": "доохлаждение до температуры подачи на маслообразователь 55-60",
        "font_size": 7,
    },
}
