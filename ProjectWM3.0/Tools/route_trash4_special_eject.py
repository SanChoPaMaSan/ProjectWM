import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools

BLUEPRINT_PATH = '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'

bp = unreal.load_asset(BLUEPRINT_PATH)
if not bp:
    raise RuntimeError('Could not load {}'.format(BLUEPRINT_PATH))

event_graph = next((g for g in BlueprintTools.list_graphs(bp) if g.get_name() == 'EventGraph'), None)
if not event_graph:
    raise RuntimeError('EventGraph not found')

nodes = {node.get_name(): node for node in BlueprintTools.find_nodes(event_graph)}
trash4_set_mesh = nodes.get('K2Node_VariableSet_18')
special_detach = nodes.get('K2Node_CallFunction_25')
if not trash4_set_mesh or not special_detach:
    raise RuntimeError('Required Trash4 or special-eject nodes were not found')

def pin(node, name, direction):
    result = next((p for p in node.list_all_pins()
                   if p.get_pin_name() == name and p.get_pin_direction() == direction), None)
    if not result:
        raise RuntimeError('Pin {}.{} not found'.format(node.get_name(), name))
    return result

trash4_then = pin(trash4_set_mesh, 'then', unreal.EdGraphPinDirection.EGPD_OUTPUT)
detach_execute = pin(special_detach, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)

# The Detach node accepts the existing Trash3 source and this Trash4 source.
# Creating this link automatically replaces Trash4's old ContinueEject link,
# leaving Trash1 and Trash2 on their current generic path.
if detach_execute not in trash4_then.list_connected_pins():
    if not trash4_then.try_create_connection(detach_execute):
        raise RuntimeError('Could not route Trash4 into the special eject chain')

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_loaded_asset(bp)

targets = ['{}:{}'.format(p.get_owning_node().get_name(), p.get_pin_name())
           for p in trash4_then.list_connected_pins()]
sources = ['{}:{}'.format(p.get_owning_node().get_name(), p.get_pin_name())
           for p in detach_execute.list_connected_pins()]
unreal.log_warning('TRASH4_SPECIAL_EJECT saved targets={} detach_sources={}'.format(targets, sources))
