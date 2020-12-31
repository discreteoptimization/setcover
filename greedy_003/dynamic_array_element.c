#include <stdlib.h>

#include "dynamic_array_element.h"

/* dynamically sized array; doubles size if added element exceeds capacity; elements are of type `element' */
void _double_capacity_element(struct dynamic_array_element* array) {
	struct element* extended_data = calloc(2 * array->capacity, sizeof(struct element));		
	for (int i = 0; i < array->capacity; ++i)
		extended_data[i] = (array->data)[i];
	free(array->data);
	array->data = extended_data;
	array->capacity *= 2;
}

void _add_element(struct element arg, struct dynamic_array_element* array) {
	if (array->size == array->capacity)
		_double_capacity_element(array);
	array->data[(array->size)++] = arg;
}

void initialize_element(struct dynamic_array_element* array) {
	array->data = calloc(16, sizeof(struct element));
	array->size = 0;
	array->capacity = 16;
	array->add = _add_element;
}