from game_messages import Message
import tcod
from components.ai import ConfusedMonster


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False,
                        'message': Message('You are fine', 'yellow')})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True,
                        'message': Message('You feel better', 'green')})
    return results


def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if (entity.fighter and
                entity != caster and
                tcod.map_is_in_fov(fov_map, entity.x, entity.y)):
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({'consumed': True,
                        'target': target,
                        'message':
                        Message('Bolt strikes the {0}. Damage is {1}'.format(
                            target.name, damage))})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append({'consumed': False,
                        'target': None,
                        'message': Message('No enemy is close enough.',
                                           'red')})

    return results


def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not tcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message(
                            'You cannot target a tile outside fov', 'yellow')})
        return results

    results.append({'consumed': True,
                    'message': Message(
                        'Fireball burns everything within {0} tiles'.format(
                            radius), 'orange')})

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message(
                'The {0} gets burned for {1} hp'.format(
                    entity.name, damage), 'orange')})
            results.extend(entity.fighter.take_damage(damage))

    return results


def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []
    print('Координаты цели ' + str(target_x) + ' ' + str(target_y))
    if not tcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message(
                            'You cannot target a tile outside fov', 'yellow')})
        return results
    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            print('координаты цели на карте ' + str(entity.x) + ' '
                  + str(entity.y))
            confused_ai = ConfusedMonster(entity.ai, 10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({'consumed': True,
                            'message': Message(
                                '{0} confused'.format(entity.name), 'green')})
            break
    else:
        results.append({'consumed': False,
                        'message': Message(
                            'There is no enemy', 'yellow')})
    return results
