# -*- coding: utf-8 -*-
import ImageFilter
import mahotas
import operator
import scipy

from numpy import mgrid, exp
from PIL import Image, ImageDraw
from scipy import ndimage, stats

# Based on paper http://research.google.com/pubs/pub35094.html
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

    def height(self):
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
    return out


def extract_handwritten_text(im, factor=2):

    def _extract_handwritten_text(im, factor):
        factor = factor * 1.0
        bim = binarize(im.point(lambda x: x * factor), grayscale=False)
        pixels = bim.load()
        width, height = im.size
        for x in range(width):
            for y in range(height):
                px = pixels[x, y]
                if px[0] == px[1] == px[2]:
                    pixels[x, y] = (255, 255, 255)
        pixels = bim.load()
        bmask = binarize(bim)
        mpixels = bmask.load()
        for x in range(width):
            for y in range(height):
                if mpixels[x, y] == 0:
                    pixels[x, y] = (255, 255, 255)
        notes = binarize(bim, rc=True)
        return notes

    if isinstance(factor, (list, tuple)):
        bim = _extract_handwritten_text(im, factor=factor[0])
        w, h = bim.size
        for f in factor[1:]:
            fim = _extract_handwritten_text(im, factor=f)
            bpixels = bim.load()
            fpixels = fim.load()
            for x in range(w):
                for y in range(h):
                    if fpixels[x, y] == 0:
                        bpixels[x, y] = 0
    else:
        bim = _extract_handwritten_text(im, factor=factor)
    return bim


def remove_noise(im, size=2):
    out = im.convert("L")
    out = gaussian_filter(out, size=size)
    out = binarize(out, rc=True)
    return out


def draw_overlay(original_image, mask_image, color=(255, 0, 0)):
    out = original_image.convert("RGB")
    width, height = out.size
    opixels = out.load()
    mpixels = mask_image.load()
    for x in range(width):
        for y in range(height):
            if not mpixels[x, y]:
                opixels[x, y] = color
    return out


def draw_regions(original_image, mask_image):
    height = original_image.size[1]
    regions = find_regions(mask_image)
    filtered_regions = filter_regions(regions,
                                      noise_heigth=NOISE_FACTOR * height)
    draw = ImageDraw.Draw(original_image)
    for r in filtered_regions[2]:
        draw.rectangle(r.box(), outline="red")
    del draw
    draw = ImageDraw.Draw(original_image)
    for r in filtered_regions[1]:
        draw.rectangle(r.box(), outline="green")
    del draw
    draw = ImageDraw.Draw(original_image)
    for r in filtered_regions[0]:
        draw.rectangle(r.box(), outline="blue")
    del draw
    return original_image


def process_image(im, factor=[2, 0.25]):
    bim = extract_handwritten_text(im, factor=factor)
    nim = remove_noise(bim).convert("1")
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
    x, y = mgrid[-m:n, -m:n]
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
def find_regions(im):
    width, height = im.size
    regions = {}
    pixel_region = [[0 for y in range(height)] for x in range(width)]
    equivalences = {}
    n_regions = 0
    # First pass. Find regions.
    for x in xrange(width):
        for y in xrange(height):
            # Look for a black pixel
            if im.getpixel((x, y)) in (0, (0, 0, 0), (0, 0, 0, 255)):
                # Get the region number from north or west
                # or create new region
                region_n = pixel_region[x-1][y] if x > 0 else 0
                region_w = pixel_region[x][y-1] if y > 0 else 0
                max_region = max(region_n, region_w)
                if max_region > 0:
                    # A neighbour already has a region
                    # new region is the smallest > 0
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
        for y in xrange(height):
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
    heights, widths, remainder = [], [], []
    for region in regions:
        if region.height() < noise_heigth:
            small.append(region)
        else:
            remainder.append(region)
    for region in remainder:
        heights.append(region.height())
        widths.append(region.width())
    h_75 = stats.mstats.scoreatpercentile(heights, 75)
    for region in remainder:
        region_height = region.height()
        if region_height < h_75 / 2:
            small.append(region)
        elif region_height > 2 * h_75 or region.width() > 8 * h_75:
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


def thumbnail(im, max_height=500):
    aspect_ratio = float(im.size[0]) / float(im.size[1])
    if im.size[0] > 500:
        return im.resize((aspect_ratio * max_height, max_height),
                         Image.ANTIALIAS)


def pil2np(im):
    return scipy.misc.pilutil.fromimage(im)


def np2pil(im):
    return scipy.misc.pilutil.toimage(im)
