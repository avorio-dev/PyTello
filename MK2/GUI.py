####################################################################################################################
# IMPORTS
import os
from datetime import datetime

import pygame

import tkinter as tk
import submodules.PyUtils.TkInter.ZAGThemeTk

from win32api import GetSystemMetrics
from tkinter import ttk, messagebox, scrolledtext

from MK2.TelloMK2 import TelloMK2
from MK2.Cockpit import Cockpit
from submodules.PyUtils.Logging import ZAGLogger


####################################################################################################################
# CORE

class GUI:
    # ---> ATTRIBUTES
    window_width = int(GetSystemMetrics(0))
    window_height = int(GetSystemMetrics(1))
    _log_entries = []
    _tello = None
    _cockpit = None

    # ---> CONSTANTS
    DARK_THEME = "dark"
    DEFAULT_THEME = "default"

    # Mapping of colors for log text
    LOG_COLORS = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "magenta",
    }

    # ---> CONSTRUCTOR
    def __init__(self, frame_border):
        # Initialize pygame (pygame must be initialized before tkinter)
        pygame.init()
        self._clock = pygame.time.Clock()  # Create a Clock object for controlling the update rate

        # Set border for all frames for easy debug
        self._show_frame_border = frame_border

        # Set default theme
        self.current_theme = self.DARK_THEME

        # Set Tkinter
        self._init_root()

        # Apply custom theme to all components of your GUI
        self._styler.apply_theme_recurs(self._root, self.current_theme)

    # ---> FUNCTIONS
    def run_mainloop(self):
        self._root.after(1500, self._create_tello_instance)
        self._root.mainloop()

    def _init_root(self):
        self._root = tk.Tk()
        self._root.title("Astro-Tello")
        self._root.state("zoomed")

        # Icons must have an instance attribute to avoid that garbage collector delete them
        # self._load_icons()

        self._styler = submodules.PyUtils.TkInter.ZAGThemeTk.ZAGThemeTk()

        # Main Layout
        frame_root = ttk.Frame(self._root, name="frame_root")
        frame_root.pack(fill="both", expand=True, padx=20, pady=20)

        frame_toolbar = ttk.Frame(frame_root, name="frame_toolbar")
        frame_toolbar.pack(side="top", fill="x", padx=5, pady=5)

        frame_streaming = ttk.Frame(frame_root, name="frame_streaming")
        frame_streaming.pack(side="left", fill="both", padx=5, pady=5)

        frame_map = ttk.Frame(frame_root, name="frame_map")
        frame_map.pack(side="right", fill="both", padx=5, pady=5)

        frame_log = ttk.Frame(frame_root, name="frame_log")
        frame_log.pack(side="left", fill="both", padx=5, pady=5)

        # Toolbar Frame
        self._init_frame_toolbar(frame_toolbar)

        # Streaming Frame
        self._init_frame_streaming(frame_streaming)

        # LOG Frame
        self._init_frame_log(frame_log)

        # Map Frame
        self._init_frame_map(frame_map)

        self._set_border(frame_toolbar)
        self._set_border(frame_streaming)
        self._set_border(frame_log)
        self._set_border(frame_map)

    def _init_frame_toolbar(self, frame_toolbar):
        # Welcome Label
        welcome_label = ttk.Label(frame_toolbar, text="SR71 - BlackTello !", anchor=tk.CENTER)
        welcome_label.pack(side="left", fill=tk.BOTH, expand=True)

        # ---> Theme
        menu_btn = ttk.Menubutton(frame_toolbar, text="Select Theme")
        menu_btn.pack(side="right")

        themes = self._styler.get_loaded_themes()

        # Set var which will trace the selected item menu
        self._selected_theme = tk.StringVar()
        self._selected_theme.set(self.current_theme)
        self._selected_theme.trace("w", self._switch_theme)

        menu_themes = tk.Menu(menu_btn, tearoff=0)
        for theme in themes:
            menu_themes.add(label=theme,
                            variable=self._selected_theme,
                            itemType=tk.RADIOBUTTON)
        menu_btn["menu"] = menu_themes

    def _init_frame_streaming(self, frame_streaming):
        pass

    def _init_frame_log(self, frame_log):
        log_text = scrolledtext.ScrolledText(frame_log, state=tk.DISABLED, wrap=tk.WORD, width=150)
        log_text.pack(fill="both", expand=True)

        for tag, color_code in self.LOG_COLORS.items():
            log_text.tag_configure(tag, foreground=color_code)

        self._update_log(frame_log, log_text)

    def _init_frame_map(self, frame_map):
        text = ttk.Label(frame_map, text="MAP Route", anchor=tk.CENTER)
        text.pack()

        embedded_frame = ttk.Frame(frame_map, width=self.window_width / 2, height=self.window_height)
        embedded_frame.pack()

        os.environ['SDL_WINDOWID'] = str(embedded_frame.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib'

        screen = pygame.display.set_mode((embedded_frame.winfo_width(), embedded_frame.winfo_height()))
        self._update_pygame_frame_map(screen)

    def _update_pygame_frame_map(self, py_surface):
        GRID_COLOR = (255, 255, 255)
        GRID_LINE_WIDTH = 1
        GRID_SPACING = 40

        py_surface.fill((0, 0, 255))

        py_width, py_height = py_surface.get_width(), py_surface.get_height()

        py_surface.fill((0, 0, 255))


        pygame.draw.rect(py_surface, GRID_COLOR,
                         (GRID_SPACING, GRID_SPACING, py_width - 2 * GRID_SPACING, py_height - 2 * GRID_SPACING), 2)

        # Disegna la griglia orizzontale
        for y in range(GRID_SPACING, py_height - GRID_SPACING, GRID_SPACING):
            pygame.draw.line(py_surface, GRID_COLOR, (GRID_SPACING, y), (py_width - GRID_SPACING, y), GRID_LINE_WIDTH)

        # Disegna la griglia verticale
        for x in range(GRID_SPACING, py_width - GRID_SPACING, GRID_SPACING):
            pygame.draw.line(py_surface, GRID_COLOR, (x, GRID_SPACING), (x, py_height - GRID_SPACING), GRID_LINE_WIDTH)

        pygame.draw.circle(py_surface, (255, 0, 0), (20, 10), 30)
        pygame.display.update()

        self._clock.tick(60)  # Set the update rate limit to 60 FPS
        self._root.after(1, lambda: self._update_pygame_frame_map(py_surface))

    def _create_tello_instance(self):
        self._tello = TelloMK2()
        self._root.after(100, self._init_tello_instance)

    def _init_tello_instance(self):
        self._tello.initialize()
        self._cockpit = Cockpit(self._tello)

    def _set_border(self, frame):
        if self._show_frame_border:
            frame.configure(borderwidth=2, relief="groove")

    def _switch_theme(self, *args):
        # Selected by String Var of menubutton
        self._current_theme = self._selected_theme.get()
        self._styler.apply_theme_recurs(self._root, self._current_theme)

    def _update_log(self, log_frame, log_text):
        if self._tello is not None:
            current_indx = len(self._log_entries)
            self._log_entries.clear()
            self._log_entries = self._tello.get_log_entries().copy()
            log_text.config(state=tk.NORMAL)

            for log_indx in range(current_indx, len(self._log_entries)):
                for tag, color_code in self.LOG_COLORS.items():
                    if tag in self._log_entries[log_indx]:
                        log_text.insert(tk.END, self._log_entries[log_indx] + "\n", tag)
                        break
                else:
                    log_text.insert(tk.END, self._log_entries[log_indx] + "\n")

            log_text.see(tk.END)  # Scroll to the end
            log_text.config(state=tk.DISABLED)

        log_frame.after(10, lambda: self._update_log(log_frame, log_text))


if __name__ == "__main__":
    gui = GUI(False)
    gui.run_mainloop()
