# To do: understand item relationships, how to spawn new items according to a template and fill with connections to backend
# also how to destroy items and deallocate stuff and how to close the program for good.


import dearpygui.dearpygui as dpg
import pykea_home_smart as phs

device_list = []
backend = None
def instanciate_backend():
    global backend
    backend = phs.PykeaHomeSmart()
    global device_list
    device_list = backend.get_smart_device_list()

def toggle_device(sender, app_data):
    user_data = dpg.get_item_user_data(sender)
    #global backend
    backend.toggle_device(user_data, 'n')

if __name__ == "__main__":
    instanciate_backend()
    dpg.create_context()

    with dpg.window(label="Toggle ", pos=(0, 0)):
        for device in device_list:
            tag = device[6]
            name = device[1]
            dpg.add_button(label=name, callback=toggle_device, tag=tag, user_data=name)


    dpg.create_viewport(title='Custom Title', width=600, height=400)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()