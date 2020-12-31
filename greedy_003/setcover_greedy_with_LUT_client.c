/******************************************************************************
 *
 * Solves the set cover problem with a greedy approach described in
 *
 * "Introduction to Algorithms"
 * 3rd edition
 * Cormen, Leiserson, Rivest, Stein
 *
 * section 35.3 "The set-covering problem"
 * page 1117
 * 
 * in time in order of the sum of elements in the problem sets.
 * See also exercise 35.3-3 on page 1122 and the following 
 * StackExchange Computer Science entry:
 *
 * https://cs.stackexchange.com/questions/16142/how-to-implement-greedy-set-cover-in-a-way-that-it-runs-in-linear-time
 *
 * Input: Path to problem file
 *        Example: solver.exe ..\data\sc_27_0
 *
 ******************************************************************************/

#include <stdio.h>

#include "types.h"
#include "functions.h"

int main(int nargs, char** args) {
	
	// catch missing argument
	if (nargs != 2) {
		printf("Error: Program requires path to problem description file as an argument.");
		return -1;
	}
	
	char* output;
	char* path = args[1];
	
	// solve problem
	greedy_with_LUT(path, &output);
	
	// write output to stdout
	printf("%s", output);
	
}