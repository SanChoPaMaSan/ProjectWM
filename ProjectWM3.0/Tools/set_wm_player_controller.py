import unreal

blueprint = unreal.load_asset('/Game/LEVEL/BP_WMGameMode')
klass = unreal.load_class(None, '/Game/LEVEL/BP_WMGameMode.BP_WMGameMode_C')
cdo = unreal.get_default_object(klass)
controller_class = unreal.load_class(None, '/Script/ProjectWM.LobbyPlayerController')
cdo.set_editor_property('player_controller_class', controller_class)
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
unreal.log('WM_GM player_controller_class={}'.format(cdo.get_editor_property('player_controller_class')))
