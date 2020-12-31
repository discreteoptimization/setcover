Efficient greedy solver for setcover problem
============================================

Open source greedy solver for the Discrete Optimization set cover assignment.

Solves the set cover problem in time in order of the sum of elements in the sets given in the problem description.

See also problem 35.3-3 on page 1122 of "Introduction to Algorithms", 3e by Cormen, Leiserson, Rivest and Stein.
The following [Computer Science Stack Exchange entry](https://cs.stackexchange.com/questions/16142/how-to-implement-greedy-set-cover-in-a-way-that-it-runs-in-linear-time) shows concise Python code this algorithm is based upon.

The greedy solver is written in ANSI C, compiles on gcc 8.2.0 (MinGW), and needs no libraries besides standard libraries.

Compile with

`gcc -o solver.exe setcover_greedy_with_LUT_client.c greedy_with_LUT.c greedy_with_LUT_core.c read_problem_description_from_file.c find_most_cost_efficient_set.c remove_element_from_all_sets.c dynamic_array_element.c dynamic_array_index_pair.c`

Then call the solver by typing

`solver.exe ..\data\sc_27_0`

in the Windows command prompt, or any other problem description file as an argument.

Author: [Max Herrmann](https://github.com/minimental) (m.herrmann@blaetterundsterne.org)