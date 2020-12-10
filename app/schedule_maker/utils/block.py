from utils_ak.interactive_imports import *

PERIODS_PER_HOUR = 12
PERIODS_PER_DAY = 24 * PERIODS_PER_HOUR

import copy
import math

from app.schedule_maker.utils.interval import calc_interval_length, cast_interval


def validate_disjoint(b1, b2):
    # assert a disposition information
    try:
        disposition = b1.interval.upper - b2.interval.lower
    except:
        disposition = 1

    assert calc_interval_length(b1.interval & b2.interval) == 0, cast_js({'disposition': disposition})


def gen_pair_validator(validate=validate_disjoint):
    def f(parent, new_block):
        for b in parent.children:
            validate(b, new_block)
    return f



def t_acc(parent, child, key):
    pv, v = cast_prop_values(parent, child, key)
    pv = pv if pv else 0
    v = v if v else 0
    return pv + v


def size_acc(parent, child, key):
    size, time_size = child.relative_props.get('size', 0), child.relative_props.get('time_size', 0)
    size, time_size = int(size), int(time_size)
    if size:
        return int(size)
    else:
        assert time_size % 5 == 0
        return time_size // 5


def time_size_acc(parent, child, key):
    size, time_size = child.relative_props.get('size', 0), child.relative_props.get('time_size', 0)
    size, time_size = int(size), int(time_size)
    if size:
        return size * 5
    else:
        return time_size


def class_acc(parent, child, key):
    return child.relative_props.get('class')


DYNAMIC_ACCUMULATORS = {'t': t_acc}
STATIC_ACCUMULATORS = {'size': size_acc, 'time_size': time_size_acc, 'class': class_acc}
DYNAMIC_KEYS = ['t', 'pouring_line', 'melting_line']
REQUIRED_STATIC_KEYS = ['size', 'time_size', 'class']


class Block:
    def __init__(self, block_class=None, props=None, **kwargs):
        block_class = block_class or 'block'
        props = props or {}
        props['class'] = block_class
        props.update(kwargs)

        self.parent = None
        self.children = []

        self.props = Props(props=props,
                           dynamic_accumulators=DYNAMIC_ACCUMULATORS,
                           dynamic_keys=DYNAMIC_KEYS,
                           static_accumulators=STATIC_ACCUMULATORS,
                           required_static_keys=REQUIRED_STATIC_KEYS)

        # accumulate basic static props on initialization
        self.props.accumulate_static()

    def __getitem__(self, item):
        if isinstance(item, str):
            res = [b for b in self.children if b.props['class'] == item]
        elif isinstance(item, int):
            res = self.children[item]
        elif isinstance(item, slice):
            # Get the start, stop, and step from the slice
            res = [self[ii] for ii in range(*item.indices(len(self)))]
        else:
            raise TypeError('Item type not supported')

        if not res:
            return

        if hasattr(res, '__len__') and len(res) == 1:
            return res[0]
        else:
            return res

    @property
    def size(self):
        return self.props['size']

    @property
    def beg(self):
        return self.props['t']

    @property
    def end(self):
        return self.props['t'] + self.props['size']

    @property
    def interval(self):
        return cast_interval(self.beg, self.end)

    def __str__(self):
        res = f'{self.props["class"]} ({self.beg}, {self.end}]\n'

        for child in self.children:
            for line in str(child).split('\n'):
                if not line:
                    continue
                res += '  ' + line + '\n'
        return res

    def __repr__(self):
        return str(self)

    def iter(self):
        yield self

        for child in self.children:
            for b in child.iter():
                yield b

    def set_parent(self, parent):
        self.parent = parent
        self.props.parent = parent.props

    def add_child(self, block):
        self.children.append(block)
        self.props.children.append(block.props)

    def add(self, block):
        block.set_parent(self)
        self.add_child(block)
        return block


def simple_push(parent, block, validator='basic', new_props=None):
    if validator == 'basic':
        validator = gen_pair_validator()

    # set parent for proper abs_props
    block.set_parent(parent)

    # update props for current try
    new_props = new_props or {}
    block.props.update(new_props)

    if validator:
        try:
            validator(parent, block)
        except AssertionError as e:
            try:
                # todo: hardcode
                return cast_dict(e.__str__()) # {'disposition': 2}
            except:
                return
    return parent.add(block)


def add_push(parent, block):
    return simple_push(parent, block, validator=None)


# simple greedy algorithm
def dummy_push(parent, block, max_tries=24, beg='last_end', end=PERIODS_PER_DAY * 10, validator='basic', iter_props=None):
    # note: make sure parent abs props are updated
    if beg == 'last_beg':
        cur_t = max([0] + [child.beg for child in parent.children])
    elif beg == 'last_end':
        cur_t = max([0] + [child.end for child in parent.children])
    elif isinstance(beg, int):
        cur_t = beg
    else:
        raise Exception('Unknown beg type')

    end = min(end, cur_t + max_tries)

    iter_props = iter_props or [{}]

    while cur_t < end:
        dispositions = []
        for props in iter_props:
            props = copy.deepcopy(props)
            props['t'] = cur_t

            res = simple_push(parent, block, validator=validator, new_props=props)

            if isinstance(res, Block):
                return block
            elif isinstance(res, dict):
                # optimization by disposition from validate_disjoint error
                if 'disposition' in res:
                    dispositions.append(res['disposition'])

        if len(dispositions) == len(iter_props):
            # all iter_props failed because of bad disposition
            cur_t += min(dispositions)
        else:
            cur_t += 1

    raise Exception('Failed to push element')


class BlockMaker:
    def __init__(self, root_class='root', default_push_func=simple_push):
        self.root = Block(root_class)
        self.blocks = [self.root]
        self.default_push_func = default_push_func

    def make(self, block_obj=None, push_func=None, push_kwargs=None, **kwargs):
        push_func = push_func or self.default_push_func
        push_kwargs = push_kwargs or {}

        if isinstance(block_obj, str) or block_obj is None:
            block = Block(block_obj, **kwargs)
        elif isinstance(block_obj, Block):
            block = block_obj
        else:
            raise Exception('Unknown block obj type')

        push_func(self.blocks[-1], block, **push_kwargs)
        return BlockMakerContext(self, block)


class BlockMakerContext:
    def __init__(self, maker, block):
        self.maker = maker
        self.block = block

    def __enter__(self):
        self.maker.blocks.append(self.block)
        return self.block

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.maker.blocks.pop()


if __name__ == '__main__':
    a = Block('a', size=3, t=5)
    b = Block('b', size=2)
    c = Block('c', size=1)

    dummy_push(a, b)
    dummy_push(a, c)
    print(a)

    maker = BlockMaker(default_push_func=dummy_push)
    make = maker.make

    with make('a', size=3):
        make('b', size=2)
        make('c', size=1)
    print(maker.root)

    maker = BlockMaker(default_push_func=add_push)
    make = maker.make

    with make('a', size=3, t=5):
        make('b', size=2)
        make('b', size=2)
        make('c', size=1)

    print(maker.root['a']['b'][0].interval)
    print(maker.root['a'][2])

    b = Block('a', time_size=10)
    print(b.size)

    try:
        b = Block('a', time_size=11)
        raise Exception('Should not happen')
    except AssertionError:
        print('Time size should be divided by 5')
