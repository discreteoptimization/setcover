#include <stdlib.h>
#include <stdio.h>

#include "types.h"
#include "functions.h"

/* converts 6 into 110 */
char* convert_binary_integer_array_to_character_array(int* binary_integer_array, int number_of_elements) {
	
	char* converted_array = calloc(2 * number_of_elements + 1, sizeof(char));
	
	for (int i = 0; i < number_of_elements; ++i) {
		converted_array[2*i] = binary_integer_array[i] ? '1' : '0';
		converted_array[2*i + 1] = ' ';
	}
	
	converted_array[2 * number_of_elements - 1] = '\0';
	
	return converted_array;
}

/* given a path to the problem file, solves the problem and writes the results to the referenced output string */
void greedy_with_LUT(const char* path, char** output) {
	
	struct problem specific_problem;
	struct solution specific_solution;
	
	// read problem description from file and create element-value-table
	read_problem_description_from_file(path, &specific_problem);
	
	// solve problem
	greedy_with_LUT_core(&specific_problem, &specific_solution);
	
	// allocate memory for output
	*output = calloc(64 + 2 * specific_solution.number_of_sets, sizeof(char));
	
	// format output
	char* solution_string = convert_binary_integer_array_to_character_array(specific_solution.mask_of_picked_sets, specific_solution.number_of_sets);
	sprintf(*output, "%i 0\n%s", (int) specific_solution.cost, solution_string);
	
	// free resources
	free(solution_string);
	free(specific_problem.element_value_table);
	free(specific_problem.sets);
	free(specific_solution.mask_of_picked_sets);
	
}