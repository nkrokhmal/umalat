from app.imports.runtime import *

LineName = utils.dotdict(
    {
        "WATER": "Моцарелла в воде",
        "SALT": "Пицца чиз",
        "RICOTTA": "Рикотта",
        "MASCARPONE": "Маскарпоне",
    }
)
DepartmentName = utils.dotdict(
    {
        "MOZZARELLA": "Моцарельный цех",
        "RICOTTA": "Рикоттный цех",
        "MASCARPONE": "Маскарпоновый цех",
    }
)

if __name__ == "__main__":
    print(DepartmentName.MOZZARELLA)
    print(LineName.WATER)
