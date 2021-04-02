from copy import deepcopy
import numpy as np


class Boilings:
    def __init__(self, max_weight=1000, min_weight=1000, boiling_number=0):
        self.max_weight = max_weight
        self.min_weight = min_weight
        self.boiling_number = boiling_number
        self.boilings = []
        self.cur_boiling = []

    def cur_sum(self):
        if self.cur_boiling:
            return sum([x["plan"] for x in self.cur_boiling])
        return 0

    def add(self, sku, max_weight_iterator=None, boilings_count=1):
        is_next = True
        while sku["plan"] > 0:
            if is_next:
                max_weight = next(max_weight_iterator)
                is_next = False
            remainings = (
                self.max_weight - self.cur_sum()
                if not max_weight
                else max_weight - self.cur_sum()
            )
            boiling_weight = min(remainings, sku["plan"])

            new_boiling = deepcopy(sku)
            new_boiling["plan"] = boiling_weight
            new_boiling["boiling_count"] = boilings_count
            new_boiling["max_boiling_weight"] = max_weight
            new_boiling["id"] = self.boiling_number

            sku["plan"] -= boiling_weight

            self.cur_boiling.append(new_boiling)

            if boiling_weight == remainings:
                self.boilings += self.cur_boiling
                self.boiling_number += 1
                self.cur_boiling = []
                is_next = True

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

    def add_group(self, skus, max_weight=None, boilings_count=1, new=True):
        if new:
            self.add_remainings()
        for sku in skus:
            max_weight_list = CircularList()
            if isinstance(max_weight, int) or isinstance(max_weight, np.int64) or isinstance(max_weight, float):
                max_weight_list.add(int(max_weight))
            elif isinstance(max_weight, list):
                max_weight_list.create(max_weight)

            max_weight_iterator = iter(max_weight_list)
            self.add(sku, max_weight_iterator=max_weight_iterator, boilings_count=boilings_count)


class Node:
    def __init__(self, data, next):
        self.data = data
        self.next = next


class CircularList:
    def __init__(self):
        self.root = Node(None, None)
        self.root.next = self.root
        self.length = 0
        self.cur = self.root

    def add(self, data):
        if self.length == 0:
            self.root.data = data
        else:
            self.cur.next = Node(data, self.cur.next)
            self.cur = self.cur.next
        self.length += 1

    def create(self, lst):
        for item in lst:
            self.add(item)

    def __iter__(self):
        self.current_node = self.root
        self.next_node = self.root
        return self

    def __next__(self):
        if self.length == 0:
            return None
        elif self.next_node == self.root:
            self.next_node = self.next_node.next
            return self.root.data
        elif self.next_node:
            self.current_node = self.next_node
            self.next_node = self.next_node.next
            return self.current_node.data
