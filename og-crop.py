#!/usr/bin/env -S uv run
# /// script
# dependencies = ["Pillow", "pygame"]
# ///
"""
og-crop.py — Interactive 1.91:1 crop tool for Open Graph images.

USAGE
-----
    python og-crop.py IMAGE

    Displays the image with a 1.91:1 crop box overlay.
    - Click + drag to move the box.
    - Scroll wheel (or +/-) to resize it.
    - Press Enter to save og-FILENAME next to the original.
    - Press Escape or Q to quit without saving.
"""

import sys
from pathlib import Path

import pygame
from PIL import Image

OG_RATIO = 1.91  # width / height
DIM_ALPHA = 140  # 0-255 darkness of the area outside the crop box


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    src_path = Path(sys.argv[1]).resolve()
    if not src_path.exists():
        print(f'File not found: {src_path}')
        sys.exit(1)

    img = Image.open(src_path).convert('RGB')
    img_w, img_h = img.size

    pygame.init()
    info = pygame.display.Info()
    max_w = int(info.current_w * 0.90)
    max_h = int(info.current_h * 0.85)
    scale = min(max_w / img_w, max_h / img_h, 1.0)
    disp_w = max(1, int(img_w * scale))
    disp_h = max(1, int(img_h * scale))

    screen = pygame.display.set_mode((disp_w, disp_h + 30))
    pygame.display.set_caption(f'og-crop: {src_path.name}')
    font = pygame.font.SysFont('monospace', 14)

    # Convert PIL image to pygame surface
    disp_img = img.resize((disp_w, disp_h), Image.LANCZOS)
    raw = disp_img.tobytes('raw', 'RGB')
    surf = pygame.image.fromstring(raw, (disp_w, disp_h), 'RGB')

    # Crop box in original image coordinates [x, y, w, h]
    def initial_box():
        w = img_w
        h = round(w / OG_RATIO)
        if h > img_h:
            h = img_h
            w = round(h * OG_RATIO)
        return [float((img_w - w) // 2), float((img_h - h) // 2), float(w), float(h)]

    box = initial_box()

    def clamp_box():
        w = max(10.0, min(box[2], float(img_w)))
        h = round(w / OG_RATIO)
        if h > img_h:
            h = float(img_h)
            w = round(h * OG_RATIO)
        x = max(0.0, min(box[0], img_w - w))
        y = max(0.0, min(box[1], img_h - h))
        box[0], box[1], box[2], box[3] = x, y, float(w), float(h)

    def box_disp_rect():
        x, y, w, h = box
        return pygame.Rect(
            int(x * scale), int(y * scale),
            int(w * scale), int(h * scale),
        )

    def resize_box(delta_img_px):
        cx = box[0] + box[2] / 2
        cy = box[1] + box[3] / 2
        box[2] += delta_img_px
        box[3] = box[2] / OG_RATIO
        box[0] = cx - box[2] / 2
        box[1] = cy - box[3] / 2
        clamp_box()

    def draw():
        screen.blit(surf, (0, 0))

        # Dim overlay outside crop box
        overlay = pygame.Surface((disp_w, disp_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, DIM_ALPHA))
        r = box_disp_rect()
        # Cut out the crop area by drawing a transparent rect
        pygame.draw.rect(overlay, (0, 0, 0, 0), r)
        screen.blit(overlay, (0, 0))

        # Crop box border
        pygame.draw.rect(screen, (255, 255, 255), r, 2)
        # Corner handles
        for cx, cy in [(r.left, r.top), (r.right, r.top),
                       (r.left, r.bottom), (r.right, r.bottom)]:
            pygame.draw.rect(screen, (255, 255, 255),
                             pygame.Rect(cx - 5, cy - 5, 10, 10))

        # Status bar
        x, y, w, h = (round(v) for v in box)
        msg = (f'  crop: {w}×{h}  origin: ({x},{y})'
               f'  |  drag to move  |  scroll/+- to resize'
               f'  |  Enter=save  Esc=quit')
        pygame.draw.rect(screen, (30, 30, 30),
                         pygame.Rect(0, disp_h, disp_w, 30))
        txt = font.render(msg, True, (200, 200, 200))
        screen.blit(txt, (4, disp_h + 7))

        pygame.display.flip()

    drag_start_mouse = None
    drag_start_box = None

    clamp_box()
    draw()

    step = int(img_w * 0.02) or 1

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    clamp_box()
                    x, y, w, h = (round(v) for v in box)
                    cropped = img.crop((x, y, x + w, y + h))
                    out_path = src_path.parent / ('og-' + src_path.name)
                    cropped.save(out_path)
                    print(f'Saved: {out_path}  ({w}×{h})')
                    try:
                        rel = out_path.relative_to(
                            Path(__file__).resolve().parent / 'blog' / 'posts'
                        )
                        print(f'  URL: https://antocuni.eu/{rel}')
                    except ValueError:
                        pass
                    running = False
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    resize_box(step)
                    draw()
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    resize_box(-step)
                    draw()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    drag_start_mouse = event.pos
                    drag_start_box = (box[0], box[1])
                elif event.button == 4:  # scroll up
                    resize_box(step)
                    draw()
                elif event.button == 5:  # scroll down
                    resize_box(-step)
                    draw()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drag_start_mouse = None
                    drag_start_box = None

            elif event.type == pygame.MOUSEMOTION:
                if drag_start_mouse is not None:
                    dx = (event.pos[0] - drag_start_mouse[0]) / scale
                    dy = (event.pos[1] - drag_start_mouse[1]) / scale
                    box[0] = drag_start_box[0] + dx
                    box[1] = drag_start_box[1] + dy
                    clamp_box()
                    draw()

            elif event.type == pygame.MOUSEWHEEL:
                # pygame 2.x MOUSEWHEEL event
                resize_box(step * event.y)
                draw()

    pygame.quit()


if __name__ == '__main__':
    main()
