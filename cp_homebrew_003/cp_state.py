#!/usr/bin/env python
# encoding: utf-8
from collections import defaultdict

from cp_estimator import Estimator


class State(object):
    def __init__(self, estimator, set2items, item2sets,
                 parent=None, picked_set=None, decision=None):
        # Don't use this constructor directly. Use .from_task() instead
        self.estimator = estimator  # just copy the pointer from the parent for fast access
        self.set2items = set2items  # {set_index: set(indexes of not covered items)}
        self.item2sets = item2sets  # {item_index: set(indexes of sets that can cover the item and have no decision yet)}
        self.parent = parent        # parent state object
        self.picked_set = picked_set  # picked set index
        self.decision = decision    # whether we build picked_set or not
        self.is_feasible = True
        if decision:
            self.chosen_sets = {picked_set}
        else:
            self.chosen_sets = set()
        self.propagate_constaints()
        if self.is_feasible:
            self.recalc_cost()

    def recalc_cost(self):
        additional = self.estimator.cost_of_chosen_list(self.chosen_sets)
        if self.parent is None:
            self.current_cost = additional
        else:
            self.current_cost = self.parent.current_cost + additional

    @classmethod
    def from_task(cls, task):
        # Make initial state
        estimator = Estimator(task)

        set2items = {s.index: set(s.items) for s in task.sets}
        item2sets = defaultdict(set)
        for set_idx, set_items in set2items.iteritems():
            for item_idx in set_items:
                item2sets[item_idx].add(set_idx)

        return cls(estimator, set2items, dict(item2sets),
                   parent=None, picked_set=None, decision=False)

    def __repr__(self):
        return 'State(picked={},chosen={})'.format(self.picked_set, self.decision)

    # Search

    def next_child(self):
        picked_set = self.estimator.pick_a_set(self)
        return self.create_child(picked_set, decision=True)

    def create_child(self, picked_set, decision):
        set2items = {s: i.copy() for s, i in self.set2items.iteritems()}  # Copy for mutating in child state
        item2sets = {i: s.copy() for i, s in self.item2sets.iteritems()}  # TODO: Copy is expensive. Can we avoid it?
        return self.__class__(self.estimator, set2items, item2sets,
                              parent=self, picked_set=picked_set, decision=decision)

    def negate(self):
        # Generate sibling state, where picked_set is not chosen
        # If we already there, rollback to the parent state and repeat on it
        state = self
        while state:
            if state.decision:
                return state.parent.create_child(state.picked_set, decision=False)
            else:
                state = state.parent
        return None # if we have eventually got stat = None, it means that we are reached initial state

    # Constraints propagation

    def propagate_constaints(self):
        if self.decision:
            self.propagate_on_choice()
        else:
            self.propagate_on_toss()

    def propagate_on_choice(self):
        self.on_sets_chosen(self.chosen_sets)  # there is only one set in chosen_sets (picked_set)

    def propagate_on_toss(self):
        if self.picked_set is not None:  # "if we are not at the init state"
            orphaned_items = self.set2items.pop(self.picked_set)
            for item_idx in orphaned_items:
                sets = self.item2sets[item_idx]
                sets.remove(self.picked_set)
                if not sets:
                    self.is_feasible = False
                    # We can't cover the item.
                    # No matter, what else. State doesn't lead to any feasible solutions
                    return

            # before = len(self.set2items)
            # self.remove_expensive_subsets(orphaned_items,  # Too expensive calculations :o(
            #                               self.estimator.cost_of_chosen(self.picked_set))
            # after = len(self.set2items)
            # if after != before:
            #     self.estimator.metrics['cut_exp'] += 1
            # else:
            #     self.estimator.metrics['not_cut_exp'] += 1
            # if not self.is_feasible:
            #     self.estimator.metrics['rollback_exp'] += 1
            #     return

        # Immediately set 1 for every set that can't be replaced with another set
        required_sets = self.detect_required_sets()
        self.chosen_sets.update(required_sets)
        self.on_sets_chosen(required_sets)

    def detect_required_sets(self):
        required_sets = set()
        for item, sets in self.item2sets.iteritems():
            if len(sets) == 1:  # only one set can cover this item
                required_sets.update(sets)
        return required_sets

    def on_items_covered(self, to_remove):
        overvalued_sets = set()
        for item in to_remove:
            overvalued_sets.update(self.item2sets.pop(item))

        for s in overvalued_sets & set(self.set2items):
            items = self.set2items[s]
            items -= to_remove
            if not items:
                del self.set2items[s]

        #before = len(self.set2items)
        #self.remove_redundant_sets(overvalued_sets & set(self.set2items))  # expensive operation. Work good only on the large datasets
        #after = len(self.set2items)
        #if after < before:
        #    print 'profit {}->{}'.format(before, after)

    def remove_expensive_subsets(self, items, cost_limit):
        # We can cover items with the cost=cost_limit
        # But we don't do that. So, we don't want to cover the items with the more expensive sets
        costs = self.estimator.set_costs

        iter_items = iter(items)
        candidates = list(self.item2sets[next(iter_items)])

        for cand_idx in candidates:
            if costs[cand_idx] >= cost_limit:
                cand_items = self.set2items[cand_idx]
                if len(cand_items) <= len(items) and cand_items <= items:
                    del self.set2items[cand_idx]

                    for item_idx in cand_items:
                        sets = self.item2sets[item_idx]
                        sets.remove(cand_idx)
                        if not sets:
                            self.is_feasible = False
                            return  # We cant cover the item

    def on_sets_chosen(self, sets):
        covered_items = set()
        for s in sets:
            covered_items.update(self.set2items.pop(s))

        self.on_items_covered(covered_items)

    # Getting info

    def is_all_covered(self):
        return not self.item2sets

    def get_optimistic_cost(self):
        return self.estimator.get_optimistic(self)


if __name__ == '__main__':
    from reader import read_input
    from time import time as now
    state = State.from_task(read_input('sc_15_0'))
    # st = now()
    # state.remove_redundant_sets()
    # print now() - st
