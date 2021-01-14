import glob
import sys
import os
import numpy as np
import weakref
import pygame

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
from carla import ColorConverter as cc

IM_WIDTH = 1280
IM_HEIGHT = 720

class Actor(object):
    def __init__(self, world, rolename, actor, blueprint, spawn_point):
        self.role_name = rolename
        self.world = world
        self.blueprint = blueprint
        self.spawn_point = spawn_point
        self.actor = actor
        self.sensors_list = []
        self.img_sensor_data = None
        self.surface = None
        self.sensors = [
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB', {}],
            ['sensor.camera.depth', cc.Raw, 'Camera Depth (Raw)', {}],
            ['sensor.camera.depth', cc.Depth, 'Camera Depth (Gray Scale)', {}],
            ['sensor.camera.depth', cc.LogarithmicDepth, 'Camera Depth (Logarithmic Gray Scale)', {}],
            ['sensor.camera.semantic_segmentation', cc.Raw, 'Camera Semantic Segmentation (Raw)', {}],
            ['sensor.camera.semantic_segmentation', cc.CityScapesPalette,
                'Camera Semantic Segmentation (CityScapes Palette)', {}],
            ['sensor.lidar.ray_cast', None, 'Lidar (Ray-Cast)', {'range': '50'}],
            ['sensor.camera.dvs', cc.Raw, 'Dynamic Vision Sensor', {}],
            ['sensor.camera.rgb', cc.Raw, 'Camera RGB Distorted',
                {'lens_circle_multiplier': '3.0',
                'lens_circle_falloff': '3.0',
                'chromatic_aberration_intensity': '0.5',
                'chromatic_aberration_offset': '0'}]]
    
    def move_forward(self):
        self.actor.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
        
    def add_camera_sensor(self):
        cam_bp = self.world.get_blueprint_library().find(self.sensors[0][0])
        cam_bp.set_attribute("image_size_x", f"{IM_WIDTH}")
        cam_bp.set_attribute("image_size_y", f"{IM_HEIGHT}")
        cam_bp.set_attribute("fov", "110")
        
        spawn_point = carla.Transform(carla.Location(x = 2.5, z = 0.7))
        sensor = self.world.spawn_actor(cam_bp, spawn_point, attach_to = self.actor)
        self.sensors_list.append(sensor)
        weak_self = weakref.ref(self)
        sensor.listen(lambda image: Actor._parse_image(weak_self, image))    
    
    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, (0, 0))
        
    @staticmethod
    def _parse_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        image.convert(self.sensors[0][1])
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))        