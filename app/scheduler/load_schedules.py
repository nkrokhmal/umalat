import flask


def load_schedules(path, prefix, departments=None):
    # NOTE: DOES NOT RETURN DEPARTMENT IF NOT PRESENT
    schedules = {}
    departments = departments or []

    for department, name in config.DEPARTMENT_NAMES.items():
        if departments and department not in departments:
            continue
        fn = os.path.join(path, f"{prefix} Расписание {name}.pickle")
        if os.path.exists(fn):
            with open(fn, "rb") as f:
                schedules[department] = ParallelepipedBlock.from_dict(pickle.load(f))

            if department == "mozzarella":
                # reload models for mozzarella - need for use later
                for block in schedules[department].iter(cls="boiling"):
                    _id = int(
                        re.findall(r"(\d+)>", str(block.props["boiling_model"]))[0]
                    )  # <MozzarellaBoiling 15> -> 15
                    model = cast_model(MozzarellaBoiling, _id)
                    block.props.update(boiling_model=model)

                for block in schedules[department].iter(cls="packing"):
                    bdf = block.props["boiling_group_df"]
                    bdf["sku"] = bdf["sku"].apply(lambda sku: int(re.findall(r"(\d+)>", str(sku))[0]))
                    bdf["sku"] = bdf["sku"].apply(lambda sku: cast_model(MozzarellaSKU, sku))

                    bdf["boiling"] = bdf["boiling"].apply(lambda boiling: int(re.findall(r"(\d+)>", str(boiling))[0]))
                    bdf["boiling"] = bdf["boiling"].apply(lambda boiling: cast_model(MozzarellaBoiling, boiling))

    return schedules


def assert_schedules_presence(schedules, raise_if_not_present=None, warn_if_not_present=None):
    raise_if_not_present = raise_if_not_present or []
    warn_if_not_present = warn_if_not_present or []

    for department in raise_if_not_present:
        if department not in schedules:
            raise Exception(f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES[department]}")

    for department in warn_if_not_present:
        if department not in schedules:
            logger.warning(f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES[department]}")
            if os.environ.get("APP_ENVIRONMENT") == "runtime":
                flask.flash(
                    f"Отсутствует утвержденное расписание для цеха: {config.DEPARTMENT_NAMES[department]}",
                    "warning",
                )


if __name__ == "__main__":
    load_schedules(
        "/Users/marklidenberg/Yandex.Disk.localized/master/code/git/2020.10-umalat/umalat/app/data/dynamic/2021-01-01/approved",
        "2021-01-01",
    )
