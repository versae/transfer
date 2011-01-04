import Image
from random import randint

BACKGROUND_COLOR = 255

class Node:
    def __init__(self):
        # Coarsening properties
        self.pixels = None
        self.color = 0
        self.marked = False

        # Node properties
        self.location = (0,0)
        self.relative_width = 0
        self.relative_height = 0
        self.number_of_pixels = 0
        # Only for patches self.foreground_density = 0
        self.average_stroke_width = 0
        
        # Only for non-binary self.crossing_number 
        self.variance_of_projection = 0 #?
        self.maximum_runlength = 0 #?
        # Edge Properties
        self.components_number = 0 # Common edges
        self.width_mean = 0
        self.height_mean = 0
        self.width_variance = 0
        self.height_variance = 0
        self.pixels_variance = 0
        self.stroke_width_variance = 0
        # Only patch self.hole_ratio = 0
        # Only patch self.overlap_ratio = 0
        
    def get_new_location(self):
        count_i = 0
        count_j = 0
        for i,j in self.pixels:
            count_i += i
            count_j += j
        count_i /= len(self.pixels)
        count_j /= len(self.pixels)
        return (count_i, count_j)

    def get_min_max_coordinates(self):
        min_width = 99999 #FIXME
        max_width = 0
        min_height = 99999
        max_height = 0
        for pixel in self.pixels:
            if pixel[0] > max_width:
                max_width = pixel[0]
            if pixel[0] < min_width:
                min_width = pixel[0]
            if pixel[1] > max_height:
                max_height = pixel[1]
            if pixel[1] < min_height:
                min_height = pixel[1]
        return (min_width, max_width, min_height, max_height)

    def get_relative_width_and_height(self):
        min_width, max_width, min_height, max_height = self.get_min_max_coordinates()
        return (max_width-min_width, max_height-min_height)

    def is_edge_pixel(self, pixel):
        i,j = pixel
        return not ((i-1,j) in self.pixels and (i,j-1) in self.pixels \
            and (i+1,j) in self.pixels and (i,j+1) in self.pixels)

    def get_average_stroke_width(self):
        edge_pixels = [p for p in self.pixels if self.is_edge_pixel(p)]
        return float(len(edge_pixels))/len(self.pixels)

    def update_local_properties(self):
        self.number_of_pixels = len(self.pixels)
        self.location = self.get_new_location()
        self.relative_width, self.relative_height = self.get_relative_width_and_height()
        self.average_stroke_width = self.get_average_stroke_width()

    def update_global_properties(self, graph):
        self.pixels_variance = self.number_of_pixels - graph.average_pixel_number
        self.width_variance = self.relative_width - graph.average_width
        self.height_variance = self.relative_height - graph.average_height
        self.stroke_width_variance = self.average_stroke_width - graph.average_stroke_width

    def create_tile(self):
        min_width, max_width, min_height, max_height = self.get_min_max_coordinates()
        width = max_width - min_width + 1
        height = max_height - min_height + 1
        print width, height
        im = Image.new("1", (width, height), 255)
        for i,j in self.pixels:
            new_i = i-min_width
            new_j = j-min_height
            im.putpixel((new_i, new_j), 0)
        return im

    def is_horizontal(self, node):
        return self.location[1] == node.location[1]

    def get_mu(self):
        value = 0.0
        #value += self.relative_height + self.relative_width + self.average_stroke_width
        value += self.width_variance#self.pixels_variance + \
                   #+ \
                  #20*self.height_variance + \
                  #5*self.stroke_width_variance
        return value/len(self.pixels)

class Graph():

    def __init__(self):
        self.nodes = []
        self.average_pixel_number = 0
        self.average_width = 0
        self.average_height = 0
        self.average_stroke_width = 0

    def append(self, node):
        self.nodes.append(node)

    def compute_properties(self, width, height):
        image = Image.new("RGB", (width, height), (255, 255, 255))
        for node in self.nodes:
            node.update_local_properties()
            # Global properties
            self.average_pixel_number += node.number_of_pixels
            self.average_width += node.relative_width
            self.average_height += node.relative_height
            self.average_stroke_width += node.average_stroke_width

        number_of_nodes = len(self.nodes)
        self.average_pixel_number /= number_of_nodes
        self.average_width /= number_of_nodes
        self.average_height /= number_of_nodes
        self.average_stroke_width /= number_of_nodes
        for node in self.nodes:
            node.update_global_properties(self)
        PIXEL_THRESHOLD = 5 * self.average_pixel_number
        for node in self.nodes:
            if node.pixels_variance > PIXEL_THRESHOLD:
                node.marked = True
            # Drawing test
            #if node.pixels_variance > THRESHOLD:
            #        print node.pixels_variance, node.width_variance, node.height_variance, node.stroke_width_variance
#            for pixel in node.pixels:
#                if node.pixels_variance > PIXEL_THRESHOLD:
##                    image.putpixel(pixel, (255,0,0))
#               else:
#                   try:
#                       image.putpixel(pixel, (0,0,0))
#                    except:
#                        print pixel
#                        import ipdb;ipdb.set_trace()
        #image.save('output.png', "PNG")

def get_conected_pixels(im,i,j,width,height):
    pixels = []
    pixels.append((i,j),)
    final_pixels = pixels[:]
    pixels_to_check = set(pixels)
    while True:
        for i,j in pixels:
            if i>0 and im.getpixel((i-1,j)) != BACKGROUND_COLOR:
                pixels_to_check.add((i-1,j))
            if i<width-1 and im.getpixel((i+1,j)) != BACKGROUND_COLOR:
                pixels_to_check.add((i+1,j))
            if j>0 and im.getpixel((i,j-1)) != BACKGROUND_COLOR:
                pixels_to_check.add((i,j-1))
            if j<height-1 and im.getpixel((i,j+1)) != BACKGROUND_COLOR:
                pixels_to_check.add((i,j+1))
            if i>0 and j>0 and im.getpixel((i-1,j-1)) != BACKGROUND_COLOR:
                pixels_to_check.add((i-1,j-1))
            if i<width-1 and j<height-1 and im.getpixel((i+1,j+1)) != BACKGROUND_COLOR:
                pixels_to_check.add((i+1,j+1))
            if i<width-1 and j>0 and im.getpixel((i+1,j-1)) != BACKGROUND_COLOR:
                pixels_to_check.add((i+1,j-1))
            if i>0 and j<height-1 and im.getpixel((i-1,j+1)) != BACKGROUND_COLOR:
                pixels_to_check.add((i-1,j+1))
        pixels_to_check_list = list(pixels_to_check)
        for new_pixel in pixels_to_check_list:
            if new_pixel not in final_pixels:
                final_pixels.append(new_pixel)
            else:
                pixels_to_check.remove(new_pixel)
        if pixels_to_check == set():
            break
        else:
            pixels.extend(list(pixels_to_check))
            pixels_to_check = set()
    return list(pixels)

def get_conected_pixels2(im, width, height):
    graph = nx.Graph()
    print 'Filtering foreground...',
    for i in range(width-1):
        for j in range(height-1):
            graph.add_edge((i,j),(i+1,j))
            graph.add_edge((i,j),(i,j+1))
    for i in range(width):
        for j in range(height):
            if im.getpixel((i,j)) != BACKGROUND_COLOR:
                graph.remove_node((i,j))
    print 'Done.'
    for pixel in graph.nodes():
        pass

def detect_elements(image):
    graph = Graph()
    width, height = im.size
    checked_pixels = []
    for i in range(width):
        for j in range(height):
            if (i,j) not in checked_pixels:
                color = im.getpixel((i,j))
                if color != BACKGROUND_COLOR:
                    node = Node()
                    pixels = get_conected_pixels(image,i,j,width,height)
                    checked_pixels.extend(pixels)
                    node.pixels = pixels
                    node.color = (randint(0,255), randint(0,255), randint(0,255))
                    graph.append(node)
    return graph


def get_conected_points_in_array(table,i,j):
    width, height = table.shape
    pixels = []
    pixels.append((i,j),)
    final_pixels = pixels[:]
    pixels_to_check = set(pixels)
    while True:
        for i,j in pixels:
            if i>0 and j<height-1 and table[i-1][j] != BACKGROUND_COLOR:
                pixels_to_check.add((i-1,j))
            if i<width-1  and j<height-1 and table[i+1][j] != BACKGROUND_COLOR:
                pixels_to_check.add((i+1,j))
            if j>0 and table[i][j-1] != BACKGROUND_COLOR:
                pixels_to_check.add((i,j-1))
            if j<height-1 and table[i][j+1] != BACKGROUND_COLOR:
                pixels_to_check.add((i,j+1))
            if i>0 and j>0 and table[i-1][j-1] != BACKGROUND_COLOR:
                pixels_to_check.add((i-1,j-1))
            if i<width-1 and j<height-1 and table[i+1][j+1] != BACKGROUND_COLOR:
                pixels_to_check.add((i+1,j+1))
            if i<width-1 and j>0 and table[i+1][j-1] != BACKGROUND_COLOR:
                pixels_to_check.add((i+1,j-1))
            if i>0 and j<height-1 and table[i-1][j+1] != BACKGROUND_COLOR:
                pixels_to_check.add((i-1,j+1))
        pixels_to_check_list = list(pixels_to_check)
        for new_pixel in pixels_to_check_list:
            if new_pixel not in final_pixels:
                final_pixels.append(new_pixel)
            else:
                pixels_to_check.remove(new_pixel)
        if pixels_to_check == set():
            break
        else:
            pixels.extend(list(pixels_to_check))
            pixels_to_check = set()
    return list(pixels)

def reversed_pixels(pixels):
    return [(j,i) for (i,j) in pixels]

def detect_elements_in_array(table):
    graph = Graph()
    height, width = table.shape
    checked_pixels = []
    for j in range(width):
        for i in range(height):
            if table[i][j] != BACKGROUND_COLOR and(i,j) not in checked_pixels:
                    node = Node()
                    pixels = get_conected_points_in_array(table,i,j)
                    checked_pixels.extend(pixels)
                    node.pixels = reversed_pixels(pixels)
                    node.color = (randint(0,255), randint(0,255), randint(0,255))
                    graph.append(node)
    return graph

def detect_elements_from_noisy_source(table, foreground_pixels):
    """
    Pixels contains a list of foregroung pixels and table contains the original
    binarized image as a numpy table
    """
    graph = Graph()
    height, width = table.shape
    checked_pixels = []
    print len(foreground_pixels)
    counter = 0
    for i,j in foreground_pixels:
        counter += 1
        if (i,j) not in checked_pixels:
            node = Node()
            pixels = get_conected_points_in_array(table,i,j)
            checked_pixels.extend(pixels)
            node.pixels = reversed_pixels(pixels)
            node.color = (randint(0,255), randint(0,255), randint(0,255))
            graph.append(node)
    return graph

