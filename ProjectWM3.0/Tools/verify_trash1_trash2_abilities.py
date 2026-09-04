import unreal

EXPECTED = {
    '/Game/Fab/Trash/T/BP_Trash1': '/Script/ProjectWM.TrashKnockbackActor',
    '/Game/Fab/Trash/T/BP_Trash2': '/Script/ProjectWM.TrashSlowZoneActor',
    '/Game/Fab/Trash/T/BP_Trash3': '/Script/Engine.Actor',
    '/Game/Fab/Trash/T/BP_Trash4': '/Script/ProjectWM.StunTrashActor',
}

for path, expected_parent in EXPECTED.items():
    blueprint = unreal.load_asset(path)
    parent = unreal.BlueprintEditorLibrary.get_blueprint_parent_class(blueprint) if blueprint else None
    actual = parent.get_path_name() if parent else 'None'
    ok = actual == expected_parent
    unreal.log_warning('TRASH_ABILITY_VERIFY|asset={}|ok={}|parent={}'.format(blueprint.get_name() if blueprint else path, ok, actual))
    if not ok:
        raise RuntimeError('Unexpected parent for {}'.format(path))
