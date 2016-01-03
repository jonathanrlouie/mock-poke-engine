# This is a mock Pokemon engine that features an AI that human players can
# have Pokemon battles with.

# WARNING: The engine is currently incomplete and is not accurate to the games.
# The AI itself is also a work in progress and uses a naive implementation.

import random, copy

# A StateNode contains the game state at a node in the game tree, as well as
# a list of its child nodes. It also contains information about who is able
# to make a decision at this node in the game tree.

# turn is 0 when both players able to decide
# turn is 1 when only human player is able to decide
# turn is 2 when only ai is able to decide
# state is the current state at that node
# statematrix is the payoff matrix for that node
class StateNode:
    def __init__(self, turn, state, statematrix):
        self.turn = turn
        self.state = state
        self.statematrix = statematrix

# A State contains a list of the player's pokemon,
# and a list of the AI's (the opponent's) pokemon.
class State:
    def __init__(self, pokemans, enemy_pokemans):
        self.pokemans = pokemans
        self.enemy_pokemans = enemy_pokemans

# A Move has a name, an attack power value, and an accuracy
# value for the move as a percentage.
class Move:
    def __init__(self, name, atk, acc):
        self.name = name
        self.atk = atk
        self.acc = acc

# A Pokeman has a name, a set of moves it can attack with, a current
# hitpoint value, a maximum hitpoint value, and a flag indicating
# whether or not it has fainted (defaulted to False).
class Pokeman:
    def __init__(self, name, moves, hp, max_hp, fainted = False):
        self.name = name
	self.moves = moves
	self.hp = hp
	self.max_hp = max_hp
	self.fainted = fainted
        
# subtract attack power of an attack from the hp of the pokemon; check if the pokemon has fainted
def attack(pokeman, other, move, printing):
    if printing:
        print(pokeman.name + " attacks " + other.name + " using " + move.name)
    if other.hp - move.atk <= 0:
        if printing:
            print(other.name + " fainted!")
        return Pokeman(other.name, other.moves, other.hp - move.atk, other.max_hp, True)
    else:
        if printing:
            print(other.name + " now has " + str(other.hp - move.atk) + " hp")
        return Pokeman(other.name, other.moves, other.hp - move.atk, other.max_hp, False)

# Swap the positions of the pokemon in the list of pokemon to switch in a new active pokemon.
# The active pokemon is always first in the list, just like in the actual games.
def swap_pokemans(pokemans, index, printing):
    if printing:
        print(pokemans[index].name + " has been switched in!")
    pokemans_copy = copy.copy(pokemans)
    tmp = pokemans_copy[0]
    pokemans_copy[0] = pokemans_copy[index]
    pokemans_copy[index] = tmp
    return pokemans_copy

# after an attack, update the list of pokemon with the injured pokemon
def updateTeam(pokeman, pokemans):
    pokemans_copy = copy.copy(pokemans)
    pokemans_copy[0] = copy.copy(pokeman)
    return pokemans_copy

# return next state the game should be in after processing the decisions from both players
def advance_state(current_state, decision1, decision2, printing):
    new_team = copy.copy(current_state.pokemans)
    new_enemy_team = copy.copy(current_state.enemy_pokemans)

    # Process the player's decision first. This is not accurate to the actual games, where turn order is determined
    # by speed (this will be changed to better reflect the actual games)
    active_poke = new_team[0]
    enemy_active_poke = new_enemy_team[0]
    if decision1 < 4:
        new_enemy_team = updateTeam(attack(active_poke,enemy_active_poke,active_poke.moves[decision1],printing),current_state.enemy_pokemans)
    else:
        new_team = swap_pokemans(new_team, decision1-3, printing)

    # Process the AI's decision
    new_active_poke = new_team[0]
    new_enemy_active_poke = new_enemy_team[0]
    if not new_enemy_active_poke.fainted:
        if decision2 < 4:
            new_team = updateTeam(attack(new_enemy_active_poke,new_active_poke,new_enemy_active_poke.moves[decision2],printing),current_state.pokemans)
        else:
            new_enemy_team = swap_pokemans(new_enemy_team, decision2-3, printing)
    return State(new_team, new_enemy_team)

# call this when the player needs to select a new pokemon to use after one has fainted
def decide_fainted(current_state):
    decision = -1
    while decision == -1:
        selection = raw_input("Select a pokeman:\n")
        switcher = {
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5
        }
        decision = switcher.get(selection, -1)
        if decision > 0 and decision < 6 and current_state.pokemans[decision].fainted:
            print("That pokeman has already fainted!")
            decision = -1
    return State(swap_pokemans(current_state.pokemans,decision,True),current_state.enemy_pokemans)

# call this when the AI needs to select a new pokemon to use after one has fainted
def ai_decide_fainted(current_state):
    # AI decides which pokemon to use next randomly, for now
    poke_picked = random.randint(1,5)
    while current_state.enemy_pokemans[poke_picked].fainted:
        poke_picked = random.randint(1,5)
    return State(current_state.pokemans,swap_pokemans(current_state.enemy_pokemans,poke_picked,True))
        
# validate the AI's selection; if it tries to pick an illegal move, randomly pick a valid one and
# print an error message
def verify_decision(option_picked, current_state):
    picked = option_picked
    while picked > 3 and current_state.enemy_pokemans[picked-3].fainted:
        picked = random.randint(0,8)
    if not picked == option_picked:
        print("Fail: illegal move. Random pick used instead.")
    return picked

# call this when the AI needs to select a move
def ai_decide(current_state):
    # run the minmax algorithm
    option_picked = make_decision(current_state)

    # verify that the AI picked a valid move; if not, fallback to picking a random move
    option_picked = verify_decision(option_picked, current_state)
    return option_picked

# check if the current state is a game over state
def check_game_over(current_state):
    game_over = True
    for i in current_state.pokemans:
        if not i.fainted:
            game_over = False
    if not game_over:
        game_over = True
        for j in current_state.enemy_pokemans:
            if not j.fainted:
                game_over = False
    return game_over

# the game loop itself
def simulate_game(pokemans, enemy_pokemans):
    game_over = False
    current_state = State(pokemans, enemy_pokemans)
    print("Battle start!")
    while not game_over:
        # get AI's decision
        enemy_decision = ai_decide(current_state)
        print("Your team: " +
              current_state.pokemans[0].name + ", " +
              current_state.pokemans[1].name + ", " +
              current_state.pokemans[2].name + ", " +
              current_state.pokemans[3].name + ", " +
              current_state.pokemans[4].name + ", " +
              current_state.pokemans[5].name)
        print("Your opponent's team: " +
              current_state.enemy_pokemans[0].name + ", " +
              current_state.enemy_pokemans[1].name + ", " +
              current_state.enemy_pokemans[2].name + ", " +
              current_state.enemy_pokemans[3].name + ", " +
              current_state.enemy_pokemans[4].name + ", " +
              current_state.enemy_pokemans[5].name)
        decision = -1
        # get player's decision
        while decision == -1:
            selection = raw_input("Select a move (0 through 8):\n")
            switcher = {
                '0': 0,
                '1': 1,
                '2': 2,
                '3': 3,
                '4': 4,
                '5': 5,
                '6': 6,
                '7': 7,
                '8': 8
            }
            decision = switcher.get(selection, -1)
            if decision > 3 and decision < 9 and current_state.pokemans[decision-3].fainted:
                print("That pokeman has already fainted!")
                decision = -1
        new_state = advance_state(current_state, decision, enemy_decision, True)
        # check if players need to switch pokemon, as current pokemon has fainted
        if not check_game_over(new_state):
            if new_state.pokemans[0].fainted:
                new_state = decide_fainted(new_state)
            if new_state.enemy_pokemans[0].fainted:
                new_state = ai_decide_fainted(new_state)
        else:
            game_over = True
        current_state = new_state
    print("Game is over!")


# AI methods start here

# generate a tree of payoff matrices and then pick an option using a mixed strategy
def make_decision(current_state):
    tree = generate_tree(current_state, 2)
    return minmax(tree)
    

# Generate a tree of states, where the current state is the root node.
# Each node corresponds to a new state that can be reached by a joint decision between players
def generate_tree(current_state, depth):
    if (depth == 0 or check_game_over(current_state)):
        return StateNode(0, current_state, [])
    elif current_state.pokemans[0].fainted:
        # turn is set to 1 for this node, since only the player can affect the outcome of the next state
        return StateNode(1, current_state, map(lambda x: generate_tree(x, depth), generate_swap_states(current_state)))
    elif current_state.enemy_pokemans[0].fainted:
        # turn is set to 2 for this node, since only the AI can affect the outcome of the next state
        return StateNode(2, current_state, map(lambda x: generate_tree(x, depth), generate_ai_swap_states(current_state)))
    else:
        # generate a new node for a regular battle state, in which both players make decisions simultaneously
        return StateNode(0, current_state, map(lambda x: map(lambda y: generate_tree(y, depth-1), x), generate_move_states(current_state)))

# generate the states for when the player's pokemon has fainted and they select a new pokemon
def generate_swap_states(current_state):
    switches = filter(lambda x: not x[1].fainted and not x[0] == 0, zip(range(0,len(current_state.pokemans)), current_state.pokemans))
    new_states = map(lambda x: State(swap_pokemans(current_state.pokemans,x[0],False),current_state.enemy_pokemans),switches)
    # would need to simulate things like entry hazards/poison dmg here
    return new_states

# generate the states for when the AI's pokemon has fainted and the AI selects a new pokemon
def generate_ai_swap_states(current_state):
    switches = filter(lambda x: not x[1].fainted and not x[0] == 0, zip(range(0,len(current_state.enemy_pokemans)), current_state.enemy_pokemans))
    new_states = map(lambda x: State(current_state.pokemans, swap_pokemans(current_state.enemy_pokemans,x[0],False)),switches)
    # would need to simulate things like entry hazards/poison dmg here
    return new_states

# generate the states for when both players are making decisions simultaneously
def generate_move_states(current_state):
    switches = filter(lambda x: not x[1].fainted and not x[0] == 0, zip(range(0,len(current_state.pokemans)), current_state.pokemans))
    switches = map(lambda x: x[0]+3,switches)
    enemy_switches = filter(lambda x: not x[1].fainted and not x[0] == 0, zip(range(0,len(current_state.enemy_pokemans)), current_state.enemy_pokemans))
    enemy_switches = map(lambda x: x[0]+3, enemy_switches)
    return generate_move_states_helper(current_state,switches,enemy_switches)

# helper for generate_move_states; generates matrix of possible states
def generate_move_states_helper(current_state, switches, enemy_switches):
    options = range(0,4)
    options.extend(switches)
    enemy_options = range(0,4)
    enemy_options.extend(enemy_switches)
    enemy_index_options = zip(range(0,len(options)), options)
    new_states = []
    for (index,j) in enemy_index_options:
        new_states.append([])
        for i in options:
            new_states[index].append(advance_state(current_state,i,j,False))
    return new_states

# From AI perspective; higher goodness value means the state is favourable for the AI
# add 100 to goodness value of state per pokemon alive on AI's side
# subtract 100 from goodness value per pokemon alive on player's side
# total the fraction of hp remaining for each pokemon on the AI's side and add that to the goodness value
# total the fraction of hp remaining for each pokemon on the player's side and subtract that from the goodness value
def state_evaluator(state):
    ai_alive_pokes = len(filter(lambda x: not x.fainted, state.enemy_pokemans))
    other_alive_pokes = len(filter(lambda x: not x.fainted, state.pokemans))
    ai_hp_total = sum([int(100*(poke.hp / float(poke.max_hp))) for poke in state.enemy_pokemans])
    other_hp_total = sum([int(100*(poke.hp / float(poke.max_hp))) for poke in state.pokemans])
    return ai_alive_pokes * 100 - other_alive_pokes * 100 + ai_hp_total - other_hp_total

# the decision making algorithm for the AI
def minmax(tree):
    # the proper indices of the selectable options
    options = get_options(tree.state)
    # the matrix of values calculated by minmax
    values = map(lambda x: map(lambda y: minmax_helper(y),x), tree.statematrix)
    # horribly naive implementation
    sum_values = map(lambda x: sum(x), values)
    option_index = sum_values.index(max(sum_values))
    return options[option_index]

# helper for minmax to generate all possible options the AI can make in the current state
def get_options(state):
    options = []
    # since this is only for the AI to make its decision, only need to check if AI's pokemans have fainted
    if not state.enemy_pokemans[0].fainted:
        options.extend(range(0,4))
    options.extend(map(lambda y: y[0],filter(lambda x: not x[1].fainted, zip(range(4,4+len(state.enemy_pokemans)-1),state.enemy_pokemans[1:]))))
    return options

# helper for minmax to generate and propogate goodness values up the game tree
def minmax_helper(tree):
    # base case; check if child node
    if not tree.statematrix:
        return state_evaluator(tree.state)
    elif tree.turn == 1:
        # only the player is making a decision here, so just minimize the goodness value
        return min(map(lambda x: minmax_helper(x), tree.statematrix))
    elif tree.turn == 2:
        # only the AI is making a decision here, so maximize the goodness value
        return max(map(lambda x: minmax_helper(x), tree.statematrix))
    else:
        # both players are making a decision here
        values = map(lambda x: map(lambda y: minmax_helper(y), x),tree.statematrix)
        # horribly naive implementation
        return max(map(lambda x: sum(x),values))

# main method
if __name__ == '__main__':
    moves = (Move("punch", 100, 80),
             Move("dance", 120, 50),
             Move("sing", 10, 65),
             Move("ONE PUNCH", 400, 100),
             Move("kick", 40, 40),
             Move("throw", 50, 60),
             Move("slap", 20, 65),
             Move("be annoying", 10, 50))
    pokemans = [Pokeman("Jar Jar", (moves[7], moves[4], moves[1], moves[6]),300,300),
                     Pokeman("pekachu", (moves[7], moves[2], moves[3], moves[6]),400,400),
                     Pokeman("caillou",(moves[7], moves[1], moves[0], moves[3]),246,246),
                     Pokeman("chairzard", (moves[7], moves[2], moves[1], moves[6]),334,334),
                     Pokeman("mootoo", (moves[4], moves[1], moves[5], moves[7]),540,540),
                     Pokeman("nonamebrand", (moves[1], moves[2], moves[5], moves[6]),210,210)]
    enemy_pokemans = [Pokeman("enemy_Jar Jar", (moves[7], moves[4], moves[1], moves[6]),300,300),
                     Pokeman("enemy_pekachu", (moves[7], moves[2], moves[3], moves[6]),400,400),
                     Pokeman("enemy_caillou", (moves[7], moves[1], moves[0], moves[3]),246,246),
                     Pokeman("enemy_chairzard", (moves[7], moves[2], moves[1], moves[6]),334,334),
                     Pokeman("enemy_mootoo", (moves[4], moves[1], moves[5], moves[7]),540,540),
                     Pokeman("enemy_nonamebrand", (moves[1], moves[2], moves[5], moves[6]),210,210)]
    simulate_game(pokemans, enemy_pokemans)
