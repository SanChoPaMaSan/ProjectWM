import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools

PATH = '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'


def find_pin(node, name, direction):
    return next((pin for pin in node.list_all_pins()
                 if pin.get_pin_name() == name and pin.get_pin_direction() == direction), None)


bp = unreal.load_asset(PATH)
graph = next(graph for graph in BlueprintTools.list_graphs(bp) if graph.get_name() == 'EventGraph')
nodes = {node.get_name(): node for node in BlueprintTools.find_nodes(graph)}
left_mouse = nodes['K2Node_InputKey_2']
old_switch = nodes['K2Node_SwitchInteger_1']
pressed = find_pin(left_mouse, 'Pressed', unreal.EdGraphPinDirection.EGPD_OUTPUT)
old_execute = find_pin(old_switch, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
server_node = next((node for node in BlueprintTools.find_nodes(graph)
                    if node.get_node_title() == 'ServerEjectSelectedTrash'), None)
if not server_node:
    raise RuntimeError('ServerEjectSelectedTrash node missing')
server_execute = find_pin(server_node, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
server_type = find_pin(server_node, 'SelectedTrashType', unreal.EdGraphPinDirection.EGPD_INPUT)

pressed_targets = ['{}:{}'.format(pin.get_owning_node().get_name(), pin.get_pin_name())
                   for pin in pressed.list_connected_pins()]
old_is_disconnected = old_execute not in pressed.list_connected_pins()
server_is_connected = server_execute in pressed.list_connected_pins()
type_is_connected = bool(server_type.list_connected_pins())
unreal.log_warning('SERVER_EJECT_VERIFY old_disconnected={} server_connected={} type_connected={} pressed_targets={}'.format(
    old_is_disconnected, server_is_connected, type_is_connected, pressed_targets))
if not (old_is_disconnected and server_is_connected and type_is_connected):
    raise RuntimeError('Server-authoritative eject graph validation failed')
