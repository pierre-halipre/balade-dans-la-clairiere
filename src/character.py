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

from abc import ABC, abstractmethod
from common import Cell, Element, Sprite
from const import Const
from resources import Resources
from tool import Math, Pen, Screen, Timer


class Character(ABC, Element, Sprite):
    def __init__(self, x, y, n_x_cell, n_y_cell):
        Element.__init__(self, x, y, n_x_cell, n_y_cell)
        Sprite.__init__(self)

    def set_waited(self):
        self.set_state(0)

    def is_waited(self):
        return self.is_state(0)

    def set_moved(self):
        self.set_state(1)

    def is_moved(self):
        return self.is_state(1)

    @abstractmethod
    def need_update(self):
        pass

    @abstractmethod
    def update(self, board, settings):
        pass

    def get_sprite(self, surfaces, is_loop, ratio_reset):
        surface = None

        if is_loop:
            surface = self.get_loop(surfaces)
        else:
            surface = self.get_simple(surfaces)

        Pen.set_alpha(surface, ratio_reset)

        return surface


class Player(Character):
    def __init__(self, board):
        x = self.get_x_center(board)
        y = self.get_y_center(board)
        Character.__init__(self, x, y, 1, 1)

        self.x_previous = self.x
        self.y_previous = self.y
        x_cell = self.get_x_cell_min()
        y_cell = self.get_y_cell_min()
        self.cell_move = Cell(x_cell, y_cell, self)

        self.set_ticks_max()
        self.set_waited()

    def set_won(self):
        self.set_state(2)

    def is_won(self):
        return self.is_state(2)

    def set_lost(self):
        self.set_state(3)

    def is_lost(self):
        return self.is_state(3)

    def set_idled(self):
        self.set_state(4)

    def is_idled(self):
        return self.is_state(4)

    def need_update(self):
        return not self.is_waited()

    def update(self, board, settings):
        self.update_ticks()

        if self.need_reset_ticks():
            if self.need_update():
                self.set_waited()
            else:
                pass

            self.set_ticks_max()
        else:
            pass

    def reset(self, board):
        self.x = self.get_x_center(board)
        self.y = self.get_y_center(board)
        self.x_previous = self.x
        self.y_previous = self.y
        self.cell_move.reset(self)

        self.set_ticks_max()
        self.set_waited()

    def get_x_center(self, board):
        return Screen.to_x((board.n_x_cell - 1) / 2)

    def get_y_center(self, board):
        return Screen.to_y((board.n_y_cell - 1) / 2)

    def get_x(self):
        if self.is_moved():
            ratio_distance = 1 - self.get_proportion_ticks()
            distance = Math.floor((self.x - self.x_previous) * ratio_distance)
            x = self.x_previous + distance
        else:
            x = self.x

        return x

    def get_y(self):
        if self.is_moved():
            ratio_distance = 1 - self.get_proportion_ticks()
            distance = Math.floor((self.y - self.y_previous) * ratio_distance)
            y = self.y_previous + distance
        else:
            y = self.y

        return y

    def set_cell_move_event(self, x_cell, y_cell, board):
        if board.is_inside_cell(x_cell, y_cell) and self.is_waited():
            x_cell_move = x_cell - board.get_x_cell_min()
            y_cell_move = y_cell - board.get_y_cell_min()
            self.cell_move.set(x_cell_move, y_cell_move, self)
        else:
            pass

    def check_cell_move_event(self, obstacles):
        if (
            self.cell_move.distance == 0 or
            obstacles.has(self.cell_move.x_cell, self.cell_move.y_cell)
        ):
            self.cell_move.reset(self)
        else:
            pass

    def get_cells_move_demo(self, board):
        cells_hint = {
            Const.hint.won: [],
            Const.hint.empty: []
        }

        need_move_lost = False

        for x_cell in range(board.n_x_cell):
            for y_cell in range(board.n_y_cell):
                cell = Cell(x_cell, y_cell, self)
                ratio_won = board.hint.get(Const.hint.won, x_cell, y_cell)
                ratio_lost = board.hint.get(Const.hint.lost, x_cell, y_cell)
                ratio_wrong = board.hint.get(Const.hint.wrong, x_cell, y_cell)

                if (
                    ratio_lost != 0 and
                    cell.is_same_x(self) and
                    cell.is_same_y(self)
                ):
                    need_move_lost = True
                elif ratio_lost == 0 and ratio_wrong == 0:
                    if (
                        ratio_won != 0 and
                        (cell.is_same_x(self) or cell.is_same_y(self))
                    ):
                        cells_hint[Const.hint.won].append(cell)
                    else:
                        cells_hint[Const.hint.empty].append(cell)
                else:
                    pass

        cells_move_demo = None

        if len(cells_hint[Const.hint.won]) > 0:
            cells_move_demo = cells_hint[Const.hint.won]
        elif need_move_lost:
            cells_move_demo = cells_hint[Const.hint.empty]
        else:
            pass

        return cells_move_demo

    def set_cell_move_demo(self, board):
        cells = self.get_cells_move_demo(board)

        if cells is not None:
            cell_best = None

            for cell in cells:
                if cell_best is None or cell_best.distance > cell.distance:
                    cell_best = cell
                else:
                    pass

            self.cell_move.set(cell_best.x_cell, cell_best.y_cell, self)
        else:
            pass

    def set_cell_move(self):
        if self.cell_move.distance > 0:
            self.x_previous = self.x
            self.y_previous = self.y
            self.x = Screen.to_x(self.cell_move.x_cell)
            self.y = Screen.to_y(self.cell_move.y_cell)

            self.cell_move.reset(self)
            self.set_moved()
            self.set_ticks_max()
        else:
            pass

    def catch(self, enemies, settings):
        for enemy in enemies:
            if enemy.is_moved() and self.is_inside_element(enemy):
                enemy.set_caught()
                enemy.set_ticks_max()
                enemy.update_score(settings)

                if (
                    (self.is_won() and not enemy.to_catch) or
                    (self.is_lost() and enemy.to_catch) or
                    self.is_idled()
                ):
                    self.set_idled()
                elif enemy.to_catch:
                    self.set_won()
                else:
                    self.set_lost()

                self.set_ticks_max()
            else:
                pass

    def get_surface(self, ratio_reset):
        kind = None
        x_distance = Math.abs(self.x_previous - self.x)
        y_distance = Math.abs(self.y_previous - self.y)

        if x_distance > y_distance:
            if self.x < self.x_previous:
                kind = Const.way.left
            else:
                kind = Const.way.right
        elif self.y < self.y_previous:
            kind = Const.way.top
        else:
            kind = Const.way.bottom

        surfaces = Resources.player[kind]

        return self.get_sprite(surfaces, True, ratio_reset)


class Foe(Character):
    def __init__(self, x, y):
        Character.__init__(self, x, y, 1, 1)

        self.x_min_hint = None
        self.y_min_hint = None

        self.set_ticks_max()
        self.set_waited()

    def set_outed(self):
        self.set_state(2)

    def is_outed(self):
        return self.is_state(2)

    def set_disappeared(self):
        self.set_state(3)

    def is_disappeared(self):
        return self.is_state(3)

    def need_update(self):
        return self.is_waited() or self.is_outed()

    def fill_hint(self, board):
        if self.x_min_hint is not None and self.y_min_hint is not None:
            x_cell_start = board.trunc_x_cell(self.get_x_cell_min_hint())
            x_cell_stop = board.trunc_x_cell(self.get_x_cell_max_hint() + 1)
            y_cell_start = board.trunc_y_cell(self.get_y_cell_min_hint())
            y_cell_stop = board.trunc_y_cell(self.get_y_cell_max_hint() + 1)
            kind_hint = self.get_kind_hint()

            for x_cell in range(x_cell_start, x_cell_stop, 1):
                for y_cell in range(y_cell_start, y_cell_stop, 1):
                    ratio_hint = self.get_ratio_hint(x_cell, y_cell)
                    board.hint.set(kind_hint, x_cell, y_cell, ratio_hint)
        else:
            pass

    def get_x_cell_min_hint(self):
        return Screen.to_x_cell(self.x_min_hint)

    def get_x_cell_max_hint(self):
        return Screen.to_x_cell(self.x_min_hint + self.get_w() - 1)

    def get_y_cell_min_hint(self):
        return Screen.to_y_cell(self.y_min_hint)

    def get_y_cell_max_hint(self):
        return Screen.to_y_cell(self.y_min_hint + self.get_h() - 1)

    @abstractmethod
    def get_kind_hint(self):
        pass

    @abstractmethod
    def get_ratio_hint(self, x_cell, y_cell):
        pass

    @abstractmethod
    def find_hint(self):
        pass


class Enemy(Foe):
    def __init__(self, x, y):
        Foe.__init__(self, x, y)

        self.speed = None
        self.way = None
        self.to_catch = None

    def set_attributes(self, speed, way, to_catch):
        self.speed = speed
        self.way = way
        self.to_catch = to_catch

    def set_caught(self):
        self.set_state(4)

    def is_caught(self):
        return self.is_state(4)

    def need_update(self):
        return Foe.need_update(self) or self.is_caught()

    def update(self, board, settings):
        if self.is_moved():
            self.x += self.way.x * self.speed
            self.y += self.way.y * self.speed

            if self.is_went(board):
                self.set_outed()
                self.set_ticks_max()
                self.update_score(settings)
            else:
                pass
        else:
            pass

        self.update_ticks()

        if self.need_reset_ticks():
            if self.need_update():
                if self.is_caught() or self.is_outed():
                    self.set_disappeared()
                else:
                    self.set_moved()
            else:
                pass

            self.set_ticks_max()
        else:
            pass

    def is_went(self, board):
        return (
            (self.way.is_right() and self.get_x_min() >= board.get_w()) or
            (self.way.is_left() and self.get_x_max() < 0) or
            (self.way.is_bottom() and self.get_y_min() >= board.get_h()) or
            (self.way.is_top() and self.get_y_max() < 0)
        )

    def update_score(self, settings):
        if self.is_caught():
            if self.to_catch:
                settings.score.update_points()
            elif settings.status.is_play(False):
                settings.score.update_lives()
            else:
                pass
        else:
            if self.to_catch:
                if settings.mode.is_easy() and settings.status.is_play(False):
                    settings.score.update_lives()
                else:
                    pass
            else:
                if settings.mode.is_hard():
                    settings.score.update_points()
                else:
                    pass

    def get_kind_hint(self):
        kind_hint = None

        if self.to_catch:
            kind_hint = Const.hint.won
        else:
            kind_hint = Const.hint.lost

        return kind_hint

    def get_ratio_hint(self, x_cell, y_cell):
        ratio_hint_tail = self.get_ratio_hint_tail()
        ratio_hint_head = self.get_ratio_hint_head()

        if self.way.is_right() or self.way.is_bottom():
            ratio_hint_min = ratio_hint_tail
            ratio_hint_max = ratio_hint_head
        else:
            ratio_hint_min = ratio_hint_head
            ratio_hint_max = ratio_hint_tail

        if self.way.is_horizontal():
            cell = x_cell
            cell_min = self.get_x_cell_min_hint() + 1
            cell_max = self.get_x_cell_max_hint()
        else:
            cell = y_cell
            cell_min = self.get_y_cell_min_hint() + 1
            cell_max = self.get_y_cell_max_hint()

        ratio_hint = None

        if cell < cell_min:
            ratio_hint = ratio_hint_min
        elif cell < cell_max:
            ratio_hint = 1
        else:
            ratio_hint = ratio_hint_max

        if self.is_caught():
            ratio_hint *= self.get_proportion_ticks()
        else:
            pass

        return ratio_hint

    def find_hint(self):
        ticks_waited = None

        if self.is_waited():
            ticks_waited = self.ticks
        else:
            ticks_waited = 0

        ticks_caught = (Timer.get_ticks_motion() - ticks_waited) * self.speed
        self.x_min_hint = self.get_x_min() + ticks_caught * self.way.x
        self.y_min_hint = self.get_y_min() + ticks_caught * self.way.y

    def get_ratio_hint_tail(self):
        remaining_hint_tail = None
        remaining_hint = self.get_remaining_hint()
        size_cell = Screen.size_cell

        if self.way.is_right() or self.way.is_bottom():
            remaining_hint_tail = size_cell - remaining_hint % size_cell
        else:
            remaining_hint_inverse = size_cell - 1 + remaining_hint
            remaining_hint_tail = remaining_hint_inverse % size_cell + 1

        return self.to_ratio_hint(remaining_hint_tail)

    def get_ratio_hint_head(self):
        remaining_hint_head = None
        remaining_hint = self.get_remaining_hint()
        size_cell = Screen.size_cell

        if self.way.is_right() or self.way.is_bottom():
            remaining_hint_inverse = size_cell - 1 + remaining_hint
            remaining_hint_head = remaining_hint_inverse % size_cell + 1
        else:
            remaining_hint_head = size_cell - remaining_hint % size_cell

        return self.to_ratio_hint(remaining_hint_head)

    def get_remaining_hint(self):
        remaining_hint = None

        if self.way.is_horizontal():
            remaining_hint = self.x_min_hint
        else:
            remaining_hint = self.y_min_hint

        return remaining_hint

    def to_ratio_hint(self, remaining_hint):
        ticks_remaining_hint = Math.ceil(remaining_hint / self.speed)
        ratio_hint = ticks_remaining_hint / Timer.get_ticks_motion()

        if ratio_hint > 1:
            ratio_hint = 1
        else:
            pass

        return ratio_hint

    def get_surface(self, ratio_reset):
        resources = None

        if self.to_catch:
            resources = Resources.enemy_to_catch
        else:
            resources = Resources.enemy_to_avoid

        kind_way = None

        if self.way.is_right():
            kind_way = Const.way.right
        elif self.way.is_left():
            kind_way = Const.way.left
        elif self.way.is_top():
            kind_way = Const.way.top
        else:
            kind_way = Const.way.bottom

        surfaces = resources[kind_way]

        return self.get_sprite(surfaces, True, ratio_reset)

    def get_surface_effect(self, ratio_reset):
        kind_effect = None

        if self.to_catch:
            kind_effect = Const.effect.to_catch
        else:
            kind_effect = Const.effect.to_avoid

        surface_effect = Resources.effect[kind_effect]

        return self.get_sprite(surface_effect, False, ratio_reset)


class Obstacle(Foe):
    def __init__(self, x_cell, y_cell):
        Foe.__init__(self, Screen.to_x(x_cell), Screen.to_y(y_cell))

    def update(self, board, settings):
        self.update_ticks()

        if self.need_reset_ticks():
            if self.need_update():
                if self.is_waited():
                    self.set_moved()
                else:
                    self.set_disappeared()
            else:
                pass

            self.set_ticks_max()
        else:
            pass

    def get_kind_hint(self):
        return Const.hint.wrong

    def get_ratio_hint(self, x_cell, y_cell):
        ratio_hint = None

        if self.is_outed():
            ratio_hint = self.get_proportion_ticks()
        elif self.is_waited():
            ratio_hint = 1 - self.get_proportion_ticks()
        else:
            ratio_hint = 1

        return ratio_hint

    def find_hint(self):
        self.x_min_hint = self.get_x_min()
        self.y_min_hint = self.get_y_min()

    def get_surface(self, ratio_reset, player):
        kind = None
        x = player.get_x() - self.get_x_min()
        y = player.get_y() - self.get_y_min()

        if x >= 0:
            if Math.abs(x) >= Math.abs(y):
                kind = Const.way.right
            elif y >= 0:
                kind = Const.way.bottom
            else:
                kind = Const.way.top
        else:
            if Math.abs(x) >= Math.abs(y):
                kind = Const.way.left
            elif y >= 0:
                kind = Const.way.bottom
            else:
                kind = Const.way.top

        surfaces = Resources.obstacle[kind]

        return self.get_sprite(surfaces, True, ratio_reset)
