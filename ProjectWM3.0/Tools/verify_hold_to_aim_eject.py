import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools


PATH = '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'


def pin(node, name, direction):
    return next((item for item in node.list_all_pins()
                 if item.get_pin_name() == name and item.get_pin_direction() == direction), None)


bp = unreal.load_asset(PATH)
graph = next(item for item in BlueprintTools.list_graphs(bp) if item.get_name() == 'EventGraph')
nodes = list(BlueprintTools.find_nodes(graph))
left_mouse = next(item for item in nodes if item.get_name() == 'K2Node_InputKey_2')
begin_node = next((item for item in nodes if item.get_node_title() == 'BeginTrashAim'), None)
release_node = next((item for item in nodes if item.get_node_title() == 'ReleaseTrashAimAndEject'), None)
if not begin_node or not release_node:
    raise RuntimeError('Hold-to-aim call node is missing')

pressed = pin(left_mouse, 'Pressed', unreal.EdGraphPinDirection.EGPD_OUTPUT)
released = pin(left_mouse, 'Released', unreal.EdGraphPinDirection.EGPD_OUTPUT)
begin_execute = pin(begin_node, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
release_execute = pin(release_node, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
begin_type = pin(begin_node, 'SelectedTrashType', unreal.EdGraphPinDirection.EGPD_INPUT)
release_type = pin(release_node, 'SelectedTrashType', unreal.EdGraphPinDirection.EGPD_INPUT)

pressed_ok = begin_execute in pressed.list_connected_pins()
released_ok = release_execute in released.list_connected_pins()
begin_type_ok = bool(begin_type.list_connected_pins())
release_type_ok = bool(release_type.list_connected_pins())
unreal.log_warning(
    'HOLD_AIM_EJECT_VERIFY pressed_ok={} released_ok={} begin_type_ok={} release_type_ok={}'.format(
        pressed_ok, released_ok, begin_type_ok, release_type_ok
    )
)
if not all((pressed_ok, released_ok, begin_type_ok, release_type_ok)):
    raise RuntimeError('Hold-to-aim eject graph validation failed')
