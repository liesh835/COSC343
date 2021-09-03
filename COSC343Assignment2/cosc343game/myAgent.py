import numpy as np
from numpy import random
import random

playerName = "myAgent"
nPercepts = 75  # This is the number of percepts
nActions = 5  # This is the number of actions
nChromosomes = 7  # This is the number of chromosomes

# Train against random for 5 generations, then against self for 1 generations
trainingSchedule = [("randomPlayer", 250)]


# This is the class for your creature/agent

class MyCreature:

    def __init__(self):
        # You should initialise self.chromosome member variable here (whatever you choose it
        # to be - a list/vector/matrix of numbers - and initialise it with some random
        # values

        # creates a list of randomized floats (between 0 and 2) pertaining to chromosome values
        self.chromosome = [random.uniform(0, 2) for _ in range(nChromosomes)]

    def AgentFunction(self, percepts):
        actions = np.zeros((nActions))  # list of actions, initialized to zero

        # You should implement a model here that translates from 'percepts' to 'actions'
        # through 'self.chromosome'.
        #
        # The 'actions' variable must be returned and it must be a 5-dim numpy vector or a
        # list with 5 numbers.
        #
        # The index of the largest numbers in the 'actions' vector/list is the action taken
        # with the following interpretation:
        # 0 - move left
        # 1 - move up
        # 2 - move right
        # 4 - eat
        #
        # Different 'percepts' values should lead to different 'actions'.  This way the agent
        # reacts differently to different situations.
        #
        # Different 'self.chromosome' should lead to different 'actions'.  This way different
        # agents can exhibit different behaviour.

        # A dictionary of actions associated with the column and row values that a creature can view in that
        # specific action.
        action_dict = {
            "up": [[0, 2], [0, 5]],
            "down": [[3, 5], [0, 5]],
            "left": [[0, 5], [0, 2]],
            "right": [[0, 5], [3, 5]]
        }

        # Selecting action values for each value based on the creatures surroundings in that action
        actions[0] += chooseActions(self, percepts, action_dict["up"])
        actions[1] += chooseActions(self, percepts, action_dict["down"])
        actions[2] += chooseActions(self, percepts, action_dict["left"])
        actions[3] += chooseActions(self, percepts, action_dict["right"])

        # action value for when the creature is on a tile with a strawberry present
        if percepts[2, 2, 1] == 1:
            actions[4] = ((self.chromosome[4] + 1) * self.chromosome[4]) * random.uniform(0.45, 0.75)
        else:
            # if not on food, avoid the action "eat" on an empty tile from randomness
            actions[4] = -999999

        return actions


def chooseActions(self, percepts, action):
    # A function that takes self, the tensor percepts and the dual-tuple of the range of columns and rows that each
    # action can see.
    # Returns total actions, the calculated action value (using percepts) for the given action.

    actions = 0  # action value in iteration
    total_actions = 0  # return value of action value for given action
    creature_map = percepts[:, :, 0]  # 5x5 map with information about creatures and their size
    food_map = percepts[:, :, 1]  # 5x5 map with information about strawberries
    wall_map = percepts[:, :, 2]  # 5x5 map with information about walls
    my_size = creature_map[2, 2]  # current size of monster
    random_weights = random.uniform(0.55, 0.75)  # random weight to allow further training of the agent

    # behavioural dictionary that refers to the 7 chromosomes and their fundamental value in the calculation
    behavioural_dict = {
        "food_driven": (self.chromosome[0]),  # motivation to find food
        "attack_driven": self.chromosome[1],  # motivation to attack enemies
        "wall_avoiding": self.chromosome[2],  # motivation to avoid walls
        "eating_driven": self.chromosome[3],  # motivation to eat food
        "enemy_avoiding": self.chromosome[4],  # motivation to run from bigger enemies
        "relative_distance": self.chromosome[5],  # motivation based on relative distance of creatures/food/walls
        "relative_size": self.chromosome[6],  # motivation based on relative size between enemies
    }
    # iterates through the col and row values provided by the action dictionary
    for x in range(action[0][0], action[0][1]):
        for y in range(action[1][0], action[1][1]):
            # calculates the size difference between my creature and the creature at x,y on the creature map
            size_diff = my_size - abs(percepts[x][y][0])
            # takes euclidean dist between coordinates to included relative value based on how far away objects are
            dist = np.linalg.norm(np.array([x, y]) - np.array([2, 2]))

            # avoid getting a divided by zero case
            if dist == 0:
                dist += 0.3

            # if the food map has food at the observable tile
            if food_map[x][y] > 0:
                # movement towards it is based on food chromosomes, divided by the chance of encountering an enemy
                actions = (behavioural_dict["food_driven"] + (behavioural_dict["eating_driven"] / 2)) \
                          / behavioural_dict["enemy_avoiding"] + ((1 / dist) * behavioural_dict["relative_distance"])

                # if the wall map has a wall at the observable tile
            elif wall_map[x][y] > 0:
                # movement away from the wall based on wall avoiding chromosome, plus the distance away from it
                actions = (behavioural_dict["wall_avoiding"]) + ((dist / 2) *
                                                                 behavioural_dict["relative_distance"])

                # if there is an enemy at the observable tile
            elif creature_map[x][y] < 0:
                if my_size < abs(creature_map[x][y]):  # bigger sized creature
                    # movement away from the enemy based on enemy avoiding chromosome, and the relative size, distance
                    actions = (behavioural_dict["enemy_avoiding"] *
                               (behavioural_dict["relative_size"] * size_diff)) + \
                              ((dist / 2) * behavioural_dict["relative_distance"]) * (
                                          1 / behavioural_dict["attack_driven"])

                elif my_size > abs(creature_map[x][y]):  # smaller sized creature
                    # movement towards enemy based on attack driven chromosome, enemy avoiding and relative size/dist
                    actions = behavioural_dict["attack_driven"] * (
                            behavioural_dict["relative_size"] * size_diff) / behavioural_dict["enemy_avoiding"] \
                              + ((1 / dist) * behavioural_dict["relative_distance"])
            else:
                # return random action if none of these cases are hit
                actions = random.uniform(0, 2)
                # incorporate the random weights
        total_actions += (actions * random_weights)
    return total_actions


def newGeneration(old_population):
    # This function should return a list of 'new_agents' that is of the same length as the
    # list of 'old_agents'.  That is, if previous game was played with N agents, the next game
    # should be played with N agents again.

    # This function should also return average fitness of the old_population
    N = len(old_population)

    # Fitness for all agents
    fitness = np.zeros((N))

    # This loop iterates over your agents in the old population - the purpose of this boiler plate
    # code is to demonstrate how to fetch information from the old_population in order
    # to score fitness of each agent
    for n, creature in enumerate(old_population):
        # creature is an instance of MyCreature that you implemented above, therefore you can access any attributes
        # (such as `self.chromosome').  Additionally, the objects has attributes provided by the
        # game engine:
        #
        # creature.alive - boolean, true if creature is alive at the end of the game
        # creature.turn - turn that the creature lived to (last turn if creature survived the entire game)
        # creature.size - size of the creature
        # creature.strawb_eats - how many strawberries the creature ate
        # creature.enemy_eats - how much energy creature gained from eating enemies
        # creature.squares_visited - how many different squares the creature visited
        # creature.bounces - how many times the creature bounced

        # This fitness functions just considers length of survival.  It's probably not a great fitness
        # function - you might want to use information from other stats as well

        survived = 1
        # rewards creature if it survives the whole round
        if creature.alive:
            survived = 1.5

        # reward creature mainly on eating and gaining size, consideration of squares visited to ensure movement
        # and turns alive to ensure sustainability/survivability
        fitness_function = ((creature.strawb_eats * creature.enemy_eats) * creature.size) + \
                           ((creature.squares_visited / 2) * (creature.turn * survived))

        fitness[n] = (fitness_function / 100)

        # At this point you should sort the agent according to fitness and create new population
    new_population = list()
    for n in range(N):
        # Create new creature
        new_creature = MyCreature()

        # Here you should modify the new_creature's chromosome by selecting two parents (based on their
        # fitness) and crossing their chromosome to overwrite new_creature.chromosome

        # Consider implementing elitism, mutation and various other
        # strategies for producing new creature.

        # Elitism, where 3 top creatures are 'revived' into the new population
        sorted_population_zip = sorted(list(zip(old_population, fitness)), key=lambda y: y[1])
        sorted_population, sorted_fitness = list(zip(*sorted_population_zip))
        elite_lim = 4

        if n < elite_lim:
            new_creature = sorted_population[-1]
        else:
            # after elitism concludes, tournament selection for the parent creatures commences

            # fitness scores and creatures zipped together
            tournament_scores = random.sample(list(zip(old_population, fitness)),
                                              k=15)  # random zipped list of 15 creatures
            sorted_scores = sorted(tournament_scores, key=lambda x: x[1])  # sort tournament creatures by fitness
            tournament_creatures, fitness_scores = list(zip(*sorted_scores))  # unzip sorted tournament creatures
            parent_1 = tournament_creatures[-1]  # parent1 has the best fitness value (sample)

            # repeat tournament to get 2nd parent
            tournament_scores_2 = random.sample(list(zip(old_population, fitness)),
                                                k=15)
            sorted_scores_2 = sorted(tournament_scores_2, key=lambda x: x[1])
            tournament_creatures_2, fitness_scores_2 = list(zip(*sorted_scores_2))

            # to ensure parent1 and parent2 are not the same creature
            if parent_1 == tournament_creatures_2[-1]:
                parent_2 = tournament_creatures_2[-2]  # take second best in this case
            else:
                parent_2 = tournament_creatures_2[-1]

            # mutation: 5% chance for a chromosome to be mutated during crossover
            mutation_lim = 6
            for i in range(nChromosomes):
                x = np.random.randint(100)
                if x < mutation_lim:  # mutation randomizes the chromosome of the child completely for biodiversity
                    new_creature.chromosome[i] = np.random.rand()
                else:  # if not mutated then perform normal random crossover between the two parents
                    new_creature.chromosome[i] = random.choice([parent_1.chromosome[i], parent_2.chromosome[i]])

        # Add the new agent to the new population
        new_population.append(new_creature)

    # At the end you need to compute average fitness and return it along with your new population
    avg_fitness = np.mean(fitness)

    return new_population, avg_fitness
