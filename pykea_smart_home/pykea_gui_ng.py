# To do: understand item relationships, how to spawn new items according to a template and fill with connections to backend
# also how to destroy items and deallocate stuff and how to close the program for good.


from nicegui import ui,events
from nicegui.events import ValueChangeEventArguments
import pykea_home_smart as phs

device_list = []
backend = None
# room list > key room name; values: [(device, key), (device, key)..]
room_dict = {}
def instanciate_backend():
    global backend
    backend = phs.PykeaHomeSmart()
    global device_list
    device_list = backend.get_smart_device_list()
    global room_dict
    room_dict = backend.get_room_dictionary()



def show(event: ValueChangeEventArguments):
    name = type(event.sender).__name__
    ui.notify(f'{name}: {event.value}')

def toggle_room(room_name):
    try:
        print(room_name)
        backend.toggle_room(room_name)
    except Exception as e:
        print(e)

def toggle_device(device_key):
    try:
        print(device_key)
        backend.toggle_device_by_id(int(device_key))
    except Exception as e:
        print(e)



if __name__ in ("__main__","__mp_main__"):
    # The "__mp_main__" is needed to allow for multiprocessing which is needed in NiceGUI
    instanciate_backend()
    ui.button('Button', on_click=lambda: ui.notify('Click'))



    for key, value in room_dict.items():
        # this loop does not work correctly. the last room name gets associated with all lambda functions > better wording: at runtime key = key of last room
        with ui.row():
            ui.button(text=f'{key}', on_click=lambda i=key: toggle_room(i))
            for v in value:
                device_name = v[0]
                device_key = v[1]
                ui.button(text=f'{device_name}', on_click=lambda j=device_key: toggle_device(j))
    ui.radio(['A', 'B', 'C'], value='A', on_change=show).props('inline')
    with ui.row():
        ui.input('Text input', on_change=show)
        ui.select(['One', 'Two'], value='One', on_change=show)
    ui.link('And many more...', '/documentation').classes('mt-8')

    ui.run()