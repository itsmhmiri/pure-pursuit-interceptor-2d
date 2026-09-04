import math

class MovingTarget:
    def __init__(self, x:float, y:float, vx:float, vy:float):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def step(self, dt:float):
        self.x += self.vx * dt
        self.y += self.vy * dt

class ConstrainedMissile:
    def __init__(self, x:float, y:float, speed:float, max_turn_deg:float = 30):
        self.x = x
        self.y = y
        self.speed = speed
        self.heading_deg = 0.0
        self.max_turn_deg = math.radians(max_turn_deg)

    def distance(self, target:MovingTarget) -> float:
        # calculating the distance between target and interceptor
        return math.hypot((target.x -self.x), (target.y - self.y))

    def step(self, target:MovingTarget, dt:float) -> float:
        dx = target.x - self.x
        dy = target.y - self.y
        
        # calculating line-of-sight (LOS)
        los = math.atan2(dy, dx)

        # calculating angle difference between LOS and current angle (heading_deg)
        angle_diff = (los - self.heading_deg + math.pi) % (2 * math.pi) - math.pi
        
        # calculating max possible turn in the current step
        max_turn = self.max_turn_deg * dt

        # capping the turning angle to maximum possible angle
        clamped_turn = max(-max_turn, min(max_turn, angle_diff))
        self.heading_deg += clamped_turn

        # heading toward the target with calculated LOS and speed
        self.x += math.cos(self.heading_deg) * self.speed * dt
        self.y += math.sin(self.heading_deg) * self.speed * dt

        # calculating distance after moving
        return self.distance(target)


if __name__ == '__main__':
    dt = 0.01
    target = MovingTarget(1200, 500, 80, -20)
    missile = ConstrainedMissile(0, 0, 200, 30)
    hit_radius = 1.0
    t = 0.0
    hit = False

    while t < 15.00:
        target.step(dt)
        d = missile.step(target, dt)
        if d < hit_radius:
            hit = True
            print(f"Target got intercepted in {t//dt} steps")
            break
        print(f"distance: {d:.4f}  |  tick: {t:.2f}  |  missile angle: {math.degrees(missile.heading_deg):.2f}")
        t += dt
    
    if not hit:
        print("target was not intercepted")
