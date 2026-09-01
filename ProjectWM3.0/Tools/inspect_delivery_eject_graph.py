import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools, _get_node_type_id

PATH = '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'
bp = unreal.load_asset(PATH)
if not bp:
    raise RuntimeError('Could not load {}'.format(PATH))

event_graph = next(graph for graph in BlueprintTools.list_graphs(bp) if graph.get_name() == 'EventGraph')
wanted = {
    'K2Node_VariableSet_18', 'K2Node_VariableSet_27', 'K2Node_VariableSet_28',
    'K2Node_CallFunction_64',
    'K2Node_CallFunction_25', 'K2Node_CallFunction_94', 'K2Node_CallFunction_5',
    'K2Node_CallFunction_91', 'K2Node_CallFunction_68', 'K2Node_CallFunction_78',
    'K2Node_CallFunction_83', 'K2Node_CallFunction_85', 'K2Node_CallFunction_86',
}
for node in BlueprintTools.find_nodes(event_graph):
    if node.get_name() not in wanted:
        continue
    entries = []
    for pin in node.list_all_pins():
        targets = ['{}:{}'.format(p.get_owning_node().get_name(), p.get_pin_name()) for p in pin.list_connected_pins()]
        entries.append('{} {} {} {} -> {}'.format(pin.get_pin_direction(), pin.get_pin_name(), pin.get_pin_type_display_string(), pin.get_pin_value(), targets))
    unreal.log_warning('EJECT_DETAIL {} | type={} | {} | {}'.format(node.get_name(), _get_node_type_id(node), node.get_node_title(), ' || '.join(entries)))

# API probe only: this commandlet does not save the blueprint.  It verifies that
# a custom event can be called from more than one ejection branch.
probe_event = BlueprintTools.create_node(event_graph, 'AddEvent|Custom|_TempEjectProbe', unreal.IntPoint(0, 0))
try:
    probe_call = BlueprintTools.create_node(event_graph, '|_TempEjectProbe', unreal.IntPoint(400, 0))
    unreal.log_warning('EJECT_PROBE custom-call={}'.format(probe_call.get_node_title()))
except Exception as exc:
    unreal.log_warning('EJECT_PROBE failed={}'.format(exc))

nodes_by_name = {node.get_name(): node for node in BlueprintTools.find_nodes(event_graph)}
trash4_then = next(pin for pin in nodes_by_name['K2Node_VariableSet_18'].list_all_pins()
                   if pin.get_pin_name() == 'then' and pin.get_pin_direction() == unreal.EdGraphPinDirection.EGPD_OUTPUT)
detach_exec = next(pin for pin in nodes_by_name['K2Node_CallFunction_25'].list_all_pins()
                   if pin.get_pin_name() == 'execute' and pin.get_pin_direction() == unreal.EdGraphPinDirection.EGPD_INPUT)
try:
    connected = trash4_then.try_create_connection(detach_exec)
    unreal.log_warning('EJECT_PROBE direct-special={} trash4links={} detachlinks={}'.format(
        connected, len(trash4_then.list_connected_pins()), len(detach_exec.list_connected_pins())))
except Exception as exc:
    unreal.log_warning('EJECT_PROBE direct-special-failed={}'.format(exc))
