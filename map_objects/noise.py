from map_objects.tile import Tile
from opensimplex import OpenSimplex
import random
from entity import Entity
from pygame.math import Vector2
import numpy as np


class Generator:
    def __init__(self, width, height, seed, scale, octaves,
                 persistance, lactunarity, offset):
        self.width = width
        self.height = height
        self.seed = seed
        self.scale = scale
        self.octaves = octaves
        self.persistance = persistance
        self.lactunarity = lactunarity
        self.offset = offset
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tiles = self.GenerateNoiseMap()
        return tiles

    def GenerateNoiseMap(self):
        # initialize 2d array for noise map
        noise_map = [[0 for x in range(self.width)]
                     for y in range(self.height)]

        random.seed(self.seed)
        octaveOffset = [0 for o in range(self.octaves)]

        # make an 2d-vector
        for i in range(self.octaves):
            offsetX = random.randrange(-100000, 100000) + self.offset.x
            offsetY = random.randrange(-100000, 100000) + self.offset.y
            octaveOffset[i] = Vector2(offsetX, offsetY)

        half_width = self.width / 2
        half_height = self.height / 2

        max_noise_height = np.amin(noise_map)
        min_noise_height = np.amax(noise_map)

        for y in range(self.height):
            for x in range(self.width):
                amplitude = 1
                frequincy = 1
                noise_height = 0

                # going through octaves to generate more
                for i in range(self.octaves):
                    sampleX = float((x - half_width) /
                                    self.scale * frequincy +
                                    octaveOffset[i].x)
                    sampleY = float((y - half_height) /
                                    self.scale * frequincy +
                                    octaveOffset[i].y)
                    tmp = OpenSimplex(self.seed)
                    noiseValue = tmp.noise2d(sampleX, sampleY) * 2 - 1
                    noise_height += noiseValue * amplitude

                    amplitude *= self.persistance
                    frequincy *= self.lactunarity

                if noise_height > max_noise_height:
                    max_noise_height = noise_height
                elif noise_height < min_noise_height:
                    min_noise_height = noise_height

                noise_map[x][y] = noise_height

        # Normalize noise map to get values fro 0 to 1
        for y in range(self.height):
            for x in range(self.width):
                noise_map[x][y] = float((noise_map[x][y] - min_noise_height) /
                                        (max_noise_height - min_noise_height))

        for y in range(self.height):
            for x in range(self.width):
                if noise_map[x][y] < 0.3:
                    noise_map[x][y] = Tile(True)
                else:
                    noise_map[x][y] = Tile(False)
        # wrapping a noise map
        noise_map = np.pad(noise_map, self.width, mode='wrap')
        return noise_map

    def generate_entities(self, entities, max_mon):
        num_of_mon = random.randint(0, max_mon)
        print('num_of_mon ' + str(num_of_mon))

        for y in range(self.height):
            for x in range(self.width):
                if self.tiles[x][y].blocked:
                    continue
                else:

                    if (num_of_mon > 0
                            and
                            not any([entity for entity in entities
                                     if entity.x == x and entity.y == y])
                            and
                            random.randint(0, 100) < 20):
                        if random.randint(0, 100) < 80:
                            monster = Entity(x, y, 0x1006,
                                             'white', 'Ghost', blocks=True)
                        else:
                            monster = Entity(x, y, 0x1006,
                                             'red', 'Angry Ghost',
                                             blocks=True)
                        entities.append(monster)
                        print("monster added")

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False
