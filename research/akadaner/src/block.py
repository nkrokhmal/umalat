import copy


import portion
def cast_interval(a, b):
    return portion.openclosed(a, b)

def calc_interval_length(i):
    if i.empty:
        return 0
    return sum([c.upper - c.lower for c in i])


PERIODS_PER_HOUR = 12
PERIODS_PER_DAY = 24 * PERIODS_PER_HOUR


def validate_disjoint(b1, b2):
    b1, b2 = min([b1, b2], key=lambda b: str(b.interval)), max([b1, b2], key=lambda b: str(b.interval))
    assert calc_interval_length(b1.interval & b2.interval) == 0


class Block:
    def __init__(self, block_class='block', **props):
        self.block_class = block_class

        if 'props' in props:
            props.update(props.pop('props'))

        if 'parent' in props:
            self.parent = props.pop('parent')
        else:
            self.parent = None

        self.children = []

        props['class'] = block_class

        self.local_props = props or {}

    @property
    def props(self):
        if self.parent:
            # accumulated keys
            res = copy.deepcopy(self.parent.props)
        else:
            res = {}

        for key in self.local_props:
            if key not in res:
                res[key] = self.local_props[key]
            else:
                # both contain key
                if key in ['t', 'y']:  # accumulated keys
                    res[key] = res[key] + self.local_props[key]
                else:
                    res[key] = self.local_props[key]
        return res


    @property
    def beg(self):
        return self.props.get('t', 0)

    @property
    def size(self):
        return self.props.get('size', 0)

    @property
    def end(self):
        return self.beg + self.size

    @property
    def interval(self):
        return cast_interval(self.beg, self.end)

    def __str__(self):
        res = f'{self.block_class} {self.local_props}\n'
        for child in self.children:
            for line in str(child).split('\n'):
                if not line:
                    continue
                res += '  ' + line + '\n'
        return res

    def __repr__(self):
        return str(self)

    def push(self, block, after=None, before=PERIODS_PER_DAY, validator=None):
        original_parent = block.parent
        block.parent = self

        after = after or 0

        cur_t = after

        while cur_t < before:
            block.local_props['t'] = cur_t

            validated = self.validate(block, validator=validator)

            if validated:
                self.add(block)
                return block
            else:
                # try to fit the block
                cur_t += 1

        block.parent = original_parent


    def add(self, block):
        self.children.append(block)

    def validate(self, block, validator=None):
        validator = validator or validate_disjoint
        for b in self.children:
            try:
                validator(b, block)
            except AssertionError:
                return False
        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def make(self, block_class='block', method='push', validator=None, **kwargs):
        block = Block(block_class, props=kwargs, parent=self)
        if method == 'push':
            self.push(block, validator=validator)
        elif method == 'add':
            self.add(block)
        return block

    def get_child(self, child_class):
        if isinstance(child_class, str):
            children_with_key = [child for child in self.children if child.block_class == child_class]
            if len(children_with_key) == 0:
                raise KeyError(child_class)
            elif len(children_with_key) > 1:
                raise Exception(f'Too many keys: {child_class}')

            return children_with_key[0]
        elif isinstance(child_class, int):
            return self.children[child_class]
        else:
            raise Exception(f'Unknown key type {child_class}')

    def __getitem__(self, item):
        return self.props[item]

    def get(self, item, *args, **kwargs):
        return self.props.get(item, *args, *kwargs)

    def __iter__(self):
        yield self
        for child in self.children:
            for b in child:
                yield b

    def flatten(self):
        return [self] + sum([child.flatten() for child in self.children], [])


if __name__ == '__main__':
    root = Block('root', t=10)

    with root.make('boiling', block_num=12) as boiling:
        with boiling.make('water_pouring', y=6, method='add') as water_pouring:
            total_size = 27

            with water_pouring.make(y=0) as b:
                b.make('pouring_label', size=6, block_num=12)
                b.make('pouring_name', size=total_size - 6, name='чильеджина  3,6 альче  8500кг')
            with water_pouring.make(y=1) as b:
                b.make('pouring_and_fermenting', size=8)
                b.make('soldification', size=7)
                b.make('cutting', size=7)
                b.make('pouring_off', size=3)
                b.make('extra', size=total_size - 8 - 8 - 7 - 3)

        boiling.make('termizator', size=6, visible=False)

        with boiling.make('melting', y=10, method='add') as melting:
            total_size = 25
            with melting.make(y=0) as b:
                b.make('melting_label', size=3)
                b.make('melting_name', size=total_size - 3, name='чильеджина 5кг/сердечки/фдл 0,125(безлактозная)/0,1')
            with melting.make(y=1) as b:
                b.make('serving', size=6)
                b.make('melting_process', size=total_size - 6, speed=900)
            with melting.make(y=2) as b:
                b.make(size=6, visible=False)
                b.make('cooling1', size=5)
                b.make('cooling2', size=10)

        with boiling.make('packing', y=14, method='add') as packing:
            total_size = 25
            with packing.make(y=0) as b:
                b.make('packing_label', size=3)
                b.make('packing_name', size=total_size - 3, name='чильеджина 5кг/сердечки/фдл 0,125(безлактозная)/0,1')
            with packing.make(y=1) as b:
                b.make('packing_brand', size=total_size, name='безлактозная/претто')
            with packing.make(y=2) as b:
                b.make('configuration', size=3, visible=False)
                b.make('configuration', size=1)
                b.make('configuration', size=5, visible=False)
                b.make('configuration', size=1)

