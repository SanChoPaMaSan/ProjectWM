import unreal

TARGETS = [
    ('/Game/Fab/Trash/T/BP_Trash1', '/Script/ProjectWM.TrashKnockbackActor'),
    ('/Game/Fab/Trash/T/BP_Trash2', '/Script/ProjectWM.TrashSlowZoneActor'),
]

for blueprint_path, parent_path in TARGETS:
    blueprint = unreal.load_asset(blueprint_path)
    parent_class = unreal.load_class(None, parent_path)
    if not blueprint or not parent_class:
        raise RuntimeError('Could not load {} or {}'.format(blueprint_path, parent_path))

    if unreal.BlueprintEditorLibrary.get_blueprint_parent_class(blueprint) != parent_class:
        unreal.BlueprintEditorLibrary.reparent_blueprint(blueprint, parent_class)

    if blueprint_path.endswith('BP_Trash2'):
        component = unreal.load_object(None, blueprint_path + '.BP_Trash2_C:trash_1_GEN_VARIABLE')
        if component:
            component.set_notify_rigid_body_collision(True)
        else:
            unreal.log_warning('TRASH2_ABILITY could not find mesh component to enable hit events')

    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    if not unreal.EditorAssetLibrary.save_loaded_asset(blueprint):
        raise RuntimeError('Could not save {}'.format(blueprint_path))
    unreal.log_warning('TRASH_ABILITY parent {} -> {}'.format(
        blueprint.get_name(), unreal.BlueprintEditorLibrary.get_blueprint_parent_class(blueprint).get_path_name()))
