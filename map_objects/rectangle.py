from components.ai import BasicMonster
from components.fighter import Fighter
from components.item import Item
from random import randint
from render_functions import RenderOrder

from entity import Entity
from item_functions import heal


class Room():
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.room_type = 'kitchen'
        self.tile_type = None

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

    def place_entities(self, entities, max_monsters_per_room,
                       max_items_per_room):
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)

        for i in range(number_of_monsters):
            x = randint(self.x1 + 1, self.x2 - 1)
            y = randint(self.y1 + 1, self.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and
                        entity.y == y]):
                if randint(0, 100) < 80:
                    fighter_component = Fighter(hp=1, defense=0, power=1)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'g',
                                     'white', 'Ghost', blocks=True,
                                     render_order=RenderOrder.ACTOR,
                                     fighter=fighter_component,
                                     ai=ai_component)
                else:
                    fighter_component = Fighter(hp=1, defense=1, power=1)
                    ai_component = BasicMonster()
                    monster = Entity(x, y, 'g',
                                     'red', 'Angry Ghost', blocks=True,
                                     render_order=RenderOrder.ACTOR,
                                     fighter=fighter_component,
                                     ai=ai_component)
                entities.append(monster)

        for i in range(number_of_items):
            x = randint(self.x1 + 1, self.x2 - 1)
            y = randint(self.y1 + 1, self.y2 - 1)

            if not any([entity for entity in entities
                        if entity.x == x and entity.y == y]):
                item_component = Item(use_function=heal, amount=4)
                item = Entity(x, y, '!', 'violet', 'Healing Potion',
                              render_order=RenderOrder.ITEM,
                              item=item_component)

                entities.append(item)
