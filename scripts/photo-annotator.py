#!/usr/bin/env python3
"""
Photo Annotator - Add distance/direction measurements to Stingray photos
Uses PIL/Pillow for image manipulation
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont
import json

def annotate_photo(photo_path, output_path, measurements):
    """
    Add measurement annotations to a photo
    
    measurements = {
        'distance': '12 feet',
        'direction': 'Southwest',
        'height': '10 feet above ground',
        'signal_strength': '-15.5 dBm',
        'species': 'LightPolaflag'
    }
    """
    
    # Open image
    img = Image.open(photo_path)
    draw = ImageDraw.Draw(img)
    
    # Get image dimensions
    width, height = img.size
    
    # Try to load a nice font, fallback to default
    try:
        # Try different font sizes
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        label_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        data_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 35)
    except:
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        data_font = ImageFont.load_default()
    
    # Draw semi-transparent overlay at top
    overlay_height = 200
    overlay = Image.new('RGBA', (width, overlay_height), (0, 0, 0, 180))
    img.paste(overlay, (0, 0), overlay)
    
    # Draw title
    species = measurements.get('species', 'Unknown Stingray')
    draw.text((20, 20), f"🎯 {species}", fill=(255, 255, 255), font=title_font)
    
    # Draw measurements
    y_offset = 90
    
    if measurements.get('distance'):
        draw.text((20, y_offset), f"📏 Distance: {measurements['distance']}", 
                 fill=(255, 200, 0), font=label_font)
        y_offset += 50
    
    if measurements.get('direction'):
        draw.text((20, y_offset), f"🧭 Direction: {measurements['direction']}", 
                 fill=(255, 200, 0), font=label_font)
    
    # Draw info box at bottom
    info_height = 150
    info_overlay = Image.new('RGBA', (width, info_height), (0, 0, 0, 180))
    img.paste(info_overlay, (0, height - info_height), info_overlay)
    
    # Draw additional info
    y_bottom = height - info_height + 20
    
    if measurements.get('height'):
        draw.text((20, y_bottom), f"📐 Height: {measurements['height']}", 
                 fill=(100, 200, 255), font=data_font)
        y_bottom += 45
    
    if measurements.get('signal_strength'):
        draw.text((20, y_bottom), f"📡 Signal: {measurements['signal_strength']}", 
                 fill=(255, 100, 100), font=data_font)
        y_bottom += 45
    
    # Draw arrow pointing to device (if coordinates provided)
    if measurements.get('device_x') and measurements.get('device_y'):
        device_x = int(measurements['device_x'])
        device_y = int(measurements['device_y'])
        
        # Draw arrow
        arrow_color = (255, 0, 0)
        arrow_width = 5
        
        # Arrow line
        draw.line([(device_x, device_y - 100), (device_x, device_y - 20)], 
                 fill=arrow_color, width=arrow_width)
        
        # Arrow head
        draw.polygon([
            (device_x, device_y - 20),
            (device_x - 20, device_y - 50),
            (device_x + 20, device_y - 50)
        ], fill=arrow_color)
        
        # Circle around device
        circle_radius = 30
        draw.ellipse([
            (device_x - circle_radius, device_y - circle_radius),
            (device_x + circle_radius, device_y + circle_radius)
        ], outline=arrow_color, width=arrow_width)
    
    # Draw distance scale (optional)
    if measurements.get('show_scale'):
        scale_length = 200  # pixels
        scale_feet = 10  # represents 10 feet
        scale_x = width - scale_length - 40
        scale_y = height - 60
        
        # Scale bar
        draw.rectangle([
            (scale_x, scale_y),
            (scale_x + scale_length, scale_y + 20)
        ], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        
        # Scale text
        draw.text((scale_x + scale_length // 2 - 40, scale_y - 30), 
                 f"{scale_feet} feet", fill=(255, 255, 255), font=data_font)
    
    # Save annotated image
    img.save(output_path, quality=95)
    print(f"✅ Annotated photo saved to: {output_path}")

def interactive_annotate(photo_path):
    """Interactive mode to annotate a photo"""
    print("\n🎯 Stingray Photo Annotator")
    print("="*50)
    
    measurements = {}
    
    # Get measurements from user
    measurements['species'] = input("\n🏷️  Species name (e.g., LightPolaflag): ").strip()
    measurements['distance'] = input("📏 Distance (e.g., 12 feet): ").strip()
    measurements['direction'] = input("🧭 Direction (e.g., Southwest): ").strip()
    measurements['height'] = input("📐 Height (e.g., 10 feet above ground): ").strip()
    measurements['signal_strength'] = input("📡 Signal strength (e.g., -15.5 dBm): ").strip()
    
    # Ask if they want to mark device location
    mark_device = input("\n📍 Mark device location on photo? (y/n): ").strip().lower()
    if mark_device == 'y':
        print("\nOpen the photo and estimate pixel coordinates:")
        print("(0,0 is top-left, width x height is bottom-right)")
        try:
            measurements['device_x'] = input("  X coordinate: ").strip()
            measurements['device_y'] = input("  Y coordinate: ").strip()
        except:
            pass
    
    # Ask about scale
    show_scale = input("\n📏 Show distance scale? (y/n): ").strip().lower()
    measurements['show_scale'] = show_scale == 'y'
    
    # Generate output filename
    base_name = os.path.splitext(photo_path)[0]
    output_path = f"{base_name}_annotated.jpg"
    
    # Annotate
    annotate_photo(photo_path, output_path, measurements)
    
    # Save metadata
    metadata_path = f"{base_name}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(measurements, f, indent=2)
    print(f"📄 Metadata saved to: {metadata_path}")

def batch_annotate(photo_path, metadata_path):
    """Annotate using a metadata JSON file"""
    with open(metadata_path, 'r') as f:
        measurements = json.load(f)
    
    base_name = os.path.splitext(photo_path)[0]
    output_path = f"{base_name}_annotated.jpg"
    
    annotate_photo(photo_path, output_path, measurements)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Interactive mode:")
        print("    python3 photo-annotator.py <photo.jpg>")
        print("\n  Batch mode with metadata:")
        print("    python3 photo-annotator.py <photo.jpg> <metadata.json>")
        print("\nExample:")
        print("  python3 photo-annotator.py lightpole.jpg")
        print("  python3 photo-annotator.py lightpole.jpg lightpole_metadata.json")
        sys.exit(1)
    
    photo_path = sys.argv[1]
    
    if not os.path.exists(photo_path):
        print(f"❌ Error: Photo not found: {photo_path}")
        sys.exit(1)
    
    if len(sys.argv) > 2:
        # Batch mode
        metadata_path = sys.argv[2]
        if not os.path.exists(metadata_path):
            print(f"❌ Error: Metadata file not found: {metadata_path}")
            sys.exit(1)
        batch_annotate(photo_path, metadata_path)
    else:
        # Interactive mode
        interactive_annotate(photo_path)

if __name__ == '__main__':
    main()
