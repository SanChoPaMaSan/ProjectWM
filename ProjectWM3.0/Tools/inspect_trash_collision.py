import unreal

PATHS = [
    '/Game/Fab/Trash/T/BP_Trash1',
    '/Game/Fab/Trash/T/BP_Trash2',
    '/Game/Fab/Trash/T/BP_Trash3',
    '/Game/Fab/Trash/T/BP_Trash4',
]

for path in PATHS:
    bp = unreal.load_asset(path)
    generated = unreal.load_class(None, '{}.{}_C'.format(path, bp.get_name())) if bp else None
    cdo = unreal.get_default_object(generated) if generated else None
    if not cdo:
        unreal.log_error('TRASH_COLLISION missing {}'.format(path))
        continue
    for component in cdo.get_components_by_class(unreal.PrimitiveComponent):
        unreal.log_warning(
            'TRASH_COLLISION|asset={}|component={}|profile={}|object_type={}|collision={}'.format(
                bp.get_name(), component.get_name(), component.get_collision_profile_name(),
                component.get_collision_object_type(), component.get_collision_enabled()
            )
        )
