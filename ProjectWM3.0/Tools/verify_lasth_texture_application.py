import unreal


EXPECTED = {
    "Aircon": "M_LH_Aircon_color",
    "Aircon2": "M_LH_Aircon2_color",
    "Bath": "M_LH_bath_color",
    "Bed1": "M_LH_bed_wood_color",
    "Bed2": "M_LH_Material_008",
    "Bed3": "M_LH_Material_010",
    "Brymachine": "M_LH_Material_009",
    "Case1": "M_LH_Material_004",
    "Case2": "M_LH_case_wood",
    "Case3": "M_LH_door_outside_color",
    "Case4": "M_LH_case4_color",
    "Hfloor": "M_LH_roof",
    "Hightplane": "M_LH_wall_outside_002",
    "ShoesBox1": "M_LH_clothbox_color",
    "ShoesBox2": "M_LH_chair_color",
    "ShoesBox3": "M_LH_door_outside_color",
    "Shoescase": "M_LH_case_wood",
    "Sink": "M_LH_sink_color",
    "Sink2": "M_LH_sink_color",
    "Sink2_001": "M_LH_sink_color",
    "Sofa": "M_LH_sofa_color",
    "Stand1": "M_LH_doorcase_inside_color",
    "Table": "M_LH_case_wood",
    "Table2": "M_LH_Material_016",
    "Table3": "M_LH_case_wood",
    "Table4": "M_LH_case_wood",
    "TV1": "M_LH_tv_color_001",
    "TV2": "M_LH_tv_color_001",
    "TV3": "M_LH_tv_color_001",
}
for index in range(1, 6):
    EXPECTED[f"Boxbox{index}"] = "M_LH_Boxbox_color"
for index in range(1, 8):
    EXPECTED[f"Chair{index}"] = "M_LH_chair_color"
for index in range(1, 7):
    EXPECTED[f"Clothbox{index}"] = "M_LH_clothbox_color"
for index in range(2, 10):
    EXPECTED[f"Door{index}"] = (
        "M_LH_door_outside_color" if index == 2 else "M_LH_door_inside_color_001"
    )
for index in range(1, 10):
    EXPECTED[f"Doorcase{index}"] = (
        "M_LH_Aircon_color" if index == 2 else "M_LH_doorcase_inside_color_001"
    )
for index in range(1, 3):
    EXPECTED[f"Icebox{index}"] = "M_LH_Aircon_color"


def log(message):
    unreal.log(f"LH_VERIFY|{message}")


ok = 0
bad = 0
for mesh_name, expected_material_name in sorted(EXPECTED.items()):
    mesh = unreal.load_asset(f"/Game/H/{mesh_name}")
    if not mesh:
        bad += 1
        log(f"MISSING_MESH|{mesh_name}")
        continue
    materials = mesh.get_editor_property("static_materials")
    actual = None
    if materials:
        actual_interface = materials[0].get_editor_property("material_interface")
        if actual_interface:
            actual = actual_interface.get_name()
    if actual == expected_material_name:
        ok += 1
    else:
        bad += 1
        log(f"MISMATCH|{mesh_name}|expected={expected_material_name}|actual={actual}")

log(f"SUMMARY|ok={ok}|bad={bad}|expected={len(EXPECTED)}")
