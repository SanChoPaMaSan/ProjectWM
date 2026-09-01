import unreal

unreal.log('LOBBY_API BlueprintEditorLibrary={}'.format([x for x in dir(unreal.BlueprintEditorLibrary) if 'graph' in x.lower() or 'node' in x.lower() or 'compile' in x.lower() or 'variable' in x.lower()]))
unreal.log('LOBBY_API EditorAssetLibrary={}'.format([x for x in dir(unreal.EditorAssetLibrary) if 'save' in x.lower()]))

for asset_path in [
    '/Game/LEVEL/BP_LobbyGameMode',
    '/Game/LEVEL/BP_LobbyUIController',
    '/Game/LEVEL/BP_LobbyPlayerController',
    '/Game/UI/WBP_LobbyMenu',
    '/Game/LEVEL/LV_Lobby',
]:
    asset = unreal.load_asset(asset_path)
    unreal.log('LOBBY_INSPECT asset={} class={}'.format(asset_path, asset.get_class().get_name() if asset else 'MISSING'))
    if asset:
        unreal.log('LOBBY_DIR {} {}'.format(asset_path, [x for x in dir(asset) if 'graph' in x.lower() or 'widget' in x.lower() or 'tree' in x.lower()]))
        try:
            unreal.log('LOBBY_GRAPHS {} {}'.format(asset_path, unreal.BlueprintEditorLibrary.list_graph_names(asset)))
        except Exception as exc:
            unreal.log_warning('LOBBY_GRAPHS_FAIL {} {}'.format(asset_path, exc))
        try:
            generated_class = unreal.load_class(None, asset_path + '.' + asset.get_name() + '_C')
            cdo = unreal.get_default_object(generated_class)
            unreal.log('LOBBY_INSPECT cdo={}'.format(cdo.get_path_name()))
            for prop in ['player_controller_class', 'default_pawn_class', 'game_state_class', 'b_use_seamless_travel']:
                try:
                    unreal.log('LOBBY_INSPECT {}={}'.format(prop, cdo.get_editor_property(prop)))
                except Exception:
                    pass
        except Exception as exc:
            unreal.log_warning('LOBBY_INSPECT no_cdo {}: {}'.format(asset_path, exc))

widget = unreal.load_object(None, '/Game/UI/WBP_LobbyMenu.WBP_LobbyMenu:WidgetTree.StartButton')
if widget:
    unreal.log('LOBBY_INSPECT StartButton enabled={}'.format(widget.get_editor_property('is_enabled')))
else:
    unreal.log_warning('LOBBY_INSPECT StartButton MISSING')

for path in ['/Game/UI/WBP_LobbyMenu', '/Game/LEVEL/BP_LobbyUIController', '/Game/LEVEL/BP_LobbyGameMode']:
    bp = unreal.load_asset(path)
    try:
        graph = unreal.BlueprintEditorLibrary.find_event_graph(bp)
        unreal.log('LOBBY_GRAPH_API {} {}'.format(path, [x for x in dir(graph) if 'node' in x.lower() or 'remove' in x.lower() or 'select' in x.lower()]))
        nodes = graph.get_editor_property('nodes')
        unreal.log('LOBBY_NODES {} count={}'.format(path, len(nodes)))
        for node in nodes:
            unreal.log('LOBBY_NODE {} {} {}'.format(path, node.get_name(), unreal.BlueprintEditorLibrary.get_node_title(node)))
    except Exception as exc:
        unreal.log_warning('LOBBY_NODES_FAIL {} {}'.format(path, exc))
