import unreal

blueprint = unreal.load_asset('/Game/LEVEL/BP_LobbyGameMode')
klass = unreal.load_class(None, '/Game/LEVEL/BP_LobbyGameMode.BP_LobbyGameMode_C')
cdo = unreal.get_default_object(klass)
cdo.set_editor_property('use_seamless_travel', False)
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
unreal.log('LOBBY_TRAVEL use_seamless_travel={}'.format(cdo.get_editor_property('use_seamless_travel')))
