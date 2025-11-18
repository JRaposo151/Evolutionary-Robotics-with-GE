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
def find_scene_dir(default_rel_paths=None):
    """
    Return a Path to a candidate scene dir. Strategy:
      1) use env var SDF_SCENE_DIR if set
      2) try the script repo root (two parents up from this file)
      3) try current working dir
      4) try common /workspace path (for docker/ssh)
      5) try user's HOME path used in local machine
      6) fallback to the first existent candidate from default_rel_paths
    """
    candidates = []
    env_dir = os.environ.get("SDF_SCENE_DIR")
    if env_dir:
        candidates.append(Path(env_dir))

    # repo root (assumes this script lives inside the repo)
    try:
        repo_root = Path(__file__).resolve().parents[0]  # adjust if needed
        candidates.append(repo_root)
    except Exception:
        pass

    # cwd, workspace and home
    candidates += [Path.cwd(), Path("/workspace"), Path.home()]

    # any additional fallback relative paths you want checked inside repo root
    if default_rel_paths:
        for rp in default_rel_paths:
            candidates.append(Path(rp))

    # return first existing path that contains the SDF or meshes; otherwise return repo_root-like
    for c in candidates:
        if c and c.exists():
            return c.resolve()

    # last resort: return cwd
    return Path.cwd().resolve()


# Use it:
SCENE_DIR = find_scene_dir([
    # optional extra candidates you might want to try relative to repository:
    Path.home() / "PycharmProjects" / "Tese_RE" / "Teste_Tereeno",
    Path.home() / "Documents" / "GitHub" / "Evolutionary-Robotics-with-GE" / "sge_FOR_ER" / "sge" / "sge",
    Path("/workspace")  # docker
])
print("Using SCENE_DIR =", SCENE_DIR)

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
    """
    Resolve URIs robustly:
      - supports file:// absolute URIs but will search for the same basename in candidate dirs
      - supports model:// by searching scene_dir/models and scene_dir
      - searches fallback candidate dirs (scene_dir, repo root, cwd, /workspace, HOME)
    """
    uri = str(uri).strip()

    # helper to search by basename in candidate directories
    def search_for_basename(base_dirs, basename, max_matches=1):
        matches = []
        for d in base_dirs:
            d = Path(d)
            if not d.exists():
                continue
            # use rglob to find files with same name (case sensitive)
            for found in d.rglob(basename):
                matches.append(found.resolve())
                if len(matches) >= max_matches:
                    return matches
        return matches

    # If it's a file:// URI, try direct path first, then search by basename
    if uri.startswith("file://"):
        local = uri[len("file://"):]
        pth = Path(local)
        if pth.exists():
            return pth.resolve()
        # not found at that absolute path on this machine -> try to find the same filename elsewhere
        basename = Path(local).name
        candidate_dirs = [scene_dir,
                          Path(__file__).resolve().parents[2] if '__file__' in globals() else Path.cwd(),
                          Path.cwd(), Path("/workspace"), Path.home()]
        matches = search_for_basename(candidate_dirs, basename, max_matches=1)
        if matches:
            return matches[0]
        return None

    # model:// style URIs common in gazebo
    if uri.startswith("model://"):
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
            # search for the model folder by name inside scene_dir or repo
            candidate_dirs = [scene_dir, Path(__file__).resolve().parents[2] if '__file__' in globals() else Path.cwd(), Path.home(), Path("/workspace")]
            for d in candidate_dirs:
                matches = list(Path(d).rglob(f"*{model_name}*"))
                for m in matches:
                    candidate = (m / tail).resolve() if tail else m.resolve()
                    if candidate.exists():
                        return candidate
        return None

    # direct path (relative or absolute) - try as-is
    pth = Path(uri)
    if pth.exists():
        return pth.resolve()

    # try relative to the scene_dir
    pth = (scene_dir / uri).resolve()
    if pth.exists():
        return pth

    # last resort: search for this basename in candidate dirs
    basename = Path(uri).name
    candidate_dirs = [scene_dir, Path(__file__).resolve().parents[2] if '__file__' in globals() else Path.cwd(), Path.cwd(), Path("/workspace"), Path.home()]
    matches = search_for_basename(candidate_dirs, basename, max_matches=1)
    return matches[0] if matches else None
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
        # print("terrain bodies:", terrain_bodies)
        # if terrain_bodies:
        #     for b in terrain_bodies:
        #         try:
        #             aabb = p.getAABB(b)
        #             print("body", b, "AABB:", aabb)
        #         except Exception as e:
        #             print("getAABB error for", b, e)
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