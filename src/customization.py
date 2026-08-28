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
from tkinter import Canvas, CENTER, E, LEFT, NW, Tk, W
from tkinter.filedialog import askopenfile
from tkinter.messagebox import askyesno, showerror
from tkinter.ttk import Button, Entry, Label, LabelFrame
from PIL import Image, ImageTk, UnidentifiedImageError
from pygame import error
from const import Const
from tool import Math, Pen

POPUP_CUSTOM = "Voulez-vous personnaliser les graphismes ?"

INSTRUCTIONS_WIDTH = 60
INSTRUCTIONS_LABEL = (
    "Pour chaque personnage du jeu, entrez le nom (au format\n"
    "ASCII) et choisissez l'image (au format BMP, JPEG ou PNG)."
)

LABEL_WIDTH = 8
BUTTON_WIDTH = 8

NAME_WIDTH = 16
NAME_TOO_LONG = "Nom trop long."
NAME_NOT_ASCII = "Caractère invalide."
NAME_LABEL = "Nom :"

IMAGE_TYPES_NAME = "Images"
IMAGE_TYPES_FILE = ".bmp .jpg .jpeg .png"
IMAGE_INVALID = "Fichier invalide."
IMAGE_LABEL = "Image :"

BUTTON_CANCEL = "Annuler"
BUTTON_CHOOSE = "Ouvrir"
BUTTON_OK = "Valider"


class Widget:
    def __init__(self, widget):
        self.widget = widget

    def set_position(self, i, j, i_span=1, j_span=1):
        self.widget.grid(row=i, column=j, rowspan=i_span, columnspan=j_span)
        self.widget.grid(padx=4, pady=4)

    def set_sticky(self, direction):
        self.widget.grid(sticky=direction)

    def set_width(self, n_characters):
        self.widget.configure(width=n_characters)

    def set_height(self, n_characters):
        self.widget.configure(height=n_characters)

    def set_text(self, text):
        self.widget.configure(text=text)


class WidgetFrame(Widget):
    def __init__(self, text, frame):
        Widget.__init__(self, LabelFrame(master=frame))

        self.set_text(text)


class WidgetLabel(Widget):
    def __init__(self, text, frame):
        Widget.__init__(self, Label(master=frame))

        self.set_text(text)
        self.set_width(LABEL_WIDTH)
        self.widget.configure(anchor=NW, justify=LEFT)


class WidgetEntry(Widget):
    def __init__(self, frame, window):
        Widget.__init__(self, Entry(master=frame))

        self.set_width(NAME_WIDTH)
        validate_command = (window.register(window.validate), "%P")
        self.widget.configure(validate="key", validatecommand=validate_command)

    def get_info(self):
        info = self.widget.get()

        if info == "":
            info = None
        else:
            pass

        return info


class WidgetButton(Widget):
    def __init__(self, frame):
        Widget.__init__(self, Button(master=frame))

        self.set_width(BUTTON_WIDTH)

    def set_command(self, text, command):
        self.set_text(text)
        self.widget.configure(command=command)


class WidgetImage(Widget):
    def __init__(self, size, frame):
        Widget.__init__(self, Canvas(master=frame))

        self.set_width(size)
        self.set_height(size)

        self.size = size
        self.photo = ""
        self.path = None

        self.set_image(None)

    def set_image(self, path):
        self.photo = ""

        if path is not None:
            image = Image.open(path)
            image = image.resize((self.size, self.size))
            self.photo = ImageTk.PhotoImage(image)
        else:
            pass

        thickness = self.widget.cget("highlightthickness")
        point = (thickness, thickness)
        self.widget.create_image(point, image=self.photo, anchor=NW)
        self.path = path

    def get_info(self):
        return self.path


class Character(WidgetFrame):
    def __init__(self, kind, row, column, window):
        text = Const.text[kind][Const.language.french].capitalize()
        WidgetFrame.__init__(self, text, window)

        self.set_position(row, column)

        self.label_name = WidgetLabel(NAME_LABEL, self.widget)
        self.label_name.set_position(0, 0)

        self.name = WidgetEntry(self.widget, window)
        self.name.set_position(0, 1, 1, 2)

        self.label_image = WidgetLabel(IMAGE_LABEL, self.widget)
        self.label_image.set_position(1, 0)

        self.button = WidgetButton(self.widget)
        self.button.set_position(1, 1)
        self.change_button(BUTTON_CHOOSE, self.choose, window)

        size = self.button.widget.winfo_reqwidth()
        self.image = WidgetImage(size, self.widget)
        self.image.set_position(1, 2)

    def choose(self, window):
        if not window.is_busy():
            window.set_busy()
            path = Popup.choose()

            if path is not None:
                try:
                    Image.open(path)
                    Pen.load(path)
                    self.change_button(BUTTON_CANCEL, self.cancel, window)
                except (UnidentifiedImageError, error):
                    Popup.error(IMAGE_INVALID)
                    path = None
            else:
                pass

            self.image.set_image(path)
            window.unset_busy()
        else:
            pass

    def cancel(self, window):
        if not window.is_busy():
            window.set_busy()
            self.change_button(BUTTON_CHOOSE, self.choose, window)
            self.image.set_image(None)
            window.unset_busy()
        else:
            pass

    def change_button(self, text, command, window):
        self.button.set_command(text, lambda: command(window))


class Window(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.command_cancel)
        self.title(Const.path.caption_text)
        self.iconbitmap(Math.path(Const.path.caption_icon))
        self.resizable(False, False)

        self.instructions = WidgetLabel(INSTRUCTIONS_LABEL, self)
        self.instructions.set_position(0, 0, 1, 2)
        self.instructions.set_width(INSTRUCTIONS_WIDTH)
        self.instructions.widget.configure(anchor=CENTER)

        self.player = Character(Const.character.player, 1, 0, self)
        kind_enemy_to_catch = Const.character.enemy_to_catch
        self.enemy_to_catch = Character(kind_enemy_to_catch, 1, 1, self)
        kind_enemy_to_avoid = Const.character.enemy_to_avoid
        self.enemy_to_avoid = Character(kind_enemy_to_avoid, 2, 0, self)
        self.obstacle = Character(Const.character.obstacle, 2, 1, self)

        self.button_ok = WidgetButton(self)
        self.button_ok.set_position(3, 0)
        self.button_ok.set_sticky(E)
        self.button_ok.set_command(BUTTON_OK, self.command_ok)
        self.button_cancel = WidgetButton(self)
        self.button_cancel.set_position(3, 1)
        self.button_cancel.set_sticky(W)
        self.button_cancel.set_command(BUTTON_CANCEL, self.command_cancel)

    def show(self):
        self.eval('tk::PlaceWindow . center')
        self.deiconify()
        self.mainloop()

    def is_not_ascii(self, text):
        not_ascii = False

        for character in text:
            if not 32 <= ord(character) <= 126:
                not_ascii = True
            else:
                pass

        return not_ascii

    def is_too_long(self, text):
        return len(text) > NAME_WIDTH

    def validate(self, text):
        valid = True
        self.set_busy()

        if self.is_too_long(text):
            valid = False
            Popup.error(NAME_TOO_LONG)
        elif self.is_not_ascii(text):
            valid = False
            Popup.error(NAME_NOT_ASCII)
        else:
            pass

        self.unset_busy()

        return valid

    def command_ok(self):
        if not self.is_busy():
            self.set_busy()
            self.set_infos()
            self.unset_busy()
            self.command_cancel()
        else:
            pass

    def command_cancel(self):
        self.destroy()

    def is_busy(self):
        return self.call("tk", "busy", "status", self) == 1

    def set_busy(self):
        self.call("tk", "busy", "hold", self)

    def unset_busy(self):
        self.call("tk", "busy", "forget", self)

    def set_infos(self):
        Customization.player.set_info(self.player)
        Customization.enemy_to_catch.set_info(self.enemy_to_catch)
        Customization.enemy_to_avoid.set_info(self.enemy_to_avoid)
        Customization.obstacle.set_info(self.obstacle)


class Popup:
    @staticmethod
    def error(text):
        showerror(Const.path.caption_text, text)

    @staticmethod
    def question(text):
        return askyesno(Const.path.caption_text, text)

    @staticmethod
    def choose():
        file_types = {(IMAGE_TYPES_NAME, IMAGE_TYPES_FILE)}
        file = askopenfile(filetypes=file_types)
        path = None

        if file is not None:
            path = file.name
            file.close()
        else:
            pass

        return path


@dataclass
class Info(dict):
    def __init__(self):
        self.name = None
        self.path = None

    def set_info(self, character):
        self.name = character.name.get_info()
        self.path = character.image.get_info()


@dataclass
class Customization:
    player = Info()
    enemy_to_catch = Info()
    enemy_to_avoid = Info()
    obstacle = Info()

    @staticmethod
    def fill_infos():
        window = Window()

        if Popup.question(POPUP_CUSTOM):
            window.show()
        else:
            window.destroy()
