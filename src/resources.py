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
from dataclasses import dataclass
from unicodedata import combining, normalize
from const import Const
from customization import Customization
from tool import Color, Loading, Math, Pen, Screen, Sound


class Resources:
    music = {}
    hint = {}
    cursor = {}
    ground = {}
    player = {}
    enemy = {}
    effect = {}
    obstacle = {}
    commands = {}
    font = {}
    screenplay = {}
    button = {}

    @staticmethod
    def init():
        icon = Pen.load(Const.path.caption_icon)
        caption = Const.path.caption_text
        Screen.set_icon_and_caption(icon, caption)
        Loading.display(0, 14)

        Customization.fill_infos()
        Loading.display(1, 14)

        Resources.music = Resources.init_music()
        Loading.display(2, 14)

        Resources.hint = Resources.init_hint()
        Loading.display(3, 14)

        Resources.cursor = Resources.init_cursor()
        Loading.display(4, 14)

        Resources.ground = Resources.init_ground()
        Loading.display(5, 14)

        Resources.player = Resources.init_player()
        Loading.display(6, 14)

        Resources.enemy_to_catch = Resources.init_enemy_to_catch()
        Loading.display(7, 14)

        Resources.enemy_to_avoid = Resources.init_enemy_to_avoid()
        Loading.display(8, 14)

        Resources.obstacle = Resources.init_obstacle()
        Loading.display(9, 14)

        Resources.effect = Resources.init_effect()
        Loading.display(10, 14)

        Resources.commands = Resources.init_commands()
        Loading.display(11, 14)

        Resources.font = Resources.init_font()
        Loading.display(12, 14)

        Resources.screenplay = Resources.init_screenplay()
        Loading.display(13, 14)

        Resources.button = Resources.init_button()
        Loading.display(14, 14)

    @staticmethod
    def init_music():
        path_theme = Math.path(Const.path.music_theme)
        path_melody = Math.path(Const.path.music_melody)

        return {
            Const.music.theme: Sound.create(path_theme),
            Const.music.melody: Sound.create(path_melody)
        }

    @staticmethod
    def init_hint():
        def create_hint(color):
            size = 32
            surface = Pen.create(size, size)
            area = Pen.create_area(0, 0, size, size)
            surface = Pen.create_rectangle(size, size, area, color)

            return Pen.scale_cell(surface)

        return {
            Const.hint.won: create_hint(Color.green),
            Const.hint.lost: create_hint(Color.red),
            Const.hint.wrong: create_hint(Color.blue),
            Const.hint.empty: create_hint(Color.grey)
        }

    @staticmethod
    def init_cursor():
        def create_cursor(color):
            size_max = 32
            surfaces = []

            for size in range(Math.floor(size_max / 2)):
                w_cursor = size_max - 2 * size
                h_cursor = size_max - 2 * size
                area = Pen.create_area(size, size, w_cursor, h_cursor)
                surface = Pen.create_ellipse(size_max, size_max, area, color)
                surfaces.append(Pen.scale_cell(surface))

            return surfaces

        return {
            Const.cursor.free: create_cursor(Color.green),
            Const.cursor.busy: create_cursor(Color.red)
        }

    @staticmethod
    def init_ground():
        def draw_border(condition, surface, sprite_sheet, w, h):
            if condition:
                Pen.draw_surface(surface, sprite_sheet, w, h)
            else:
                pass

        def create_border(top_left, top_right, bottom_left, bottom_right):
            sprite_sheet = Pen.load(Const.path.image_ground_border)
            w = Math.floor(sprite_sheet.get_width() / 2)
            h = Math.floor(sprite_sheet.get_height() / 2)
            surface = Pen.create(w, h)
            draw_border(top_left, surface, sprite_sheet, -w, -h)
            draw_border(top_right, surface, sprite_sheet, 0, -h)
            draw_border(bottom_left, surface, sprite_sheet, -w, 0)
            draw_border(bottom_right, surface, sprite_sheet, 0, 0)

            return Pen.scale_cell(surface)

        def get_kind_border(x_cell, y_cell):
            kind_border = None

            if x_cell == 0:
                if y_cell == 0:
                    kind_border = Const.ground.top_left
                elif y_cell == 6:
                    kind_border = Const.ground.bottom_left
                else:
                    kind_border = Const.ground.left
            elif x_cell == 4:
                if y_cell == 0:
                    kind_border = Const.ground.top_right
                elif y_cell == 6:
                    kind_border = Const.ground.bottom_right
                else:
                    kind_border = Const.ground.right
            elif y_cell == 0:
                kind_border = Const.ground.top
            elif y_cell == 6:
                kind_border = Const.ground.bottom
            elif y_cell == 7:
                kind_border = Const.ground.full
            else:
                pass

            return kind_border

        surface_center = Pen.load(Const.path.image_ground_center)
        surface_center = Pen.scale_cell(surface_center)
        surfaces_border = {
            Const.ground.top: create_border(True, True, False, False),
            Const.ground.bottom: create_border(False, False, True, True),
            Const.ground.left: create_border(True, False, True, False),
            Const.ground.right: create_border(False, True, False, True),
            Const.ground.top_left: create_border(True, True, True, False),
            Const.ground.top_right: create_border(True, True, False, True),
            Const.ground.bottom_left: create_border(True, False, True, True),
            Const.ground.bottom_right: create_border(False, True, True, True),
            Const.ground.full: create_border(True, True, True, True)
        }

        background = Pen.create(5 * Screen.size_cell, 8 * Screen.size_cell)
        foreground = Pen.create(5 * Screen.size_cell, 8 * Screen.size_cell)

        for x_cell in range(0, 5, 1):
            for y_cell in range(0, 8, 1):
                Pen.draw_cell(background, surface_center, x_cell, y_cell)

                kind_border = get_kind_border(x_cell, y_cell)

                if kind_border is not None:
                    surface = surfaces_border[kind_border]
                    Pen.draw_cell(foreground, surface, x_cell, y_cell)
                else:
                    pass

        return {
            Const.ground.background: background,
            Const.ground.foreground: foreground
        }

    @staticmethod
    def create_player():
        sprite_sheet = Pen.load(Const.path.image_player)

        def create_player(sprite_sheet, j):
            surfaces = []

            for i in range(0, 3, 1):
                sprite = Pen.get_sprite(sprite_sheet, i, j, 3, 4)
                sprite = Pen.scale_cell(sprite)
                surfaces.append(sprite)

            return surfaces

        return {
            Const.way.top: create_player(sprite_sheet, 3),
            Const.way.bottom: create_player(sprite_sheet, 0),
            Const.way.left: create_player(sprite_sheet, 1),
            Const.way.right: create_player(sprite_sheet, 2)
        }

    @staticmethod
    def init_player():
        surfaces = None

        if Customization.player.path is not None:
            path = Customization.player.path
            surfaces = Resources.create_character_custom(path)
        else:
            surfaces = Resources.create_player()

        return surfaces

    @staticmethod
    def create_foe(path_image):
        sprite_sheet = Pen.load(path_image)

        def create_foe_way(sprite_sheet, j):
            surfaces = []
            w = Screen.size_cell
            h = Screen.size_cell

            for i in range(0, 3, 1):
                surface = Pen.create(w, h)
                sprite = Pen.get_sprite(sprite_sheet, i, j, 3, 4)
                w_sprite = Math.floor(2 * w / 3)
                h_sprite = Math.floor(h / 2)
                sprite = Pen.scale(sprite, w_sprite, h_sprite)
                x_sprite = Math.floor(w / 6)
                y_sprite = Math.floor(h / 4)
                Pen.draw_surface(surface, sprite, x_sprite, y_sprite)
                surfaces.append(surface)

            return surfaces

        return {
            Const.way.top: create_foe_way(sprite_sheet, 3),
            Const.way.bottom: create_foe_way(sprite_sheet, 0),
            Const.way.left: create_foe_way(sprite_sheet, 1),
            Const.way.right: create_foe_way(sprite_sheet, 2)
        }

    @staticmethod
    def init_enemy_to_catch():
        surfaces = None

        if Customization.enemy_to_catch.path is not None:
            path = Customization.enemy_to_catch.path
            surfaces = Resources.create_character_custom(path)
        else:
            surfaces = Resources.create_foe(Const.path.image_enemy_to_catch)

        return surfaces

    @staticmethod
    def init_enemy_to_avoid():
        surfaces = None

        if Customization.enemy_to_avoid.path is not None:
            path = Customization.enemy_to_avoid.path
            surfaces = Resources.create_character_custom(path)
        else:
            surfaces = Resources.create_foe(Const.path.image_enemy_to_avoid)

        return surfaces

    @staticmethod
    def init_obstacle():
        surfaces = None

        if Customization.obstacle.path is not None:
            path = Customization.obstacle.path
            surfaces = Resources.create_character_custom(path)
        else:
            surfaces = Resources.create_foe(Const.path.image_obstacle)

        return surfaces

    @staticmethod
    def create_character_custom(path):
        surface = Pen.scale_cell(Pen.load(path))
        surfaces = {}

        for way in Const.way.get_all():
            surfaces[way] = [surface]

        return surfaces

    @staticmethod
    def init_effect():
        surfaces = {}
        sprite_sheet = Pen.load(Const.path.image_effect)

        for effect in Const.effect.get_all():
            surfaces[effect] = []
            j = None

            if effect == Const.effect.to_catch:
                j = 0
            else:
                j = 1

            for i in range(0, 10, 1):
                surface = Pen.get_sprite(sprite_sheet, i, j, 10, 2)
                surfaces[effect].append(Pen.scale_cell(surface))

        return surfaces

    @staticmethod
    def init_commands():
        w = 5 * Screen.size_cell
        h = 8 * Screen.size_cell

        surface_greyed_out = Pen.create(w, h)
        Pen.draw_color(surface_greyed_out, Color.white)

        surface_blacken = Pen.create(w, h)
        Pen.draw_color(surface_blacken, Color.black)

        return {
            Const.commands.greyed_out: surface_greyed_out,
            Const.commands.blacken: surface_blacken
        }

    @staticmethod
    def init_font():
        font = {
            Const.font.small: None,
            Const.font.medium: None,
            Const.font.big: None
        }

        kinds_size = (Const.font.small, Const.font.medium, Const.font.big)
        size_cell = Screen.size_cell
        sizes = {
            Const.font.small: (size_cell, size_cell, 9 * " "),
            Const.font.medium: (5 * size_cell, size_cell, 23 * " "),
            Const.font.big: (5 * size_cell, size_cell, 13 * " ")
        }
        created = False
        size_font = 1

        while not created:
            font_current = Pen.get_font(size_font)

            for kind_size in kinds_size:
                size = font_current.size(sizes[kind_size][2])

                if (
                    font[kind_size] is None and
                    (
                        size[0] > sizes[kind_size][0] or
                        size[1] > sizes[kind_size][1]
                    )
                ):
                    font[kind_size] = Pen.get_font(size_font - 1)
                else:
                    pass

            created = True

            for kind_size in kinds_size:
                if font[kind_size] is None:
                    created = False
                else:
                    pass

            size_font += 1

        return font

    @staticmethod
    def init_screenplay():
        surfaces = {}

        def create_screenplay(surfaces, size, kind):
            w = 5 * Screen.size_cell
            h = Screen.size_cell
            surfaces[kind] = TextScreenplay(w, h, size, kind)

        create_screenplay(surfaces, Const.font.big, Const.screenplay.menu_0)
        create_screenplay(surfaces, Const.font.big, Const.screenplay.menu_1)
        create_screenplay(surfaces, Const.font.medium, Const.screenplay.menu_2)
        create_screenplay(surfaces, Const.font.medium, Const.screenplay.menu_3)
        create_screenplay(surfaces, Const.font.medium, Const.screenplay.menu_4)
        create_screenplay(surfaces, Const.font.medium, Const.screenplay.menu_5)

        create_screenplay(surfaces, Const.font.big, Const.screenplay.pause_0)

        create_screenplay(surfaces, Const.font.big, Const.screenplay.end_0)
        create_screenplay(surfaces, Const.font.big, Const.screenplay.end_1)
        create_screenplay(surfaces, Const.font.big, Const.screenplay.end_2)

        surfaces[Const.screenplay.mode] = TextMode()
        surfaces[Const.screenplay.score] = TextScore()

        create_screenplay(surfaces, Const.font.medium, Const.screenplay.none)

        return surfaces

    @staticmethod
    def init_button():
        surfaces = {}

        surface = Pen.load(Const.path.image_button_frame)
        surfaces[Const.button.frame] = Pen.scale_cell(surface)

        def create_button(surfaces, i, kind):
            surfaces[kind] = Button(i, kind)

        create_button(surfaces, 2, Const.mode.easy)
        create_button(surfaces, 0, Const.mode.normal)
        create_button(surfaces, 1, Const.mode.hard)
        create_button(surfaces, 3, Const.mode.lives_0)
        create_button(surfaces, 4, Const.mode.lives_1)
        create_button(surfaces, 5, Const.mode.lives_2)
        create_button(surfaces, 6, Const.mode.lives_3)

        create_button(surfaces, 7, Const.control.play)
        create_button(surfaces, 8, Const.control.pause)
        create_button(surfaces, 9, Const.control.resume)
        create_button(surfaces, 10, Const.control.replay)

        create_button(surfaces, 11, Const.music.on)
        create_button(surfaces, 12, Const.music.off)

        create_button(surfaces, 13, Const.language.french)
        create_button(surfaces, 14, Const.language.english)

        create_button(surfaces, 15, Const.menu.turn_off)
        create_button(surfaces, 16, Const.menu.home)

        return surfaces

    @staticmethod
    def get_text(kind, language):
        if (
            kind == Const.character.player and
            Customization.player.name is not None
        ):
            text = Customization.player.name
        elif (
            kind == Const.character.enemy_to_catch and
            Customization.enemy_to_catch.name is not None
        ):
            text = Customization.enemy_to_catch.name
        elif (
            kind == Const.character.enemy_to_avoid and
            Customization.enemy_to_avoid.name is not None
        ):
            text = Customization.enemy_to_avoid.name
        elif (
            kind == Const.character.obstacle and
            Customization.obstacle.name is not None
        ):
            text = Customization.obstacle.name
        else:
            text = Const.text[kind][language]

        text = Resources.to_text_ascii(text)

        kind_character = None

        if kind == Const.screenplay.menu_2:
            kind_character = Const.character.player
        elif kind == Const.screenplay.menu_3:
            kind_character = Const.character.enemy_to_catch
        elif kind == Const.screenplay.menu_4:
            kind_character = Const.character.enemy_to_avoid
        elif kind == Const.screenplay.menu_5:
            kind_character = Const.character.obstacle
        else:
            pass

        if kind_character is not None:
            text_character = Resources.get_text(kind_character, language)
            text = text.format(text_character)
        else:
            pass

        return text

    @staticmethod
    def to_text_ascii(text):
        text_raw = normalize("NFKD", text)
        text_ascii = ""

        for letter in text_raw:
            if combining(letter) == 0:
                text_ascii += letter
            else:
                pass

        return text_ascii


@dataclass
class Button:
    def __init__(self, i, kind):
        w = Screen.size_cell
        h = Screen.size_cell
        surface = Pen.create(w, h)

        sprite_sheet = Pen.load(Const.path.image_button_icon)
        sprite = Pen.get_sprite(sprite_sheet, i, 0, 17, 1)
        sprite = Pen.scale(sprite, Math.floor(w / 2), Math.floor(h / 2))

        x_sprite = Math.floor((surface.get_width() - sprite.get_width()) / 2)
        y_sprite = Math.floor((surface.get_height() - sprite.get_height()) / 2)
        Pen.draw_surface(surface, sprite, x_sprite, y_sprite)

        self.image = surface
        self.text = TextButton(w, h, Const.font.small, kind)


@dataclass
class TextSurface(ABC, dict):
    @abstractmethod
    def get(self, settings):
        pass

    def get_text(self, kind, language):
        return Resources.get_text(kind, language)


class TextLocal(TextSurface):
    def __init__(self, w, h, size, kind):
        font = Resources.font[size]

        text = self.get_text(kind, Const.language.english)
        self[Const.language.english] = Pen.create_text(w, h, text, font)

        text = self.get_text(kind, Const.language.french)
        self[Const.language.french] = Pen.create_text(w, h, text, font)

    def get(self, settings):
        return self[settings.language.value]


class TextScreenplay(TextLocal):
    def get_text(self, kind, language):
        text = TextLocal.get_text(self, kind, language)

        if kind != Const.screenplay.menu_1:
            text = text.capitalize()
        else:
            pass

        return text


class TextButton(TextLocal):
    def get_text(self, kind, language):
        return TextLocal.get_text(self, kind, language).upper()


class TextMode(TextSurface):
    def __init__(self):
        def create_text_local(kind):
            w = 5 * Screen.size_cell
            h = Screen.size_cell

            return TextScreenplay(w, h, Const.font.big, kind)

        self[Const.mode.easy] = create_text_local(Const.mode.easy)
        self[Const.mode.normal] = create_text_local(Const.mode.normal)
        self[Const.mode.hard] = create_text_local(Const.mode.hard)

    def get(self, settings):
        return self[settings.mode.value_game][settings.language.value]


class TextScore(TextSurface):
    def __init__(self):
        self.w = 5 * Screen.size_cell
        self.h = Screen.size_cell

    def get(self, settings):
        points = settings.score.points
        score = str("0") * (3 - len(str(points))) + str(points)
        font = Resources.font[Const.font.big]

        return Pen.create_text(self.w, self.h, score, font)
