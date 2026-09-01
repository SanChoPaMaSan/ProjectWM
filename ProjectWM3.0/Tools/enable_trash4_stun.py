import unreal

targets = [
    ('/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1', '/Script/ProjectWM.StunDeliveryVehicle'),
    ('/Game/Fab/Trash/T/BP_Trash4', '/Script/ProjectWM.StunTrashActor'),
]

for blueprint_path, parent_path in targets:
    blueprint = unreal.load_asset(blueprint_path)
    parent_class = unreal.load_class(None, parent_path)
    if not blueprint or not parent_class:
        raise RuntimeError('Could not load {} or {}'.format(blueprint_path, parent_path))

    current_parent = unreal.BlueprintEditorLibrary.get_blueprint_parent_class(blueprint)
    if current_parent != parent_class:
        unreal.BlueprintEditorLibrary.reparent_blueprint(blueprint, parent_class)
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
    unreal.log_warning('TRASH4_STUN parent {} -> {}'.format(
        blueprint_path, unreal.BlueprintEditorLibrary.get_blueprint_parent_class(blueprint).get_path_name()))
