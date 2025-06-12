import os
from PIL import Image

image_folder = r"G:\常嘉硕\大学\中南大学\Games Programming\Pygame\TowerDesign\Experiments\AImap2.0\maze_loops_optimization_correct_batch"

original_images = []
optimal_images = []

for i in range(1, 26):
    idx = f"{i:02d}"
    for file in os.listdir(image_folder):
        if f"map_{idx}_" in file:
            full_path = os.path.join(image_folder, file)
            if "original" in file:
                original_images.append(full_path)
            elif "optimized" in file:
                optimal_images.append(full_path)

original_images.sort()
optimal_images.sort()

def make_grid(image_paths, output_path, rows=5, cols=5, padding=50, bg_color=(255, 255, 255)):
    imgs = [Image.open(p).convert("RGB") for p in image_paths]
    w, h = imgs[0].size
    grid_w = cols * w + (cols - 1) * padding
    grid_h = rows * h + (rows - 1) * padding
    grid_img = Image.new("RGB", (grid_w, grid_h), color=bg_color)
    for idx, img in enumerate(imgs):
        x = idx % cols
        y = idx // cols
        px = x * (w + padding)
        py = y * (h + padding)
        grid_img.paste(img, (px, py))
    grid_img.save(output_path)

make_grid(original_images, os.path.join(image_folder, "original_grid.png"))
make_grid(optimal_images, os.path.join(image_folder, "optimal_grid.png"))
