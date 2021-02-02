from copy import deepcopy


class Boilings:
    def __init__(self, max_weight=1000, min_weight=1000, boiling_number=0):
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.boiling_number = boiling_number
        self.boilings = []
        self.cur_boiling = []

    def cur_sum(self):
        if self.cur_boiling:
            return sum([x['plan'] for x in self.cur_boiling])
        return 0

    def add(self, sku):
        while sku['plan'] > 0:
            remainings = self.max_weight - self.cur_sum()
            boiling_weight = min(remainings, sku['plan'])
            new_boiling = deepcopy(sku)
            new_boiling['plan'] = boiling_weight
            new_boiling['id'] = self.boiling_number
            sku['plan'] -= boiling_weight
            self.cur_boiling.append(new_boiling)
            if boiling_weight == remainings:
                self.boilings += self.cur_boiling
                self.boiling_number += 1
                self.cur_boiling = []

    def finish(self):
        if self.cur_boiling:
            self.boilings += self.cur_boiling
            self.boiling_number += 1
            self.cur_boiling = []

    def add_remainings(self):
        if self.cur_boiling:
            self.boilings += self.cur_boiling
            self.boiling_number += 1
            self.cur_boiling = []

    def add_group(self, skus, new=True):
        if new:
            self.add_remainings()
        for sku in skus:
            self.add(sku)


class MergedBoilings:
    def __init__(self, max_weight=1000, min_weight=1000, boiling_number=0):
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.boiling_number = boiling_number
        self.boilings = []
        self.cur_boiling = []

    def add_sku(self, sku):
        new_boiling = deepcopy(sku)
        new_boiling['plan'] = sku['plan']
        new_boiling['id'] = self.boiling_number
        self.cur_boiling.append(new_boiling)

    def finish(self):
        if self.cur_boiling:
            self.boilings += self.cur_boiling
            self.boiling_number += 1
            self.cur_boiling = []

    def add_group(self, skus, new=True):
        if new:
            self.finish()
        for sku in skus:
            self.add_sku(sku)
