import unreal

game_mode_class = unreal.load_class(None, '/Game/LEVEL/BP_WMGameMode.BP_WMGameMode_C')
game_state_class = unreal.load_class(None, '/Game/LEVEL/BP_WMGameState.BP_WMGameState_C')

if not game_mode_class:
    unreal.log_error('MATCH_END BP_WMGameMode missing')
else:
    game_mode_cdo = unreal.get_default_object(game_mode_class)
    unreal.log('MATCH_END game_mode_class={}'.format(game_mode_class.get_path_name()))
    for name in ['match_duration_seconds', 'game_state_class', 'player_controller_class']:
        try:
            unreal.log('MATCH_END game_mode {}={}'.format(name, game_mode_cdo.get_editor_property(name)))
        except Exception as exc:
            unreal.log_error('MATCH_END game_mode {} failed: {}'.format(name, exc))

if not game_state_class:
    unreal.log_error('MATCH_END BP_WMGameState missing')
else:
    game_state_cdo = unreal.get_default_object(game_state_class)
    unreal.log('MATCH_END game_state_class={}'.format(game_state_class.get_path_name()))
    unreal.log('MATCH_END game_state trash_names={}'.format([name for name in dir(game_state_cdo) if 'trash' in name.lower() or 'house' in name.lower()]))
    for name in ['house1_trash_count', 'house2_trash_count', 'house_1trash_count', 'house_2trash_count']:
        try:
            unreal.log('MATCH_END game_state {}={}'.format(name, game_state_cdo.get_editor_property(name)))
        except Exception as exc:
            unreal.log_warning('MATCH_END game_state {} failed: {}'.format(name, exc))

house_zone_class = unreal.load_class(None, '/Game/Fab/Trash/BP_HouseTrashZone.BP_HouseTrashZone_C')
if not house_zone_class:
    unreal.log_error('MATCH_END BP_HouseTrashZone missing')
else:
    house_zone_cdo = unreal.get_default_object(house_zone_class)
    unreal.log('MATCH_END house_zone names={}'.format([name for name in dir(house_zone_cdo) if 'trash' in name.lower() or 'house' in name.lower()]))

unreal.EditorLoadingAndSavingUtils.load_map('/Game/LEVEL/WM')
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if 'HouseTrashZone' not in actor.get_class().get_name():
        continue
    unreal.log('MATCH_END zone actor={} class={}'.format(actor.get_name(), actor.get_class().get_name()))
    for name in ['house_id', 'current_trash_count', 'houseid', 'currenttrashcount']:
        try:
            unreal.log('MATCH_END zone {}={}'.format(name, actor.get_editor_property(name)))
        except Exception as exc:
            unreal.log_warning('MATCH_END zone {} failed: {}'.format(name, exc))
