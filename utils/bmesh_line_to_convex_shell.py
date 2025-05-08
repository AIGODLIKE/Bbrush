# SPDX-FileCopyrightText: 2016-2022 Blender Foundation
#
# SPDX-License-Identifier: GPL-2.0-or-later


from mathutils import Vector
from mathutils.geometry import intersect_point_line as PtLineIntersect


class CAD_prefs:
    VTX_PRECISION = 1.0e-5
    VTX_DOUBLES_THRSHLD = 0.0001


def point_on_edge(p, edge):
    '''
    > p:        vector
    > edge:     tuple of 2 vectors
    < returns:  True / False if a point happens to lie on an edge
    '''
    pt, _percent = PtLineIntersect(p, *edge)
    on_line = (pt - p).length < CAD_prefs.VTX_PRECISION
    return on_line and (0.0 <= _percent <= 1.0)


def line_from_edge_intersect(edge1, edge2):
    '''
    > takes 2 tuples, each tuple contains 2 vectors
    - prepares input for sending to intersect_line_line
    < returns output of intersect_line_line
    '''
    [p1, p2], [p3, p4] = edge1, edge2
    return LineIntersect(p1, p2, p3, p4)


def get_intersection(edge1, edge2):
    '''
    > takes 2 tuples, each tuple contains 2 vectors
    < returns the point halfway on line. See intersect_line_line
    '''
    line = line_from_edge_intersect(edge1, edge2)
    if line:
        return (line[0] + line[1]) / 2


def test_coplanar(edge1, edge2):
    '''
    the line that describes the shortest line between the two edges
    would be short if the lines intersect mathematically. If this
    line is longer than the VTX_PRECISION then they are either
    coplanar or parallel.
    '''
    line = line_from_edge_intersect(edge1, edge2)
    if line:
        return (line[0] - line[1]).length < CAD_prefs.VTX_PRECISION


def closest_idx(pt, e):
    '''
    > pt:       vector
    > e:        bmesh edge
    < returns:  returns index of vertex closest to pt.

    if both points in e are equally far from pt, then v1 is returned.
    '''
    if isinstance(e, bmesh.types.BMEdge):
        ev = e.verts
        v1 = ev[0].co
        v2 = ev[1].co
        distance_test = (v1 - pt).length <= (v2 - pt).length
        return ev[0].index if distance_test else ev[1].index

    print("received {0}, check expected input in docstring ".format(e))


def closest_vector(pt, e):
    '''
    > pt:       vector
    > e:        2 vector tuple
    < returns:
    pt, 2 vector tuple: returns closest vector to pt

    if both points in e are equally far from pt, then v1 is returned.
    '''
    if isinstance(e, tuple) and all([isinstance(co, Vector) for co in e]):
        v1, v2 = e
        distance_test = (v1 - pt).length <= (v2 - pt).length
        return v1 if distance_test else v2

    print("received {0}, check expected input in docstring ".format(e))


def coords_tuple_from_edge_idx(bm, idx):
    ''' bm is a bmesh representation '''
    return tuple(v.co for v in bm.edges[idx].verts)


def vectors_from_indices(bm, raw_vert_indices):
    ''' bm is a bmesh representation '''
    return [bm.verts[i].co for i in raw_vert_indices]


def vertex_indices_from_edges_tuple(bm, edge_tuple):
    '''
    > bm:           is a bmesh representation
    > edge_tuple:   contains two edge indices.
    < returns the vertex indices of edge_tuple
    '''

    def k(v, w):
        return bm.edges[edge_tuple[v]].verts[w].index

    return [k(i >> 1, i % 2) for i in range(4)]


def get_vert_indices_from_bmedges(edges):
    '''
    > bmedges:      a list of two bm edges
    < returns the vertex indices of edge_tuple as a flat list.
    '''
    temp_edges = []
    print(edges)
    for e in edges:
        for v in e.verts:
            temp_edges.append(v.index)
    return temp_edges


def num_edges_point_lies_on(pt, edges):
    ''' returns the number of edges that a point lies on. '''
    res = [point_on_edge(pt, edge) for edge in [edges[:2], edges[2:]]]
    return len([i for i in res if i])


def find_intersecting_edges(bm, pt, idx1, idx2):
    '''
    > pt:           Vector
    > idx1, ix2:    edge indices
    < returns the list of edge indices where pt is on those edges
    '''
    if not pt:
        return []
    idxs = [idx1, idx2]
    edges = [coords_tuple_from_edge_idx(bm, idx) for idx in idxs]
    return [idx for edge, idx in zip(edges, idxs) if point_on_edge(pt, edge)]


def duplicates(indices):
    return len(set(indices)) < 4


def vert_idxs_from_edge_idx(bm, idx):
    edge = bm.edges[idx]
    return edge.verts[0].index, edge.verts[1].index


import bpy
import bmesh
from mathutils.geometry import intersect_line_line as LineIntersect

import itertools
from collections import defaultdict


def order_points(edge, point_list):
    ''' order these edges from distance to v1, then
    sandwich the sorted list with v1, v2 '''
    v1, v2 = edge

    def dist(co):
        return (v1 - co).length

    point_list = sorted(point_list, key=dist)
    return [v1] + point_list + [v2]


def remove_permutations_that_share_a_vertex(bm, permutations):
    ''' Get useful Permutations '''
    final_permutations = []
    for edges in permutations:
        raw_vert_indices = vertex_indices_from_edges_tuple(bm, edges)
        if duplicates(raw_vert_indices):
            continue

        # reaches this point if they do not share.
        final_permutations.append(edges)

    return final_permutations


def get_valid_permutations(bm, edge_indices):
    raw_permutations = itertools.permutations(edge_indices, 2)
    permutations = [r for r in raw_permutations if r[0] < r[1]]
    return remove_permutations_that_share_a_vertex(bm, permutations)


def can_skip(closest_points, vert_vectors):
    '''this checks if the intersection lies on both edges, returns True
    when criteria are not met, and thus this point can be skipped'''
    if not closest_points:
        return True
    if not isinstance(closest_points[0].x, float):
        return True
    if num_edges_point_lies_on(closest_points[0], vert_vectors) < 2:
        return True

    # if this distance is larger than than VTX_PRECISION, we can skip it.
    cpa, cpb = closest_points
    return (cpa - cpb).length > CAD_prefs.VTX_PRECISION


def get_intersection_dictionary(bm, edge_indices):
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    permutations = get_valid_permutations(bm, edge_indices)

    k = defaultdict(list)
    d = defaultdict(list)

    for edges in permutations:
        raw_vert_indices = vertex_indices_from_edges_tuple(bm, edges)
        vert_vectors = vectors_from_indices(bm, raw_vert_indices)

        points = LineIntersect(*vert_vectors)

        # some can be skipped.    (NaN, None, not on both edges)
        if can_skip(points, vert_vectors):
            continue

        # reaches this point only when an intersection happens on both edges.
        [k[edge].append(points[0]) for edge in edges]

    # k will contain a dict of edge indices and points found on those edges.
    for edge_idx, unordered_points in k.items():
        tv1, tv2 = bm.edges[edge_idx].verts
        v1 = bm.verts[tv1.index].co
        v2 = bm.verts[tv2.index].co
        ordered_points = order_points((v1, v2), unordered_points)
        d[edge_idx].extend(ordered_points)

    return d


def update_mesh(bm, d):
    ''' Make new geometry (delete old first) '''

    oe = bm.edges
    ov = bm.verts

    new_verts = []
    collect = new_verts.extend
    for old_edge, point_list in d.items():
        num_edges_to_add = len(point_list) - 1
        for i in range(num_edges_to_add):
            a = ov.new(point_list[i])
            b = ov.new(point_list[i + 1])
            oe.new((a, b))
            bm.normal_update()
            collect([a, b])

    bmesh.ops.delete(bm, geom=[edge for edge in bm.edges if edge.select], context='EDGES')

    # bpy.ops.mesh.remove_doubles(
    #    threshold=cm.CAD_prefs.VTX_DOUBLES_THRSHLD,
    #    use_unselected=False)

    bmesh.ops.remove_doubles(bm, verts=new_verts, dist=CAD_prefs.VTX_DOUBLES_THRSHLD)


def unselect_nonintersecting(bm, d_edges, edge_indices):
    if len(edge_indices) > len(d_edges):
        reserved_edges = set(edge_indices) - set(d_edges)
        for edge in reserved_edges:
            bm.edges[edge].select = False
        print("unselected {}, non intersecting edges".format(reserved_edges))


def find_boundary_edge(bm):
    for edge in bm.edges:
        if edge.is_boundary:
            return edge


def bmesh_line_to_convex_shell(lines):
    start_v = None
    last_v = None
    bm = bmesh.new()
    for index, co in enumerate(lines):
        co = [*co[:], 0]
        if last_v is not None:
            last_v = bm.verts.new(co, last_v)
        else:
            last_v = bm.verts.new(co)
        last_v.index = index
        if start_v is None:
            start_v = last_v
    bm.edges.new((last_v, start_v))
    bm_line_to_convex_shell(bm)

    boundary_edge = find_boundary_edge(bm)
    find_edges = [boundary_edge, ]
    a,b = boundary_edge.verts
    def find(v):
        for edge in a.link_edges:
            le = []
            if edge not in find_edges and edge.is_boundary:
                le.append(edge)


def bm_line_to_convex_shell(bm):
    selected_edges = [edge for edge in bm.edges if edge.select]
    edge_indices = [i.index for i in selected_edges]

    d = get_intersection_dictionary(bm, edge_indices)

    update_mesh(bm, d)
    bmesh.ops.contextual_create(bm, geom=bm.edges)
    bmesh.ops.triangulate(bm, faces=bm.faces)


if __name__ == "__main__":
    obj = bpy.context.object
    bm = bmesh.from_edit_mesh(obj.data)

    bm_line_to_convex_shell(bm)

    bmesh.update_edit_mesh(obj.data)
