import unreal


if not unreal.EditorLoadingAndSavingUtils.load_map('/Game/LEVEL/WM'):
    raise RuntimeError('Could not load WM')

for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    class_name = actor.get_class().get_name()
    if class_name in ('BP_RoadPathStart_C', 'BP_RoadPathEnd_C'):
        unreal.log_warning('WM_TRAFFIC_PLACEMENT class={} label={} loc={} rot={} scale={}'.format(
            class_name, actor.get_actor_label(), actor.get_actor_location(), actor.get_actor_rotation(),
            actor.get_actor_scale3d()))
