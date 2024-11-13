from cProfile import Profile
from pstats import SortKey, Stats
import test as raytracer

with Profile() as profile:
    raytracer.main_loop()
    Stats(profile).strip_dirs().sort_stats(SortKey.TIME).print_stats()