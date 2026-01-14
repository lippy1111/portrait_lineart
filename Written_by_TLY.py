# -*- coding: utf-8 -*-
"""
Written by TLY
Generates vector line art from a portrait image and saves as SVG
"""

import os
import math
from random import random, randint
from PIL import Image, ImageOps, ImageFilter, ImageDraw
import numpy as np

# ---------------------------
# CONFIG
# ---------------------------

img_path = r"C:\TLY\China\SUStech\SEM5\Designing for beginners\Assignments\Assignment 14\portrait.jpg"
output_svg = r"C:\TLY\China\SUStech\SEM5\Designing for beginners\Assignments\Assignment 14\final.svg"

resolution = 512  # resizing for faster processing
stroke_width = 2
draw_contours = True
draw_hatch = True
hatch_size = 16
brightness_threshold = 200  # controls where hatching is applied
max_lines_per_patch = 3

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def find_edges(im):
    """Convert image to grayscale, enhance contrast, and detect edges."""
    im_gray = im.convert("L")
    im_gray = ImageOps.autocontrast(im_gray, cutoff=5)
    edges = im_gray.filter(ImageFilter.FIND_EDGES)
    edges = edges.point(lambda p: 255 if p > 50 else 0)
    return edges

def get_edge_points(im):
    """Return list of (x,y) coordinates of white pixels."""
    px = im.load()
    w, h = im.size
    points = []
    for y in range(h):
        for x in range(w):
            if px[x, y] > 128:
                points.append((x, y))
    return points

def connect_points(points, max_dist=20):
    """Order points into lines using nearest-neighbor approach."""
    if not points:
        return []
    
    points = points.copy()
    lines = []
    current = points.pop(0)
    line = [current]

    while points:
        nearest = min(points, key=lambda p: math.hypot(p[0]-current[0], p[1]-current[1]))
        dist = math.hypot(nearest[0]-current[0], nearest[1]-current[1])
        if dist > max_dist:
            lines.append(line)
            line = []
        line.append(nearest)
        current = nearest
        points.remove(nearest)

    if line:
        lines.append(line)
    return lines

def makesvg(lines, width=1024, height=1024, stroke_width=1):
    """Convert lines to SVG format."""
    out = f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{width}" height="{height}">'
    for line in lines:
        if len(line) < 2:
            continue
        pts_str = " ".join(f"{px},{py}" for px, py in line)
        out += f'<polyline points="{pts_str}" stroke="black" stroke-width="{stroke_width}" fill="none" />\n'
    out += "</svg>"
    return out

def generate_hatch_lines(im, patch_size=16, brightness_threshold=220, max_lines_per_patch=4, line_length=30):
    """
    Generate hatching lines for darker areas using average patch brightness.
    - patch_size: size of each patch in pixels
    - brightness_threshold: skip patches brighter than this
    - max_lines_per_patch: maximum number of lines per patch
    - line_length: length of each hatch line
    """
    print("Generating hatching lines...")
    
    px = np.array(im.convert("L"))  # ensure grayscale
    h, w = px.shape
    hatch_lines = []

    for y in range(0, h, patch_size):
        for x in range(0, w, patch_size):
            # get patch and compute average brightness
            patch = px[y:y+patch_size, x:x+patch_size]
            avg_brightness = np.mean(patch)
            
            if avg_brightness > brightness_threshold:
                continue  # skip mostly bright patches

            # number of lines proportional to darkness
            num_lines = max(1, int((brightness_threshold - avg_brightness) / 40))
            num_lines = min(num_lines, max_lines_per_patch)

            for _ in range(num_lines):
                # random start point inside patch
                x0 = x + random() * patch_size
                y0 = y + random() * patch_size

                # random angle 0–360°
                angle = random() * 2 * math.pi
                x1 = int(x0 + line_length * math.cos(angle))
                y1 = int(y0 + line_length * math.sin(angle))

                # clamp inside image
                x1 = max(0, min(w - 1, x1))
                y1 = max(0, min(h - 1, y1))

                hatch_lines.append([(x0, y0), (x1, y1)])

    return hatch_lines
# ---------------------------
# MAIN
# ---------------------------

# Load and resize image
im = Image.open(img_path)
im = im.resize((resolution, int(resolution * im.height / im.width)))

lines = []

# Contours / outline
if draw_contours:
    edges = find_edges(im)
    points = get_edge_points(edges)
    lines += connect_points(points)

# Hatching for shading
if draw_hatch:
    hatches = generate_hatch_lines(im, patch_size=hatch_size, brightness_threshold=brightness_threshold,
                                   max_lines_per_patch=max_lines_per_patch)
    lines += hatches

# Ensure output folder exists
os.makedirs(os.path.dirname(output_svg), exist_ok=True)

# Save SVG
svg_content = makesvg(lines, im.width, im.height, stroke_width)
with open(output_svg, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"SVG saved to {output_svg}")
print(f"Number of lines: {len(lines)}")
