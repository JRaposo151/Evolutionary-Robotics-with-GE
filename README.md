
# Evolutionary Robotics with Grammar-Based Evolution (SGE) + PyBullet Mars Terrain

This project implements an evolutionary robotics pipeline where **robot morphologies are evolved using a grammar-based evolutionary algorithm** and evaluated in **PyBullet**. The system supports running experiments locally, inside a **Docker container**, and within a **Conda environment**.

The repository contains:

* experiment scripts to evolve and evaluate robots
* a PyBullet simulation environment (flat plane and Mars terrain)
* integration with a grammar-based evolutionary algorithm (SGE3 / DSGE-style workflow)
* utilities for running and resuming experiments from checkpoints

---

## How it works

At a high level, the pipeline follows this loop:

1. **Grammar-based evolution** generates candidate robot “individuals” (morphology encoded by a grammar).
2. Each individual is **materialized** (e.g., URDF robot) and evaluated in **PyBullet**.
3. The evaluation produces **fitness metrics** (distance traveled, stability, etc.).
4. Evolution uses the fitness to create the next generation (selection + variation).
5. The process repeats, and results/checkpoints are stored on disk.

---

## Key components

* **PyBullet Simulation**

  * Robots are loaded as URDFs and evaluated in physics simulation.
  * For this project, supports different terrains:

    * **Flat plane**
    * **Mars terrain (mesh-based)**

* **Grammar-based Evolution Algorithm**

  * This project uses the **SGE3** implementation by Nuno Lourenço as the evolutionary engine.
    The SGE3 README already documents the algorithm, operators, and configuration format, so this repository focuses on how SGE3 is applied to evolving robots and running physics-based evaluations.

---

## Requirements

You can run this project either:

* **inside Docker** (recommended for reproducibility), or
* **locally with Conda**.

### Conda (recommended locally)

* Python 3.10
* PyBullet
* gymnasium
* stable-baselines3 (if running PPO-based controllers or evaluation scripts)
* numpy, pyyaml, etc.

> Tip: keep `PYTHONNOUSERSITE=1` when debugging to avoid mixing system Python packages with the conda environment.

---

## Getting started (Conda)

1. Create / activate your conda environment (example):

```bash
conda create -n ppo5090 python=3.10 -y
conda activate ppo5090
```

2. Install dependencies:

```bash
pip install pybullet gymnasium numpy pyyaml
pip install stable-baselines3  # optional, only if you run PPO scripts
```

3. Run an experiment (example) ( mars has to be 1 to be activated, 0 to be not activated ):

```bash
PYTHONUNBUFFERED=1 PYTHONPATH=/workspace \
python -m sge_FOR_ER.sge.examples.Test_Robots \
  --experiment_name dumps/example \
  --seed 42 \
  --parameters ../parameters/standard.yml
  --mars 1
```

---

## Running with Docker

This repository can be used in a Docker workflow. Typical setup:

1. Build the image (or use your existing image)
2. Run a container with the repo mounted
3. Activate the conda environment inside the container
4. Run the same `python -m ...` command

Example structure (adjust to your Dockerfile / image):
### 1) Build the Docker image
From the repository root (where the `Dockerfile` is):

```bash
docker build -t evolutionary-robotics-ge .
```

```bash
docker run -d --gpus "device=2" \
  -v "$(pwd)":/workspace \
  --name "(name of the docker)" \
  evolutionary-robotics-ge \
  bash -c "sleep infinity"
```
```bash
docker exec -it  "(name of the docker)" bash
```

Then inside:

```bash
source /opt/conda/etc/profile.d/conda.sh

conda activate ppo5090

PYTHONUNBUFFERED=1 PYTHONPATH=/workspace \
python -m sge_FOR_ER.sge.examples.Test_Robots \
  --experiment_name dumps/example \
  --seed 42 \
  --parameters ../parameters/standard.yml
  --mars 1
```

---

## Mars terrain assets

This project uses Mars terrain assets sourced from the `mars_gazebo` repository. Specifically, the following files are reused:

* `mars.world`
* `mars_topografi.dae`
* `mars_topografi.obj`
* `material.mtl`
* `material_0.png`
* `model_texture.jpg`

Upstream source: `aunefyren/mars_gazebo` (GitHub). ([GitHub][1])

These assets are used to generate/load a Mars-like surface for simulation, enabling more realistic traction and stability tests compared to a flat plane.


The mars.world file contains absolute file:///... URIs for mars_topografi.dae (e.g., lines around 33 and 40). You must update those <uri> entries to match your local file path.

Example line to edit:

<uri>file:///home/your-user/path/to/mars_topografi.dae</uri>

Recommended alternatives:

Replace the absolute path with the correct absolute path on your machine, or

Prefer a setup using relative paths + proper search paths, if your simulator tooling supports it.

WARNING: If mars.world is not updated, terrain loading may fail with PyBullet errors like “failed to parse link” / “Cannot load SDF file.”
---

## Evolution engine (SGE3)

The grammar-based evolutionary algorithm is provided by:

* `nunolourenco/sge3` (Dynamic / Structured Grammatical Evolution in Python 3). ([GitHub][2])

Since this project uses SGE3 as a dependency/base, its upstream README is the reference for:

* algorithm details
* parameter configuration
* recommended citations / references

---
## Repository structure (code overview)

This section highlights the main entry points and the most important modules.

### Main entry points
- `sge_FOR_ER/sge/examples/Test_Robots.py`  
  Main experiment runner used to launch evolution/evaluation runs (supports command-line args like `--seed`, `--parameters`, and experiment output folders).


This section highlights the main modules and directories you will interact with when evolving, training, and testing robots.

### Simulation environments (PyBullet + Stable-Baselines compatible)
- `sge_FOR_ER/sge/sge/Env_mars.py`  
  PyBullet environment that loads the Mars world/terrain and evaluates robots in a Mars-like scenario. Implements a Gym/Gymnasium-style API (reset/step/observation/reward) suitable for Stable-Baselines workflows.

- `sge_FOR_ER/sge/sge/Env_horizontal.py`  
  PyBullet environment for the default flat/horizontal plane scenario. Also implements the Gym/Gymnasium-style API for Stable-Baselines training/testing.

Both environments are responsible for:
- loading the terrain (Mars mesh or flat plane)
- spawning robot URDFs
- applying actions to robot joints
- stepping the simulation
- building observations and computing rewards/termination

### Experiment and evaluation scripts
- `Controller_testing/`  
  Collection of scripts used for manual and automated testing, including:
  - testing robots evolved by the grammar/evolution pipeline
  - testing industrial/reference robots (e.g., Laikago and Husky)
  - debugging physics, friction, controller behavior, and reward setups

### Grammars and grammar testing
- `sge_FOR_ER/sge/grammars/`  
  Main grammar definitions used by the evolutionary algorithm to generate robot morphologies.

- `Grammar/`  
  Testing and scratch directory used during grammar development (not the main grammar source).

- `robotExpansion_DSGE/`  
  Utilities and experiments for testing/validating grammar expansion behavior (DSGE/grammar debugging workflows).

### Symmetry testing
- `SIMETRIA_WORKING/Simetric_Robot.py`  
  Script used to test and validate symmetry constraints in the grammar-generated robots (to confirm symmetry logic is being applied correctly).

### URDF building blocks and robot construction
- `URDFs_set/`  
  Contains the URDF components (links, joints) used to construct evolved robots, plus scripts/utilities that assemble robot URDFs from the grammar output.
### Parameters and configuration
- `parameters/standard.yml`  
  Main configuration file used by the experiment runner (e.g., population size, generations, mutation/crossover settings, evaluation settings).


---

## Troubleshooting

### PyBullet GUI black screen / OpenGL issues

On some Linux setups, PyBullet GUI can fail due to OpenGL / Mesa driver resolution when using Conda (Conda may override system C++ runtime libraries). If you get a black window or “failed to create an OpenGL context”, a reliable workaround is to set these environment variables before running (terminal or PyCharm):

```bash
PYTHONUNBUFFERED=1
PYTHONNOUSERSITE=1
DISPLAY=:1
LIBGL_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri
LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6
PYTHONPATH=.
```
Important: use PYTHONPATH=. (project root) instead of a full absolute path.
This avoids hardcoding usernames/paths and makes the project more portable.
Then run your script as usual.

### “Cannot load SDF/URDF” on Mars assets

If loading SDF/mesh assets fails, ensure:

* mesh paths are correct (prefer relative paths + `setAdditionalSearchPath`)
* the process working directory is your repo root
* the relevant files exist on disk

---

## Citation / Acknowledgements

* Mars terrain assets adapted from `aunefyren/mars_gazebo`. ([GitHub][1])
* Evolution engine based on `nunolourenco/sge3` Structured/Dynamic Structured Grammatical Evolution. ([GitHub][2])

---

## License

Add your license here (e.g., MIT, Apache-2.0, GPL, or “All rights reserved”). If you are redistributing assets/code from other repositories, ensure license compatibility and include required notices.

[1]: https://github.com/aunefyren/mars_gazebo?utm_source=chatgpt.com "aunefyren/mars_gazebo: Trying to place a robot on Mars ..."
[2]: https://github.com/nunolourenco/sge3?utm_source=chatgpt.com "nunolourenco/sge3: Implementation of SGE Algorithm in ..."
