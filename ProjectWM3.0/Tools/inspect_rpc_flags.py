import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')
import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools

bp = unreal.load_asset('/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1')
graph = next(g for g in BlueprintTools.list_graphs(bp) if g.get_name() == 'EventGraph')
for node in BlueprintTools.find_nodes(graph):
    if node.get_name() in ('K2Node_CustomEvent_7', 'K2Node_CustomEvent_4', 'K2Node_CustomEvent_6'):
        props = []
        for name in ['function_flags', 'event_reference', 'custom_function_name', 'b_is_override']:
            try:
                props.append('{}={}'.format(name, node.get_editor_property(name)))
            except Exception as exc:
                props.append('{}=ERR:{}'.format(name, exc))
        unreal.log_warning('RPC_FLAGS {} title={} {}'.format(node.get_name(), node.get_node_title(), ' | '.join(props)))
