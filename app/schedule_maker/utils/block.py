from utils_ak.interactive_imports import *

PERIODS_PER_HOUR = 12
PERIODS_PER_DAY = 24 * PERIODS_PER_HOUR

import copy
import math

from app.schedule_maker.utils.interval import calc_interval_length, cast_interval


def validate_disjoint(b1, b2):
    # assert a disposition information
    # todo: hack, a little bit hardcode

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


class Block:
    def __init__(self, block_class=None, parent=None, **props):
        block_class = block_class or 'block'
        self.parent = parent
        self.children = []

        props['class'] = block_class

        if 'props' in props:
            props.update(props.pop('props'))

        self.rel_props = props or {}
        self.abs_props = {}

    @property
    def props(self):
        return self.abs_props if self.rel_props.get('props_mode') == 'absolute' or self.abs_props.get('props_mode') == 'absolute' else self.rel_props

    def __getitem__(self, item):
        if isinstance(item, str):
            res = [b for b in self.children if b.rel_props['class'] == item]
        elif isinstance(item, int):
            res = self.children[item]
        elif isinstance(item, slice):
            # Get the start, stop, and step from the slice
            res = [self[ii] for ii in range(*item.indices(len(self)))]
        else:
            raise TypeError('Item type not supported')

        if isinstance(res, Block):
            res.upd_abs_props()
        elif isinstance(res, list):
            for b in res:
                b.upd_abs_props()

        if not res:
            return

        if hasattr(res, '__len__') and len(res) == 1:
            return res[0]
        else:
            return res

    @property
    def size(self):
        res = self.props.get('size', 0)
        if not res:
            # check that int is divided by 5
            assert self.props.get('time_size', 0) % 5 == 0
            res = int(self.props.get('time_size', 0) / 5)

        # check if int-like
        assert math.ceil(res) == math.floor(res)

        return int(res)

    @property
    def beg(self):
        return self.props.get('t', 0)

    @property
    def end(self):
        return self.beg + self.size

    @property
    def interval(self):
        return cast_interval(self.beg, self.end)

    def __str__(self):
        res = f'{self.rel_props["class"]} ({self.beg}, {self.end}]\n'

        for child in self.children:
            for line in str(child).split('\n'):
                if not line:
                    continue
                res += '  ' + line + '\n'
        return res

    def __repr__(self):
        return str(self)

    def _inherit_props(self, parent_props, props):
        cur_props = copy.deepcopy(parent_props)

        # specify what we don't inherit
        cur_props = {k: v for k, v in cur_props.items() if k not in ['size', 'time_size']}

        # add our props
        for key in props:
            if key not in cur_props:
                # new key
                cur_props[key] = props[key]
            else:
                if key in ['t', 'y']:  # accumulated keys
                    cur_props[key] += props[key]
                else:
                    if props[key] is not None:
                        cur_props[key] = props[key]
        return cur_props

    def upd_abs_props(self):
        if not self.parent:
            self.abs_props = copy.deepcopy(self.rel_props)
        else:
            self.abs_props = self._inherit_props(self.parent.abs_props, self.rel_props)

        # todo: hardcode
        self.abs_props['size'] = self.size
        self.abs_props['time_size'] = self.abs_props['size'] * 5

    def iter(self):
        self.upd_abs_props()

        yield self

        for child in self.children:
            for b in child.iter():
                yield b

    def add(self, block):
        block.parent = self
        self.children.append(block)
        return block


@clockify()
def simple_push(parent, block, validator='basic', props=None):
    if validator == 'basic':
        validator = gen_pair_validator()

    # set parent for proper abs_props
    block.parent = parent

    props = props or {}
    if props:
        block.rel_props.update(props)
        block.upd_abs_props()

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

# todo: limit end
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
            res = simple_push(parent, block, validator=validator, props=props)
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
    def __init__(self, root_name='root', default_push_func=simple_push):
        self.root = Block(block_class=root_name)
        self.blocks = [self.root]
        self.default_push_func = default_push_func

    def make(self, block_obj=None, push_func=None, push_kwargs=None, **kwargs):
        push_func = push_func or self.default_push_func
        push_kwargs = push_kwargs or {}

        if isinstance(block_obj, str) or block_obj is None:
            block = Block(block_class=block_obj, **kwargs)
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

    with make('a', size=3, t=5, override=True):
        make('b', size=2)
        make('b', size=2)
        make('c', size=1)

    print(maker.root['a']['b'][0].interval)
    print(maker.root['a'][2])

    b = Block('a', time_size=10)
    print(b.size)

    b = Block('a', time_size=11)
    try:
        print(b.size)
        raise Exception('Should not happend')
    except AssertionError:
        print('Time size should be divided by 5')
