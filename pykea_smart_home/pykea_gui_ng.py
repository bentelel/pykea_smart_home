# To do: understand item relationships, how to spawn new items according to a template and fill with connections to backend
# also how to destroy items and deallocate stuff and how to close the program for good.
import time

from nicegui import ui
from nicegui.events import ValueChangeEventArguments
import pykea_home_smart as phs


class UI:
    """
    Class holding everything the UI needs and all associated methods.
    """

    def __init__(self):
        self.backend, self.device_list, self.room_dict = self.instantiate_backend()
        self.BACKGROUND_COLOR_UI = '#ddeeff'
        self.BACKGROUND_COLOR_ROOM_BUTTON = '#fcba03'
        self.POLL_RATE_IN_S = 5

        ui.query('body').style(f'background-color: {self.BACKGROUND_COLOR_UI}')  # Set background color of tab

        self.build_room_and_device_buttons()

        # ui.timer(SETTINGS.POLL_RATE_IN_S, lambda: refresh_ui_elements())

        ui.run()

    def instantiate_backend(self):
        backend = phs.PykeaHomeSmart()
        device_list = backend.get_smart_device_list()
        room_dict = backend.get_room_dictionary()
        room_dict_sorted = {k: room_dict[k] for k in sorted(room_dict)}
        return backend, device_list, room_dict_sorted

    def handle_exception(self, e):
        ui.notify(e, close_button='Dismiss')

    def toggle_room(self, room_name):
        try:
            self.backend.toggle_room(room_name)
        except Exception as e:
            self.handle_exception(e)

    def toggle_device(self, device_key):
        try:
            print(device_key)
            self.backend.toggle_device_by_id(int(device_key))
        except Exception as e:
            self.handle_exception(e)

    @ui.refreshable
    def build_room_and_device_buttons(self):
        try:
            for key, value in self.room_dict.items():
                with ui.row():
                    with ui.button_group():
                        ui.button(text=f'{key}',
                                  color=self.BACKGROUND_COLOR_ROOM_BUTTON,
                                  on_click=lambda i=key: self.toggle_room(i))
                        for v in value:
                            device_name = v[0]
                            device_key = v[1]
                            ui.button(text=f'{device_name}',
                                      on_click=lambda j=device_key: self.toggle_device(j))
            return
        except Exception as e:
            self.handle_exception(e)

    def refresh_ui_elements(self):
        ui.notify("refreshing")
        self.room_dict.pop(0)
        self.build_room_and_device_buttons.refresh()


if __name__ in ("__main__", "__mp_main__"):
    # "__mp_main__" is needed to allow for multiprocessing which is needed in NiceGUI
    ui_instance = UI()
