# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 13:00:09 2024

to do:
-color changing does not work yet > does only seem to work for certain rgb values and not continoues
    > either the calculation of hue only works for certain values or the lamp has a fixed set of possible colors

-fix bridget connection seeking on first startup. something is wrong with the token that gets created or something like that.

- divide "print list" and "get list" into 2 functions (one for call as a class and one for using CLI?)

> object checks (ison isreachable.) > move into it's own function?

@author: LukasBentele
"""

import dirigera
import sys
import os
import re
from colorsys import rgb_to_hls
import config
import time
import threading


class PykeaHomeSmart:
    """
    This class give access to various methods which allow a more user friendly access to the dirigera library.
    The class can be called as an instance or run standalone as a CLI with text based commands.
    """
    def __init__(self):
        self.__dirigera_ip_str = config.bridge_ip
        self.__token_str = config.bridge_token
        self.__light_and_outlet_dict = {}

        self.__stop_event = threading.Event()
        self.__thread = threading.Thread(target=self.__refresh_loop)

        # Preliminary actions
        try:

            if not self.__dirigera_ip_str or not self.__token_str:
                self.get_bridge_token()

            self.__dirigera_hub = dirigera.Hub(
                token=self.__token_str
                , ip_address=self.__dirigera_ip_str
            )

            # Initially fill the dictionary
            self.__refresh_object_dicts(self.__dirigera_hub)
            # start the refreshing thread which keeps the dictionary up to date at all times.
            self.__start_refreshing()

        except Exception as e:
            if isinstance(e, SystemExit):
                self.__stop_refreshing()
                raise e

    def __refresh_loop(self):
        while not self.__stop_event.is_set() and self.__dirigera_hub and self.__light_and_outlet_dict:
            # Perform dictionary refresh operations here
            self.__refresh_object_dicts(self.__dirigera_hub)
            time.sleep(config.refresh_rate_in_s)  # Refresh every 1 second

    def __start_refreshing(self):
        self.__thread.start()

    def __stop_refreshing(self):
        self.__stop_event.set()
        self.__thread.join()

    def get_bridge_token(self, ip_address: str):
        """
        Currently not working!
        Function supplies the bridge token is needed to connect to the dirigera home bridge.
        :param ip_address: IP address of the bridge in the format <192.168.178.1>
        :return: token string
        """

        if not self.__check_if_ip_in_valid_format(ip_address):
            raise ValueError('The IP address provided is not in the correct format.')

        self.__dirigera_ip_str = ip_address

        # 192.168.178.27
        command_base = 'generate-token '
        command_ip = ip_address
        command = command_base + command_ip
        command_and_pause = command + " & echo Please copy the token before proceeding. You will be tasked to reenter it in the next step. & pause"

        try:
            os.system(command_and_pause)
        except Exception as e:
            raise('Error: &s' % e)

        token = 'token as string goes here'

        return token

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

    def __get_device_by_custom_name(self, name: str):
        """
        Gets a device object by its name as specified via the bridge (as opposed to getting it by the ID associated in the device dictionary).
        :param name: string, custom name of the device
        :return: device object
        """
        #global light_and_outlet_dict
        for dev in self.__light_and_outlet_dict.values():
            if dev.attributes.custom_name.lower() == name:
                return dev

    def quit_program(self):
        """Quits the app and connection to the bridge"""
        print('0')
        self.__stop_refreshing()
        sys.exit(0)

    def restart_program(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

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

    def get_light_level(self, obj_key):
        """
        States the current light level of the device if it supports light level changes.
        :param obj_key: Device key of the device dictionary. integer
        :return: return light level as an integer between 1 and 100.
        """
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
        print('The light level of device %s is %s%%.' %(str(self.__dirigera_hub.get_light_by_id(obj.id).attributes.custom_name), str(self.__dirigera_hub.get_light_by_id(obj.id).attributes.light_level)))
        return int(self.__dirigera_hub.get_light_by_id(obj.id).attributes.light_level)

    def get_light_color_temp_range(self, obj_key):
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

    def set_color_temp(self, obj_key, temp):
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
            raise Exception('The device key invalid. Check list to see all available devices.')
        if not obj.is_reachable:
            raise Exception('The device not reachable. Please make sure the device is powered on.')
        if not obj.attributes.is_on:
            raise Exception('The device is not turned on. The temperature will not be changed.')
        if 'colorTemperature' not in obj.capabilities.can_receive:
            raise Exception('The device does not support color temparature changes.')
        t_min = self.__dirigera_hub.get_light_by_id(obj.id).attributes.color_temperature_max
        t_max = self.__dirigera_hub.get_light_by_id(obj.id).attributes.color_temperature_min

        if not (t_min <= temp <= t_max):
            raise Exception('The specified temparature is out of the devices range. The range is %s - %s' % (t_min, t_max))

        self.__dirigera_hub.get_light_by_id(obj.id).set_color_temperature(temp)
        return

    def set_light_color(self, obj_key, r: int, g: int, b: int):
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
            raise Exception('The device key invalid. Check list to see all available devices.')
        if not obj.is_reachable:
            raise Exception('The device not reachable. Please make sure the device is powered on.')
        if not obj.attributes.is_on:
            raise Exception('The device is not turned on. The hue will not be changed.')
        if 'colorHue' not in obj.capabilities.can_receive and 'colorSaturation' not in obj.capabilities.can_receive:
            raise Exception('The device does not support color changes.')

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
            raise Exception('The room \'%s\' does not exist. Available rooms: %s.' % (room, rooms))

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

    def get_smart_device_list(self):
        """
        Displays a list of all devices, their key, their custom name, their room, their isOn state, their type, if they are reachable and their bridge ID.
        :return: object_list [key, name, room, isOn, type, is_reachable, ID]
        """
        object_list = []
        print('#### Homesmart devices ####')
        for key, val in self.__light_and_outlet_dict.items():
            print("{:<8}  {:<25} {:<25} {:<15} {:<15} {:<20} {:<20}".format(
                'Key: ' + str(key)
                , ' | Name: ' + val.attributes.custom_name
                , '  | Room: ' + val.room.name
                , ' | Is On: ' + str(val.attributes.is_on)
                , ' | Type: ' + str(val.type)
                , '  | Reachable: ' + str(val.is_reachable)
                , ' | Id: ' + val.id
            )
            )
            object_list.append([str(key), str(val.attributes.custom_name), str(val.room.name), str(val.attributes.is_on), str(val.type), str(val.is_reachable), str(val.id)])
        print('  ')
        return object_list

    def toggle_device_by_name(self, obj_name: str):
        """
        Toggles a device on or off.
        :param obj_name: Device name string
        :return: None
        """
        try:
            obj = self.__get_device_by_custom_name(str(obj_name).lower())
        except:
            raise Exception('Device key or name is invalid. Check device list to see all available devices.')

        if obj is None:
            raise Exception('Device not found (None).')

        if not obj.is_reachable:
            raise Exception('Device not reachable. Please make sure the device is powered on.')

        object_is_on_state = obj.attributes.is_on

        if obj.type == 'light':
            self.__dirigera_hub.get_light_by_id(obj.id).set_light(lamp_on=not object_is_on_state)
        elif obj.type == 'outlet':
            self.__dirigera_hub.get_outlet_by_id(obj.id).set_on(outlet_on=not object_is_on_state)
        return

    def toggle_device_by_id(self, obj_key: int):
        """
        Toggles a device on or off.
        :param obj_key: Device key of the device dictionary. integer
        :return: None
        """
        try:
            obj = self.__light_and_outlet_dict[int(obj_key)]
        except:
            raise Exception('Device key or name is invalid. Check device list to see all available devices.')

        if obj is None:
            raise Exception('Device not found (None).')

        if not obj.is_reachable:
            raise Exception('Device not reachable. Please make sure the device is powered on.')

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
        light_and_outlet_list_sorted = sorted(light_and_outlet_list, key=lambda x: (x.room.name, x.id))
        self.__light_and_outlet_dict = self.__convert_list_to_dict(light_and_outlet_list_sorted)
        return


if __name__ == "__main__":
    instance = PykeaHomeSmart()
