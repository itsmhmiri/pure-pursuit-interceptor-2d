import argparse
import math
from visualizer import SimVisualizer

class MovingTarget:
    def __init__(self, x:float, y:float, vx:float, vy:float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def step(self, dt:float):
        self.x += self.vx * dt
        self.y += self.vy * dt

class Missile:
    def __init__(self, x:float, y:float, speed:float):
        self.x = x
        self.y = y
        self.speed = speed

    def distance(self, target:MovingTarget) -> float:
        # calculating the distance between target and interceptor
        return math.hypot((target.x -self.x), (target.y - self.y))

    def step(self, target:MovingTarget, dt:float) -> float:
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
    parser = argparse.ArgumentParser(description="2D Pure Pursuit: Moving Target")
    parser.add_argument("--web", action="store_true", help="Launch Rerun web viewer (recommended for WSL/browser)")
    parser.add_argument("--no-viz", action="store_true", help="Disable Rerun visualizer")
    args = parser.parse_args()

    dt = 0.01
    target = MovingTarget(1200, 500, 60, 0)
    missile = Missile(0, 0, 150)
    hit_radius = 1.0
    t = 0.0
    hit = False

    viz = SimVisualizer("2_moving_target", web=args.web, enabled=not args.no_viz)

    while t < 15.00:
        target.step(dt)
        d = missile.step(target, dt)
        if d < hit_radius:
            hit = True
            viz.log_step(t, missile, target, d, hit=True)
            print(f"Target got intercepted in {int(t // dt)} steps ({t:.2f}s)")
            break
        viz.log_step(t, missile, target, d, hit=False)
        print(f"distance: {d:.4f}  |  tick: {t:.2f}")
        t += dt
    
    if not hit:
        print("target was not intercepted")
    viz.finish()
