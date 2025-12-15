"""
Script to create a sharp, multi-resolution icon for AI Email Summarizer.
Uses the same design but renders at proper resolutions for crisp display.
"""

from PIL import Image, ImageDraw, ImageFont
import math

def create_icon_at_size(size):
    """Create the email summarizer icon at the specified size."""
    # Create a new image with transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate proportional sizes
    padding = size * 0.1
    envelope_width = size - (padding * 2)
    envelope_height = envelope_width * 0.7
    
    # Center the envelope
    left = padding
    top = (size - envelope_height) / 2 + size * 0.05
    right = size - padding
    bottom = top + envelope_height
    
    # Colors - nice blue gradient effect approximation
    envelope_color = (66, 133, 244)  # Google Blue
    flap_color = (52, 109, 204)  # Darker blue for depth
    paper_color = (255, 255, 255)
    accent_color = (234, 67, 53)  # Red accent for AI spark
    
    # Draw envelope body (rectangle with rounded corners for larger sizes)
    corner_radius = max(2, int(size * 0.08))
    
    # Draw main envelope body
    draw.rounded_rectangle(
        [left, top, right, bottom],
        radius=corner_radius,
        fill=envelope_color
    )
    
    # Draw envelope flap (triangle at top)
    flap_points = [
        (left, top),  # Top left
        (right, top),  # Top right
        ((left + right) / 2, (top + bottom) / 2 - size * 0.02)  # Center point
    ]
    draw.polygon(flap_points, fill=flap_color)
    
    # Draw a small paper/document peeking out
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
    line_spacing = size * 0.06
    line_height = max(1, int(size * 0.02))
    
    for i in range(3):
        line_top = paper_top + size * 0.04 + (i * line_spacing)
        line_width_factor = 0.9 if i < 2 else 0.6  # Last line shorter
        draw.rounded_rectangle(
            [left + line_margin, line_top, 
             left + line_margin + (envelope_width - line_margin * 1.4) * line_width_factor, 
             line_top + line_height],
            radius=max(1, line_height // 2),
            fill=line_color
        )
    
    # Draw AI sparkle/magic indicator (small star/spark in corner)
    spark_size = size * 0.15
    spark_x = right - size * 0.18
    spark_y = bottom - size * 0.12
    
    # Draw a simple 4-pointed star for AI indicator
    def draw_star(cx, cy, outer_r, inner_r, points=4):
        coords = []
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
    small_star_points = draw_star(small_spark_x, small_spark_y, spark_size * 0.25, spark_size * 0.1, 4)
    draw.polygon(small_star_points, fill=accent_color)
    
    return img


def create_multi_resolution_icon():
    """Create an ICO file with multiple resolutions for sharp display."""
    # Standard Windows icon sizes for crisp display at all scales
    sizes = [16, 24, 32, 48, 64, 128, 256]
    
    images = []
    for size in sizes:
        img = create_icon_at_size(size)
        images.append(img)
        print(f"Created {size}x{size} icon")
    
    # Save as ICO with all sizes
    # The first image is the main one, others are alternates
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
