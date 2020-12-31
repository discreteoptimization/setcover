#include <stdio.h>
#include <stdlib.h>

#include "types.h"
#include "functions.h"

/* reads problem description from file and fills `problem' data type accordingly */
void read_problem_description_from_file(const char* path, struct problem* specific_problem) {
	FILE* file = fopen(path, "r");
	// read header
	int number_of_sets, number_of_elements;
	fscanf(file, "%i %i", &number_of_elements, &number_of_sets);
	
	specific_problem->number_of_sets = number_of_sets;
	specific_problem->number_of_elements = number_of_elements;
	
	// initialize with largest float (normal) number
	specific_problem->minimum_efficiency = (float) 0x7f7fffff;
	
	// allocate and initialize set array
	specific_problem->sets = calloc(number_of_sets, sizeof(struct set));
	for (int i = 0; i < number_of_sets; ++i) {
		specific_problem->sets[i].index_of_root_element = 0;
		specific_problem->sets[i].elements = malloc(sizeof(struct dynamic_array_element));
		initialize_element(specific_problem->sets[i].elements);
	}
	
	// allocate and initialize element-value-table
	specific_problem->element_value_table = calloc(number_of_elements, sizeof(struct dynamic_array_index_pair));
	for (int i = 0; i < number_of_elements; ++i)
		initialize(&(specific_problem->element_value_table[i]));
	
	int character;
	int lineIndex = 0;
	int isCost = 1;
	int characterIndex = 0;
	int terminatingCharacterReached = 0;
	char string[32];
	int element_value;
	int element_index = 0;
	
	int character_count = 0;
	
	// skipping a line break followed by a call to `fscanf()'
	fgetc(file);
	
	// read file character-wise
	while ((character = fgetc(file)) != EOF) {
		
		// ignore 0xD (carriage return)
		if (character == 0xD) continue;	
		
		// terminating character found
		if ((character == ' ') || (character == '\n')) {				
			
			// handle multiple white spaces and white space + line break			
			if (!terminatingCharacterReached) {
				if (isCost) {
					string[characterIndex] = 0;
					specific_problem->sets[lineIndex].cost = atof(&(string[0]));
					isCost = 0;					
					
				}
				else {
					string[characterIndex] = 0;
					
					element_value = atoi(&(string[0]));
					struct index_pair element_value_table_entry;
					element_value_table_entry.set_index = lineIndex;
					element_value_table_entry.element_index = element_index;
					// add entry to element-value-table
					(specific_problem->element_value_table[element_value]).add(element_value_table_entry, &(specific_problem->element_value_table[element_value]));
					// add element to set
					struct element _element;
					_element.value = element_value;
					_element.index_previous = element_index - 1;
					_element.index_next = element_index + 1;
					((specific_problem->sets[lineIndex]).elements)->add(_element, specific_problem->sets[lineIndex].elements);
					// increment element index
					++element_index;
				}				
			}
				
			// reset character index
			characterIndex = 0;
			
			// line break found
			if (character == '\n') {					

				specific_problem->sets[lineIndex].number_of_elements = element_index;
				
				specific_problem->sets[lineIndex].efficiency = specific_problem->sets[lineIndex].cost / specific_problem->sets[lineIndex].number_of_elements;
				// mark last element of set
				specific_problem->sets[lineIndex].elements->data[element_index - 1].index_next = -1;
				// mark first element of set
				specific_problem->sets[lineIndex].elements->data[0].index_previous = -1;
				
				// identify most cost efficient set index
				if (specific_problem->sets[lineIndex].efficiency < specific_problem->minimum_efficiency) {
					specific_problem->minimum_efficiency_set_index = lineIndex;
					specific_problem->minimum_efficiency = specific_problem->sets[lineIndex].efficiency;
				}
				
				isCost = 1;
				element_index = 0;
				lineIndex++;
				
			}
			
			terminatingCharacterReached = 1;
			continue;
		}		
		
		// append character to cost/element string
		string[characterIndex++] = (char) character;
		terminatingCharacterReached = 0;		
		
	}
	
	// deal with file not ending with line break
	if (lineIndex < number_of_sets) {
		
		if (isCost) {
			string[characterIndex] = 0;
			specific_problem->sets[lineIndex].cost = atof(&(string[0]));
			isCost = 0;
		}
		else {
			string[characterIndex] = 0;
			element_value = atoi(&(string[0]));
			struct index_pair element_value_table_entry;
			element_value_table_entry.set_index = lineIndex;
			element_value_table_entry.element_index = element_index;
			// add entry to element-value-table
			(specific_problem->element_value_table[element_value]).add(element_value_table_entry, &(specific_problem->element_value_table[element_value]));
			// add element to set
			struct element _element;
			_element.value = element_value;
			_element.index_previous = element_index - 1;
			_element.index_next = element_index + 1;
			((specific_problem->sets[lineIndex]).elements)->add(_element, specific_problem->sets[lineIndex].elements);
		}
		
		specific_problem->sets[lineIndex].number_of_elements = element_index;
	}
	
	fclose(file);
	
}