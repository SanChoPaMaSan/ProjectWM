import unreal

widget_blueprint = unreal.load_asset('/Game/UI/WBP_LobbyMenu')
controller_class = unreal.load_class(None, '/Script/ProjectWM.LobbyMenuWidget')

if not widget_blueprint:
    raise RuntimeError('WBP_LobbyMenu was not found')
if not controller_class:
    raise RuntimeError('ULobbyMenuWidget class was not found')

unreal.BlueprintEditorLibrary.reparent_blueprint(widget_blueprint, controller_class)
unreal.BlueprintEditorLibrary.compile_blueprint(widget_blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(widget_blueprint)

unreal.log('LOBBY_CONNECT parent={}'.format(unreal.BlueprintEditorLibrary.get_blueprint_parent_class(widget_blueprint)))
