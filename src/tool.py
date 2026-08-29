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
import math
import os
import random
import sys
import pygame
from const import Const


class Math:
    @staticmethod
    def floor(n):
        return math.floor(n)

    @staticmethod
    def ceil(n):
        return math.ceil(n)

    @staticmethod
    def round(n):
        n_rounded = None
        fractional, integer = math.modf(n)

        if fractional < 0.5:
            n_rounded = int(integer)
        else:
            n_rounded = int(integer) + 1

        return n_rounded

    @staticmethod
    def trunc_ratio(n):
        n_truncated = None

        if n > 1:
            n_truncated = 1
        else:
            n_truncated = n

        return n_truncated

    @staticmethod
    def pow(n):
        return math.pow(n, 2)

    @staticmethod
    def sqrt(n):
        return math.sqrt(n)

    @staticmethod
    def abs(n):
        return math.fabs(n)

    @staticmethod
    def fact(n):
        return math.factorial(n)

    @staticmethod
    def rand_int(n_min, n_max):
        return random.randrange(n_min, n_max + 1, 1)

    @staticmethod
    def rand_list(iterable):
        return random.choice(iterable)

    @staticmethod
    def path(name_file):
        folder = None

        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            folder = getattr(sys, "_MEIPASS")
        else:
            folder = os.path.join("..", Const.path.folder)

        return os.path.join(folder, name_file)


class Screen(pygame.Surface):
    window = None

    @staticmethod
    def init():
        random.seed(0)
        pygame.init()

        w_screen = pygame.display.get_desktop_sizes()[0][0]
        h_screen = pygame.display.get_desktop_sizes()[0][1]
        Screen.size_cell = Math.floor(h_screen * 3 / 4 / 8)

        if Screen.size_cell > 100:
            Screen.size_cell = 100
        else:
            pass

        if 5 * Screen.size_cell > w_screen:
            Screen.size_cell = Math.floor(w_screen / 5)
        else:
            pass

        w_window = 5 * Screen.size_cell
        h_window = 8 * Screen.size_cell
        Screen.window = pygame.display.set_mode((w_window, h_window))

    @staticmethod
    def set_icon_and_caption(surface, name):
        pygame.display.set_icon(surface)
        pygame.display.set_caption(name)

    @staticmethod
    def quit():
        pygame.quit()
        sys.exit()

    @staticmethod
    def display():
        pygame.display.flip()

    @staticmethod
    def to_x_cell(x):
        return Math.floor(x / Screen.size_cell)

    @staticmethod
    def to_y_cell(y):
        return Math.floor(y / Screen.size_cell)

    @staticmethod
    def to_x(x_cell):
        return x_cell * Screen.size_cell

    @staticmethod
    def to_y(y_cell):
        return y_cell * Screen.size_cell


class Timer:
    run = True
    ticked = False
    ticks_game = 0
    time_motion = 500
    ticks_frame = Math.ceil(1000 / 60)

    @staticmethod
    def update():
        ticks_game = pygame.time.get_ticks()

        if ticks_game - Timer.ticks_game >= Timer.ticks_frame:
            Timer.ticks_game = ticks_game
            Timer.ticked = True
        else:
            pass

    @staticmethod
    def tick():
        ticked = Timer.ticked
        Timer.ticked = False

        return ticked

    @staticmethod
    def get_ticks_motion():
        return Math.ceil(Timer.time_motion / Timer.ticks_frame)


class Event:
    x_cell = None
    y_cell = None
    click = False

    @staticmethod
    def reset():
        Event.x_cell = None
        Event.y_cell = None
        Event.click = False

    @staticmethod
    def set_cell(x, y):
        Event.x_cell = Screen.to_x_cell(x)
        Event.y_cell = Screen.to_y_cell(y)

    @staticmethod
    def find():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Screen.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                Event.click = True
                Event.set_cell(event.pos[0], event.pos[1])
            else:
                pass

        if not Event.click:
            coordinates = pygame.mouse.get_pos()
            Event.set_cell(coordinates[0], coordinates[1])
        else:
            pass

    @staticmethod
    def is_click():
        return Event.click

    @staticmethod
    def is_hoover():
        return (
            not Event.is_click() and
            Event.x_cell is not None and
            Event.y_cell is not None
        )

    @staticmethod
    def has():
        return Event.is_click() or Event.is_hoover()


@dataclass
class Color:
    transparency = pygame.Color(0, 0, 0, 0)
    black = pygame.Color(0, 0, 0, 255)
    white = pygame.Color(255, 255, 255, 255)
    grey = pygame.Color(127, 127, 127, 255)
    green = pygame.Color(0, 255, 0, 255)
    red = pygame.Color(255, 0, 0, 255)
    blue = pygame.Color(0, 0, 255, 255)


class Pen:
    ratio_greyed_out = 0.50

    @staticmethod
    def create(w, h):
        return pygame.Surface((w, h), pygame.SRCALPHA)

    @staticmethod
    def load(name_file):
        return pygame.image.load(Math.path(name_file))

    @staticmethod
    def set_alpha(surface, ratio):
        surface.set_alpha(Math.floor(ratio * 255))

    @staticmethod
    def set_color_key(surface, color_key):
        surface.set_colorkey(color_key)

    @staticmethod
    def scale(surface, w, h):
        return pygame.transform.scale(surface, (w, h))

    @staticmethod
    def scale_cell(surface):
        return Pen.scale(surface, Screen.size_cell, Screen.size_cell)

    @staticmethod
    def draw_color(surface, color):
        surface.fill(color)

    @staticmethod
    def create_ellipse(w, h, area, color):
        surface = Pen.create(w, h)
        pygame.draw.ellipse(surface, color, area, 1)

        return surface

    @staticmethod
    def create_rectangle(w, h, area, color):
        surface = Pen.create(w, h)
        pygame.draw.rect(surface, color, area, 1)

        return surface

    @staticmethod
    def create_area(left, top, w, h):
        return pygame.Rect(left, top, w, h)

    @staticmethod
    def get_sprite(source, i, j, n_columns, n_raws):
        w = source.get_width() / n_columns
        h = source.get_height() / n_raws
        surface = Pen.create(w, h)
        surface.blit(source, (0, 0), pygame.Rect(i * w, j * h, w, h))

        return surface

    @staticmethod
    def create_text(w, h, text, font):
        surface_text = font.render(text, False, Color.black, Color.white)
        Pen.set_color_key(surface_text, Color.white)

        surface = Pen.create(w, h)
        x = Math.floor((surface.get_width() - surface_text.get_width()) / 2)
        y = Math.floor((surface.get_height() - surface_text.get_height()) / 2)
        Pen.draw_surface(surface, surface_text, x, y)

        return surface

    @staticmethod
    def get_font(size_font):
        return pygame.font.Font(Math.path(Const.path.font), size_font)

    @staticmethod
    def draw_surface(surface_1, surface_2, x, y):
        surface_1.blit(surface_2, (x, y))

    @staticmethod
    def draw_screen(surface, x, y):
        Pen.draw_surface(Screen.window, surface, x, y)

    @staticmethod
    def draw_cell(surface_1, surface_2, x_cell, y_cell):
        x = x_cell * Screen.size_cell
        y = y_cell * Screen.size_cell
        Pen.draw_surface(surface_1, surface_2, x, y)

    @staticmethod
    def draw_cell_screen(surface, x_cell, y_cell):
        Pen.draw_cell(Screen.window, surface, x_cell, y_cell)


class Loading:
    @staticmethod
    def display(step, steps):
        w_window = Screen.window.get_width()
        h_window = Screen.window.get_height()

        name = Pen.load(Const.path.image_copyright)
        w = w_window
        h = w * name.get_height() / name.get_width()
        name = Pen.scale(name, w, h)
        Pen.draw_screen(name, 0, h_window - name.get_height())

        title = Pen.load(Const.path.image_title)
        w = w_window
        h = w * title.get_height() / title.get_width()
        title = Pen.scale(title, w, h)
        Pen.draw_screen(title, 0, 0)

        w = w_window
        h = h_window - name.get_height() - title.get_height()
        hourglass = Pen.scale(Loading.get_hourglass(step, steps), w, h)
        Pen.draw_screen(hourglass, 0, title.get_height())

        Screen.display()

    @staticmethod
    def get_hourglass(step, steps):
        size = 64
        border = Math.floor(size / 6)
        off = Math.floor(border / 2)
        p_min = 1 + border
        p_max = size - 2 - border
        p_mid = Math.floor(size / 2) - 1

        surface = Pen.create(size, size)
        Pen.draw_color(surface, Color.black)

        Loading.draw_line(surface, (p_min, p_min - off), (p_max, p_min - off))
        Loading.draw_line(surface, (p_min, p_min - off), (p_min, p_min))
        Loading.draw_line(surface, (p_max, p_min - off), (p_max, p_min))

        Loading.draw_line(surface, (p_min, p_max + off), (p_max, p_max + off))
        Loading.draw_line(surface, (p_min, p_max), (p_min, p_max + off))
        Loading.draw_line(surface, (p_max, p_max), (p_max, p_max + off))

        Loading.draw_line(surface, (p_min, p_min), (p_max, p_min))
        Loading.draw_line(surface, (p_min, p_max), (p_max, p_max))
        Loading.draw_line(surface, (p_min, p_min), (p_mid, p_mid))
        Loading.draw_line(surface, (p_mid + 1, p_mid), (p_max, p_min))
        Loading.draw_line(surface, (p_min, p_max), (p_mid + 1, p_mid))
        Loading.draw_line(surface, (p_mid, p_mid), (p_max, p_max))

        n_max_lines = p_mid - p_min - 2
        n_max_pixels = Math.floor(n_max_lines * (n_max_lines + 1) / 2)
        n_pixels = Math.floor(n_max_pixels * (1 - step / steps))
        n_lines = 0

        for n_line_pixels in range(0, n_max_lines, 1):
            if n_pixels - n_line_pixels - 1 >= 0:
                n_lines += 1
                n_pixels -= n_line_pixels + 1
            else:
                break

        Loading.draw_sand(surface, p_min, p_max, n_lines, n_max_lines)

        return surface

    @staticmethod
    def draw_line(surface, point_1, point_2):
        if point_2[0] != point_1[0]:
            a = (point_2[1] - point_1[1]) / (point_2[0] - point_1[0])

            for x in range(point_1[0], point_2[0] + 1, 1):
                y = Math.floor(a * (x - point_1[0]) + point_1[1])
                surface.set_at((x, y), Color.white)
        else:
            for y in range(point_1[1], point_2[1] + 1, 1):
                surface.set_at((point_1[0], y), Color.white)

    @staticmethod
    def draw_sand(surface, p_min, p_max, n_lines, n_max_lines):
        for n_line in range(0, n_max_lines, 1):
            x_1 = p_min + 5 + n_line
            x_2 = p_max - 5 - n_line
            y = None

            if n_line >= n_max_lines - n_lines:
                y = p_min + 2 + n_line
            else:
                y = p_max - 2 - n_line

            Loading.draw_line(surface, (x_1, y), (x_2, y))


@dataclass
class Sound:
    @staticmethod
    def create(file_path):
        return pygame.mixer.Sound(file_path)
