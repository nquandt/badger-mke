# Milwaukee Tool logo for the GitHub Universe badge: a procedural, never-quite-repeating cycle.
# Each cycle randomly composes an entrance, a hold with glitch bursts, and an exit.
# Left/Right = screens (logo, product cards, level), Down = QR, Select = context action,
# Up = play/pause, Back = close QR / go home / exit.
import math
import random
from array import array

import missing_details

badge.mode(HIRES | VSYNC)
previous_clear = badge.default_clear
badge.default_clear = None
screen.antialias = image.X2
screen.fill_rule = image.NON_ZERO

LOGO_W = __W__
# 0: registered mark, 1: lightning bolt, 2-3: "Milwaukee" lettering
LOGO = __DATA__

# (image slug, name, category, SKU) for the product cards; the QR links to milwaukeetool.com/products/<SKU>
PRODUCTS = __PRODUCTS__
PRODUCT_DIR = "/system/apps/milwaukee/products/"
ROLE = "Staff Software Engineer"

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


# ---- UI layer: animated logo, product cards, level; QR overlays ----

title_font = font.ignore
body_font = missing_details.mona_sans()
GRAY = (95, 95, 95)

LEVEL = len(PRODUCTS) + 1      # screens: 0 logo, 1..n product cards, n+1 level
SCREEN_COUNT = LEVEL + 1
TRANS_MS = 420
IDLE_MS = 25000                # return to the logo after this long without a button press
IDLE_QR_MS = 60000
HINT_MS = 3000
ICON_MS = 1200
LEVEL_SX = 1                   # flip to -1 if the bubble moves the wrong way
LEVEL_SY = 1


def setting_or(key, default):
    try:
        value = setting(key)
        return value if value else default
    except Exception:
        return default


def measure(text, size=None):
    return screen.measure_text(text, font_size=size) if size else screen.measure_text(text)


def fit(text, width, size=None):
    while text and measure(text, size)[0] > width:
        text = text[:-1]
    return text


def put(text, x, y, rgb, a=1.0, size=None, face=None):
    screen.font = face or body_font
    screen.pen = pen(rgb, a)
    if size:
        screen.text(text, x, y, size)
    else:
        screen.text(text, x, y)


def put_centred(text, y, rgb, a=1.0, size=None, face=None, maxw=300):
    screen.font = face or body_font
    text = fit(text, maxw, size)
    width, _ = measure(text, size)
    put(text, (WIDTH - width) / 2, y, rgb, a, size, face)


def logo_at(cx, cy, width, rgb, a=1.0):
    k = width / LOGO_W
    for p in (WA, WB, BOLT, MARK):
        p.transform = mat3().translate(vec2(cx, cy)).scale(k, k)
        screen.pen = pen(rgb, a)
        screen.shape(p)


_images = {}


def product_image(slug):
    if slug not in _images:
        try:
            _images[slug] = image.load(PRODUCT_DIR + slug + ".png")
        except Exception:
            _images[slug] = None
    return _images[slug]


def hint(text, a):
    if a > 0:
        put_centred(text, 226, W, a * .75, 11)


def draw_card(i, hint_a):
    slug, name, cat, sku = PRODUCTS[i]
    fill(R)
    logo_at(46, 17, 72, W)
    for k in range(len(PRODUCTS)):
        screen.pen = pen(W, 1.0 if k == i else .45)
        screen.shape(shape.circle(WIDTH - 14 - (len(PRODUCTS) - 1 - k) * 12, 17, 4 if k == i else 3))
    screen.pen = pen(W)
    screen.shape(shape.rounded_rectangle(14, 34, 292, 142, 10))
    im = product_image(slug)
    if im is not None:
        x = 160 - im.width // 2
        y = 105 - im.height // 2
        screen.blit(im, rect(0, 0, im.width, im.height), rect(x, y, im.width, im.height))
    else:
        put_centred(name, 96, GRAY, size=14)
    screen.font = title_font
    put(fit(name, 292), 14, 176, W, face=title_font)
    put(fit(cat, 292, 14), 14, 205, W, .88, 14)
    hint("< > browse     ^ v QR     SEL home", hint_a)


def draw_qr(title, sub, url, tag):
    fill(W)
    q = image.qr(url, image.QR_LOW, 2)
    scale = max(1, 166 // q.width)
    size = q.width * scale
    screen.blit(q, rect(0, 0, q.width, q.height), rect((WIDTH - size) // 2, 6 + (166 - size) // 2, size, size))
    put_centred(title, 176, K, face=title_font)
    put_centred(sub, 205, GRAY, size=13)
    put_centred(tag, 222, (140, 140, 140), size=10)
    screen.pen = pen(R)
    screen.shape(shape.rectangle(0, HEIGHT - 6, WIDTH, 6))


def draw_contact_qr():
    li = contact_qr == 0
    handle = setting_or("CONTACT_LINKEDIN" if li else "GITHUB_USERNAME", "nquandt")
    url = ("https://www.linkedin.com/in/" if li else "https://github.com/") + handle
    draw_qr(setting_or("CONTACT_NAME", "Nicholas Quandt"), ROLE, url,
            ("LinkedIn" if li else "GitHub") + " - " + handle + "     < > switch")


def draw_product_qr(i):
    slug, name, cat, sku = PRODUCTS[i]
    draw_qr(name, cat, "https://www.milwaukeetool.com/products/" + sku, "milwaukeetool.com/products/" + sku + "     SELECT closes")


tilt_x = tilt_y = 0.0
zero_x = zero_y = 0.0


def read_tilt():
    global tilt_x, tilt_y
    ax, ay, az = badge.imu()[:3]
    g = math.sqrt(ax * ax + ay * ay + az * az) or 1.0
    rx = math.degrees(math.asin(max(-1.0, min(1.0, ax / g))))
    ry = math.degrees(math.asin(max(-1.0, min(1.0, ay / g))))
    tilt_x += (rx - tilt_x) * .25
    tilt_y += (ry - tilt_y) * .25


def draw_level(hint_a):
    read_tilt()
    dx = (tilt_x - zero_x) * LEVEL_SX
    dy = (tilt_y - zero_y) * LEVEL_SY
    ang = math.sqrt(dx * dx + dy * dy)
    level = ang < 1.0
    fill(R)
    cx, cy, rad = 160, 100, 68
    screen.pen = pen(W)
    screen.shape(shape.stroke(shape.circle(cx, cy, rad), 3))
    screen.pen = pen(W, .45)
    screen.shape(shape.stroke(shape.circle(cx, cy, rad // 2), 1.5))
    screen.shape(shape.rectangle(cx - rad, cy, rad * 2, 1))
    screen.shape(shape.rectangle(cx, cy - rad, 1, rad * 2))
    screen.pen = pen(W)
    screen.shape(shape.stroke(shape.circle(cx, cy, 16), 3))
    reach = rad - 14
    bx, by = cx + dx / 25 * reach, cy + dy / 25 * reach
    d = math.sqrt((bx - cx) ** 2 + (by - cy) ** 2)
    if d > reach:
        bx, by = cx + (bx - cx) * reach / d, cy + (by - cy) * reach / d
    screen.pen = pen(Y if level else W, .95)
    screen.shape(shape.circle(bx, by, 12))
    put_centred("%.1f" % ang, cy + rad + 12, W, face=title_font)
    put_centred("LEVEL" if level else "TILT", cy + rad + 42, W, .9, 12)
    logo_at(46, 17, 72, W)
    hint("< > browse     ^ zero     SEL home", hint_a)


def draw_logo_screen(now, hint_a):
    global cycle, current, cycle_start
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
    hint("< > browse   v contact QR   ^ pause   SEL exit", hint_a)


def draw_screen(idx, now, hint_a):
    if qr_open and idx == 0:
        draw_contact_qr()
    elif qr_open and 1 <= idx <= len(PRODUCTS):
        draw_product_qr(idx - 1)
    elif idx == 0:
        draw_logo_screen(now, hint_a)
    elif idx == LEVEL:
        draw_level(hint_a)
    else:
        draw_card(idx - 1, hint_a)


def band(p):
    """Red slanted wipe: covers the old screen left to right, then uncovers the new one."""
    far = WIDTH + 90
    if p < .5:
        a, b = -90, -90 + (far + 90) * ease_out(p / .5)
        lead_edge = b
    else:
        a, b = -90 + (far + 90) * ease_out((p - .5) / .5), far
        lead_edge = a
    poly(R, a + 30, 0, b + 30, 0, b - 30, HEIGHT, a - 30, HEIGHT)
    screen.pen = pen(W, .9)
    screen.shape(shape.custom(array("f", (lead_edge + 30, 0, lead_edge + 36, 0, lead_edge - 24, HEIGHT, lead_edge - 30, HEIGHT))))


cycle = 0
current = make_plan(0, None)
cycle_start = badge.ticks

paused = False
icon_kind = 0       # 1 = pause bars, 2 = play triangle
icon_until = 0

screen_idx = 0
qr_open = False
contact_qr = 0      # 0 = LinkedIn, 1 = GitHub
trans = None        # (start_ms, target_idx)
last_input = badge.ticks
hint_until = 0


def pressed(name):
    return badge.pressed(BUTTONS[name])


BUTTONS = {"up": BUTTON_UP, "down": BUTTON_DOWN, "left": BUTTON_LEFT, "right": BUTTON_RIGHT,
           "select": BUTTON_SELECT}


def start_logo(now):
    """Arriving back at the logo: continue with the logo already up (start of a hold)."""
    global cycle, current, cycle_start
    cycle += 1
    current = make_plan(cycle, current)
    cycle_start = now - current[3]


def go(target, now):
    global trans, qr_open
    qr_open = False
    trans = (now, target)


def toggle_pause(now):
    global paused, cycle_start, icon_kind, icon_until
    if paused:
        paused = False
        start_logo(now)
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


def handle_input(now):
    """Five buttons: Up, Down, Left, Right, Select. Select doubles as back and, on the logo, exits."""
    global qr_open, contact_qr, zero_x, zero_y, last_input, hint_until
    if any(pressed(n) for n in BUTTONS):
        last_input = now
        hint_until = now + HINT_MS
    if pressed("select"):
        if qr_open:
            qr_open = False
        elif screen_idx != 0:
            go(0, now)
        else:
            reset()
    elif pressed("left") or pressed("right"):
        step = -1 if pressed("left") else 1
        if not qr_open:
            go((screen_idx + step) % SCREEN_COUNT, now)
        elif screen_idx == 0:
            contact_qr ^= 1
    elif pressed("down"):
        if screen_idx != LEVEL:
            qr_open = not qr_open
            contact_qr = 0
    elif pressed("up"):
        if screen_idx == 0 and not qr_open:
            toggle_pause(now)
        elif screen_idx == LEVEL:
            zero_x, zero_y = tilt_x, tilt_y
        elif 1 <= screen_idx <= len(PRODUCTS):
            qr_open = not qr_open
    elif screen_idx != 0 or qr_open:
        limit = IDLE_QR_MS if qr_open else IDLE_MS
        if now - last_input > limit:
            go(0, now)


def update():
    global trans, screen_idx
    now = badge.ticks
    if trans is None:
        handle_input(now)
    hint_a = clamp((hint_until - now) / 600)
    if trans is not None:
        p = (now - trans[0]) / TRANS_MS
        if p >= .5 and screen_idx != trans[1]:
            screen_idx = trans[1]
            if screen_idx == 0 and not paused:
                start_logo(now)
        if p >= 1:
            trans = None
            draw_screen(screen_idx, now, hint_a)
        else:
            draw_screen(screen_idx, now, hint_a)
            band(p)
    else:
        draw_screen(screen_idx, now, hint_a)


def on_exit():
    screen.antialias = image.OFF
    screen.fill_rule = image.NON_ZERO
    unclip()
    badge.default_clear = previous_clear


run(update)
