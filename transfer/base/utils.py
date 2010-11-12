# -*- coding: utf-8 -*-


class Region():

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

    def box(self):
        return [(self._min_x, self._min_y), (self._max_x, self._max_y)]


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
            if im.getpixel((x, y)) == (0, 0, 0, 255): # Black
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
