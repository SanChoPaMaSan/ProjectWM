import unreal

checks = [
    ('DELIVERY', '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1.BP_DeliveryVehicle_v1_C', ['playerindex', 'player_index']),
    ('HUD', '/Game/UI/WBP_RobotHUD.WBP_RobotHUD_C', ['teamindex', 'team_index']),
    ('GAMESTATE', '/Game/LEVEL/BP_WMGameState.BP_WMGameState_C', ['house1trashcount', 'house2trashcount', 'house1_trash_count', 'house2_trash_count']),
]

for label, path, properties in checks:
    klass = unreal.load_class(None, path)
    if not klass:
        unreal.log_error('TEAM_SCORE {} class missing {}'.format(label, path))
        continue
    cdo = unreal.get_default_object(klass)
    unreal.log('TEAM_SCORE {} class={}'.format(label, klass.get_path_name()))
    for name in properties:
        try:
            unreal.log('TEAM_SCORE {} {}={}'.format(label, name, cdo.get_editor_property(name)))
        except Exception as exc:
            unreal.log_warning('TEAM_SCORE {} {} failed {}'.format(label, name, exc))
