import argparse
import math
from visualizer import SimVisualizer

class Target:
    def __init__(self, x:float, y:float):
        self.x = x
        self.y = y


class Missile:
    def __init__(self, x:float, y:float, speed:float):
        self.x = x
        self.y = y
        self.speed = speed

    def distance(self, target:Target) -> float:
        # calculating the distance between target and interceptor
        return math.hypot((target.x -self.x), (target.y - self.y))

    def step(self, target:Target, dt:float) -> float:
        dx = target.x - self.x
        dy = target.y - self.y
        
        # calculating line-of-sight (LOS)
        los = math.atan2(dy, dx)

        # heading toward the target with calculated LOS and speed
        self.x += math.cos(los) * self.speed * dt
        self.y += math.sin(los) * self.speed * dt

        # calculating distance after moving
        return self.distance(target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="2D Pure Pursuit: Fixed Target")
    parser.add_argument("--web", action="store_true", help="Launch Rerun web viewer (recommended for WSL/browser)")
    parser.add_argument("--no-viz", action="store_true", help="Disable Rerun visualizer")
    args = parser.parse_args()

    dt = 0.01
    target = Target(300, 400)
    missile = Missile(0, 0, 100)
    hit_radius = 1.0
    t = 0.0
    d = missile.distance(target)

    viz = SimVisualizer("1_fixed_target", web=args.web, enabled=not args.no_viz)

    while d >= hit_radius:
        d = missile.step(target, dt)
        hit = d < hit_radius
        viz.log_step(t, missile, target, d, hit=hit)
        print(f"distance: {d:.4f}  |  step: {t:.4f}")
        t += dt

    print(f"Target got intercepted in {int(t // dt)} steps)")
    viz.finish()
