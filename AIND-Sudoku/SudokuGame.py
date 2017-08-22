class SudokuGame(object):
    """Represents a Sudoku game: abstracts the grid and offer an automated way to solve it"""
    _rows = 'ABCDEFGHI'
    _cols = '123456789' #doubles as digits
    _assignments = []
    _strategies = []

    def __init__ (self, serialized_grid):
        
        self._boxes = self.cross(self._rows, self._cols)
        self.unitlist = self.create_constraints(self._rows, self._cols)
        
        units = dict((s, [u for u in self.unitlist if s in u]) for s in self._boxes)
        self._peers = dict((s, set(sum(units[s],[]))-set([s])) for s in self._boxes)
        
        if serialized_grid != None:
            self._grid = self.fill_grid(serialized_grid)
            self.display()
    
    def display(self):
        """
        Display the values as a 2-D grid.
        Args:
            values(dict): The sudoku in dictionary form
        """
        width = 1 + max(len(self._grid[s]) for s in self._boxes)
        line = '+'.join(['-'*(width*3)]*3)
        print(line)
        for r in self._rows:
            print(''.join(self._grid[r+c].center(width)+('|' if c in '36' else '')
                          for c in self._cols))
            if r in 'CF': print(line)
        print(line)
        return
    
    def cross(self, A, B):
        return [a+b for a in A for b in B]

    def get_assingments(self):
        return self._assignments    

    def fill_grid(self, serialized_grid):
        """
        Convert grid into a dict of {square: char} with '123456789' for empties.
        Args:
            grid(string) - A grid in string form.
        Returns:
            A grid in dictionary form
                Keys: The boxes, e.g., 'A1'
                Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
        """
        return dict(zip(self._boxes,[c if c!= '.' else self._cols for c in serialized_grid]))
    
    def assign_value(self, values, box, value):
        """
        Please use this function to update your values dictionary!
        Assigns a value to a given box. If it updates the board record it.
        """
        values[box] = value
        if len(value) == 1: 
            self._assignments.append(values.copy())
        return values
    
    def create_constraints(self, rows, cols):
        row_units = [self.cross(r, cols) for r in rows]
        column_units = [self.cross(rows, c) for c in cols]
        square_units = [self.cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
        
        return row_units + column_units + square_units

    def inject_strategies(self, strategies):
        self._strategies = strategies
    
    def eliminate(self, values):
        """
        Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        solved_values = [box for box in values.keys() if len(values[box]) == 1]
        for box in solved_values:
            digit = values[box]
            for peer in self._peers[box]:
                self.assign_value(values, peer, values[peer].replace(digit,''))
                
        return values

    def reduce_puzzle(self, values):
        stalled = False
        while not stalled:
            # Check how many boxes have a determined value
            solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

            self.eliminate(values) 
            for strategy in self._strategies:
                 # Sanity check, return False if there is a box with zero available values:
                if len([box for box in values.keys() if len(values[box]) == 0]):
                    return  False
                strategy(values, self)   

            # Check how many boxes have a determined value, to compare
            solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
            # If no new values were added, stop the loop.
            stalled = solved_values_before == solved_values_after
           
        return values 

    def search(self, values):
        values = self.reduce_puzzle(values)
   
        if values is False: 
            return False    

        if all(len(values[s]) == 1 for s in self._boxes): 
            return values
        else:
            v,k= min((len(values[s]), s) for s in self._boxes if len(values[s]) > 1);

            for c in values[k]:
                tc = dict(values)
                self.assign_value(tc, k, c)
                tc = self.search(tc) 
                if tc: 
                    return tc
        return False

    def solve(self):
        """
        Find the solution to a Sudoku grid.
        Args:
            grid(string): a string representing a sudoku grid.
                Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        Returns:
            The dictionary representation of the final sudoku grid. False if no solution exists.
        """
        if not any(self._strategies):
            print ('There are no solving strategies defined! This is going to be painfully slow!')
        self._grid = self.search(self._grid)
        return self._grid
        
class DiagonalSudokuGame(SudokuGame):
    """Represents a Sudoku game which also enforce diagonal restrictions"""
    def create_constraints(self, rows, cols):
        unitlist = super(DiagonalSudokuGame, self).create_constraints(rows, cols)
        diagonal_units = [[a+b for a,b in zip(rows, cols)]] + [[a+b for a,b in zip(reversed(rows), cols)]]
        
        return unitlist + diagonal_units
        
