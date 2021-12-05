from typing import Hashable, Optional, Iterable, Dict, Any, Union, cast, Iterator, Tuple
from uuid import uuid4

class DuplicateIdentiferError(Exception):
    pass

class NodeNotInGraphError(Exception):
    pass

class NodesNotConnectedError(Exception):
    pass

class EdgeAlreadyExistsError(Exception):
    pass

class Node:
    def __init__(self, tag: Optional[Any] = None, identifier: Optional[Hashable] = None, data=None):
        self.identifier = identifier if identifier else uuid4()
        self.tag = tag if tag else self.identifier 
        self.data = data

        # What I connect to
        self._forward_edges: Dict[Hashable, 'Edge'] = {}
        # What connects to me
        self._backward_edges: Dict[Hashable, 'Edge'] = {}

    def add_connection(self, other: 'Node', data: Optional[Any] = None) -> 'Edge':
        if other.identifier in self._forward_edges:
            raise EdgeAlreadyExistsError(other.identifier)

        edge = Edge(self, other, data)
        self._forward_edges[other.identifier] = edge
        other._backward_edges[self.identifier] = edge
        return edge

    def remove_connection(self, other: 'Node'):
        if other.identifier not in self._forward_edges:
            raise NodesNotConnectedError(other.identifier)
        del self._forward_edges[other.identifier]
        del other._backward_edges[self.identifier]

    # To copy or not to copy...
    # One the one hand, exposing internal data like this means users may inadventenly ruin everything by mutating it incorrectly
    # on the other hand "we're all consenting adults here."
    def forward_edges(self):
        return self._forward_edges

    def backward_edges(self):
        return self._backward_edges

    # WARNING: No loop detection
    def traverse_forward_edges(self) -> Iterator['Edge']:
        for edge in self._forward_edges.values():
            yield edge
            yield from edge.to.traverse_forward_edges()

    # WARNING: No loop detection
    def traverse_backward_edges(self) -> Iterator['Edge']:
        for edge in self._backward_edges.values():
            yield edge
            yield from edge.from_.traverse_backward_edges()

    def __repr__(self):
        return f"Node({self.tag}, {self.identifier}, {self.data})"

class Edge:
    def __init__(self, from_: Node, to: Node, data: Optional[Any] = None):
        self.from_ = from_
        self.to = to
        self.data = data

    def __repr__(self):
        return f"Edge({self.from_}, {self.to}, {self.data})"

NodeReference = Union[Node, Hashable]
class Graph:
    """
    A generic Graph data structure

    Mostly just concered with bookkeeping around node addition/removal
    """

    def __init__(self):
        self._nodes = dict()

    def create_node(
        self,
        tag: Optional[Any] = None,
        identifier: Optional[Hashable] = None,
        #                          List of (node, data) or node
        connections: Optional[Iterable[Union[Tuple[NodeReference, Any], NodeReference]]] = None,
        data=None,
    ) -> Node:
        node = Node(tag, identifier, data)
        if node.identifier in self._nodes:
            raise DuplicateIdentiferError(node.identifier)

        self._nodes[node.identifier] = node
        if connections is not None:
            for conn in connections:
                reference, data = None,  None
                if isinstance(conn, tuple):
                    reference, data = conn
                else:
                    reference, data = conn, None

                if not isinstance(reference, Node):
                    if reference not in self._nodes:
                        raise NodeNotInGraphError(reference)
                    reference = self._nodes[reference]
                reference = cast(Node, reference)
                node.add_connection(reference, data=data)
        return node

    def remove_node(self, node: NodeReference):
        if not isinstance(node, Node):
            if node not in self._nodes:
                raise NodeNotInGraphError(node)
            node = self._nodes[node]
        elif node.identifier not in self._nodes:
            raise NodeNotInGraphError(node.identifier)
        node = cast(Node, node)
        for connection in list(node._forward_edges.values()):
            node.remove_connection(connection.to)
        for connection in list(node._backward_edges.values()):
            connection.from_.remove_connection(node)
        del self._nodes[node.identifier]

    def __contains__(self, identifier: Hashable) -> bool:
        return identifier in self._nodes

    def __getitem__(self, identifier: Hashable) -> Node:
        if identifier not in self._nodes:
            raise NodeNotInGraphError(identifier)
        return self._nodes[identifier]

    def __delitem__(self, identifier: NodeReference):
        self.remove_node(identifier)

    def __len__(self) -> int:
        return len(self._nodes)
