import tcod
from bearlibterminal import terminal as blt
from enum import Enum
from game_states import GameStates
import textwrap


class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


def get_names_under_mouse(mouse, entities, fov_map, camera):
    x = mouse[0] - 1
    y = mouse[1] - 1

    names = [entity.name for entity in entities
             if camera.to_camera_coordinates(entity.x, entity.y) == (x, y) and
             tcod.map_is_in_fov(fov_map, entity.x, entity.y)]

    names = ', '.join(names)

    return names.capitalize()


def render_bar(x, y, width, name, value, max_val, foreground, background):
    bar_width = int(float(value) / max_val * width)

    last_bg = blt.state(blt.TK_BKCOLOR)
    blt.bkcolor(background)
    blt.clear_area(x, y, width, 1)
    blt.bkcolor(last_bg)

    if bar_width > 0:
        last_bg = blt.state(blt.TK_BKCOLOR)
        blt.bkcolor(foreground)
        blt.clear_area(x, y, bar_width, 1)
        blt.bkcolor(last_bg)

    text = name + ':' + str(value) + '/' + str(max_val)
    x_centered = x + (width - len(text)) // 2
    blt.color('white')
    blt.puts(x_centered, y, '[font=small]' + text)


def create_window(x, y, w, h, title=None):
    last_bg = blt.state(blt.TK_BKCOLOR)
    blt.bkcolor(blt.color_from_argb(200, 0, 0, 0))
    blt.clear_area(x, y, w + 1, h + 1)
    blt.bkcolor(last_bg)

    border = '[U+250C]' + '[U+2500]'*(w - 2) + '[U+2510]'
    blt.puts(x, y, '[font=small]' + border)
    for i in range(1, h):
        blt.puts(x, y + i, '[font=small][U+2502]')
        blt.puts(x + w - 1, y + i, '[font=small][U+2502]')
    border = '[U+2514]' + '[U+2500]'*(w - 2) + '[U+2518]'
    blt.puts(x, y + h, '[font=small]' + border)

    if title is not None:
        leng = len(title)
        offset = (w + 2 - leng) // 2
        blt.clear_area(x + offset, y, leng, 1)
        blt.puts(x + offset, y, '[font=small]' + title)


def menu(header, options, width, screen_width, screen_height, title=None):
    if len(options) > 26:
        raise ValueError('Cannot have a menu with more than 26 options.')

    menu_x = int((screen_width - width) / 2)

    header_wrapped = textwrap.wrap(header, width)
    header_height = len(header_wrapped)

    menu_h = int(header_height + 1 + 26)
    menu_y = int((screen_height - menu_h) / 2)

    create_window(menu_x, menu_y, width, menu_h, title)

    for i, line in enumerate(header_wrapped):
        blt.puts(menu_x + 1, menu_y + 1 + i, header_wrapped[i])

    y = menu_y + header_height + 1
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ')' + option_text
        blt.puts(menu_x + 1, y, text)
        y += 1
        letter_index += 1
    blt.refresh()


def inventory_menu(header, inventory, inventory_width,
                   screen_width, screen_height):

    if len(inventory.items) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory.items]
    menu(header, options, inventory_width, screen_width, screen_height,
         title='INVENTORY')


def render_all(entities, player, game_map, camera,
               fov_map, fov_recompute,
               message_log,
               sidebar_x, sidebar_width,
               panel_y, panel_height,
               screen_width, screen_height,
               game_state, mouse):
    camera.move_camera(player.x, player.y, game_map)
    if fov_recompute:
        create_window(0, 0, camera.width + 2, camera.height + 1)
        create_window(0, panel_y, camera.width + 2,
                      panel_height, 'MESSAGE LOG')
        create_window(sidebar_x, 0, sidebar_width, screen_height - 1,
                      'PLAYER STATS')
        names = get_names_under_mouse(mouse, entities, fov_map, camera)

        for y in range(camera.height):
            for x in range(camera.width):
                map_x = camera.x + x
                map_y = camera.y + y
                visible = tcod.map_is_in_fov(fov_map, map_x, map_y)
                wall = game_map.tiles[map_x][map_y].block_sight
                # print("map coord " + str(map_x) + ' ' + str(map_y))
                #
                if visible:
                    if wall:
                        blt.puts(x + 1, y + 1,
                                 '[font][color=light_wall][U+0023]')
                    else:
                        blt.puts(x + 1, y + 1,
                                 '[font][color=light_ground][U+002E]')
                    game_map.tiles[map_x][map_y].explored = True
                elif game_map.tiles[map_x][map_y].explored:
                    if wall:
                        blt.puts(x + 1, y + 1,
                                 '[font][color=dark_wall][U+0023]')
                    else:
                        blt.puts(x + 1, y + 1,
                                 '[font][color=dark_ground][U+002E]')

    # entities.append(entities.pop(0))

    entities_in_render_order = sorted(entities,
                                      key=lambda x: x.render_order.value)

    for entity in entities_in_render_order:
        draw_entity(entity, camera, fov_map)
    # for y in range(camera.height):
    #     blt.puts(camera.width, y, '[color=white][U+2551]')
    # for x in range(camera.width):
    #     blt.puts(x, camera.height, '[color=white][U+2550]')
    # blt.puts(camera.width, camera.height, '[color=white][U+2569]')
    render_bar(sidebar_x + 1, 1, sidebar_width - 2, 'HP', player.fighter.hp,
               player.fighter.max_hp,
               'dark red', 'darkest red')
    y = 1
    for message in message_log.messages:
        # print(message.text)
        blt.color(message.color)
        blt.puts(message_log.x, panel_y + y, '[font=small]' + message.text)
        y += 1
    blt.color('white')
    if names:
        blt.clear_area(mouse[0] + 1, mouse[1], len(names), 1)
        blt.puts(mouse[0] + 1, mouse[1], names)

    if game_state in (GameStates.SHOW_INVENTORY,
                      GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it'
        else:
            inventory_title = 'Press the key next to an item to drop it'

        inventory_menu(inventory_title,
                       player.inventory,
                       50, screen_width, screen_height)


def draw_entity(entity, camera, fov_map):
    x, y = camera.to_camera_coordinates(entity.x, entity.y)
    blt.color(entity.color)
    if x in range(camera.width) and y in range(camera.height):
        if tcod.map_is_in_fov(fov_map, entity.x, entity.y):
            blt.puts(x + 1, y + 1, entity.char)
