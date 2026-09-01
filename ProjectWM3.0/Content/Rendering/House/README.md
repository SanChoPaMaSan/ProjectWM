# HOUSE Plane material

`T_HousePlane_Tile_BaseColor.png` is the generated seamless warm-ivory porcelain tile base color used by `M_HousePlane_Tile`.

The material is tuned for the project's global toon color treatment: restrained texture contrast, high roughness, and no screen-space outline dependency.
# Bathroom tile override

- `T_Bathroom_FloorTile_BaseColor`: warm ivory 4x4 square ceramic tile albedo.
- `T_Bathroom_WallTile_BaseColor`: near-white 3x4 portrait ceramic wall tile albedo.
- `M_HousePlane_Tile` limits these finishes to the two bathroom XY regions in each mirrored HOUSE level instance using a world-position mask. Up-facing surfaces use the floor tile; vertical surfaces use the wall tile.

# Exterior yard

- `M_HousePlane_Tile`: applies the user-imported `025_basecolor_1k` grass surface only outside both HOUSE footprint masks.
- `PCG_YardGrass`: distributes 2,346 randomized instances using the user-imported grass cluster meshes (`0_58`, `0_1_57`, `0_56`, and related variants).
- The generated `T_Yard_Grass_BaseColor`, `SM_GrassCluster`, and `M_GrassBlade` assets were removed.
