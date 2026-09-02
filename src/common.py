"""Copyright 2023 Pierre Halipré

This file is part of Balade dans la clairière.

Balade dans la clairière is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

Balade dans la clairière is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
Balade dans la clairière. If not, see <https://www.gnu.org/licenses/>.
"""

from tool import Math, Pen, Screen, Timer


class State:
    def __init__(self):
        self.value = None

    def set_state(self, value):
        self.value = value

    def is_state(self, value):
        return self.value == value


class Counter:
    def __init__(self):
        self.ticks = None

    def update_ticks(self):
        self.ticks -= 1

    def need_reset_ticks(self):
        return self.ticks == 0

    def set_ticks_max(self):
        self.ticks = Timer.get_ticks_motion()

    def get_ratio_ticks(self):
        return (self.ticks + 1) / (Timer.get_ticks_motion() + 2)

    def get_proportion_ticks(self):
        return self.ticks / Timer.get_ticks_motion()


class Sprite(Counter, State):
    def __init__(self):
        Counter.__init__(self)
        State.__init__(self)

    def get_loop(self, surfaces):
        i_sprite = None
        n_surfaces = len(surfaces)
        n_sprites = (n_surfaces - 1) * 2

        if n_sprites == 0:
            i_sprite = 0
        else:
            proportion_ticks = self.get_proportion_ticks()
            i_surface = Math.round(proportion_ticks * n_sprites) % n_sprites
            track = Math.floor(i_surface / n_surfaces)
            i_sprite = i_surface - track * (i_surface % (n_surfaces - 1)) * 2

        return surfaces[i_sprite]

    def get_simple(self, surfaces):
        proportion_ticks = self.get_proportion_ticks()
        i_sprite = Math.round((1 - proportion_ticks) * (len(surfaces) - 1))

        return surfaces[i_sprite]


class Element:
    def __init__(self, x, y, n_x_cell, n_y_cell):
        self.x = x
        self.y = y
        self.n_x_cell = n_x_cell
        self.n_y_cell = n_y_cell

    def get_w(self):
        return Screen.to_x(self.n_x_cell)

    def get_h(self):
        return Screen.to_y(self.n_y_cell)

    def get_x_min(self):
        return self.x

    def get_x_max(self):
        return self.get_x_min() + self.get_w() - 1

    def get_y_min(self):
        return self.y

    def get_y_max(self):
        return self.get_y_min() + self.get_h() - 1

    def get_x_cell_min(self):
        return Screen.to_x_cell(self.get_x_min())

    def get_x_cell_max(self):
        return Screen.to_x_cell(self.get_x_max())

    def get_y_cell_min(self):
        return Screen.to_y_cell(self.get_y_min())

    def get_y_cell_max(self):
        return Screen.to_y_cell(self.get_y_max())

    def is_inside_cell(self, x_cell, y_cell):
        return (
            self.get_x_cell_min() <= x_cell <= self.get_x_cell_max() and
            self.get_y_cell_min() <= y_cell <= self.get_y_cell_max()
        )

    def is_inside_element(self, element):
        return (
            self.get_x_min() <= element.get_x_max() and
            self.get_x_max() >= element.get_x_min() and
            self.get_y_min() <= element.get_y_max() and
            self.get_y_max() >= element.get_y_min()
        )

    def draw_surface(self, surface, x, y):
        Pen.draw_screen(surface, self.x + x, self.y + y)

    def draw_cell_surface(self, surface, x_cell, y_cell):
        x_cell_screen = self.get_x_cell_min() + x_cell
        y_cell_screen = self.get_y_cell_min() + y_cell
        Pen.draw_cell_screen(surface, x_cell_screen, y_cell_screen)


class Cell:
    def __init__(self, x_cell, y_cell, player):
        self.x_cell = None
        self.y_cell = None
        self.distance = None

        self.set(x_cell, y_cell, player)

    def set(self, x_cell, y_cell, player):
        self.x_cell = x_cell
        self.y_cell = y_cell

        x_distance = Math.abs(self.x_cell - player.get_x_cell_min())
        y_distance = Math.abs(self.y_cell - player.get_y_cell_min())
        self.distance = Math.sqrt(Math.pow(x_distance) + Math.pow(y_distance))

    def reset(self, player):
        self.set(player.get_x_cell_min(), player.get_y_cell_min(), player)

    def is_same_x(self, player):
        return self.x_cell == player.get_x_cell_min()

    def is_same_y(self, player):
        return self.y_cell == player.get_y_cell_min()


class Way:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_left(self):
        return self.x == -1

    def is_right(self):
        return self.x == 1

    def is_horizontal(self):
        return self.is_left() or self.is_right()

    def is_top(self):
        return self.y == -1

    def is_bottom(self):
        return self.y == 1

    def is_vertical(self):
        return self.is_top() or self.is_bottom()

    def is_same(self, way):
        return self.x == way.x and self.y == way.y
