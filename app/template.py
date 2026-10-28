# Milwaukee Tool logo for the GitHub Universe badge: a procedural, never-quite-repeating cycle.
# Each cycle randomly composes an entrance, a hold with glitch bursts, and an exit.
# Up = play/pause, Back exits.
import math
import random
from array import array

badge.mode(HIRES | VSYNC)
previous_clear = badge.default_clear
badge.default_clear = None
screen.antialias = image.X2
screen.fill_rule = image.NON_ZERO

LOGO_W = __W__
# 0: registered mark, 1: lightning bolt, 2-3: "Milwaukee" lettering
LOGO = __DATA__

WIDTH, HEIGHT = 320, 240
FIT = 276 / LOGO_W
CX, CY = WIDTH / 2, HEIGHT / 2 + 4
HALF = 138

R = (219, 1, 28)
W = (255, 255, 255)
Y = (255, 214, 0)
K = (0, 0, 0)

SPEED = 0.6          # entrance playback speed
HOLD_MS = 15000      # base hold; each cycle varies it between 0.6x and 1.4x

IN_DUR = (1750, 2000, 1700)     # virtual ms of each entrance
OUT_DUR = (1300, 1000, 900)     # real ms of each exit
BURST_W = (3, 2, 2, 2, 1.5, .6)  # tear, split, flicker, jitter, zap, invert

parts = [shape.custom(*(array("f", c) for c in part)) for part in LOGO]
MARK, BOLT, WA, WB = parts
FULL = shape.rectangle(0, 0, WIDTH, HEIGHT)
ox = oy = 0.0   # screen shake offset


def clamp(v):
    return 0.0 if v < 0 else 1.0 if v > 1 else v


def ease_out(t):
    return 1 - (1 - clamp(t)) ** 3


def ease_in(t):
    return clamp(t) ** 3


def ease_back(t):
    t = clamp(t)
    return 1 + 2.70158 * (t - 1) ** 3 + 1.70158 * (t - 1) ** 2


def prog(t, start, length):
    return clamp((t - start) / length)


def rnd(n):
    x = math.sin(n * 12.9898) * 43758.5453
    return x - math.floor(x)


def pen(rgb, a=1.0):
    return color.rgb(rgb[0], rgb[1], rgb[2], int(255 * clamp(a)))


def part(p, rgb, dx=0.0, dy=0.0, s=1.0, a=1.0, sx=None, sy=None):
    if a <= 0:
        return
    p.transform = mat3().translate(vec2(CX + dx + ox, CY + dy + oy)).scale(
        FIT * (sx if sx is not None else s), FIT * (sy if sy is not None else s))
    screen.pen = pen(rgb, a)
    screen.shape(p)


def word(rgb, **kw):
    part(WA, rgb, **kw)
    part(WB, rgb, **kw)


def everything(rgb, **kw):
    word(rgb, **kw)
    part(BOLT, rgb, **kw)
    part(MARK, rgb, **kw)


def clip_to(x, y, w, h):
    screen.clip = rect(x, y, max(w, 0), h)


def unclip():
    screen.clip = rect(0, 0, WIDTH, HEIGHT)


def fill(rgb, a=1.0):
    screen.pen = pen(rgb, a)
    screen.shape(FULL)


def box(x, y, w, h, rgb, a=1.0):
    screen.pen = pen(rgb, a)
    screen.shape(shape.rectangle(x, y, w, h))


def poly(rgb, *pts):
    screen.pen = pen(rgb)
    screen.shape(shape.custom(array("f", pts)))


def lead(p):
    return CX + (-67.5 + 135 * p) * FIT, CY + (30 - 41.3 * p) * FIT


# ---- entrances (t is virtual ms) ----

def sparks_at(t0, t, count, seed):
    age = t - t0
    if age < 0 or age > 360:
        return
    for i in range(count):
        a = rnd(i + seed) * 6.28
        sp = .05 + rnd(i + seed + 30) * .25
        lx, ly = lead(rnd(i + seed + 60))
        box(lx + math.cos(a) * sp * age, ly + math.sin(a) * sp * age, 3, 3, W if age < 110 else Y, 1 - age / 360)


def bolt_fly(e):
    d = (1 - e) * 430
    for g in (3, 2, 1):
        gg = g * 22 * (1 - e)
        part(BOLT, W, dx=-d - gg, dy=(d + gg) * .306, a=.14 * (4 - g) * (1 - e))
    part(BOLT, W, dx=-d, dy=d * .306)


def impact_in(t):
    global ox, oy
    sh = 8 * (1 - prog(t, 550, 450)) ** 2 if 550 < t < 1000 else 0
    ox = (rnd(int(t)) - .5) * sh * 2
    oy = (rnd(int(t) + 7) - .5) * sh * 2
    p = prog(t, 300, 250)
    if p > 0:
        word(W, s=3 - 2 * ease_in(p), a=p)
    if t > 550:
        k = prog(t, 550, 500)
        w = 5 * (1 - k)
        if w > 0.4:
            screen.pen = pen(W, 1 - k)
            screen.shape(shape.stroke(shape.circle(CX + ox, CY + oy, (t - 550) * .7), w))
    bp = ease_out(prog(t, 900, 350))
    if bp > 0:
        clip_to(CX - HALF + ox, 0, 276 * bp, HEIGHT)
        part(BOLT, W)
        unclip()
    for i in range(22):
        tb = 900 + i * 16
        age = t - tb
        if age < 0 or age > 450:
            continue
        lx, ly = lead(ease_out(prog(tb, 900, 350)))
        vx = (rnd(i) - .3) * .25
        vy = (rnd(i + 50) - .9) * .3
        box(lx + vx * age, ly + vy * age + age * age * .0004, 3, 3, W if age < 150 else Y, 1 - age / 450)
    if t > 1400:
        part(MARK, W, s=ease_back(prog(t, 1400, 250)))
    ox = oy = 0.0


def mask(ex, from_left):
    if from_left:
        poly(R, -60, 0, ex + 30, 0, ex - 30, HEIGHT, -60, HEIGHT)
    else:
        poly(R, ex + 30, 0, WIDTH + 60, 0, WIDTH + 60, HEIGHT, ex - 30, HEIGHT)


def edge_glow(ex):
    screen.pen = pen(W, .9)
    screen.shape(shape.custom(array("f", (ex + 30, 0, ex + 36, 0, ex - 24, HEIGHT, ex - 30, HEIGHT))))


def wipe_strike(t):
    word(W)
    w = ease_out(prog(t, 250, 900))
    ex = CX - HALF - 50 + 376 * w
    mask(ex, False)
    if 0 < w < 1:
        edge_glow(ex)
    if t > 1500:
        part(MARK, W, s=ease_back(prog(t, 1500, 250)))
    b = prog(t, 1150, 230)
    if b > 0:
        bolt_fly(ease_in(b))
    if 1380 < t < 1700:
        fill(W, .8 * (1 - prog(t, 1380, 320)))
        sparks_at(1380, t, 24, 5)


def bolt_first(t):
    b = prog(t, 0, 300)
    if 0 < b < 1:
        bolt_fly(ease_in(b))
    if t >= 300:
        part(BOLT, W)
    w = prog(t, 420, 450)
    if w > 0:
        word(W, s=1.35 - .35 * ease_back(w), a=clamp(w * 2.5))
    if t > 1000:
        part(MARK, W, s=ease_back(prog(t, 1000, 250)))
    fl = prog(t, 300, 300)
    if 0 < fl < 1:
        fill(W, .7 * (1 - fl))
        sparks_at(300, t, 16, 9)


# ---- glitch vocabulary ----

def glitch_layers(frame, seed, bands, amp, split, tear, keep=None):
    bh = HEIGHT // bands
    for i in range(bands):
        if keep is not None and not keep(i):
            continue
        off = (rnd(frame * 7 + i + seed) - .5) * amp if tear else 0
        clip_to(0, i * bh, WIDTH, bh)
        if split:
            everything((0, 229, 255), dx=off - split, a=.7)
            everything(K, dx=off + split, a=.5)
        everything(W, dx=off)
    unclip()


def burst(b, r):
    a, dur, kind, bands, seed = b
    g = 1 - (r - a) / dur
    frame = int(r // 50)
    if kind == 0:
        glitch_layers(frame, seed, bands, 70 * g, 5 * g, True)
    elif kind == 1:
        glitch_layers(frame, seed, 1, 0, 7 * g, False)
    elif kind == 2:
        everything(W, dx=(rnd(frame) - .5) * 6 * g)
        if int((r - a) // 60) % 2 == 0:
            part(BOLT, Y, s=1.04)
    elif kind == 3:
        everything(W, dx=(rnd(frame + 9) - .5) * 8 * g, dy=(rnd(frame) - .5) * 16 * g)
    elif kind == 4:
        everything(W)
        part(BOLT, Y, s=1 + .07 * g, a=.85)
        for i in range(10):
            lx, ly = lead(rnd(i + frame * 3 + seed))
            box(lx + (rnd(i + frame) - .5) * 24, ly + (rnd(i + frame + 5) - .5) * 24, 3, 3, W if i % 2 else Y, g)
    else:
        fill(W)
        everything(R)


# ---- exits (k is 0..1 across the exit) ----

def glitch_out(k, frame, n):
    glitch_layers(frame, n, 8, 40 + 170 * k, 5 + 8 * k, True,
                  lambda i: rnd(i * 5.3 + n * 2.1) > k * k * 1.1 or rnd(frame * 3 + i) < .2 * (1 - k))


def wipe_out(k):
    everything(W)
    ex = CX - HALF - 50 + 376 * ease_out(k)
    mask(ex, True)
    if k < 1:
        edge_glow(ex)
    if .1 < k < .5 and int(k * 30) % 2 == 0:
        part(BOLT, Y, a=.9)


def crt_off(k):
    k1 = clamp(k / .6)
    k2 = clamp((k - .6) / .4)
    sy = max(.02, 1 - ease_out(k1))
    sx = 1 - ease_in(k2)
    word(W, sx=sx, sy=sy)
    part(BOLT, Y if k1 > .3 else W, sx=sx, sy=sy)
    part(MARK, W, sx=sx, sy=sy)
    if k1 > .8 and k2 < 1:
        box(CX - HALF * sx, CY - 1.5, 276 * sx, 3, W, 1 - k2)


# ---- procedural plan: a fresh random composition per cycle ----

ENTRANCES = (impact_in, wipe_strike, bolt_first)


def pick(k, avoid):
    v = int(random.random() * k)
    return (v + 1) % k if v == avoid else v


def pick_burst():
    r = random.random() * sum(BURST_W)
    for i, w in enumerate(BURST_W):
        if r < w:
            return i
        r -= w
    return 0


def make_plan(n, prev):
    in_kind = pick(3, prev[1] if prev else -1)
    out_kind = pick(3, prev[2] if prev else -1)
    in_dur = IN_DUR[in_kind] / SPEED
    hold = HOLD_MS * (.6 + .8 * random.random())
    blank = 300 + random.random() * 500
    nb = max(2, int(hold // 3500))   # a burst every ~3.5s of hold
    slot = (hold - 1200) / nb
    bursts = []
    last = -1
    for j in range(nb):
        kind = pick_burst()
        if kind == last:
            kind = (kind + 1) % 5
        last = kind
        bursts.append((in_dur + 700 + j * slot + random.random() * slot * .55,
                       160 + random.random() * 340, kind, 3 + int(random.random() * 5), j * 11 + n))
    h_end = in_dur + hold
    return (n, in_kind, out_kind, in_dur, h_end, OUT_DUR[out_kind], h_end + OUT_DUR[out_kind] + blank, bursts)


def draw(plan, r):
    n, in_kind, out_kind, in_dur, h_end, out_dur, total, bursts = plan
    fill(R)
    if r < in_dur:
        ENTRANCES[in_kind](r * SPEED)
    elif r < h_end:
        for b in bursts:
            if b[0] <= r < b[0] + b[1]:
                burst(b, r)
                return
        everything(W)
    elif r < h_end + out_dur:
        k = (r - h_end) / out_dur
        if out_kind == 0:
            glitch_out(k, int(r // 50), n)
        elif out_kind == 1:
            wipe_out(k)
        else:
            crt_off(k)


cycle = 0
current = make_plan(0, None)
cycle_start = badge.ticks

# Up button: play / pause. Pause snaps to the plain logo and holds it; play resumes with the logo
# continuing into a fresh cycle (hold, glitches, exit). A small icon confirms each press.
paused = False
icon_kind = 0       # 1 = pause bars, 2 = play triangle
icon_until = 0
ICON_MS = 1200


def toggle_pause(now):
    global paused, cycle, current, cycle_start, icon_kind, icon_until
    if paused:
        paused = False
        cycle += 1
        current = make_plan(cycle, current)
        cycle_start = now - current[3]      # start at the end of the entrance: logo already up
        icon_kind = 2
    else:
        paused = True
        icon_kind = 1
    icon_until = now + ICON_MS


def draw_icon(now):
    left = icon_until - now
    if left <= 0:
        return
    screen.pen = pen(W, clamp(left / 400))
    if icon_kind == 1:
        screen.shape(shape.rectangle(286, 10, 6, 18))
        screen.shape(shape.rectangle(298, 10, 6, 18))
    else:
        screen.shape(shape.custom(array("f", (286, 10, 305, 19, 286, 28))))


def update():
    global cycle, current, cycle_start
    now = badge.ticks
    if badge.pressed(BUTTON_UP):
        toggle_pause(now)
    if paused:
        fill(R)
        everything(W)
    else:
        r = now - cycle_start
        if r >= current[6]:
            cycle_start += current[6]
            cycle += 1
            current = make_plan(cycle, current)
            r = now - cycle_start
        draw(current, r)
    draw_icon(now)


def on_exit():
    screen.antialias = image.OFF
    screen.fill_rule = image.NON_ZERO
    unclip()
    badge.default_clear = previous_clear


run(update)
