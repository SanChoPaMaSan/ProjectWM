import sys
sys.path.insert(0, r'C:\Program Files\Epic Games\UE_5.8\Engine\Plugins\Experimental\Toolsets\EditorToolset\Content\Python')

import unreal
from editor_toolset.toolsets.blueprint import BlueprintTools


def log(message):
    unreal.log_warning('TRASH2_SPAWN {}'.format(message))


for path in ('/Game/Fab/Trash/T/BP_Trash2', '/Game/Fab/Trash/BP_TrashZoneSpawner'):
    bp = unreal.load_asset(path)
    if not bp:
        raise RuntimeError('Missing {}'.format(path))
    generated = unreal.load_class(None, '{}.{}_C'.format(path, bp.get_name()))
    cdo = unreal.get_default_object(generated) if generated else None
    log('asset={} generated={} cdo={}'.format(path, generated, bool(cdo)))
    if path.endswith('BP_Trash2') and cdo:
        for component in cdo.get_components_by_class(unreal.PrimitiveComponent):
            log('trash2_component={} collision={} simulating={}'.format(
                component.get_name(), component.get_collision_enabled(),
                component.is_simulating_physics()))

    for graph in BlueprintTools.list_graphs(bp):
        if graph.get_name() != 'EventGraph':
            continue
        for node in BlueprintTools.find_nodes(graph):
            title = node.get_node_title()
            if any(key in title for key in ('Spawn', 'ForLoop', 'Array', 'Trash', 'Random', 'Branch', 'BeginPlay')):
                pins = []
                for pin in node.list_all_pins():
                    targets = ['{}:{}'.format(item.get_owning_node().get_name(), item.get_pin_name())
                               for item in pin.list_connected_pins()]
                    pins.append('{} links={} [{}]'.format(pin.get_pin_name(), len(targets), ','.join(targets)))
                log('node={} title={} pins={}'.format(node.get_name(), title, '; '.join(pins)))

    if path.endswith('BP_TrashZoneSpawner'):
        for property_name in ('trash_count', 'spawn_succeeded'):
            try:
                log('spawner_default {}={}'.format(
                    property_name, cdo.get_editor_property(property_name)))
            except Exception as error:
                log('spawner_default {} unavailable={}'.format(property_name, error))

for map_path in ('/Game/LEVEL/WM', '/Game/H/LEVEL/HOUSE'):
    if not unreal.EditorLoadingAndSavingUtils.load_map(map_path):
        log('map={} could_not_load'.format(map_path))
        continue
    world = unreal.EditorLevelLibrary.get_editor_world()
    spawners = [actor for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
                if 'Trash' in actor.get_name() and 'Spawner' in actor.get_name()]
    log('map={} placed_spawners={}'.format(map_path, len(spawners)))
    for actor in spawners:
        log('placed_spawner={} class={} location={}'.format(
            actor.get_name(), actor.get_class(), actor.get_actor_location()))
    trash_counts = {}
    for actor in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor):
        class_name = actor.get_class().get_name()
        if class_name.startswith('BP_Trash'):
            trash_counts[class_name] = trash_counts.get(class_name, 0) + 1
    log('map={} placed_trash={}'.format(map_path, sorted(trash_counts.items())))
