import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools


PATH = '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'


def pin(node, name, direction):
    result = next((item for item in node.list_all_pins()
                   if item.get_pin_name() == name and item.get_pin_direction() == direction), None)
    if not result:
        raise RuntimeError('Missing pin {}.{}'.format(node.get_name(), name))
    return result


bp = unreal.load_asset(PATH)
if not bp:
    raise RuntimeError('Missing {}'.format(PATH))
graph = next((item for item in BlueprintTools.list_graphs(bp) if item.get_name() == 'EventGraph'), None)
if not graph:
    raise RuntimeError('Missing EventGraph')

nodes = {item.get_name(): item for item in BlueprintTools.find_nodes(graph)}
left_mouse = nodes.get('K2Node_InputKey_2')
old_switch = nodes.get('K2Node_SwitchInteger_1')
selected_type = nodes.get('K2Node_VariableGet_50')
if not all((left_mouse, old_switch, selected_type)):
    raise RuntimeError('Required left-mouse release nodes are missing')

pressed = pin(left_mouse, 'Pressed', unreal.EdGraphPinDirection.EGPD_OUTPUT)
old_execute = pin(old_switch, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
selected_output = pin(selected_type, 'SelectedTrashType', unreal.EdGraphPinDirection.EGPD_OUTPUT)

server_node = next((item for item in BlueprintTools.find_nodes(graph)
                    if item.get_node_title() == 'ServerEjectSelectedTrash'), None)
if not server_node:
    server_node = BlueprintTools.create_node(graph, 'Trash|ServerEjectSelectedTrash', unreal.IntPoint(3520, 580))

server_execute = pin(server_node, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
server_type = pin(server_node, 'SelectedTrashType', unreal.EdGraphPinDirection.EGPD_INPUT)

# The old path runs on the owning client and removes its local replicated array
# before its Actor reference reaches the server.  Replace it with the RPC; the
# server now resolves and removes the true held Actor itself.
if old_execute in pressed.list_connected_pins():
    pressed.break_single_pin_link(old_execute)

for source, target, label in (
    (pressed, server_execute, 'left mouse -> server eject'),
    (selected_output, server_type, 'selected type -> server eject'),
):
    if target not in source.list_connected_pins() and not source.try_create_connection(target):
        raise RuntimeError('Failed connection {}'.format(label))

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
if not unreal.EditorAssetLibrary.save_loaded_asset(bp):
    raise RuntimeError('Could not save {}'.format(PATH))

unreal.log_warning('SERVER_EJECT_V2 saved pressed_targets={} selected_targets={}'.format(
    ['{}:{}'.format(item.get_owning_node().get_name(), item.get_pin_name()) for item in pressed.list_connected_pins()],
    ['{}:{}'.format(item.get_owning_node().get_name(), item.get_pin_name()) for item in selected_output.list_connected_pins()]))
