import inspect
import sys

import pykea_home_smart as phs
import os


class CLI:
    def __init__(self):
        self.bridge_api = phs.PykeaHomeSmart()
        self.device_list = []
        # __commands structure:
        # key: main command alias(es)
        # values: tuple
        #          0: function to trigger
        #          1: Help text
        #          2: optional flags
        # to call cmd use structure cmd -optional_flags argument1 argument2 ..
        self.__commands = {
            ('h', 'help'): (
                    self.display_help,
                    'Displays the help menu.'
                    ,[])
            , ('q', 'quit'): (
                    self.bridge_api.quit_program,
                    'Quits the program.'
                    ,[])
            , ('rs', 'restart'): (
                    self.bridge_api.restart_program,
                    'Restarts the program. Useful if you lost connection to your Dirigera bridge.'
                    ,[])
            , ('cl', 'clear'): (
                    self.clear_console,
                    'Clears all previous output in the window.',
                    [])
            , ('l', 'list'): (
                    self.bridge_api.get_smart_device_list,
                    'Displays all available home smart devices and their key. The key can be used to access the device in other commands.'
                    ,[])
            , ('lr', 'listroom', 'roomlist'): (
                    self.bridge_api.display_room_list,
                   'Displays all available rooms, the number of their devices and their names.',
                    [])
            , ('lv', 'slv', 'level', 'set_level'): (
                    self.bridge_api.change_light_level,
                    'Changes the light level of a light. Takes one integer parameter from 1 - 100. lv 2 100 > sets the light level of light with key 2 to 100%',
                    ['-n'])
            , ('glv', 'get_level'): (
                    self.bridge_api.get_light_level,
                    'Displays the current light level of the device if the device supports light level changes.',
                    ['-n'])
            , ('t', 'toggle'): (
                    self.toggle_device,
                    'Toggles the devices given by the key (integer) on or off. t 1 > toggles device 1 on or off.',
                    ['-n'])
            , ('tr', 'toggle_room'): (
                    self.bridge_api.toggle_room,
                    'Toggles all devices in a given room on or off. tr arbeitszimmer > toggles device in the \'arbeitszimmer\' or off. \n \t\t\t Use optional parameter \'n\' to toggle by name: t some_device n > toggles the device named \'some_device\'.'
                    ,[])
            , ('c', 'sc', 'color'): (
                    self.bridge_api.set_light_color,
                    'Change the devices color. takes integer parameters key r g b between 0 - 255. c 2 255 0 0 > sets the color of device 2 to pure red.'
                    ,['-h', '-n'])
            , ('ct','color_temp'): (
                    self.bridge_api.set_color_temp,
                    'Changes the color temperatur of a light. Takes one integer parameter which has to be inbetween the minimum and maximum temperatur of the light.\n \t\t\t To get the temparature range for a light, use command ctl. ct 2 3500 > sets the color temparature of light 2 to 3500 lumen.'
                    ,['-max', '-min', '-n'])
            , ('gct', 'get_color_temp'): (
                    self.bridge_api.get_light_color_temp_range,
                    'Displays the temprature range for a given light. ctl 2 > displays the range of the light with key 2.'
                    ,['-n'])
        }
        self.__available_commands = [item for key in self.__commands.keys() for item in key]

    def instantiate_bridge_api(self):
        self.bridge_api = phs.PykeaHomeSmart()
        self.device_list = self.bridge_api.get_smart_device_list()

    def command_parser(self, user_input: str):
        """
        This parses the user input into a runable command, optional flags and command arguments and runs the command if possible.
        Attention: args can not start with "-" or they will be interpreted as flags!
        :param user_input: string typed by user.
        :return: None
        """
        try:
            user_input_parts = user_input.split(' ', 1)
            command = user_input_parts.pop(0) #get cmd part of input and delete that from the input list
            flags = [x for x in user_input_parts if x.startswith("-")]
            args = [x for x in user_input_parts if not x.startswith("-")]

            if command not in self.__available_commands:
                raise Exception("Not a valid command, use help for a list of available commands")

            for key, value in self.__commands.items():
                if command not in key:
                    pass
                else:
                    function = value[0]
                    self.run_command(function, flags, args)
        except Exception as e:
            print(e)

    def run_command(self, function, flags: list, args: list):
        if self.has_parameter(function, "flags") and self.has_parameter(function, "args"):
            function(flags, args)
        elif self.has_parameter(function, "flags") and not self.has_parameter(function, "args"):
            function(flags)
        elif not self.has_parameter(function, "flags") and self.has_parameter(function, "args"):
            function(args)
        elif not self.has_parameter(function, "flags") and not self.has_parameter(function, "args"):
            function()

    def has_parameter(self, function, parameter_name):
        signature = inspect.signature(function)
        parameters = signature.parameters
        return parameter_name in parameters

    def quit(self):
        self.bridge_api.quit_program()
        sys.exit(0)

    def clear_console(self):
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')
        print('Welcome to the PyKEA home smart console. Enter a cmd or enter h to get a list of commands.')
        return

    def display_help(self):
        for key, val in self.__commands.items():
            print("{:<10} {:<100}".format(
                str(key) + ':',
                val[1]))

    def toggle_device(self, obj_identifier: str, flags: list):
        try:
            if "-n" in flags:
                self.bridge_api.toggle_device_by_name(obj_identifier)
            else:
                self.bridge_api.toggle_device_by_id(int(obj_identifier))
        except Exception as e:
            print("Error: " + str(e))

    def __main(self):
        try:
            print('Welcome to the PyKEA home smart console. Enter a cmd or enter h to get a list of commands.')

            while True:
                user_input = input('').strip().lower()
                self.command_parser(user_input)
                print('\n')

        except Exception as e:
            print(e)
            self.quit()



if __name__ == "__main__":
    instance = CLI()
    instance._CLI__main()