#include "types.h"

/* from the given sets, finds the set with the least cost/(number of elements ratio) */
void find_most_cost_efficient_set(struct set* sets, int number_of_sets, float* minimum_efficiency, int* minimum_efficiency_set_index) {
	
	// reset minimum efficiency value: largest float (normal) number
	*minimum_efficiency = (float) 0x7f7fffff;
	
	// identify most cost efficient set index
	for (int i = 0; i < number_of_sets; ++i) {
		
		sets[i].efficiency = sets[i].cost / sets[i].number_of_elements;
		
		if (sets[i].efficiency < *minimum_efficiency) {
			*minimum_efficiency_set_index = i;
			*minimum_efficiency = sets[i].efficiency;
		}		
	}	
	
}