# This file is part of PyOP2
#
# PyOP2 is Copyright (c) 2012, Imperial College London and
# others. Please see the AUTHORS file in the main source directory for
# a full list of copyright holders.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * The name of Imperial College London or that of other
#       contributors may not be used to endorse or promote products
#       derived from this software without specific prior written
#       permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTERS
# ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

"""Provides functions for reading triangle files into OP2 data structures."""

from pyop2 import op2
import numpy as np


def read_triangle(f, layers=None):
    """Read the triangle file with prefix f into OP2 data strctures. Presently
    only .node and .ele files are read, attributes are ignored, and there may
    be bugs. The dat structures are returned as:

        (nodes, coords, elements, elem_node)

    These items have type:

        (Set, Dat, Set, Map)

    The Layers argument allows the reading of data for extruded meshes.
    It is to be used when dealing with extruded meshes.
    """
    # Read nodes
    with open(f + '.node') as h:
        num_nodes = int(h.readline().split(' ')[0])
        node_values = [0] * num_nodes
        for line in h:
            if line[0] == '#':
                continue
            if layers is None:
                vals = line.split()
                node = int(vals[0]) - 1
                x, y = [float(x) for x in vals[1:3]]
                node_values[node] = (x, y)
            else:
                vals = line.strip(" \n").split()
                node = int(vals[0]) - 1
                x, y = [float(x) for x in [vals[1], vals[2]]]
                node_values[node] = (x, y)

    nodes = op2.Set(num_nodes, 1, "nodes")
    vnodes = op2.Set(num_nodes, 2, "vnodes")
    coords = op2.Dat(vnodes, np.asarray(node_values, dtype=np.float64),
                     np.float64, "coords")

    # Read elements
    with open(f + '.ele') as h:
        if layers is None:
            num_tri, nodes_per_tri, num_attrs = \
                map(lambda x: int(x), h.readline().split())
            map_values = [0] * num_tri
            for line in h:
                if line[0] == '#':
                    continue
                vals = line.split()
                tri = int(vals[0])
                ele_nodes = [int(x) - 1 for x in vals[1:nodes_per_tri + 1]]
                map_values[tri - 1] = ele_nodes
        else:
            lline = h.readline().strip('\n').split(' ')
            final_line = [x for x in lline if x != '']

            num_tri, nodes_per_tri, num_attrs = \
                map(lambda x: int(x), final_line)
            map_values = [0] * num_tri
            for line in h:
                if line[0] == '#':
                    continue
                vals = [x for x in line.strip('\n').split(' ') if x != '']
                tri = int(vals[0])
                ele_nodes = [int(x) - 1 for x in vals[1:nodes_per_tri + 1]]
                map_values[tri - 1] = ele_nodes

    # Ref: http://stackoverflow.com/a/952952/396967
    flat_map = [item for sublist in map_values for item in sublist]

    if layers is None:
        elements = op2.Set(num_tri, 1, "elements")
    else:
        elements = op2.Set(num_tri, 1, "elements", layers=layers)
    elem_node = op2.Map(elements, nodes, 3, flat_map, "elem_node")
    elem_vnode = op2.Map(elements, vnodes, 3, flat_map, "elem_vnode")

    return nodes, vnodes, coords, elements, elem_node, elem_vnode
