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
from factory import Collision, Factory
from tool import Math


class Foes(ABC, list):
    @abstractmethod
    def add(self, player, board, settings):
        pass

    def reset(self):
        self.clear()

    def update(self, board, settings):
        for foe in self:
            foe.update(board, settings)

    def fill_hint(self, board):
        for foe in self:
            if not foe.is_outed():
                foe.find_hint()
                foe.fill_hint(board)
            else:
                pass

    def remove(self):
        for i in range(len(self) - 1, -1, -1):
            if self[i].is_disappeared():
                self.pop(i)
            else:
                pass


class Enemies(Foes):
    def __init__(self):
        Foes.__init__(self)

    def add(self, player, board, settings):
        n_to_catch = 0
        n_to_avoid = 0

        for enemy in self:
            if not enemy.is_outed():
                if enemy.to_catch:
                    n_to_catch += 1
                else:
                    n_to_avoid += 1
            else:
                pass

        n_max_to_catch = settings.mode.n_enemies_to_catch
        n_max_to_avoid = settings.mode.n_enemies_to_avoid

        n_to_catch_to_add = n_max_to_catch - n_to_catch
        n_to_avoid_to_add = n_max_to_avoid - n_to_avoid

        if n_to_avoid == n_max_to_avoid:
            n_add = 0

            while n_add < n_to_catch_to_add:
                self.add_enemy(True, player, board, settings)
                n_add += 1
        else:
            pass

        n_add = 0

        while n_add < n_to_avoid_to_add:
            self.add_enemy(False, player, board, settings)
            n_add += 1

    def add_enemy(self, to_catch, player, board, settings):
        enemy = Factory.create_enemy(to_catch, player, board, settings.score)
        collided = False

        for other in self:
            if Collision.has(enemy, other, board):
                collided = True
            else:
                pass

        if not collided:
            self.append(enemy)
        else:
            pass


class Obstacles(Foes):
    def __init__(self):
        Foes.__init__(self)

    def add(self, player, board, settings):
        n = 0

        for obstacle in self:
            if obstacle.is_waited() or obstacle.is_moved():
                n += 1
            else:
                pass

        n_max = None

        if not settings.score.has_points_max():
            n_max = settings.score.get_level()
        else:
            n_max = settings.mode.n_obstacles

        n_add = 0

        while n_add < n_max - n:
            self.append(Factory.create_obstacle(player, self, board))
            n_add += 1

    def has(self, x_cell, y_cell):
        has = False

        for obstacle in self:
            if (
                not obstacle.is_disappeared() and
                obstacle.get_x_cell_min() == x_cell and
                obstacle.get_y_cell_min() == y_cell
            ):
                has = True
            else:
                pass

        return has

    def update_from_level(self, score):
        n_to_out = None

        if (
            score.get_level() > score.get_level_previous() or
            score.has_points_limit()
        ):
            if score.get_level() < score.get_level_limit():
                n_to_out = score.get_level() - score.get_level_max()
            else:
                n_to_out = score.get_level_max()
        else:
            n_to_out = 0

        if n_to_out > 0:
            can_out = []

            for obstacle in self:
                if obstacle.is_moved():
                    can_out.append(obstacle)
                else:
                    pass

            n_out = 0

            while n_out < n_to_out:
                if len(can_out) > 0:
                    obstacle = Math.rand_list(can_out)
                    obstacle.set_outed()
                    obstacle.set_ticks_max()
                    can_out.remove(obstacle)
                else:
                    pass

                n_out += 1
        else:
            pass
