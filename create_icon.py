"""
Creates a multi-resolution .ico icon file for AI Email Summarizer.
Generates a professional envelope icon with AI indicator at various sizes for crisp Windows display.
"""

from PIL import Image, ImageDraw
import math

def create_icon_at_size(size):
    """
    Create an envelope icon with AI sparkle at the specified size.
    
    Args:
        size: Icon dimension in pixels (square)
    
    Returns:
        PIL.Image: Generated icon image
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    padding = size * 0.1
    envelope_width = size - (padding * 2)
    envelope_height = envelope_width * 0.7
    
    # Center the envelope
    left = padding
    top = (size - envelope_height) / 2 + size * 0.05
    right = size - padding
    bottom = top + envelope_height
    
    envelope_color = (66, 133, 244)
    flap_color = (52, 109, 204)
    paper_color = (255, 255, 255)
    accent_color = (234, 67, 53)
    
    corner_radius = max(2, int(size * 0.08))
    
    draw.rounded_rectangle(
        [left, top, right, bottom],
        radius=corner_radius,
        fill=envelope_color
    )
    
    flap_points = [
        (left, top),
        (right, top),
        ((left + right) / 2, (top + bottom) / 2 - size * 0.02)
    ]
    draw.polygon(flap_points, fill=flap_color)
    
    paper_margin = size * 0.15
    paper_top = top + size * 0.08
    paper_height = envelope_height * 0.45
    
    draw.rounded_rectangle(
        [left + paper_margin, paper_top, right - paper_margin, paper_top + paper_height],
        radius=max(1, corner_radius // 2),
        fill=paper_color
    )
    
    # Draw lines on the paper to represent text/summary
    line_color = (200, 200, 200)
    line_margin = size * 0.22
    line_color = (200, 200, 200)
    line_margin = size * 0.22
    line_spacing = size * 0.06
    line_height = max(1, int(size * 0.02))
    
    for i in range(3):
        line_top = paper_top + size * 0.04 + (i * line_spacing)
        line_width_factor = 0.9 if i < 2 else 0.6
        draw.rounded_rectangle(
            [left + line_margin, line_top, 
             left + line_margin + (envelope_width - line_margin * 1.4) * line_width_factor, 
             line_top + line_height],
            radius=max(1, line_height // 2),
            fill=line_color
        )
    
    
    # Draw a simple 4-pointed star for AI indicator
    def draw_star(cx, cy, outer_r, inner_r, points=4):
        for i in range(points * 2):
            angle = (i * math.pi / points) - math.pi / 2
            r = outer_r if i % 2 == 0 else inner_r
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            coords.append((x, y))
        return coords
    
    star_points = draw_star(spark_x, spark_y, spark_size * 0.5, spark_size * 0.2, 4)
    draw.polygon(star_points, fill=accent_color)
    
    # Add a smaller secondary sparkle
    small_spark_x = spark_x - size * 0.08
    small_spark_y = spark_y - size * 0.1
    small_spark_x = spark_x - size * 0.08
    small_spark_y = spark_y - size * 0.1
    small_star_points = draw_star(small_spark_x, small_spark_y, spark_size * 0.25, spark_size * 0.1, 4)
    draw.polygon(small_star_points, fill=accent_color)
    
    return img


def create_multi_resolution_icon():
    """
    Create a multi-resolution .ico file containing icons at standard Windows sizes.
    Generates sizes from 16x16 to 256x256 for optimal display at all DPI settings.
    """
    for size in sizes:
        img = create_icon_at_size(size)
        images.append(img)
        print(f"Created {size}x{size} icon")
    
    images[0].save(
        'app_icon.ico',
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print("\nSaved app_icon.ico with all resolutions!")
    print("Icon sizes included: " + ", ".join([f"{s}x{s}" for s in sizes]))


if __name__ == "__main__":
    try:
        create_multi_resolution_icon()
        print("\n✓ Icon created successfully!")
        print("Now rebuild your app with: pyinstaller 'AI Email Summarizer.spec'")
    except ImportError:
        print("Pillow is required. Install it with: pip install Pillow")
