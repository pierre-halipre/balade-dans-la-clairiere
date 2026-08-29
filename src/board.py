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

from common import Counter, Sprite, Element
from const import Const
from resources import Resources
from tool import Pen, Screen


class Board(Element):
    def __init__(self):
        Element.__init__(self, Screen.size_cell, Screen.size_cell, 3, 5)

        self.hint = Hint(self)
        self.cursor = Cursor()

    def reset(self):
        self.hint.reset(self)
        self.cursor.reset()

    def get_n_max_enemies(self):
        return self.n_x_cell - 1

    def get_n_max_obstacles(self):
        return self.n_x_cell

    def trunc_x_cell(self, x_cell):
        x_cell_truncated = None

        if x_cell < 0:
            x_cell_truncated = 0
        elif x_cell > self.n_x_cell - 1:
            x_cell_truncated = self.n_x_cell
        else:
            x_cell_truncated = x_cell

        return x_cell_truncated

    def trunc_y_cell(self, y_cell):
        y_cell_truncated = None

        if y_cell < 0:
            y_cell_truncated = 0
        elif y_cell > self.n_y_cell - 1:
            y_cell_truncated = self.n_y_cell
        else:
            y_cell_truncated = y_cell

        return y_cell_truncated

    def display(self, player, enemies, obstacles, ratio_reset):
        self.display_hint(ratio_reset)
        self.display_cursor(ratio_reset)
        self.display_obstacles(player, obstacles, ratio_reset)
        self.display_enemies(enemies, ratio_reset)
        self.display_player(player, ratio_reset)

    def display_hint(self, ratio_reset):
        for x_cell in range(0, self.n_x_cell, 1):
            for y_cell in range(0, self.n_y_cell, 1):
                surface_hint = Resources.hint[Const.hint.empty]
                Pen.set_alpha(surface_hint, Pen.ratio_greyed_out)
                self.draw_cell_surface(surface_hint, x_cell, y_cell)

                for kind_hint in Const.hint.get_foes():
                    surface_hint = Resources.hint[kind_hint]
                    ratio_hint = self.hint.get(kind_hint, x_cell, y_cell)
                    ratio = ratio_hint * ratio_reset * Pen.ratio_greyed_out
                    Pen.set_alpha(surface_hint, ratio)
                    self.draw_cell_surface(surface_hint, x_cell, y_cell)

    def display_cursor(self, ratio_reset):
        surface = self.cursor.get_surface(ratio_reset)

        if surface is not None:
            x_cell = self.cursor.x_cell
            y_cell = self.cursor.y_cell
            self.draw_cell_surface(surface, x_cell, y_cell)
        else:
            pass

    def display_obstacles(self, player, obstacles, ratio_reset):
        for obstacle in obstacles:
            ratio_update = None

            if obstacle.is_waited():
                ratio_update = 1 - obstacle.get_ratio_ticks()
            elif obstacle.is_outed():
                ratio_update = obstacle.get_ratio_ticks()
            else:
                ratio_update = 1

            surface = obstacle.get_surface(ratio_update * ratio_reset, player)
            self.draw_surface(surface, obstacle.x, obstacle.y)

    def display_enemies(self, enemies, ratio_reset):
        for enemy in enemies:
            ratio_update = None

            if enemy.is_moved():
                ratio_update = 1
            elif enemy.is_caught() or enemy.is_outed():
                ratio_update = enemy.get_ratio_ticks()
            else:
                ratio_update = 1 - enemy.get_ratio_ticks()

            surface = enemy.get_surface(ratio_update * ratio_reset)
            self.draw_surface(surface, enemy.x, enemy.y)

            if enemy.is_caught():
                surface_effect = enemy.get_surface_effect(ratio_reset)
                self.draw_surface(surface_effect, enemy.x, enemy.y)
            else:
                pass

    def display_player(self, player, ratio_reset):
        surface = player.get_surface(ratio_reset)
        self.draw_surface(surface, player.get_x(), player.get_y())

        if ratio_reset != 1:
            surface = Resources.player[Const.way.bottom][0]
            Pen.set_alpha(surface, 1 - ratio_reset)
            x = player.get_x_center(self)
            y = player.get_y_center(self)
            self.draw_surface(surface, x, y)
        else:
            pass


class Hint(dict):
    def __init__(self, board):
        for kind_hint in Const.hint.get_foes():
            self[kind_hint] = []

            for x_cell in range(board.n_x_cell):
                self[kind_hint].append([])

                for y_cell in range(board.n_y_cell):
                    self[kind_hint][x_cell].append([])
                    self[kind_hint][x_cell][y_cell] = 0

    def get(self, kind_hint, x_cell, y_cell):
        return self[kind_hint][x_cell][y_cell]

    def set(self, kind_hint, x_cell, y_cell, ratio_hint):
        if ratio_hint > self.get(kind_hint, x_cell, y_cell):
            self[kind_hint][x_cell][y_cell] = ratio_hint
        else:
            pass

    def reset(self, board):
        for kind_hint in Const.hint.get_foes():
            for x_cell in range(board.n_x_cell):
                for y_cell in range(board.n_y_cell):
                    self[kind_hint][x_cell][y_cell] = 0

    def fill(self, enemies, obstacles, board):
        self.reset(board)
        enemies.fill_hint(board)
        obstacles.fill_hint(board)


class Cursor(Sprite):
    def __init__(self):
        Sprite.__init__(self)

        self.x_cell = None
        self.y_cell = None

        self.set_free()
        self.set_ticks_max()

    def is_free(self):
        return self.is_state(Const.cursor.free)

    def set_free(self):
        self.set_state(Const.cursor.free)

    def is_busy(self):
        return self.is_state(Const.cursor.busy)

    def set_busy(self):
        self.set_state(Const.cursor.busy)

    def reset(self):
        self.unset()
        self.set_free()
        self.set_ticks_max()

    def unset(self):
        self.x_cell = None
        self.y_cell = None

    def has(self):
        return self.x_cell is not None and self.y_cell is not None

    def update_ticks(self):
        Counter.update_ticks(self)

        if self.need_reset_ticks():
            self.set_ticks_max()
        else:
            pass

    def update(self, player):
        if player.need_update():
            self.set_busy()
        else:
            self.set_free()

    def update_cell(self, x_cell, y_cell, board):
        if board.is_inside_cell(x_cell, y_cell):
            self.x_cell = x_cell - board.get_x_cell_min()
            self.y_cell = y_cell - board.get_y_cell_min()
        else:
            self.unset()

    def get_surface(self, ratio_reset):
        surface = None

        if self.has():
            kind = None

            if self.is_busy():
                kind = Const.cursor.busy
            else:
                kind = Const.cursor.free

            surface = self.get_loop(Resources.cursor[kind])
            Pen.set_alpha(surface, ratio_reset * Pen.ratio_greyed_out)
        else:
            pass

        return surface
