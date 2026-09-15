import unreal


BASE = '/Game/Fab/Car/BP/'
EXPECTED = {
    'BP_RoadPathStart': '/Script/ProjectWM.TrafficStartActor',
    'BP_RoadPathEnd': '/Script/ProjectWM.TrafficEndActor',
}
EXPECTED.update({'BP_Car{}'.format(index): '/Script/ProjectWM.TrafficCarActor' for index in range(1, 8)})

for name, parent_path in EXPECTED.items():
    path = BASE + name
    bp = unreal.load_asset(path)
    parent = unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp) if bp else None
    actual = parent.get_path_name() if parent else None
    if actual != parent_path:
        raise RuntimeError('{} parent {} != {}'.format(name, actual, parent_path))
    generated = unreal.load_class(None, path + '.' + name + '_C')
    cdo = unreal.get_default_object(generated)
    if name.startswith('BP_Car'):
        components = cdo.get_components_by_class(unreal.StaticMeshComponent)
        component = components[0] if components else None
        if not component or not component.get_editor_property('static_mesh'):
            raise RuntimeError('{} has no configured mesh'.format(name))
    if name == 'BP_RoadPathStart':
        classes = cdo.get_editor_property('car_classes')
        if len(classes) != 7:
            raise RuntimeError('StartBP car class count {}'.format(len(classes)))
        if cdo.get_editor_property('min_spawn_interval') != 5.0 or cdo.get_editor_property('max_spawn_interval') != 10.0:
            raise RuntimeError('StartBP interval is not 5-10')
    unreal.log_warning('CAR_TRAFFIC_VERIFY {} ok'.format(name))
