STYLE = {
    "boiling_num": {"text": "{boiling_id}"},
    "boiling_name": {
        "text": lambda b: "адыгейский {}%".format(b.props["boiling_model"].percent)
    },  # todo next: make properly
    "collecting": {"color": "red", "text": "набор"},
    "coagulation": {"color": "yellow", "text": "коагуляция и сбор белка"},
    "pouring_off": {"color": "#92D050", "text": "слив"},  # green
    "cleaning": {
        "color": "#DAEEF3",
        "text": "мойка оборудования и цеха",
        "font_size": 12,
    },  # blue
    "lunch": {
        "color": "#DAEEF3",
        "text": "обед",
        "font_size": 12,
    },  # blue
}
