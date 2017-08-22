from SudokuGame import SudokuGame 
from SudokuGame import DiagonalSudokuGame 

def naked_twins(values, game):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in game.unitlist:
        for box in unit:
            twin = [tu for tu in unit if box != tu and len(values[box]) ==2 and values[box] == values[tu]]
            if any(twin):
                the_others = [to for to in  unit if box != to and to not in twin]
                for to in the_others:
                    for c in values[box]:
                        game.assign_value(values, to, values[to].replace(c, ''))    
    return values

def only_choice(values, game):
    digits = game._cols
    for unit in game.unitlist:
        for c in digits:
            how_many = [m for m in unit if c in values[m]]
            if len(how_many) == 1:
                game.assign_value(values, how_many[0], c)
    return values

def only_square(values, game):
    """Eliminate values using the only square strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the squares replaces by identified value.
    """
    almost_completed  =  [u for u in game.unitlist if len([b for b in u if len(values[b]) == 1]) == 7]   
    for candidate_unit in almost_completed:
        not_solved = [b for b in candidate_unit if len(values[b]) == 2]
        
        for box in not_solved:
            for unit in [u for u in game.unitlist if box in u and u != candidate_unit]:
                domain = [b for b in unit if len(values[b]) == 1]
                candiates = [b for b in domain if values[b] in values[box]]
                if any(candiates):
                    val = values[box].replace(values[candiates[0]], '')
                    game.assign_value(values, box, val)
                    break
                
    return values

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    game = DiagonalSudokuGame(diag_sudoku_grid)
    
    strategies = []
    strategies.append(only_square)
    strategies.append(only_choice)
    strategies.append(naked_twins)    
    
    game.inject_strategies(strategies)

    t = game.solve()
    game.display()
    
    try:
        from visualize import visualize_assignments
        visualize_assignments(game.get_assingments())

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
