#include <stdlib.h>

#include "types.h"
#include "functions.h"

// pick the minimum efficiency set, and iterate over its elements, successively removing them from the other sets
void greedy_with_LUT_core(struct problem* specific_problem, struct solution* specific_solution) {
	
	// declare local variables
	int current_set_index, current_element_index;
	int stop = 0;
	int number_of_elements_picked = 0;
	struct element current_element;
	
	// allocate and initialize solution array
	specific_solution->mask_of_picked_sets = calloc(specific_problem->number_of_sets, sizeof(int));
	for (int i = 0; i < specific_problem->number_of_sets; ++i)
		specific_solution->mask_of_picked_sets[i] = 0;
	
	// initialize solution properties
	specific_solution->number_of_sets = specific_problem->number_of_sets;
	specific_solution->number_of_elements = specific_problem->number_of_elements;
	specific_solution->cost = 0;
	specific_solution->number_of_sets_picked = 0;
	
	while(!stop) {
		
		current_set_index = specific_problem->minimum_efficiency_set_index;
		current_element_index = specific_problem->sets[current_set_index].index_of_root_element;
		
		// store set that was picked
		specific_solution->mask_of_picked_sets[current_set_index] = 1;
		
		// iterate over elements
		while (current_element_index != -1) {
			
			// look up element to be removed
			current_element = specific_problem->sets[current_set_index].elements->data[current_element_index];
			
			// remove element from all sets
			remove_element_from_all_sets(current_element, specific_problem->sets, specific_problem->element_value_table);
			
			if ((++number_of_elements_picked) == specific_problem->number_of_elements) {
				// mark stop for outer set loop
				stop = 1;
				break;
			}
			
			// next element
			current_element_index = specific_problem->sets[current_set_index].elements->data[current_element_index].index_next;
		}
		
		// find new cost efficient set
		find_most_cost_efficient_set(specific_problem->sets, specific_problem->number_of_sets, &specific_problem->minimum_efficiency, &specific_problem->minimum_efficiency_set_index);

		// increment cost
		specific_solution->cost += specific_problem->sets[current_set_index].cost;
		
		// increment number of sets picked
		++specific_solution->number_of_sets_picked;
	}
	
}