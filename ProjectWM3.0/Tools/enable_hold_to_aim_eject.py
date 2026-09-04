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


def find_or_create_call(graph, title, query, location):
    node = next((item for item in BlueprintTools.find_nodes(graph)
                 if item.get_node_title() == title), None)
    return node or BlueprintTools.create_node(graph, query, location)


bp = unreal.load_asset(PATH)
if not bp:
    raise RuntimeError('Missing {}'.format(PATH))
graph = next((item for item in BlueprintTools.list_graphs(bp) if item.get_name() == 'EventGraph'), None)
if not graph:
    raise RuntimeError('Missing EventGraph')

nodes = {item.get_name(): item for item in BlueprintTools.find_nodes(graph)}
left_mouse = nodes.get('K2Node_InputKey_2')
selected_type = nodes.get('K2Node_VariableGet_50')
if not left_mouse or not selected_type:
    raise RuntimeError('Required left mouse or SelectedTrashType node is missing')

pressed = pin(left_mouse, 'Pressed', unreal.EdGraphPinDirection.EGPD_OUTPUT)
released = pin(left_mouse, 'Released', unreal.EdGraphPinDirection.EGPD_OUTPUT)
selected_output = pin(selected_type, 'SelectedTrashType', unreal.EdGraphPinDirection.EGPD_OUTPUT)

old_server_node = next((item for item in BlueprintTools.find_nodes(graph)
                        if item.get_node_title() == 'ServerEjectSelectedTrash'), None)
if old_server_node:
    old_server_execute = pin(old_server_node, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
    if old_server_execute in pressed.list_connected_pins():
        pressed.break_single_pin_link(old_server_execute)

begin_node = find_or_create_call(
    graph, 'BeginTrashAim', 'Trash|Trajectory|BeginTrashAim', unreal.IntPoint(3520, 460))
release_node = find_or_create_call(
    graph, 'ReleaseTrashAimAndEject', 'Trash|Trajectory|ReleaseTrashAimAndEject', unreal.IntPoint(3520, 680))

begin_execute = pin(begin_node, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
begin_type = pin(begin_node, 'SelectedTrashType', unreal.EdGraphPinDirection.EGPD_INPUT)
release_execute = pin(release_node, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
release_type = pin(release_node, 'SelectedTrashType', unreal.EdGraphPinDirection.EGPD_INPUT)

for source, target, label in (
    (pressed, begin_execute, 'Pressed -> BeginTrashAim'),
    (selected_output, begin_type, 'SelectedTrashType -> BeginTrashAim'),
    (released, release_execute, 'Released -> ReleaseTrashAimAndEject'),
    (selected_output, release_type, 'SelectedTrashType -> ReleaseTrashAimAndEject'),
):
    if target not in source.list_connected_pins() and not source.try_create_connection(target):
        raise RuntimeError('Failed connection {}'.format(label))

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
if not unreal.EditorAssetLibrary.save_loaded_asset(bp):
    raise RuntimeError('Could not save {}'.format(PATH))

unreal.log_warning(
    'HOLD_AIM_EJECT saved pressed={} released={} begin_type={} release_type={}'.format(
        ['{}:{}'.format(item.get_owning_node().get_name(), item.get_pin_name()) for item in pressed.list_connected_pins()],
        ['{}:{}'.format(item.get_owning_node().get_name(), item.get_pin_name()) for item in released.list_connected_pins()],
        bool(begin_type.list_connected_pins()), bool(release_type.list_connected_pins())
    )
)
