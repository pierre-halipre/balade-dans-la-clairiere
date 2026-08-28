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

from dataclasses import dataclass
from character import Enemy, Obstacle
from common import Way
from tool import Math, Screen, Timer


class Factory:
    @staticmethod
    def create_obstacle(player, obstacles, board):
        columns = []

        for x_cell in range(board.n_x_cell):
            columns.append(x_cell)

        rows = []

        for y_cell in range(board.n_y_cell):
            rows.append(y_cell)

        for obstacle in obstacles:
            if obstacle.is_waited() or obstacle.is_moved():
                columns.remove(obstacle.get_x_cell_min())
                rows.remove(obstacle.get_y_cell_min())
            else:
                pass

        column = Math.rand_list(columns)

        if (
            player.get_x_cell_min() == column and
            player.get_y_cell_min() in rows
        ):
            rows.remove(player.get_y_cell_min())
        else:
            pass

        for obstacle in obstacles:
            if (
                obstacle.is_outed() and
                obstacle.get_x_cell_min() == column and
                obstacle.get_y_cell_min() in rows
            ):
                rows.remove(obstacle.get_y_cell_min())
            else:
                pass

        row = Math.rand_list(rows)

        return Obstacle(column, row)

    @staticmethod
    def create_enemy(to_catch, player, board, score):
        speed = Factory.get_speed(score)
        way = Factory.get_way(player, board)

        x_cell = Factory.get_x_cell(to_catch, way, player, board)
        x = Factory.get_x(x_cell, way, speed, board)

        y_cell = Factory.get_y_cell(to_catch, way, player, board)
        y = Factory.get_y(y_cell, way, speed, board)

        enemy = Enemy(x, y)
        enemy.set_attributes(speed, way, to_catch)

        return enemy

    @staticmethod
    def get_speed(score):
        speed_min = Factory.get_speed_min(score)
        speed_max = Factory.get_speed_max(score)

        return Math.rand_int(speed_min, speed_max)

    @staticmethod
    def get_speed_min(score):
        speed_min = None

        if (
            score.get_level_previous() < score.get_level_limit() and
            score.get_level_previous() > 0
        ):
            speed_limit = Factory.get_speed_limit()
            factor_level = score.get_level_previous() / score.get_level_limit()
            speed_min = Math.ceil(speed_limit * factor_level)
        else:
            speed_min = Factory.get_speed_max(score)

        return speed_min

    @staticmethod
    def get_speed_max(score):
        speed_max = None

        if score.get_level_previous() < score.get_level_limit():
            speed_limit = Factory.get_speed_limit()
            level_previous = score.get_level_previous()
            factor_level = (1 + level_previous) / score.get_level_limit()
            speed_max = Math.ceil(speed_limit * factor_level)
        else:
            speed_max = Factory.get_speed_limit()

        return speed_max

    @staticmethod
    def get_speed_limit():
        return Math.ceil(Screen.size_cell / Timer.get_ticks_motion())

    @staticmethod
    def get_way(player, board):
        ways = []

        x_cell_player = player.get_x_cell_min()
        y_cell_player = player.get_y_cell_min()
        x_cell_middle_board = Math.floor(board.n_x_cell / 2)
        y_cell_middle_board = Math.floor(board.n_y_cell / 2)

        if x_cell_player < x_cell_middle_board:
            ways.append(Ways.left)
        elif x_cell_player > x_cell_middle_board:
            ways.append(Ways.right)
        else:
            ways.append(Ways.left)
            ways.append(Ways.right)

        if y_cell_player < y_cell_middle_board:
            ways.append(Ways.top)
        elif y_cell_player > y_cell_middle_board:
            ways.append(Ways.bottom)
        else:
            ways.append(Ways.top)
            ways.append(Ways.bottom)

        return Math.rand_list(ways)

    @staticmethod
    def get_x_cell(to_catch, way, player, board):
        x_cell = None

        if way.is_vertical():
            x_cells = []
            x_cell_player = player.get_x_cell_min()

            if to_catch:
                for x_cell in range(0, x_cell_player - 1, 1):
                    x_cells.append(x_cell)

                for x_cell in range(x_cell_player + 1, board.n_x_cell, 1):
                    x_cells.append(x_cell)
            else:
                x_cells.append(x_cell_player)

            x_cell = Math.rand_list(x_cells)
        else:
            pass

        return x_cell

    @staticmethod
    def get_x(x_cell, way, speed, board):
        x = None

        if way.is_vertical():
            x = Screen.to_x(x_cell)
        elif way.is_right():
            x = -Screen.to_x(1) + speed
        else:
            x = Screen.to_x(board.n_x_cell) - speed

        return x

    @staticmethod
    def get_y_cell(to_catch, way, player, board):
        y_cell = None

        if way.is_horizontal():
            y_cells = []
            y_cell_player = player.get_y_cell_min()

            if to_catch:
                for y_cell in range(0, y_cell_player - 1, 1):
                    y_cells.append(y_cell)

                for y_cell in range(y_cell_player + 1, board.n_y_cell, 1):
                    y_cells.append(y_cell)
            else:
                y_cells.append(y_cell_player)

            y_cell = Math.rand_list(y_cells)
        else:
            pass

        return y_cell

    @staticmethod
    def get_y(y_cell, way, speed, board):
        y = None

        if way.is_horizontal():
            y = Screen.to_y(y_cell)
        elif way.is_bottom():
            y = -Screen.to_y(1) + speed
        else:
            y = Screen.to_y(board.n_y_cell) - speed

        return y


@dataclass
class Ways:
    right = Way(1, 0)
    left = Way(-1, 0)
    bottom = Way(0, 1)
    top = Way(0, -1)


class Collision:
    @staticmethod
    def has(enemy, other, board):
        has = None

        if Collision.is_same_axis(enemy, other):
            if (
                Collision.is_outside(enemy, other) or
                Collision.is_outed_before(enemy, other, board) or
                (
                    Collision.is_same_direction(enemy, other) and
                    Collision.is_waited_enought(enemy, other, board)
                )
            ):
                has = False
            else:
                has = True
        else:
            if (
                Collision.can_before(enemy, other) or
                Collision.can_after(enemy, other)
            ):
                has = False
            else:
                has = True

        return has

    @staticmethod
    def is_same_axis(enemy, other):
        return (
            (enemy.way.is_horizontal() and other.way.is_horizontal()) or
            (enemy.way.is_vertical() and other.way.is_vertical())
        )

    @staticmethod
    def is_outside(enemy, other):
        return (
            (
                enemy.way.is_horizontal() and
                (
                    enemy.get_y_min() > other.get_y_max() or
                    enemy.get_y_max() < other.get_y_min()
                )
            ) or
            (
                enemy.way.is_vertical() and
                (
                    enemy.get_x_min() > other.get_x_max() or
                    enemy.get_x_max() < other.get_x_min()
                )
            )
        )

    @staticmethod
    def is_outed_before(enemy, other, board):
        other_ticks = Collision.get_ticks_outed(other, board)
        ticks = Collision.get_ticks_waited(enemy)

        return other_ticks <= ticks

    @staticmethod
    def is_same_direction(enemy, other):
        return enemy.way.is_same(other.way)

    @staticmethod
    def is_waited_enought(enemy, other, board):
        ticks_waited = Collision.get_ticks_waited(enemy)
        other_ticks_waited = Collision.get_ticks_waited(other)
        distance_waited = (ticks_waited - other_ticks_waited) * other.speed

        if enemy.way.is_right():
            distance = other.get_x_min() + distance_waited - enemy.get_x_max()
        elif enemy.way.is_left():
            distance = enemy.get_x_min() - other.get_x_max() + distance_waited
        elif enemy.way.is_bottom():
            distance = other.get_y_min() + distance_waited - enemy.get_y_max()
        else:
            distance = enemy.get_y_min() - other.get_y_max() + distance_waited

        if distance <= 0:
            ticks = 0
        elif enemy.speed > other.speed:
            speed = enemy.speed - other.speed
            ticks = Collision.get_ticks_distance(enemy, speed, distance)
        else:
            ticks = Collision.get_ticks_outed(enemy, board)

        other_ticks_outed = Collision.get_ticks_outed(other, board)

        return ticks >= other_ticks_outed

    @staticmethod
    def can_before(enemy, other):
        distance = None

        if enemy.way.is_right():
            distance = other.get_x_min() - enemy.get_x_max()
        elif enemy.way.is_left():
            distance = enemy.get_x_min() - other.get_x_max()
        elif enemy.way.is_bottom():
            distance = other.get_y_min() - enemy.get_y_max()
        else:
            distance = enemy.get_y_min() - other.get_y_max()

        ticks = Collision.get_ticks_distance_enemy(enemy, distance)

        other_distance = None

        if other.way.is_right():
            other_distance = enemy.get_x_max() - other.get_x_min()
        elif other.way.is_left():
            other_distance = other.get_x_max() - enemy.get_x_min()
        elif other.way.is_bottom():
            other_distance = enemy.get_y_max() - other.get_y_min()
        else:
            other_distance = other.get_y_max() - enemy.get_y_min()

        other_ticks = Collision.get_ticks_distance_enemy(other, other_distance)

        return ticks > other_ticks

    @staticmethod
    def can_after(enemy, other):
        distance = None

        if enemy.way.is_right():
            distance = other.get_x_max() - enemy.get_x_min()
        elif enemy.way.is_left():
            distance = enemy.get_x_max() - other.get_x_min()
        elif enemy.way.is_bottom():
            distance = other.get_y_max() - enemy.get_y_min()
        else:
            distance = enemy.get_y_max() - other.get_y_min()

        ticks = Collision.get_ticks_distance_enemy(enemy, distance)

        other_distance = None

        if other.way.is_right():
            other_distance = enemy.get_x_min() - other.get_x_max()
        elif other.way.is_left():
            other_distance = other.get_x_min() - enemy.get_x_max()
        elif other.way.is_bottom():
            other_distance = enemy.get_y_min() - other.get_y_max()
        else:
            other_distance = other.get_y_min() - enemy.get_y_max()

        other_ticks = Collision.get_ticks_distance_enemy(other, other_distance)

        return ticks < other_ticks

    @staticmethod
    def get_ticks_waited(enemy):
        ticks = None

        if enemy.is_waited():
            ticks = enemy.ticks
        else:
            ticks = 0

        return ticks

    @staticmethod
    def get_ticks_outed(enemy, board):
        distance = None

        if enemy.way.is_right():
            distance = board.get_w() - enemy.get_x_min()
        elif enemy.way.is_left():
            distance = enemy.get_x_max() + 1
        elif enemy.way.is_bottom():
            distance = board.get_h() - enemy.get_y_min()
        else:
            distance = enemy.get_y_max() + 1

        return Collision.get_ticks_distance_enemy(enemy, distance)

    @staticmethod
    def get_ticks_distance(enemy, speed, distance):
        ticks_waited = Collision.get_ticks_waited(enemy)

        return Math.ceil(distance / speed) + ticks_waited

    @staticmethod
    def get_ticks_distance_enemy(enemy, distance):
        return Collision.get_ticks_distance(enemy, enemy.speed, distance)
