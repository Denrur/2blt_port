class Camera:
    def __init__(self, width, height, x, y):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def move_camera(self, target_x, target_y, game_map):
        # Новые координаты камеры, чтобы цель была по центру экрана
        x = int(target_x - self.width / 2)
        y = int(target_y - self.height / 2)
        # print("Camera width and height " +
        #      str(self.width) + ' ' + str(self.height))
        # print("Camera coordinates " + str(x) + ' ' + str(y))
        # print("Target coordinates " + str(target_x) + ' ' + str(target_y))
        # Проверяем чтобы камера не выходила за границы карты
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > game_map.width - self.width:
            x = game_map.width - self.width

        if y > game_map.height - self.height:
            y = game_map.height - self.height
        # print("Cam_coord " + str(x) + ' ' + str(y))
        # if x != self.x or y != self.y:
        #     return True

        (self.x, self.y) = (x, y)

    def to_camera_coordinates(self, x, y):
        # Конвертируем координаты на карте в координаты на экране
        (x, y) = (x - self.x, y - self.y)
        # if (x < 0 or y < 0 or x >= self.width or y >= self.height):
        #    return(None, None)
        return (x, y)
