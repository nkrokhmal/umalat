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
    # todo soon: take from models
    "pasteurization_2": {"color": "#FFFF00", "text": "900 литров"},  # yellow
    "increasing_temperature": {
        "color": "#00B0F0",
        "text": lambda b: f"набор tC через маслообразователь, анализ/нормализация {str(b.props['boiling_model'].percent)}%",
    },
    "packing": {
        "color": "#00B050",
        # todo soon: rename to output_kg
        "text": lambda b: f"фасовка V{str(b.props['boiling_model'].weight_netto)} кг, {str(b.props['boiling_model'].line.output_ton)}кг",
    },  # green
    "displacement": {"color": "#FFC000", "text": "вытеснение"},  # orange
    "cleaning": {
        "color": "white",
        "text": "мойка оборудования/уборка цеха/маркировка продукции",
    },
}
