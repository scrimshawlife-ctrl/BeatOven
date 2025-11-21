"""
BeatOven PatchBay System

Node-graph routing abstraction with JSON/YAML patch descriptors,
hot-reload routing, and signal flow inspection.
Guarantees deterministic routing order.
"""

import hashlib
import json
import yaml
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Set, Tuple
from enum import Enum
from collections import defaultdict
import numpy as np


class NodeType(Enum):
    """Types of patch nodes."""
    INPUT = "input"
    OUTPUT = "output"
    PROCESSOR = "processor"
    MIXER = "mixer"
    SPLITTER = "splitter"
    MODIFIER = "modifier"


class SignalType(Enum):
    """Types of signals in the patch."""
    AUDIO = "audio"
    CONTROL = "control"
    TRIGGER = "trigger"
    SYMBOLIC = "symbolic"


@dataclass
class Port:
    """A connection port on a node."""
    name: str
    signal_type: SignalType
    is_input: bool
    node_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "signal_type": self.signal_type.value,
            "is_input": self.is_input,
            "node_id": self.node_id
        }


@dataclass
class Connection:
    """A connection between two ports."""
    source_node: str
    source_port: str
    dest_node: str
    dest_port: str
    gain: float = 1.0
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_node": self.source_node,
            "source_port": self.source_port,
            "dest_node": self.dest_node,
            "dest_port": self.dest_port,
            "gain": self.gain,
            "enabled": self.enabled
        }


@dataclass
class PatchNode:
    """A node in the patch graph."""
    id: str
    name: str
    node_type: NodeType
    inputs: List[Port] = field(default_factory=list)
    outputs: List[Port] = field(default_factory=list)
    params: Dict[str, Any] = field(default_factory=dict)
    processor: Optional[Callable] = None

    def __post_init__(self):
        for port in self.inputs:
            port.node_id = self.id
            port.is_input = True
        for port in self.outputs:
            port.node_id = self.id
            port.is_input = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type.value,
            "inputs": [p.to_dict() for p in self.inputs],
            "outputs": [p.to_dict() for p in self.outputs],
            "params": self.params
        }


@dataclass
class PatchDescriptor:
    """Complete patch configuration."""
    name: str
    version: str = "1.0"
    nodes: List[PatchNode] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "nodes": [n.to_dict() for n in self.nodes],
            "connections": [c.to_dict() for c in self.connections],
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), default_flow_style=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatchDescriptor":
        nodes = []
        for node_data in data.get("nodes", []):
            inputs = [Port(
                name=p["name"],
                signal_type=SignalType(p["signal_type"]),
                is_input=True
            ) for p in node_data.get("inputs", [])]
            outputs = [Port(
                name=p["name"],
                signal_type=SignalType(p["signal_type"]),
                is_input=False
            ) for p in node_data.get("outputs", [])]
            nodes.append(PatchNode(
                id=node_data["id"],
                name=node_data["name"],
                node_type=NodeType(node_data["node_type"]),
                inputs=inputs,
                outputs=outputs,
                params=node_data.get("params", {})
            ))

        connections = [Connection(**c) for c in data.get("connections", [])]

        return cls(
            name=data["name"],
            version=data.get("version", "1.0"),
            nodes=nodes,
            connections=connections,
            metadata=data.get("metadata", {})
        )


class SignalBuffer:
    """Buffer for passing signals between nodes."""

    def __init__(self, signal_type: SignalType, size: int = 1024):
        self.signal_type = signal_type
        self.size = size
        if signal_type == SignalType.AUDIO:
            self.data = np.zeros(size, dtype=np.float32)
        elif signal_type == SignalType.CONTROL:
            self.data = np.zeros(size, dtype=np.float32)
        elif signal_type == SignalType.TRIGGER:
            self.data = np.zeros(size, dtype=np.bool_)
        else:
            self.data = {}

    def clear(self):
        if isinstance(self.data, np.ndarray):
            self.data.fill(0)
        else:
            self.data = {}


class PatchBay:
    """
    Central patch routing system.

    Manages node-graph signal routing with deterministic ordering,
    hot-reload support, and signal flow inspection.
    """

    def __init__(self):
        self._nodes: Dict[str, PatchNode] = {}
        self._connections: List[Connection] = []
        self._execution_order: List[str] = []
        self._buffers: Dict[Tuple[str, str], SignalBuffer] = {}
        self._current_patch: Optional[PatchDescriptor] = None

    def load_patch(self, descriptor: PatchDescriptor) -> bool:
        """
        Load a patch descriptor.

        Args:
            descriptor: Patch configuration

        Returns:
            True if loaded successfully
        """
        # Clear existing
        self._nodes.clear()
        self._connections.clear()
        self._buffers.clear()

        # Add nodes
        for node in descriptor.nodes:
            self._nodes[node.id] = node

        # Add connections
        for conn in descriptor.connections:
            if self._validate_connection(conn):
                self._connections.append(conn)

        # Compute execution order
        self._execution_order = self._topological_sort()

        # Initialize buffers
        self._init_buffers()

        self._current_patch = descriptor
        return True

    def load_from_json(self, json_str: str) -> bool:
        """Load patch from JSON string."""
        data = json.loads(json_str)
        descriptor = PatchDescriptor.from_dict(data)
        return self.load_patch(descriptor)

    def load_from_yaml(self, yaml_str: str) -> bool:
        """Load patch from YAML string."""
        data = yaml.safe_load(yaml_str)
        descriptor = PatchDescriptor.from_dict(data)
        return self.load_patch(descriptor)

    def load_from_file(self, path: str) -> bool:
        """Load patch from file."""
        with open(path, 'r') as f:
            content = f.read()

        if path.endswith('.json'):
            return self.load_from_json(content)
        elif path.endswith('.yaml') or path.endswith('.yml'):
            return self.load_from_yaml(content)
        else:
            raise ValueError(f"Unsupported file format: {path}")

    def hot_reload(self, descriptor: PatchDescriptor) -> bool:
        """
        Hot-reload patch while preserving state where possible.

        Args:
            descriptor: New patch configuration

        Returns:
            True if reloaded successfully
        """
        # Save current buffer states for nodes that exist in both
        saved_buffers = {}
        for key, buffer in self._buffers.items():
            saved_buffers[key] = buffer.data.copy() if isinstance(buffer.data, np.ndarray) else dict(buffer.data)

        # Load new patch
        success = self.load_patch(descriptor)

        # Restore buffers where possible
        if success:
            for key, data in saved_buffers.items():
                if key in self._buffers:
                    if isinstance(data, np.ndarray):
                        min_len = min(len(data), len(self._buffers[key].data))
                        self._buffers[key].data[:min_len] = data[:min_len]

        return success

    def add_node(self, node: PatchNode) -> bool:
        """Add a node to the patch."""
        if node.id in self._nodes:
            return False
        self._nodes[node.id] = node
        self._execution_order = self._topological_sort()
        return True

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and its connections."""
        if node_id not in self._nodes:
            return False

        # Remove connections
        self._connections = [
            c for c in self._connections
            if c.source_node != node_id and c.dest_node != node_id
        ]

        del self._nodes[node_id]
        self._execution_order = self._topological_sort()
        return True

    def connect(
        self,
        source_node: str,
        source_port: str,
        dest_node: str,
        dest_port: str,
        gain: float = 1.0
    ) -> bool:
        """Create a connection between nodes."""
        conn = Connection(
            source_node=source_node,
            source_port=source_port,
            dest_node=dest_node,
            dest_port=dest_port,
            gain=gain
        )

        if not self._validate_connection(conn):
            return False

        self._connections.append(conn)
        self._execution_order = self._topological_sort()
        self._init_buffers()
        return True

    def disconnect(
        self,
        source_node: str,
        source_port: str,
        dest_node: str,
        dest_port: str
    ) -> bool:
        """Remove a connection."""
        for i, conn in enumerate(self._connections):
            if (conn.source_node == source_node and
                conn.source_port == source_port and
                conn.dest_node == dest_node and
                conn.dest_port == dest_port):
                del self._connections[i]
                return True
        return False

    def process(self, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process signal through the patch.

        Args:
            input_data: Input signals keyed by node_id:port_name

        Returns:
            Output signals keyed by node_id:port_name
        """
        if input_data is None:
            input_data = {}

        # Clear buffers
        for buffer in self._buffers.values():
            buffer.clear()

        # Set input data
        for key, data in input_data.items():
            if key in self._buffers:
                if isinstance(data, np.ndarray):
                    self._buffers[key].data[:len(data)] = data
                else:
                    self._buffers[key].data = data

        # Process in topological order
        for node_id in self._execution_order:
            node = self._nodes.get(node_id)
            if node and node.processor:
                # Gather inputs
                node_inputs = {}
                for port in node.inputs:
                    key = (node_id, port.name)
                    if key in self._buffers:
                        node_inputs[port.name] = self._buffers[key].data

                # Process
                outputs = node.processor(node_inputs, node.params)

                # Distribute outputs
                if outputs:
                    for port_name, data in outputs.items():
                        # Send to connected inputs
                        for conn in self._connections:
                            if conn.source_node == node_id and conn.source_port == port_name and conn.enabled:
                                dest_key = (conn.dest_node, conn.dest_port)
                                if dest_key in self._buffers:
                                    if isinstance(data, np.ndarray):
                                        self._buffers[dest_key].data += data * conn.gain
                                    else:
                                        self._buffers[dest_key].data = data

        # Collect outputs
        outputs = {}
        for node_id, node in self._nodes.items():
            if node.node_type == NodeType.OUTPUT:
                for port in node.inputs:
                    key = (node_id, port.name)
                    if key in self._buffers:
                        outputs[f"{node_id}:{port.name}"] = self._buffers[key].data

        return outputs

    def inspect_flow(self) -> Dict[str, Any]:
        """
        Inspect current signal flow.

        Returns:
            Signal flow information
        """
        return {
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "connections": [c.to_dict() for c in self._connections],
            "execution_order": self._execution_order,
            "buffer_count": len(self._buffers)
        }

    def get_execution_order(self) -> List[str]:
        """Get deterministic execution order."""
        return list(self._execution_order)

    def export_patch(self) -> PatchDescriptor:
        """Export current patch as descriptor."""
        return PatchDescriptor(
            name=self._current_patch.name if self._current_patch else "exported_patch",
            nodes=list(self._nodes.values()),
            connections=list(self._connections)
        )

    def _validate_connection(self, conn: Connection) -> bool:
        """Validate a connection."""
        # Check nodes exist
        if conn.source_node not in self._nodes:
            return False
        if conn.dest_node not in self._nodes:
            return False

        source_node = self._nodes[conn.source_node]
        dest_node = self._nodes[conn.dest_node]

        # Check ports exist
        source_port = next((p for p in source_node.outputs if p.name == conn.source_port), None)
        dest_port = next((p for p in dest_node.inputs if p.name == conn.dest_port), None)

        if source_port is None or dest_port is None:
            return False

        # Check signal type compatibility
        if source_port.signal_type != dest_port.signal_type:
            return False

        return True

    def _topological_sort(self) -> List[str]:
        """
        Compute deterministic topological sort of nodes.

        Returns nodes in processing order based on connections.
        """
        # Build adjacency list
        graph = defaultdict(list)
        in_degree = {node_id: 0 for node_id in self._nodes}

        for conn in self._connections:
            if conn.enabled:
                graph[conn.source_node].append(conn.dest_node)
                in_degree[conn.dest_node] += 1

        # Kahn's algorithm with deterministic ordering
        queue = sorted([n for n, d in in_degree.items() if d == 0])
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for neighbor in sorted(graph[node]):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    queue.sort()  # Maintain deterministic order

        # Add any remaining nodes (disconnected)
        remaining = sorted(set(self._nodes.keys()) - set(result))
        result.extend(remaining)

        return result

    def _init_buffers(self):
        """Initialize signal buffers for all ports."""
        self._buffers.clear()

        for node_id, node in self._nodes.items():
            for port in node.inputs + node.outputs:
                key = (node_id, port.name)
                self._buffers[key] = SignalBuffer(port.signal_type)


def create_default_patch() -> PatchDescriptor:
    """Create a default BeatOven patch."""
    nodes = [
        PatchNode(
            id="input",
            name="Input",
            node_type=NodeType.INPUT,
            outputs=[Port("symbolic", SignalType.SYMBOLIC, False)]
        ),
        PatchNode(
            id="rhythm",
            name="Rhythm Engine",
            node_type=NodeType.PROCESSOR,
            inputs=[Port("symbolic", SignalType.SYMBOLIC, True)],
            outputs=[
                Port("events", SignalType.CONTROL, False),
                Port("audio", SignalType.AUDIO, False)
            ]
        ),
        PatchNode(
            id="harmony",
            name="Harmonic Engine",
            node_type=NodeType.PROCESSOR,
            inputs=[Port("symbolic", SignalType.SYMBOLIC, True)],
            outputs=[
                Port("chords", SignalType.CONTROL, False),
                Port("audio", SignalType.AUDIO, False)
            ]
        ),
        PatchNode(
            id="timbre",
            name="Timbre Engine",
            node_type=NodeType.PROCESSOR,
            inputs=[
                Port("control", SignalType.CONTROL, True),
                Port("audio_in", SignalType.AUDIO, True)
            ],
            outputs=[Port("audio", SignalType.AUDIO, False)]
        ),
        PatchNode(
            id="mixer",
            name="Mixer",
            node_type=NodeType.MIXER,
            inputs=[
                Port("drums", SignalType.AUDIO, True),
                Port("harmony", SignalType.AUDIO, True),
                Port("timbre", SignalType.AUDIO, True)
            ],
            outputs=[Port("master", SignalType.AUDIO, False)]
        ),
        PatchNode(
            id="output",
            name="Output",
            node_type=NodeType.OUTPUT,
            inputs=[Port("audio", SignalType.AUDIO, True)]
        )
    ]

    connections = [
        Connection("input", "symbolic", "rhythm", "symbolic"),
        Connection("input", "symbolic", "harmony", "symbolic"),
        Connection("rhythm", "audio", "mixer", "drums"),
        Connection("harmony", "audio", "mixer", "harmony"),
        Connection("harmony", "chords", "timbre", "control"),
        Connection("timbre", "audio", "mixer", "timbre"),
        Connection("mixer", "master", "output", "audio")
    ]

    return PatchDescriptor(
        name="default_beatoven",
        version="1.0",
        nodes=nodes,
        connections=connections,
        metadata={"author": "BeatOven", "description": "Default patch"}
    )


__all__ = [
    "PatchBay", "PatchNode", "PatchDescriptor", "Connection", "Port",
    "NodeType", "SignalType", "SignalBuffer", "create_default_patch"
]
