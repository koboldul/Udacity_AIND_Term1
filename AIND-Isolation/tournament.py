"""
Estimate the strength rating of student-agent with iterative deepening and
a custom heuristic evaluation function against fixed-depth minimax and
alpha-beta search agents by running a round-robin tournament for the student
agent. Note that all agents are constructed from the student CustomPlayer
implementation, so any errors present in that class will affect the outcome
here.

The student agent plays a fixed number of "fair" matches against each test
agent. The matches are fair because the board is initialized randomly for both
players, and the players play each match twice -- switching the player order
between games. This helps to correct for imbalances in the game due to both
starting position and initiative.

For example, if the random moves chosen for initialization are (5, 2) and
(1, 3), then the first match will place agentA at (5, 2) as player 1 and
agentB at (1, 3) as player 2 then play to conclusion; the agents swap
initiative in the second match with agentB at (5, 2) as player 1 and agentA at
(1, 3) as player 2.
"""

import itertools
import random
import warnings

from collections import namedtuple

from isolation import Board
from sample_players import RandomPlayer
from sample_players import HumanPlayer
from sample_players import GreedyPlayer
from sample_players import null_score
from sample_players import open_move_score
from sample_players import improved_score
from game_agent import *

NUM_MATCHES = 5  # number of matches against each opponent
TIME_LIMIT = 150  # number of milliseconds before timeout

TIMEOUT_WARNING = "One or more agents lost a match this round due to " + \
                  "timeout. The get_move() function must return before " + \
                  "time_left() reaches 0 ms. You will need to leave some " + \
                  "time for the function to return, and may need to " + \
                  "increase this margin to avoid timeouts during  " + \
                  "tournament play."

DESCRIPTION = """
This script evaluates the performance of the custom heuristic function by
comparing the strength of an agent using iterative deepening (ID) search with
alpha-beta pruning against the strength rating of agents using other heuristic
functions.  The `ID_Improved` agent provides a baseline by measuring the
performance of a basic agent using Iterative Deepening and the "improved"
heuristic (from lecture) on your hardware.  The `Student` agent then measures
the performance of Iterative Deepening and the custom heuristic against the
same opponents.
"""

Agent = namedtuple("Agent", ["player", "name"])


def play_match(player1, player2):
    """
    Play a "fair" set of matches between two agents by playing two games
    between the players, forcing each agent to play from randomly selected
    positions. This should control for differences in outcome resulting from
    advantage due to starting position on the board.
    """
    num_wins = {player1: 0, player2: 0}
    num_timeouts = {player1: 0, player2: 0}
    num_invalid_moves = {player1: 0, player2: 0}
    games = [Board(player1, player2), Board(player2, player1)]

    # initialize both games with a random move and response
    moves = []
    for i in range(2):
        move = random.choice(games[0].get_legal_moves())
        if i == 0:
            moves.append([move])
        else:
            moves[-1].append(move)
        games[0].apply_move(move)
        games[1].apply_move(move)

    # play both games and tally the results
    for game in games:
        winner, h, termination = game.play(time_limit=TIME_LIMIT)
        h = moves + h
        import json
        j = json.dumps(h)
        
        if not SUPRESS_MESSAGES:
            print('Winner {0}'.format(winner.get_name()))
            #print('\nFirst_player_won: {0}. Game: {1}'.format(winner.get_name() == game.__player_1__.get_name(), j))
            #input("Press Enter to continue...")
        
        if player1 == winner:
            num_wins[player1] += 1

            if termination == "timeout":
                num_timeouts[player2] += 1
            else:
                num_invalid_moves[player2] += 1

        elif player2 == winner:

            num_wins[player2] += 1

            if termination == "timeout":
                num_timeouts[player1] += 1
            else:
                num_invalid_moves[player1] += 1

    if sum(num_timeouts.values()) != 0:
        warnings.warn(TIMEOUT_WARNING)

    return num_wins[player1], num_wins[player2]


def play_round(agents, num_matches):
    """
    Play one round (i.e., a single match between each pair of opponents)
    """
    agent_1 = agents[-1]
    wins = 0.
    total = 0.

    print("\nPlaying Matches:")
    print("----------")

    for idx, agent_2 in enumerate(agents[:-1]):

        counts = {agent_1.player: 0., agent_2.player: 0.}
        names = [agent_1.name, agent_2.name]
        
        agent_1.player.set_name(agent_1.name)            
        agent_2.player.set_name(agent_2.name)            
        

        print("  Match {}: {!s:^11} vs {!s:^11}".format(idx + 1, *names), end=' ')

        # Each player takes a turn going first
        for p1, p2 in itertools.permutations((agent_1.player, agent_2.player)):
            for _ in range(num_matches):
                score_1, score_2 = play_match(p1, p2)
                counts[p1] += score_1
                counts[p2] += score_2
                total += score_1 + score_2

        wins += counts[agent_1.player]

        print("\tResult: {} to {}".format(int(counts[agent_1.player]),
                                          int(counts[agent_2.player])))

    return 100. * wins / total


def main():

    HEURISTICS = [("Null", null_score),
                  ("Open", open_move_score),
                  ("Improved", improved_score)]
    AB_ARGS = {"search_depth": 5, "method": 'alphabeta', "iterative": False}
    MM_ARGS = {"search_depth": 3, "method": 'minimax', "iterative": False}
    CUSTOM_ARGS = {"method": 'alphabeta', 'iterative': True}
    PVS_ARGS = {"method": 'pvs', 'iterative': True}

    # Create a collection of CPU agents using fixed-depth minimax or alpha beta
    # search, or random selection.  The agent names encode the search method
    # (MM=minimax, AB=alpha-beta) and the heuristic function (Null=null_score,
    # Open=open_move_score, Improved=improved_score). For example, MM_Open is
    # an agent using minimax search with the open moves heuristic.
    mm_agents = [Agent(CustomPlayer(score_fn=h, **MM_ARGS), "MM_" + name) for name, h in HEURISTICS]
    ab_agents = [Agent(CustomPlayer(score_fn=h, **AB_ARGS), "AB_" + name) for name, h in HEURISTICS]
    random_agents = [Agent(RandomPlayer(), "random"), Agent(GreedyPlayer(), "greedy")]
    THE_agent = [Agent(CustomPlayer(score_fn=improved_score, **CUSTOM_ARGS), "ID_Improved")]
    
    # ID_Improved agent is used for comparison to the performance of the
    # submitted agent for calibration on the performance across different
    # systems; i.e., the performance of the student agent is considered
    # relative to the performance of the ID_Improved agent to account for
    # faster or slower computers.
    #test_agents = [Agent(CustomPlayer(score_fn=improved_score, **CUSTOM_ARGS), "ID_Improved"),
    #               Agent(CustomPlayer(score_fn=custom_score, **CUSTOM_ARGS), "Student")]
    
    test_agents = [
        #Agent(CustomPlayer(score_fn=my_little_killer, **CUSTOM_ARGS), "my_little_killer"),
        #Agent(CustomPlayer(score_fn=you_cant_catch_me_adaptive, **CUSTOM_ARGS), "you_cant_catch_me_adaptive"),
        #Agent(CustomPlayer(score_fn=reversed_aggression, **CUSTOM_ARGS), "reversed_aggression"),
        Agent(CustomPlayer(score_fn=improved_score, **CUSTOM_ARGS), "ID_Improved"),
        #Agent(CustomPlayer(score_fn=as_far_aggression, **CUSTOM_ARGS), "as_far_aggression"),
        #Agent(CustomPlayer(score_fn=super_improve_score, **CUSTOM_ARGS), "super_improve_score"),
        #Agent(CustomPlayer(score_fn=random_1, **CUSTOM_ARGS), "random"),
        #Agent(CustomPlayer(score_fn=block_in_two, **CUSTOM_ARGS), "block_in_two"),
        Agent(CustomPlayer(score_fn=free_in_two, **CUSTOM_ARGS), "free_in_two"),
        Agent(CustomPlayer(score_fn=blind_aggression, **CUSTOM_ARGS), "blind"),
        #Agent(CustomPlayer(score_fn=you_cant_catch_me, **CUSTOM_ARGS), "you_cant_catch_me"),
        #Agent(CustomPlayer(score_fn=central_knight, **CUSTOM_ARGS), "central_knight"),
        #Agent(CustomPlayer(score_fn=division, **CUSTOM_ARGS), "division"),
        Agent(CustomPlayer(score_fn=combine, **CUSTOM_ARGS), "The chosen one"),
        #Agent(CustomPlayer(score_fn=killer_combine, **CUSTOM_ARGS), "killer_combine")   
    ]

    print(DESCRIPTION)
    for agentUT in test_agents:
        print("")
        print("*************************")
        print("{:^25}".format("Evaluating: " + agentUT.name))
        print("*************************")

        agents = random_agents + mm_agents + ab_agents + [agentUT]
        human = THE_agent + [ Agent(HumanPlayer(), "human") ] 
        if USE_HUMAN:
            win_ratio = play_round(human, NUM_MATCHES)
        else:
            win_ratio = play_round(agents, NUM_MATCHES)

        print("\n\nResults:")
        print("----------")
        print("{!s:<15}{:>10.2f}%".format(agentUT.name, win_ratio))


if __name__ == "__main__":
    SUPRESS_MESSAGES = True # supress some messages used during development
    USE_HUMAN = False # uses the human player and turns on the UI
    main()
