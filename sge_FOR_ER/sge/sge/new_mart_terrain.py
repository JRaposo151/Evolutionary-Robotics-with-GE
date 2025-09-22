#!/usr/bin/env python3
"""
Cleaned loader: try p.loadSDF first; if it fails, parse the SDF to find meshes/heightmaps,
convert DAE -> OBJ if needed, and load in PyBullet as visual + collision shapes.

This version:
 - deduplicates mesh URIs (so the same mesh isn't loaded twice)
 - resolves file:// URIs to absolute Paths and loads each resolved mesh only once
 - picks the largest-loaded body as the terrain (by AABB volume)
 - uses the rayTest-derived spawn_pos when loading Laikago
"""
import os
import sys
import time
import math
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pybullet as p
import pybullet_data

# ---------------- USER SETTINGS ----------------
SCENE_DIR = Path.home() /"Documents"/"GitHub"/"Evolutionary-Robotics-with-GE"/"sge_FOR_ER"/"sge"/"sge"
SDF_FILENAME = "mars.world"
MESH_SCALE = [1.0, 1.0, 1.0]
# ------------------------------------------------

def normalize_quat(q):
    import math
    q = list(q)
    n = math.sqrt(sum(x * x for x in q))
    return [x / n for x in q] if n > 0 else [0, 0, 0, 1]

def parse_sdf_for_meshes_and_heightmaps(sdf_path):
    meshes = []
    heightmaps = []
    try:
        tree = ET.parse(sdf_path)
    except Exception as e:
        #print("Could not parse SDF:", e)
        return {'meshes': [], 'heightmaps': []}
    root = tree.getroot()
    for mesh in root.findall('.//mesh'):
        uri = mesh.find('uri')
        if uri is not None and uri.text:
            meshes.append(uri.text.strip())
    for hm in root.findall('.//heightmap'):
        uri = hm.find('uri')
        if uri is not None and uri.text:
            heightmaps.append(uri.text.strip())
    return {'meshes': meshes, 'heightmaps': heightmaps}

def resolve_uri_to_path(uri, scene_dir):
    uri = uri.strip()
    if uri.startswith('file://'):
        local = uri[len('file://'):]
        pth = Path(local)
        if pth.exists():
            return pth.resolve()
        pth = (scene_dir / local).resolve()
        return pth if pth.exists() else None
    if uri.startswith('model://'):
        parts = uri.split('/', 3)
        if len(parts) >= 3:
            model_name = parts[2]
            tail = parts[3] if len(parts) >= 4 else ''
            cand = scene_dir / 'models' / model_name / tail
            if cand.exists():
                return cand.resolve()
            cand = scene_dir / model_name / tail
            if cand.exists():
                return cand.resolve()
            matches = list(scene_dir.rglob(f"*{model_name}*"))
            if matches:
                cand = matches[0] / tail
                if cand.exists():
                    return cand.resolve()
        return None
    pth = Path(uri)
    if pth.exists():
        return pth.resolve()
    pth = (scene_dir / uri).resolve()
    if pth.exists():
        return pth
    return None

def convert_dae_to_obj(dae_path, obj_path):
    """Try assimp CLI then trimesh/pycollada fallback. Return True on success."""
    assimp_cmd = shutil.which("assimp") or shutil.which("assimp-cli") or shutil.which("assimp.exe")
    if assimp_cmd:
        cmd = [assimp_cmd, "export", str(dae_path), str(obj_path)]
        #print("Running assimp:", " ".join(cmd))
        try:
            subprocess.check_call(cmd)
            return obj_path.exists()
        except Exception as e:
            print("assimp conversion failed:", e)
    try:
        import trimesh
        #print("Trying trimesh to load DAE...")
        mesh = trimesh.load(str(dae_path), force='scene')
        if isinstance(mesh, trimesh.Scene):
            combined = trimesh.util.concatenate([g for g in mesh.geometry.values()])
        else:
            combined = mesh
        combined.export(str(obj_path))
        return obj_path.exists()
    except Exception as e:
        print("trimesh/pycollada failed or not installed:", e)
    #print("Automatic conversion failed. Please convert the DAE to OBJ using Blender or assimp.")
    return False

def load_meshes_into_pybullet(mesh_paths, scene_dir, mesh_scale):
    """
    mesh_paths: iterable of URI strings (from SDF). Resolve them, dedupe, convert .dae -> .obj if needed,
                 load each resolved file once and return list of created body ids.
    """
    loaded_ids = []
    resolved_paths = []
    for mesh_uri in mesh_paths:
        pth = resolve_uri_to_path(mesh_uri, scene_dir)
        if pth is None:
            #print("Could not resolve mesh URI:", mesh_uri)
            continue
        resolved_paths.append(pth)
        break

    # Deduplicate preserving order
    seen = set()
    unique_paths = []
    for pth in resolved_paths:
        key = str(pth.resolve())
        if key in seen:
            #print("Skipping duplicate mesh path:", key)
            continue
        seen.add(key)
        unique_paths.append(pth)

    for resolved in unique_paths:
        ext = resolved.suffix.lower()
        mesh_file = resolved
        if ext == ".dae":
            obj_target = resolved.with_suffix(".obj")
            if not obj_target.exists():
                #print("Converting DAE -> OBJ:", resolved, "->", obj_target)
                ok = convert_dae_to_obj(resolved, obj_target)
                if not ok:
                    #print("Conversion failed for", resolved, "; trying visual-only (no collision).")
                    try:
                        vid = p.createVisualShape(p.GEOM_MESH, fileName=str(resolved), meshScale=mesh_scale)
                        bid = p.createMultiBody(baseMass=0, baseVisualShapeIndex=vid, basePosition=[0,0,0])
                        loaded_ids.append(bid)
                        #print("Loaded visual-only body id:", bid)
                        continue
                    except Exception as e:
                        #print("Visual-only load also failed:", e)
                        continue
            mesh_file = obj_target

        #print("Creating visual+collision for mesh:", mesh_file)
        try:
            vis_id = p.createVisualShape(p.GEOM_MESH, fileName=str(mesh_file), meshScale=mesh_scale)
            col_id = p.createCollisionShape(p.GEOM_MESH, fileName=str(mesh_file), meshScale=mesh_scale, flags=p.GEOM_FORCE_CONCAVE_TRIMESH)
            body_id = p.createMultiBody(baseMass=0, baseCollisionShapeIndex=col_id, baseVisualShapeIndex=vis_id, basePosition=[0,0,0])
            loaded_ids.append(body_id)
            #print("Loaded mesh body id:", body_id)
        except Exception as e:
            #print("Failed to create collision for mesh (try visual-only):", e)
            try:
                vid = p.createVisualShape(p.GEOM_MESH, fileName=str(mesh_file), meshScale=mesh_scale)
                bid = p.createMultiBody(baseMass=0, baseVisualShapeIndex=vid, basePosition=[0,0,0])
                loaded_ids.append(bid)
                #print("Loaded visual-only body id:", bid)
            except Exception as ee:
                print("Visual-only also failed:", ee)
    return loaded_ids

def pick_largest_body_by_aabb(bodies):
    """Return the body id with the largest AABB volume (helpful if multiple bodies loaded)."""
    best = None
    best_vol = -1.0
    for b in bodies:
        try:
            aabb_min, aabb_max = p.getAABB(b)
            dx = aabb_max[0] - aabb_min[0]
            dy = aabb_max[1] - aabb_min[1]
            dz = aabb_max[2] - aabb_min[2]
            vol = max(0.0, dx*dy*dz)
            # prefer larger volumes
            if vol > best_vol:
                best_vol = vol
                best = b
        except Exception:
            continue
    return best

def world_generation():
    scene_dir = Path(SCENE_DIR).expanduser()
    sdf_path = scene_dir / SDF_FILENAME
    if not sdf_path.exists():
        #print("SDF not found:", sdf_path)
        candidates = list(scene_dir.glob("*.sdf")) + list(scene_dir.glob("*.world"))
        if not candidates:
            #print("No SDF/WORLD found. Abort.")
            sys.exit(1)
        sdf_path = candidates[0]
        #print("Using candidate:", sdf_path)

    # start PyBullet
    p.setAdditionalSearchPath(str(scene_dir))

    # 1) try to load SDF (we will remove loaded SDF bodies and manually load meshes to ensure correct collisions)
    loaded_sdf = p.loadSDF(str(sdf_path))

    # parse SDF to find mesh/heightmap URIs (do this always)
    parsed = parse_sdf_for_meshes_and_heightmaps(sdf_path)
    #print("Parsed SDF -> meshes:", parsed['meshes'], "heightmaps:", parsed['heightmaps'])

    terrain_bodies = []

    # if loadSDF created bodies, remove them (they often create cheap box collisions)
    if loaded_sdf:
        for bid in loaded_sdf:
            #print("SDF-created body debug - id:", bid, "numJoints:", p.getNumJoints(bid), "AABB:", p.getAABB(bid))
            try:
                p.removeBody(bid)
                #print("Removed SDF-created body", bid)
            except Exception as e:
                print("Failed to remove SDF body", bid, e)

    # load meshes (deduplicated internally)
    if parsed['meshes']:
        terrain_bodies = load_meshes_into_pybullet(parsed['meshes'], scene_dir, MESH_SCALE)

    # fallback try any mesh file in folder if nothing loaded
    if not terrain_bodies:
        any_meshes = list(scene_dir.glob("*.obj")) + list(scene_dir.glob("*.dae")) + list(scene_dir.glob("*.stl"))
        if any_meshes:
            #print("Fallback: loading", any_meshes[0])
            terrain_bodies = load_meshes_into_pybullet([str(any_meshes[0])], scene_dir, MESH_SCALE)

    # pick the best terrain_id (largest by aabb volume) if multiple were created
    terrain_id = None
    if terrain_bodies:
        terrain_id = pick_largest_body_by_aabb(terrain_bodies)
        #print("Using terrain body id (manual):", terrain_id, "all bodies:", terrain_bodies)
    #else:
        #print("No manual terrain created; no terrain collision available.")

    return terrain_id

# if __name__ == "__main__":
#     main()