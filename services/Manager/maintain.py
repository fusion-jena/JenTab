from consolemenu import *
from consolemenu.format import *
from consolemenu.items import *

from maintenance.resetErrors import run as resetErrors
from maintenance.resetFullMissCea import run as resetFullMissCea
from maintenance.resetPartialMissCea import run as resetPartialMissCea
from maintenance.manualTables import run as manualTables

# styling of the menu
menu_format = MenuFormatBuilder().set_border_style_type(MenuBorderStyleType.HEAVY_BORDER) \
    .set_title_align('center') \
    .set_subtitle_align('center') \
    .set_left_margin(4) \
    .set_right_margin(4) \
    .show_header_bottom_border(True)

# Create the menu
menu = ConsoleMenu(
    title="JenTab Manager Maintenance Tools",
    prologue_text="Be aware that the options here do modify the database. Do a database backup before executing anything!",
    formatter=menu_format,
)

# add menu options
menu.append_item(FunctionItem("Reset tables that returned errors", resetErrors, should_exit=True))
menu.append_item(FunctionItem("Reset tables that contain no results for CEA task", resetFullMissCea, should_exit=True))
menu.append_item(FunctionItem("Reset tables that lack some results for CEA task", resetPartialMissCea, should_exit=True))
menu.append_item(FunctionItem("Replace and reset tables from /maintenance/manualTables", manualTables, should_exit=True))

# show the menu
menu.show()
