# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 21:58:21 2024

@author: Lukas Bentele
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 15:58:57 2024

@author: LukasBentele
"""

import dearpygui.dearpygui as dpg
import pykea_home_smart as phs


def btn1_clicked():
    print('btn1 clicked')

window_width = 800
window_height = 600
dpg.create_context()

with dpg.window(width=window_width, height=window_height, pos=(0,0), no_title_bar=True, no_move=True):
    dpg.add_text("hello world")
    button1 = dpg.add_button(label="button1", tag="btn1")
    dpg.set_item_callback("btn1", btn1_clicked)

    slider_int = dpg.add_slider_int(label="slider_int",width=100,min_value=0,max_value=200)


dpg.create_viewport(title='Custom Title', width=window_width, height=window_height)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()