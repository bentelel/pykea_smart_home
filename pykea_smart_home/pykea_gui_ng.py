# Rebuilding the complete ui at poll rate is not a good idea. at low poll rates this leads to the buttons not being
# click able because the ui is constantly rebuilding.
# i need to refresh the button colors etc without rebuilding everything. > put the ui elements into a dict etc and
# update them then
# > need some kind of factory which build the ui elements and not that "build everything" method..

from nicegui import ui, app
import pykea_home_smart as phs

# room dict
#{'arbeitszimmer': [('Work work work ', 1), ('Chromeschnutze', 2), ('Schmonk', 3)], 'küche': [('Spüli', 4)], 'schlafzimmer': [('Lumpe', 5), ('Brigitte', 6)], 'wohnzimmer': [('Eckeschnecke', 7), ('Strickli', 8), ('Granitstrahl', 9), ('Kugelfisch', 10), ('Laberlampe', 11)]}
# device dict
#{1: ('Work work work ', 'Arbeitszimmer', 'False', 'light', 'True', '54aef854-c8f0-4754-8ff2-adcf30c9fffc_1'), 2: ('Chromeschnutze', 'Arbeitszimmer', 'False', 'light', 'True', '7473acbe-d3ec-4b3c-8356-f7a88369cff0_1'), 3: ('Schmonk', 'Arbeitszimmer', 'False', 'light', 'True', '9f7bea2a-091b-430c-ae89-be64ab31b337_1'), 4: ('Spüli', 'Küche', 'True', 'light', 'False', 'a12ba763-53a6-4e5a-aafd-76e8507a2a9a_1'), 5: ('Lumpe', 'Schlafzimmer', 'False', 'light', 'True', '118c9469-8922-4fce-84bd-e75c665a9612_1'), 6: ('Brigitte', 'Schlafzimmer', 'False', 'light', 'True', '295f0d5f-1571-4949-beb4-9f5224bb3e79_1'), 7: ('Eckeschnecke', 'Wohnzimmer', 'True', 'outlet', 'True', '1427a58e-614f-4e73-acdc-9b654669d662_1'), 8: ('Strickli', 'Wohnzimmer', 'True', 'light', 'True', '2ba4f56f-bab0-4cf7-bb9d-c8612c3bc3f0_1'), 9: ('Granitstrahl', 'Wohnzimmer', 'True', 'outlet', 'True', 'f14803a6-1cae-42d5-aaed-51a545263ce3_1'), 10: ('Kugelfisch', 'Wohnzimmer', 'True', 'outlet', 'True', 'fc56c5d9-0b9f-4843-8faf-4db5a3edad89_1'), 11: ('Laberlampe', 'Wohnzimmer', 'True', 'outlet', 'True', 'fd4b1821-56d2-44ec-ae87-ffd869c9e39d_1')}


class UI:
    """
    Class holding everything the UI needs and all associated methods.
    """

    def __init__(self):
        self.backend, self.device_dict, self.room_dict = self.instantiate_backend()
        self.BACKGROUND_COLOR_UI = '#ddeeff'
        self.BACKGROUND_COLOR_ROOM_BUTTON = '#fcba03'
        self.BACKGROUND_COLOR_DEVICE_BUTTON_ON = '#03d3fc'
        self.BACKGROUND_COLOR_DEVICE_BUTTON_OFF = '#036ffc'
        self.BACKGROUND_COLOR_DEVICE_BUTTON_UNREACHABLE = '#757778'
        self.POLL_RATE_IN_S = 0.5
        self.refresh_flag = True

        self.active_tab = None

        self.DEBUGGING_ROOM_DICT = {'arbeitszimmer': [('Work work work ', 1), ('Chromeschnutze', 2), ('Schmonk', 3)], 'küche': [('Spüli', 4)], 'schlafzimmer': [('Lumpe', 5), ('Brigitte', 6)], 'wohnzimmer': [('Eckeschnecke', 7), ('Strickli', 8), ('Granitstrahl', 9), ('Kugelfisch', 10), ('Laberlampe', 11)]}
        self.DEBUGGING_DEVICE_DICT = {1: ('Work work work ', 'Arbeitszimmer', 'False', 'light', 'True', '54aef854-c8f0-4754-8ff2-adcf30c9fffc_1'), 2: ('Chromeschnutze', 'Arbeitszimmer', 'False', 'light', 'True', '7473acbe-d3ec-4b3c-8356-f7a88369cff0_1'), 3: ('Schmonk', 'Arbeitszimmer', 'False', 'light', 'True', '9f7bea2a-091b-430c-ae89-be64ab31b337_1'), 4: ('Spüli', 'Küche', 'True', 'light', 'False', 'a12ba763-53a6-4e5a-aafd-76e8507a2a9a_1'), 5: ('Lumpe', 'Schlafzimmer', 'False', 'light', 'True', '118c9469-8922-4fce-84bd-e75c665a9612_1'), 6: ('Brigitte', 'Schlafzimmer', 'False', 'light', 'True', '295f0d5f-1571-4949-beb4-9f5224bb3e79_1'), 7: ('Eckeschnecke', 'Wohnzimmer', 'True', 'outlet', 'True', '1427a58e-614f-4e73-acdc-9b654669d662_1'), 8: ('Strickli', 'Wohnzimmer', 'True', 'light', 'True', '2ba4f56f-bab0-4cf7-bb9d-c8612c3bc3f0_1'), 9: ('Granitstrahl', 'Wohnzimmer', 'True', 'outlet', 'True', 'f14803a6-1cae-42d5-aaed-51a545263ce3_1'), 10: ('Kugelfisch', 'Wohnzimmer', 'True', 'outlet', 'True', 'fc56c5d9-0b9f-4843-8faf-4db5a3edad89_1'), 11: ('Laberlampe', 'Wohnzimmer', 'True', 'outlet', 'True', 'fd4b1821-56d2-44ec-ae87-ffd869c9e39d_1')}



        ui.query('body').style(f'background-color: {self.BACKGROUND_COLOR_UI}')  # Set background color of tab

        self.build_room_and_device_buttons()


        if self.refresh_flag:
            ui.timer(self.POLL_RATE_IN_S, lambda: self.refresh_device_and_room_dicts())

        ui.page_title('pykea smart home')
        ui.run()
        print('init done')

    def instantiate_backend(self):
        try:
            print("instantiating backend")
            backend = phs.PykeaHomeSmart()
            device_dict = backend.get_device_dictionary()
            device_dict_sorted = {k: device_dict[k] for k in sorted(device_dict)}
            room_dict = backend.get_room_dictionary()
            room_dict_sorted = {k: room_dict[k] for k in sorted(room_dict)}
            return backend, device_dict_sorted, room_dict_sorted
        except Exception as e:
            self.handle_exception(e)

    def handle_exception(self, e) -> None:
        ui.notify(e, close_button='Dismiss')
        print(f"Error: {e}")

    def toggle_room(self, room_name) -> None:
        try:
            self.backend.toggle_room(room_name)
        except Exception as e:
            self.handle_exception(e)

    def toggle_device(self, device_key) -> None:
        try:
            self.backend.toggle_device_by_id(int(device_key))
        except Exception as e:
            self.handle_exception(e)

    def set_active_tab(self, new_active_tab) -> None:
        #ui.notify(new_active_tab)
        try:
            self.active_tab = new_active_tab
        except Exception as e:
            self.handle_exception(e)

    @ui.refreshable_method
    def build_room_and_device_buttons(self) -> None:
        try:

            with ui.tabs().classes('w-full') as tabs:
                first_tab = ui.tab(name='Rooms', icon='home')
                second_tab = ui.tab(name='Devices')
                tab_dict = {
                    first_tab: second_tab,
                    second_tab: first_tab
                }
                if not self.active_tab:
                    self.set_active_tab(first_tab)
                with ui.tab_panels(tabs, value=self.active_tab
                        #,on_change=lambda i=tab_dict[self.active_tab]: self.set_active_tab(i)
                                   ).classes('w-full'):
                    with ui.tab_panel(first_tab):
                        for key, value in self.room_dict.items():
                            with ui.row():
                                with ui.button_group():
                                    ui.button(text=f'{key}',
                                              color=self.BACKGROUND_COLOR_ROOM_BUTTON,
                                              on_click=lambda i=key: self.toggle_room(i))
                                    for v in value:
                                        device_name = v[0]
                                        device_key = v[1]
                                        device_is_on = self.device_dict[device_key][2]
                                        device_is_reachable = self.device_dict[device_key][4]
                                        if device_is_on.lower() == 'true':
                                            button_color = self.BACKGROUND_COLOR_DEVICE_BUTTON_ON
                                        else:
                                            button_color = self.BACKGROUND_COLOR_DEVICE_BUTTON_OFF
                                        if device_is_reachable.lower() == 'false':
                                            button_color = self.BACKGROUND_COLOR_DEVICE_BUTTON_UNREACHABLE
                                        ui.button(text=f'{device_name}',
                                                  color=button_color,
                                                  on_click=lambda j=device_key: self.toggle_device(j))
                        ui.button(text='Refresh', on_click=self.refresh_ui_elements)
                    with ui.tab_panel(second_tab):
                        for key, dev in self.device_dict.items():
                            with ui.row():
                                device_name = dev[0]
                                device_is_on = dev[2]
                                device_is_reachable = dev[4]
                                if device_is_on.lower() == 'true':
                                    button_color = self.BACKGROUND_COLOR_DEVICE_BUTTON_ON
                                else:
                                    button_color = self.BACKGROUND_COLOR_DEVICE_BUTTON_OFF
                                if device_is_reachable.lower() == 'false':
                                    button_color = self.BACKGROUND_COLOR_DEVICE_BUTTON_UNREACHABLE
                                ui.button(text=f'{device_name}',
                                          color=button_color,
                                          on_click=lambda j=key: self.toggle_device(j))
        except Exception as e:
            self.handle_exception(f"test {e}")


    def refresh_device_and_room_dicts(self) -> None:
        try:
            device_dict = self.backend.get_device_dictionary()
            self.device_dict = {k: device_dict[k] for k in sorted(device_dict)}
            room_dict = self.backend.get_room_dictionary()
            self.room_dict = {k: room_dict[k] for k in sorted(room_dict)}
        except Exception as e:
            self.handle_exception(f"test {e}")

    def refresh_ui_elements(self) -> None:
        """
        This refreshes the dictionaries fetched from the backend and refreshes all ui elements which are
        build using build_room_and_device_buttons.
        This is triggered every POLL_RATE_IN_S seconds.
        :return None:
        """
        try:
            self.build_room_and_device_buttons.refresh()
        except Exception as e:
            self.handle_exception(f"test {e}")


if __name__ in ("__mp_main__"):
    pass
    # "__mp_main__" is needed to allow for multiprocessing which is needed in NiceGUI
    # this will be triggered twice. once by running this skript and once by ui.run() i think because ui.run() spawns a subprocess
ui_instance = UI()
