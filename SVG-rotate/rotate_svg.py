# Code by Sergio00166

import xml.etree.ElementTree as ET
import argparse
import math
import re


# --------- Geometry helpers ---------
def rotate_point(x, y, cx, cy, ang):
    ca = math.cos(ang)
    sa = math.sin(ang)
    dx, dy = x - cx, y - cy
    return (cx + dx*ca - dy*sa, cy + dx*sa + dy*ca)

def numfmt(v):
    # Compact formatting, but stable
    s = f"{v:.6f}"
    s = s.rstrip("0").rstrip(".")
    return s if s else "0"


# --------- Path parsing and conversion to absolute ---------
# Tokenizer: command letters or numbers (incl. exponents)
_cmd_re = re.compile(r"[MmZzLlHhVvCcSsQqTtAa]")
_num_re = re.compile(r"[+-]?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?:[eE][+-]?\d+)?")

def tokenize_path(d):
    i, n = 0, len(d)
    while i < n:
        m = _cmd_re.match(d, i)
        if m:
            yield m.group(0)
            i = m.end()
            continue
        m = _num_re.match(d, i)
        if m:
            yield float(m.group(0))
            i = m.end()
            continue
        # skip separators
        i += 1


def to_absolute_segments(d):
    # Returns list of (cmd, params_abs) where cmd is uppercase
    toks = list(tokenize_path(d))
    i = 0
    out = []
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    prev_cmd = None
    prev_c_ctrl = None  # last cubic control point (for S)
    prev_q_ctrl = None  # last quad control point (for T)

    def take(n):
        nonlocal i
        vals = toks[i:i+n]
        i += n
        return vals

    while i < len(toks):
        t = toks[i]
        i += 1
        if isinstance(t, str):
            cmd = t
        else:
            # Implicit command repetition
            if prev_cmd is None:
                raise ValueError("Path starts with numbers")
            cmd = prev_cmd
            i -= 1  # put number back; handler will read it

        is_rel = cmd.islower()
        C = cmd.upper()

        def rel_or_abs(x, y):
            return (cur[0]+x, cur[1]+y) if is_rel else (x, y)

        if C == 'M':
            x, y = take(2)
            p = rel_or_abs(x, y)
            out.append(('M', [p[0], p[1]]))
            cur = p
            start = p
            prev_c_ctrl = prev_q_ctrl = None
            # Subsequent implicit lineto pairs for extra coords
            while i < len(toks) and not isinstance(toks[i], str):
                x, y = take(2)
                p = rel_or_abs(x, y)
                out.append(('L', [p[0], p[1]]))
                cur = p
                prev_c_ctrl = prev_q_ctrl = None

        elif C == 'Z':
            out.append(('Z', []))
            cur = start
            prev_c_ctrl = prev_q_ctrl = None

        elif C == 'L':
            while i < len(toks) and not isinstance(toks[i], str):
                x, y = take(2)
                p = rel_or_abs(x, y)
                out.append(('L', [p[0], p[1]]))
                cur = p
            prev_c_ctrl = prev_q_ctrl = None

        elif C == 'H':
            while i < len(toks) and not isinstance(toks[i], str):
                x = take(1)[0]
                x = cur[0] + x if is_rel else x
                cur = (x, cur[1])
                out.append(('L', [cur[0], cur[1]]))
            prev_c_ctrl = prev_q_ctrl = None

        elif C == 'V':
            while i < len(toks) and not isinstance(toks[i], str):
                y = take(1)[0]
                y = cur[1] + y if is_rel else y
                cur = (cur[0], y)
                out.append(('L', [cur[0], cur[1]]))
            prev_c_ctrl = prev_q_ctrl = None

        elif C == 'C':
            while i < len(toks) and not isinstance(toks[i], str):
                x1,y1,x2,y2,x,y = take(6)
                p1 = rel_or_abs(x1,y1)
                p2 = rel_or_abs(x2,y2)
                p  = rel_or_abs(x,y)
                out.append(('C', [p1[0],p1[1], p2[0],p2[1], p[0],p[1]]))
                cur = p
                prev_c_ctrl = p2
                prev_q_ctrl = None

        elif C == 'S':
            while i < len(toks) and not isinstance(toks[i], str):
                x2,y2,x,y = take(4)
                p2 = rel_or_abs(x2,y2)
                p  = rel_or_abs(x,y)
                if prev_cmd and prev_cmd.upper() in ('C','S') and prev_c_ctrl:
                    # reflect last cubic control point
                    rx = 2*cur[0] - prev_c_ctrl[0]
                    ry = 2*cur[1] - prev_c_ctrl[1]
                    p1 = (rx, ry)
                else:
                    p1 = cur
                out.append(('C', [p1[0],p1[1], p2[0],p2[1], p[0],p[1]]))
                cur = p
                prev_c_ctrl = p2
                prev_q_ctrl = None

        elif C == 'Q':
            while i < len(toks) and not isinstance(toks[i], str):
                x1,y1,x,y = take(4)
                p1 = rel_or_abs(x1,y1)
                p  = rel_or_abs(x,y)
                out.append(('Q', [p1[0],p1[1], p[0],p[1]]))
                cur = p
                prev_q_ctrl = p1
                prev_c_ctrl = None

        elif C == 'T':
            while i < len(toks) and not isinstance(toks[i], str):
                x,y = take(2)
                p  = rel_or_abs(x,y)
                if prev_cmd and prev_cmd.upper() in ('Q','T') and prev_q_ctrl:
                    rx = 2*cur[0] - prev_q_ctrl[0]
                    ry = 2*cur[1] - prev_q_ctrl[1]
                    p1 = (rx, ry)
                else:
                    p1 = cur
                out.append(('Q', [p1[0],p1[1], p[0],p[1]]))
                cur = p
                prev_q_ctrl = p1
                prev_c_ctrl = None

        elif C == 'A':
            # rx ry xrot largeArcFlag sweepFlag x y
            while i < len(toks) and not isinstance(toks[i], str):
                rx, ry, xrot, laf, sf, x, y = take(7)
                p = rel_or_abs(x, y)
                # Normalize flags to ints 0/1 (they may be floats due to tokenizer)
                laf = 1 if int(laf) else 0
                sf  = 1 if int(sf) else 0
                # Convert to absolute A; store, rotation handled later
                out.append(('A', [rx, ry, xrot, laf, sf, p[0], p[1]]))
                cur = p
            prev_c_ctrl = prev_q_ctrl = None

        else:
            raise NotImplementedError(f"Unsupported command: {C}")

        prev_cmd = cmd

    return out


def rotate_abs_segments(segments, cx, cy, ang):
    out = []
    for cmd, p in segments:
        if cmd == 'Z' or cmd == 'M' or cmd == 'L':
            if cmd in ('M','L'):
                x, y = rotate_point(p[0], p[1], cx, cy, ang)
                out.append((cmd, [x, y]))
            else:
                out.append((cmd, []))
        elif cmd == 'C':
            x1,y1 = rotate_point(p[0], p[1], cx, cy, ang)
            x2,y2 = rotate_point(p[2], p[3], cx, cy, ang)
            x ,y  = rotate_point(p[4], p[5], cx, cy, ang)
            out.append(('C', [x1,y1,x2,y2,x,y]))
        elif cmd == 'Q':
            x1,y1 = rotate_point(p[0], p[1], cx, cy, ang)
            x ,y  = rotate_point(p[2], p[3], cx, cy, ang)
            out.append(('Q', [x1,y1,x,y]))
        elif cmd == 'A':
            # Under rotation by ang: endpoints rotate; rx,ry unchanged; xrot += ang
            rx, ry, xrot, laf, sf, x, y = p
            x, y = rotate_point(x, y, cx, cy, ang)
            xrot = (xrot + math.degrees(ang)) % 360.0
            out.append(('A', [rx, ry, xrot, laf, sf, x, y]))
        else:
            # Should not appear, but keep safe
            out.append((cmd, p))
    return out


def segments_to_d(segments):
    out = []
    for cmd, p in segments:
        if cmd == 'Z':
            out.append('Z')
        elif cmd in ('M','L'):
            out.append(f"{cmd}{numfmt(p[0])} {numfmt(p[1])}")
        elif cmd == 'C':
            out.append(f"C{numfmt(p[0])} {numfmt(p[1])} {numfmt(p[2])} {numfmt(p[3])} {numfmt(p[4])} {numfmt(p[5])}")
        elif cmd == 'Q':
            out.append(f"Q{numfmt(p[0])} {numfmt(p[1])} {numfmt(p[2])} {numfmt(p[3])}")
        elif cmd == 'A':
            # flags must be integers 0/1
            rx, ry, xrot, laf, sf, x, y = p
            out.append(f"A{numfmt(rx)} {numfmt(ry)} {numfmt(xrot)} {int(laf)} {int(sf)} {numfmt(x)} {numfmt(y)}")
        else: pass
    return " ".join(out)


# --------- SVG rotation (in-place, preserving structure) ---------

def rotate_svg(src, dst, angle_deg):
    tree = ET.parse(src)
    root = tree.getroot()

    # Namespace mapping
    ns = {"svg": "http://www.w3.org/2000/svg"}
    # ET write preserves ns if registered
    ET.register_namespace('', ns["svg"])

    # Determine pivot from viewBox
    vb = root.attrib.get("viewBox")
    if not vb:
        raise ValueError("SVG root must have a viewBox to auto-center rotation.")
    minx, miny, vw, vh = [float(x) for x in vb.strip().split()]
    cx, cy = (minx + vw/2.0, miny + vh/2.0)
    ang = math.radians(angle_deg)

    # polygon/polyline
    for tag in ("polygon","polyline"):
        for e in root.findall(f".//svg:{tag}", ns):
            pts = e.get("points", "").strip()
            if not pts:
                continue
            new_pts = []
            for token in re.split(r"\s+", pts.strip()):
                if not token: continue
                if "," in token:
                    x,y = token.split(",",1)
                else: continue
                rx, ry = rotate_point(float(x), float(y), cx, cy, ang)
                new_pts.append(f"{numfmt(rx)},{numfmt(ry)}")
            e.set("points", " ".join(new_pts))

    # circle / ellipse
    for e in root.findall(".//svg:circle", ns) + root.findall(".//svg:ellipse", ns):
        if "cx" in e.attrib and "cy" in e.attrib:
            rx, ry = rotate_point(float(e.get("cx","0")), float(e.get("cy","0")), cx, cy, ang)
            e.set("cx", numfmt(rx))
            e.set("cy", numfmt(ry))

    # rect (rotate center, keep width/height and rx/ry)
    for e in root.findall(".//svg:rect", ns):
        if all(k in e.attrib for k in ("x","y","width","height")):
            w = float(e.get("width","0")); h = float(e.get("height","0"))
            cxr = float(e.get("x","0")) + w/2.0
            cyr = float(e.get("y","0")) + h/2.0
            rx0, ry0 = rotate_point(cxr, cyr, cx, cy, ang)
            e.set("x", numfmt(rx0 - w/2.0))
            e.set("y", numfmt(ry0 - h/2.0))

    # line
    for e in root.findall(".//svg:line", ns):
        if all(k in e.attrib for k in ("x1","y1","x2","y2")):
            x1,y1 = rotate_point(float(e.get("x1","0")), float(e.get("y1","0")), cx, cy, ang)
            x2,y2 = rotate_point(float(e.get("x2","0")), float(e.get("y2","0")), cx, cy, ang)
            e.set("x1", numfmt(x1)); e.set("y1", numfmt(y1))
            e.set("x2", numfmt(x2)); e.set("y2", numfmt(y2))

    # path
    for e in root.findall(".//svg:path", ns):
        d = e.get("d")
        if not d: continue
        segs_abs = to_absolute_segments(d)
        segs_rot = rotate_abs_segments(segs_abs, cx, cy, ang)
        e.set("d", segments_to_d(segs_rot))

    # polyline/points inside marker/symbol/defs are handled as well due to .// search
    tree.write(dst, encoding="utf-8", xml_declaration=True)


# --------- Run ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rotate an SVG file by a given angle.")
    parser.add_argument("input", help="Path to the input SVG file")
    parser.add_argument("output", help="Path to the output SVG file")
    parser.add_argument("angle", type=float, help="Rotation angle in degrees")

    args = parser.parse_args()
    rotate_svg(args.input, args.output, angle_deg=args.angle)


