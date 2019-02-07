from game_messages import Message


def heal(*args, **kwargs):
    entity = args[0]
    # print(entity.name)
    amount = kwargs.get('amount')
    # print(amount)
    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False,
                        'message': Message('You are fine', 'yellow')})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True,
                        'message': Message('You feel better', 'green')})
    # print(results)
    return results
