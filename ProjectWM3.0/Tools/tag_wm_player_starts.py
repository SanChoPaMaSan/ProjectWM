import unreal

unreal.EditorLoadingAndSavingUtils.load_map('/Game/LEVEL/WM')
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    label = actor.get_actor_label()
    if label == 'Player1Start':
        actor.set_editor_property('player_start_tag', 'HOUSE1')
        unreal.log('WM_START_TAG {}=HOUSE1'.format(actor.get_name()))
    elif label == 'Player2Start':
        actor.set_editor_property('player_start_tag', 'HOUSE2')
        unreal.log('WM_START_TAG {}=HOUSE2'.format(actor.get_name()))

unreal.EditorLoadingAndSavingUtils.save_map(unreal.EditorLevelLibrary.get_editor_world(), '/Game/LEVEL/WM')
