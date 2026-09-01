import unreal

blueprint = unreal.load_asset('/Game/LEVEL/BP_LobbyGameMode')
controller_class = unreal.load_class(None, '/Script/ProjectWM.LobbyPlayerController')

if not blueprint:
    raise RuntimeError('BP_LobbyGameMode was not found')
if not controller_class:
    raise RuntimeError('ALobbyPlayerController was not found')

generated_class = unreal.load_class(None, '/Game/LEVEL/BP_LobbyGameMode.BP_LobbyGameMode_C')
game_mode_cdo = unreal.get_default_object(generated_class)
game_mode_cdo.set_editor_property('player_controller_class', controller_class)

unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
unreal.log('LOBBY_PC_SET {}'.format(game_mode_cdo.get_editor_property('player_controller_class')))
