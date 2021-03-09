from app.schedule_maker.departments.mozarella.algo import *


# todo: refactor
def make_schedule_with_boiling_inside_a_day(
    boiling_plan_df, start_times=None, first_group_id=None, date=None
):
    start_times = start_times or {LineName.WATER: "08:00", LineName.SALT: "07:00"}
    res = {}

    # make first boiling - no cleaning boilings
    boilings = make_boilings(boiling_plan_df, first_group_id=first_group_id)
    schedule = make_schedule(boilings, start_times=start_times)
    res[None] = calc_schedule_stats(schedule)

    start_from = None
    if cast_t(res[None]["max_non_full_cleaning_time"]) >= cast_t("12:00"):
        boilings = make_boilings(boiling_plan_df, first_group_id=first_group_id)
        water_boilings = [
            boiling
            for boiling in boilings
            if boiling.props["boiling_model"].line.name == LineName.WATER
        ]
        boilings = list(
            sorted(
                boilings,
                key=lambda boiling: listify(schedule["master"]["boiling"]).index(
                    [
                        b
                        for b in listify(schedule["master"]["boiling"])
                        if b.props["boiling_id"] == boiling.props["boiling_id"]
                    ][0]
                ),
            )
        )

        if water_boilings:
            start_from = boilings.index(water_boilings[-1])

        for i in tqdm(range(len(boilings) - 1)):
            boilings = make_boilings(boiling_plan_df, first_group_id=first_group_id)
            boilings = list(
                sorted(
                    boilings,
                    key=lambda boiling: listify(schedule["master"]["boiling"]).index(
                        [
                            b
                            for b in listify(schedule["master"]["boiling"])
                            if b.props["boiling_id"] == boiling.props["boiling_id"]
                        ][0]
                    ),
                )
            )
            schedule = make_schedule(
                boilings,
                cleanings={boilings[i].props["boiling_id"]: "full"},
                start_times=start_times,
            )
            res[i] = calc_schedule_stats(schedule)

    suitable = {
        k: v
        for k, v in res.items()
        if cast_t(v["max_non_full_cleaning_time"]) < cast_t("12:00")
    }

    if suitable:
        if start_from:
            res = {k: v for k, v in suitable.items() if k is None or k >= start_from}
            if not res:
                res = suitable
        else:
            res = suitable

        best = min(res.items(), key=lambda v: v[1]["total_time"])
    else:
        # todo: make properly
        raise AssertionError(
            "Для правила 12 часов необходимо вставить две полные варки внутридня. Укажите эти полные варки в ручном режиме в плане варок и не используйте автоматическое вставление полной варки по правилу 12 часов."
        )
        # res.pop(None)
        # best = min(res.items(), key=lambda v: v[1]['max_non_full_cleaning_time'])

    logger.info(f"Best cleaning_boiling: {best}")

    boilings = make_boilings(boiling_plan_df, first_group_id=first_group_id)
    cleaning_boiling = None if best[0] is None else boilings[best[0]]
    cleanings = (
        {} if not cleaning_boiling else {cleaning_boiling.props["boiling_id"]: "full"}
    )
    return make_schedule(
        boilings, cleanings=cleanings, start_times=start_times, date=date
    )
