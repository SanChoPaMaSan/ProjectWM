import unreal

if not unreal.EditorLoadingAndSavingUtils.load_map('/Game/LEVEL/WM'):
    raise RuntimeError('Could not load WM')

for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    label = actor.get_actor_label()
    class_name = actor.get_class().get_name()
    if 'house' in label.lower() or 'house' in actor.get_name().lower() or 'levelinstance' in class_name.lower():
        unreal.log_warning('WM_HOUSE_REF label={} name={} class={} loc={} rot={}'.format(
            label, actor.get_name(), class_name, actor.get_actor_location(), actor.get_actor_rotation()))
