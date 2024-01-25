import argparse
import os
import random
from PIL import Image


def make_collage(images, filename, width, init_height, max_images=None):
    """
    Make a collage image with a width equal to `width` from `images` and save to `filename`.
    """
    if not images:
        print('No images for collage found!')
        return False

    # Limit the number of images if max_images is specified
    if max_images is not None and max_images > 0:
        images = images[:max_images]

    margin_size = 0
    # run until a suitable arrangement of images is found
    while True:
        # copy images to images_list
        images_list = images[:]
        coefs_lines = []
        images_line = []
        x = 0
        while images_list:
            # get first image and resize to `init_height`
            img_path = images_list.pop(0)
            img = Image.open(img_path)
            img.thumbnail((width, init_height))
            # when `x` will go beyond the `width`, start the next line
            if x > width:
                coefs_lines.append((float(x) / width, images_line))
                images_line = []
                x = 0
            x += img.size[0] + margin_size
            images_line.append(img_path)
        # finally add the last line with images
        coefs_lines.append((float(x) / width, images_line))

        # compact the lines, by reducing the `init_height`, if any with one or less images
        if len(coefs_lines) <= 1:
            break
        if any(map(lambda c: len(c[1]) <= 1, coefs_lines)):
            # reduce `init_height`
            init_height -= 0
        else:
            break

    # get output height
    out_height = 0
    for coef, imgs_line in coefs_lines:
        if imgs_line:
            out_height += int(init_height / coef) + margin_size
    if not out_height:
        print('Height of collage could not be 0!')
        return False

    # get output height
    out_height = 0
    for coef, imgs_line in coefs_lines:
        if imgs_line:
            out_height += int(init_height / coef) + margin_size
    if not out_height:
        print('Height of collage could not be 0!')
        return False

    # Check if filename has a valid extension
    _, file_extension = os.path.splitext(filename)
    if not file_extension:
        print('Invalid file extension for the output collage image!')
        return False

    collage_image = Image.new('RGB', (width, int(out_height)), (35, 35, 35))
    # put images to the collage
    y = 0
    for coef, imgs_line in coefs_lines:
        if imgs_line:
            x = 0
            for img_path in imgs_line:
                img = Image.open(img_path)
                # if need to enlarge an image - use `resize`, otherwise use `thumbnail`, it's faster
                k = (init_height / coef) / img.size[1]
                if k > 1:
                    img = img.resize((int(img.size[0] * k), int(img.size[1] * k)), Image.LANCZOS)
                else:
                    img.thumbnail((int(width / coef), int(init_height / coef)), Image.LANCZOS)
                if collage_image:
                    collage_image.paste(img, (int(x), int(y)))
                x += img.size[0] + margin_size
            y += int(init_height / coef) + margin_size

    collage_image.save(filename)
    return True

def get_images_from_folder(folder):
    """
    Get a list of image files from the specified folder and its subfolders.
    """
    images = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(os.path.join(root, file))
    return images


def main():
    # prepare argument parser
    parse = argparse.ArgumentParser(description='Photo collage maker')
    parse.add_argument('-f', '--folder', dest='folder', help='folder with images (*.jpg, *.jpeg, *.png)', default='.')
    parse.add_argument('-o', '--output', dest='output', help='output collage image filename', default='collage.png')
    parse.add_argument('-w', '--width', dest='width', type=int, help='resulting collage image width')
    parse.add_argument('-i', '--init_height', dest='init_height', type=int, help='initial height for resizing the images')
    parse.add_argument('-s', '--shuffle', action='store_true', dest='shuffle', help='enable images shuffle')
    parse.add_argument('-m', '--max_images', dest='max_images', type=int, help='maximum number of images to include in the collage')

    args = parse.parse_args()
    if not args.width or not args.init_height:
        parse.print_help()
        exit(1)

      # get images
    files = get_images_from_folder(args.folder)
    if not files:
        print('No images for making collage! Please select another directory with images!')
        exit(1)

    # Limit the number of images to the specified maximum
    max_images = args.max_images if args.max_images is not None else None
    if max_images is not None and max_images < 0:
        print('Invalid value for max_images. Please provide a non-negative integer.')
        exit(1)

    # Limit the number of images in the collage
    if max_images is not None and max_images > 0:
        files = files[:max_images]

    # shuffle images if needed
    if args.shuffle:
        random.shuffle(files)

    print('Making collage...')
    res = make_collage(files, args.output, args.width, args.init_height, max_images=args.max_images)
    if not res:
        print('Failed to create collage!')
        exit(1)
    print('Collage is ready!')


if __name__ == '__main__':
    main()

    # python3 collage.py -f "data/Snake Images" -o collage_v1.jpg -w 1280 -i 50 -s -m 156
