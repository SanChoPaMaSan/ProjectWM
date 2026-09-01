import os
import re

import unreal


SOURCE_ROOT = r"C:\Users\admin\Downloads\블랜더_텍스처"
TEXTURE_DEST = "/Game/H/LH_Applied/Textures"
MATERIAL_DEST = "/Game/H/LH_Applied/Materials"


# LastH.blend에서 실제로 참조하는 이미지 파일만 나열한다.
USED_IMAGE_FILES = [
    "Fabric048_2K-JPG_Color.jpg",
    "Leather034A_2K-JPG_Color.jpg",
    "Marble012_2K-JPG_Color.jpg",
    "Metal029_2K-JPG_Color.jpg",
    "Metal061B_2K-JPG_Color.jpg",
    "Metal063_2K-JPG_Roughness.jpg",
    "Plaster001_2K-PNG_Color.png",
    "Plastic010_2K-JPG_Color.jpg",
    "Porcelain002_2K-JPG_Color.jpg",
    "RoofingTiles012A_2K-JPG_Color.jpg",
    "Texturelabs_Brick_151S.jpg",
    "Tiles027_2K-JPG_Displacement.jpg",
    "Wood017_2K-JPG_Color.jpg",
    "Wood021_2K-JPG_Color.jpg",
    "Wood030_2K-JPG_Color.jpg",
    "Wood048_2K-JPG_Color.jpg",
    "Wood056_2K-JPG_Color.jpg",
    "Wood058_2K-JPG_Color.jpg",
    "Wood067_2K-JPG_Color.jpg",
    "WoodFloor013_2K-JPG_Color.jpg",
    "WoodFloor051_2K-JPG_Color.jpg",
]


# Blender material -> 이미지 파일. 한 이미지가 여러 재질에서 재사용된다.
MATERIAL_IMAGES = {
    "Aircon2_color": "Plastic010_2K-JPG_Color.jpg",
    "Aircon_color": "Plastic010_2K-JPG_Color.jpg",
    "Aircon_inside": "Metal029_2K-JPG_Color.jpg",
    "bath_color": "Porcelain002_2K-JPG_Color.jpg",
    "bed_wood_color": "Wood048_2K-JPG_Color.jpg",
    "Boxbox_color": "Wood048_2K-JPG_Color.jpg",
    "case4_color": "Wood017_2K-JPG_Color.jpg",
    "case_wood": "Wood048_2K-JPG_Color.jpg",
    "chair_color": "Wood030_2K-JPG_Color.jpg",
    "clothbox6_knob": "Metal029_2K-JPG_Color.jpg",
    "clothbox_color": "Wood056_2K-JPG_Color.jpg",
    "door_inside_color.001": "Wood058_2K-JPG_Color.jpg",
    "door_outside_color": "Wood067_2K-JPG_Color.jpg",
    "doorcase_inside_color": "WoodFloor013_2K-JPG_Color.jpg",
    "doorcase_inside_color.001": "Wood021_2K-JPG_Color.jpg",
    "floor_inside": "WoodFloor051_2K-JPG_Color.jpg",
    "inside_dark": "Metal063_2K-JPG_Roughness.jpg",
    "Material.002": "Metal061B_2K-JPG_Color.jpg",
    "Material.004": "Wood067_2K-JPG_Color.jpg",
    "Material.005": "Fabric048_2K-JPG_Color.jpg",
    "Material.007": "Fabric048_2K-JPG_Color.jpg",
    "Material.008": "Wood067_2K-JPG_Color.jpg",
    "Material.009": "Plaster001_2K-PNG_Color.png",
    "Material.010": "Wood067_2K-JPG_Color.jpg",
    "Material.011": "Fabric048_2K-JPG_Color.jpg",
    "Material.015": "Metal029_2K-JPG_Color.jpg",
    "Material.016": "Plastic010_2K-JPG_Color.jpg",
    "roof": "RoofingTiles012A_2K-JPG_Color.jpg",
    "sink_color": "Marble012_2K-JPG_Color.jpg",
    "sofa_color": "Leather034A_2K-JPG_Color.jpg",
    "toilet_metal": "Metal061B_2K-JPG_Color.jpg",
    "toilet_tile_1": "Tiles027_2K-JPG_Displacement.jpg",
    "toilet_tile_2": "Texturelabs_Brick_151S.jpg",
    "tv_color.001": "Metal029_2K-JPG_Color.jpg",
    "wall_outside.002": "Plaster001_2K-PNG_Color.png",
}


# 기존 /Game/H 메시들은 대부분 재질 슬롯이 하나뿐이다. 새 Blender 모델의
# 첫 번째(주 재질) 슬롯을 기존 메시의 슬롯 0에 대응시킨다.
MESH_MATERIALS = {
    "Aircon": "Aircon_color",
    "Aircon2": "Aircon2_color",
    "Bath": "bath_color",
    "Bed1": "bed_wood_color",
    "Bed2": "Material.008",
    "Bed3": "Material.010",
    "Brymachine": "Material.009",
    "Case1": "Material.004",
    "Case2": "case_wood",
    "Case3": "door_outside_color",
    "Case4": "case4_color",
    "Hfloor": "roof",
    "Hightplane": "wall_outside.002",
    "ShoesBox1": "clothbox_color",
    "ShoesBox2": "chair_color",
    "ShoesBox3": "door_outside_color",
    "Shoescase": "case_wood",
    "Sink": "sink_color",
    "Sink2": "sink_color",
    "Sink2_001": "sink_color",
    "Sofa": "sofa_color",
    "Stand1": "doorcase_inside_color",
    "Table": "case_wood",
    "Table2": "Material.016",
    "Table3": "case_wood",
    "Table4": "case_wood",
    "TV1": "tv_color.001",
    "TV2": "tv_color.001",
    "TV3": "tv_color.001",
}

for index in range(1, 6):
    MESH_MATERIALS[f"Boxbox{index}"] = "Boxbox_color"
for index in range(1, 8):
    MESH_MATERIALS[f"Chair{index}"] = "chair_color"
for index in range(1, 7):
    MESH_MATERIALS[f"Clothbox{index}"] = "clothbox_color"
for index in range(2, 10):
    MESH_MATERIALS[f"Door{index}"] = (
        "door_outside_color" if index == 2 else "door_inside_color.001"
    )
for index in range(1, 10):
    MESH_MATERIALS[f"Doorcase{index}"] = (
        "Aircon_color" if index == 2 else "doorcase_inside_color.001"
    )
for index in range(1, 3):
    MESH_MATERIALS[f"Icebox{index}"] = "Aircon_color"


NON_COLOR_IMAGES = {
    "Metal063_2K-JPG_Roughness.jpg",
    "Tiles027_2K-JPG_Displacement.jpg",
}


def log(message):
    unreal.log(f"LH_APPLY|{message}")


def safe_name(value):
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def asset_name_for_image(filename):
    return "T_LH_" + safe_name(os.path.splitext(filename)[0])


def material_asset_name(source_material_name):
    return "M_LH_" + safe_name(source_material_name)


def find_source_images():
    wanted = set(USED_IMAGE_FILES)
    matches = {filename: [] for filename in USED_IMAGE_FILES}
    for root, _, files in os.walk(SOURCE_ROOT):
        for filename in files:
            if filename in wanted:
                matches[filename].append(os.path.join(root, filename))

    resolved = {}
    for filename, paths in matches.items():
        if len(paths) == 1:
            resolved[filename] = paths[0]
        elif len(paths) == 0:
            log(f"SOURCE_MISSING|{filename}")
        else:
            paths.sort(key=lambda path: (len(path), path.lower()))
            resolved[filename] = paths[0]
            log(f"SOURCE_DUPLICATE|{filename}|using={paths[0]}|count={len(paths)}")
    return resolved


def import_textures(source_images):
    unreal.EditorAssetLibrary.make_directory(TEXTURE_DEST)
    tasks = []
    filename_by_task = {}
    for filename, source_path in source_images.items():
        task = unreal.AssetImportTask()
        task.filename = source_path
        task.destination_path = TEXTURE_DEST
        task.destination_name = asset_name_for_image(filename)
        task.automated = True
        task.replace_existing = True
        task.save = True
        tasks.append(task)
        filename_by_task[id(task)] = filename

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

    imported = {}
    for task in tasks:
        filename = filename_by_task[id(task)]
        expected_path = f"{TEXTURE_DEST}/{asset_name_for_image(filename)}"
        texture = unreal.load_asset(expected_path)
        if not texture:
            log(f"TEXTURE_IMPORT_FAILED|{filename}|expected={expected_path}")
            continue
        if filename in NON_COLOR_IMAGES:
            texture.set_editor_property("srgb", False)
            try:
                texture.set_editor_property(
                    "compression_settings", unreal.TextureCompressionSettings.TC_MASKS
                )
            except Exception as exc:
                log(f"TEXTURE_COMPRESSION_WARNING|{filename}|{exc}")
            unreal.EditorAssetLibrary.save_loaded_asset(texture)
        imported[filename] = texture
        log(f"TEXTURE_OK|{filename}|{texture.get_path_name()}")
    return imported


def get_or_create_material(source_material_name):
    asset_name = material_asset_name(source_material_name)
    asset_path = f"{MATERIAL_DEST}/{asset_name}"
    material = unreal.load_asset(asset_path)
    if material:
        return material
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name,
        MATERIAL_DEST,
        unreal.Material,
        unreal.MaterialFactoryNew(),
    )


def rebuild_material(source_material_name, texture):
    material = get_or_create_material(source_material_name)
    if not material:
        log(f"MATERIAL_CREATE_FAILED|{source_material_name}")
        return None

    unreal.MaterialEditingLibrary.delete_all_material_expressions(material)

    if source_material_name == "inside_dark":
        dark_color = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionConstant3Vector, -360, -80
        )
        dark_color.set_editor_property("constant", unreal.LinearColor(0.03, 0.03, 0.03, 1.0))
        unreal.MaterialEditingLibrary.connect_material_property(
            dark_color, "", unreal.MaterialProperty.MP_BASE_COLOR
        )
        roughness_sample = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionTextureSample, -360, 80
        )
        roughness_sample.set_editor_property("texture", texture)
        unreal.MaterialEditingLibrary.connect_material_property(
            roughness_sample, "R", unreal.MaterialProperty.MP_ROUGHNESS
        )
    else:
        texture_sample = unreal.MaterialEditingLibrary.create_material_expression(
            material, unreal.MaterialExpressionTextureSample, -300, 0
        )
        texture_sample.set_editor_property("texture", texture)
        unreal.MaterialEditingLibrary.connect_material_property(
            texture_sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR
        )

    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    log(f"MATERIAL_OK|{source_material_name}|{material.get_path_name()}")
    return material


def build_materials(imported_textures):
    unreal.EditorAssetLibrary.make_directory(MATERIAL_DEST)
    materials = {}
    for source_material_name, filename in MATERIAL_IMAGES.items():
        texture = imported_textures.get(filename)
        if not texture:
            log(f"MATERIAL_SKIPPED_NO_TEXTURE|{source_material_name}|{filename}")
            continue
        try:
            material = rebuild_material(source_material_name, texture)
        except Exception as exc:
            log(f"MATERIAL_FAILED|{source_material_name}|{type(exc).__name__}|{exc}")
            continue
        if material:
            materials[source_material_name] = material
    return materials


def apply_materials(materials):
    applied = 0
    failed = 0
    for mesh_name, source_material_name in sorted(MESH_MATERIALS.items()):
        mesh_path = f"/Game/H/{mesh_name}"
        mesh = unreal.load_asset(mesh_path)
        material = materials.get(source_material_name)
        if not mesh:
            failed += 1
            log(f"MESH_MISSING|{mesh_name}|{mesh_path}")
            continue
        if not isinstance(mesh, unreal.StaticMesh):
            failed += 1
            log(f"MESH_WRONG_TYPE|{mesh_name}|{mesh.get_class().get_name()}")
            continue
        if not material:
            failed += 1
            log(f"MESH_NO_MATERIAL|{mesh_name}|{source_material_name}")
            continue

        try:
            mesh.set_material(0, material)
            unreal.EditorAssetLibrary.save_loaded_asset(mesh)
            applied += 1
            log(f"MESH_OK|{mesh_name}|slot0={material.get_path_name()}")
        except Exception as exc:
            failed += 1
            log(f"MESH_FAILED|{mesh_name}|{type(exc).__name__}|{exc}")

    log(f"MESH_SUMMARY|applied={applied}|failed={failed}|expected={len(MESH_MATERIALS)}")
    return applied, failed


def main():
    log(f"START|source={SOURCE_ROOT}")
    source_images = find_source_images()
    log(f"SOURCE_SUMMARY|found={len(source_images)}|expected={len(USED_IMAGE_FILES)}")

    # Texturelabs_Brick_151S는 현재 제공 폴더에 없지만, 기존 HOUSE 메시 중 이
    # 재질을 받을 대상은 없으므로 나머지 적용은 안전하게 계속한다.
    imported_textures = import_textures(source_images)
    materials = build_materials(imported_textures)
    applied, failed = apply_materials(materials)

    log(
        "DONE|"
        f"textures={len(imported_textures)}|materials={len(materials)}|"
        f"meshes={applied}|failed={failed}"
    )


if __name__ == "__main__":
    main()
