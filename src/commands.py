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
from common import Counter, Element, State
from const import Const
from resources import Resources
from tool import Pen, Screen


class Commands(Counter):
    def __init__(self, settings):
        Counter.__init__(self)

        self.screenplay = Screenplay(settings)
        self.buttons = Buttons(settings)

    def get_ratio_reset(self, settings):
        ratio_reset = None

        if settings.status.need_reset:
            ratio_reset = self.get_ratio_ticks()
        else:
            ratio_reset = 1

        return ratio_reset

    def display(self, settings):
        ratio_transition = self.get_ratio_ticks()

        self.display_greyed_out(ratio_transition, settings)

        self.screenplay.display(ratio_transition, settings)
        self.buttons.display(ratio_transition, settings)

        self.display_blacken(ratio_transition, settings)

    def display_greyed_out(self, ratio_transition, settings):
        ratio_greyed_out = None

        if settings.status.is_transition():
            if self.screenplay.has_texts_current():
                if self.screenplay.has_texts_previous():
                    ratio_greyed_out = 1
                else:
                    ratio_greyed_out = 1 - ratio_transition
            else:
                ratio_greyed_out = ratio_transition
        elif self.screenplay.has_texts_current():
            ratio_greyed_out = 1
        else:
            ratio_greyed_out = 0

        surface_greyed_out = Resources.commands[Const.commands.greyed_out]
        ratio = ratio_greyed_out * Pen.ratio_greyed_out
        Pen.set_alpha(surface_greyed_out, ratio)
        Pen.draw_screen(surface_greyed_out, 0, 0)

    def display_blacken(self, ratio_transition, settings):
        ratio_blacken = None

        if settings.status.is_turn_on(True):
            ratio_blacken = ratio_transition
        elif settings.status.is_turn_off(True):
            ratio_blacken = 1 - ratio_transition
        else:
            ratio_blacken = 0

        surface_blacken = Resources.commands[Const.commands.blacken]
        Pen.set_alpha(surface_blacken, ratio_blacken)
        Pen.draw_screen(surface_blacken, 0, 0)

    def display_foreground(self):
        Pen.draw_screen(Resources.ground[Const.ground.foreground], 0, 0)

    def display_background(self):
        Pen.draw_screen(Resources.ground[Const.ground.background], 0, 0)


class Screenplay(Element):
    def __init__(self, settings):
        Element.__init__(self, 0, 0, 5, 7)

        self.texts_current = []
        self.texts_previous = []

        y_cell = 0

        while y_cell < self.n_y_cell:
            self.texts_current.append(None)
            self.texts_previous.append(None)
            y_cell += 1

        self.update(settings)

    def has_texts(self, texts):
        has = False

        for y_cell in range(self.n_y_cell):
            if texts[y_cell] is not None:
                has = True
            else:
                pass

        return has

    def has_texts_current(self):
        return self.has_texts(self.texts_current)

    def has_texts_previous(self):
        return self.has_texts(self.texts_previous)

    def save_texts(self):
        for y_cell in range(self.n_y_cell):
            self.texts_previous[y_cell] = self.texts_current[y_cell]

    def reset_texts(self):
        for y_cell in range(self.n_y_cell):
            self.texts_current[y_cell] = None

    def display(self, ratio_transition, settings):
        if settings.status.is_transition():
            if self.has_texts_current():
                ratio = 1 - ratio_transition
                self.draw_text(self.texts_current, ratio, settings)
            else:
                pass

            if self.has_texts_previous():
                ratio = ratio_transition
                self.draw_text(self.texts_previous, ratio, settings)
            else:
                pass
        elif self.has_texts_current():
            self.draw_text(self.texts_current, 1, settings)
        else:
            pass

    def draw_text(self, texts, ratio, settings):
        for y_cell in range(self.n_y_cell):
            text = texts[y_cell].get(settings)
            Pen.set_alpha(text, ratio)
            self.draw_cell_surface(text, 0, y_cell)

    def update(self, settings):
        self.save_texts()

        if settings.status.is_play(True):
            self.reset_texts()
        elif settings.status.is_pause(True):
            self.set_texts_pause()
        elif settings.status.is_end(True):
            self.set_texts_end()
        elif (
            settings.status.is_turn_off(True) or
            settings.status.is_menu(True)
        ):
            self.set_texts_menu()
        else:
            pass

    def set_texts_menu(self):
        for y_cell in range(self.n_y_cell):
            kind = None

            if y_cell == 0:
                kind = Const.screenplay.menu_0
            elif y_cell == 1:
                kind = Const.screenplay.menu_1
            elif y_cell == 2:
                kind = Const.screenplay.menu_2
            elif y_cell == 3:
                kind = Const.screenplay.menu_3
            elif y_cell == 4:
                kind = Const.screenplay.menu_4
            elif y_cell == 5:
                kind = Const.screenplay.menu_5
            else:
                kind = Const.screenplay.none

            self.texts_current[y_cell] = Resources.screenplay[kind]

    def set_texts_pause(self):
        for y_cell in range(self.n_y_cell):
            kind = None

            if y_cell == 3:
                kind = Const.screenplay.pause_0
            else:
                kind = Const.screenplay.none

            self.texts_current[y_cell] = Resources.screenplay[kind]

    def set_texts_end(self):
        for y_cell in range(self.n_y_cell):
            kind = None

            if y_cell == 0:
                kind = Const.screenplay.end_0
            elif y_cell == 2:
                kind = Const.screenplay.end_1
            elif y_cell == 3:
                kind = Const.screenplay.score
            elif y_cell == 4:
                kind = Const.screenplay.end_2
            elif y_cell == 5:
                kind = Const.screenplay.mode
            else:
                kind = Const.screenplay.none

            self.texts_current[y_cell] = Resources.screenplay[kind]


class Buttons(Element):
    def __init__(self, settings):
        Element.__init__(self, 0, 7 * Screen.size_cell, 5, 1)

        self.button_mode = ButtonMode(self.x, 0, self.y, settings)
        self.button_control = ButtonControl(self.x, 1, self.y, settings)
        self.button_music = ButtonMusic(self.x, 2, self.y, settings)
        self.button_language = ButtonLanguage(self.x, 3, self.y, settings)
        self.button_menu = ButtonMenu(self.x, 4, self.y, settings)

    def update(self, settings):
        if not settings.status.is_transition():
            self.reset_previous_image()
        else:
            self.save_previous_image()

        self.button_mode.update(settings)
        self.button_control.update(settings)
        self.button_music.update(settings)
        self.button_language.update(settings)
        self.button_menu.update(settings)

    def update_hoover(self, x_cell, y_cell):
        self.button_mode.update_hover(x_cell, y_cell)
        self.button_control.update_hover(x_cell, y_cell)
        self.button_music.update_hover(x_cell, y_cell)
        self.button_language.update_hover(x_cell, y_cell)
        self.button_menu.update_hover(x_cell, y_cell)

    def reset_previous_image(self):
        self.button_mode.reset_previous_image()
        self.button_control.reset_previous_image()
        self.button_music.reset_previous_image()
        self.button_language.reset_previous_image()
        self.button_menu.reset_previous_image()

    def save_previous_image(self):
        self.button_mode.save_previous_image()
        self.button_control.save_previous_image()
        self.button_music.save_previous_image()
        self.button_language.save_previous_image()
        self.button_menu.save_previous_image()

    def reset_hoover(self):
        self.button_mode.set_outside()
        self.button_control.set_outside()
        self.button_music.set_outside()
        self.button_language.set_outside()
        self.button_menu.set_outside()

    def set_settings(self, x_cell, y_cell, settings):
        if self.button_music.is_inside_cell(x_cell, y_cell):
            settings.update_music()
        elif self.button_language.is_inside_cell(x_cell, y_cell):
            settings.update_language()
        elif self.button_mode.is_inside_cell(x_cell, y_cell):
            settings.update_mode()
        elif self.button_control.is_inside_cell(x_cell, y_cell):
            settings.update_control()
        elif self.button_menu.is_inside_cell(x_cell, y_cell):
            settings.update_home()
        else:
            pass

    def display(self, ratio, settings):
        self.button_mode.display(ratio, settings)
        self.button_control.display(ratio, settings)
        self.button_music.display(ratio, settings)
        self.button_language.display(ratio, settings)
        self.button_menu.display(ratio, settings)


class Button(ABC, Element, State):
    def __init__(self, x, x_cell, y, settings):
        Element.__init__(self, x + Screen.to_x(x_cell), y, 1, 1)
        State.__init__(self)

        self.text = None
        self.current_image = None
        self.previous_image = None

        self.update(settings)
        self.set_outside()

    @abstractmethod
    def get_kind(self, settings):
        pass

    def is_outside(self):
        return self.is_state(0)

    def set_outside(self):
        self.set_state(0)

    def is_inside(self):
        return self.is_state(1)

    def set_inside(self):
        self.set_state(1)

    def update(self, settings):
        kind = self.get_kind(settings)
        self.text = Resources.button[kind].text.get(settings)
        self.current_image = Resources.button[kind].image

    def update_hover(self, x_cell, y_cell):
        if self.is_inside_cell(x_cell, y_cell):
            self.set_inside()
        else:
            self.set_outside()

    def reset_previous_image(self):
        self.previous_image = None

    def save_previous_image(self):
        self.previous_image = self.current_image

    def display(self, ratio_transition, settings):
        self.draw_button(Resources.button[Const.button.frame], 1)

        if settings.status.is_transition():
            ratio = None

            if self.current_image == self.previous_image:
                ratio = 1
            else:
                ratio = ratio_transition

            self.draw_button(self.previous_image, ratio)
            self.draw_button(self.current_image, 1 - ratio)
        elif self.is_inside():
            self.draw_button(self.current_image, Pen.ratio_greyed_out)
            self.draw_button(self.text, 1)
        else:
            self.draw_button(self.current_image, 1)

    def draw_button(self, surface, ratio):
        Pen.set_alpha(surface, ratio)
        self.draw_cell_surface(surface, 0, 0)


class ButtonMode(Button):
    def __init__(self, x, x_cell, y, settings):
        Button.__init__(self, x, x_cell, y, settings)

        self.lives = None

    def get_kind(self, settings):
        kind = None

        if (
            settings.status.is_turn_off(True) or
            settings.status.is_turn_on(True) or
            settings.status.is_menu(True) or
            settings.status.is_end(True)
        ):
            if settings.mode.is_easy():
                kind = Const.mode.easy
            elif settings.mode.is_normal():
                kind = Const.mode.normal
            else:
                kind = Const.mode.hard
        elif settings.status.is_play(False):
            if settings.score.lives == 3:
                kind = Const.mode.lives_3
            elif settings.score.lives == 2:
                kind = Const.mode.lives_2
            elif settings.score.lives == 1:
                kind = Const.mode.lives_1
            else:
                kind = Const.mode.lives_0
        else:
            kind = Const.mode.lives_3

        return kind

    def need_refresh(self, settings):
        return (
            settings.status.is_play(False) and
            (self.lives is None or self.lives != settings.score.lives)
        )


class ButtonControl(Button):
    def __init__(self, x, x_cell, y, settings):
        Button.__init__(self, x, x_cell, y, settings)

    def get_kind(self, settings):
        kind = None

        if (
            settings.status.is_turn_off(True) or
            settings.status.is_turn_on(True) or
            settings.status.is_menu(True)
        ):
            kind = Const.control.play
        elif settings.status.is_play(True):
            kind = Const.control.pause
        elif settings.status.is_pause(True):
            kind = Const.control.resume
        else:
            kind = Const.control.replay

        return kind


class ButtonMusic(Button):
    def __init__(self, x, x_cell, y, settings):
        Button.__init__(self, x, x_cell, y, settings)

    def get_kind(self, settings):
        kind = None

        if settings.music.is_on():
            kind = Const.music.on
        else:
            kind = Const.music.off

        return kind


class ButtonLanguage(Button):
    def __init__(self, x, x_cell, y, settings):
        Button.__init__(self, x, x_cell, y, settings)

    def get_kind(self, settings):
        kind = None

        if settings.language.is_english():
            kind = Const.language.english
        else:
            kind = Const.language.french

        return kind


class ButtonMenu(Button):
    def __init__(self, x, x_cell, y, settings):
        Button.__init__(self, x, x_cell, y, settings)

    def get_kind(self, settings):
        kind = None

        if (
            settings.status.is_turn_off(True) or
            settings.status.is_turn_on(True) or
            settings.status.is_menu(True)
        ):
            kind = Const.menu.turn_off
        else:
            kind = Const.menu.home

        return kind
