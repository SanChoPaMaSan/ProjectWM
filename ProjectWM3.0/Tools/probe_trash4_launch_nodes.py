import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools, _get_node_type_id

bp = unreal.load_asset('/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1')
graph = next(g for g in BlueprintTools.list_graphs(bp) if g.get_name() == 'EventGraph')
for node_type in ['피직스|SetSimulatePhysics', '피직스|SetEnableGravity']:
    node = BlueprintTools.create_node(graph, node_type, unreal.IntPoint(-10000, -10000))
    unreal.log_warning('TRASH4_PROBE type={} result={} pins={}'.format(
        node_type, _get_node_type_id(node), [p.get_pin_name() for p in node.list_all_pins()]))
