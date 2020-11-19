from matplotlib import colors


def cast_color(obj):
    if isinstance(obj, (tuple, list)):
        if all(isinstance(x, int) for x in obj):
            return '#{:02x}{:02x}{:02x}'.format(*obj)
        elif all(isinstance(x, float) for x in obj):
            return colors.to_hex(obj)
    elif isinstance(obj, str):
        try:
            return cast_color(colors.to_rgb(obj))
        except:
            pass
    raise Exception('Unknown object type')


if __name__ == '__main__':
    print(cast_color('grey'))
    print(cast_color((1., 0., 1.)))
    print(cast_color((15, 15, 16)))
    print(cast_color('#808081'))