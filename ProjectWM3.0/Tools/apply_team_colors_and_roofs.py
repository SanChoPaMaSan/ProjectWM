import unreal


TEAM_DEST = "/Game/TeamVisuals"
WM_MAP = "/Game/LEVEL/WM"
ROOF_MESH_PATH = "/Game/H/Hfloor"


def log(message):
    unreal.log(f"TEAM_APPLY|{message}")


def create_or_update_color_material(name, color, metallic, roughness):
    asset_path = f"{TEAM_DEST}/{name}"
    material = unreal.load_asset(asset_path)
    if not material:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            name, TEAM_DEST, unreal.Material, unreal.MaterialFactoryNew()
        )
    if not material:
        raise RuntimeError(f"Could not create {asset_path}")

    unreal.MaterialEditingLibrary.delete_all_material_expressions(material)
    color_node = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant3Vector, -400, -60
    )
    color_node.set_editor_property("constant", unreal.LinearColor(*color, 1.0))
    metallic_node = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant, -400, 40
    )
    metallic_node.set_editor_property("r", metallic)
    roughness_node = unreal.MaterialEditingLibrary.create_material_expression(
        material, unreal.MaterialExpressionConstant, -400, 120
    )
    roughness_node.set_editor_property("r", roughness)

    unreal.MaterialEditingLibrary.connect_material_property(
        color_node, "", unreal.MaterialProperty.MP_BASE_COLOR
    )
    unreal.MaterialEditingLibrary.connect_material_property(
        metallic_node, "", unreal.MaterialProperty.MP_METALLIC
    )
    unreal.MaterialEditingLibrary.connect_material_property(
        roughness_node, "", unreal.MaterialProperty.MP_ROUGHNESS
    )
    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    log(f"MATERIAL_OK|{material.get_path_name()}")
    return material


def get_or_spawn_roof(label, location, rotation, material, roof_mesh):
    actor = None
    for candidate in unreal.EditorLevelLibrary.get_all_level_actors():
        if candidate.get_actor_label() == label:
            actor = candidate
            break

    if not actor:
        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        actor = actor_subsystem.spawn_actor_from_class(
            unreal.StaticMeshActor, location, rotation
        )
        if not actor:
            raise RuntimeError(f"Could not spawn roof overlay {label}")
        static_mesh_component = actor.get_editor_property("static_mesh_component")
        static_mesh_component.set_editor_property("static_mesh", roof_mesh)
        actor.set_actor_label(label)
        log(f"ROOF_CREATED|{label}")
    else:
        actor.set_actor_location(location, False, False)
        actor.set_actor_rotation(rotation, False)
        log(f"ROOF_UPDATED|{label}")

    actor.set_actor_enable_collision(False)
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        component.set_material(0, material)
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)

    return actor


def main():
    unreal.EditorAssetLibrary.make_directory(TEAM_DEST)

    # Robot: bright, metallic team bodies. Roof: saturated but non-metallic.
    red_robot = create_or_update_color_material("M_Robot_RedMetallic", (0.82, 0.015, 0.02), 0.88, 0.20)
    blue_robot = create_or_update_color_material("M_Robot_BlueMetallic", (0.01, 0.12, 0.90), 0.88, 0.20)
    red_roof = create_or_update_color_material("M_Roof_Red", (0.72, 0.018, 0.025), 0.05, 0.38)
    blue_roof = create_or_update_color_material("M_Roof_Blue", (0.015, 0.10, 0.72), 0.05, 0.38)

    roof_mesh = unreal.load_asset(ROOF_MESH_PATH)
    if not roof_mesh:
        raise RuntimeError(f"Missing roof mesh {ROOF_MESH_PATH}")

    if not unreal.EditorLoadingAndSavingUtils.load_map(WM_MAP):
        raise RuntimeError(f"Could not load {WM_MAP}")

    # Hfloor inside the shared HOUSE level: local (210, -1100, -100), yaw 90.
    # HOUSE is at (-2000, 4270), yaw 0; HOUSE2 is at (2000, -4270), yaw 180.
    # Offset Z by 2 cm to prevent z-fighting with the shared roof mesh.
    get_or_spawn_roof(
        "HOUSE1_RedTeamRoof",
        unreal.Vector(-1790.0, 3170.0, -97.9),
        unreal.Rotator(0.0, 90.0, 0.0),
        red_roof,
        roof_mesh,
    )
    get_or_spawn_roof(
        "HOUSE2_BlueTeamRoof",
        unreal.Vector(1790.0, -3170.0, -97.9),
        unreal.Rotator(0.0, 270.0, 0.0),
        blue_roof,
        roof_mesh,
    )

    unreal.EditorLoadingAndSavingUtils.save_map(unreal.EditorLevelLibrary.get_editor_world(), WM_MAP)
    log("DONE|robot_materials=2|roof_materials=2|roof_overlays=2")


if __name__ == "__main__":
    main()
