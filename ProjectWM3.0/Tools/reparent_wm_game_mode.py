import unreal

blueprint = unreal.load_asset('/Game/LEVEL/BP_WMGameMode')
parent_class = unreal.load_class(None, '/Script/ProjectWM.WMGameMode')
unreal.BlueprintEditorLibrary.reparent_blueprint(blueprint, parent_class)
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
klass = unreal.load_class(None, '/Game/LEVEL/BP_WMGameMode.BP_WMGameMode_C')
cdo = unreal.get_default_object(klass)
unreal.log('WM_GM pawn={} controller={}'.format(
    cdo.get_editor_property('default_pawn_class'), cdo.get_editor_property('player_controller_class')))
