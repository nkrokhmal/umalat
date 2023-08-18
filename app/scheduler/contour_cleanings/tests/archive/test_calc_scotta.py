def _test(path, prefix):
    schedules = load_schedules(
        path,
        prefix=prefix,
        departments=["ricotta", "mozzarella"],
    )
    print(schedules.keys())
    print(calc_scotta_input_tanks(schedules))
    print(calc_is_bar12_present(schedules))


# if __name__ == "__main__":
#     _test(
#         "/Users/marklidenberg/Yandex.Disk.localized/Загрузки/umalat/2021-07-16/approved",
#         "2021-07-16",
#     )
