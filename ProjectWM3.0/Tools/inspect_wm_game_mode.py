import unreal

game_mode_class = unreal.load_class(None, '/Game/LEVEL/BP_WMGameMode.BP_WMGameMode_C')
cdo = unreal.get_default_object(game_mode_class)
for name in ['default_pawn_class', 'player_controller_class', 'player_state_class', 'game_state_class', 'hud_class', 'b_use_seamless_travel']:
    try:
        unreal.log('WM_GM {}={}'.format(name, cdo.get_editor_property(name)))
    except Exception as exc:
        unreal.log_warning('WM_GM {} failed {}'.format(name, exc))

world = unreal.load_asset('/Game/LEVEL/WM')
settings = world.get_world_settings()
unreal.log('WM_MAP default_game_mode={}'.format(settings.get_editor_property('default_game_mode')))
