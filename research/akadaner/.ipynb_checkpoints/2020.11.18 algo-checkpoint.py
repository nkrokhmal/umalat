import copy
import interval

PERIODS_PER_HOUR = 12
PERIODS_PER_DAY = 24 * PERIODS_PER_HOUR


def calc_interval_length(i):
    return sum([c[1] - c[0] for c in i])


def validate(b1, b2):
    b1, b2 = min([b1, b2], key=lambda b: str(b.interval)), max([b1, b2], key=lambda b: str(b.interval))

    if calc_interval_length(b1.interval & b2.interval) != 0:
        return False

    return True


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
        return interval.interval[self.beg, self.end]

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

    def push(self, block, after=None, before=PERIODS_PER_DAY):
        after = after or 0

        cur_t = after

        while cur_t < before:
            block.local_props['t'] = cur_t

            validated = self.validate(block)

            if validated:
                self.add(block)
                return block
            else:
                # try to fit the block
                cur_t += 1

    def add(self, block):
        self.children.append(block)

    def validate(self, block):
        for b in self.children:
            validated = validate(b, block)
            if not validated:
                return False
        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def make(self, block_class='block', method='push', **kwargs):
        block = Block(block_class, props=kwargs, parent=self)
        if method == 'push':
            self.push(block)
        elif method == 'add':
            self.add(block)
        return block

    def __getitem__(self, key):
        if isinstance(key, str):
            children_with_key = [child for child in self.children if child.block_class == key]
            if len(children_with_key) == 0:
                raise KeyError(key)
            elif len(children_with_key) > 1:
                raise Exception(f'Too many keys: {key}')

            return children_with_key[0]
        elif isinstance(key, int):
            return self.children[key]

        else:
            raise Exception(f'Unknown key type {key}')

    def __iter__(self):
        yield self
        for child in self.children:
            for b in child:
                yield b

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

    for b in root:
        print(b)