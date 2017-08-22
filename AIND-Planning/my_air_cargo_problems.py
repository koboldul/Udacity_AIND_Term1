from aimacode.logic import PropKB
from aimacode.planning import Action
from aimacode.search import (
    Node, Problem,
)
from aimacode.utils import expr
from lp_utils import (
    FluentState, encode_state, decode_state,
)
from my_planning_graph import PlanningGraph

import itertools

class AirCargoProblem(Problem):
    _IN = 'In'
    _AT = 'At'
    _LOAD = 'Load'
    _FLY = 'Fly'
    _UNLOAD = 'Unload'
    _CARGO = 'Cargo'
    _PLANE = 'Plane'
    _AIRPORT = 'Airport'    

    def __init__(self, cargos, planes, airports, initial: FluentState, goal: list):
        """
        :param cargos: list of str
            cargos in the problem
        :param planes: list of str
            planes in the problem
        :param airports: list of str
            airports in the problem
        :param initial: FluentState object
            positive and negative literal fluents (as expr) describing initial state
        :param goal: list of expr
            literal fluents required for goal test
        """
        self.state_map = initial.pos + initial.neg
        self.initial_state_TF = encode_state(initial, self.state_map)
        Problem.__init__(self, self.initial_state_TF, goal=goal)
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        self.actions_list = self.get_actions()

    def get_actions(self):
        '''
        This method creates concrete actions (no variables) for all actions in the problem
        domain action schema and turns them into complete Action objects as defined in the
        aimacode.planning module. It is computationally expensive to call this method directly;
        however, it is called in the constructor and the results cached in the `actions_list` property.

        Returns:
        ----------
        list<Action>
            list of Action objects
        '''
        def load_actions():
            '''Create all concrete Load actions and return a list

            :return: list of Action objects
            '''
            '''Create all concrete Unload actions and return a list

            :return: list of Action objects
            '''
            loads = []
            
            for element in itertools.product(self.cargos, self.planes, self.airports):
                cargo, plane, airport = element
                precond_pos = [expr("%s(%s,%s)"%(self._AT, plane, airport))]
                precond_pos.append(expr("%s(%s,%s)"%(self._AT, cargo, airport)))  
                precond_pos.append(expr("%s(%s)"%(self._CARGO, cargo)))  
                precond_pos.append(expr("%s(%s)"%(self._AIRPORT, airport)))  
                precond_pos.append(expr("%s(%s)"%(self._PLANE, plane)))  
                precond_neg = []
                
                effect_rem = [expr("%s(%s,%s)"%(self._AT, cargo, airport))]
                effect_add = [expr("%s(%s,%s)"%(self._IN, cargo, plane))]
                
                action_e = expr("%s(%s,%s)"%(self._LOAD, cargo, plane))
            
                action = Action(action_e, [precond_pos, precond_neg], [effect_add, effect_rem])
                loads.append(action)
            return loads

        def unload_actions():
            '''Create all concrete Unload actions and return a list

            :return: list of Action objects
            '''
            unloads = []
            
            for element in itertools.product(self.cargos, self.planes, self.airports):
                cargo, plane, airport = element
                precond_pos = [expr("%s(%s,%s)"%(self._AT, plane, airport))]
                precond_pos.append(expr("%s(%s,%s)"%(self._IN, cargo, plane)))  
                precond_pos.append(expr("%s(%s)"%(self._CARGO, cargo)))  
                precond_pos.append(expr("%s(%s)"%(self._AIRPORT, airport)))  
                precond_pos.append(expr("%s(%s)"%(self._PLANE, plane)))  
                precond_neg = []
                
                effect_add = [expr("%s(%s,%s)"%(self._AT, cargo, airport))]
                effect_rem = [expr("%s(%s,%s)"%(self._IN, cargo, plane))]
                
                action_e = expr("%s(%s,%s)"%(self._UNLOAD, cargo, plane))
            
                action = Action(action_e, [precond_pos, precond_neg], [effect_add, effect_rem])
                unloads.append(action)
            return unloads

        def fly_actions():
            '''Create all concrete Fly actions and return a list

            :return: list of Action objects
            '''
            flys = []
            for element in itertools.product(self.planes, self.airports, self.airports):
                plane, from_a, to_a = element
                if from_a == to_a:
                    continue;
                precond_pos = [expr("%s(%s,%s)"%(self._AT, plane, from_a))]
                precond_pos.append(expr("%s(%s)"%(self._PLANE, plane)))  
                precond_pos.append(expr("%s(%s)"%(self._AIRPORT, to_a)))  
                precond_pos.append(expr("%s(%s)"%(self._AIRPORT, from_a)))  
                precond_neg = []
                
                effect_rem = [expr("%s(%s,%s)"%(self._AT, plane, from_a))]
                effect_add = [expr("%s(%s,%s)"%(self._AT, plane, to_a))]
                
                action_e = expr("%s(%s,%s,%s)"%(self._FLY, plane, from_a, to_a))
            
                action = Action(action_e, [precond_pos, precond_neg], [effect_add, effect_rem])
                flys.append(action)
            return flys
        
        return unload_actions() + load_actions() + fly_actions()

    def actions(self, state: str) -> list:
        """ Return the actions that can be executed in the given state.

        :param state: str
            state represented as T/F string of mapped fluents (state variables)
            e.g. 'FTTTFF'
        :return: list of Action objects
        """
        true_states = [sm for ind_m, sm in enumerate(self.state_map) for ind_s, s in enumerate(state) if s == 'T' and ind_s==ind_m]
        possible_actions = [a for a in self.actions_list if all([(p in true_states) for p in a.precond_pos if len(p.args) > 1])]
        
        return possible_actions

    def result(self, state: str, action: Action):
        """ Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).

        :param state: state entering node
        :param action: Action applied
        :return: resulting state after action
        """
        # TODO implement
        useless = decode_state(state, self.state_map)
        pos = useless.pos
        neg = useless.neg

        for pc in action.effect_add:
           pos.append(pc)
           if pc in neg:
              neg.remove(pc)
        for pc in action.effect_rem:
           neg.append(pc)
           pos.remove(pc)

        new_state = FluentState(pos, neg)
        return encode_state(new_state, self.state_map)

    def goal_test(self, state: str) -> bool:
        """ Test the state to see if goal is reached

        :param state: str representing state
        :return: bool
        """
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for clause in self.goal:
            if clause not in kb.clauses:
                return False
        return True

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    def h_pg_levelsum(self, node: Node):
        '''
        This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition.
        '''
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    def h_ignore_preconditions(self, node: Node):
        '''
        This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        '''
        pos_s = decode_state(node.state, self.state_map)
        kb = PropKB()
        kb.tell(pos_s.pos_sentence())
        solved = [x for x in self.goal if x in kb.clauses]        

        return len(self.goal) - len(solved) 


def air_cargo_p1() -> AirCargoProblem:
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('At(C1, JFK)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('At(P1, JFK)'),
           expr('At(P2, SFO)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p2() -> AirCargoProblem:
    cargos = ['C1', 'C2', 'C3']
    planes = ['P1', 'P2', 'P3']
    airports = ['JFK', 'SFO', 'OTP']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           expr('At(P3, OTP)'),
           expr('At(C3, OTP)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('At(C2, OTP)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('In(C2, P3)'),
           expr('At(C3, SFO)'),
           expr('At(C3, JFK)'),
           expr('In(C3, P1)'),
           expr('In(C3, P2)'),
           expr('In(C3, P3)'),
           expr('At(C1, JFK)'),
           expr('At(C1, OTP)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('In(C1, P3)'),
           expr('At(P1, JFK)'),
           expr('At(P1, OTP)'),
           expr('At(P2, SFO)'),
           expr('At(P2, OTP)'),
           expr('At(P3, JFK)'),
           expr('At(P3, SFO)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, OTP)'),
            expr('At(C3, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p3() -> AirCargoProblem:
    cargos = ['C1', 'C2', 'C3', 'C4']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO', 'OTP', 'LHR']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           expr('At(C4, LHR)'),
           expr('At(C3, OTP)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('At(C2, OTP)'),
           expr('At(C2, LHR)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           
           expr('At(C1, JFK)'),
           expr('At(C1, SFO)'),
           expr('At(C1, LHR)'),
           expr('In(C1, P2)'),
           expr('In(C1, P1)'),

           expr('In(C3, P2)'),
           expr('In(C3, P1)'),
           expr('At(C3, JFK)'),
           expr('At(C3, LHR)'),
           expr('At(C3, SFO)'),

           expr('In(C4, P2)'),
           expr('In(C4, P1)'),
           expr('At(C4, JFK)'),
           expr('At(C4, OTP)'),
           expr('At(C4, SFO)'), 

           expr('At(P1, JFK)'),
           expr('At(P1, OTP)'),
           expr('At(P1, LHR)'),
           expr('At(P2, LHR)'),
           expr('At(P2, SFO)'),
           expr('At(P2, OTP)') 
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, LHR)'),
            expr('At(C2, OTP)'),
            expr('At(C3, SFO)'),
            expr('At(C4, JFK)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)