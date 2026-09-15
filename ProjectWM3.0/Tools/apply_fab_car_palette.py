import unreal


CAR_PATH = '/Game/Fab/Car'
TEXTURE_PATH = CAR_PATH + '/Textures/T_Car_Color'
MATERIAL_NAME = 'M_Car_Palette'
CAR_MESHES = (
    'SM_ClassicCar',
    'SM_HatchbackCar',
    'SM_MonsterTruck',
    'SM_Van',
    'SM_MuscleCar',
    'SM_Pickup',
    'SM_SportCar',
)


texture = unreal.load_asset(TEXTURE_PATH)
if not isinstance(texture, unreal.Texture2D):
    raise RuntimeError('Missing palette texture {}'.format(TEXTURE_PATH))

material = unreal.load_asset(CAR_PATH + '/' + MATERIAL_NAME)
if not material:
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        MATERIAL_NAME, CAR_PATH, unreal.Material, unreal.MaterialFactoryNew())
if not material:
    raise RuntimeError('Could not create car material')

unreal.MaterialEditingLibrary.delete_all_material_expressions(material)
palette_sample = unreal.MaterialEditingLibrary.create_material_expression(
    material, unreal.MaterialExpressionTextureSample, -360, 0)
palette_sample.set_editor_property('texture', texture)
unreal.MaterialEditingLibrary.connect_material_property(
    palette_sample, 'RGB', unreal.MaterialProperty.MP_BASE_COLOR)

metallic = unreal.MaterialEditingLibrary.create_material_expression(
    material, unreal.MaterialExpressionConstant, -360, 120)
metallic.set_editor_property('r', 0.25)
unreal.MaterialEditingLibrary.connect_material_property(
    metallic, '', unreal.MaterialProperty.MP_METALLIC)

roughness = unreal.MaterialEditingLibrary.create_material_expression(
    material, unreal.MaterialExpressionConstant, -360, 200)
roughness.set_editor_property('r', 0.35)
unreal.MaterialEditingLibrary.connect_material_property(
    roughness, '', unreal.MaterialProperty.MP_ROUGHNESS)

unreal.MaterialEditingLibrary.recompile_material(material)
if not unreal.EditorAssetLibrary.save_loaded_asset(material):
    raise RuntimeError('Could not save {}'.format(material.get_path_name()))

for mesh_name in CAR_MESHES:
    mesh = unreal.load_asset(CAR_PATH + '/' + mesh_name)
    if not isinstance(mesh, unreal.StaticMesh):
        raise RuntimeError('Missing static mesh {}'.format(mesh_name))
    slots = mesh.get_editor_property('static_materials')
    for slot_index in range(max(1, len(slots))):
        mesh.set_material(slot_index, material)
    if not unreal.EditorAssetLibrary.save_loaded_asset(mesh):
        raise RuntimeError('Could not save {}'.format(mesh.get_path_name()))
    assigned = [mesh.get_material(index).get_path_name() for index in range(max(1, len(slots)))]
    unreal.log_warning('FAB_CAR_PALETTE mesh={} slots={}'.format(mesh_name, assigned))

unreal.log_warning('FAB_CAR_PALETTE complete material={}'.format(material.get_path_name()))
