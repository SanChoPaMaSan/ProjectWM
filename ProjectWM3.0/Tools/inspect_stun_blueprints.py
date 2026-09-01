import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools, _get_node_type_id

PATHS = [
    '/Game/Fab/Trash/T/BP_Trash4',
    '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1',
]

for path in PATHS:
    bp = unreal.load_asset(path)
    if not bp:
        unreal.log_error('STUN missing {}'.format(path))
        continue
    parent = unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp)
    unreal.log_warning('STUN_BP path={} parent={} graphs={}'.format(
        path, parent.get_path_name() if parent else 'None', [g.get_name() for g in BlueprintTools.list_graphs(bp)]))
    generated = unreal.load_class(None, path + '.' + bp.get_name() + '_C')
    cdo = unreal.get_default_object(generated)
    for prop in ['b_replicates', 'b_replicate_movement']:
        try:
            unreal.log_warning('STUN_PROP {} {}={}'.format(path, prop, cdo.get_editor_property(prop)))
        except Exception:
            pass
    for graph in BlueprintTools.list_graphs(bp):
        for node in BlueprintTools.find_nodes(graph):
            title = node.get_node_title()
            if any(x.lower() in title.lower() for x in ['overlap', 'move', 'input', 'suction', 'eject', 'trash', 'stun']):
                pins = []
                for pin in node.list_all_pins():
                    linked = ['{}:{}'.format(p.get_owning_node().get_name(), p.get_pin_name()) for p in pin.list_connected_pins()]
                    pins.append('{} {} -> {}'.format(pin.get_pin_direction(), pin.get_pin_name(), linked))
                unreal.log_warning('STUN_NODE {} {} {} type={} pins={}'.format(
                    bp.get_name(), graph.get_name(), node.get_name(), _get_node_type_id(node), ' | '.join(pins)))
