import yaml
from langgraph.graph import Graph

def load_graph(config_path: str) -> Graph:
    """
    Loads a LangGraph graph from a YAML configuration file.

    Args:
        config_path: The path to the YAML configuration file.

    Returns:
        A LangGraph graph object.
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    graph = Graph()
    
    # Add nodes
    for node_name, node_config in config.get('nodes', {}).items():
        # This is a simplified example. A more robust implementation would
        # dynamically import the callables and handle different node types.
        graph.add_node(node_name, lambda x: x)

    # Add edges
    for edge_config in config.get('edges', []):
        graph.add_edge(edge_config['source'], edge_config['target'])
        
    return graph