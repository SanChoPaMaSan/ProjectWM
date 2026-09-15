"""Reload saved maps, verify pass settings and report useful camera positions."""
import unreal

def log(value):
    unreal.log('TOON_VERIFY|' + str(value))

root = '/Game/Rendering/Toon/'
color = unreal.load_asset(root + 'M_PP_ToonGlobal')
outline = unreal.load_asset(root + 'M_PP_ToonOutline')
assert color and outline
assert color.get_editor_property('blendable_location') == unreal.BlendableLocation.BL_SCENE_COLOR_AFTER_TONEMAPPING
assert outline.get_editor_property('blendable_location') == unreal.BlendableLocation.BL_SCENE_COLOR_BEFORE_DOF
for mat in [color, outline]:
    assert mat.get_editor_property('material_domain') == unreal.MaterialDomain.MD_POST_PROCESS
    errors = unreal.MaterialEditingLibrary.recompile_material(mat)
    assert not errors, str(errors)
    log('COMPILED|' + mat.get_name())
assert unreal.MaterialEditingLibrary.get_material_default_scalar_parameter_value(color, 'BandCount') == 3.0
assert unreal.MaterialEditingLibrary.get_material_default_scalar_parameter_value(color, 'BandSoftness') > 0.0
for path in ['/Game/LEVEL/WM', '/Game/LEVEL/LV_Lobby']:
    assert unreal.EditorLoadingAndSavingUtils.load_map(path)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    volumes = [a for a in actors if isinstance(a, unreal.PostProcessVolume) and a.get_actor_label() == 'PPV_GlobalToon']
    assert len(volumes) == 1, path
    volume = volumes[0]
    assert volume.get_editor_property('unbound') and volume.get_editor_property('enabled')
    assert volume.get_editor_property('blend_weight') == 1.0
    settings = volume.get_editor_property('settings')
    entries = settings.get_editor_property('weighted_blendables').get_editor_property('array')
    for name in ['MI_PP_ToonGlobal', 'MI_PP_ToonOutline']:
        matches = [e for e in entries if e.get_editor_property('object') == unreal.load_asset(root + name)]
        assert len(matches) == 1 and matches[0].get_editor_property('weight') == 1.0
    if path.endswith('/WM'):
        assert settings.get_editor_property('auto_exposure_method') == unreal.AutoExposureMethod.AEM_MANUAL
        assert settings.get_editor_property('auto_exposure_bias') == 0.0
    log('MAP_OK|' + path)
    for actor in actors:
        if isinstance(actor, unreal.PlayerStart) or actor.get_actor_label() in ['HOUSE', 'HOUSE2']:
            log('CAMERA_REFERENCE|' + actor.get_actor_label() + '|' + str(actor.get_actor_location()) + '|' + str(actor.get_actor_rotation()))
log('PASS')
