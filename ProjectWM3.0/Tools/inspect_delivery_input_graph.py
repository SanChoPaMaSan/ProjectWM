import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools, _get_node_type_id

bp = unreal.load_asset('/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1')
graph = next(item for item in BlueprintTools.list_graphs(bp) if item.get_name() == 'EventGraph')
for node in BlueprintTools.find_nodes(graph):
    descriptor = '{} {} {}'.format(node.get_name(), node.get_node_title(), _get_node_type_id(node)).lower()
    if node.get_name() not in ('K2Node_VariableSet_1', 'K2Node_VariableSet_2', 'K2Node_IfThenElse_1', 'K2Node_EventTick_0', 'K2Node_MakeArray_0') and not any(term in descriptor for term in ('inputkey', 'right mouse', 'absorb', 'pickup', 'suction', 'trashactor', 'overlap', 'eventtick')):
        continue
    pins = []
    for item in node.list_all_pins():
        links = ['{}:{}'.format(link.get_owning_node().get_name(), link.get_pin_name())
                 for link in item.list_connected_pins()]
        if node.get_name() == 'K2Node_MakeArray_0' or links or item.get_pin_name() in ('Pressed', 'Released', 'execute', 'then', 'Key', 'TrashActor'):
            pins.append('{}={} -> {}'.format(item.get_pin_name(), item.get_pin_value(), links))
    unreal.log_warning('DELIVERY_INPUT|name={}|type={}|title={}|pins={}'.format(
        node.get_name(), _get_node_type_id(node), node.get_node_title(), ' ; '.join(pins)))
