import glob
import os
import sys
import argparse
from world import World
import coloredlogs, logging

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

def game_loop(args):
    try:
        world = World(args)
        if args.weather is not None:            
            world.set_weather(args.weather)
        if args.list:
            world.list_options()        
        
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
        '--rolename',
        metavar='NAME',
        default='hero',
        help='actor role name (default: "hero")')
    
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