assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# vmihaylov: creating diagonal constraints for diagonal Sudoku
# vmihaylov (code-review fix): changed direct enumeration of boxes to more flexible - loops over rows and columns
diagonal_units = [[r + c for r, c in zip(rows, cols)], [r + c for r, c in zip(rows, cols[::-1])]]

# vmihaylov: adding diagonal constraints to constraint list
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    
    # vmihaylov (code-review fix): replace value of box with new one and save a copy of values into history for further visualization
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    
    # vmihaylov: looking for twins inside every unit. twin is two-digit value appearing twice in unit
    for unit in unitlist:
        # vmihaylov: collecting all two-digit values in unit
        two_digit_values = [values[box] for box in unit if len(values[box]) == 2] 
        
        # vmihaylov: finding twins by computing two-digit values appearing twice in unit
        twins = [twin for twin in set(two_digit_values) if two_digit_values.count(twin) == 2] 
        
        # vmihaylov: Eliminate the naked twins as possibilities for their peers. NB: peers in this case are not global peers array for box, but other (non-twin) boxes of same unit
        # vmihaylov: checking if non-twin box in unit has any of twin's digit and removing this digit from list of possibilities for that particular box
        for twin in twins:
            for box in unit:
                if values[box] != twin: # vmihaylov: skipping twin's box
                    for digit in twin: 
                        if digit in values[box]:
                            assign_value(values, box, values[box].replace(digit, ''))

    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    
    chars = []
    digits = '123456789'
    
    # vmihaylov (code-review fix): traversing grid and storing it digits in chars array, if found dot in chars (stands for empty, unsolved box), put there all possible options - i.e. 123456789
    for c in grid:
        # vmihaylov: code was a bit inaccurate since allowed to input unexpected chars like 'a', '_' etc in grid - now it throws exception if something except 1..9, '.' found.
        assert(c in digits + '.')
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
            
    # vmihaylov (code-review fix): check if grid has proper (9 x 9) size 
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """

    # vmihaylov (code-review fix): determining size of biggest cell to have enough space to fit all box possibilities 
    width = 1+max(len(values[s]) for s in boxes)
    
    # vmihaylov (code-review fix): calculating horizontal lines
    line = '+'.join(['-'*(width*3)]*3)
    
    # vmihaylov (code-review fix): drawing grid cell by cell with vertical separator every 3 cols and horizontal separator every 3 rows
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    # vmihaylov (code-review fix)
    Looks for boxes with single possible digit and remove this digit from all possibilities of peers (i.e. from same row, same column, same square and in case of diagonal sudoku if box is on main diagonal - from diagonal(s) respectively 
    Args: 
        values(dict): The sudoku in dictionary form
    """
    
    # vmihaylov (code-review fix): looking for boxes with single possibility inside
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    
    # vmihaylov (code-review fix): traversing all boxes with single possibility inside
    for box in solved_values:
        # vmihaylov (code-review fix): determining digit inside box
        digit = values[box]
        
        # vmihaylov (code-review fix): looking for peers of box and removing particular value from list of peer's possibilities
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    """
    # vmihaylov (code-review fix)
    Looks for digit that appears only once in possibility list of all boxes inside unit and places this digit instead of list of possible values 
    Args: 
        values(dict): The sudoku in dictionary form
    """
    
    # vmihaylov (code-review fix): traversing all units and for every digit counting number of occurences of this digit inside of possibility list of every box
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            # vmihaylov (code-review fix): if digit appears only once in possibility list of all boxes inside unit, then replace possibility list of this box with digit. Original algorytm could replace digit with same digit, so it could eat more memory since assign_values stores whole copy of values for each assignment in history - small fix "values[dplaces[0]] != digit" reduces memory usage
            if len(dplaces) == 1 and values[dplaces[0]] != digit:
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    # vmihaylov (code-review fix)
    Tries eliminate, only_choice and naked_twins strategy with sudoku in dictionary form as long as list of possibilities reduces 
    Args: 
        values(dict): The sudoku in dictionary form
    """
 
    stalled = False
    while not stalled:
        # vmihaylov (code-review fix): storing copy of values to compare after eliminate/only_choice/naked_twins
        solved_values_before = values.copy() 
        
        # vmihaylov (code-review fix): apply eliminate/only_choice/naked_twins strategy
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        
        # vmihaylov (code-review fix): just new reference to values to make explicit what is "Stalled" means
        solved_values_after = values 
        
        # vmihaylov (code-review fix): stalled means we did not make any progress with our strategies last time we applied them, so second attempt will not make any progress and we shoud break cycle and return current sudoku with progress we have now
        stalled = solved_values_before == solved_values_after
        
        # vmihaylov (code-review fix): for case of incorrect sudoku - if we have some box with zero possibilities, break cycle and return false instead of sudoku grid
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
