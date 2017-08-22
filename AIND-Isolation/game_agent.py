"""This file contains all the classes you must complete for this project.

You can use the test cases in agent_test.py to help during development, and
augment the test suite with your own test cases to further test your code.

You must test your agent's strength against a set of agents with known
relative strength using tournament.py and include the results in your report.
"""
import math

from sample_players import Player
from score_functions import *

custom_score = free_in_two

class Timeout(Exception):
    """Subclass base exception for code clarity."""
    pass

class CustomPlayer(Player):
    """Game-playing agent that chooses a move using your evaluation function
    and a depth-limited minimax algorithm with alpha-beta pruning. You must
    finish and test this player to make sure it properly uses minimax and
    alpha-beta to return a good move before the search time limit expires.

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    iterative : boolean (optional)
        Flag indicating whether to perform fixed-depth search (False) or
        iterative deepening search (True).

    method : {'minimax', 'alphabeta'} (optional)
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    _minimax = 'minimax'
    _prunning = 'alphabeta'
    _pvs = 'pvs'    
    
    def __init__(self, search_depth=3, score_fn=super_improve_score,
                 iterative=True, method='minimax', timeout=10.):
        self.search_depth = search_depth
        self.iterative = iterative
        self.score = score_fn
        self.method = method
        self.time_left = None
        self.TIMER_THRESHOLD = timeout
        self._graph = None
        self.is_alpha_method = method == self._prunning

    def get_move(self, game, legal_moves, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        This function must perform iterative deepening if self.iterative=True,
        and it must use the search method (minimax or alphabeta) corresponding
        to the self.method value.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        legal_moves : list<(int, int)>
            A list containing legal moves. Moves are encoded as tuples of pairs
            of ints defining the next (row, col) for the agent to occupy.

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left
        #if self._graph == None:
        #    self._graph = create_partition_graph(game)
        try:
            if not legal_moves:
                return (-1, -1)
            move = legal_moves[0]
            depth =  1 if self.iterative else self.search_depth 
            done = False
            while not done:
                if self.is_alpha_method:
                    score, pos = self.alphabeta(game, depth)            
                elif self.method == self._pvs:
                    score, pos = self.pvs(game, depth)            
                else:
                    score, pos = self.minimax(game, depth)            
                move = pos if pos != None else move
                depth = depth + 1

                done = not self.iterative or abs(score) == math.inf

        except Timeout:
            pass
        #print('Func {0} depth {1} '.format(self.score.__name__, depth)) 
        return move

    def minimax(self, game, depth, maximizing_player=True):
        return self.get_min_max_value(0, depth, game) 
    
    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        return self.get_min_max_value(0, depth, game)
    
    def get_min_max_value(self, depth, max_depth, game, is_max=True, alpha=-math.inf, beta=math.inf):
        if self.time_left() < self.TIMER_THRESHOLD:
           raise Timeout()
        score = -math.inf if is_max else math.inf 
        pos = game.NOT_MOVED
         
        utility = game.utility(self)
        if utility != 0:
             score = utility
        elif depth == max_depth:
             score = self.score(game, self)
        else:
            next_type = not is_max
            
            for scenario in game.get_legal_moves():
                s, _ = self.get_min_max_value(depth+1, max_depth, game.forecast_move(scenario), next_type, alpha, beta) 
                if (is_max and score < s) or (next_type and score > s):
                    pos = scenario
                    score = s                
                if self.is_alpha_method:
                    if is_max: alpha = max(score, alpha)
                    else: beta = min(score, beta)
                    if (beta <= alpha): break;    
                    
        return (score, pos)  

    def pvs(self, game, depth, color=1, alpha=-math.inf, beta=-math.inf):
        if self.time_left() < self.TIMER_THRESHOLD:
           raise Timeout()
        score = -math.inf
        pos = game.NOT_MOVED
         
        utility = game.utility(self)
        if utility != 0:
             score = utility
        elif depth == 0:
             score = self.score(game, self)
        else:
            first_child = True
            for scenario in game.get_legal_moves():
                s = None
                if not first_child:                
                    s, _ = self.pvs(game.forecast_move(scenario), depth-1, -color, -alpha-1, -alpha) 
                    if alpha < s < beta:
                        s, _ = self.pvs(game.forecast_move(scenario),depth-1,  -color, -beta, s) 
                else:
                    first_child = False            
                    s, _ = self.pvs(game.forecast_move(scenario),depth-1,  -color, -beta, -alpha) 
                s = -s
                if alpha < s:
                    alpha = s
                    pos = scenario 
                score = alpha
                if alpha <= beta: break;
                    
        return (score, pos)  
