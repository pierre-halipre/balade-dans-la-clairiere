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

from common import State
from const import Const
from resources import Resources
from tool import Math


class Settings:
    def __init__(self, board):
        self.score = Score(board)
        self.status = Status()
        self.mode = Mode(board)
        self.music = Music()
        self.language = Language()

        self.score.reset()
        self.status.set_turn_off(False)
        self.mode.set_normal()
        self.music.set_on()
        self.music.change(Const.music.theme)
        self.language.set_french()

    def update_end(self):
        self.status.set_end(True)
        self.music.change(None)

    def update_mode(self):
        if self.status.is_menu(False) or self.status.is_end(False):
            self.mode.update()
            self.status.need_refresh = True
        else:
            pass

    def update_control(self):
        if (
            self.status.is_menu(False) or
            self.status.is_pause(False) or
            self.status.is_end(False)
        ):
            self.status.set_play(True)
            self.music.change(Const.music.melody)
        elif self.status.is_play(False):
            self.status.set_pause(True)
            self.music.change(None)
        else:
            pass

    def update_music(self):
        self.music.update()
        self.status.need_refresh = True

    def update_language(self):
        self.language.update()
        self.status.need_refresh = True

    def update_home(self):
        if self.status.is_menu(False):
            self.status.set_turn_off(True)
            self.music.change(None)
        elif (
            self.status.is_play(False) or
            self.status.is_pause(False) or
            self.status.is_end(False)
        ):
            self.status.set_menu(True)
            self.music.change(Const.music.theme)
        else:
            pass


class Score(State):
    def __init__(self, board):
        State.__init__(self)
        self.lives = None
        self.points = None
        self.points_previous = None

        self.points_level = board.n_y_cell
        self.points_max = board.n_x_cell * board.n_y_cell
        self.points_limit = 999

    def reset(self):
        self.lives = 3
        self.points = 0
        self.points_previous = 0

    def has_points_max(self):
        return self.points > self.points_max

    def has_points_limit(self):
        return self.points == self.points_limit

    def get_level(self):
        return Math.floor(self.points / self.points_level)

    def get_level_previous(self):
        return Math.floor(self.points_previous / self.points_level)

    def get_level_max(self):
        return Math.floor(self.points_max / self.points_level)

    def get_level_limit(self):
        return 2 * self.get_level_max()

    def update_lives(self):
        self.lives -= 1

    def update_points_previous(self):
        self.points_previous = self.points

    def update_points(self):
        if self.points < self.points_limit:
            self.points += 1
        else:
            pass


class Status(State):
    def __init__(self):
        State.__init__(self)

        self.need_reset = False
        self.need_resume = False
        self.need_transition = False
        self.need_refresh = False
        self.state_transition = None

    def could_state(self, value, transition):
        return (
            (State.is_state(self, value) and not self.is_transition()) or
            (self.state_transition == value and transition)
        )

    def set_state(self, value):
        self.state_transition = None
        State.set_state(self, value)

    def is_transition(self):
        return self.state_transition is not None

    def set_transition(self, value):
        self.need_transition = True
        self.state_transition = value

    def is_turn_off(self, transition):
        return self.could_state(0, transition)

    def set_turn_off(self, transition):
        if transition:
            self.set_transition(0)
        else:
            self.set_state(0)

    def is_turn_on(self, transition):
        return self.could_state(1, transition)

    def set_turn_on(self, transition):
        if transition:
            self.need_reset = True
            self.set_transition(1)
        else:
            self.set_menu(False)

    def is_menu(self, transition):
        return self.could_state(2, transition)

    def set_menu(self, transition):
        if transition:
            self.need_reset = True
            self.set_transition(2)
        else:
            self.set_state(2)

    def is_play(self, transition):
        return self.could_state(3, transition)

    def set_play(self, transition):
        if transition:
            if self.is_menu(False) or self.is_end(False):
                self.need_reset = True
            else:
                self.need_resume = True

            self.set_transition(3)
        else:
            self.set_state(3)

    def is_pause(self, transition):
        return self.could_state(4, transition)

    def set_pause(self, transition):
        if transition:
            self.set_transition(4)
        else:
            self.set_state(4)

    def is_end(self, transition):
        return self.could_state(5, transition)

    def set_end(self, transition):
        if transition:
            self.set_transition(5)
        else:
            self.set_state(5)

    def update(self):
        if self.is_turn_off(True):
            self.set_turn_off(False)
        elif self.is_turn_on(True):
            self.set_turn_on(False)
        elif self.is_play(True):
            self.set_play(False)
        elif self.is_pause(True):
            self.set_pause(False)
        elif self.is_menu(True):
            self.set_menu(False)
        else:
            self.set_end(False)


class Mode(State):
    def __init__(self, board):
        State.__init__(self)
        self.n_max_enemies = board.n_x_cell - 1
        self.n_min_enemies = 1
        self.n_enemies_to_avoid = None
        self.n_enemies_to_catch = None
        self.n_obstacles = board.n_x_cell

    def is_easy(self):
        return self.is_state(Const.mode.easy)

    def set_easy(self):
        self.set_state(Const.mode.easy)
        self.n_enemies_to_avoid = 0
        self.n_enemies_to_catch = self.n_max_enemies + self.n_min_enemies

    def is_normal(self):
        return self.is_state(Const.mode.normal)

    def set_normal(self):
        self.set_state(Const.mode.normal)
        self.n_enemies_to_avoid = self.n_max_enemies
        self.n_enemies_to_catch = self.n_min_enemies

    def is_hard(self):
        return self.is_state(Const.mode.hard)

    def set_hard(self):
        self.set_state(Const.mode.hard)
        self.n_enemies_to_avoid = self.n_max_enemies + self.n_min_enemies
        self.n_enemies_to_catch = 0

    def update(self):
        if self.is_normal():
            self.set_hard()
        elif self.is_hard():
            self.set_easy()
        else:
            self.set_normal()


class Music(State):
    def __init__(self):
        State.__init__(self)

        self.current = None
        self.previous = None

    def is_on(self):
        return self.is_state(Const.music.on)

    def set_on(self):
        self.set_state(Const.music.on)

    def is_off(self):
        return self.is_state(Const.music.off)

    def set_off(self):
        self.set_state(Const.music.off)

    def update(self):
        if self.is_on():
            self.set_off()
            self.volume(0)
        else:
            self.set_on()
            self.volume(1)

    def stop(self):
        if self.previous is not None:
            self.previous.stop()
        else:
            pass

    def volume(self, proportion):
        if self.current is not None:
            self.current.set_volume(proportion)
        else:
            pass

    def fade(self, proportion):
        if self.previous is not None:
            self.previous.set_volume(proportion)
        else:
            pass

        self.volume(1 - proportion)

    def change(self, kind):
        self.previous = self.current

        if kind is not None:
            self.current = Resources.music[kind]
            self.current.set_volume(0)
            self.current.play(-1)
        else:
            self.current = None


class Language(State):
    def __init__(self):
        State.__init__(self)

    def is_french(self):
        return self.is_state(Const.language.french)

    def set_french(self):
        self.set_state(Const.language.french)

    def is_english(self):
        return self.is_state(Const.language.english)

    def set_english(self):
        self.set_state(Const.language.english)

    def update(self):
        if self.is_french():
            self.set_english()
        else:
            self.set_french()
