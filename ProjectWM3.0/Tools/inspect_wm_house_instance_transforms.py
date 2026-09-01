import unreal


def log(message):
    unreal.log(f"HOUSE_INSTANCE|{message}")


if unreal.EditorLoadingAndSavingUtils.load_map("/Game/LEVEL/WM"):
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() in ("HOUSE", "HOUSE2"):
            log(
                f"label={actor.get_actor_label()}|name={actor.get_name()}|"
                f"loc={actor.get_actor_location()}|rot={actor.get_actor_rotation()}|"
                f"scale={actor.get_actor_scale3d()}"
            )
else:
    log("WM_LOAD_FAILED")
