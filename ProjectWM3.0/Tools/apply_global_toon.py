"""Build adjustable global toon passes and connect the two shipping maps.

Run through UnrealEditor-Cmd -run=pythonscript with D3D11 (not NullRHI)
so recompile_material validates the actual desktop shaders before maps save.
"""
import unreal

ROOT = '/Game/Rendering/Toon'
LIB = unreal.MaterialEditingLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()


def log(value):
    unreal.log('TOON_APPLY|' + str(value))


def material(name, location, code, parameters, scene_id):
    path = ROOT + '/' + name
    mat = unreal.load_asset(path)
    if not mat:
        mat = TOOLS.create_asset(name, ROOT, unreal.Material, unreal.MaterialFactoryNew())
    LIB.delete_all_material_expressions(mat)
    mat.set_editor_property('material_domain', unreal.MaterialDomain.MD_POST_PROCESS)
    mat.set_editor_property('blendable_location', location)
    node = LIB.create_material_expression(mat, unreal.MaterialExpressionCustom, 0, 0)
    node.set_editor_property('description', name)
    node.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    names = ['SceneColor'] + (['SceneDepth'] if 'OutlineWidth' in parameters else []) + list(parameters)
    inputs = []
    for name in names:
        entry = unreal.CustomInput()
        entry.set_editor_property('input_name', name)
        inputs.append(entry)
    node.set_editor_property('inputs', inputs)
    node.set_editor_property('code', code)
    scene = LIB.create_material_expression(mat, unreal.MaterialExpressionSceneTexture, -500, -200)
    scene.set_editor_property('scene_texture_id', scene_id)
    assert LIB.connect_material_expressions(scene, 'Color', node, 'SceneColor')
    if 'OutlineWidth' in parameters:
        depth = LIB.create_material_expression(mat, unreal.MaterialExpressionSceneTexture, -500, -350)
        depth.set_editor_property('scene_texture_id', unreal.SceneTextureId.PPI_SCENE_DEPTH)
        assert LIB.connect_material_expressions(depth, 'Color', node, 'SceneDepth')
    for index, (name, default) in enumerate(parameters.items()):
        param = LIB.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -500, index * 100)
        param.set_editor_property('parameter_name', name)
        param.set_editor_property('default_value', default)
        param.set_editor_property('group', 'Global Toon')
        assert LIB.connect_material_expressions(param, '', node, name)
    assert LIB.connect_material_property(node, '', unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    errors = LIB.recompile_material(mat)
    if errors:
        raise RuntimeError(name + ': ' + str(errors))
    assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    log('COMPILED|' + path)
    return mat


def instance(name, parent):
    result = unreal.load_asset(ROOT + '/' + name)
    if not result:
        result = TOOLS.create_asset(name, ROOT, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    LIB.set_material_instance_parent(result, parent)
    LIB.update_material_instance(result)
    assert unreal.EditorAssetLibrary.save_loaded_asset(result)
    return result


color_code = '''
// LDR luminance bands preserve hue. Keep true black black and retain texture
// detail by blending; never divide by an unbounded near-zero luminance.
float3 color = max(SceneColor.rgb, 0.0);
float y = dot(color, float3(0.2126, 0.7152, 0.0722));
float bands = clamp(round(BandCount), 2.0, 8.0);
float band = 0.5 / bands;
float width = clamp(BandSoftness, 0.001, 0.12);
for (int i = 1; i < 8; ++i)
{
    if (i < bands)
    {
        float threshold = float(i) / bands;
        band += smoothstep(threshold - width, threshold + width, y) / bands;
    }
}
// Keep emissive whites continuous, avoiding a discontinuity at exactly 1.0.
band = lerp(band, y, smoothstep(0.85, 1.0, y));
float scale = clamp(band / max(y, 0.001), 0.65, 1.65);
float3 result = lerp(color, color * scale, saturate(ToonStrength));
float gray = dot(result, float3(0.2126, 0.7152, 0.0722));
return saturate(lerp(gray.xxx, result, Saturation));
'''

outline_code = '''
// Depth silhouettes before bloom/temporal resolve. Per-buffer conversion and
// clamp keep neighbor samples within this view, including split-screen views.
float2 uv = GetDefaultSceneTextureUV(Parameters, 1);
float2 texel = GetSceneTextureBufferSize(1).zw * max(OutlineWidth, 0.0);
float center = SceneDepth.r;
float edge = 0.0;
float2 offsets[4] = {float2(1,0), float2(-1,0), float2(0,1), float2(0,-1)};
for (int i = 0; i < 4; ++i)
{
    float2 p = ClampSceneTextureUV(uv + offsets[i] * texel, 1);
    float neighbor = SceneTextureLookup(p, 1, false).r;
    // Draw inside the nearer surface; sky and background stay untouched.
    float delta = max(neighbor - center, 0.0) / max(center, 10.0);
    edge = max(edge, smoothstep(DepthThreshold, DepthThreshold * 2.0, delta));
}
edge *= 1.0 - smoothstep(MaxOutlineDistance * 0.8, MaxOutlineDistance, center);
return SceneColor.rgb * (1.0 - edge * saturate(OutlineStrength));
'''

color = material('M_PP_ToonGlobal', unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING,
                 color_code, {'BandCount': 3.0, 'BandSoftness': 0.025, 'ToonStrength': 0.65, 'Saturation': 1.04},
                 unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
outline = material('M_PP_ToonOutline', unreal.BlendableLocation.BL_SCENE_COLOR_BEFORE_DOF,
                   outline_code, {'OutlineWidth': 1.0, 'OutlineStrength': 0.65,
                                  'DepthThreshold': 0.025, 'MaxOutlineDistance': 12000.0},
                   unreal.SceneTextureId.PPI_POST_PROCESS_INPUT0)
color_mi = instance('MI_PP_ToonGlobal', color)
outline_mi = instance('MI_PP_ToonOutline', outline)

for path in ['/Game/LEVEL/WM', '/Game/LEVEL/LV_Lobby']:
    world = unreal.EditorLoadingAndSavingUtils.load_map(path)
    assert world, path
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    volumes = [a for a in actors.get_all_level_actors() if isinstance(a, unreal.PostProcessVolume)]
    volume = next((a for a in volumes if a.get_actor_label() == 'PPV_GlobalToon'), None)
    if not volume:
        volume = actors.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector())
        volume.set_actor_label('PPV_GlobalToon')
    volume.set_editor_property('unbound', True)
    volume.set_editor_property('enabled', True)
    volume.set_editor_property('blend_weight', 1.0)
    settings = volume.get_editor_property('settings')
    weighted = settings.get_editor_property('weighted_blendables')
    # Replace only our passes, preserving any unrelated authored blendables.
    entries = [entry for entry in weighted.get_editor_property('array')
               if entry.get_editor_property('object') not in [color, outline, color_mi, outline_mi]]
    for asset in [outline_mi, color_mi]:
        entry = unreal.WeightedBlendable()
        entry.set_editor_property('weight', 1.0)
        entry.set_editor_property('object', asset)
        entries.append(entry)
    weighted.set_editor_property('array', entries)
    settings.set_editor_property('weighted_blendables', weighted)
    volume.set_editor_property('settings', settings)
    assert unreal.EditorLoadingAndSavingUtils.save_map(world, path)
    log('MAP_SAVED|' + path + '|passes=2')
log('DONE')
