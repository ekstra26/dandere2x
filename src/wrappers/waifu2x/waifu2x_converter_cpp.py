"""
    This file is part of the Dandere2x project.
    Dandere2x is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    Dandere2x is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with Dandere2x.  If not, see <https://www.gnu.org/licenses/>.
""""""
========= Copyright aka_katto 2018, All rights reserved. ============
Original Author: aka_katto 
Purpose: 
 
====================================================================="""
import copy
import os
import subprocess
from threading import Thread

from context import Context
from dandere2xlib.utils.dandere2x_utils import get_lexicon_value, file_exists, \
    rename_file, wait_on_either_file_controller
from dandere2xlib.utils.yaml_utils import get_options_from_section
from ..waifu2x.abstract_upscaler import AbstractUpscaler


class Waifu2xConverterCpp(AbstractUpscaler, Thread):

    def __init__(self, context: Context):
        super().__init__(context)
        Thread.__init__(self, name="Waifu2x Converter Cpp Thread")

        # implementation specific
        self.active_waifu2x_subprocess = None

    # override
    def run(self, timeout=None) -> None:
        fix_w2x_ncnn_vulkan_names = Thread(target=self.__fix_waifu2x_converter_cpp_names,
                                           name="Waifu2x Converter CPP Fix Names")
        fix_w2x_ncnn_vulkan_names.start()
        super().run()

    # override
    def repeated_call(self) -> None:
        exec_command = copy.copy(self.upscale_command)
        console_output = open(self.context.console_output_dir + "waifu2x_converter_cpp_output.txt", "w")

        # replace the exec command with the files we're concerned with
        for x in range(len(exec_command)):
            if exec_command[x] == "[input_file]":
                exec_command[x] = self.residual_images_dir

            if exec_command[x] == "[output_file]":
                exec_command[x] = self.residual_upscaled_dir

        console_output.write(str(exec_command))
        os.chdir(self.context.waifu2x_converter_cpp_path)
        self.active_waifu2x_subprocess = subprocess.Popen(exec_command, shell=False, stderr=console_output,
                                                          stdout=console_output)
        self.active_waifu2x_subprocess.wait()

    # override
    def upscale_file(self, input_image: str, output_image: str) -> None:

        exec_command = copy.copy(self.upscale_command)
        console_output = open(self.context.console_output_dir + "waifu2x-converter-cpp-output.txt", "w")

        # replace the exec command with the files we're concerned with
        for x in range(len(exec_command)):
            if exec_command[x] == "[input_file]":
                exec_command[x] = input_image

            if exec_command[x] == "[output_file]":
                exec_command[x] = output_image

        os.chdir(self.context.waifu2x_converter_cpp_path)

        console_output.write(str(exec_command))
        self.active_waifu2x_subprocess = subprocess.Popen(exec_command, shell=False, stderr=console_output,
                                                          stdout=console_output)
        self.active_waifu2x_subprocess.wait()

    # override
    def _construct_upscale_command(self) -> list:
        waifu2x_converter_cpp_upscale_command = [self.context.waifu2x_converter_cpp_file_path,
                                                 "-i", "[input_file]",
                                                 "--noise-level", str(self.noise_level),
                                                 "--scale-ratio", str(self.scale_factor)]

        waifu2x_conv_options = get_options_from_section(self.context.config_yaml["waifu2x_converter"]["output_options"])

        # add custom options to waifu2x_vulkan
        for element in waifu2x_conv_options:
            waifu2x_converter_cpp_upscale_command.append(element)

        waifu2x_converter_cpp_upscale_command.extend(["-o", "[output_file]"])

        return waifu2x_converter_cpp_upscale_command

    # TODO, update waifu2x-conveter-cpp from legacy to newer to eliminate this subthread.
    def __fix_waifu2x_converter_cpp_names(self):
        """
            Waifu2x-Conveter-Cpp (legacy) will output the file names in a format that needs to be fixed for
            dandere2x to work. I believe this is fixed in later versions, hence the TODO
        """

        file_names = []
        for x in range(1, self.frame_count):
            file_names.append("output_" + get_lexicon_value(6, x))

        for file in file_names:
            dirty_name = self.residual_upscaled_dir + file + '_[NS-L' + str(self.noise_level) + '][x' + str(
                self.scale_factor) + '.000000]' + ".png"
            clean_name = self.residual_upscaled_dir + file + ".png"

            wait_on_either_file_controller(clean_name, dirty_name, self.controller)

            if file_exists(clean_name):
                pass

            elif file_exists(dirty_name):
                while file_exists(dirty_name):
                    try:
                        rename_file(dirty_name, clean_name)
                    except PermissionError:
                        pass
