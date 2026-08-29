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


@dataclass
class Id:
    n = 0

    @staticmethod
    def get():
        Id.n += 1

        return Id.n - 1


@dataclass
class Path:
    folder = "res"
    caption_text = "Balade dans la clairière"
    caption_icon = "icon.ico"
    image_title = "title.png"
    image_copyright = "copyright.png"
    image_ground_border = "ground_border.png"
    image_ground_center = "ground_center.png"
    image_player = "witch.png"
    image_enemy_to_catch = "butterfly.png"
    image_enemy_to_avoid = "crow.png"
    image_effect = "effect.png"
    image_obstacle = "ladybug.png"
    image_button_frame = "button_frame.png"
    image_button_icon = "button_icon.png"
    music_theme = "theme.mp3"
    music_melody = "melody.mp3"
    font = "font.otf"


@dataclass
class Hint:
    won = Id.get()
    lost = Id.get()
    wrong = Id.get()
    empty = Id.get()

    @staticmethod
    def get_foes():
        return (Hint.won, Hint.lost, Hint.wrong)


@dataclass
class Cursor:
    free = Id.get()
    busy = Id.get()


@dataclass
class Ground:
    top = Id.get()
    bottom = Id.get()
    left = Id.get()
    right = Id.get()
    top_left = Id.get()
    top_right = Id.get()
    bottom_left = Id.get()
    bottom_right = Id.get()
    full = Id.get()
    center = Id.get()
    background = Id.get()
    foreground = Id.get()


@dataclass
class Way:
    top = Id.get()
    bottom = Id.get()
    left = Id.get()
    right = Id.get()

    @staticmethod
    def get_all():
        return (Way.top, Way.bottom, Way.left, Way.right)


@dataclass
class Character:
    player = Id.get()
    enemy_to_catch = Id.get()
    enemy_to_avoid = Id.get()
    obstacle = Id.get()

    @staticmethod
    def get_enemies():
        return (Character.enemy_to_catch, Character.enemy_to_avoid)


@dataclass
class Effect:
    to_catch = Id.get()
    to_avoid = Id.get()

    @staticmethod
    def get_all():
        return (Effect.to_catch, Effect.to_avoid)


@dataclass
class Commands:
    greyed_out = Id.get()
    blacken = Id.get()


@dataclass
class Screenplay:
    menu_0 = Id.get()
    menu_1 = Id.get()
    menu_2 = Id.get()
    menu_3 = Id.get()
    menu_4 = Id.get()
    menu_5 = Id.get()
    pause_0 = Id.get()
    end_0 = Id.get()
    end_1 = Id.get()
    end_2 = Id.get()
    mode = Id.get()
    score = Id.get()
    none = Id.get()


@dataclass
class Button:
    frame = Id.get()
    image = Id.get()
    text = Id.get()


@dataclass
class Mode:
    easy = Id.get()
    normal = Id.get()
    hard = Id.get()
    lives_0 = Id.get()
    lives_1 = Id.get()
    lives_2 = Id.get()
    lives_3 = Id.get()


@dataclass
class Control:
    play = Id.get()
    pause = Id.get()
    resume = Id.get()
    replay = Id.get()


@dataclass
class Music:
    on = Id.get()
    off = Id.get()
    theme = Id.get()
    melody = Id.get()


@dataclass
class Language:
    french = Id.get()
    english = Id.get()


@dataclass
class Menu:
    turn_off = Id.get()
    home = Id.get()


@dataclass
class Font:
    small = Id.get()
    medium = Id.get()
    big = Id.get()


@dataclass
class Label(dict):
    def __init__(self, text_french, text_english):
        self[Language.french] = text_french
        self[Language.english] = text_english

    def set_custom(self, text):
        self[Language.french] = text
        self[Language.english] = text


@dataclass
class Const:
    path = Path()
    hint = Hint()
    cursor = Cursor()
    ground = Ground()
    way = Way()
    character = Character()
    effect = Effect()
    commands = Commands()
    screenplay = Screenplay()
    button = Button()
    mode = Mode()
    control = Control()
    music = Music()
    language = Language()
    menu = Menu()
    font = Font()
    text = {
        Character.player: Label("la sorcière", "the witch"),
        Character.enemy_to_catch: Label("les papillons", "the butterflies"),
        Character.enemy_to_avoid: Label("les corbeaux", "the crows"),
        Character.obstacle: Label("les coccinelles", "the ladybugs"),
        Mode.easy: Label("facile", "easy"),
        Mode.normal: Label("normal", "normal"),
        Mode.hard: Label("dur", "hard"),
        Mode.lives_0: Label("0 vie", "0 life"),
        Mode.lives_1: Label("1 vie", "1 life"),
        Mode.lives_2: Label("2 vies", "2 lives"),
        Mode.lives_3: Label("3 vies", "3 lives"),
        Control.play: Label("jouer", "play"),
        Control.pause: Label("pause", "pause"),
        Control.resume: Label("reprise", "resume"),
        Control.replay: Label("rejouer", "replay"),
        Music.on: Label("musique", "music"),
        Music.off: Label("muet", "mute"),
        Language.french: Label("français", "anglais"),
        Language.english: Label("french", "english"),
        Menu.turn_off: Label("quitter", "quit"),
        Menu.home: Label("retour", "return"),
        Screenplay.menu_0: Label("balade dans", "ramble in"),
        Screenplay.menu_1: Label("la clairière", "the glade"),
        Screenplay.menu_2: Label("déplace {},", "move {},"),
        Screenplay.menu_3: Label("attrape {},", "catch {},"),
        Screenplay.menu_4: Label("fuis {},", "flee {},"),
        Screenplay.menu_5: Label("évite {} !", "avoid {} !"),
        Screenplay.pause_0: Label("pause !", "pause !"),
        Screenplay.end_0: Label("fin du jeu !", "game over !"),
        Screenplay.end_1: Label("score :", "score :"),
        Screenplay.end_2: Label("mode :", "mode :"),
        Screenplay.none: Label("", "")
    }
