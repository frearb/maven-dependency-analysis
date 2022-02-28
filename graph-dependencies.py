#!/usr/bin/env python
import os.path
import sys

import maven

def pom_visitor(poms, dirname, names):
    if 'pom.xml' in names:
        pom = '%s/pom.xml' % dirname
        poms.append(maven.parse(pom))

def dependency_edges(pom, group = None):
    if group is None:
        group_filter = lambda d: True
    else:
        group_filter = lambda d: d.groupId.startswith(group)
    edges = set()
    for dependency in filter(group_filter, pom['dependencies']):
        edges.add((pom['artifact'].artifactId, dependency.artifactId, dependency.scope))
    return edges

def print_graph(edges):
    print('digraph dependencies {')
    for edge in edges:
        a, b, _ = edge
        print('  "%s" -> "%s";' % (a, b))
    print('}')

def export_graph(edges):
    out = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
<key for="node" id="d5" yfiles.type="nodegraphics"/>
<key for="edge" id="d9" yfiles.type="edgegraphics"/>
<graph edgedefault="directed" id="G">'''
    nodeStrs = set()
    edgeStrs = set()
    for edge in edges:
        a, b, s = edge
        astr = '\n<node id="%s"><data key="d5"> <y:ShapeNode><y:Geometry width="%s"/> <y:NodeLabel>%s</y:NodeLabel></y:ShapeNode></data></node>' % (a,len(a)*8,a)
        bstr = '\n<node id="%s"><data key="d5"> <y:ShapeNode><y:Geometry width="%s"/> <y:NodeLabel>%s</y:NodeLabel></y:ShapeNode></data></node>' % (b,len(b)*8,b)
        nodeStrs.add(astr)
        nodeStrs.add(bstr)
        edgeStrs.add('\n<edge source="%s" target="%s"> <data key="d9"><y:PolyLineEdge><y:Arrows source="none" target="%s"/><y:BendStyle smoothed="true"/></y:PolyLineEdge></data></edge>' % (a, b, 'white_delta' if s == 'test' else 'standard'))
    for node in nodeStrs:
        out += node
    for edge in edgeStrs:
        out += edge
    out += '\n</graph>\n</graphml>'
    with open("./pom.graphml", "w") as output_file:
        output_file.write(out)

if __name__ == '__main__':
    directory = sys.argv[1]
    group = sys.argv[2]
    poms = []
    #os.path.walk(directory, pom_visitor, poms)
    for path, _, files in os.walk(directory):
        pom_visitor(poms, path, files)
    edges = set()
    for pom in poms:
        edges = edges | dependency_edges(pom, group)
    print_graph(edges)
    export_graph(edges)
