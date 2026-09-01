import unreal


def log(message):
    unreal.log(f"DELIVERY_VISUAL|{message}")


paths = [
    "/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/BP_DeliveryVehicle_v1.BP_DeliveryVehicle_v1_C",
    "/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/Cylinder.Cylinder_C",
    "/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/Cylinder_001.Cylinder_001_C",
    "/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/Cylinder_007.Cylinder_007_C",
]

asset_paths = [
    "/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/Cylinder",
    "/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/Cylinder_001",
    "/Game/BendylabStudios/BLS_DeliveryRobot_v1/Blueprint/Cylinder_007",
    "/Game/BendylabStudios/BLS_DeliveryRobot_v1/Mesh/SM_Delivery_Robot_v1",
    "/Game/BendylabStudios/BLS_DeliveryRobot_v1/Mesh/SM_DeliveryRobot_v1",
]
for asset_path in asset_paths:
    asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
    loaded = unreal.load_asset(asset_path)
    log(
        f"ASSET|path={asset_path}|class={asset_data.asset_class_path}|"
        f"loaded_class={loaded.get_class().get_name() if loaded else 'None'}"
    )

for path in paths:
    actor_class = unreal.load_class(None, path)
    if not actor_class:
        log(f"CLASS_MISSING|{path}")
        continue
    cdo = unreal.get_default_object(actor_class)
    log(f"CLASS|{path}|cdo={cdo.get_name()}")
    for component in cdo.get_components_by_class(unreal.SceneComponent):
        mesh_path = "None"
        if isinstance(component, unreal.StaticMeshComponent):
            static_mesh = component.get_editor_property("static_mesh")
            mesh_path = static_mesh.get_path_name() if static_mesh else "None"
        elif isinstance(component, unreal.SkeletalMeshComponent):
            skeletal_mesh = component.get_editor_property("skeletal_mesh")
            mesh_path = skeletal_mesh.get_path_name() if skeletal_mesh else "None"
        materials = []
        if isinstance(component, unreal.MeshComponent):
            for index in range(component.get_num_materials()):
                material = component.get_material(index)
                materials.append(material.get_path_name() if material else "None")
        child_class = "None"
        if isinstance(component, unreal.ChildActorComponent):
            child = component.get_editor_property("child_actor_class")
            child_class = child.get_path_name() if child else "None"
        log(
            "COMPONENT|"
            f"owner={path.rsplit('.', 1)[0]}|name={component.get_name()}|"
            f"class={component.get_class().get_name()}|mesh={mesh_path}|"
            f"materials={materials}|child={child_class}"
        )
