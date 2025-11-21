#!/usr/bin/env python3
"""
BeatOven Patch Inspector

Utility script to inspect, validate, and visualize PatchBay configurations.
"""

import argparse
import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from beatoven.core.patchbay import PatchBay, PatchDescriptor, create_default_patch


def load_patch(path: str) -> PatchDescriptor:
    """Load patch from file."""
    with open(path, 'r') as f:
        content = f.read()

    if path.endswith('.json'):
        data = json.loads(content)
    elif path.endswith('.yaml') or path.endswith('.yml'):
        import yaml
        data = yaml.safe_load(content)
    else:
        raise ValueError(f"Unsupported format: {path}")

    return PatchDescriptor.from_dict(data)


def print_patch_info(patch: PatchDescriptor):
    """Print patch information."""
    print(f"\nPatch: {patch.name}")
    print(f"Version: {patch.version}")
    print(f"Nodes: {len(patch.nodes)}")
    print(f"Connections: {len(patch.connections)}")

    print("\n--- Nodes ---")
    for node in patch.nodes:
        inputs = ", ".join(p.name for p in node.inputs)
        outputs = ", ".join(p.name for p in node.outputs)
        print(f"  [{node.node_type.value}] {node.id}: {node.name}")
        if inputs:
            print(f"    Inputs: {inputs}")
        if outputs:
            print(f"    Outputs: {outputs}")

    print("\n--- Connections ---")
    for conn in patch.connections:
        status = "✓" if conn.enabled else "✗"
        gain = f" (gain: {conn.gain})" if conn.gain != 1.0 else ""
        print(f"  {status} {conn.source_node}:{conn.source_port} → {conn.dest_node}:{conn.dest_port}{gain}")


def print_execution_order(patchbay: PatchBay):
    """Print execution order."""
    order = patchbay.get_execution_order()
    print("\n--- Execution Order ---")
    for i, node_id in enumerate(order):
        print(f"  {i+1}. {node_id}")


def visualize_ascii(patch: PatchDescriptor):
    """Create ASCII visualization of patch."""
    print("\n--- Signal Flow (ASCII) ---")

    # Find input and output nodes
    inputs = [n for n in patch.nodes if n.node_type.value == "input"]
    outputs = [n for n in patch.nodes if n.node_type.value == "output"]
    processors = [n for n in patch.nodes if n.node_type.value not in ("input", "output")]

    print("\n  INPUTS          PROCESSORS          OUTPUTS")
    print("  ------          ----------          -------")

    max_rows = max(len(inputs), len(processors), len(outputs))

    for i in range(max_rows):
        row = "  "
        if i < len(inputs):
            row += f"[{inputs[i].id:10}]"
        else:
            row += " " * 12

        row += "  →  "

        if i < len(processors):
            row += f"[{processors[i].id:10}]"
        else:
            row += " " * 12

        row += "  →  "

        if i < len(outputs):
            row += f"[{outputs[i].id:10}]"
        else:
            row += " " * 12

        print(row)


def validate_patch(patchbay: PatchBay, patch: PatchDescriptor) -> bool:
    """Validate patch configuration."""
    print("\n--- Validation ---")

    success = patchbay.load_patch(patch)

    if success:
        print("  ✓ Patch loaded successfully")
    else:
        print("  ✗ Patch failed to load")
        return False

    # Check for orphan nodes
    connected_nodes = set()
    for conn in patch.connections:
        connected_nodes.add(conn.source_node)
        connected_nodes.add(conn.dest_node)

    all_nodes = {n.id for n in patch.nodes}
    orphans = all_nodes - connected_nodes

    if orphans:
        print(f"  ⚠ Orphan nodes (not connected): {', '.join(orphans)}")
    else:
        print("  ✓ All nodes connected")

    # Check execution order
    order = patchbay.get_execution_order()
    if len(order) == len(patch.nodes):
        print("  ✓ Execution order valid")
    else:
        print("  ⚠ Some nodes may not be executed")

    return True


def export_patch(patch: PatchDescriptor, output_path: str, format: str):
    """Export patch to file."""
    if format == "json":
        content = patch.to_json()
    elif format == "yaml":
        content = patch.to_yaml()
    else:
        raise ValueError(f"Unknown format: {format}")

    with open(output_path, 'w') as f:
        f.write(content)

    print(f"\nExported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="BeatOven Patch Inspector")
    parser.add_argument("patch", nargs="?", help="Path to patch file (JSON or YAML)")
    parser.add_argument("--default", action="store_true", help="Use default patch")
    parser.add_argument("--validate", action="store_true", help="Validate patch")
    parser.add_argument("--order", action="store_true", help="Show execution order")
    parser.add_argument("--ascii", action="store_true", help="ASCII visualization")
    parser.add_argument("--export", help="Export patch to file")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Export format")

    args = parser.parse_args()

    # Load patch
    if args.default:
        patch = create_default_patch()
        print("Using default BeatOven patch")
    elif args.patch:
        patch = load_patch(args.patch)
        print(f"Loaded patch from: {args.patch}")
    else:
        parser.print_help()
        return

    # Create patchbay
    patchbay = PatchBay()

    # Print basic info
    print_patch_info(patch)

    # Validation
    if args.validate:
        validate_patch(patchbay, patch)
    else:
        patchbay.load_patch(patch)

    # Execution order
    if args.order:
        print_execution_order(patchbay)

    # ASCII visualization
    if args.ascii:
        visualize_ascii(patch)

    # Export
    if args.export:
        export_patch(patch, args.export, args.format)


if __name__ == "__main__":
    main()
