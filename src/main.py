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

from board import Board
from character import Player
from commands import Commands
from foes import Enemies, Obstacles
from resources import Resources
from settings import Settings
from tool import Event, Screen, Timer

Screen.init()
Resources.init()

board = Board()
settings = Settings(board)
player = Player(board)
enemies = Enemies()
obstacles = Obstacles()
commands = Commands(settings)

while Timer.run:
    Event.find()
    Timer.update()

    if Timer.tick():
        if settings.status.is_turn_off(False):
            settings.status.set_turn_on(True)
        elif settings.status.is_transition():
            commands.update_ticks()

            if settings.music.is_on():
                settings.music.fade(commands.get_proportion_ticks())
            else:
                pass

            if commands.need_reset_ticks():
                settings.status.update()
                settings.music.stop()
            else:
                pass
        elif Event.has():
            x_cell = Event.x_cell
            y_cell = Event.y_cell

            if Event.is_hoover():
                if not settings.status.is_transition():
                    commands.buttons.update_hoover(x_cell, y_cell)
                else:
                    pass

                if settings.status.is_play(False):
                    board.cursor.update_cell(x_cell, y_cell, board)
                else:
                    pass
            elif Event.is_click():
                if settings.status.is_play(False):
                    player.set_cell_move_event(x_cell, y_cell, board)
                else:
                    pass

                if not settings.status.is_transition():
                    commands.buttons.set_settings(x_cell, y_cell, settings)
                else:
                    pass
            else:
                pass
        else:
            pass

        if not settings.status.is_transition() and settings.status.need_reset:
            board.reset()
            settings.reset()
            player.reset(board)
            enemies.reset()
            obstacles.reset()

            settings.status.need_reset = False
        elif (
            not settings.status.is_transition() and
            settings.status.need_resume
        ):
            settings.status.need_resume = False
        elif settings.status.is_play(False) or settings.status.is_menu(False):
            board.cursor.update_ticks()

            obstacles.update(board, settings)
            obstacles.remove()

            enemies.update(board, settings)
            enemies.remove()

            if not player.need_update():
                if settings.status.is_menu(False):
                    player.set_cell_move_demo(board)
                else:
                    player.check_cell_move_event(obstacles)

                player.set_cell_move()
            else:
                pass

            player.update(board, settings)

            if not player.need_update():
                if settings.score.lives <= 0:
                    settings.update_end()
                else:
                    enemies.add(player, board, settings)
                    player.catch(enemies, settings)
            else:
                pass

            if player.need_update():
                obstacles.update_from_level(settings.score)
                obstacles.add(player,  board, settings)
                settings.score.update_points_previous()
            else:
                pass

            board.hint.fill(enemies, obstacles, board)
            board.cursor.update(player)

            if commands.buttons.button_mode.need_refresh(settings):
                settings.status.need_refresh = True
            else:
                pass
        else:
            pass

        Event.reset()

        if settings.status.need_transition:
            commands.set_ticks_max()
            commands.buttons.reset_hoover()
            commands.screenplay.update(settings)
            settings.status.need_transition = False
            settings.status.need_refresh = True
        else:
            pass

        if settings.status.need_refresh:
            commands.buttons.update(settings)
            settings.status.need_refresh = False
        else:
            pass

        commands.display_background()
        ratio_reset = commands.get_ratio_reset(settings)
        board.display(player, enemies, obstacles, ratio_reset)
        commands.display_foreground()
        commands.display(settings)
        Screen.display()

        if settings.status.is_turn_off(False):
            Timer.run = False
        else:
            pass

Screen.quit()
