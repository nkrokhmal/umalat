import typing as tp


def sku_successful_msg(action: tp.Literal["add", "change", "delete"] = "add") -> str:
    action_mapping = {"add": "добавлено", "change": "изменено", "delete": "удалено"}

    return f"SKU успешно {action_mapping.get(action)}"


def sku_exception_msg() -> str:
    return f"Ошибка при добавлении SKU. В базе уже есть SKU с таким кодом или именем"


def boiling_successful_msg() -> str:
    return "Параметры варки успешно изменены"
