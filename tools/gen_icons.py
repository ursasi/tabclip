#!/usr/bin/env python3
"""TabClip icon generator: gradient rounded square + a fan of tab cards + list lines.
No external deps. Renders at 4x and box-downsamples for anti-aliasing."""
import zlib, struct, os

SS = 4  # supersample factor


def lerp(a, b, t):
    return a + (b - a) * t


def in_round_rect(x, y, x0, y0, x1, y1, r):
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def over(dst, src):
    """alpha-composite src over dst (both (r,g,b,a))"""
    sa = src[3] / 255.0
    da = dst[3] / 255.0
    oa = sa + da * (1 - sa)
    if oa == 0:
        return (0, 0, 0, 0)
    return tuple(
        int(round((src[i] * sa + dst[i] * da * (1 - sa)) / oa)) for i in range(3)
    ) + (int(round(oa * 255)),)


def render(size):
    N = size * SS
    bg_r0, bg_g0, bg_b0 = (99, 102, 241)    # indigo-500
    bg_r1, bg_g1, bg_b1 = (147, 51, 234)    # purple-600
    corner = 0.235
    buf = [[(0, 0, 0, 0)] * N for _ in range(N)]

    for py in range(N):
        for px in range(N):
            x = px / N
            y = py / N
            col = (0, 0, 0, 0)
            c = in_round_rect(x, y, 0, 0, 1, 1, corner)
            if c:
                t = (x + y) / 2.0
                r = lerp(bg_r0, bg_r1, t)
                g = lerp(bg_g0, bg_g1, t)
                b = lerp(bg_b0, bg_b1, t)
                # soft top-left highlight
                hl = max(0.0, 1.0 - ((x - 0.22) ** 2 + (y - 0.16) ** 2) / 0.20)
                r = lerp(r, 255, hl * 0.22)
                g = lerp(g, 255, hl * 0.22)
                b = lerp(b, 255, hl * 0.22)
                col = (int(r), int(g), int(b), 255)

            # fan of cards (back to front)
            if in_round_rect(x, y, 0.40, 0.10, 0.90, 0.62, 0.075):
                col = over(col, (255, 255, 255, 95))
            if in_round_rect(x, y, 0.27, 0.19, 0.80, 0.73, 0.08):
                col = over(col, (255, 255, 255, 150))
            if in_round_rect(x, y, 0.12, 0.29, 0.67, 0.87, 0.085):
                col = over(col, (255, 255, 255, 255))

            # list lines on the front card
            lx0, lx1 = 0.215, 0.575
            lh = 0.052
            indigo = (79, 70, 229, 255)
            for i, (fy, frac) in enumerate([(0.435, 1.0), (0.565, 0.78), (0.695, 0.56)]):
                yy = fy
                if in_round_rect(x, y, lx0, yy - lh / 2, lx0 + (lx1 - lx0) * frac, yy + lh / 2, lh / 2):
                    col = over(col, indigo)
            buf[py][px] = col

    # downsample
    out = [[(0, 0, 0, 0)] * size for _ in range(size)]
    for oy in range(size):
        for ox in range(size):
            rs = gs = bs = as_ = 0
            for dy in range(SS):
                for dx in range(SS):
                    r, g, b, a = buf[oy * SS + dy][ox * SS + dx]
                    rs += r * a; gs += g * a; bs += b * a; as_ += a
            if as_ == 0:
                out[oy][ox] = (0, 0, 0, 0)
            else:
                out[oy][ox] = (rs // as_, gs // as_, bs // as_, as_ // (SS * SS))
    return out


def write_png(path, px):
    h = len(px)
    w = len(px[0])

    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(v for x in range(w) for v in px[y][x]) for y in range(h))
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(raw, 9)))
        f.write(chunk(b"IEND", b""))


if __name__ == "__main__":
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons")
    os.makedirs(outdir, exist_ok=True)
    for s in (16, 32, 48, 128, 256):
        write_png(os.path.join(outdir, f"{s}.png"), render(s))
        print("wrote", os.path.join(outdir, f"{s}.png"))
