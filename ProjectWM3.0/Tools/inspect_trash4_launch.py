import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools, _get_node_type_id

path = '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'
bp = unreal.load_asset(path)
event_graph = next(g for g in BlueprintTools.list_graphs(bp) if g.get_name() == 'EventGraph')

for node in BlueprintTools.find_nodes(event_graph):
    title = node.get_node_title()
    if not any(key in title for key in [
        'BP_Trash3', 'BP_Trash4', 'CurrentEjectTrash3', 'CurrentEjectTrash4',
        'CurrentEjectMesh', 'Detach From Actor', 'Set Actor Location',
        'SetCollisionEnabled', 'SetCollisionResponseToChannel', 'SetSimulatePhysics',
        'SetEnableGravity', 'SetPhysicsLinearVelocity', 'SetPhysicsAngularVelocity',
        'ContinueEject', 'Multicast_ShowTrash'
    ]):
        continue
    pins = []
    for pin in node.list_all_pins():
        links = ['{}:{}'.format(p.get_owning_node().get_name(), p.get_pin_name()) for p in pin.list_connected_pins()]
        pins.append('{} {}={} -> {}'.format(pin.get_pin_direction(), pin.get_pin_name(), pin.get_pin_value(), links))
    unreal.log_warning('LAUNCH_NODE {} type={} title={} pins={}'.format(
        node.get_name(), _get_node_type_id(node), title, ' || '.join(pins)))
