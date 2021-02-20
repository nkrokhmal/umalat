from utils.dict import dotdict

LineName = dotdict(
    {
        'WATER': 'Моцарелла в воде',
        'SALT': 'Пицца чиз',
        'RICOTTA': 'Рикотта'
    }
)
DepartmentName = dotdict(
    {
        'MOZZ': 'Моцарельный цех',
        'RIC': 'Рикоттный цех',
        'MASC': 'Маскарпоновый цех'
    }
)

if __name__ == '__main__':
    print(DepartmentName.MOZZ)
    print(LineName.WATER)