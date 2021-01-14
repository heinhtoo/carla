#### required dependencies
- coloredlogs


#### use -m to change map
available maps:
- Town01, Town02, Town03, Town04, Town05, Town06, Town07, Town10HD.

osm or xodr maps are also available using --osm-path and -x or --xodr-path respectively.

![#f03c15](https://via.placeholder.com/15/f03c15/000000?text=+) `Can run with openstreetmap data but opening with carla doesn't support myanmar fonts.`

#### spawn npc command - filterv for vehicle blueprints flitering

available vehicles blueprints:
- vehicle.audi.a2
- vehicle.audi.etron
- vehicle.audi.tt
- vehicle.bh.crossbike
- vehicle.bmw.grandtourer
- vehicle.bmw.isetta
- vehicle.carlamotors.carlacola
- vehicle.chevrolet.impala
- vehicle.citroen.c3
- vehicle.diamondback.century
- vehicle.dodge_charger.police
- vehicle.gazelle.omafiets
- vehicle.harleydavidson.low_rider
- vehicle.jeep.wrangler_rubicon
- vehicle.kawasaki.ninja
- vehicle.lincoln.mkz2017
- vehicle.mercedes-benz.coupe
- vehicle.mini.cooperst
- vehicle.mustang.mustang
- vehicle.nissan.micra
- vehicle.nissan.patrol
- vehicle.seat.leon
- vehicle.tesla.cybertruck
- vehicle.tesla.model3
- vehicle.toyota.prius
- vehicle.volkswagen.t2
- vehicle.yamaha.yzf

-n for number of vehicles (default : 10)

-w for number of walkers (default : 50)

#### for dynamic weather, run dynamic_weather.py only to avoid collision.
for specific weather, run with -w or --weather

available weathers:
- ClearNoon
- ClearSunset
- CloudyNoon
- CloudySunset
- Default
- HardRainNoon
- HardRainSunset
- MidRainSunset
- MidRainyNoon
- SoftRainNoon
- SoftRainSunset
- WetCloudyNoon
- WetCloudySunset
- WetNoon
- WetSunset