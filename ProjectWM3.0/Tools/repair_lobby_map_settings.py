import unreal

game_mode_class = unreal.load_class(None, '/Game/LEVEL/BP_LobbyGameMode.BP_LobbyGameMode_C')
world = unreal.load_asset('/Game/LEVEL/LV_Lobby')

if not game_mode_class:
    raise RuntimeError('BP_LobbyGameMode_C was not found')
if not world:
    raise RuntimeError('LV_Lobby was not found')

world_settings = world.get_world_settings()
world_settings.set_editor_property('default_game_mode', game_mode_class)
unreal.EditorAssetLibrary.save_loaded_asset(world)
unreal.log('LOBBY_REPAIR LV_Lobby default_game_mode={}'.format(world_settings.get_editor_property('default_game_mode')))

for path in [
    '/Game/LEVEL/BP_LobbyGameMode',
    '/Game/LEVEL/BP_LobbyUIController',
    '/Game/UI/WBP_LobbyMenu',
]:
    blueprint = unreal.load_asset(path)
    if not blueprint:
        raise RuntimeError('Missing {}'.format(path))
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
    unreal.log('LOBBY_REPAIR compiled {}'.format(path))
