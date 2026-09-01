import unreal

blueprint = unreal.load_asset('/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1')
klass = unreal.load_class(None, '/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1.BP_DeliveryVehicle_v1_C')
cdo = unreal.get_default_object(klass)
cdo.set_editor_property('spawn_collision_handling_method', unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN)
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
unreal.log('DELIVERY_SPAWN collision_policy={}'.format(cdo.get_editor_property('spawn_collision_handling_method')))
