#!/usr/bin/env python
# encoding: utf-8
from math import ceil


class Estimator(object):
    def __init__(self, task):
        self.set_costs = {s.index: float(s.cost) for s in task.sets}
        self.metrics = {'cut_exp': 0, 'not_cut_exp': 0, 'rollback_exp': 0}

    def get_optimistic(self, state):
        # split every set on the not covered items and choose the cheapest one for every item
        splitted_costs = {set_idx: self.set_costs[set_idx] / len(items)
                          for set_idx, items in state.set2items.iteritems()
                          if items}
        additional = sum(min(splitted_costs[set_idx] for set_idx in sets)
                         for item, sets in state.item2sets.iteritems())
        return ceil(state.current_cost + additional)

    def cost_of_chosen_list(self, chosen_sets):
        return sum(self.set_costs[s_idx] for s_idx in chosen_sets)

    def cost_of_chosen(self, set_idx):
        return self.set_costs[set_idx]

    def pick_a_set(self, state):
        # Pick a set, basing on covering and the cost
        item_weights = {idx: 1.0 / len(sets)  # The lesser candidates has item, the more critical item is
                        for idx, sets in state.item2sets.iteritems()}
        return max(state.set2items.iteritems(),
                   key=lambda (s_idx, items): sum(item_weights[i] for i in items) / self.set_costs[s_idx])[0]
