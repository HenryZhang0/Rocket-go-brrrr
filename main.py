import math
import pygame
import random
import time
WIDTH = 1024
HEIGHT = 576
TPS = 100
GAME_SPEED = 60/TPS

# time
time_last_update = time.time()
time_accumulator = 0
time_slice = 1/TPS

# Define Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# initialize pygame and create window
pygame.init()
pygame.mixer.init()  # For sound
screen = pygame.Surface((WIDTH, HEIGHT))
output = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Game")
clock = pygame.time.Clock()  # For syncing the FPS

# sprites
rocket_sprite = pygame.transform.scale(pygame.image.load(
    "rocket.png").convert_alpha(), (30, 40))


class Planet:
    def __init__(self, x, y, radius, field):
        self.x = x
        self.y = y
        self.radius = radius
        self.field = field

    def update(self):
        pass

    def render(self, screen):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, BLUE, (self.x, self.y), self.field, 3)


planets = [Planet(600, 300, 80, 260)]


def distance(x, y, x1, y1):
    return ((x-x1)**2+(y-y1)**2)**(1/2)


def unit_vector(vector):
    dist = distance(vector[0], vector[1], 0, 0)
    return [vector[0]/dist, vector[1]/dist]


class Rocket:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.vect = speed
        self.rect = pygame.Rect(x, y, speed[0], speed[1])
        self.gravitying = list()
        self.launch = False

        self.force = [0, 0]
        self.trail = [[self.x, self.y]] * 15
        self.trail_counter = 0

    def update(self):
        if not self.launch:
            return

        self.vect[0] += self.force[0]
        self.vect[1] += self.force[1]

        decel = 1
        self.vect[0] *= decel
        self.vect[1] *= decel

        self.x += self.vect[0]
        self.y += self.vect[1]
        self.rect = pygame.Rect(self.x, self.y, 20, 20)

        if self.trail_counter % 40 == 0:
            self.trail.append([self.x, self.y])
            self.trail.pop(0)
        self.trail_counter += 1

    def gravitize(self, plans):
        self.force = [0, 0]  # resets all forces
        self.gravitying = list()
        for planet in plans:
            dist = distance(self.x, self.y, planet.x, planet.y)
            if not dist <= planet.field:
                continue

            gravity = 0.014

            dist = distance(planet.x, planet.y, self.y, self.y)

            gravity_dir = unit_vector([planet.x - self.x, planet.y - self.y])
            print(gravity_dir)
            friction = -0.000

            unit_velocity = distance(0, 0, self.vect[0], self.vect[1])

            friction_vect = [self.vect[0] * friction, self.vect[1] * friction]

            self.force[0] += gravity * gravity_dir[0] + friction_vect[0]
            self.force[1] += gravity * gravity_dir[1] + friction_vect[1]

            self.gravitying.append(gravity_dir)

    def render(self, screen):
        #pygame.draw.rect(screen, WHITE, self.rect)

        for dot in self.trail:
            pygame.draw.circle(screen, WHITE, (dot[0], dot[1]), 3)

        angle = - math.degrees(math.acos((1 * self.vect[0] + 0 * self.y) / (
            1 * (self.vect[0]**2 + self.vect[1]**2)**(1/2))))

        #angle = 0

        if self.vect[1] < 0:
            angle *= -1
        angle -= 90
        rocket = pygame.transform.rotate(rocket_sprite, angle)

        screen.blit(rocket, (self.x - int(rocket.get_width() / 2),
                    self.y - int(rocket.get_height() / 2)))

        pygame.draw.line(screen, BLUE, (self.x, self.y),
                         (self.x + self.vect[0]*50, self.y + self.vect[1]*50), 4)
        for g in self.gravitying:
            pygame.draw.line(screen, RED, (self.x, self.y), (self.x +
                             g[0] * 100, self.y + g[1]*100), 3)
        #print(self.x, self.y, (self.x + self.vect[0]*20, self.y + self.vect[1]*20))


# rockets = [Rocket(600, 500, [0, 0]),Rocket(600, 500, [2, 0]), Rocket(600, 500, [1, -1])]
test_rockets = []# [Rocket(600, 500, [1, -1])]
rocket = Rocket(100,300,[2,0])

class Launchpad:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0

    def rotate(self, dir):
        self.angle += dir*0.1
        dist = distance(rocket.vect[0], rocket.vect[1], 0, 0)
        rocket.vect[0] = math.cos(self.angle) * dist
        rocket.vect[1] = math.sin(self.angle) * dist

    def render(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), 20, 3)

launchpad = Launchpad(100,300)

class Home:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 30, 30)

    def render(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)


home = Home(950, 250)

SCROLL = (0, 0)
BLOCK_OFFSET = (100, 600)


def render():
    global main_block
    screen.fill(BLACK)
    for planet in planets:
        planet.render(screen)  # 3

    launchpad.render(screen)

    rocket.render(screen)


    for test_rocket in test_rockets:
        test_rocket.render(screen)
    home.render(screen)
    output.blit(screen, (0, 0))


def update(splice):
    global rockets
    for planet in planets:
        planet.update()

    for test_rocket in test_rockets:
        test_rocket.update()
        test_rocket.gravitize(planets)

    rocket.update()
    rocket.gravitize(planets)


    if rocket.rect.colliderect(home.rect):
        print("win!")
        pygame.time.wait(3000)


# Game loop
running = True
start_game = False
clicked_up = True


def takeoff():
    rocket.launch = True
    print(rocket.launch)
    for test_rocket in test_rockets:
        test_rocket.launch = True


def main():
    global running, time_last_update, time_accumulator, time_slice, start_game, clicked_up
    while running:
        # gets all the events which have occured till now and keeps tab of them.
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and clicked_up:
                planets.append(Planet(event.pos[0], event.pos[1], 20, 150))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    start_game = True
                    keyed_up = False
                    takeoff()
                if event.key == pygame.K_UP:
                    launchpad.rotate(1)
                

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    keyed_up = True

        delta_time = time.time() - time_last_update
        time_last_update += delta_time
        time_accumulator += delta_time

        while time_accumulator > time_slice:
            # print(time_accumulator)
            update(1)
            time_accumulator -= time_slice

        render()  # 3 Draw/render
        pygame.display.flip()  # Done after drawing everything to the screen

    # end of main loop


if __name__ == '__main__':
    main()

pygame.quit()
