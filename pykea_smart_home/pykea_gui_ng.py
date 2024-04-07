# To do: understand item relationships, how to spawn new items according to a template and fill with connections to backend
# also how to destroy items and deallocate stuff and how to close the program for good.


from nicegui import ui
from nicegui.events import ValueChangeEventArguments
import pykea_home_smart as phs

device_list = []
backend = None
def instanciate_backend():
    global backend
    backend = phs.PykeaHomeSmart()
    global device_list
    device_list = backend.get_smart_device_list()

def toggle_device(sender, app_data):
    #user_data = dpg.get_item_user_data(sender)
    #global backend
    #backend.toggle_device(user_data, 'n')
    pass

def show(event: ValueChangeEventArguments):
    name = type(event.sender).__name__
    ui.notify(f'{name}: {event.value}')

if __name__ in ("__main__","__mp_main__"):
    # The "__mp_main__" is needed to allow for multiprocessing which is needed in NiceGUI
    #instanciate_backend()
    ui.button('Button', on_click=lambda: ui.notify('Click'))
    with ui.row():
        ui.checkbox('Checkbox', on_change=show)
        ui.switch('Switch', on_change=show)
    ui.radio(['A', 'B', 'C'], value='A', on_change=show).props('inline')
    with ui.row():
        ui.input('Text input', on_change=show)
        ui.select(['One', 'Two'], value='One', on_change=show)
    ui.link('And many more...', '/documentation').classes('mt-8')

    ui.run()