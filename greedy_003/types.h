struct index_pair {
	int set_index;
	int element_index;
};

struct element {
	int value;
	int index_previous;
	int index_next;
};

struct dynamic_array_index_pair {
	int size;
	int capacity;
	
	struct index_pair* data;
	
	void (*add)(struct index_pair, struct dynamic_array_index_pair*);
};

struct dynamic_array_element {
	int size;
	int capacity;
	
	struct element* data;
	
	void (*add)(struct element, struct dynamic_array_element*);
};

struct set {
	float cost;
	float efficiency;
	int number_of_elements;
	int index_of_root_element;
	struct dynamic_array_element* elements;
};

struct problem {
	int number_of_sets;
	int number_of_elements;
	int minimum_efficiency_set_index;
	float minimum_efficiency;
	struct dynamic_array_index_pair* element_value_table;
	struct set* sets;
};

struct solution {
	int number_of_sets;
	int number_of_sets_picked;
	int number_of_elements;
	int* mask_of_picked_sets;
	double cost;
};