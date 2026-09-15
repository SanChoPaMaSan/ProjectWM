import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools


PATHS = (
    '/Game/Fab/Car/BP/BP_RoadPathStart',
    '/Game/Fab/Car/BP/BP_RoadPathEnd',
) + tuple('/Game/Fab/Car/BP/BP_Car{}'.format(index) for index in range(1, 8))

for path in PATHS:
    bp = unreal.load_asset(path)
    if not bp:
        raise RuntimeError('Missing {}'.format(path))
    parent = unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp)
    generated = unreal.load_class(None, '{}.{}_C'.format(path, bp.get_name()))
    cdo = unreal.get_default_object(generated) if generated else None
    components = []
    if cdo:
        for component in cdo.get_components_by_class(unreal.ActorComponent):
            components.append('{}:{}'.format(component.get_name(), component.get_class().get_name()))
    graph_nodes = []
    for graph in BlueprintTools.list_graphs(bp):
        if graph.get_name() == 'EventGraph':
            graph_nodes = ['{}={}'.format(node.get_name(), node.get_node_title())
                           for node in BlueprintTools.find_nodes(graph)]
    unreal.log_warning('CAR_TRAFFIC_INSPECT asset={} parent={} components={} variables={} nodes={}'.format(
        bp.get_name(), parent.get_path_name() if parent else None, components,
        BlueprintTools.list_variables(bp), graph_nodes))
