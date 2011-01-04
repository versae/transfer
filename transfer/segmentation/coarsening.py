#!/usr/bin/env python
#-*- encoding:utf-8 -*-
#
#####################################################################
# Coarsening Algorithm
# 
# Source: Overlapped text segmentation using Markov Random Field and
# Aggregation (Peng, Setlur, Govindaraju, Sitaram )
#
# Shape context: http://en.wikipedia.org/wiki/Shape_context
#
#####################################################################

import Image
import networkx as nx
import numpy
import pickle
from random import randint
import sys

from node_extraction import *
from utils import binarize, thumbnail, pil2np

BACKGROUND_COLOR = 255


def coarse(im_color):
    # Create numpy array from image
    width, height = im_color.size
    if height > 1000:
        im_color = thumbnail(im_color, 1000)
    # Binarization
    im = binarize(im_color)
    I = pil2np(im)
    width, height = I.shape
    width, height = im.size
    table_width, table_height = I.shape
    if table_width != width:
        I = numpy.transpose(I)
    graph = detect_elements_in_array(I)
    graph.compute_properties(width, height)
    image = Image.new("RGB", (width, height), (255, 255, 255))
    for node in graph.nodes:
        if node.marked:
            coarsed_graph = coarsening(node.create_tile(), 100)
            for node_id in coarsed_graph.nodes():
                color = coarsed_graph.node[node_id]['node'].color
                for i,j in coarsed_graph.node[node_id]['node'].pixels:
                    ominw, omaxw, ominh, omaxh = node.get_min_max_coordinates()
                    image.putpixel((i+ominw, j+ominh), color)
    return image

def coarsening(im, tau):
    """
    Input: Text image im and a predefined threshold T
    Initialization: Create a graph G, where initially 
    each foreground pixel p is a node and store all
    nodes in a queue Q
    """

    def coarsened(graph, tau):
        for node_id in graph.nodes():
            node = graph.node[node_id]['node']
            if len(node.pixels) < tau:
                return False
        return True

    def merge_initial_nodes(graph):
        for node_id in graph.nodes():
            for neighbor_id in graph.edge[node_id]:
                merge_nodes(graph_copy, node_id, neighbor_id)

    def merge_candidate_nodes(graph, a, b):
        node_a = graph.node[a]
        node_b = graph.node[b]
        pixels = node_a['pixels'] + node_b['pixels']
        color = (randint(0,255), randint(0,255), randint(0,255))
        return {'pixels':pixels, 'color':color, 'mu':1, 'j_index':1}

    def merge_nodes(graph, a, b):
        node_a = graph.node[a]['node']
        node_b = graph.node[b]['node']
        node_id = a+b
        node = Node()
        node.pixels = node_a.pixels + node_b.pixels
        node.color = (randint(0,255), randint(0,255), randint(0,255))
        node.mui=1
        node.j_index=1
        node.update_local_properties()
        graph.add_node(node_id, node=node)
        a_edges_copy = graph.edge[a].copy()
        for edge in a_edges_copy:
            graph.add_edge(node_id, edge)
        b_edges_copy = graph.edge[b].copy()
        for edge in b_edges_copy:
            graph.add_edge(node_id, edge)
        
        graph.remove_node(a)
        try:
            graph.remove_node(b)
        except:
            pass
        return node_id

    def common_nodes(graph, a, b):
        counter = 0
        for node in graph.edge[a]:
            if node in graph.edge[b]:
                counter += 1
        return counter
    graph = nx.Graph()
    width, height = im.size
    queue = []
    for i in range(width):
        for j in range(height):
            color = im.getpixel((i,j))
            if color != BACKGROUND_COLOR:
                node_id = '%d-%d' % (i,j)
                node = Node()
                node.pixels = ((i,j),)
                node.color = (randint(0,255), randint(0,255), randint(0,255))
                node.mu = 1
                node.j_index = 1
                graph.add_node(node_id, node=node)
                # Node is linked with his 4-window neighbors
                if i>0 and im.getpixel((i-1,j)) != BACKGROUND_COLOR:
                    graph.add_edge(node_id, '%d-%d' % (i-1,j))
                if i<width-1 and im.getpixel((i+1,j)) != BACKGROUND_COLOR:
                    graph.add_edge(node_id, '%d-%d' % (i+1,j))
                if j>0 and im.getpixel((i,j-1)) != BACKGROUND_COLOR:
                    graph.add_edge(node_id, '%d-%d' % (i,j-1))
                if j<height-1 and im.getpixel((i,j+1)) != BACKGROUND_COLOR:
                    graph.add_edge(node_id, '%d-%d' % (i,j+1))
                if i>0 and j>0 and im.getpixel((i-1,j-1)) != BACKGROUND_COLOR:
                    graph.add_edge(node_id, '%d-%d' % (i-1,j-1))
                if i<width-1 and j<height-1 and im.getpixel((i+1,j+1)) != BACKGROUND_COLOR:
                    graph.add_edge(node_id, '%d-%d' % (i+1,j+1))
                if i<width-1 and j>0 and im.getpixel((i+1,j-1)) != BACKGROUND_COLOR:
                    graph.add_edge(node_id, '%d-%d' % (i+1,j-1))
                if i>0 and j<height-1 and im.getpixel((i-1,j+1)) != BACKGROUND_COLOR:
                    graph.add_edge(node_id, '%d-%d' % (i-1,j+1))
                # Append node to the processing queue
                queue.append(node_id)
    
    graph.node[node_id]
    image = Image.new("RGB", (width, height), (255, 255, 255))
    for node_id in graph.nodes():
        node = graph.node[node_id]['node']
        node.update_local_properties()
        pixel = node.pixels[0]
        color = node.color
        image.putpixel(pixel, color)
    # image.save('output1.png', "PNG")
    # Iteration loop
    iters = 0
    while not coarsened(graph, tau) and iters<50:
        iters += 1
        # 1: Check the size (the number of pixels) m of every node in the
        # queue Q, if m > T is satisfied for all nodes, then stop, otherwise
        # continue
        structural_graph = Graph()
        for node_id in graph.nodes():
            structural_graph.nodes.append(graph.node[node_id]['node'])
        structural_graph.compute_properties(width, height)
        for node in structural_graph.nodes:
            node.update_global_properties(structural_graph)
        for node_id in queue:
            if node_id not in graph.nodes():
                continue
            elif len(graph.node[node_id]['node'].pixels) > tau:
                queue.append(node_id)
                queue.remove(node_id)
                continue
        # 2: Select the first node Ni from the Q, if its size m > T move 
        # this node to the end of the queue and go back to step 1, otherwise
        # continue
            else:
                node_i = graph.node[node_id]['node']
        # 3: Calculate mui of the first node N
                mui = 1
        # 4: Traverse all neighbors of Ni, temporarily merging Ni and each
        # of its neighbors N, individually to create a candidate node Ni+j,
        # where j belongs to N(i) is consistent with equation 4
                neighbors = []
                #candidates = []
                for neighbor in graph.edge[node_id]:
                    if neighbor != node_id:
                        node = graph.node[neighbor]['node']
                        neighbors.append((neighbor,
                                        node.get_mu(),
                                        common_nodes(graph, node_id, neighbor)+1))
                #    candidates.append(merge_candidate_nodes(graph, node_id, neighbor))
        # 5: User Equation 4 to identify optimal neighbor Ni, and store merged
        # node Ni+j, at the end of Q
                degree = len(neighbors)
                if degree == 0:
                    continue
                mu = node_i.get_mu()
                index = 0
                min_value = 99999
                for i in range(degree):
                    proximity = abs(mu - neighbors[i][1])/(4*neighbors[i][2])
                    # More weight to horizontal nodes
                    if node_i.is_horizontal(graph.node[neighbor]['node']):
                        proximity /= 50
                    if  proximity < min_value:
                        min_value = proximity
                        index = i
                if min_value > 0.25:
                    continue
                try:
                    new_node = neighbors[index][0]
                except:
                    pass
                new_id = merge_nodes(graph, node_id, new_node)
                queue.append(new_id)
        # 6: Remove Ni and Nj from the queue Q, and update neighbors relations
        # for graph G
                queue.remove(new_node)
                if node_id != new_node: #FIXME
                    queue.remove(node_id)
        # 7: Go to step 1
    return graph

