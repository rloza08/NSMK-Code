#!/usr/bin/env python3
from cursesmenu import SelectionMenu
import time
import os
import logging
import curses
# stdscr = curses.initscr()
# curses.start_color()


def draw(stdscr, str):
    # logger = logging.getLogger(__file__)
    # hdlr = logging.FileHandler(__file__ + ".log")
    # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    # hdlr.setFormatter(formatter)
    # logger.addHandler(hdlr)
    # logger.setLevel(logging.DEBUG)
    #
    # logger.info("begin")
    #
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_RED)
    stdscr.addstr(12,10, 'current selection : {}'.format(str), curses.color_pair(1))
    stdscr.addstr(14,10, 'selected org               : ORG2', curses.color_pair(1))
    stdscr.addstr(15,10, 'selected store list        : SHA2', curses.color_pair(1))
    stdscr.addstr(16,10, 'selected l3fwrule template : 004', curses.color_pair(1))
    # logger.info("yeah")
    # stdscr.getch()
    # logger.info("end")


_menu = {}

# _menu["main"] = ["orgs", "store-list", "l3fwrules"]
# _menu["orgs"] = ["Org-1", "Org-New", "Org-QA"]
# _menu["store-list"]=["SHA", "JEW", "INT"]
# _menu["l3fwrules"] = ["l3fwrules_004", "l3fwrules_005", "l3fwrules_006", "l3fwrules_007"]

_menu["main"] = ["networks", "stores", "l3fwrules", "s2svpnrules", "vlans", "convert"]
_menu["networks"] = ["actions", "settings"]
_menu["stores"] = ["actions", "settings"]
_menu["l3fwrules"] = ["actions", "settings"]
_menu["s2s"] = ["actions", "settings"]
_menu["networks"] = ["actions", "settings"]
_menu["store-list"]=["SHA", "JEW", "INT"]
_menu["l3fwrules"] = ["l3fwrules_004", "l3fwrules_005", "l3fwrules_006", "l3fwrules_007"]


menu_in_use = _menu["main"]

while True:
    selection = SelectionMenu.get_selection(menu_in_use)
    # print (selection)
    # time.sleep(3)
    if selection == len(menu_in_use):
        os._exit(0)
    item = menu_in_use[selection]
    curses.wrapper(draw,item)
    if menu_in_use is _menu["main"]:
        menu_in_use = _menu[item]
    else:
        menu_in_use = _menu["main"]

