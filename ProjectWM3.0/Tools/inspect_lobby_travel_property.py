import unreal
klass = unreal.load_class(None, '/Game/LEVEL/BP_LobbyGameMode.BP_LobbyGameMode_C')
cdo = unreal.get_default_object(klass)
unreal.log('LOBBY_TRAVEL_PROPERTIES {}'.format([x for x in dir(cdo) if 'seamless' in x.lower() or 'travel' in x.lower()]))
for name in ['use_seamless_travel', 'b_use_seamless_travel']:
    try:
        unreal.log('LOBBY_TRAVEL {}={}'.format(name, cdo.get_editor_property(name)))
    except Exception as exc:
        unreal.log_warning('LOBBY_TRAVEL {} failed {}'.format(name, exc))
