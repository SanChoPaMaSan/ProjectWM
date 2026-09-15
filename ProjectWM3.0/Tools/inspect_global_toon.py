import unreal

def log(value):
    unreal.log('TOON_INSPECT|' + str(value))

material = unreal.load_asset('/Game/Rendering/Toon/M_PP_ToonGlobal')
log('MATERIAL|' + str(material))
if material:
    log(material.get_editor_property('material_domain'))
    log(material.get_editor_property('blendable_location'))
    log('EXPRESSIONS|' + str(unreal.MaterialEditingLibrary.get_num_material_expressions(material)))
    for obj in unreal.MaterialEditingLibrary.get_material_expressions(material):
        if isinstance(obj, unreal.MaterialExpressionCustom):
            log('CODE|' + obj.get_editor_property('code'))
            log('INPUTS|' + str(obj.get_editor_property('inputs')))
for path in ['/Game/LEVEL/WM', '/Game/LEVEL/LV_Lobby']:
    world = unreal.EditorLoadingAndSavingUtils.load_map(path)
    log('MAP|' + path + '|' + str(bool(world)))
    for actor in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if isinstance(actor, unreal.PostProcessVolume):
            log('VOLUME|' + actor.get_actor_label() + '|' + str(actor.get_editor_property('unbound')))
            settings = actor.get_editor_property('settings')
            log('BLENDABLES|' + str(settings.get_editor_property('weighted_blendables')))
            for key in ['auto_exposure_method', 'auto_exposure_bias', 'override_auto_exposure_method']:
                log(key + '|' + str(settings.get_editor_property(key)))
log('DONE')
