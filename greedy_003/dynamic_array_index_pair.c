#include <stdlib.h>

#include "dynamic_array_index_pair.h"

/* dynamically sized array; doubles size if added element exceeds capacity; elements are index pairs */
void _double_capacity(struct dynamic_array_index_pair* array) {
	struct index_pair* extended_data = calloc(2 * array->capacity, sizeof(struct index_pair));		
	for (int i = 0; i < array->capacity; ++i)
		extended_data[i] = (array->data)[i];
	free(array->data);
	array->data = extended_data;
	array->capacity *= 2;
}

void _add(struct index_pair arg, struct dynamic_array_index_pair* array) {
	if (array->size == array->capacity)
		_double_capacity(array);
	array->data[(array->size)++] = arg;
}

void initialize(struct dynamic_array_index_pair* array) {
	array->data = calloc(16, sizeof(struct index_pair));
	array->size = 0;
	array->capacity = 16;
	array->add = _add;
}