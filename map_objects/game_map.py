from map_objects.rectangle import Room
from map_objects.tile import Tile
from random import choice
import functools
import tcod


class GameMap:
    def __init__(self, width, height, full_rooms):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.full_rooms = full_rooms

    def initialize_tiles(self):
        tiles = [[Tile(True)
                  for y in range(self.height)]
                 for x in range(self.width)]

        return tiles

    def make_bsp(self, depth, min_size, player, entities,
                 max_monsters_per_room, max_items_per_room):
        global rooms
        rooms = []

        bsp = tcod.bsp_new_with_size(0, 0, self.width, self.height)

        tcod.bsp_split_recursive(bsp, 0, depth, min_size + 1, min_size + 1,
                                 1.5, 1.5)

        tcod.bsp_traverse_inverted_level_order(bsp,
                                               functools.partial(
                                                   self.traverse_node,
                                                   entities=entities,
                                                   mmpr=max_monsters_per_room,
                                                   mipr=max_items_per_room,
                                                   min_size=min_size))

        player_room = choice(rooms)
        rooms.remove(player_room)
        player_room_x, player_room_y = player_room.center()
        player.x = player_room_x
        player.y = player_room_y

        # player.x = int(player_room[0])
        # player.y = int(player_room[1])

    def traverse_node(self, node, _, entities, mmpr, mipr, min_size):
        # global rooms
        if tcod.bsp_is_leaf(node):
            minx = node.x + 1
            maxx = node.x + node.w - 1
            miny = node.y + 1
            maxy = node.y + node.h - 1
            if maxx == self.width - 1:
                maxx -= 1
            if maxy == self.height - 1:
                maxy -= 1

            if self.full_rooms is False:
                minx = tcod.random_get_int(None, minx,
                                           maxx - min_size + 1)
                miny = tcod.random_get_int(None, miny,
                                           maxy - min_size + 1)
                maxx = tcod.random_get_int(None, minx + min_size - 2,
                                           maxx)
                maxy = tcod.random_get_int(None, miny + min_size - 2,
                                           maxy)

            node.x = minx
            node.y = miny
            node.w = maxx - minx + 1
            node.h = maxy - miny + 1

            new_room = Room(node.x, node.y, node.w, node.h)

            for x in range(minx, maxx + 1):
                for y in range(miny, maxy + 1):
                    self.tiles[x][y].blocked = False
                    self.tiles[x][y].block_sight = False

            new_room.place_entities(entities, mmpr, mipr)
            # new_room = Rect(node.x, node.y, node.w, node.h)

            rooms.append(new_room)
            # print(new_room.room_type)
            # rooms.append(((minx + maxx) / 2, (miny + maxy) / 2))

        else:
            left = tcod.bsp_left(node)
            right = tcod.bsp_right(node)
            node.x = min(left.x, right.x)
            node.y = min(left.y, right.y)
            node.w = max(left.x + left.w, right.x + right.w) - node.x
            node.h = max(left.y + left.h, right.y + right.h) - node.y

            if node.horizontal:
                if (left.x + left.w - 1 < right.x or
                        right.x + right.w - 1 < left.x):
                    x1 = tcod.random_get_int(None, left.x,
                                             left.x + left.w - 1)
                    x2 = tcod.random_get_int(None,
                                             right.x,
                                             right.x + right.w - 1)
                    y = tcod.random_get_int(None, left.y + left.h, right.y)
                    self.vline_up(x1, y - 1)
                    self.hline(x1, y, x2)
                    self.vline_down(x2, y + 1)
                else:
                    minx = max(left.x, right.x)
                    maxx = min(left.x + left.w - 1, right.x + right.w - 1)
                    x = tcod.random_get_int(None, minx, maxx)

                    while x > self.width - 1:
                        x -= 1
                    self.vline_down(x, right.y)
                    self.vline_up(x, right.y - 1)

            else:
                if (left.y + left.h - 1 < right.y or
                        right.y + right.h - 1 < left.y):
                    y1 = tcod.random_get_int(None, left.y,
                                             left.y + left.h - 1)
                    y2 = tcod.random_get_int(None, right.y,
                                             right.y + right.h - 1)
                    x = tcod.random_get_int(None, left.x + left.w, right.x)
                    self.hline_left(x - 1, y1)
                    self.vline(x, y1, y2)
                    self.hline_right(x + 1, y2)
                else:
                    miny = max(left.y, right.y)
                    maxy = min(left.y + left.h - 1, right.y + right.h - 1)
                    y = tcod.random_get_int(None, miny, maxy)

                    while y > self.height - 1:
                        y -= 1

                    self.hline_left(right.x - 1, y)
                    self.hline_right(right.x, y)

        return True

    def vline(self, x, y1, y2):
        if y1 > y2:
            y1, y2 = y2, y1

        for y in range(y1, y2 + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def vline_up(self, x, y):
        while y >= 0 and self.tiles[x][y].blocked is True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            y -= 1

    def vline_down(self, x, y):
        while y < self.height and self.tiles[x][y].blocked is True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            y += 1

    def hline(self, x1, y, x2):
        if x1 > x2:
            x1, x2 = x2, x1

        for x in range(x1, x2 + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def hline_left(self, x, y):
        while x >= 0 and self.tiles[x][y].blocked is True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            x -= 1

    def hline_right(self, x, y):
        while x < self.width and self.tiles[x][y].blocked is True:
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False
            x += 1

    # def make_map(self, max_rooms, room_min_size, room_max_size, map_width,
    #             map_height, player):
    #    rooms = []
    #    num_rooms = 0

    #    for r in range(max_rooms):
    #        w = randint(room_min_size, room_max_size)
    #        h = randint(room_min_size, room_max_size)
    #        x = randint(0, map_width - w - 1)
    #        y = randint(0, map_height - h - 1)

    #        new_room = Rect(x, y, w, h)

    #        for other_room in rooms:
    #            if new_room.intersect(other_room):
    #                break
    #        else:
    #            self.create_room(new_room)

    #            (new_x, new_y) = new_room.center()

    #            if num_rooms == 0:
    #                player.x = int(new_x)
    #                player.y = int(new_y)
    #            else:
    #                (prev_x, prev_y) = rooms[num_rooms - 1].center()

    #                if randint(0, 1) == 1:
    #                    self.create_h_tunnel(prev_x, new_x, prev_y)
    #                    self.create_v_tunnel(prev_y, new_y, new_x)
    #                else:
    #                    self.create_v_tunnel(prev_y, new_y, prev_x)
    #                    self.create_h_tunnel(prev_x, new_x, new_y)

    #            rooms.append(new_room)
    #            num_rooms += 1
    #
    # def create_room(self, room):
    #    for x in range(room.x1 + 1, room.x2):
    #        for y in range(room.y1 + 1, room.y2):
    #            self.tiles[x][y].blocked = False
    #            self.tiles[x][y].block_sight = False

    # def create_h_tunnel(self, x1, x2, y):
    #    for x in range(min(x1, x2), max(x1, x2) + 1):
    #        self.tiles[x][y].blocked = False
    #        self.tiles[x][y].block_sight = False

    # def create_v_tunnel(self, y1, y2, x):
    #    for y in range(min(y1, y2), max(y1, y2) + 1):
    #        self.tiles[x][y].blocked = False
    #        self.tiles[x][y].block_sight = False

    # def place_entities(self, rooms, entities, max_monster_per_room):
    #    number_of_monsters = randint(0, max_monster_per_room)

    #    for i in range(number_of_monsters):
    #        x =
    #        number_of_monsters = randint()

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False
