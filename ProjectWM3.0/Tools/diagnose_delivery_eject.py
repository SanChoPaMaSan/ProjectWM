import sys

# EditorToolset is an engine editor plugin. Add its Python package only for
# this read-only commandlet; no project setting is changed.
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools, _get_node_type_id


PATH = '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'
KEYWORDS = (
    'eject', 'release', 'currenteject', 'heldtrash', 'trashreleasequeue',
    'isejecting', 'detach', 'hidden', 'simulate physics', 'enable gravity',
    'add impulse', 'staticmeshcomponent', 'server_', 'multicast', 'trash1',
    'trash2', 'trash3', 'trash4', 'delay',
)
TARGET_NAMES = {
    'K2Node_IfThenElse_4', 'K2Node_IfThenElse_8', 'K2Node_IfThenElse_9',
    'K2Node_IfThenElse_10', 'K2Node_IfThenElse_11', 'K2Node_IfThenElse_13',
    'K2Node_MacroInstance_1', 'K2Node_GetArrayItem_0', 'K2Node_GetArrayItem_1',
    'K2Node_GetArrayItem_2', 'K2Node_GetArrayItem_3', 'K2Node_GetArrayItem_4',
    'K2Node_CallArrayFunction_3', 'K2Node_CallArrayFunction_4',
    'K2Node_CallArrayFunction_5', 'K2Node_CallArrayFunction_13',
    'K2Node_CallArrayFunction_17', 'K2Node_CallArrayFunction_18',
    'K2Node_CallArrayFunction_19', 'K2Node_CallFunction_37',
    'K2Node_CallFunction_46', 'K2Node_CallFunction_47', 'K2Node_CallFunction_64',
    'K2Node_SwitchInteger_1', 'K2Node_PromotableOperator_22',
    'K2Node_VariableGet_4', 'K2Node_VariableGet_51', 'K2Node_VariableSet_22',
}


def connected(pin):
    return ['{}.{}'.format(p.get_owning_node().get_name(), p.get_pin_name()) for p in pin.list_connected_pins()]


bp = unreal.load_asset(PATH)
if not bp:
    raise RuntimeError('Missing {}'.format(PATH))

unreal.log_warning('EJECT_DIAG_BEGIN path={}'.format(PATH))
for graph in BlueprintTools.list_graphs(bp):
    matches = []
    for node in BlueprintTools.find_nodes(graph):
        descriptor = '{} {} {}'.format(node.get_name(), node.get_node_title(), _get_node_type_id(node)).lower()
        if node.get_name() in TARGET_NAMES or any(keyword in descriptor for keyword in KEYWORDS):
            matches.append(node)

    if not matches:
        continue

    unreal.log_warning('EJECT_DIAG_GRAPH {} nodes={}'.format(graph.get_name(), len(matches)))
    for node in matches:
        details = []
        for pin in node.list_all_pins():
            links = connected(pin)
            name = pin.get_pin_name()
            if links or name in ('execute', 'then', 'TrashActor', 'CurrentEjectActor', 'CurrentEjectMesh', 'Target', 'ReturnValue', 'Array Element'):
                details.append('{} {}={} -> {}'.format(pin.get_pin_direction(), name, pin.get_pin_value(), links))
        unreal.log_warning('EJECT_DIAG_NODE graph={} name={} type={} title={} pins={}'.format(
            graph.get_name(), node.get_name(), _get_node_type_id(node), node.get_node_title(), ' | '.join(details)))

unreal.log_warning('EJECT_DIAG_END')
