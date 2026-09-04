import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools


path = '/Game/Fab/Trash/BP_HouseTrashZone'
bp = unreal.load_asset(path)
if not bp:
    raise RuntimeError('Missing {}'.format(path))

unreal.log_warning('HOUSE_TRASH_ZONE variables={}'.format(BlueprintTools.list_variables(bp)))
for graph in BlueprintTools.list_graphs(bp):
    if graph.get_name() != 'EventGraph':
        continue
    for node in BlueprintTools.find_nodes(graph):
        title = node.get_node_title()
        pins = []
        for pin in node.list_all_pins():
            targets = ['{}:{}'.format(item.get_owning_node().get_node_title(), item.get_pin_name())
                       for item in pin.list_connected_pins()]
            pins.append('{} [{}]'.format(pin.get_pin_name(), ','.join(targets)))
        unreal.log_warning('HOUSE_TRASH_ZONE node={} title={} pins={}'.format(
            node.get_name(), title, '; '.join(pins)))

if not unreal.EditorLoadingAndSavingUtils.load_map('/Game/LEVEL/WM'):
    raise RuntimeError('Could not load WM')
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if actor.get_class().get_name() != 'BP_HouseTrashZone_C':
        continue
    unreal.log_warning('HOUSE_TRASH_ZONE actor={} label={} props={}'.format(
        actor.get_name(), actor.get_actor_label(),
        {name: actor.get_editor_property(name) for name in ('HouseID', 'TrashCount', 'CurrentTrashCount')
         if actor.has_editor_property(name)}))
