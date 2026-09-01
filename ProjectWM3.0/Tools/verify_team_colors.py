import unreal


def log(message):
    unreal.log(f"TEAM_VERIFY|{message}")


expected_materials = [
    "/Game/TeamVisuals/M_Robot_RedMetallic",
    "/Game/TeamVisuals/M_Robot_BlueMetallic",
    "/Game/TeamVisuals/M_Roof_Red",
    "/Game/TeamVisuals/M_Roof_Blue",
]
for path in expected_materials:
    asset = unreal.load_asset(path)
    log(f"MATERIAL|path={path}|exists={bool(asset)}")

expected_roofs = {
    "HOUSE1_RedTeamRoof": "M_Roof_Red",
    "HOUSE2_BlueTeamRoof": "M_Roof_Blue",
}
found = 0
bad = 0
if unreal.EditorLoadingAndSavingUtils.load_map("/Game/LEVEL/WM"):
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        label = actor.get_actor_label()
        expected_material_name = expected_roofs.get(label)
        if not expected_material_name:
            continue
        found += 1
        components = actor.get_components_by_class(unreal.StaticMeshComponent)
        component = components[0] if components else None
        mesh = component.get_editor_property("static_mesh") if component else None
        material = component.get_material(0) if component else None
        actual_name = material.get_name() if material else "None"
        is_ok = mesh and mesh.get_name() == "Hfloor" and actual_name == expected_material_name
        if not is_ok:
            bad += 1
        log(
            f"ROOF|label={label}|ok={is_ok}|mesh={mesh.get_path_name() if mesh else 'None'}|"
            f"material={material.get_path_name() if material else 'None'}|loc={actor.get_actor_location()}"
        )
else:
    bad += 2
    log("WM_LOAD_FAILED")

log(f"SUMMARY|found={found}|bad={bad}|expected={len(expected_roofs)}")
