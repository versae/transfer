# -*- coding: utf-8 -*-
import ImageFilter
import mahotas
import operator
import scipy

from numpy import mgrid, exp
from PIL import Image, ImageDraw
from scipy import ndimage, stats

# Based on paper http://research.google.com/pubs/pub35094.html
# and calculate from CCs with h < 7 @300ppi in tabloid paper sizes
NOISE_FACTOR = 5.4264e-5


class Region(object):

    def __init__(self, x, y):
        self._pixels = [(x, y)]
        self._min_x = x
        self._max_x = x
        self._min_y = y
        self._max_y = y

    def add(self, x, y):
        self._pixels.append((x, y))
        self._min_x = min(self._min_x, x)
        self._max_x = max(self._max_x, x)
        self._min_y = min(self._min_y, y)
        self._max_y = max(self._max_y, y)

    def heigth(self):
        return abs(self._max_y - self._min_y)

    def width(self):
        return abs(self._max_x - self._min_x)

    def box(self):
        return [(self._min_x, self._min_y), (self._max_x, self._max_y)]

    def _json(self):
        return [self._min_x, self._min_y, self._max_x - self._min_x,
                self._max_y - self._min_y]


def region_serializer(python_object):
    if isinstance(python_object, Region):
        return {'__class__': 'Region',
                'box': python_object._json()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def binarize(im, threshold=None, grayscale=True, rc=False):
    if grayscale:
        out = im.convert("L")
    else:
        out = im
    if not threshold:
        if rc:
            threshold = get_rc_threshold(out, from_image=True)
        else:
            threshold = get_otsu_threshold(out, from_image=True)

    def _transform(pixel):
        if ((isinstance(pixel, (int, float)) and pixel < threshold)
            or (isinstance(pixel, (list, tuple))
                and all(map(lambda v: v < threshold, pixel[:3])))):
            return 0
        else:
            return 255

    out = out.point(_transform)
    if grayscale:
        return out.convert("1")
    else:
        return out


def count_colours(npixels, ul_pixel, lr_pixel, on_colour=(0, 0, 0),
                  off_colour=(255, 255, 255)):
    on_pixels = 0
    off_pixels = 0
    others_pixels = 0
    num_pixels = 0
    pixel_r = 0
    pixel_g = 0
    pixel_b = 0
    pixel_colours = []
    for nx in range(ul_pixel[0], lr_pixel[0] + 1):
        for ny in range(ul_pixel[1], lr_pixel[1] + 1):
            # npixels is transposed
            npixel = npixels[ny][nx]
            if all(npixel == on_colour):
                on_pixels += 1
            else:
                if all(npixel == off_colour):
                    off_pixels += 1
                else:
                    others_pixels += 1
                    pixel_r += npixel[0]
                    pixel_g += npixel[1]
                    pixel_b += npixel[2]
                    pixel_colours.append((pixel_r, pixel_g, pixel_b))
            num_pixels += 1
    others_pixels = others_pixels or 1
    median_colour = (pixel_r / others_pixels, pixel_g / others_pixels,
                     pixel_b / others_pixels)
    mode_colour = scipy.stats.mstats.mode(scipy.array(pixel_colours))[0]
    if pixel_colours and len(mode_colour) > 0:
        mode_colour = [int(c) for c in mode_colour.data[0]]
    else:
        mode_colour = (127, 127, 127)
    return (on_pixels, off_pixels, others_pixels, num_pixels,
            median_colour, mode_colour)


def remove_foreground(im, foreground_colour=(0, 0, 0),
                      background_colour=(255, 255, 255), tolerance=2):

    def fill(pixels, p1, p2, colour, replacement, inverse=False):
        for cy in xrange(p1[1], p2[1] + 1):
            for cx in xrange(p1[0], p2[0] + 1):
                # npixels is transposed
                if inverse:
                    if any(pixels[cy][cx] != colour):
                            pixels[cy][cx] = replacement
                else:
                    if all(pixels[cy][cx] == colour):
                            pixels[cy][cx] = replacement
        return pixels

    filtered_image = im.filter(ImageFilter.ModeFilter)
    grayscale_binarization = binarize(filtered_image, grayscale=False)
    binarization = binarize(grayscale_binarization, threshold=255)
#    grayscale_binarization.show()
    # pil2np transpose the matrix in some cases
    gim = pil2np(grayscale_binarization)
    bim = pil2np(binarization)
    regions = find_regions(binarization, pixel_list=True)
    heigth = filtered_image.size[1]
    filtered_regions = filter_regions(regions,
                                      noise_heigth=NOISE_FACTOR * heigth)
    for filtered_region in filtered_regions:
        for region in filtered_region:
            [p1, p2] = region.box()
            results = count_colours(gim, p1, p2, foreground_colour,
                                    background_colour)
            on, off, others, total_pixels, median_colour, mode_colour = results
            if others > off * tolerance:
                gim = fill(gim, p1, p2, foreground_colour, mode_colour)
            elif off > others:
                gim = fill(gim, p1, p2, background_colour, foreground_colour,
                           inverse=True)
            else:
                gim = fill(gim, p1, p2, foreground_colour, median_colour)
#        np2pil(gim).show()
    return np2pil(gim)


def extract_colours(im, k=None):
    bim = binarize(im.filter(ImageFilter.MedianFilter), grayscale=False)
    width, heigth = bim.size
    pixels = bim.load()
    npixels = bim.convert("RGB").load()
    for x in range(width):
        for y in range(heigth):
            px = pixels[x, y]
            if px[0] == px[1] == px[2]:
                pixels[x, y] = (255, 255, 255)
            elif k:
                # Define the neighborhood
                ul_pixel = (x - k if x >= k else 0,
                            x + k if x + k <= width else width)
                lr_pixel = (y - k if y >= k else 0,
                            y + k if y + k <= heigth else heigth)
                on_pixels = 0
                off_pixels = 0
                others_pixels = 0
                num_pixels = 0
                pixel_r = 0
                pixel_g = 0
                pixel_b = 0
                for nx in range(*ul_pixel):
                    for ny in range(*lr_pixel):
                        npixel = npixels[nx, ny]
                        if npixel == (0, 0, 0):
                            on_pixels += 1
                        elif npixel == (255, 255, 255):
                            off_pixels += 1
                        else:
                            others_pixels += 1
                        pixel_r += npixel[0]
                        pixel_g += npixel[1]
                        pixel_b += npixel[2]
                        num_pixels += 1
                max_pixels = max(on_pixels, off_pixels, others_pixels)
                if max_pixels == on_pixels or max_pixels == off_pixels:
                    pixels[x, y] = (255, 255, 255)
                else:
                    pixels[x, y] = (pixel_r / num_pixels, pixel_g / num_pixels,
                                    pixel_b / num_pixels)
    return bim.filter(ImageFilter.MedianFilter)


# Based on paper http://www.wseas.us/e-library/conferences/2009/moscow/ISCGAV/ISCGAV09.pdf
def kfill_colour(im, k=3, accuracy=0):

    def kfill_count_core_pixel(tmp, x, y, c_lr, colour):
        core_pixel = 0
        for cy in xrange(y, c_lr["y"] + 1):
            for cx in xrange(x, c_lr["x"] + 1):
                if all([(c == colour[i]) for i, c in enumerate(tmp[cx][cy])]):
                    core_pixel += 1
        return core_pixel

    def kfill_median_colour(tmp, x, y, c_lr, k=False):
        core_pixel_r = 0
        core_pixel_g = 0
        core_pixel_b = 0
        num_pixels = 0
        size_x, size_y = res.shape[:2]
        y_upper = (y, y - 1)[k and y > 1]
        y_lower = (c_lr["y"] + 1, c_lr["y"] + 2)[k and c_lr["y"] + 1 > size_y]
        x_upper = (x, x - 1)[x > 1 and k]
        x_lower = (c_lr["x"] + 1, c_lr["x"] + 2)[k and c_lr["x"] + 1 > size_x]
        for cy in xrange(y_upper, y_lower):
            for cx in xrange(x_upper, x_lower):
                core_pixel = tmp[cx][cy]
                core_pixel_r += core_pixel[0]
                core_pixel_g += core_pixel[1]
                core_pixel_b += core_pixel[2]
                num_pixels += 1
        return (core_pixel_r / num_pixels, core_pixel_g / num_pixels,
                core_pixel_b / num_pixels)

    def kfill_set_core_pixel(res, x, y, c_lr, colour=None, orig=None):
        # Condition out of the loops
        if orig == None:
            for cy in xrange(y, c_lr["y"] + 1):
                for cx in xrange(x, c_lr["x"] + 1):
                    res[cx][cy] = colour
        else:
            for cy in xrange(y, c_lr["y"] + 1):
                for cx in xrange(x, c_lr["x"] + 1):
                    res[cx][cy] = orig[cx][cy]
        return res

    res = pil2np(im.convert("RGB"))
    tmp = pil2np(im.convert("RGB"))
    src_size_x, src_size_y = res.shape[:2]
    # windows position (lower right core coordinate)
    c_lr = {
        'x': 0,
        'y': 0,
    }
    ncp = (k - 2) * (k - 2) # number of core pixel
    ncp_required = 1 + (ncp / 2.0) # number of core pixel (modified version)
    colour_on = (0, 0, 0)
    colour_off = (255, 255, 255)
    # move window over the image
    for y in xrange(0, src_size_y - (k - 3)):
        for x in xrange(0, src_size_x - (k - 3)):
            # calculate lower right core coordinate
            c_lr["x"] = x + (k - 3)
            c_lr["y"] = y + (k - 3)
            # count core ON / OFF pixel
            core_pixel_on = kfill_count_core_pixel(tmp, x, y, c_lr, colour_on)
            core_pixel_off = kfill_count_core_pixel(tmp, x, y, c_lr,
                                                    colour_off)
            if core_pixel_on >= ncp_required or core_pixel_off >= ncp_required:
                median_colour = kfill_median_colour(tmp, x, y, c_lr, k=True)
                res = kfill_set_core_pixel(res, x, y, c_lr,
                                           colour=median_colour)
            elif core_pixel_on > accuracy:
                median_colour = kfill_median_colour(tmp, x, y, c_lr)
                res = kfill_set_core_pixel(res, x, y, c_lr,
                                           colour=median_colour)
            else:
                res = kfill_set_core_pixel(res, x, y, c_lr, orig=tmp)
    del tmp
    return np2pil(res)


# Adapted to kfill modified through python-gamera from http://www.cs.buu.ac.th/~krisana/cv/paper/Apccas98.pdf
def kfill(im, k=2):

    def is_black(p):
        if isinstance(p, (list, dict)):
            return True
        return bool(p)

    def equation_satisfied(n, r, c):
        return ((c <= 1) and ((n > 3 * k - 4)
                              or (n == 3 * k - 4) and (r == 2)))

    def kfill_count_core_pixel(tmp, x, y, c_lr):
        core_pixel = 0
        for cy in xrange(y, c_lr["y"] + 1):
            for cx in xrange(x, c_lr["x"] + 1):
                if tmp[cx][cy] == 0:
                    core_pixel += 1
        return core_pixel

    def kfill_set_core_pixel(res, x, y, c_lr, v):
        for cy in xrange(y, c_lr["y"] + 1):
            for cx in xrange(x, c_lr["x"] + 1):
                res[cx][cy] = v
        return res

    def kfill_get_condition_variables(tmp, k, x, y, size_x, size_y):
        # upper left corner of current window
        ul_x, ul_y = 0, 0
        # upper right corner of current window
        ur_x, ur_y = 0, 0
        # lower left corner of current window
        ll_x, ll_y = 0, 0
        # lower right corner of current window
        lr_x, lr_y = 0, 0
        nnp = 4 * (k - 1) # total number of neighborhood pixels
        nh_pixel = [] # array for neighborhood pixel
        nh_pixel_count = 0
        corner_pixel_count, nh_ccs = 0, 0
        pixelvalue = None
        # calculate window borders
        ul_x = x - 1
        ul_y = y - 1
        ur_x = x + k - 2
        ur_y = y - 1
        ll_x = x - 1
        ll_y = y + k - 2
        lr_x = x + k - 2
        lr_y = y + k - 2
        # fill array with neighborhood and count neighborhood ON pixel
        for ul_to_ur_np in xrange(ul_x, ur_x):
            if ul_to_ur_np < 0 or y - 1 < 0:
                pixelvalue = 0
            else:
                pixelvalue = tmp[ul_to_ur_np][y - 1]
            nh_pixel.append(is_black(pixelvalue))
            if is_black(pixelvalue):
                nh_pixel_count += 1
        for ur_to_lr_np in xrange(ur_y, lr_y):
            if ur_to_lr_np < 0 or x + k - 2 > size_x - 1:
                pixelvalue = 0
            else:
                pixelvalue = tmp[x + k - 2][ur_to_lr_np]
            nh_pixel.append(is_black(pixelvalue))
            if is_black(pixelvalue):
                nh_pixel_count += 1
        for lr_to_ll_np in xrange(lr_x, ll_x, -1):
            if lr_to_ll_np > size_x - 1 or y + k - 2 > size_y - 1:
                pixelvalue = 0
            else:
                pixelvalue = tmp[lr_to_ll_np][y + k - 2]
            nh_pixel.append(is_black(pixelvalue))
            if is_black(pixelvalue):
                nh_pixel_count += 1
        for ll_to_ul_np in xrange(ll_y, ul_y, -1):
            if x - 1 < 0 or ll_to_ul_np > size_y - 1:
                pixelvalue = 0
            else:
                pixelvalue = tmp[x - 1][ll_to_ul_np]
            nh_pixel.append(is_black(pixelvalue))
            if is_black(pixelvalue):
                nh_pixel_count += 1
        # count corner ON pixel
        corner_pixel_count = int(nh_pixel[(k - 1) * 0]) + \
                             int(nh_pixel[(k - 1) * 1]) + \
                             int(nh_pixel[(k - 1) * 2]) + \
                             int(nh_pixel[(k - 1) * 3])
        # get ccs in neighborhood
        nh_ccs = 0
        for nhpixel in xrange(0, len(nh_pixel)):
            nh_ccs += abs(nh_pixel[(nhpixel + 1) % nnp] - nh_pixel[nhpixel])
        nh_ccs = nh_ccs / 2
        n = nh_pixel_count
        r = corner_pixel_count
        c = nh_ccs
        del nh_pixel
        return n, r, c

    res = pil2np(im.convert("L"))
    tmp = pil2np(im.convert("L"))
    src_size_x, src_size_y = res.shape
    x, y = 0, 0 # windows position (upper left core coordinate)
    # windows position (lower right core coordinate)
    c_lr = {
        'x': 0,
        'y': 0,
    }
    ncp = (k - 2) * (k - 2) # number of core pixel
    ncp_required = ncp / 2.0 # number of core pixel required (modified version)
    core_pixel = 0 # number of ON core pixel
    r = 0 # number of pixel in the neighborhood corners
    n = 0 # number of neighborhood pixel
    c = 0 # number of ccs in neighborhood
    # move window over the image
    for y in xrange(0, src_size_y - (k - 3)):
        for x in xrange(0, src_size_x - (k - 3)):
            # calculate lower right core coordinate
            c_lr["x"] = x + (k - 3)
            c_lr["y"] = y + (k - 3)
            # count core ON pixel
            core_pixel = kfill_count_core_pixel(tmp, x, y, c_lr)
            # ON >= (k-2)^2/2 ?
            if core_pixel >= ncp_required:
                # Examine in the Neighborhood
                n, r, c = kfill_get_condition_variables(tmp, k, x, y,
                                                        src_size_x, src_size_y)
                n = 4 * (k-1) - n
                r = 4 - r
                # eq. satisfied?
                if equation_satisfied(n, r, c):
                    res = kfill_set_core_pixel(res, x, y, c_lr, 0)
                else:
                    res = kfill_set_core_pixel(res, x, y, c_lr, 255)
            else:
                # Examine in the Neighborhood
                n, r, c = kfill_get_condition_variables(tmp, k, x, y,
                                                        src_size_x, src_size_y)
                # eq. satisfied?
                if equation_satisfied(n, r, c):
                    res = kfill_set_core_pixel(res, x, y, c_lr, 255)
                else:
                    res = kfill_set_core_pixel(res, x, y, c_lr, 0)
    del tmp
    return np2pil(res)


def extract_handwritten_text(im, factor=2):

    def _extract_handwritten_text(im, factor):
        factor = factor * 1.0
        bim = binarize(im.point(lambda x: x * factor), grayscale=False)
        pixels = bim.load()
        width, heigth = im.size
        for x in range(width):
            for y in range(heigth):
                px = pixels[x, y]
                if px[0] == px[1] == px[2]:
                    pixels[x, y] = (255, 255, 255)
        pixels = bim.load()
        bmask = bim.convert("1")
        mpixels = bmask.load()
        for x in range(width):
            for y in range(heigth):
                if mpixels[x, y] == 0:
                    pixels[x, y] = (255, 255, 255)
        notes = binarize(bim, rc=True)
        return notes

    image = im.filter(ImageFilter.MedianFilter)
    if isinstance(factor, (list, tuple)):
        bim = _extract_handwritten_text(image, factor=factor[0])
        w, h = bim.size
        for f in factor[1:]:
            fim = _extract_handwritten_text(image, factor=f)
            bpixels = bim.load()
            fpixels = fim.load()
            for x in range(w):
                for y in range(h):
                    if fpixels[x, y] == 0:
                        bpixels[x, y] = 0
    else:
        bim = _extract_handwritten_text(image, factor=factor)
    return bim


def remove_noise(im, size=2):
    out = im.convert("L")
    out = gaussian_filter(out, size=size)
    out = binarize(out, rc=True)
    return out


def no_white_mask(im):
    return binarize(im, threshold=255).convert("1")


def draw_overlay(original_image, mask_image, colour=(255, 0, 0)):
    out = original_image.convert("RGB")
    width, heigth = out.size
    opixels = out.load()
    mpixels = mask_image.load()
    for x in range(width):
        for y in range(heigth):
            if not mpixels[x, y]:
                opixels[x, y] = colour
    return out


# Based on http://www.ece.umassd.edu/faculty/acosta/icassp/icassp_2004/pdfs/0300229.pdf
def activity_detector(im, radius=10, increment=16):
    regions = find_regions(im)
    width, height = im.size
    mask = Image.new("L", (width, height), 0)
    pixels = mask.load()
    for region in regions:
        [(min_x, min_y), (max_x, max_y)] = region.box()
        for x in range(min_x - radius, max_x + radius + 1):
            for y in range(min_y - radius, max_y + radius + 1):
                try:
                    pixels[x, y] += increment
                except IndexError:
                    pass
    return mask


def draw_regions(original_image, mask_image, outline=["green", "blue", "red"],
                 fill=[None, None, None], mode_pass=[False, False, False]):
    heigth = original_image.size[1]
    regions = find_regions(mask_image)
    filtered_regions = filter_regions(regions,
                                      noise_heigth=NOISE_FACTOR * heigth)
    out = original_image.convert("RGB")
    for i, region in enumerate(filtered_regions):
        if mode_pass[i]:
            widths = scipy.asarray([f.width() for f in filtered_regions[i]])
            heigths = scipy.asarray([f.heigth() for f in filtered_regions[i]])
            mode_width = float(scipy.stats.mstats.mode(widths)[0])
            mode_heigth = float(scipy.stats.mstats.mode(heigths)[0])
        if outline[i] or fill[i]:
            draw = ImageDraw.Draw(out)
            for r in filtered_regions[i]:
                if (not mode_pass[i]
                    or (mode_pass[i]
                        and (mode_width - mode_pass[i] <= r.width() \
                             <= mode_width + mode_pass[i]
                             or mode_heigth - mode_pass[i] <= r.heigth() \
                             <= mode_heigth + mode_pass[i]))):
                    draw.rectangle(r.box(), outline=outline[i], fill=fill[i])
            del draw
    return out


def process_image(im, factor=[2, 0.25]):
    bim = extract_handwritten_text(im, factor=factor)
    nim = remove_noise(bim)
    return draw_overlay(im, nim)


def gaussian_filter(im, size=5):
    return np2pil(ndimage.gaussian_filter(pil2np(im), size))


# Gauss filter taken from http://rcjp.wordpress.com/2008/04/02/gaussian-pil-image-filter/
def gaussian_grid(size=5):
    """
    Create a square grid of integers of gaussian shape
    e.g. gaussian_grid() returns
    array([[ 1,  4,  7,  4,  1],
           [ 4, 20, 33, 20,  4],
           [ 7, 33, 55, 33,  7],
           [ 4, 20, 33, 20,  4],
           [ 1,  4,  7,  4,  1]])
    """
    m = size / 2
    n = m + 1 # Remember python is 'upto' n in the range below
    x, y = mgrid[0 - m:n, m:n]
    # Multiply by a factor to get 1 in the corner of the grid
    # i.e., for a 5x5 grid -> fac * exp(-0.5 * (2**2 + 2**2)) = 1
    fac = exp(m ** 2)
    g = fac * exp(-0.5 * (x ** 2 + y ** 2))
    return g.round().astype(int)


class GaussianFilter(ImageFilter.BuiltinFilter):

    def __init__(self, size=5, *args, **kwargs):
        self.name = "Gaussian blur filter"
        gg = gaussian_grid(size).flatten().tolist()
        self.filterargs = (size, size), sum(gg), 0, tuple(gg)


# Parts taken from: http://stackoverflow.com/questions/1989987/my-own-ocr-program-in-python
def find_regions(im, pixel_list=True):
    width, heigth = im.size
    regions = {}
    pixel_region = [[0 for y in range(heigth)] for x in range(width)]
    equivalences = {}
    n_regions = 0
    # First pass. Find regions.
    for x in xrange(width):
        for y in xrange(heigth):
            # Look for a black pixel
            pixel = im.getpixel((x, y))
            if pixel in (0, (0, 0, 0), (0, 0, 0, 255)):
                # Get the region number from north or west
                # or create new region
                region_n = pixel_region[x-1][y] if x > 0 else 0
                region_w = pixel_region[x][y-1] if y > 0 else 0
                max_region = max(region_n, region_w)
                if max_region > 0:
                    # A neighbour already has a region
                    # New region is the smallest > 0
                    new_region = min(filter(lambda i: i > 0,
                                            (region_n, region_w)))
                    # Update equivalences
                    if max_region > new_region:
                        if max_region in equivalences:
                            equivalences[max_region].add(new_region)
                        else:
                            equivalences[max_region] = set((new_region, ))
                else:
                    n_regions += 1
                    new_region = n_regions
                pixel_region[x][y] = new_region
    # Scan image again, assigning all equivalent regions the same region value.
    for x in xrange(width):
        for y in xrange(heigth):
                r = pixel_region[x][y]
                if r > 0:
                    while r in equivalences:
                        r = min(equivalences[r])
                    if not r in regions:
                        regions[r] = Region(x, y)
                    else:
                        regions[r].add(x, y)
    return list(regions.itervalues())


def filter_regions(regions, noise_heigth=7):
    small, medium, large = [], [], []
    heigths, widths, remainder = [], [], []
    for region in regions:
        if region.heigth() < noise_heigth:
            small.append(region)
        else:
            remainder.append(region)
    for region in remainder:
        heigths.append(region.heigth())
        widths.append(region.width())
    h_75 = stats.mstats.scoreatpercentile(heigths, 75)
    for region in remainder:
        region_heigth = region.heigth()
        if region_heigth < h_75 / 2:
            small.append(region)
        elif region_heigth > 2 * h_75 or region.width() > 8 * h_75:
            large.append(region)
        else:
            medium.append(region)
    return small, medium, large


def get_otsu_threshold(im, from_image=False):
    if from_image:
        img = scipy.misc.pilutil.fromimage(im)
    else:
        img = scipy.misc.pilutil.imread(im)
    otsu_threshold = mahotas.thresholding.otsu(img)
    return otsu_threshold


def get_rc_threshold(im, from_image=False):
    if from_image:
        img = scipy.misc.pilutil.fromimage(im)
    else:
        img = scipy.misc.pilutil.imread(im)
    otsu_threshold = mahotas.thresholding.rc(img)
    return otsu_threshold


def equalize(im):
    # Taken from http://effbot.org/zone/pil-histogram-equalization.htm
    lut = []
    h = im.histogram()
    for b in range(0, len(h), 256):
        # Step size
        step = reduce(operator.add, h[b:b + 256]) / 255
        # Create equalization lookup table
        n = 0
        for i in range(256):
            lut.append(n / step)
            n = n + h[i + b]
    return im.point(lut)


def thumbnail(im, max_heigth=500):
    if im.size[1] <= max_heigth:
        return im
    aspect_ratio = float(im.size[0]) / float(im.size[1])
    if im.size[1] > 500:
        return im.resize((aspect_ratio * max_heigth, max_heigth),
                         Image.ANTIALIAS)


def pil2np(im):
    if im.mode == '1':
        return scipy.array(scipy.asarray(im.convert("L")))
    return scipy.array(scipy.asarray(im))


def np2pil(im):
    return Image.fromarray(im)
