# Global toon treatment

The WM and LV_Lobby maps use PPV_GlobalToon with two material instances:

| Asset in /Game/Rendering/Toon | Purpose | Defaults |
| --- | --- | --- |
| MI_PP_ToonGlobal | Hue-preserving LDR luminance bands after tonemapping | BandCount 3, BandSoftness 0.025, ToonStrength 0.65, Saturation 1.04 |
| MI_PP_ToonOutline | Depth silhouettes before DOF and temporal resolve | OutlineWidth 1 pixel, OutlineStrength 0.65, DepthThreshold 0.025, MaxOutlineDistance 12000 cm |

Open either instance and enable a scalar parameter override to tune it. Set
ToonStrength or OutlineStrength to zero to disable that component. WM's manual
exposure and authored light placement are preserved. The outline uses depth,
not surface normals, so detailed normal maps do not produce dense internal lines.
The outline fades over the last 20 percent of MaxOutlineDistance.

This is a screen-space stylization of the rendered image, not a replacement of
Unreal's lighting model. Texture contrast, translucent effects and highlights
still need art review. A three-band target is blended with original detail;
the final image intentionally contains more than three absolute brightnesses.

## Rebuild and verification

Run Tools/apply_global_toon.py through UnrealEditor-Cmd with -run=pythonscript,
-AllowCommandletRendering and -d3d11. It rebuilds the two materials, preserves
existing material instance overrides, replaces only these passes in the target
volumes, and saves only the affected assets/maps. Re-running resets parent
defaults; it does not reset instance overrides.

Run Tools/verify_global_toon.py with the same flags to recompile the materials
and verify saved map connections, volume coverage and WM exposure settings.

Run Tools/capture_global_toon.py using an actual editor's -ExecutePythonScript
option. It captures viewport images to Saved/ToonReview and exits without saving
temporary changes. The off images disable only the two toon passes, retaining
the same map exposure. These are editor reference views, not a multiplayer test.

Before the first application, the original WM.umap, LV_Lobby.umap and
M_PP_ToonGlobal.uasset were copied to Saved/ToonBackup_20260908. This includes
the pre-existing, uncommitted traffic changes in WM. Close the editor before
restoring those files if a full rollback is required. Do not overwrite later
map edits with that backup.

## Validation on 2026-09-08

- Both materials compiled successfully for DX11/SM5; saved-map verification
  passed for WM and LV_Lobby, including preservation of WM's manual exposure.
- Six 1280x720 reference screenshots were captured: two indoor player-start
  views and one exterior view, each with the toon passes off/on. The indoor
  and exterior results were visually inspected. An initial hard threshold
  produced noisy highlights; the final material adds BandSoftness and preserves
  emissive whites continuously.
- Final BuildCookRun completed successfully (exit 0), including build, cook,
  stage, pak and archive. Package: Saved/Packages/Windows_Toon_V1/ProjectWM.exe.
- Final packaged WM map rendered in DX11 during a 600-frame benchmark smoke
  run and exited normally. No runtime Error/Fatal or shader compile errors
  were found in Saved/Logs/ToonRuntime.log.
- Evidence: Saved/Logs/ToonApply.log, ToonCapture.log, ToonPackage.log,
  ToonRuntime.log, and Saved/ToonReview/*.png.
- This does not verify two-client travel, sustained gameplay, moving-camera
  outline stability or a controlled GPU performance comparison. The capture
  references are editor views; the package smoke run is a separate check.
- Existing Blueprint comment NodeGuid warnings were reported during map load;
  the build/cook passed and those unrelated assets were not modified.
