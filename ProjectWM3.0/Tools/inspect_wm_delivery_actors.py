import unreal

unreal.EditorLoadingAndSavingUtils.load_map('/Game/LEVEL/WM')
for actor in unreal.EditorLevelLibrary.get_all_level_actors():
    if 'DeliveryVehicle' in actor.get_class().get_name() or 'DeliveryVehicle' in actor.get_name():
        unreal.log('WM_DELIVERY_ACTOR name={} label={} loc={}'.format(
            actor.get_name(), actor.get_actor_label(), actor.get_actor_location()))
