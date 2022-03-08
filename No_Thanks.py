import random
import numpy as np
import pandas as pd
import itertools

# 1. State, Action and Reward
# ----------------------------------------------------------------------------

def hand_states():
    """
    Computes all possible combinations of cards a player could have.
    """
    
    player_cards = [-i for i in range(3,12)]
    player_card_combos = []
    
    for i in range(10):
        player_card_combos.append(list(itertools.combinations(player_cards,i)))

    return [i for sublist in player_card_combos for i in sublist]

def states():
    """
    Computes every possible state.
    
    Each state consists of 4 elements:
        
        state[0] = the open card (the card that is currently being passed between players)
        state[1] = the number of chips on the open card
        state[2] = the number of chips currently in possession of the player
        state[3] = the list of cards currently in possession of the player
    """
    
    open_card_states = [-x for x in range(3,12)]
    open_chip_states = [x for x in range(13)]
    player_chip_states = [x for x in range(13)]
    player_card_states = hand_states()
    
    states = [open_card_states, open_chip_states, player_chip_states, player_card_states]   
    states = [(i,j,k,l) for i in open_card_states for j in open_chip_states for k in player_chip_states for l in player_card_states]
    states_all = list()
    
    for i in range(len(states)):
        if (states[i][1] + states[i][2] <= 44) and (states[i][0] in states[i][3] == False):
            states_all.append(states[i])
            
    return states_all 
      
def actions():
    """
    Computes every possible action available to the player.
    
    For No Thanks!, there's only two possible actions: take or pass.
    """
    
    actions_all = ["take", "pass"]
    
    return actions_all

def card_point_tally(hand):
    """
    Calculates the total sum of all cards in a players hand, taking into account 
    that only the lowest value card counts in a run of consecutive cards.
    """
    
    hand.sort()
    
    for i in hand:
        if i-1 in hand:
            hand.remove(i)
    
    return sum(hand)
    
def rewards(states, actions):
    """
    Initialises the reward matrix. Each value corresponds to the total points of the player 
    if action[i] is chosen at state[i].
    """
    
    R = np.zeros((len(states), len(actions)))
    
    for i in range(len(states)):
        to_list = list(states[i][3])
        to_list.append(states[i][0])
        R[i][0] = states[i][2] + states[i][1] - card_point_tally(to_list)
        R[i][1] = states[i][2] - card_point_tally(list(states[i][3])) - 1
    
    R = pd.DataFrame(data = R, columns = actions, index = states)
    
    return R

# 2. Agents
# ----------------------------------------------------------------------------
    
class MonteCarloAgent(object):
    """
    Given the discrete state-action matrix, the agent navigates through the 
    fields by simulating multiple games. While the matrix is initialized with 
    all values at zero, Monte Carlo (MC) updates all visited state-action 
    values after every completed game.
    
    q(s,a) = q(s,a) + (alpha) * (R - q(s,a))

    The q-value at state s taking action a is updated dependent on the 
    achieved reward in this episode R, and the step size parameter alpha. In 
    order to decide which action to take in a respective state, the 
    epsilon-greedy form of the algorithm chooses:

    With epsilon probability: Random action
    With 1-epsilon probability: Action with maximum q-values
    """
    
    def agent_init(self, agent_init_info):
        """
        Initializes the agent to get parameters and import/create q-tables.
        Required parameters: agent_init_info as dict
        """
        
        # (1) Store the parameters provided in agent_init_info
        self.states = states()
        self.actions = actions()
        self.state_seen = list()
        self.action_seen = list()
        self.q_seen = list()
        
        self.epsilon = agent_init_info["epsilon"]
        self.step_size = agent_init_info["step_size"]
        self.R = rewards(self.states, self.actions)
        
        self.q = pd.DataFrame(data = np.zeros((len(self.states),len(self.actions))), columns = self.actions, index = self.states)
        self.visit = self.q.copy()
        
    def step(self, state_dict, actions_dict):
        """
        Choose the optimal next action according to the followed policy.
        Required parameters:
            - state_dict as dict
            - actions_dict as dict
        """
        
        # (1) Transform state dictionary into tuple
        state = tuple(state_dict)
        
        # (2) Choose action using epsilon greedy
        # (2a) Random action
        if random.random() < self.epsilon:
            actions_possible = [key for key,val in actions_dict.items() if val != 0]
            action = random.choice(actions_possible)
         
        # (2b) Greedy action
        else:
            actions_possible = [key for key,val in actions_dict.items() if val != 0]
            random.shuffle(actions_possible)
            val_max = 0
            
            for i in actions_possible:
                val = self.q.loc[[state],i][0]
                if val >= val_max:
                    val_max = val
                    action = i
        
        # (3) Add state-action pair if not seen in this simulation
        if ((state),action) not in self.q_seen:
            self.state_seen.append(state)
            self.action_seen.append(action)
            
        self.q_seen.append(((state),action))
        self.visit.loc[[state], action] += 1
        
        return action
    
    def update(self, state_dict, action):
        """
        Updating Q-values according to Belman equation
        Required parameters:
            - state_dict as dict
            - action as str
        """
        
        state = [i for i in state_dict.values()]
        state = tuple(state)
        reward = self.R.loc[[state], action][0]
        
        # Update Q-values of all state-action pairs visited in the simulation
        for s,a in zip(self.state_seen, self.action_seen):
            self.q.loc[[s], a] += self.step_size * (reward - self.q.loc[[s], a])
            print(self.q.loc[[s],a])
            
        self.state_seen, self.action_seen, self.q_seen = list(), list(), list()
        
        
class QLearningAgent(object):
    """
    In its basic form, Q-learning works in a similar way. However, while MC 
    waits for the completion of each episode before updating q-values, 
    Q-learning updates them with a lag of one step, at each step.
    
    q(s,a) = q(s,a) + (alpha) * (r + q(s-hat,a-hat) - q(s,a))
    
    The q-value is thereby dependent on the step-size parameter, the reward of 
    the next step r, and the q-value of the next step at state s-hat and 
    action-hat.

    Both algorithms consequently take the same 2 parameters which have the 
    following effects:

    Alpha: A higher step size parameter increases the change in q-values at 
    each update while prohibiting values to converge closer to their true 
    optimum.
    
    Epsilon: A higher epsilon grants more exploration of actions, which do not
    appear profitable at first sight. At the same time, this dilutes the 
    optimal game strategy when it has been picked up by the agent.
    """
    
    def agent_init(self, agent_init_info):
        """
        Initializes the agent to get parameters and import/create q-tables.
        Required parameters: agent_init_info as dict
        """
        
        # (1) Store the parameters provided in agent_init_info
        self.states = states()
        self.actions = actions()
        self.prev_state = 0
        self.prev_action = 0
        
        self.epsilon = agent_init_info["epsilon"]
        self.step_size = agent_init_info["step_size"]
        self.R = rewards(self.states, self.actions)
        
        self.q = pd.DataFrame(data = np.zeros((len(self.states),len(self.actions))), columns = self.actions, index = self.states)
        self.visit = self.q.copy()
        
    def step(self, state_dict, actions_dict):
        """
        Choose the optimal next action according to the followed policy.
        Required parameters:
            - state_dict as dict
            - actions_dict as dict
        """
        
        # (1) Transform state dictionary into tuple
        state = tuple(state_dict)
        
        # (2) Choose action using epsilon greedy
        # (2a) Random action
        if random.random() < self.epsilon:
            actions_possible = [key for key,val in actions_dict.items() if val != 0]
            action = random.choice(actions_possible)
         
        # (2b) Greedy action
        else:
            actions_possible = [key for key,val in actions_dict.items() if val != 0]
            random.shuffle(actions_possible)
            val_max = 0
            
            for i in actions_possible:
                val = self.q.loc[state,i][0]
                if val >= val_max:
                    val_max = val
                    action = i
        
        return action
    
    def update(self, state_dict, action):
        """
        Updating Q-values according to Belman equation
        Required parameters:
            - state_dict as dict
            - action as str
        """
        
        state = [i for i in state_dict]
        state = tuple(state)
        
        # (1) Set prev_state unless first turn
        if self.prev_state != 0:
            prev_q = self.q.loc[[self.prev_state], self.prev_action][0]
            this_q = self.q.loc[[state], action][0]
            reward = self.R.loc[[state], action][0]
        
            print("\n")
            print(f'prev_q: {prev_q}')
            print(f'this_q: {this_q}')
            print(f'prev_state: {self.prev_state}')
            print(f'this_state: {state}')
            print(f'prev_action: {self.prev_action}')
            print(f'this_action: {action}')
            print(f'reward: {reward}')
            
            # Calculate new Q-values
            if reward == 0:
                self.q.loc[[self.prev_state], self.prev_action] = prev_q + self.step_size * (reward + this_q - prev_q)
            else:
                self.q.loc[[self.prev_state], self.prev_action] = prev_q + self.step_size * (reward - prev_q)
        
            self.visit.loc[[self.prev_state], self.prev_action] += 1
        
        # (2) Save and return action/state
        self.prev_state = state
        self.prev_action = action

# 3. Deck
# ----------------------------------------------------------------------------

class Deck(object):
    """
    Deck consists of list of numbers (cards). Is initialised with cards labelled from 3-11. 
    Decks can be shuffled, drawn from and number of cards counted.
    """
    
    def __init__(self):
        self.deck = []
        
    def build(self):
        cards_all = range(3,12)
        deck = random.sample(cards_all, 9)
        
        for card in deck:
            self.deck.append(card)
        
        print("The deck has been shuffled.")
            
    def draw(self):
        return self.deck.pop()

    def check_end(self):
        if self.deck == []:
            return True
        
# 4. Player
# ----------------------------------------------------------------------------
        
class Player(object):
    """
    Player consists of a list of cards and number of chips in posession.
    Players can take or pass cards and/or chips. Total points to player at any
    time can be calculated.
    """
    
    def __init__(self, name):
        self.name = name
        self.card_hand = list()
        self.chip_hand = 3
        
        self.state = list()
        self.actions = dict()

    def draw_card(self, deck, player):
        global card_pool
        
        card_pool = deck.draw()
        print(f'{self.name} draws the number ' + str(card_pool) + ".")
        
        player.rand_play(player, deck)
    
    def take_card(self, player, deck):
        global card_pool
        global chip_pool
        
        self.card_hand.append(card_pool)
        self.chip_hand += chip_pool
        
        print(f'{self.name} takes the ' + str(card_pool) + " and " + str(chip_pool) + " chips.")
        
        chip_pool = 0
        
        if deck.check_end() != True:
            player.draw_card(deck, player)
        
    def pass_card(self):
        global card_pool
        global chip_pool
        
        self.chip_hand -= 1
        chip_pool += 1
        
        print(f'{self.name} passes the ' + str(card_pool) + " and loses a chip.")
        
    def identify_state(self):
    
        self.state = [-card_pool, chip_pool, self.chip_hand, self.card_hand]
        
    def identify_action(self):
        
        if self.chip_hand == 0:
            self.actions = {"take":1,"pass":0}
        else:
            self.actions = {"take":1,"pass":1}
        
    def play_agent(self, player, deck):
        
        self.identify_state()
        self.identify_action()
        
        self.action = agent.step(self.state, self.actions)
        
        if self.action == "take":
            player.take_card(player, deck)
        else:
            player.pass_card() 
            
        if algorithm == "q-learning":
            agent.update(self.state, self.action)
        
    def rand_play(self, player, deck):
        """
        Action is randomly determined. Note that players must take a card if
        they are out of chips.
        """
        global chip_pool
        decision = random.randint(0,1)
        
        if self.chip_hand == 0:
            decision == 0
        
        if decision == 0:
            player.take_card(player, deck)
            
        if decision == 1:
            player.pass_card()
            
    def point_tally(self):
        """
        Calculates the total number of points a player currently has.
        """
        
        card_points = card_point_tally(self.card_hand)
        chip_points = self.chip_hand
        return card_points - chip_points
    
    
# 5. Game
# ----------------------------------------------------------------------------

def Run_Game(player_1, player_2, player_3, algo, agent_info):
    """
    A game reflects an iteration of turns, until the deck emtpies and total
    points are tallied. Winner is then determined. Initialised with three
    players.
    """
    
    global agent, algorithm
    
    algorithm = algo
    
    if algo == "q-learning":
        agent = QLearningAgent()
    else:
        agent = MonteCarloAgent()
        
    agent.agent_init(agent_info)

    Player_1 = Player(player_1)
    Player_2 = Player(player_2)
    Player_3 = Player(player_3)

    deck = Deck()
    deck.build()
    turn_no = 1
    global card_pool
    global chip_pool 
    """
    Global used as card_pool and chip_pool need to be updated each turn so
    cannot be reset between function calls.
    """
    card_pool = 0
    chip_pool = 0
    
    Player_1.draw_card(deck, Player_1)
    
    while deck.check_end() != True:
        turn_no += 1
        
        if turn_no % 3 == 1:
            Player_1.rand_play(Player_1, deck)
            
        if turn_no % 3 == 2:
            Player_2.rand_play(Player_2, deck)
            
        if turn_no % 3 == 0:
            Player_3.play_agent(Player_3, deck)
            
    else:
        P1_total = Player_1.point_tally()
        P2_total = Player_2.point_tally()
        P3_total = Player_3.point_tally()
        
        print(f'{Player_1.name} has a final score of ' + str(P1_total))
        print(f'{Player_2.name} has a final score of ' + str(P2_total))
        print(f'{Player_3.name} has a final score of ' + str(P3_total))
        
        if min(P1_total, P2_total, P3_total) == P1_total:
            print(f'{Player_1.name} has won!!!')
            
        elif min(P1_total, P2_total, P3_total) == P2_total:
             print(f'{Player_2.name} has won!!!')
         
        elif min(P1_total, P2_total, P3_total) == P3_total:
             print(f'{Player_3.name} has won!!!')
             
agent_init_info = {"epsilon":0.2, "step_size":0.2, "new_model":True}
            
Run_Game('Alice', 'Bob', 'Charlie', "q-learning", agent_init_info)  