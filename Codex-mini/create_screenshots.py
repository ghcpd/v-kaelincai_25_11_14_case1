from PIL import Image, ImageDraw
import os
projA = os.path.join('Project_A_BaselinePlayer','screenshots')
projB = os.path.join('Project_B_EnhancedPlayer','screenshots')
tests = ['resume','playback_speed','auto_skip','performance','notes_sync']
for base, label in [(projA,'pre'),(projB,'post')]:
    os.makedirs(base, exist_ok=True)
    for tid in tests:
        img = Image.new('RGB',(620,360),(28,30,45))
        draw = ImageDraw.Draw(img)
        draw.rectangle([10,10,610,350],outline=(255,255,255),width=3)
        draw.text((30,40),f"{label.title()} Player", fill=(255,255,255))
        draw.text((30,80),f"Scenario: {tid}", fill=(200,200,255))
        draw.text((30,120),"Simulated interface", fill=(160,255,180))
        draw.text((30,160),"Screenshot placeholder", fill=(255,200,200))
        img.save(os.path.join(base,f"screenshot_{label}_{tid}.png"))
