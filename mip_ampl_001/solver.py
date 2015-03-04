#!/usr/bin/python
import os
from subprocess import Popen, PIPE

def parse_solver_output(output):
    # TODO: analyze output the first line from setcover.sol
    # to determine if we get optimal solution or we stops since time limit
    lines = output.split('\n')
    for i in xrange(len(lines)):
        if lines[i].startswith('==========='):
            obj = float(lines[i+1])
            solution = list(lines[i+2].split(' ')[:-1])
            return obj, solution

def convert_input_data(input_data):
    lines = input_data.split('\n')
    N = lines[0].split(' ')[0]
    M = lines[0].split(' ')[1]
    
    f = open('setcover.data', 'wt')
    f.write('data;\n\n')
    f.write('param n := ' + N + ';\n')
    f.write('param m := ' + M + ';\n')
    f.write('\n')
    f.write('set E := \n')
    cost = []
    for i in xrange(1, int(M) + 1):
        parts = lines[i].split(' ')
        cost.append(parts[0])
        for j in xrange(1, len(parts)):
            f.write('   ' + str(i) + ' ')
            f.write(str(int(parts[j])+1) + '\n')
    f.write(';\n\n')
    f.write('param w:= ')
    for i in xrange(1, int(M) + 1):
        f.write(str(i) + ' ' + cost[i-1] + ', ')
    f.write(';\n\n')
    f.write('end;\n')
    f.close()
   
def run_ampl(input_data, solver):
    old_path = os.getcwd()
    os.chdir('./ampl/')
    
    # parse the input
    convert_input_data(input_data)

    # Run solver to solve set cover problem
    # We run twice ampl.exe to avoid use much memory
    # ampl.exe can consume about 600Mb of RAM on some problems
    process = Popen(['ampl.exe', 'setcover_commands1'], stdout=PIPE, stderr=PIPE)
    process.communicate()
    if solver == 'gurobi':
        # time limit = 300 seconds
        os.environ['gurobi_options'] = 'timelim=300 mipgap=1e-8'
        process = Popen(['gurobi.exe', 'setcover.nl', '-AMPL'], stdout=PIPE, stderr=PIPE)
        process.communicate()
        os.environ['gurobi_options'] = ''
    elif solver == 'cplex':
        # time limit = 300 seconds
        os.environ['cplex_options'] = 'timelimit=300 mipgap=1e-8'
        process = Popen(['cplex.exe', 'setcover.nl', '-AMPL'], stdout=PIPE, stderr=PIPE)
        process.communicate()
        os.environ['cplex_options'] = ''
    process = Popen(['ampl.exe', 'setcover_commands2'], stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = process.communicate()
    
    os.chdir(old_path)
    return parse_solver_output(stdout)
    
def solve_it(input_data):
    # Run AMPL on the input data, available solver:
    #  gurobi
    #  cplex
    obj, solution = run_ampl(input_data, 'gurobi')
    
    # prepare the solution in the specified output format
    output_data = str(obj) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

#import sys
#print solve_it(open(sys.argv[1]).read())
