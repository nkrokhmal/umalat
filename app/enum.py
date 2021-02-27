from utils_ak.dict import dotdict

LineName = dotdict({"WATER": "Моцарелла в воде", "SALT": "Пицца чиз"})

if __name__ == "__main__":
    print(LineName.WATER)
