# Pre-shimmer-fix state (2026-08-21)

Rollback reference before the Plane/yard flicker fix.

- All nine affected textures: `MipGenSettings=TMGS_NoMipmaps`, `Filter=TF_Default`, `LODBias=0`, `NeverStream=false`.
- SRGB is `true` except `YardGrass/Textures/025_normal_1k`, which is `false`.
- Both HOUSE level-instance `DirectionalLight_0.LightComponent0` components: `bVisible=true`, `bAffectsWorld=true`, `Intensity=6`, `Mobility=Movable`.
- Main WM Directional Light remains unchanged.

Affected textures:

- `/Game/Rendering/House/T_HousePlane_Tile_BaseColor`
- `/Game/Rendering/House/T_Bathroom_WallTile_BaseColor`
- `/Game/Rendering/House/T_Bathroom_FloorTile_BaseColor`
- `/Game/Rendering/House/YardGrass/Textures/025_basecolor_1k`
- `/Game/Rendering/House/YardGrass/Textures/025_height_1k`
- `/Game/Rendering/House/YardGrass/Textures/025_metallic_1k`
- `/Game/Rendering/House/YardGrass/Textures/025_normal_1k`
- `/Game/Rendering/House/YardGrass/Textures/025_smoothness_1k`
- `/Game/Rendering/House/YardGrass/Textures/025_ao_1k`
