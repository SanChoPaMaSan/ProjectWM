import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools

BLUEPRINT_PATH = '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1'


def get_pin(node, name, direction):
    result = next((pin for pin in node.list_all_pins()
                   if pin.get_pin_name() == name and pin.get_pin_direction() == direction), None)
    if not result:
        raise RuntimeError('Missing pin {}.{}'.format(node.get_name(), name))
    return result


def linked_names(pin):
    return ['{}:{}'.format(link.get_owning_node().get_name(), link.get_pin_name())
            for link in pin.list_connected_pins()]


bp = unreal.load_asset(BLUEPRINT_PATH)
if not bp:
    raise RuntimeError('Could not load {}'.format(BLUEPRINT_PATH))

graph = next((g for g in BlueprintTools.list_graphs(bp) if g.get_name() == 'EventGraph'), None)
if not graph:
    raise RuntimeError('EventGraph not found')

nodes = {node.get_name(): node for node in BlueprintTools.find_nodes(graph)}

# Current Trash4 branch: its own collision response is valid, but it was then
# connected to the shared Trash3 glide branch.  Keep the Trash4 nodes up to
# collision response and replace only the post-collision execution path.
trash4_collision_response = nodes.get('K2Node_CallFunction_91')
trash3_glide_simulate = nodes.get('K2Node_CallFunction_103')
launch_velocity = nodes.get('K2Node_CallFunction_107')
mesh_getter = nodes.get('K2Node_VariableGet_68')
if not all([trash4_collision_response, trash3_glide_simulate, launch_velocity, mesh_getter]):
    raise RuntimeError('Required Trash4 launch nodes are missing')

collision_then = get_pin(trash4_collision_response, 'then', unreal.EdGraphPinDirection.EGPD_OUTPUT)
trash3_simulate_execute = get_pin(trash3_glide_simulate, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
velocity_execute = get_pin(launch_velocity, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
mesh_output = get_pin(mesh_getter, 'CurrentEjectMesh', unreal.EdGraphPinDirection.EGPD_OUTPUT)

if trash3_simulate_execute in collision_then.list_connected_pins():
    collision_then.break_single_pin_link(trash3_simulate_execute)

# Trash4 uses the same initial velocity and spin nodes as Trash3, but gravity
# remains on and no Trash3-only IsGliding variable is touched.
trash4_simulate = BlueprintTools.create_node(
    graph, '피직스|SetSimulatePhysics', unreal.IntPoint(1880, 1180))
trash4_gravity = BlueprintTools.create_node(
    graph, '피직스|SetEnableGravity', unreal.IntPoint(2110, 1180))

simulate_execute = get_pin(trash4_simulate, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
simulate_then = get_pin(trash4_simulate, 'then', unreal.EdGraphPinDirection.EGPD_OUTPUT)
simulate_target = get_pin(trash4_simulate, 'self', unreal.EdGraphPinDirection.EGPD_INPUT)
simulate_value = get_pin(trash4_simulate, 'bSimulate', unreal.EdGraphPinDirection.EGPD_INPUT)
gravity_execute = get_pin(trash4_gravity, 'execute', unreal.EdGraphPinDirection.EGPD_INPUT)
gravity_then = get_pin(trash4_gravity, 'then', unreal.EdGraphPinDirection.EGPD_OUTPUT)
gravity_target = get_pin(trash4_gravity, 'self', unreal.EdGraphPinDirection.EGPD_INPUT)
gravity_value = get_pin(trash4_gravity, 'bGravityEnabled', unreal.EdGraphPinDirection.EGPD_INPUT)

if not simulate_value.set_pin_value('true'):
    raise RuntimeError('Could not set Trash4 Simulate Physics to true')
if not gravity_value.set_pin_value('true'):
    raise RuntimeError('Could not set Trash4 Enable Gravity to true')

for output, input_pin, description in [
    (collision_then, simulate_execute, 'Trash4 collision -> simulate'),
    (mesh_output, simulate_target, 'Mesh -> simulate target'),
    (simulate_then, gravity_execute, 'simulate -> gravity'),
    (mesh_output, gravity_target, 'Mesh -> gravity target'),
    (gravity_then, velocity_execute, 'gravity -> shared launch velocity'),
]:
    if input_pin not in output.list_connected_pins() and not output.try_create_connection(input_pin):
        raise RuntimeError('Could not create connection: {}'.format(description))

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
if not unreal.EditorAssetLibrary.save_loaded_asset(bp):
    raise RuntimeError('Could not save {}'.format(BLUEPRINT_PATH))

unreal.log_warning(
    'TRASH4_GRAVITY_LAUNCH saved collision={} simulate={} gravity={} velocity={} sim_default={} gravity_default={}'.format(
        linked_names(collision_then), linked_names(simulate_then), linked_names(gravity_then),
        linked_names(velocity_execute), simulate_value.get_pin_value(), gravity_value.get_pin_value()))
