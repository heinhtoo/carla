import glob
import os
import sys
import argparse
import textwrap
import re
import coloredlogs, logging
import io

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

def list_options(client, world):
    maps = [m.replace('/Game/Carla/Maps/', '') for m in client.get_available_maps()]
    indent = 4 * ' '
    def wrap(text):
        return '\n'.join(textwrap.wrap(text, initial_indent=indent, subsequent_indent=indent))
    print('weather presets:\n')
    print(wrap(', '.join(x for _, x in find_weather_presets())) + '.\n')
    print('available maps:\n')
    print(wrap(', '.join(sorted(maps))) + '.\n')
    print('available vehicles:\n')
    print(wrap(', '.join(sorted(find_vehicles_blueprints(world)))) + '.\n')

def find_weather_presets():
    presets = [x for x in dir(carla.WeatherParameters) if re.match('[A-Z].+', x)]    
    return [(getattr(carla.WeatherParameters, x), x) for x in presets]

def find_vehicles_blueprints(world):
    blueprint_library = world.get_blueprint_library()
    blueprints = [bp.id for bp in blueprint_library.filter('vehicle.*')]    
    return blueprints

def game_loop(args):
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(float(args.timeout))
        
        if args.map is not None:
            if args.map in [m.replace('/Game/Carla/Maps/', '') for m in client.get_available_maps()]:
                logging.info('load map %r.' % args.map)
                world = client.load_world(args.map)        
            else:
                logging.error('map %r not found.' % args.map)
                logging.info('Loading current world')
                world = client.get_world()  
        elif args.xodr_path is not None:
            if os.path.exists(args.xodr_path):
                with io.open(args.xodr_path, mode='r', encoding='utf-8') as od_file:
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
                world = client.generate_opendrive_world(
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
        elif args.osm_path is not None:
            if os.path.exists(args.osm_path):
                with io.open(args.osm_path, mode='r', encoding='utf-8') as od_file:
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
                world = client.generate_opendrive_world(
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
            world = client.get_world()
            
        if args.weather is not None:
            if not hasattr(carla.WeatherParameters, args.weather):
                logging.error('weather preset %r not found.' % args.weather)
            else:
                logging.info('set weather preset %r.' % args.weather)
                world.set_weather(getattr(carla.WeatherParameters, args.weather))
        if args.list:
            list_options(client, world)        
    finally:
        ##! destroy all actors
        logging.info('destroy all actors')

def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    
    argparser.add_argument(
        '-m', '--map', help='load a new map, use --list to see available maps')
    
    argparser.add_argument(
        '--weather', help='set weather preset, use --list to see available presets')

    argparser.add_argument(
        '--vehicle', default='vehicle.tesla.model3', help='load vehicle (default: vehicle.tesla.model3), use --list to see available vehicles')
    
    argparser.add_argument(
        '-t', '--timeout', default='5', help='timeout (default: 5)')
    
    argparser.add_argument(
        '-x', '--xodr-path',
        metavar='XODR_FILE_PATH',
        help='load a new map with a minimum physical road representation of the provided OpenDRIVE')
    
    argparser.add_argument(
        '--osm-path',
        metavar='OSM_FILE_PATH',
        help='load a new map with a minimum physical road representation of the provided OpenStreetMaps')
    
    argparser.add_argument(
        '-l', '--list',
        action='store_true',
        help='list available options')
    
    args = argparser.parse_args()
    coloredlogs.install(level='DEBUG')
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)
    
    try:
        game_loop(args)
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(' - Exited by user.')