# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 13:00:09 2024

to do:
-color changing does not work yet > does only seem to work for certain rgb values and not continoues
    > either the calculation of hue only works for certain values or the lamp has a fixed set of possible colors

-fix bridget connection seeking on first startup. something is wrong with the token that gets created or something like that.


> object checks (ison isreachable. ) > auslagern in eigene func?

@author: LukasBentele
"""

import dirigera
import sys
import os
import re
from colorsys import rgb_to_hls
import config


class PykeaHomeSmart:
    """
    This class give access to various methods which allow a more user friendly access to the dirigera library.
    The class can be called as an instance or run standalone as a CLI with text based commands.
    """
    def __init__(self):
        self.__dirigera_ip_str = config.bridge_ip
        self.__token_str = config.bridge_token
        self.__light_and_outlet_dict = {}
        #self.__dirigera_ip_str = ''
        #self.__token_str = ''

        # Preliminary actions
        try:

            if not self.__dirigera_ip_str or not self.__token_str:
                self.get_bridge_token()

            self.__dirigera_hub = dirigera.Hub(
                token=self.__token_str
                , ip_address=self.__dirigera_ip_str
            )

            self.__commands = {
                'h': (self.__display_help, 'Displays the help menu.')
                , 'q': (self.__quit_program, 'Quits the program.')
                , 'cl': (self.__clear_console, 'Clears all previous output in the window.')
                , 'l': (self.display_smart_device_list,
                        'Displays all available home smart devices and their key. The key can be used to access the device in other commands.')
                ,
                'lr': (self.display_room_list, 'Displays all available rooms, the number of their devices and their names.')
                , 'lv': (self.change_light_level,
                         'Changes the light level of a light. Takes one integer parameter from 1 - 100. lv 2 100 > sets the light level of light with key 2 to 100%')
                , 't': (
                    self.toggle_device,
                    'Toggles the devices given by the key (integer) on or off. t 1 > toggles device 1 on or off.')
                , 'tr': (self.toggle_room,
                         'Toggles all devices in a given room on or off. tr arbeitszimmer > toggles device in the \'arbeitszimmer\' or off. \n \t\t\t Use optional parameter \'n\' to toggle by name: t some_device n > toggles the device named \'some_device\'.')
                , 'c': (self.change_light_color,
                        'Change the devices color. takes integer parameters key r g b between 0 - 255. c 2 255 0 0 > sets the color of device 2 to pure red.')
                , 'ct': (self.change_color_temp,
                         'Changes the color temperatur of a light. Takes one integer parameter which has to be inbetween the minimum and maximum temperatur of the light.\n \t\t\t To get the temparature range for a light, use command ctl. ct 2 3500 > sets the color temparature of light 2 to 3500 lumen.')
                , 'ctl': (self.state_light_temp_range,
                          'Displays the temprature range for a given light. ctl 2 > displays the range of the light with key 2.')
            }

            self.__light_and_outlet_dict = self.__refresh_object_dicts(self.__dirigera_hub)

        except Exception as e:
            if isinstance(e, SystemExit):
                raise
            print('99')

    def get_bridge_token(self):
        user_input_ip = input('Please enter your Dirigera bridges IP address in the format of <192.168.178.01> (without <>).')
        if not self.__check_if_ip_in_valid_format(user_input_ip):
            print('The IP address provided is not in the correct format, please rerun the command and enter the IP address in the correct format.\n '
                  'A new window will open, please follow the instructions in that window and copy the token you get at the end. You will be asked to then reinsert the token here.')
        self.__dirigera_ip_str = user_input_ip

        # 192.168.178.27
        command_base = 'generate-token '
        command_ip = user_input_ip
        command = command_base + command_ip
        command_and_pause = command + " & echo Please copy the token before proceeding. You will be tasked to reenter it in the next step. & pause"

        try:
            os.system(command_and_pause)
        except Exception as e:
            print('Error: &s' % e)
            print("Something went wrong, please try again.")
            self.get_bridge_token()

        self.__token_str = input('Please copy the token just given to you here and confirm it by pressing enter.')
        return


    def __check_if_ip_in_valid_format(self, ip: str):
        # Regular expression pattern for IPv4 address
        ipv4_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'

        # Check if the IP matches the IPv4 pattern
        if re.match(ipv4_pattern, ip):
            # Check if each octet is in the valid range (0-255)
            octets = ip.split('.')
            for octet in octets:
                if not 0 <= int(octet) <= 255:
                    return False
            return True
        else:
            return False

    def __convert_list_to_dict(self, lst):
        result_dict = {}
        for i in range(0, len(lst)):
            result_dict[i + 1] = lst[i]
        return result_dict

    def get_device_by_custom_name(self, name: str):
        #global light_and_outlet_dict
        for dev in self.__light_and_outlet_dict.values():
            if dev.attributes.custom_name.lower() == name:
                return dev
        raise

    def __clear_console(self):
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')
        print('Welcome to the PyKEA home smart console. Enter a cmd or enter h to get a list of commands.')
        return

    @staticmethod
    def __quit_program():
        print('0')
        sys.exit(0)

    def __display_help(self):
        for key, val in self.__commands.items():
            print("{:<10} {:<100}".format(
                str(key) + ':',
                val[1]))

    def change_light_level(self, obj_key, level):
        """
        Changes the light level of the device if it supports light level changes.
        :param obj_key: Device key of the device dictionary. integer
        :param level: integer between 1 and 100 > 1%-100%
        :return: None
        """
        if not isinstance(level, int):
            level = int(level)
        if not (1 <= level <= 100):
            print('The light level must be between (including) 1 and 100.')
            return

        try:
            obj = self.__light_and_outlet_dict[int(obj_key)]
        except:
            print('The device key invalid. Check list to see all available devices.')
            return
        if not obj.is_reachable:
            print('The device not reachable. Please make sure the device is powered on.')
            return
        if not obj.attributes.is_on:
            print('The device not turned on. The hue will be changed anyhow.')
        if 'lightLevel' not in obj.capabilities.can_receive:
            print('The device does not support light level changes.')
            return
        self.__dirigera_hub.get_light_by_id(obj.id).set_light_level(level)
        return

    def state_light_temp_range(self, obj_key):
        """
        Returns the minimum, maximum and current color temperature of the device if the device supports it.
        :param obj_key: Device key of the device dictionary. integer
        :return: returns list [t_min, t_max, t_cur]
        """

        try:
            obj = self.__light_and_outlet_dict[int(obj_key)]
            name = obj.attributes.custom_name
        except:
            print('The device key invalid. Check list to see all available devices.')
            return
        if 'colorTemperature' not in obj.capabilities.can_receive:
            print('The device does not support color temperature changes.')
            return
        t_min = self.__dirigera_hub.get_light_by_id(obj.id).attributes.color_temperature_max
        t_max = self.__dirigera_hub.get_light_by_id(obj.id).attributes.color_temperature_min
        t_cur = self.__dirigera_hub.get_light_by_id(obj.id).attributes.color_temperature
        print('The temperature range for %s (key %s) is %s - %s lumen. '
              'Currently the temperature is %s lumen.' % (name, obj_key, t_min, t_max, t_cur))
        if not obj.attributes.is_on:
            print('The device is not turned on. The temperature can only be changed if the device is turned on.')
            return
        if not obj.is_reachable:
            print('The device is currently not reachable. Please make sure the device is powered on.')
            return [int(t_min), int(t_max), int(t_cur)]

    def change_color_temp(self, obj_key, temp):
        """
        Changes the color temperature if the device supports it.
        :param obj_key: Device key of the device dictionary. integer
        :param temp: target color temperature
        :return: None
        """
        if not isinstance(temp, int):
            temp = int(temp)

        try:
            obj = self.__light_and_outlet_dict[int(obj_key)]
        except:
            print('The device key invalid. Check list to see all available devices.')
            return
        if not obj.is_reachable:
            print('The device not reachable. Please make sure the device is powered on.')
            return
        if not obj.attributes.is_on:
            print('The device is not turned on. The temperature will not be changed.')
            return
        if 'colorTemperature' not in obj.capabilities.can_receive:
            print('The device does not support color temparature changes.')
            return
        t_min = self.__dirigera_hub.get_light_by_id(obj.id).attributes.color_temperature_max
        t_max = self.__dirigera_hub.get_light_by_id(obj.id).attributes.color_temperature_min

        if not (t_min <= temp <= t_max):
            print('The specified temparature is out of the devices range. The range is %s - %s' % (t_min, t_max))

        self.__dirigera_hub.get_light_by_id(obj.id).set_color_temperature(temp)
        return

    def change_light_color(self, obj_key, r: int, g: int, b: int):
        """
        Changes the light color of the device if the device supports it.
        :param obj_key: Device key of the device dictionary. integer
        :param r: Red value, 0 - 255, integer
        :param g: Green value, 0 - 255, integer
        :param b: Blue value, 0 - 255, integer
        :return: None
        """
        r = int(r)
        g = int(g)
        b = int(b)
        if not (isinstance(r, int) and isinstance(g, int) and isinstance(b, int)
                and (0 <= r <= 255) and (0 <= g <= 255) and (0 <= b <= 255)):
            raise TypeError('Red, green and blue values must be integers between 0 and 255.')
        try:
            obj = self.__light_and_outlet_dict[int(obj_key)]
        except:
            print('The device key invalid. Check list to see all available devices.')
            return
        if not obj.is_reachable:
            print('The device not reachable. Please make sure the device is powered on.')
            return
        if not obj.attributes.is_on:
            print('The device is not turned on. The hue will not be changed.')
            return
        if 'colorHue' not in obj.capabilities.can_receive and 'colorSaturation' not in obj.capabilities.can_receive:
            print('The device does not support color changes.')
            return

        # print('hue: ' + str(dirigera_hub.get_light_by_id('54aef854-c8f0-4754-8ff2-adcf30c9fffc_1').attributes.color_hue))
        # print('sat: ' + str(dirigera_hub.get_light_by_id('54aef854-c8f0-4754-8ff2-adcf30c9fffc_1').attributes.color_saturation))
        # print('temp: ' + str(dirigera_hub.get_light_by_id('54aef854-c8f0-4754-8ff2-adcf30c9fffc_1').attributes.color_temperature))
        # hue_normalized = dirigera_hub.get_light_by_id('54aef854-c8f0-4754-8ff2-adcf30c9fffc_1').attributes.color_hue / 360
        # sat = dirigera_hub.get_light_by_id('54aef854-c8f0-4754-8ff2-adcf30c9fffc_1').attributes.color_saturation
        # r, g, b = colorsys.hls_to_rgb(hue_normalized, 0.5, float(sat))
        # Convert RGB values to 0-255 range
        # r = int(r * 255)
        # g = int(g * 255)
        # b = int(b * 255)
        # print(str(r) + ' ' + str(g) + ' ' + str(b))

        new_hue, new_lum, new_sat = rgb_to_hls(int(r) / 360, int(g) / 360, int(b) / 360)
        # print(str(new_hue))
        # print(str(new_lum))
        # print(str(new_sat))
        self.__dirigera_hub.get_light_by_id(obj.id).set_light_color(hue=new_hue, saturation=new_sat)
        return

    def toggle_room(self, room: str):
        """
        Toggles all devices in the given room on or off.
        :param room: Room by name, string. Case-insensitive
        :return: None
        """
        if not (isinstance(room, str)):
            raise TypeError('Room must be of type string.')

        room = room.lower()
        rooms = list(set(obj.room.name.lower() for obj in self.__light_and_outlet_dict.values()))
        if room not in rooms:
            print('The room \'%s\' does not exist. Available rooms: %s.' % (room, rooms))
            return

        for obj in self.__light_and_outlet_dict.values():
            if obj.room.name.lower() == room:
                object_is_on_state = obj.attributes.is_on

                if obj.type == 'light':
                    self.__dirigera_hub.get_light_by_id(obj.id).set_light(lamp_on=not object_is_on_state)
                elif obj.type == 'outlet':
                    self.__dirigera_hub.get_outlet_by_id(obj.id).set_on(outlet_on=not object_is_on_state)
        return


    def display_room_list(self):
        """
        Displays a list of all rooms and devices in those rooms.
        :return: room_device_list > [room, [device_name, device_key]]
        """
        room_names = list(set(obj.room.name.lower() for obj in self.__light_and_outlet_dict.values()))
        room_devices = {room: [] for room in room_names}
        for key, device in self.__light_and_outlet_dict.items():
            room_devices[device.room.name.lower()].append(device.attributes.custom_name + '|' + str(key))

        room_devices_list = []
        print('Available rooms and devices:')
        for room, devices in room_devices.items():
            device_list = []

            for device in devices:
                name, key = device.split('|')
                device_list.append('%s (Key %s)' % (name, key))
            print('{:<20} {:<20}'.format(
                '%s : ' % room
                , '%s' % (', '.join(device_list))
            ))
            room_devices_list.append((str(room), device_list))

        return room_devices_list


    def display_smart_device_list(self):
        """
        Displays a list of all devices, their key, their custom name, their room, their isOn state, their type, if they are reachable and their bridge ID.
        :return: object_list [key, name, room, isOn, type, is_reachable, ID]
        """
        object_list = []
        print('#### Homesmart devices ####')
        for key, val in self.__light_and_outlet_dict.items():
            print("{:<8}  {:<25} {:<25} {:<15} {:<15} {:<20}".format(
                'Key: ' + str(key)
                , ' | Name: ' + val.attributes.custom_name
                , '  | Room: ' + val.room.name
                , ' | Is On: ' + str(val.attributes.is_on)
                , ' | Type: ' + str(val.type)
                , '  | Reachable: ' + str(val.is_reachable)
                # , ' | Id: ' + val.id
            )
            )
            object_list.append([str(key), str(val.attributes.custom_name), str(val.room.name), str(val.attributes.is_on), str(val.type), str(val.is_reachable), str(val.id)])
        print('  ')
        return object_list

    def toggle_device(self, obj_key, mode=None):
        """
        Toggles a device on or off.
        :param obj_key: Device key of the device dictionary. integer
        :param mode: Optional - "n" for name mode > allows to toggle the object by name instead of by code.
        :return: None
        """
        try:
            if not mode:
                obj = self.__light_and_outlet_dict[int(obj_key)]
            elif mode == 'n':
                obj = self.get_device_by_custom_name(str(obj_key).lower())
        except:
            print('Device key or name is invalid. Check device list to see all available devices.')
            return

        if not obj.is_reachable:
            print('Device not reachable. Please make sure the device is powered on.')
            return

        object_is_on_state = obj.attributes.is_on

        if obj.type == 'light':
            self.__dirigera_hub.get_light_by_id(obj.id).set_light(lamp_on=not object_is_on_state)
        elif obj.type == 'outlet':
            self.__dirigera_hub.get_outlet_by_id(obj.id).set_on(outlet_on=not object_is_on_state)
        return

    def __refresh_object_dicts(self, hub):
        light_list = []
        outlet_list = []

        for light in hub.get_lights():
            light_list.append(light)

        for outlet in hub.get_outlets():
            outlet_list.append(outlet)

        light_and_outlet_list = light_list + outlet_list
        light_and_outlet_list_sorted = sorted(light_and_outlet_list, key=lambda x: x.room.name)
        self.__light_and_outlet_dict = self.__convert_list_to_dict(light_and_outlet_list_sorted)
        return

    def __main(self):
        try:
            print('Welcome to the PyKEA home smart console. Enter a cmd or enter h to get a list of commands.')

            while True:
                global light_and_outlet_dict
                self.__refresh_object_dicts(self.__dirigera_hub)

                user_input = input('').strip().lower()
                user_input_parts = user_input.split(' ', 1)

                command = user_input_parts[0]

                parameters = user_input_parts[1].split(' ') if len(user_input_parts) > 1 else None

                try:
                    if command in self.__commands:
                        if parameters:
                            if len(parameters) == 1:
                                self.__commands[command][0](parameters[0])
                            if len(parameters) == 2:
                                self.__commands[command][0](parameters[0], parameters[1])
                            if len(parameters) == 3:
                                self.__commands[command][0](parameters[0], parameters[1], parameters[2])
                            if len(parameters) == 4:
                                self.__commands[command][0](parameters[0], parameters[1], parameters[2], parameters[3])
                        else:
                            self.__commands[command][0]()
                    else:
                        print('Command not found.')
                    print('\n')
                except Exception as e:
                    print(e)
        except Exception as e:
            if isinstance(e, SystemExit):
                raise
            print(e)


if __name__ == "__main__":
    instance = PykeaHomeSmart()
    instance._PykeaHomeSmart__main()
