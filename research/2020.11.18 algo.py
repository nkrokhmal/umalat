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
        self.update_props()

    def update_props(self):
        if self.parent:
            # accumulated keys
            self.props = copy.deepcopy(self.parent.props)
        else:
            self.props = {}

        for key in self.local_props:
            if key not in self.props:
                self.props[key] = self.local_props[key]
            else:
                # both contain key
                if key in ['t', 'y']:  # accumulated keys
                    self.props[key] = self.props[key] + self.local_props[key]
                else:
                    self.props[key] = self.local_props[key]

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
            block.update_props()

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


if __name__ == '__main__':
    root = Block('boiling', props={'block_num': 12})

    with root as boiling:
        total_size = 27
        with boiling.make('water_pouring', y=6) as water_pouring:
            with water_pouring.make(y=0) as upper_block:
                upper_block.make('pouring', size=6, block_num=12)
                upper_block.make('pouring_name', size=total_size - 6, name='чильеджина  3,6 альче  8500кг')
            with water_pouring.make(y=1) as lower_block:
                lower_block.make('pouring_and_fermenting', size=8)
                lower_block.make('soldification', size=7)
                lower_block.make('cutting', size=7)
                lower_block.make('pouring_off', size=3)
                lower_block.make('extra', size=total_size - 8 - 8 - 7 - 3)

    print(root)