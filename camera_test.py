import glob
import os
import sys


try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(20.0)
    print(client.get_available_maps())
    world = client.load_world('Town03')
    blueprint = world.get_blueprint_library().filter("vehicle")
    print(blueprint)
    
    


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(' - Exited by user.')