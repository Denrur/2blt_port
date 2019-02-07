from bearlibterminal import terminal as blt
from components.fighter import Fighter
from camera import Camera
from components.inventory import Inventory
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message, MessageLog
from game_states import GameStates
from input_handlers import handle_keys
from loader_functions.initialize_new_game import get_constants
from map_objects.game_map import GameMap

from render_functions import render_all, RenderOrder
# import pdb


def main():
    constants = get_constants()

    (camera_x, camera_y) = (0, 0)

    fighter_component = Fighter(hp=30, defense=0, power=5)
    inventory_component = Inventory(26)
    player = Entity(0, 0, '@', 'white', 'You', blocks=True,
                    render_order=RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component)

    entities = [player]
    game_map = GameMap(constants['map_width'], constants['map_height'],
                       constants['full_rooms'])
    game_map.make_bsp(constants['depth'], constants['min_size'],
                      player, entities,
                      constants['max_monsters_per_room'],
                      constants['max_items_per_room'])

    fov_recompute = True
    fov_map = initialize_fov(game_map)

    message_log = MessageLog(constants['message_x'],
                             constants['message_width'],
                             constants['message_height'])

    camera = Camera(constants['camera_width'],
                    constants['camera_height'],
                    camera_x, camera_y)

    blt.color("white")
    blt.composition(True)

    game_state = GameStates.PLAYERS_TURN
    previous_game_state = game_state

    targeting_item = None

    while True:
        # pdb.set_trace()
        mouse_x = blt.state(blt.TK_MOUSE_X)
        mouse_y = blt.state(blt.TK_MOUSE_Y)
        mouse = (mouse_x, mouse_y)
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y,
                          constants['fov_radius'],
                          constants['fov_light_walls'],
                          constants['fov_algorithm'])

        render_all(entities, player, game_map, camera,
                   fov_map, fov_recompute,
                   message_log,
                   constants['sidebar_x'], constants['sidebar_width'],
                   constants['panel_y'], constants['panel_height'],
                   constants['screen_width'], constants['screen_height'],
                   game_state, mouse)

        fov_recompute = False
        blt.refresh()
        blt.clear()
        action = handle_keys(game_state)

        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        exit = action.get('exit')

        left_click = action.get('left_click')
        right_click = action.get('right_click')

        if blt.TK_MOUSE_X or blt.TK_MOUSE_Y:
            fov_recompute = True

        player_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities,
                                                           destination_x,
                                                           destination_y)
                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)

                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if (entity.item and
                        entity.x == player.x and
                        entity.y == player.y):
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break

            else:
                message_log.add_message(Message(
                    'There is nothing to pick up.', 'yellow'))

        if show_inventory:
            previous_game_state = game_state
            # print(previous_game_state)
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if (inventory_index is not None and
                previous_game_state != GameStates.PLAYER_DEAD and
                inventory_index < len(player.inventory.items)):
            item = player.inventory.items[inventory_index]
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(
                    player.inventory.use(item,
                                         entities=entities,
                                         fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if game_state == GameStates.TARGETING:
            if left_click:
                print(left_click)
                (target_x, target_y) = camera.to_map_coordinates(left_click[0],
                                                                 left_click[1])
                print(target_x, target_y)
                item_use_results = player.inventory.use(targeting_item,
                                                        entities=entities,
                                                        fov_map=fov_map,
                                                        target_x=target_x,
                                                        target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if exit:
            if game_state in (GameStates.SHOW_INVENTORY,
                              GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                return False

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))

            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN

        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map,
                                                             game_map,
                                                             entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    blt.open()
    main()
    blt.close()
