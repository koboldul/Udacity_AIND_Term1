import math
from random import randint

####################################################################
# Helpers
####################################################################

memento = {}

class Node:
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data

def create_partition_graph(game):
    spaces = game.get_blank_spaces()
    graph = {}
    
    frontier = []
    frontier.append(spaces[0])          
    for s in spaces:
        if s not in graph.keys():
            mv = game.__get_moves__(s)
            graph.update({s:mv})            

    return graph

def game_progress_factor(game):
    '''
    Weight parameter couting the game progression. Not used in the end.
    '''
    return 49 / ( 2 * len(game.get_blank_spaces()))  

def base_score(score):
    '''
    Decorator for any heuristic. Would add  the win/loose score and corner avoidance after 35th ply.
    '''
    def wrapper(game, player):
        if game.is_loser(player):
            return float("-inf")

        if game.is_winner(player):
            return float("inf") 
        
        #key = score.__name__ + game.to_string()    
        #if key in memento.keys():
        #    res = memento[key]
        #else:
        res = score(game, player) + corner_score(game, player)     
   
        return res        

    return wrapper

def corner_score(game, player):
    '''
    Penalize a movement if is in the corner. Applies only to end game.
    '''
    if len(game.get_blank_spaces())  > 35: return 0    
    
    margin_no = 6
    
    marginal = [(0,0), (0,margin_no), (margin_no,margin_no), (margin_no,0)]
    current = game.get_player_location(player)
    opp_curr = game.get_player_location( game.get_opponent(player))
    
    factor = 1 if current in marginal else  0
    opp_factor = 1 if opp_curr in marginal else  0
    return  1000 * ( -factor + opp_factor)

####################################################################
# Heuristics
####################################################################

@base_score
def random_1(game, player):
    return randint(-3,3)

@base_score
def super_improve_score(game, player):
    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(game.get_opponent(player))
    
    return float(len(own_moves)- len(opp_moves)) * randint(-2,2)
 
@base_score   
def block_in_two(game, player):
    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(game.get_opponent(player))
    
    total_blocking = 0
    for mm in own_moves:
        total_blocking = total_blocking + len([x for x in game.__get_moves__(mm) if x in opp_moves])
    return  float(total_blocking - len(opp_moves))

##############################################################
# SUBMITTED ##################################################
##############################################################
@base_score
def free_in_two(game, player):
    '''
    Check if any of the next legal moves after this one would clash
    with the opponent position. More such positions lower the score.    
    '''
    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(game.get_opponent(player))
    
    total_free = 0
    for mm in own_moves:
        total_free = total_free + len([x for x in game.__get_moves__(mm) if x not in opp_moves])
    return  float(total_free - 2 * len(opp_moves))
##############################################################

@base_score
def as_far_aggression(game, player):
    opponent = game.get_opponent(player)
    
    opp_pos = game.get_player_location(opponent)
    own_pos = game.get_player_location(player)
    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(opponent)

    y_d = abs(opp_pos[0] - own_pos[0])
    x_d = abs(opp_pos[1] - own_pos[1])

    distance_score = math.sqrt(x_d*x_d+y_d*y_d)    
    
    return float((len(own_moves)-len(opp_moves)) - 2 * distance_score)  

@base_score
def blind_aggression(game, player):
    opponent = game.get_opponent(player)
    
    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(opponent)
    
    distance_score = [m for m in opp_moves if m in own_moves]
    
    return float((len(own_moves)-len(opp_moves)) + 4 * len(distance_score) )  #distance score is always 1

@base_score
def central_knight(game, player):
    '''
    Gives better score for moves that are located between [3,5] col/row - center
    '''
    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    current = game.get_player_location(player)
    
    pos_score = (abs(current[0]-4) + abs(current[1]-4)) 
    
    return float(2 * pos_score  +  own_moves - opp_moves)

@base_score
def division(game, player):
    margin_no = 6
        
    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(game.get_opponent(player))

    open_pos = game.get_blank_spaces()    
    
    zoneA = [x for x in open_pos if x[0]<3 and x[0]>=0 and x[1]<3 and x[1]<3]    
    zoneB = [x for x in open_pos if x[0]>3 and x[0]<=margin_no and x[1]<3 and x[1]>=0]
    zoneC = [x for x in open_pos if x[0]<3 and x[0]>=0 and x[1]>3 and x[1]<=margin_no]    
    zoneD = [x for x in open_pos if x[0]>3 and x[0]<=margin_no and x[1]>3 and x[1]<=margin_no]    

    zones = sorted([zoneA, zoneB, zoneC, zoneD], key=lambda x: len(x))        

    mv_A = [x for x in own_moves if x in  zoneA]
    mv_B = [x for x in own_moves if x in  zoneB]
    mv_C = [x for x in own_moves if x in  zoneC]
    mv_D = [x for x in own_moves if x in  zoneD]
    
    opp_A = [x for x in opp_moves if x in  zoneA]
    opp_B = [x for x in opp_moves if x in  zoneB]
    opp_C = [x for x in opp_moves if x in  zoneC]
    opp_D = [x for x in opp_moves if x in  zoneD]
    
    calc_mv = lambda x, z: len(x) * zones.index(z) / 2
    calc_opp_mv = lambda x, z: len(x) * (3 - zones.index(z)) / 2 

    own_score = calc_mv(mv_A, zoneA) + calc_mv(mv_B, zoneB)  + calc_mv(mv_C, zoneC)  + calc_mv(mv_D, zoneD) 
    opp_score = calc_opp_mv(opp_A, zoneA) + calc_opp_mv(opp_B, zoneB)  + calc_opp_mv(opp_C, zoneC)  + calc_opp_mv(opp_D, zoneD)
        
    return float(own_score + opp_score)
    
@base_score
def my_little_killer(game, player):
    '''
    Rewards longest path possible from that point further.
    '''
    graph = create_partition_graph(game)  
    
    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(game.get_opponent(player))
    
    frontier = [Node(None, n) for n in own_moves]    
    longest = 0    

    visited = []
    candiates = []
    longest_path = []
    end_reached = False
    while(frontier):
        cur = frontier.pop()
        visited.append(cur.data)
        
        if end_reached:
            end_reached = False
            if len(candiates) > len(longest_path):
                longest_path = candiates        
                if cur.parent != None:
                    lastparent_index = candiates.index(cur.parent.data)
                    candiates = candiates[:lastparent_index+1]
                else:
                    candiates = []
        candiates.append(cur.data)
        
        next_gen = [Node(cur, n) for n in graph[cur.data] if not n in visited]
        if next_gen:
            frontier = frontier + next_gen
        else:
            end_reached = True        
    '''
    Penalize for opponent being able to block the path
    '''
    opp_moves_in_path = [x for x in longest_path if x in opp_moves]
    '''
    Rewards if the path would create a partition. Should check the size of the partitions thoug to reward
    if there is a posibility to go on the larger one and the larger one has no opponent.
    '''
    block_bridge = len([m for m in own_moves if len(graph[m]) == 1])    

    return float(2 * len(longest_path) + len(opp_moves_in_path) - len(opp_moves) + 10 * block_bridge) 

@base_score
def null_score(game, player):
    return 0.

@base_score
def reversed_aggression(game, player):
    opponent = game.get_opponent(player)
    
    opp_pos = game.get_player_location(opponent)
    own_pos = game.get_player_location(player)
    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(opponent)

    y_d = abs(opp_pos[0] - own_pos[0])
    x_d = abs(opp_pos[1] - own_pos[1])

    distance_score = math.sqrt(x_d*x_d+y_d*y_d)    
    
    return float((len(own_moves)-len(opp_moves)) + 2 * distance_score)  

@base_score
def you_cant_catch_me(game, player):
    is_all_over, score = get_end_game_score(game, player)    
    if is_all_over: return score    

    opponent = game.get_opponent(player)
    
    opp_pos = game.get_player_location(opponent)
    own_pos = game.get_player_location(player)
    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(opponent)

    y_d = abs(opp_pos[0] - own_pos[0])
    x_d = abs(opp_pos[1] - own_pos[1])

    distance_score = math.sqrt(x_d*x_d+y_d*y_d)    
    
    return float((len(own_moves)-len(opp_moves))*2  + distance_score) / 3

@base_score
def you_cant_catch_me_adaptive(game, player):
    is_all_over, score = get_end_game_score(game, player)    
    if is_all_over: return score    

    opponent = game.get_opponent(player)
    
    opp_pos = game.get_player_location(opponent)
    own_pos = game.get_player_location(player)
    own_moves = game.get_legal_moves(player)
    opp_moves = game.get_legal_moves(opponent)

    y_d = abs(opp_pos[0] - own_pos[0])
    x_d = abs(opp_pos[1] - own_pos[1])

    distance_score = math.sqrt(x_d*x_d+y_d*y_d)    

    p = game_progress_factor(game)  

    return float((len(own_moves)- p * len(opp_moves)) + distance_score) 

def combine(game, player):
    spaces = game.get_blank_spaces()
    if len(spaces) > 30:
        return blind_aggression(game, player) 
    else: 
        return my_little_killer(game, player)
    
def killer_combine(game, player):
    spaces = game.get_blank_spaces()
    if len(spaces) > 36:
        return central_knight(game, player) 
    elif len(spaces) > 26:
        return free_in_two(game, player)
    else:    
        return my_little_killer(game, player)
    
