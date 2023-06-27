def parse_start_configuration(schedule):

    # - Get boilings sorted by start

    boilings = list(
        sorted(
            schedule["master"]["boiling", True],
            key=lambda boiling: boiling.x[0],
        )
    )

    # - Get set of line names

    line_names_set = set([boiling.props["boiling_model"].line.name for boiling in boilings])

    # - Get start configuration

    if len(line_names_set) == 1:
        start_configuration = None
    else:
        start_configuration = []
        _cur_line_names = set()
        for boiling in boilings:
            line_name = boiling.props["boiling_model"].line.name
            _cur_line_names.add(line_name)
            start_configuration.append(line_name)
            if _cur_line_names == line_names_set:
                break

    # - Return

    return start_configuration
