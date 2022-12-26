from PIL import Image
from PIL import ImageDraw

import PIL.ImageFont
import PIL.ImageOps

import numpy as np

# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#
# Uses Direct PIL import
#
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def open_img(path):
    return Image.open(path)

# dims: (left, top, right, bottom)
# dims are the dims needed to make the box to cut out of og img, not how much to trim from each side
def crop_img(img, dims):
    return img.crop(dims)

# dims: (left, top, right, bottom)
# cuts dim amount off of og img from each side
def crop_from_each_side(img, dims):
    width, height = img.size
    return img.crop((dims[0], dims[1], width - dims[2], height - dims[3]))


def show_img_from_path(img_path):
    img = open_img(img_path)
    img.show()


# dims: like (5185, 4000)
def make_solid_color_img(dims, color, out_file_path):
    img = Image.new('RGB', dims, color)
    img.save(out_file_path)


def invert_colors(img):
    return PIL.ImageOps.invert(img)



# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#
# Pixel Color Grid Tools
#
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def get_pixel_color_grid_from_path(input_img_path):
    img = open_img(input_img_path)
    return get_pixel_color_grid(img)

# returns a list of lists showing the rgb value of every pixel in an image
# not very efficient
def get_pixel_color_grid(input_img):
    in_img_w, in_img_h = input_img.size

    pixel_color_grid = []
    for y in range(in_img_h):
        row_l = []
        for x in range(in_img_w):
            rgb = input_img.getpixel((x,y))
            row_l.append(rgb)
        pixel_color_grid.append(row_l)
    return pixel_color_grid




def make_img_from_pixel_color_grid(pixel_color_grid):
    w = len(pixel_color_grid)
    h = len(pixel_color_grid[0])
    dims = (w, h)
    img = Image.new('RGB', dims, 'white')

    for x in range(w):
        for y in range(h):
            img.putpixel((x,y), pixel_color_grid[y][x])
    return img

def show_pixel_color_grid_as_img(pixel_color_grid):
    make_img_from_pixel_color_grid(pixel_color_grid).show()



# scans pixel_color_grid from top and returns row num of first row to contain a pixel that
# is different from dont_care_color color
def get_row_num_of_first_color_diff(pixle_color_grid, dont_care_color):
    for row_num, row_l in enumerate(pixle_color_grid):
        for rgb in row_l:
            if rgb != dont_care_color:
                return row_num
    raise Exception('ERROR:  image is all one color')



# degrees must be 90, 180, or 270
def rotate_pixel_color_grid(in_grid, degrees):
    grid_to_rotate = in_grid
    np_grid = np.rot90(grid_to_rotate, k = 4 - (degrees / 90))

    new_pcg = []
    for row_l in np_grid:
        new_pcg_row_l = []
        for rgb in row_l:
            new_pcg_row_l.append(tuple(rgb))
        new_pcg.append(new_pcg_row_l)
    return new_pcg


# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#
# Simple Tools
#
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def pixel_color(img, x, y):
    pcg = get_pixel_color_grid(img)
    return pcg[y][x]

# border can be an int (for adding same border to all sides) or tuple (left, top, right, bottom)
def add_border(img, border, color=0):
    if isinstance(border, int) or isinstance(border, tuple):
        return PIL.ImageOps.expand(img, border=border, fill=color)
    else:
        raise RuntimeError('Border is not an integer or tuple!')


# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#
# Complex Tools
#
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv


    # trims pic inward from each side until at lease one pixel in the row/col is not the same color as the original border
def trim_border(img):
    in_img = img.convert('RGB')

    pixel_color_grid = get_pixel_color_grid(in_img)
    border_color = pixel_color_grid[0][0]

    top_crop     = get_row_num_of_first_color_diff(pixel_color_grid, border_color)
    left_crop    = get_row_num_of_first_color_diff(rotate_pixel_color_grid(pixel_color_grid , 90), border_color)
    bottom_crop  = get_row_num_of_first_color_diff(rotate_pixel_color_grid(pixel_color_grid , 180), border_color)
    right_crop   = get_row_num_of_first_color_diff(rotate_pixel_color_grid(pixel_color_grid , 270), border_color)

    return crop_from_each_side(in_img, (left_crop, top_crop, right_crop, bottom_crop))




def simple_monospace_write_txt_on_img(img, lines, font, txt_color):
    draw = ImageDraw.Draw(img)
    letter_w, letter_h = draw.textsize("A", font)
    Image.MAX_IMAGE_PIXELS = 1000000000   #need this here

    line_num = 0
    for line_num in range(len(lines)):
        line = lines[line_num]
        x_draw = 0

        for letter_num in range(len(line)):
            letter = line[letter_num]
            draw.text((x_draw, letter_h * line_num), letter, txt_color, font)
            x_draw += letter_w
        line_num += 10.

    return img

def get_crop_coords_from_border_size_d(img, border_size_d):
    """
        Gets coords for cropping out border with output of _get_color_border_size_d_fast__if_exists()
        - w: Width of the output video (out_w). It defaults to iw. This expression is evaluated only once during the filter configuration.
        - h: Height of the output video (out_h). It defaults to ih. This expression is evaluated only once during the filter configuration.
        - x: Horizontal position, in the input video, of the left edge of the output video. It defaults to (in_w-out_w)/2. This expression is evaluated per-frame.
        - y: Vertical position, in the input video, of the top edge of the output video. It defaults to (in_h-out_h)/2. This expression is evaluated per-frame.
    """
    print(f"in _get_crop_coords_from_border_size_d() - {img.size=}")
    w = img.width - border_size_d["left"] - border_size_d["right"]
    h = img.height - border_size_d["top"] - border_size_d["bottom"]
    x = border_size_d["left"]
    y = border_size_d["top"]
    return w,h,x,y



def get_color_border_size_d_fast__if_exists(img, color_rgb, ret_false_if_no_border = True):
    """
        Returns dict of # pixel size of color border of each size.
        - Does this fast by checking individual lines to find min border instead of each individual pixel.
            - B/c of this, false positives possible, change _get_const_y_pos_l() to adjust if needed
        - Focused on returning False in the case there is no border ASAP
        - If ret_false_if_no_border == False, will just return normal border_size_d with all values = 0
    """

    def _get_const_y_pos_l(img_h):
        """ If too many errors, add more/different y_pos"""
        return [
                int(img_h * 0.25),
                int(img_h * 0.50),
                int(img_h * 0.75)
            ]

    def _get_horz_num_pixels_until_not_color_multiple_lines(img, y_pos_l, color_rgb):

        def _get_horz_num_pixels_until_not_color_single_line(img, y_pos, color_rgb):
            print("in {_get_horz_num_pixels_until_not_color_single_line()} {y_pos=}")
            img_w, img_h = img.size

            if y_pos < 0 or y_pos > img_h:
                raise Exception(f"Error: Invalid y_pos ({y_pos=}) for given img dimensions: {img_w=}, {img_h=}")

            # Could make more efficient with binary search, skipping given num pixels, etc.
            for x in range(img_w):
                if img.getpixel((x,y_pos)) != color_rgb:
                    print("Returning: ", (x,y_pos), x)
                    return x


        min_num_pixels_until_not_color = None

        for y_pos in y_pos_l:
            num_pixels_until_not_color = _get_horz_num_pixels_until_not_color_single_line(img, y_pos, color_rgb)

            # If ever find spot with no border, means edge has no border so no need to check other y_pos'
            if num_pixels_until_not_color == 0:
                return 0

            if min_num_pixels_until_not_color == None:
                min_num_pixels_until_not_color = num_pixels_until_not_color

            # If not giving good results, maybe should add a check to require a given # of matches?
            min_num_pixels_until_not_color = min(min_num_pixels_until_not_color, num_pixels_until_not_color)
            print(f"....{min_num_pixels_until_not_color=}")
        return min_num_pixels_until_not_color

    border_size_d = {"left"  : 0,
                    "bottom" : 0,
                    "right"  : 0,
                    "top"    : 0}

    # Set what happens if no color border is found
    if ret_false_if_no_border:
        ret_on_no_border = False
    else:
        ret_on_no_border = border_size_d

    # If corners of img is not given color, must not have border of given color
    if  img.getpixel((0,0)) != 0 or \
        img.getpixel((img.width - 1, img.height - 1)) != 0:
        return ret_on_no_border

    border_size_d["left"]   = _get_horz_num_pixels_until_not_color_multiple_lines(img                         , _get_const_y_pos_l(img.height), color_rgb)
    border_size_d["top"]    = _get_horz_num_pixels_until_not_color_multiple_lines(img.rotate(90,  expand=True), _get_const_y_pos_l(img.width ), color_rgb)
    border_size_d["right"]  = _get_horz_num_pixels_until_not_color_multiple_lines(img.rotate(180, expand=True), _get_const_y_pos_l(img.height), color_rgb)
    border_size_d["bottom"] = _get_horz_num_pixels_until_not_color_multiple_lines(img.rotate(270, expand=True), _get_const_y_pos_l(img.width ), color_rgb)

    # ret_on_no_border if all sides 0
    for size in border_size_d.values():
        if size != 0:
            return border_size_d
    return ret_on_no_border


# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
#
# By_Path Wrappers
#
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

def edit_img_by_path(func, args, in_img_path, out_img_path):
    img = Image.open(in_img_path)
    if args == None:
        output_img = func(img)
    else:
        output_img = func(img, *args)
    output_img.save(out_img_path)



def add_border_by_path(in_img_path, out_img_path, border, color=0):
    edit_img_by_path(add_border, [border, color], in_img_path, out_img_path)

def invert_colors_by_path(in_img_path, out_img_path):
    edit_img_by_path(invert_colors, None, in_img_path, out_img_path)

def simple_monospace_write_txt_on_img_by_path(in_img_path, out_img_path, lines, font, txt_color):
    edit_img_by_path(simple_monospace_write_txt_on_img, [lines, font, txt_color], in_img_path, out_img_path)

def trim_border_by_path(in_img_path, out_img_path):
    edit_img_by_path(trim_border, None, in_img_path, out_img_path)


if __name__ == '__main__':
    print('in pil_utils main...')
    img = Image.open("C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\ignore\\test_img.jpg")

    border_size_d = get_color_border_size_d_fast__if_exists(img, color_rgb=0, ret_false_if_no_border = True)

    get_crop_coords_from_border_size_d(img, border_size_d)


    # trim_border_by_path("C:\\Users\\Brandon\\Documents\\Personal_Projects\\g_card_tools\\code_card\\barcode.png", "C:\\Users\\Brandon\\Documents\\Personal_Projects\\g_card_tools\\code_card\\barcode_trimmed_border.png")

# #     in_img_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\white_paper_art_big_data\\white_paper_graphs\\pordh4hewmc01.jpg"
# #     out_img_path = "C:\\Users\\Brandon\\Documents\\Personal_Projects\\white_paper_art_big_data\\white_paper_graphs\\pordh4hewmc01_border.jpg"
# # #     add_border_by_path(in_img_path, out_img_path, 200, (33,33,33))
# #
# #     import font_tools
# #     font = font_tools.load_font()
# #     lines = ['test line', 'line 222222222222222222']
# #     txt_color = 'yellow'
# #     simple_monospace_write_txt_on_img_by_path(in_img_path, out_img_path, lines, font, txt_color)
# #     show_img_from_path(out_img_path)
# #
# #
# #
# #
# # #     input_path = "..\\white_paper_graphs\\btc_graph.jpg"#'../example_pics/big_black_a.jpg'
# # #     output_path = '../example_pics/trimmed_green_triangle.jpg'
# # #
# # #     trim_border(input_path, output_path)
# # #     show_img_from_path(output_path)
# #
# # #     pcg = get_pixel_color_grid_from_path(input_path)
# # #     show_pixel_color_grid_as_img(pcg)
# # #
# # #     pcg2 = rotate_pixel_color_grid(pcg, 90)
# # #     show_pixel_color_grid_as_img(pcg2)
# # #
# # #     pcg3 = rotate_pixel_color_grid(pcg, 180)
# # #     show_pixel_color_grid_as_img(pcg3)
# #
# #     invert_colors_by_path("C:\\Users\\Brandon\\Documents\\Personal_Projects\\white_paper_art_big_data\\white_paper_graphs\\btc_g.JPG","C:\\Users\\Brandon\\Documents\\Personal_Projects\\white_paper_art_big_data\\white_paper_graphs\\btc_graph_inverted.JPG")
# #
# #
# #
# # #     test_m = [[0,0,0],
# # #               [1,2,3]]
# # #     for r in rotate_pixel_color_grid(test_m, 90):
# # #         print(r)
#
#
#     OUTPUT_VID_DIMS_L =[(3840,2160),
#                         (2560,1440),
#                         (1920,1080),
#                         (1280, 720),
#                          (854, 480),
#                          (640, 360),
#                          (426, 240)]
#
#     x, y = OUTPUT_VID_DIMS_L[7]
# #     x = 1000
# #     y = x
#
#     test_pics_dir_path = 'C:\\Users\\Brandon\\Documents\\Personal_Projects\\vid_m_comp_big_data\\test_pics'
#     un_labeled_path = test_pics_dir_path +  '\\tp_' + str(x) + 'x' + str(y) + '.png'
# #     labeled_path    = test_pics_dir_path +  '\\tpl_' + str(x) + 'x' + str(y)
#     make_solid_color_img((x, y), 'green', un_labeled_path )
# #     simple_monospace_write_txt_on_img_by_path(un_labeled_path, labeled_path, [str(x) + 'x' + str(y)], font, txt_color):


