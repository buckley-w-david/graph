# Day 7 challange of Advent of Code 2020

from graph import Graph

import re

with open("input", "r") as f:
    rules = f.readlines()

subject_pattern = re.compile(r"^((?:[a-zA-Z] ?)+) bags contain")
target_pattern = re.compile(r"(\d+) ([a-zA-Z]+ [a-zA-Z]+) bags?")

graph = Graph()

for rule in rules:
    subject = subject_pattern.match(rule).group(1)
    if subject in graph:
        node = graph[subject]
    else:
        node = graph.create_node(identifier=subject)

    for target in target_pattern.findall(rule):
        c, target_name = target
        if target_name in graph:
            target_node = graph[target_name]
        else:
            target_node = graph.create_node(identifier=target_name)

        node.add_connection(target_node, int(c))


def count_bags(graph, target):
    node = graph[target]
    count = 0
    for edge in node.forward_edges().values():
        count += edge.data + edge.data*count_bags(graph, edge.to.identifier)
    return count

print(f"Part 1: {len(set([edge.from_.identifier for edge in graph['shiny gold'].traverse_backward_edges()]))}")
print(f"Part 2: {count_bags(graph, 'shiny gold')}")
