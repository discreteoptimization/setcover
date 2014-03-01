% The MIT License (MIT)
%
% Copyright (c) 2014 Andrea Rendl
%
% Permission is hereby granted, free of charge, to any person obtaining a copy
% of this software and associated documentation files (the "Software"), to deal
% in the Software without restriction, including without limitation the rights
% to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
% copies of the Software, and to permit persons to whom the Software is
% furnished to do so, subject to the following conditions:
% 
% The above copyright notice and this permission notice shall be included in
% all copies or substantial portions of the Software.
% 
% THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
% IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
% FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
% AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
% LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
% OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
% THE SOFTWARE.

% --------------------------------------------------------------- % 
%  Set covering problem - MIP formulation
% --------------------------------------------------------------- % 

include "globals.mzn";

% parameters
int: nbItems;
int: nbSets;
set of int: ITEMS = 1..nbItems;
set of int: SETS = 1..nbSets;

array [SETS] of int: weights;     % the weights of each set
array [SETS] of set of int: sets;  % the sets

% variables
array [SETS] of var 0..1: selectedSets;

% constraints
constraint    % make sure each element is in at least one of the selected sets
   forall (i in ITEMS) (sum (s in SETS where (i-1) in sets[s]) (selectedSets[s]) >= 1);
   
% objective
solve minimize sum (i in SETS) (weights[i]*selectedSets[i]);

% output directive
output [ show(selectedSets[s]) ++ " "| s in SETS ];