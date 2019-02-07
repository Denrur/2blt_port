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
from map_objects.game_map import GameMap
from render_functions import render_all, RenderOrder
# import pdb


def main():

    screen_width = blt.state(blt.TK_WIDTH)
    screen_height = blt.state(blt.TK_HEIGHT)
    map_width = int(blt.get("ini.Game.map_width"))
    map_height = int(blt.get("ini.Game.map_height"))

    depth = int(blt.get("ini.Game.depth"))
    min_size = int(blt.get("ini.Game.min_size"))
    full_rooms = {'False': False,
                  'True': True}[blt.get("ini.Game.full_rooms")]

    fov_algorithm = int(blt.get("ini.Game.fov_algorithm"))
    fov_light_walls = {'False': False,
                       'True': True}[blt.get("ini.Game.fov_light_walls")]
    fov_radius = int(blt.get("ini.Game.fov_radius"))

    max_monsters_per_room = int(blt.get("ini.Game.max_monsters_per_room"))
    max_items_per_room = 2

    camera_width = int(blt.get("ini.Game.camera_width"))
    camera_height = int(blt.get("ini.Game.camera_height"))
    (camera_x, camera_y) = (0, 0)

    fighter_component = Fighter(hp=30, defense=0, power=5)
    inventory_component = Inventory(26)
    player = Entity(0, 0, '@', 'white', 'You', blocks=True,
                    render_order=RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component)

    entities = [player]
    game_map = GameMap(map_width, map_height, full_rooms)
    game_map.make_bsp(depth, min_size, player, entities,
                      max_monsters_per_room, max_items_per_room)

    fov_recompute = True
    fov_map = initialize_fov(game_map)

    panel_height = screen_height - camera_height - 3
    panel_y = camera_height + 2  # screen_height - panel_height + 1

    sidebar_width = screen_width - camera_width - 2
    sidebar_x = camera_width + 2  # screen_width - sidebar_width + 1

    message_x = 2
    message_width = camera_width
    message_height = panel_height - 2

    message_log = MessageLog(message_x, message_width, message_height)

    camera = Camera(camera_width, camera_height, camera_x, camera_y)

    blt.color("white")
    blt.composition(True)

    game_state = GameStates.PLAYERS_TURN
    previous_game_state = game_state

    while True:
        mouse_x = blt.state(blt.TK_MOUSE_X)
        mouse_y = blt.state(blt.TK_MOUSE_Y)
        mouse = (mouse_x, mouse_y)
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y,
                          fov_radius, fov_light_walls, fov_algorithm)

        render_all(entities, player, game_map, camera,
                   fov_map, fov_recompute,
                   message_log,
                   sidebar_x, sidebar_width,
                   panel_y, panel_height,
                   screen_width, screen_height,
                   mouse, game_state)

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
                player_turn_results.extend(player.inventory.use(item))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')

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

        if exit:
            # print('exit')
            if game_state in (GameStates.SHOW_INVENTORY,
                              GameStates.DROP_INVENTORY):
                game_state = previous_game_state
                # print(game_state)
            else:
                return False


if __name__ == '__main__':
    blt.open()
    main()
    blt.close()
