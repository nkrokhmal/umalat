from umalat.app.schedule_maker.utils.block import validate_disjoint


def boiling_validator(parent, boiling):
    if not parent.children:
        return
    # todo: optimize
    #     b1 = max(parent.children, key=lambda b: b.rel_props.get('t', 0))

    for b1 in parent.children[-4:]:
        b2 = boiling

        b1.rel_props['props_mode'] = 'absolute'
        b2.rel_props['props_mode'] = 'absolute'

        b1.upd_abs_props()
        b2.upd_abs_props()

        validate_disjoint(b1['pouring'][0]['termizator'], b2['pouring'][0]['termizator'])

        if b1['pouring'].props['pouring_line'] == b2['pouring'].props['pouring_line']:
            validate_disjoint(b1['pouring'], b2['pouring'])

        if (boiling_type := b1.props['boiling_type']) == b2.props['boiling_type']:
            if boiling_type == 'water':
                validate_disjoint(b1['melting_and_packing']['melting'], b2['melting_and_packing']['melting'])
            else:
                if b1['melting_and_packing']['melting'].props['melting_line'] == \
                        b2['melting_and_packing']['melting'].props['melting_line']:
                    validate_disjoint(b1['melting_and_packing']['melting'], b2['melting_and_packing']['melting'])
                else:
                    validate_disjoint(b1['melting_and_packing']['melting'][1]['melting_process'],
                                      b2['melting_and_packing']['melting'][1]['melting_process'])

            validate_disjoint(b1['melting_and_packing']['packing'], b2['melting_and_packing']['packing'])

        b1.rel_props.pop('props_mode')
        b2.rel_props.pop('props_mode')

        b1.upd_abs_props()
        b2.upd_abs_props()