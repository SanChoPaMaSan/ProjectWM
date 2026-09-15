import unreal

BASE = '/Game/Fab/Car/BP/'

for index in range(1, 8):
    path = BASE + 'BP_Car{}'.format(index)
    bp = unreal.load_asset(path)
    cls = unreal.load_class(None, path + '.BP_Car{}_C'.format(index))
    cdo = unreal.get_default_object(cls) if cls else None
    if not cdo:
        raise RuntimeError('Missing CDO {}'.format(path))

    entries = []
    for component in cdo.get_components_by_class(unreal.StaticMeshComponent):
        mesh = component.get_editor_property('static_mesh')
        entries.append('component={} mesh={} rel_loc={} rel_rot={} rel_scale={}'.format(
            component.get_name(),
            mesh.get_path_name() if mesh else 'None',
            component.get_editor_property('relative_location'),
            component.get_editor_property('relative_rotation'),
            component.get_editor_property('relative_scale3d')))
        if mesh:
            bounds = mesh.get_bounds()
            entries.append('bounds_origin={} bounds_extent={}'.format(bounds.origin, bounds.box_extent))
    unreal.log_warning('TRAFFIC_CAR_TRANSFORM BP_Car{} {}'.format(index, ' | '.join(entries)))
