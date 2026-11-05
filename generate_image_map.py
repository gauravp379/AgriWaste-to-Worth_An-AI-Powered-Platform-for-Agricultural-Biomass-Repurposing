import os, json

d = 'data/crop_images'
m = {}
for entry in os.scandir(d):
    if entry.is_dir():
        count = 0
        images = []
        for file in os.scandir(entry.path):
            if file.is_file() and file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                images.append(file.path.replace('\\', '/'))
                count += 1
                if count >= 50:
                    break
        m[entry.name] = images

with open('js/image_map.js', 'w') as out:
    out.write('window.CROP_IMAGE_MAP=' + json.dumps(m) + ';')
