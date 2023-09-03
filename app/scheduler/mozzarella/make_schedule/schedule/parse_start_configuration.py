def parse_start_configuration(schedule):
    boilings = list(
        sorted(
            schedule["master"]["boiling", True],
            key=lambda boiling: boiling.x[0],
        )
    )
    line_names = set([boiling.props["boiling_model"].line.name for boiling in boilings])

    if len(line_names) == 1:
        start_configuration = None
    else:
        start_configuration = []
        _cur_line_names = set()
        for boiling in boilings:
            line_name = boiling.props["boiling_model"].line.name
            _cur_line_names.add(line_name)
            start_configuration.append(line_name)
            if _cur_line_names == line_names:
                break
    return start_configuration
