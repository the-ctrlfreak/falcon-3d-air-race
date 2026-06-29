"""
Falcon 3D Air Race
A 3D-style Python flight racing game using pygame.

Install:
    python3 -m pip install pygame

Run:
    python3 falcon_3d_air_race.py

Controls:
    W / Up Arrow       Pitch up
    S / Down Arrow     Pitch down
    A / Left Arrow     Roll left
    D / Right Arrow    Roll right
    Q / E              Rudder left/right
    Shift              Increase throttle
    Ctrl               Decrease throttle
    Space              Auto-level
    V                  Toggle camera distance
    H                  Toggle help
    R                  Restart after crash/finish
    Esc                Quit

Goal:
    Race FALCON against VIPER through all checkpoint rings.
"""

import math
import random
import sys
from dataclasses import dataclass

try:
    import pygame
except ImportError:
    print("pygame is not installed. Install with: python3 -m pip install pygame")
    sys.exit(1)

WIDTH, HEIGHT = 1280, 760
FPS = 60
FOV = 520
NEAR = 18

WHITE = (255, 255, 255)
BLACK = (4, 6, 12)
SKY_TOP = (32, 85, 180)
SKY_MID = (88, 185, 255)
SKY_LOW = (255, 190, 118)
HUD_GREEN = (70, 255, 160)
HUD_BLUE = (80, 220, 255)
HUD_RED = (255, 70, 70)
HUD_ORANGE = (255, 168, 64)
YELLOW = (255, 232, 75)
CYAN = (60, 235, 255)
MAGENTA = (255, 70, 205)
RUNWAY = (45, 47, 55)
RUNWAY_STRIPE = (245, 245, 235)
TREE_DARK = (24, 95, 48)
TREE_LIGHT = (48, 160, 78)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a * (1 - t) + b * t


def color_lerp(a, b, t):
    return (int(lerp(a[0], b[0], t)), int(lerp(a[1], b[1], t)), int(lerp(a[2], b[2], t)))


def v_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def v_len(a):
    return math.sqrt(v_dot(a, a))


def v_norm(a):
    n = v_len(a)
    if n < 0.000001:
        return (0, 0, 1)
    return (a[0] / n, a[1] / n, a[2] / n)


def angle_wrap(a):
    return (a + math.pi) % math.tau - math.pi


def forward_from_angles(yaw, pitch=0):
    cp = math.cos(pitch)
    return (math.sin(yaw) * cp, math.sin(pitch), math.cos(yaw) * cp)


def right_from_yaw(yaw):
    return (math.cos(yaw), 0, -math.sin(yaw))


def rotate_local(local, yaw, pitch, roll):
    x, y, z = local
    cr, sr = math.cos(roll), math.sin(roll)
    x, y = x * cr - y * sr, x * sr + y * cr
    cp, sp = math.cos(pitch), math.sin(pitch)
    y, z = y * cp - z * sp, y * sp + z * cp
    cy, sy = math.cos(yaw), math.sin(yaw)
    x, z = x * cy + z * sy, -x * sy + z * cy
    return (x, y, z)


@dataclass
class Aircraft:
    name: str
    x: float
    y: float
    z: float
    yaw: float = 0.0
    pitch: float = math.radians(3)
    roll: float = 0.0
    speed: float = 185.0
    vertical_speed: float = 0.0
    throttle: float = 0.62
    fuel: float = 100.0
    health: float = 100.0
    checkpoint: int = 0
    finished: bool = False
    crashed: bool = False
    score: int = 0
    stall: bool = False
    agl: float = 0.0
    warning: str = ""


@dataclass
class Checkpoint:
    x: float
    y: float
    z: float
    radius: float
    name: str


@dataclass
class Particle:
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    life: float
    max_life: float
    size: float
    color: tuple


class Falcon3DAirRace:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Falcon 3D Air Race")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20)
        self.small = pygame.font.SysFont("consolas", 15)
        self.big = pygame.font.SysFont("consolas", 46, bold=True)
        self.title = pygame.font.SysFont("consolas", 72, bold=True)
        self.label_font = pygame.font.SysFont("arial", 13, bold=True)
        self.time = 0
        self.camera_far = False
        self.show_help = True
        random.seed(20)
        self.checkpoints = self.make_checkpoints()
        self.clouds = self.make_clouds()
        self.decorations = self.make_decorations()
        self.reset()

    def reset(self):
        ground = self.terrain_height(0, -250)
        self.player = Aircraft("FALCON", 0, ground + 520, -250, yaw=0)
        self.rival = Aircraft("VIPER", -160, ground + 500, -330, yaw=0, speed=198, throttle=0.72)
        self.particles = []
        self.message = "RACE START: FALCON VS VIPER"
        self.message_timer = 4

    def make_checkpoints(self):
        data = [
            (0, 620, 900, "START GATE"),
            (360, 720, 2050, "BLUE TURN"),
            (-520, 860, 3330, "VALLEY CUT"),
            (-980, 980, 4750, "LEFT RIDGE"),
            (280, 760, 6120, "DIVE GATE"),
            (910, 1120, 7700, "MOUNTAIN PASS"),
            (150, 900, 9200, "CENTER GATE"),
            (-720, 680, 10850, "LOW SWEEP"),
            (-1160, 1180, 12450, "HIGH BANK"),
            (0, 880, 13900, "SUNSET GATE"),
            (780, 720, 15550, "RIGHT CUT"),
            (260, 640, 17150, "FINAL CHASE"),
            (0, 540, 18800, "FINISH GATE"),
        ]
        return [Checkpoint(x, y, z, 190 if i in (0, len(data) - 1) else 165, name) for i, (x, y, z, name) in enumerate(data)]

    def make_clouds(self):
        clouds = []
        for _ in range(120):
            clouds.append({
                "x": random.uniform(-5000, 5000),
                "y": random.uniform(900, 2600),
                "z": random.uniform(-1000, 22000),
                "size": random.uniform(75, 240),
                "shade": random.randint(0, 35),
            })
        return clouds

    def make_decorations(self):
        items = []
        for z in range(-900, 22500, 240):
            for side in (-1, 1):
                if random.random() < 0.68:
                    items.append(("tree", side * random.uniform(950, 3300), z, random.uniform(0.8, 1.7)))
                if random.random() < 0.13:
                    items.append(("tower", side * random.uniform(1300, 2900), z, random.uniform(0.8, 1.4)))
        return items

    def terrain_height(self, x, z):
        waves = 65 + 48 * math.sin(z * 0.0013) + 38 * math.sin((x + z) * 0.0016 + 2.1) + 22 * math.sin(z * 0.0045 + 1.7)
        side = max(0, abs(x) - 900) / 1850
        h = waves + 430 * side * side
        if 4100 < z < 6700:
            h += 230 * max(0, math.sin((z - 4100) / 2600 * math.pi))
        if 6900 < z < 10200:
            h += 350 * max(0, math.sin((z - 6900) / 3300 * math.pi))
        if 11900 < z < 15400:
            h += 270 * max(0, math.sin((z - 11900) / 3500 * math.pi))
        if -850 < z < 350 or 18100 < z < 19550:
            blend = clamp(1 - abs(x) / 450, 0, 1)
            h = h * (1 - blend) + 74 * blend
        return max(20, h)

    def camera(self):
        p = self.player
        fwd = forward_from_angles(p.yaw, clamp(p.pitch, math.radians(-15), math.radians(22)))
        distance = 740 if self.camera_far else 520
        height = 210 if self.camera_far else 155
        cam = (p.x - fwd[0] * distance, p.y - fwd[1] * distance + height, p.z - fwd[2] * distance)
        target = (p.x + fwd[0] * 850, p.y + fwd[1] * 480 + 42, p.z + fwd[2] * 850)
        cf = v_norm(v_sub(target, cam))
        cr = v_norm(v_cross(cf, (0, 1, 0)))
        cu = v_norm(v_cross(cr, cf))
        return cam, cr, cu, cf

    def project(self, point):
        cam, cr, cu, cf = self.camera()
        rel = v_sub(point, cam)
        cx, cy, cz = v_dot(rel, cr), v_dot(rel, cu), v_dot(rel, cf)
        if cz <= NEAR:
            return None
        scale = FOV / cz
        return (WIDTH / 2 + cx * scale, HEIGHT / 2 - cy * scale, cz, scale)

    def project_poly(self, points):
        out = []
        for pt in points:
            p = self.project(pt)
            if p is None:
                return None
            out.append((p[0], p[1]))
        return out

    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000, 0.033)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit()
                    if event.key == pygame.K_r and (self.player.crashed or self.player.finished):
                        self.reset()
                    if event.key == pygame.K_v:
                        self.camera_far = not self.camera_far
                    if event.key == pygame.K_h:
                        self.show_help = not self.show_help
            self.update(dt)
            self.draw()

    def quit(self):
        pygame.quit()
        sys.exit()

    def update(self, dt):
        self.time += dt
        self.message_timer = max(0, self.message_timer - dt)
        self.update_particles(dt)
        if not self.player.crashed and not self.player.finished:
            self.update_player(dt)
            self.check_checkpoint(self.player, True)
            self.check_ground(self.player, True)
            self.spawn_engine_particles(self.player, True)
        if not self.rival.finished:
            self.update_ai(dt)
            self.check_checkpoint(self.rival, False)
            self.spawn_engine_particles(self.rival, False)
        if self.rival.finished and not self.player.finished and not self.player.crashed:
            self.message = "VIPER FINISHED! PUSH FALCON TO THE FINISH!"
            self.message_timer = 2.5

    def update_player(self, dt):
        p = self.player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            p.pitch += math.radians(35) * dt
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            p.pitch -= math.radians(35) * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            p.roll -= math.radians(78) * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            p.roll += math.radians(78) * dt
        if keys[pygame.K_q]:
            p.yaw -= math.radians(42) * dt
        if keys[pygame.K_e]:
            p.yaw += math.radians(42) * dt
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            p.throttle += 0.38 * dt
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            p.throttle -= 0.38 * dt
        if keys[pygame.K_SPACE]:
            p.roll *= 0.86
            p.pitch *= 0.96
        p.pitch = clamp(p.pitch, math.radians(-32), math.radians(35))
        p.roll = clamp(p.roll, math.radians(-82), math.radians(82))
        p.throttle = clamp(p.throttle, 0, 1)
        self.apply_physics(p, dt, True)

    def apply_physics(self, p, dt, player=False):
        ground = self.terrain_height(p.x, p.z)
        p.agl = max(0, p.y - ground)
        if p.fuel <= 0:
            p.throttle = 0
        else:
            p.fuel = clamp(p.fuel - (0.06 + p.throttle * 0.20) * dt, 0, 100)
        flight_path = math.atan2(p.vertical_speed, max(p.speed, 1))
        aoa = p.pitch - flight_path
        p.stall = abs(math.degrees(aoa)) > 18 or p.speed < 82
        stall_factor = 0.42 if p.stall else 1.0
        roll_lift = max(0.10, math.cos(abs(p.roll)))
        density = clamp(math.exp(-p.y / 17500), 0.42, 1.05)
        base_lift = ((p.speed / 185) ** 2) * 30 * density
        pitch_lift = math.sin(p.pitch) * 73
        ground_effect = 9 * clamp(1 - p.agl / 150, 0, 1)
        turbulence = math.sin(self.time * 2.3 + p.z * 0.004) * 1.6
        vertical_acc = (base_lift + pitch_lift) * roll_lift * stall_factor - 30 + ground_effect + turbulence
        thrust = 49 * p.throttle
        drag = 0.00078 * p.speed * p.speed + abs(aoa) * 32 + abs(p.roll) * 3 + max(0, p.vertical_speed) * 0.026 + (10 if p.stall else 0)
        p.vertical_speed = clamp(p.vertical_speed + vertical_acc * dt, -260, 260)
        p.speed = clamp(p.speed + (thrust - drag) * dt, 50, 370)
        p.yaw = angle_wrap(p.yaw + math.sin(p.roll) * (p.speed / 520) * dt)
        p.roll *= 0.999
        if not player:
            p.pitch *= 0.995
        fwd = forward_from_angles(p.yaw, 0)
        p.x += fwd[0] * p.speed * dt
        p.z += fwd[2] * p.speed * dt
        p.y += p.vertical_speed * dt
        p.warning = ""
        if p.stall:
            p.warning = "STALL"
        if p.agl < 120:
            p.warning = "TERRAIN"
        if p.fuel < 12:
            p.warning = "LOW FUEL"
        p.score = int(max(0, p.z) / 7) + p.checkpoint * 1500

    def update_ai(self, dt):
        ai = self.rival
        if ai.checkpoint >= len(self.checkpoints):
            ai.finished = True
            return
        cp = self.checkpoints[ai.checkpoint]
        desired_yaw = math.atan2(cp.x - ai.x, cp.z - ai.z)
        diff = angle_wrap(desired_yaw - ai.yaw)
        ai.yaw += clamp(diff, -math.radians(42) * dt, math.radians(42) * dt)
        ai.roll = clamp(diff * 1.7, math.radians(-62), math.radians(62))
        ai.pitch = lerp(ai.pitch, clamp((cp.y - ai.y) / 1200, math.radians(-16), math.radians(20)), 0.035)
        ai.throttle = 0.74 + 0.10 * math.sin(self.time * 0.8)
        ai.speed += (232 - ai.speed) * 0.25 * dt
        self.apply_physics(ai, dt, False)
        ground = self.terrain_height(ai.x, ai.z)
        if ai.y < ground + 280:
            ai.y = lerp(ai.y, ground + 300, 0.05)
            ai.vertical_speed = max(ai.vertical_speed, 25)

    def check_checkpoint(self, aircraft, is_player):
        if aircraft.checkpoint >= len(self.checkpoints):
            aircraft.finished = True
            if is_player:
                self.message = "FALCON WINS THE RACE!" if not self.rival.finished else "FALCON FINISHED!"
                self.message_timer = 99
            return
        cp = self.checkpoints[aircraft.checkpoint]
        dist = math.sqrt((aircraft.x - cp.x) ** 2 + (aircraft.y - cp.y) ** 2 + (aircraft.z - cp.z) ** 2)
        if dist < cp.radius * 0.86:
            aircraft.checkpoint += 1
            aircraft.score += 1500
            if is_player:
                self.message = f"CHECKPOINT CLEARED: {cp.name}"
                self.message_timer = 2
                self.spawn_ring_burst(cp)

    def check_ground(self, aircraft, is_player):
        ground = self.terrain_height(aircraft.x, aircraft.z)
        if aircraft.y <= ground + 18:
            hard = aircraft.vertical_speed < -26 or aircraft.speed > 135 or abs(math.degrees(aircraft.roll)) > 18
            if hard:
                aircraft.crashed = True
                aircraft.health = 0
                aircraft.y = ground + 18
                self.spawn_explosion(aircraft.x, aircraft.y, aircraft.z)
                if is_player:
                    self.message = "FALCON CRASHED"
                    self.message_timer = 99
            else:
                aircraft.vertical_speed = 0
                aircraft.y = ground + 18
                aircraft.speed *= 0.90

    def spawn_engine_particles(self, a, player=True):
        if a.throttle <= 0.08 or random.random() > (0.85 if player else 0.40):
            return
        back = rotate_local((0, 0, -82), a.yaw, a.pitch, a.roll)
        pos = v_add((a.x, a.y, a.z), back)
        direction = forward_from_angles(a.yaw + math.pi, 0)
        colors = [(255, 230, 80), (255, 150, 45), (255, 70, 40)] if player else [(255, 75, 75), (255, 145, 50)]
        self.particles.append(Particle(pos[0] + random.uniform(-7, 7), pos[1] + random.uniform(-7, 7), pos[2] + random.uniform(-7, 7), direction[0] * random.uniform(70, 150) + random.uniform(-25, 25), random.uniform(-15, 30), direction[2] * random.uniform(70, 150) + random.uniform(-25, 25), random.uniform(0.25, 0.75), 0.75, random.uniform(5, 14) * a.throttle, random.choice(colors)))

    def spawn_ring_burst(self, cp):
        for _ in range(80):
            ang = random.uniform(0, math.tau)
            up = random.uniform(-1, 1)
            radius = math.sqrt(max(0, 1 - up * up))
            self.particles.append(Particle(cp.x, cp.y, cp.z, math.cos(ang) * radius * random.uniform(80, 240), up * random.uniform(80, 240), math.sin(ang) * radius * random.uniform(80, 240), random.uniform(0.5, 1.4), 1.4, random.uniform(5, 14), random.choice([YELLOW, CYAN, MAGENTA, HUD_GREEN, WHITE])))

    def spawn_explosion(self, x, y, z):
        for _ in range(160):
            ang = random.uniform(0, math.tau)
            speed = random.uniform(70, 360)
            self.particles.append(Particle(x + random.uniform(-25, 25), y + random.uniform(-15, 35), z + random.uniform(-25, 25), math.cos(ang) * speed, random.uniform(20, 260), math.sin(ang) * speed, random.uniform(0.6, 2.2), 2.2, random.uniform(7, 24), random.choice([(255, 225, 80), (255, 115, 45), (235, 45, 35), (120, 120, 120)])))

    def update_particles(self, dt):
        live = []
        for p in self.particles:
            p.life -= dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.z += p.vz * dt
            p.vy -= 35 * dt
            p.vx *= 0.986
            p.vz *= 0.986
            if p.life > 0:
                live.append(p)
        self.particles = live[-900:]

    def draw(self):
        self.draw_sky()
        self.draw_sun()
        self.draw_far_mountains()
        self.draw_terrain()
        self.draw_runways()
        self.draw_decorations()
        self.draw_clouds()
        self.draw_checkpoints()
        self.draw_particles_3d()
        self.draw_aircraft(self.rival, (245, 60, 60), (255, 180, 70))
        self.draw_aircraft(self.player, (235, 245, 255), (65, 210, 255))
        self.draw_hud()
        self.draw_messages()
        if self.player.crashed or self.player.finished:
            self.draw_end_overlay()
        pygame.display.flip()

    def draw_sky(self):
        for y in range(HEIGHT):
            t = y / HEIGHT
            c = color_lerp(SKY_TOP, SKY_MID, t / 0.56) if t < 0.56 else color_lerp(SKY_MID, SKY_LOW, (t - 0.56) / 0.44)
            pygame.draw.line(self.screen, c, (0, y), (WIDTH, y))
        for i in range(90):
            self.screen.fill(color_lerp((255, 230, 120), SKY_LOW, i / 90), (0, HEIGHT - 210 + i, WIDTH, 1))

    def draw_sun(self):
        sx, sy = WIDTH - 160, 110
        for r, c in [(86, (255, 200, 85)), (62, (255, 225, 110)), (38, (255, 248, 180))]:
            pygame.draw.circle(self.screen, c, (sx, sy), r)
        for i, r in enumerate([8, 16, 26, 12]):
            pygame.draw.circle(self.screen, (255, 240, 190), (sx - 160 - i * 105, sy + 62 + i * 38), r, 2)

    def draw_far_mountains(self):
        base_y = HEIGHT - 170
        for layer, color, amp, speed in [(0, (70, 100, 160), 110, 0.11), (1, (58, 84, 138), 150, 0.17), (2, (48, 71, 116), 190, 0.24)]:
            pts = []
            step = 95
            offset = -(self.player.z * speed) % (step * 2)
            for x in range(-200, WIDTH + 300, step):
                rng = random.Random(int((x + self.player.z * speed) // step + layer * 200))
                pts.extend([(x + offset, base_y + 100), (x + step * 0.5 + offset, base_y - layer * 36 - rng.randint(35, amp)), (x + step + offset, base_y + 100)])
            pygame.draw.polygon(self.screen, color, pts + [(WIDTH + 300, HEIGHT), (-300, HEIGHT)])

    def terrain_color(self, h, dist):
        if h > 520:
            base = (205, 210, 205)
        elif h > 330:
            base = (130, 110, 75)
        elif h > 150:
            base = (55, 138, 70)
        else:
            base = (38, 125, 64)
        return color_lerp(base, (115, 175, 210), clamp(dist / 9000, 0, 0.58))

    def draw_terrain(self):
        p = self.player
        cell_x, cell_z = 430, 430
        min_x, max_x = p.x - 3600, p.x + 3600
        min_z, max_z = p.z - 900, p.z + 9000
        x0 = math.floor(min_x / cell_x) * cell_x
        z0 = math.floor(min_z / cell_z) * cell_z
        quads = []
        z = z0
        while z < max_z:
            x = x0
            while x < max_x:
                pts = [(x, self.terrain_height(x, z), z), (x + cell_x, self.terrain_height(x + cell_x, z), z), (x + cell_x, self.terrain_height(x + cell_x, z + cell_z), z + cell_z), (x, self.terrain_height(x, z + cell_z), z + cell_z)]
                dist = math.hypot(x + cell_x / 2 - p.x, z + cell_z / 2 - p.z)
                quads.append((dist, pts, sum(pt[1] for pt in pts) / 4))
                x += cell_x
            z += cell_z
        quads.sort(reverse=True, key=lambda q: q[0])
        for dist, pts, avg_h in quads:
            poly = self.project_poly(pts)
            if poly:
                color = self.terrain_color(avg_h, dist)
                pygame.draw.polygon(self.screen, color, poly)
                if dist < 3800:
                    pygame.draw.lines(self.screen, color_lerp(color, BLACK, 0.18), True, poly, 1)

    def draw_runways(self):
        self.draw_runway(-850, 430, "START RUNWAY")
        self.draw_runway(18100, 19550, "FINISH RUNWAY")

    def draw_runway(self, z1, z2, label):
        width = 260
        corners = [(-width, self.terrain_height(-width, z1) + 5, z1), (width, self.terrain_height(width, z1) + 5, z1), (width, self.terrain_height(width, z2) + 5, z2), (-width, self.terrain_height(-width, z2) + 5, z2)]
        poly = self.project_poly(corners)
        if poly:
            pygame.draw.polygon(self.screen, RUNWAY, poly)
            pygame.draw.lines(self.screen, WHITE, True, poly, 3)
        z = z1 + 130
        while z < z2 - 130:
            stripe = [(-24, self.terrain_height(-24, z) + 8, z), (24, self.terrain_height(24, z) + 8, z), (24, self.terrain_height(24, z + 85) + 8, z + 85), (-24, self.terrain_height(-24, z + 85) + 8, z + 85)]
            sp = self.project_poly(stripe)
            if sp:
                pygame.draw.polygon(self.screen, RUNWAY_STRIPE, sp)
            z += 210
        center_z = (z1 + z2) / 2
        pt = self.project((0, self.terrain_height(0, center_z) + 42, center_z))
        if pt:
            img = self.small.render(label, True, WHITE)
            self.screen.blit(img, (pt[0] - img.get_width() / 2, pt[1]))

    def draw_decorations(self):
        pz = self.player.z
        for kind, x, z, scale in self.decorations:
            if pz - 800 < z < pz + 8500:
                g = self.terrain_height(x, z)
                if kind == "tree":
                    self.draw_tree(x, g, z, scale)
                else:
                    self.draw_tower(x, g, z, scale)

    def draw_tree(self, x, y, z, scale):
        bottom = self.project((x, y, z))
        top = self.project((x, y + 90 * scale, z))
        if not bottom or not top:
            return
        width = clamp(850 / bottom[2] * scale, 2, 16)
        pygame.draw.line(self.screen, (110, 75, 40), (bottom[0], bottom[1]), (top[0], top[1]), max(1, int(width / 2)))
        for i, color in enumerate([TREE_DARK, TREE_LIGHT]):
            crown = self.project((x, y + (78 + i * 20) * scale, z))
            if crown:
                pygame.draw.circle(self.screen, color, (int(crown[0]), int(crown[1])), int(clamp(2200 / crown[2] * scale, 5, 28)))

    def draw_tower(self, x, y, z, scale):
        base = self.project((x, y, z))
        top = self.project((x, y + 220 * scale, z))
        if not base or not top:
            return
        pygame.draw.line(self.screen, (70, 75, 86), (base[0], base[1]), (top[0], top[1]), max(2, int(1100 / base[2])))
        beacon = (255, 80, 80) if int(self.time * 3) % 2 == 0 else (110, 20, 20)
        pygame.draw.circle(self.screen, beacon, (int(top[0]), int(top[1])), max(2, int(1700 / top[2])))

    def draw_clouds(self):
        for c in self.clouds:
            z = ((c["z"] - self.player.z + 22000) % 23000) + self.player.z - 1000
            pt = self.project((c["x"], c["y"], z))
            if not pt:
                continue
            sx, sy, depth, scale = pt
            if sx < -250 or sx > WIDTH + 250 or sy < -180 or sy > HEIGHT + 180:
                continue
            size = clamp(c["size"] * scale, 8, 85)
            base, shadow = clamp(255 - c["shade"], 205, 255), clamp(220 - c["shade"], 170, 230)
            circles = [(sx, sy, size * 0.35), (sx + size * 0.40, sy - size * 0.10, size * 0.48), (sx + size * 0.82, sy + size * 0.04, size * 0.35), (sx + size * 0.46, sy + size * 0.15, size * 0.55)]
            for cx, cy, r in circles:
                pygame.draw.circle(self.screen, (shadow, shadow, shadow + 15), (int(cx + 4), int(cy + 6)), int(r))
            for cx, cy, r in circles:
                pygame.draw.circle(self.screen, (base, base, 255), (int(cx), int(cy)), int(r))

    def draw_checkpoints(self):
        for i, cp in enumerate(self.checkpoints):
            if i < self.player.checkpoint - 2:
                continue
            color = (90, 255, 130) if i < self.player.checkpoint else (YELLOW if i == self.player.checkpoint else CYAN)
            width = 6 if i == self.player.checkpoint else 3
            points = []
            r = cp.radius + (math.sin(self.time * 4 + i) * 12 if i == self.player.checkpoint else 0)
            for s in range(45):
                a = math.tau * s / 44
                proj = self.project((cp.x + math.cos(a) * r, cp.y + math.sin(a) * r, cp.z))
                if proj:
                    points.append((proj[0], proj[1]))
            if len(points) > 6:
                pygame.draw.lines(self.screen, color, False, points, width)
                if i == self.player.checkpoint:
                    pygame.draw.lines(self.screen, MAGENTA, False, points, 2)
                center = self.project((cp.x, cp.y, cp.z))
                if center:
                    img = self.small.render(cp.name, True, WHITE)
                    self.screen.blit(img, (center[0] - img.get_width() / 2, center[1] - cp.radius * center[3] - 32))

    def draw_particles_3d(self):
        for p in self.particles:
            pt = self.project((p.x, p.y, p.z))
            if not pt:
                continue
            sx, sy, depth, scale = pt
            if -80 < sx < WIDTH + 80 and -80 < sy < HEIGHT + 80:
                t = clamp(p.life / p.max_life, 0, 1)
                size = clamp(p.size * scale * 2, 1, 14) * t
                pygame.draw.circle(self.screen, color_lerp(BLACK, p.color, t), (int(sx), int(sy)), int(size))

    def aircraft_vertices(self, a):
        def wp(local):
            r = rotate_local(local, a.yaw, a.pitch, a.roll)
            return (a.x + r[0], a.y + r[1], a.z + r[2])
        return {
            "nose": wp((0, 0, 105)), "tail": wp((0, 0, -82)), "top": wp((0, 22, 10)), "bottom": wp((0, -16, 5)),
            "left_wing": wp((-120, -4, -4)), "right_wing": wp((120, -4, -4)), "left_tail": wp((-42, 5, -78)),
            "right_tail": wp((42, 5, -78)), "fin": wp((0, 64, -64)), "cockpit": wp((0, 21, 44)),
        }

    def draw_aircraft(self, a, main_color, trim_color):
        v = self.aircraft_vertices(a)
        faces = [
            ([v["tail"], v["left_wing"], v["top"], v["nose"]], color_lerp(main_color, (60, 120, 200), 0.25)),
            ([v["tail"], v["right_wing"], v["top"], v["nose"]], color_lerp(main_color, (60, 120, 200), 0.05)),
            ([v["nose"], v["top"], v["tail"], v["bottom"]], main_color),
            ([v["nose"], v["bottom"], v["tail"]], color_lerp(main_color, BLACK, 0.15)),
            ([v["tail"], v["left_tail"], v["fin"]], trim_color),
            ([v["tail"], v["right_tail"], v["fin"]], color_lerp(trim_color, BLACK, 0.1)),
        ]
        cam, _, _, _ = self.camera()
        sortable = []
        for pts, col in faces:
            center = (sum(pt[0] for pt in pts) / len(pts), sum(pt[1] for pt in pts) / len(pts), sum(pt[2] for pt in pts) / len(pts))
            sortable.append((v_len(v_sub(center, cam)), pts, col))
        sortable.sort(reverse=True)
        for _, pts, col in sortable:
            poly = self.project_poly(pts)
            if poly:
                pygame.draw.polygon(self.screen, col, poly)
                pygame.draw.lines(self.screen, BLACK, True, poly, 1)
        cockpit = self.project(v["cockpit"])
        if cockpit:
            pygame.draw.circle(self.screen, (75, 235, 255), (int(cockpit[0]), int(cockpit[1])), int(clamp(1600 / cockpit[2], 3, 12)))
        label = self.project((a.x, a.y + 82, a.z))
        if label:
            img = self.label_font.render(a.name, True, WHITE if a.name == "FALCON" else HUD_RED)
            shadow = self.label_font.render(a.name, True, BLACK)
            self.screen.blit(shadow, (label[0] - img.get_width() / 2 + 2, label[1] - 20 + 2))
            self.screen.blit(img, (label[0] - img.get_width() / 2, label[1] - 20))

    def draw_panel(self, rect, border=HUD_BLUE):
        surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        surf.fill((3, 8, 18, 158))
        self.screen.blit(surf, rect.topleft)
        pygame.draw.rect(self.screen, border, rect, 2)
        pygame.draw.line(self.screen, border, (rect.left, rect.top + 30), (rect.right, rect.top + 30), 1)

    def draw_hud(self):
        p, r = self.player, self.rival
        rect = pygame.Rect(18, 18, 372, 300)
        self.draw_panel(rect, HUD_BLUE)
        self.screen.blit(self.font.render("FALCON REALISTIC FLIGHT MODEL", True, HUD_GREEN), (rect.x + 12, rect.y + 6))
        flight_path = math.degrees(math.atan2(p.vertical_speed, max(p.speed, 1)))
        aoa = math.degrees(p.pitch) - flight_path
        rows = [("AIRCRAFT", p.name), ("AIRSPEED", f"{p.speed:6.0f} kt"), ("ALTITUDE", f"{p.y:6.0f} ft"), ("AGL", f"{p.agl:6.0f} ft"), ("VERT SPEED", f"{p.vertical_speed:6.0f} ft/s"), ("PITCH", f"{math.degrees(p.pitch):6.1f} deg"), ("ROLL", f"{math.degrees(p.roll):6.1f} deg"), ("HEADING", f"{math.degrees(p.yaw) % 360:6.0f} deg"), ("AOA", f"{aoa:6.1f} deg")]
        y = rect.y + 42
        for label, value in rows:
            self.screen.blit(self.small.render(label, True, (185, 230, 250)), (rect.x + 14, y + 4))
            self.screen.blit(self.font.render(value, True, WHITE), (rect.x + 175, y))
            y += 25
        self.draw_bar(30, 346, 270, 18, p.throttle, "THROTTLE", HUD_ORANGE)
        self.draw_bar(30, 394, 270, 18, p.fuel / 100, "FUEL", HUD_GREEN if p.fuel > 15 else HUD_RED)
        self.draw_bar(30, 442, 270, 18, p.health / 100, "AIRFRAME", HUD_GREEN if p.health > 35 else HUD_RED)
        race = pygame.Rect(WIDTH - 380, 18, 362, 210)
        self.draw_panel(race, MAGENTA)
        self.screen.blit(self.font.render("AIR RACE", True, YELLOW), (race.x + 14, race.y + 6))
        total = len(self.checkpoints)
        next_name = "FINISHED" if p.checkpoint >= total else self.checkpoints[p.checkpoint].name
        pos = "1st" if p.checkpoint > r.checkpoint or (p.checkpoint == r.checkpoint and p.z >= r.z) else "2nd"
        race_rows = [("Position", pos), ("Falcon CP", f"{p.checkpoint}/{total}"), ("Viper CP", f"{r.checkpoint}/{total}"), ("Next Gate", next_name), ("Score", f"{p.score:,}"), ("Camera", "FAR" if self.camera_far else "CHASE")]
        y = race.y + 45
        for label, value in race_rows:
            self.screen.blit(self.small.render(label, True, (220, 225, 255)), (race.x + 16, y + 4))
            self.screen.blit(self.font.render(value, True, WHITE if label != "Position" else HUD_GREEN), (race.x + 150, y))
            y += 26
        self.draw_compass()
        self.draw_radar()
        if p.warning and not p.crashed and not p.finished:
            pulse = 0.5 + 0.5 * math.sin(self.time * 8)
            warning = self.big.render(p.warning, True, color_lerp(HUD_ORANGE, HUD_RED, pulse))
            self.screen.blit(warning, (WIDTH // 2 - warning.get_width() // 2, 25))
        if self.show_help:
            self.draw_help_box()

    def draw_bar(self, x, y, w, h, value, label, color):
        value = clamp(value, 0, 1)
        self.screen.blit(self.small.render(f"{label}: {int(value * 100)}%", True, WHITE), (x, y - 21))
        pygame.draw.rect(self.screen, (5, 8, 16), (x, y, w, h), border_radius=6)
        pygame.draw.rect(self.screen, color, (x, y, int(w * value), h), border_radius=6)
        pygame.draw.rect(self.screen, WHITE, (x, y, w, h), 1, border_radius=6)

    def draw_compass(self):
        p = self.player
        cx, cy = WIDTH // 2, HEIGHT - 66
        pygame.draw.circle(self.screen, (3, 8, 16), (cx, cy), 50)
        pygame.draw.circle(self.screen, HUD_BLUE, (cx, cy), 50, 2)
        for deg in range(0, 360, 30):
            a = math.radians(deg) - p.yaw
            pygame.draw.line(self.screen, WHITE, (cx + math.sin(a) * 38, cy - math.cos(a) * 38), (cx + math.sin(a) * 47, cy - math.cos(a) * 47), 1)
        pygame.draw.polygon(self.screen, YELLOW, [(cx, cy - 43), (cx - 8, cy - 24), (cx + 8, cy - 24)])
        img = self.small.render(f"{math.degrees(p.yaw) % 360:03.0f} deg", True, WHITE)
        self.screen.blit(img, (cx - img.get_width() / 2, cy - 8))

    def draw_radar(self):
        p = self.player
        rect = pygame.Rect(WIDTH - 380, 250, 362, 150)
        self.draw_panel(rect, HUD_GREEN)
        self.screen.blit(self.small.render("RADAR / CHECKPOINT MAP", True, HUD_GREEN), (rect.x + 12, rect.y + 8))
        center = (rect.x + rect.w // 2, rect.y + 88)
        pygame.draw.circle(self.screen, (12, 24, 35), center, 54)
        pygame.draw.circle(self.screen, HUD_GREEN, center, 54, 2)
        for aircraft, color in [(self.rival, HUD_RED)]:
            rx = center[0] + clamp((aircraft.x - p.x) * 0.032, -50, 50)
            ry = center[1] - clamp((aircraft.z - p.z) * 0.032, -50, 50)
            pygame.draw.circle(self.screen, color, (int(rx), int(ry)), 5)
        if p.checkpoint < len(self.checkpoints):
            cp = self.checkpoints[p.checkpoint]
            rx = center[0] + clamp((cp.x - p.x) * 0.032, -50, 50)
            ry = center[1] - clamp((cp.z - p.z) * 0.032, -50, 50)
            pygame.draw.circle(self.screen, YELLOW, (int(rx), int(ry)), 5, 2)
        pygame.draw.polygon(self.screen, CYAN, [(center[0], center[1] - 8), (center[0] - 7, center[1] + 7), (center[0] + 7, center[1] + 7)])

    def draw_help_box(self):
        lines = ["Controls", "W/S or arrows: pitch", "A/D or arrows: roll", "Q/E: rudder yaw", "Shift/Ctrl: throttle", "Space: auto-level", "V: camera", "H: hide help"]
        rect = pygame.Rect(18, HEIGHT - 198, 285, 176)
        surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        surf.fill((255, 255, 255, 205))
        self.screen.blit(surf, rect.topleft)
        pygame.draw.rect(self.screen, BLACK, rect, 2)
        for i, line in enumerate(lines):
            self.screen.blit(self.small.render(line, True, BLACK), (rect.x + 12, rect.y + 12 + i * 20))

    def draw_messages(self):
        if self.message_timer > 0:
            img = self.big.render(self.message, True, WHITE)
            shadow = self.big.render(self.message, True, BLACK)
            x, y = WIDTH // 2 - img.get_width() // 2, 92
            self.screen.blit(shadow, (x + 3, y + 3))
            self.screen.blit(img, (x, y))

    def draw_end_overlay(self):
        p = self.player
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 166))
        self.screen.blit(overlay, (0, 0))
        if p.crashed:
            title, color, sub = "FALCON CRASHED", HUD_RED, "The airframe failed after terrain impact."
        else:
            title, color, sub = "FALCON FINISHED", HUD_GREEN, "Race complete."
        title_img = self.title.render(title, True, color)
        sub_img = self.font.render(sub, True, WHITE)
        score_img = self.font.render(f"Falcon score: {p.score:,}   Falcon checkpoints: {p.checkpoint}/{len(self.checkpoints)}   Viper checkpoints: {self.rival.checkpoint}/{len(self.checkpoints)}", True, YELLOW)
        restart_img = self.font.render("Press R to restart, Esc to quit", True, WHITE)
        self.screen.blit(title_img, title_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 105)))
        self.screen.blit(sub_img, sub_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 32)))
        self.screen.blit(score_img, score_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 16)))
        self.screen.blit(restart_img, restart_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 72)))


if __name__ == "__main__":
    Falcon3DAirRace().run()
