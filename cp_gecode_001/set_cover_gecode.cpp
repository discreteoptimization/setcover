/* -*- mode: C++; c-basic-offset: 2; indent-tabs-mode: nil -*- */
/*
 *  Main authors:
 *     Andrea Rendl <andrea.rendl@nicta.com.au> 
 *
 *  Permission is hereby granted, free of charge, to any person obtaining
 *  a copy of this software and associated documentation files (the
 *  "Software"), to deal in the Software without restriction, including
 *  without limitation the rights to use, copy, modify, merge, publish,
 *  distribute, sublicense, and/or sell copies of the Software, and to
 *  permit persons to whom the Software is furnished to do so, subject to
 *  the following conditions:
 *
 *  The above copyright notice and this permission notice shall be
 *  included in all copies or substantial portions of the Software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 *  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 *  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 *  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 *  LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 *  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 *  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 */

#include <iostream>
#include <vector>
#include <fstream>
#include <sstream> 
#include <exception>

#include <gecode/driver.hh>
#include <gecode/int.hh>
#include <gecode/minimodel.hh>

#include <string>
#include <cmath>
#include <cctype>

using namespace Gecode;
using namespace std;


/// class for parsing the problem instance specification
class SetCoverInstance  {
public:
  int _nbItems;
  int _nbSets;
  vector<int> _weights;
  vector<vector<int> > _sets;

  /// constructor
  SetCoverInstance(const char* _inst)   
  {
    ifstream infile(_inst);

    // read the header line of the instance file
    string line;
    if(!(std::getline(infile, line))) {
      cerr <<  "Could not read header line of file " << _inst << endl;
    }
    std::istringstream iss1(line);
    if (!(iss1 >> _nbItems >> _nbSets)) { 
      cerr << "Could not read #items and #sets in file " << _inst << endl;
    } 
    _weights.resize(_nbSets);
    _sets.resize(_nbSets);

    // read the set specifications of the instance file, line by line
    int setCounter=0;
    while (std::getline(infile, line))
      {
        std::istringstream iss(line);
	if(setCounter >= _nbSets) {
	  cerr << "Error: there are more sets (" << setCounter << ") defined than specified (" 
	       << _nbSets << ") in the header of in file " << _inst << endl;
	}
	int number;
        bool weight = true;
	while( iss >> number ) 
	  {
            // store the weight
            if(weight) {
              _weights[setCounter] = number;
              weight = false;
            }
	    else if(number > _nbItems) {
	      cerr << "Error: Set-element " << number << " of set " << setCounter 
		   << " is greater than the number of items: " << _nbItems  
		   << " in file " << _inst << endl;
	    }
            else {
              // store the element in the current set
              _sets[setCounter].push_back(number);
            }
	  }
        setCounter++;
      } // end of while-loop

    cout << "Finished reading instance file '" << _inst << "'" << endl;
  }
};



/// Base class for Set Covering Problem 
/// -> all Gecode problems inherit from the Script class
class SetCover : public IntMinimizeScript {
protected:
  // parameters -> instance specification
  const SetCoverInstance spec;

  // decision variables
  BoolVarArray selectedSets;
  IntVar costVar;

public:
  /// constructor
  SetCover(const InstanceOptions& opt) : 
    spec(opt.instance()),
    selectedSets(*this, spec._nbSets, 0, 1),  // initialize the 0-1 variables
    costVar(*this, 0, Int::Limits::max)          // initialize the cost variable
  {
    // we specify the problem constraints here in the constructor

    // =============== constraints =============================// 
    // the constraint that assures that each item is contained in at least one of the chosen sets
    for(int item=0; item<spec._nbItems; item++) {
      // collect the sets 's' that contain the item
      vector<BoolVar> setsContainingItem;      
      for(int s=0; s<spec._nbSets; s++)  {
        for(int i=0; i<spec._sets[s].size(); i++) {
          if(spec._sets[s][i] == item) {
            setsContainingItem.push_back(selectedSets[s]);
            break;
          }            
        }
      }
      BoolVarArgs sci(setsContainingItem); // generate a temporary variable array 'sci'
      linear(*this, sci, IRT_GQ, 1);
    }

    // the constraint for the cost
    IntArgs weights(spec._nbSets);
    for(int i=0; i<spec._nbSets; i++)
      weights[i] = spec._weights[i];
    linear(*this, weights, selectedSets, IRT_EQ, costVar);


    // =============== search: branching strategy  ===============// 
    // this branching strategy is very naive: it tries to select each set in the order in which 
    // they are defined. Can you come up with a better branching heuristic? ;)
    branch(*this, 
           selectedSets, // search variable
           INT_VAR_NONE(), // variable ordering: don't order the search variables -> search on them 'by array index'
           INT_VAL_MAX()); // value ordering: try the highest value first (==1), this means, try to add 
                           // the set before trying not to add it    
  }
    

  /// Constructor for cloning \a s
  SetCover(bool share, SetCover& s) : 
    MinimizeScript(share,s), spec(s.spec) //copy the parameter spec
  {
    // update the decision variables
    selectedSets.update(*this,  share, s.selectedSets);
    costVar.update(*this, share, s.costVar);
  }

 /// Perform copying during cloning
  virtual Space*
  copy(bool share) {
    return new SetCover(share,*this);
  }

  /// Print solution
  virtual void
  print(std::ostream& os) const {
    os << "cost: " << costVar.val() << endl;
    for(int i=0; i<spec._nbSets; i++) {      
      os << selectedSets[i].val() << " ";
    }
    os << endl;
  }

  /// Return cost variable
  virtual IntVar cost(void) const {
    return costVar;
  }

};


/** \brief Main-function
 */
int
main(int argc, char* argv[]) {

  if(argc < 2) {
    cerr << "Usage: ./set_cover <instance> [ <num-solutions> ]" << endl;
    cerr << "examples:  ./set_cover data/sc_6_1" << endl;
    cerr << "examples:  ./set_cover data/sc_25_0 4" << endl;
    return 1;
  }
  int nbSolutions = 10; // enter here the default number of solutions to search for
  if(argc == 3)
    nbSolutions = atoi(argv[2]);

  InstanceOptions opt("SetCover");
  opt.icl(ICL_DOM);
  opt.solutions(nbSolutions); 
  opt.parse(argc,argv);
  Script::run<SetCover,BAB,InstanceOptions>(opt);
  return 0;
}
