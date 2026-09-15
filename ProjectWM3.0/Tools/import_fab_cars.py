import unreal


SOURCE_ROOT = r'C:\Users\admin\Downloads\fbx\Fbx'
DESTINATION = '/Game/Fab/Car'
CARS = (
    ('Classic Car_9.fbx', 'SM_ClassicCar'),
    ('Hatchback Car_15.fbx', 'SM_HatchbackCar'),
    ('Monster Truck_15.fbx', 'SM_MonsterTruck'),
    ('N Van_10.fbx', 'SM_Van'),
    ('N_Muscle Car_10.fbx', 'SM_MuscleCar'),
    ('Pick Up_11.fbx', 'SM_Pickup'),
    ('Sport Car_39.fbx', 'SM_SportCar'),
)


def import_asset(filename, destination_path, destination_name, is_fbx=False):
    task = unreal.AssetImportTask()
    task.set_editor_property('filename', filename)
    task.set_editor_property('destination_path', destination_path)
    task.set_editor_property('destination_name', destination_name)
    task.set_editor_property('automated', True)
    task.set_editor_property('replace_existing', False)
    task.set_editor_property('save', True)

    if is_fbx:
        options = unreal.FbxImportUI()
        options.set_editor_property('automated_import_should_detect_type', False)
        options.set_editor_property('mesh_type_to_import', unreal.FBXImportType.FBXIT_STATIC_MESH)
        options.set_editor_property('import_as_skeletal', False)
        options.set_editor_property('import_materials', False)
        options.set_editor_property('import_textures', False)
        options.static_mesh_import_data.set_editor_property('combine_meshes', True)
        options.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs', True)
        task.set_editor_property('options', options)

    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if not task.imported_object_paths:
        raise RuntimeError('Import failed: {}'.format(filename))
    unreal.log_warning('FAB_CAR_IMPORT {} -> {}'.format(filename, list(task.imported_object_paths)))


unreal.EditorAssetLibrary.make_directory(DESTINATION)
for source_name, asset_name in CARS:
    import_asset(SOURCE_ROOT + '\\' + source_name, DESTINATION, asset_name, True)

unreal.EditorAssetLibrary.make_directory(DESTINATION + '/Textures')
import_asset(SOURCE_ROOT + '\\Texture\\Color.png', DESTINATION + '/Textures', 'T_Car_Color')

for _source_name, asset_name in CARS:
    asset_path = DESTINATION + '/' + asset_name
    asset = unreal.load_asset(asset_path)
    if not isinstance(asset, unreal.StaticMesh):
        raise RuntimeError('Missing static mesh {}'.format(asset_path))
    unreal.log_warning('FAB_CAR_VERIFY mesh={} bounds={}'.format(asset_path, asset.get_bounds().box_extent))

texture = unreal.load_asset(DESTINATION + '/Textures/T_Car_Color')
if not isinstance(texture, unreal.Texture2D):
    raise RuntimeError('Missing car texture')
unreal.log_warning('FAB_CAR_VERIFY texture={}'.format(texture.get_path_name()))
