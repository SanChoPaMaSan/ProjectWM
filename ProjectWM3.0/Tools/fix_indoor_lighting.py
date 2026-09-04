import unreal


HOUSE_MAP = "/Game/H/LEVEL/HOUSE"
WM_MAP = "/Game/LEVEL/WM"
LIGHT_LABEL_PREFIX = "IndoorFillLight_"
YARD_DIRECTIONAL_INTENSITY = 10.0
YARD_SKYLIGHT_INTENSITY = 2.0


def log(message):
    unreal.log(f"INDOOR_LIGHT_FIX|{message}")


def set_property(target, name, value):
    target_name = target.get_name() if hasattr(target, "get_name") else target.__class__.__name__
    try:
        target.set_editor_property(name, value)
        log(f"SET|{target_name}|{name}={value}")
        return True
    except Exception as exc:
        log(f"SET_FAILED|{target_name}|{name}|{type(exc).__name__}|{exc}")
        return False


def find_actor_by_label(label):
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == label:
            return actor
    return None


def get_or_create_indoor_light(index, location):
    label = f"{LIGHT_LABEL_PREFIX}{index}"
    actor = find_actor_by_label(label)
    if not actor:
        actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        actor = actor_subsystem.spawn_actor_from_class(
            unreal.PointLight, location, unreal.Rotator(0.0, 0.0, 0.0)
        )
        if not actor:
            raise RuntimeError(f"Could not create {label}")
        actor.set_actor_label(label)
        log(f"LIGHT_CREATED|{label}")
    else:
        actor.set_actor_location(location, False, False)
        log(f"LIGHT_UPDATED|{label}")

    components = actor.get_components_by_class(unreal.PointLightComponent)
    if not components:
        raise RuntimeError(f"{label} has no PointLightComponent")
    component = components[0]
    set_property(component, "mobility", unreal.ComponentMobility.MOVABLE)
    set_property(component, "intensity", 2800.0)
    set_property(component, "attenuation_radius", 1250.0)
    set_property(component, "light_color", unreal.Color(255, 244, 225, 255))
    set_property(component, "cast_shadows", True)
    set_property(component, "use_inverse_squared_falloff", True)


def configure_existing_indoor_light(actor):
    """Normalize a placed fill light without changing the authored layout."""
    components = actor.get_components_by_class(unreal.PointLightComponent)
    if not components:
        raise RuntimeError(f"{actor.get_actor_label()} has no PointLightComponent")

    component = components[0]
    set_property(component, "mobility", unreal.ComponentMobility.MOVABLE)
    set_property(component, "intensity", 2800.0)
    set_property(component, "attenuation_radius", 1250.0)
    set_property(component, "light_color", unreal.Color(255, 244, 225, 255))
    set_property(component, "cast_shadows", True)
    set_property(component, "use_inverse_squared_falloff", True)
    log(f"LIGHT_NORMALIZED|{actor.get_actor_label()}")


def configure_yard_environment_lighting():
    """Lift outdoor shade using the existing sun and sky lights, not extra lamps."""
    directional_updated = False
    skylight_updated = False
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == "DirectionalLight":
            components = actor.get_components_by_class(unreal.DirectionalLightComponent)
            if components:
                set_property(components[0], "mobility", unreal.ComponentMobility.MOVABLE)
                set_property(components[0], "intensity", YARD_DIRECTIONAL_INTENSITY)
                directional_updated = True
        elif actor.get_actor_label() == "SkyLight":
            components = actor.get_components_by_class(unreal.SkyLightComponent)
            if components:
                set_property(components[0], "mobility", unreal.ComponentMobility.MOVABLE)
                set_property(components[0], "intensity", YARD_SKYLIGHT_INTENSITY)
                skylight_updated = True

    if not directional_updated or not skylight_updated:
        raise RuntimeError(
            f"HOUSE environment lights missing: directional={directional_updated}, skylight={skylight_updated}"
        )
    log(
        f"YARD_ENVIRONMENT_NORMALIZED|directional={YARD_DIRECTIONAL_INTENSITY}|"
        f"skylight={YARD_SKYLIGHT_INTENSITY}"
    )


def apply_indoor_lights():
    if not unreal.EditorLoadingAndSavingUtils.load_map(HOUSE_MAP):
        raise RuntimeError(f"Could not load {HOUSE_MAP}")

    # Preserve the authored layout when the map already contains fill lights.
    # Earlier versions always repositioned lights 1-6 and ignored later lights,
    # which left manually added rooms inconsistent.
    existing_lights = [
        actor for actor in unreal.EditorLevelLibrary.get_all_level_actors()
        if actor.get_actor_label().startswith(LIGHT_LABEL_PREFIX)
    ]
    if existing_lights:
        for actor in existing_lights:
            configure_existing_indoor_light(actor)
        configure_yard_environment_lighting()
        unreal.EditorLoadingAndSavingUtils.save_map(
            unreal.EditorLevelLibrary.get_editor_world(), HOUSE_MAP
        )
        log(f"HOUSE_SAVED|lights={len(existing_lights)}|layout=preserved")
        return

    # Initial fallback layout for a map with no authored fill lights.
    locations = [
        unreal.Vector(-650.0, -1250.0, 330.0),
        unreal.Vector(0.0, -1250.0, 330.0),
        unreal.Vector(650.0, -1250.0, 330.0),
        unreal.Vector(-650.0, -300.0, 330.0),
        unreal.Vector(0.0, -300.0, 330.0),
        unreal.Vector(650.0, -300.0, 330.0),
    ]
    for index, location in enumerate(locations, start=1):
        get_or_create_indoor_light(index, location)
    configure_yard_environment_lighting()

    unreal.EditorLoadingAndSavingUtils.save_map(
        unreal.EditorLevelLibrary.get_editor_world(), HOUSE_MAP
    )
    log("HOUSE_SAVED|lights=6|layout=created")


def apply_exposure_fix():
    if not unreal.EditorLoadingAndSavingUtils.load_map(WM_MAP):
        raise RuntimeError(f"Could not load {WM_MAP}")

    ppv = find_actor_by_label("PPV_GlobalToon")
    if not ppv:
        raise RuntimeError("PPV_GlobalToon was not found in WM")
    settings = ppv.get_editor_property("settings")

    # Manual exposure prevents bright emissive ceiling panels from making
    # furniture, trash, and the delivery robots collapse into black shadows.
    set_property(settings, "override_auto_exposure_method", True)
    set_property(settings, "auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
    set_property(settings, "override_auto_exposure_bias", True)
    set_property(settings, "auto_exposure_bias", 0.0)
    set_property(settings, "override_auto_exposure_apply_physical_camera_exposure", True)
    set_property(settings, "auto_exposure_apply_physical_camera_exposure", False)

    unreal.EditorLoadingAndSavingUtils.save_map(
        unreal.EditorLevelLibrary.get_editor_world(), WM_MAP
    )
    log("WM_SAVED|exposure=manual")


def main():
    apply_indoor_lights()
    apply_exposure_fix()
    log("DONE|indoor_lights=6|exposure=manual")


if __name__ == "__main__":
    main()
