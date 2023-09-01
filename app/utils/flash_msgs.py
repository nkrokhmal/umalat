import typing as tp

from enum import Enum


class Action(str, Enum):
    ADD: str = "add"
    EDIT: str = "edit"
    DELETE: str = "delete"
    ERROR: str = "error"


def sku_msg(action: str) -> str | None:
    match action:
        case Action.ADD:
            return "SKU было успешно добавлено!"
        case Action.EDIT:
            return "SKU было успешно изменено!"
        case Action.DELETE:
            return "SKU было успешно удалено из базы данных"
        case Action.ERROR:
            return "Ошибка при добавлении SKU. В базе уже есть SKU с таким кодом или именем"
        case _:
            return None


def boiling_msg(action: str) -> str | None:
    match action:
        case Action.EDIT:
            return "Параметры варки успешно изменены!"
        case _:
            return None


def boiling_technology_msg(action: str) -> str | None:
    match action:
        case Action.EDIT:
            return "Параметры технологии варки успешно изменены!"
        case _:
            return None


def department_msg(action: str) -> str | None:
    match action:
        case Action.EDIT:
            return "Параметры цеха были успешно изменены!"
        case Action.ERROR:
            return "Параметры не были изменены!"
        case _:
            return None


def washer_msg(action: str) -> str | None:
    match action:
        case Action.EDIT:
            return "Параметры мойки успешно изменены!"
        case _:
            return None
