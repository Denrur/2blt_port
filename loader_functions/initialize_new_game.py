from bearlibterminal import terminal as blt


def get_constants():

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

    panel_height = screen_height - camera_height - 3
    panel_y = camera_height + 2

    sidebar_width = screen_width - camera_width - 2
    sidebar_x = camera_width + 2

    message_x = 2
    message_width = camera_width
    message_height = panel_height - 2

    constants = {
        'screen_width': screen_width,
        'screen_height': screen_height,
        'map_width': map_width,
        'map_height': map_height,
        'depth': depth,
        'min_size': min_size,
        'full_rooms': full_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room,
        'camera_width': camera_width,
        'camera_height': camera_height,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'sidebar_width': sidebar_width,
        'sidebar_x': sidebar_x,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height
    }

    return constants
