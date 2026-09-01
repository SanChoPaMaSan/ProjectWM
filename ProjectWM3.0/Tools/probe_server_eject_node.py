import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools

bp = unreal.load_asset('/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1')
graph = next(g for g in BlueprintTools.list_graphs(bp) if g.get_name() == 'EventGraph')
available = unreal.BlueprintGraphEditor.get_graph_editor(graph).list_available_nodes([])
for node_id in available:
    if 'ServerEjectSelectedTrash'.lower() in node_id.lower():
        unreal.log_warning('SERVER_EJECT_NODE {}'.format(node_id))
