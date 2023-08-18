def _remove_duplicates_in_order(values, key=None):
    # preserves order of sequence
    seen = set()
    seen_add = seen.add
    key = key or (lambda x: x)
    return [x for x in values if not (key(x) in seen or seen_add(key(x)))]


def make_cream_cheese_boiling(boiling_group_df, **props):
    boiling_model = boiling_group_df.iloc[0]["sku"].made_from_boilings[0]

    boiling_id = boiling_group_df.iloc[0]["boiling_id"]
    m = BlockMaker(
        "cream_cheese_boiling",
        boiling_model=boiling_model,
        boiling_id=boiling_id,
        base_names=_remove_duplicates_in_order(
            [
                row["sku"].name.split(" ")[0]
                + " "
                + str(row["boiling"].weight_netto).replace(".", ",")
                + "кг"  # Кремчиз 0,18кг
                for i, row in boiling_group_df.iterrows()
            ]
        ),
        **props
    )

    bt = delistify(boiling_model.boiling_technologies, single=True)

    with m.row("boiling_process"):
        m.row("cooling", size=bt.cooling_time // 5)
        m.row("separation", size=bt.separation_time // 5)
        m.row("salting", size=bt.salting_time // 5)
        m.row("separation", size=bt.separation_time // 5)
        m.row("salting", size=bt.salting_time // 5)
        m.row("P", size=bt.p_time // 5)
    with m.row(
        "packing_process",
        push_func=add_push,
        x=m.root["boiling_process"]["separation"][-1].x[0] - bt.p_time // 5,
    ):
        m.row("P", size=bt.p_time // 5)
        packing_time = sum([row["kg"] / row["sku"].packing_speed * 60 for i, row in boiling_group_df.iterrows()])
        packing_time = int(custom_round(packing_time, 5, "ceil", pre_round_precision=1))
        m.row(
            "packing",
            size=packing_time // 5,
        )
    return m.root
