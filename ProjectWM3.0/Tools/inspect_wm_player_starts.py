import unreal

world = unreal.EditorLoadingAndSavingUtils.load_map('/Game/LEVEL/WM')
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if actor.get_class().get_name() == 'PlayerStart' or actor.get_name().lower().startswith('playerstart'):
        unreal.log('WM_START name={} label={} loc={} tags={}'.format(
            actor.get_name(), actor.get_actor_label(), actor.get_actor_location(), list(actor.tags)))
