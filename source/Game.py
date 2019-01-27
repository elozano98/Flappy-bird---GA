import Objects
import random
import Constants as C
import pygame
from pygame.locals import *
import numpy as np

#************************************************************************************************************************************************************************************************
# FUNCTIONS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# GAME FUNCTIONS
def setSettings():
    background = pygame.image.load("img/background.png")
    logo = pygame.image.load("img/logo.png")
    logo = pygame.transform.scale(logo, (C.LOGO_WIDTH, C.LOGO_HEIGHT))
    screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
    general_font = pygame.font.SysFont("Comic Sans MS", C.GENERAL_FONT_SIZE)
    info_font = pygame.font.SysFont("Comic Sans MS", C.INFO_FONT_SIZE)
    return background, logo, screen, general_font, info_font

def createBirds():
    birds = []
    for bird in range(C.POPULATION):
        birds.append(Objects.Bird())
    return birds

def createTunnels():
    tunnels = [Objects.Tunnels(), Objects.Tunnels(), Objects.Tunnels()]
    tunnels[0].set_x(C.BIRD_POS_X + C.TUNNELS_DISTANCE)
    for i in range(1, len(tunnels)):
        tunnels[i].set_x(tunnels[i-1].pos_x + C.TUNNELS_DISTANCE )
    return tunnels

def printGame(screen, general_font, info_font, background, birds, tunnels, population, alive, generation, score, best_score):
    screen.blit(background, (0, 0))

    for bird in birds:
        bird.print(screen)

    for tunnel in tunnels:
        tunnel.print(screen)

    score_label = general_font.render(str(score), 1, (0, 0, 0))
    screen.blit(score_label, (C.SCORE_POS_X, C.SCORE_POS_Y))

    population_label = info_font.render("Population: " + str(population), 1, (0, 0, 0))
    alive_label = info_font.render("Alive: " + str(alive), 1, (0, 0, 0))
    generation_label = info_font.render("Generation :" + str(generation), 1, (0, 0, 0))
    best_score_label = info_font.render("Best score: " + str(best_score), 1, (0, 0, 0))
    screen.blit(population_label, (C.INFO_POS_X, 30))
    screen.blit(alive_label, (C.INFO_POS_X, 60))
    screen.blit(generation_label, (C.INFO_POS_X, 90))
    screen.blit(best_score_label, (C.INFO_POS_X, 120))

def moveTunnels(tunnels, first_tunnel, score, best_score):
    for tunnel in tunnels:
        tunnel.move()
        if tunnel.pos_x + C.TUNNEL_WIDTH < 0:
            tunnels.remove(tunnel)
            tunnels.append(Objects.Tunnels())
            tunnels[-1].set_x(tunnels[-2].pos_x + C.TUNNELS_DISTANCE)

    if first_tunnel.pos_x + C.TUNNEL_WIDTH < C.BIRD_POS_X:
        first_tunnel = tunnels[1]
        score += 1
        if score > best_score:
            best_score = score

    return first_tunnel, score, best_score

def checkGameOver(birds):
    finish = True
    for bird in birds:
        if bird.alive:
            finish = False
    if finish:
        return finish
    else:
        return finish

def treatEvent(event, birds):
    if event.type == QUIT:
        pygame.quit()
        return True

    # if event.type == KEYDOWN:

        # if event.key == K_SPACE:
        #     birds[0].jump()
        #
        # if event.key == K_UP:
        #     birds[1].jump()

    return False

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# GENETIC ALGORITHM FUNCTIONS
def predictJumps(birds):
    for bird in birds:
        if bird.alive:
            hDist = bird.h_distance / C.TUNNELS_DISTANCE
            vDist = bird.v_distance / (C.SCREEN_HEIGHT - C.MIN_TUNNEL_HEIGHT - (C.CROSS_SPACE / 2))
            bot_Dist = (C.SCREEN_HEIGHT - bird.pos_y) / C.SCREEN_HEIGHT
            top_Dist = bird.pos_y / C.SCREEN_HEIGHT

            input = np.asarray([hDist, vDist, bot_Dist, top_Dist])
            input = np.atleast_2d(input)

            output = bird.model.predict(input, 1)[0]
            if output[0] >= 0.5:
                bird.jump()

def crossover(birds, parent_1, parent_2):
    weights_1 = birds[parent_1].model.get_weights()
    weights_2 = birds[parent_2].model.get_weights()
    weights = weights_1.copy()
    for i in range(len(weights)):
        for j in range(len(weights[i])):
            if random.uniform(0, 1) > 0.5:
                weights[i][j] = weights_2[i][j]
    return weights

def mutate(weights):
    for i in range(len(weights)):
        for j in range(len(weights[i])):
            if (random.uniform(0, 1) < C.MUTATION_THRESHOLD):
                print("MUTATE!!!")
                weights[i][j] += random.uniform(-0.5, 0.5)
    return weights

def getFitness(bird):
    return bird.fitness

def getTwoParents():
    parent_1 = random.randint(0, C.SELECTION - 1)
    parent_2 = parent_1
    while parent_1 == parent_2:
        parent_2 = random.randint(0, C.SELECTION - 1)
    return parent_1, parent_2

def geneticUpdates(birds, generation):
    new_weights = []

    birds = sorted(birds, key=getFitness, reverse=True)

    for bird in birds:
        print(bird.fitness)

    # We pass the best ones directly to the next generation
    for i in range(C.SELECTION):
        new_weights.append(birds[i].model.get_weights())

    # We do the crossover until we have a new population with the size desired
    for i in range(C.POPULATION - C.SELECTION):
        parent_1, parent_2 = getTwoParents()
        new_weights.append(crossover(birds, parent_1, parent_2))

    # We introduce some random mutations on the population and prepare the new generations by updating weights of the neural networks
    for i in range(C.POPULATION):
        new_weights[i] = mutate(new_weights[i])
        birds[i].model.set_weights(new_weights[i])

    generation += 1

    return generation

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
# GAME MAIN FUNCTION
def Game():
    close_game = False
    game_over = False
    score = 0
    best_score = 0

    generation = 1
    population = C.POPULATION
    alive = population
    selection = C.SELECTION
    mutation_threshold = C.MUTATION_THRESHOLD

    tunnels = createTunnels()
    first_tunnel = tunnels[0]
    birds = createBirds()

    pygame.init()
    pygame.display.set_caption("Flappy bird - Genetic algorithm implementation")
    background, logo, screen, general_font, info_font = setSettings()

    while not close_game:

        if generation > 1:
            game_over = False
            score = 0
            tunnels = createTunnels()
            first_tunnel = tunnels[0]
            for bird in birds:
                bird.restart()
            alive = population

        while not game_over:
            # We check if the game is over
            game_over = checkGameOver(birds)

            # We print the game
            printGame(screen, general_font, info_font, background, birds, tunnels, population, alive, generation, score, best_score)

            # We move the tunnels
            first_tunnel, score, best_score = moveTunnels(tunnels, first_tunnel, score, best_score)

            # We check for the life of every bird
            for bird in birds:
                alive -= bird.die(first_tunnel)

            # We check if the game is over
            if game_over:
                generation = geneticUpdates(birds, generation)
            else:
                for bird in birds:
                    bird.fall()
                    bird.getDistances(first_tunnel)
                    if bird.alive:
                        bird.fitness += 1
                predictJumps(birds)

            # We check if we want to close the game
            for event in pygame.event.get():
                close_game = treatEvent(event, birds)

            # We update the screen
            pygame.display.update()

#************************************************************************************************************************************************************************************************


if __name__ == '__main__':
    Game()