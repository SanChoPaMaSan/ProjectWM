import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools

path = '/Game/Fab/Trash/T/BP_Trash2'
bp = unreal.load_asset(path)
if not bp:
    raise RuntimeError('Missing BP_Trash2')

generated = unreal.load_class(None, path + '.BP_Trash2_C')
cdo = unreal.get_default_object(generated)
unreal.log_warning('TRASH2_SETUP parent={} class={}'.format(
    unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp).get_path_name(), generated))
for component in cdo.get_components_by_class(unreal.ActorComponent):
    unreal.log_warning('TRASH2_SETUP component={} class={}'.format(
        component.get_name(), component.get_class().get_name()))

for graph in BlueprintTools.list_graphs(bp):
    if graph.get_name() != 'EventGraph':
        continue
    for node in BlueprintTools.find_nodes(graph):
        pins = []
        for pin in node.list_all_pins():
            targets = ['{}:{}'.format(item.get_owning_node().get_node_title(), item.get_pin_name())
                       for item in pin.list_connected_pins()]
            pins.append('{}=[{}]'.format(pin.get_pin_name(), ','.join(targets)))
        unreal.log_warning('TRASH2_SETUP node={} title={} pins={}'.format(
            node.get_name(), node.get_node_title(), '; '.join(pins)))

component = unreal.load_object(None, path + '.BP_Trash2_C:trash_1_GEN_VARIABLE')
unreal.log_warning('TRASH2_SETUP mesh_component={} mesh={} visible={} collision={} gravity={}'.format(
    component, component.get_editor_property('static_mesh') if component else None,
    component.get_editor_property('visible') if component else None,
    component.get_collision_enabled() if component else None,
    component.is_gravity_enabled() if component else None))
