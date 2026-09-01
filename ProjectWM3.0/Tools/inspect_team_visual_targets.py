import unreal


def log(message):
    unreal.log(f"TEAM_VISUALS|{message}")


delivery_class = unreal.load_class(
    None,
    "/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1.BP_DeliveryVehicle_v1_C",
)
if not delivery_class:
    log("DELIVERY_CLASS_MISSING")
else:
    delivery_cdo = unreal.get_default_object(delivery_class)
    log(f"DELIVERY_CLASS|{delivery_cdo.get_class().get_path_name()}")
    for component in delivery_cdo.get_components_by_class(unreal.MeshComponent):
        mesh_path = "None"
        if isinstance(component, unreal.StaticMeshComponent):
            static_mesh = component.get_editor_property("static_mesh")
            mesh_path = static_mesh.get_path_name() if static_mesh else "None"
        materials = []
        for index in range(component.get_num_materials()):
            material = component.get_material(index)
            materials.append(material.get_path_name() if material else "None")
        log(
            "DELIVERY_COMPONENT|"
            f"name={component.get_name()}|class={component.get_class().get_name()}|"
            f"mesh={mesh_path}|materials={materials}"
        )

if not unreal.EditorLoadingAndSavingUtils.load_map("/Game/LEVEL/WM"):
    log("WM_LOAD_FAILED")
else:
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        label = actor.get_actor_label()
        actor_name = actor.get_name()
        include = any(token.lower() in (label + actor_name).lower() for token in ["house", "roof", "hfloor", "levelinstance"])
        if not include:
            continue
        component_descriptions = []
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.get_editor_property("static_mesh")
            material0 = component.get_material(0) if component.get_num_materials() else None
            component_descriptions.append(
                f"{component.get_name()}::mesh={mesh.get_path_name() if mesh else 'None'}::"
                f"mat0={material0.get_path_name() if material0 else 'None'}"
            )
        log(
            "WM_ACTOR|"
            f"label={label}|name={actor_name}|class={actor.get_class().get_name()}|"
            f"loc={actor.get_actor_location()}|components={component_descriptions}"
        )
        try:
            world_asset = actor.get_editor_property("world_asset")
            log(f"LEVEL_INSTANCE_ASSET|label={label}|asset={world_asset.get_path_name() if world_asset else 'None'}")
        except Exception:
            pass

    # 블루프린트를 임시로 스폰하면 Construction Script로 만든 실제 로봇 메시도
    # 확인할 수 있다. 이 액터는 맵을 저장하지 않고 즉시 제거한다.
    if delivery_class:
        spawned = unreal.EditorLevelLibrary.spawn_actor_from_class(
            delivery_class, unreal.Vector(0, 0, -100000), unreal.Rotator(0, 0, 0)
        )
        if spawned:
            for component in spawned.get_components_by_class(unreal.MeshComponent):
                mesh_path = "None"
                if isinstance(component, unreal.StaticMeshComponent):
                    static_mesh = component.get_editor_property("static_mesh")
                    mesh_path = static_mesh.get_path_name() if static_mesh else "None"
                elif isinstance(component, unreal.SkeletalMeshComponent):
                    skeletal_mesh = component.get_editor_property("skeletal_mesh")
                    mesh_path = skeletal_mesh.get_path_name() if skeletal_mesh else "None"
                materials = []
                for index in range(component.get_num_materials()):
                    material = component.get_material(index)
                    materials.append(material.get_path_name() if material else "None")
                log(
                    "DELIVERY_SPAWNED_COMPONENT|"
                    f"name={component.get_name()}|class={component.get_class().get_name()}|"
                    f"mesh={mesh_path}|materials={materials}"
                )
            unreal.EditorLevelLibrary.destroy_actor(spawned)
