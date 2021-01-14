import logging
import io
import os
import sys
import glob
import re
import textwrap
from numpy import random

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
from carla import VehicleLightState as vls

SpawnActor = carla.command.SpawnActor
SetAutopilot = carla.command.SetAutopilot
SetVehicleLightState = carla.command.SetVehicleLightState
FutureActor = carla.command.FutureActor

class World(object):
    def __init__(self, args):
        self.actor_role_name = args.rolename
        self.args = args
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(float(args.timeout))        
        self.world = self.get_world()
        
    def get_world(self):
        if self.args.map is not None:
            if self.args.map in [m.replace('/Game/Carla/Maps/', '') for m in self.client.get_available_maps()]:
                logging.info('load map %r.' % self.args.map)
                world = self.client.load_world(self.args.map)        
            else:
                logging.error('map %r not found.' % self.args.map)
                logging.info('Loading current world')
                world = self.client.get_world()  
        elif self.args.xodr_path is not None:
            if os.path.exists(self.args.xodr_path):
                with io.open(self.args.xodr_path, mode='r', encoding='utf-8') as od_file:
                    try:
                        data = od_file.read()
                    except OSError:
                        print('file could not be readed.')
                        sys.exit()
                print('load opendrive map %r.' % os.path.basename(args.xodr_path))
                vertex_distance = 2.0  # in meters
                max_road_length = 500.0 # in meters
                wall_height = 1.0      # in meters
                extra_width = 0.6      # in meters
                world = self.client.generate_opendrive_world(
                    data, carla.OpendriveGenerationParameters(
                        vertex_distance=vertex_distance,
                        max_road_length=max_road_length,
                        wall_height=wall_height,
                        additional_width=extra_width,
                        smooth_junctions=True,
                        enable_mesh_visibility=True))
            else:
                logging.error('file not found.')
                exit()
        elif self.args.osm_path is not None:
            if os.path.exists(self.args.osm_path):
                with io.open(self.args.osm_path, mode='r', encoding='utf-8') as od_file:
                    try:
                        data = od_file.read()
                    except OSError:
                        print('file could not be readed.')
                        sys.exit()
                print('Converting OSM data to opendrive')
                xodr_data = carla.Osm2Odr.convert(data)
                print('load opendrive map.')
                vertex_distance = 2.0  # in meters
                max_road_length = 500.0 # in meters
                wall_height = 0.0      # in meters
                extra_width = 0.6      # in meters
                world = self.client.generate_opendrive_world(
                    xodr_data, carla.OpendriveGenerationParameters(
                        vertex_distance=vertex_distance,
                        max_road_length=max_road_length,
                        wall_height=wall_height,
                        additional_width=extra_width,
                        smooth_junctions=True,
                        enable_mesh_visibility=True))
            else:
                logging.error('file not found.')
                exit()
        else:
            world = self.client.get_world()
        return world
    
    def find_weather_presets(self):
        presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]    
        return [(getattr(carla.WeatherParameters, x), x) for x in presets]
    
    def find_vehicles_blueprints(self):
        blueprint_library = self.world.get_blueprint_library()
        blueprints = [bp.id for bp in blueprint_library.filter('vehicle.*')]    
        return blueprints
    
    def set_weather(self, weather):
        if weather is not None:
            if not hasattr(carla.WeatherParameters, weather):
                logging.error('weather preset %r not found.' % weather)
            else:
                logging.info('set weather preset %r.' % weather)
                self.world.set_weather(getattr(carla.WeatherParameters, weather))    
    
    def list_options(self):
        maps = [m.replace('/Game/Carla/Maps/', '') for m in self.client.get_available_maps()]
        indent = 4 * ' '
        def wrap(text):
            return '\n'.join(textwrap.wrap(text, initial_indent=indent, subsequent_indent=indent))
        print('weather presets:\n')
        print(wrap(', '.join(x for _, x in self.find_weather_presets())) + '.\n')
        print('available maps:\n')
        print(wrap(', '.join(sorted(maps))) + '.\n')
        print('available vehicles:\n')
        print(wrap(', '.join(sorted(self.find_vehicles_blueprints()))) + '.\n')