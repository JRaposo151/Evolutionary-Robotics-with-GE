# Evolutionary Robotics with DSGE-Style Grammar Evolution, PPO and PyBullet

This project implements an evolutionary robotics pipeline where **robot morphologies are evolved using a grammar-based evolutionary algorithm** and evaluated in **PyBullet**. The system supports running experiments locally, inside a **Docker container**, and within a **Conda environment**.

The repository contains:

* experiment scripts to evolve and evaluate robots
* a PyBullet simulation environment (flat terrain and Mars terrain)
* integration with a grammar-based evolutionary algorithm (SGE3 / DSGE-style workflow)
* utilities for running and resuming experiments from checkpoints
* [Demonstration of morphological evolution and robot behaviours](https://youtu.be/kOsOsedzV5s)

---

## How it works

At a high level, the pipeline follows this loop:

1. **Grammar-based evolution** generates candidate robot “individuals” (morphology encoded by a grammar).
2. Each individual is **materialized** (e.g., as a URDF robot) and evaluated in **PyBullet**.
3. The evaluation produces **fitness metrics** (distance travelled, stability, etc.).
4. Evolution uses the fitness to create the next generation (selection + variation).
5. The process repeats, and results/checkpoints are stored on disk.

---

## Key components

* **PyBullet Simulation**

  * Robots are loaded as URDFs and evaluated in physics simulation.
  * This project supports different terrains:

    * **Flat terrain**
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
* Gymnasium
* Stable-Baselines3 (required for PPO controller training and PPO-based evaluation)
* NumPy, PyYAML, etc.

> Tip: keep `PYTHONNOUSERSITE=1` when debugging to avoid mixing system Python packages with the Conda environment.

---

## Getting started (Conda)

1. Create and activate your Conda environment:

```bash
conda create -n ppo5090 python=3.10 -y
conda activate ppo5090
```

2. Install dependencies:

```bash
pip install pybullet gymnasium numpy pyyaml stable-baselines3
```

3. Choose the terrain in `parameters/standard.yml`.

The terrain is selected directly through the parameter configuration file. The `--mars` command-line flag is no longer used.

4. Run an experiment from the repository root:

```bash
PYTHONUNBUFFERED=1 PYTHONPATH=. \
python -m sge_FOR_ER.sge.examples.Test_Robots \
  --experiment_name dumps/example \
  --seed 42 \
  --parameters parameters/standard.yml
```

---

## Running with Docker

This repository can be used in a Docker workflow. Typical setup:

1. Build the image.
2. Run a container with the repository mounted.
3. Activate the Conda environment inside the container.
4. Run the same `python -m ...` command.

### 1) Build the Docker image

From the repository root, where the `Dockerfile` is located:

```bash
docker build -t evolutionary-robotics-ge .
```

### 2) Run the container

```bash
docker run -d --gpus "device=2" \
  -v "$(pwd)":/workspace \
  --name "your-container-name" \
  evolutionary-robotics-ge \
  bash -c "sleep infinity"
```

> Note: `--gpus "device=2"` assumes that GPU index 2 is available. Change the index according to your system, for example to `device=0`, or remove the `--gpus` option when GPU acceleration is unavailable.

### 3) Open a shell inside the container

```bash
docker exec -it "your-container-name" bash
```

### 4) Activate Conda and run an experiment

```bash
source /opt/conda/etc/profile.d/conda.sh
conda activate ppo5090

PYTHONUNBUFFERED=1 PYTHONPATH=/workspace \
python -m sge_FOR_ER.sge.examples.Test_Robots \
  --experiment_name dumps/example \
  --seed 42 \
  --parameters parameters/standard.yml
```

The terrain must be selected through the relevant settings in `parameters/standard.yml`.

---

## Expected outputs

Each experiment creates an output directory under the path provided through `--experiment_name`.

Depending on the selected configuration, the output may include:

* evolutionary fitness logs
* generated robot morphologies and URDF files
* trained PPO controller files
* evaluation CSV files
* checkpoints for resuming interrupted runs
* plots and visualisations generated during post-processing

---

## Reproducibility

The `--seed` argument controls the random seed used by an evolutionary run.

Different seeds may produce different initial populations, evolutionary trajectories, robot morphologies, and PPO training outcomes. Experiments should therefore be repeated with multiple independent seeds when assessing robustness or comparing configurations.

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

These assets are used to generate/load a Mars-like surface for simulation, enabling more realistic traction and stability tests compared to a flat terrain.

The `mars.world` file contains absolute `file:///...` URIs for `mars_topografi.dae` (for example, around lines 33 and 40). You must update those `<uri>` entries to match your local file path.

Example line to edit:

```xml
<uri>file:///home/your-user/path/to/mars_topografi.dae</uri>
```

Recommended alternatives:

* Replace the absolute path with the correct absolute path on your machine.
* Prefer a setup using relative paths and proper search paths, if your simulator tooling supports it.

> WARNING: If `mars.world` is not updated, terrain loading may fail with PyBullet errors such as “failed to parse link” or “Cannot load SDF file.”

---

## Evolution engine (SGE3)

The grammar-based evolutionary algorithm is provided by:

* `nunolourenco/sge3` (Dynamic / Structured Grammatical Evolution in Python 3). ([GitHub][2])

Since this project uses SGE3 as a dependency/base, its upstream README is the reference for:

* algorithm details
* parameter configuration
* recommended citations and references

---

## Repository structure (code overview)

This section highlights the main entry points and the most important modules.

### Main entry points

* `sge_FOR_ER/sge/examples/Test_Robots.py`  
  Main experiment runner used to launch evolution/evaluation runs. It supports command-line arguments such as `--seed`, `--parameters`, and experiment output folders.

### Simulation environments (PyBullet + Stable-Baselines compatible)

* `sge_FOR_ER/sge/sge/Env_mars.py`  
  PyBullet environment that loads the Mars world/terrain and evaluates robots in a Mars-like scenario. It implements a Gym/Gymnasium-style API (`reset`, `step`, observations, reward) suitable for Stable-Baselines workflows.

* `sge_FOR_ER/sge/sge/Env_horizontal.py`  
  PyBullet environment for the default flat/horizontal terrain scenario. It also implements the Gym/Gymnasium-style API for Stable-Baselines training and testing.

Both environments are responsible for:

* loading the terrain (Mars mesh or flat terrain)
* spawning robot URDFs
* applying actions to robot joints
* stepping the simulation
* building observations and computing rewards/termination conditions

### Experiment and evaluation scripts

* `Controller_testing/`  
  Collection of scripts used for manual and automated testing, including:

  * testing robots evolved by the grammar/evolution pipeline
  * testing industrial/reference robots (e.g., Laikago and Husky)
  * debugging physics, friction, controller behaviour, and reward setups

### Grammars and grammar testing

* `sge_FOR_ER/sge/grammars/`  
  Main grammar definitions used by the evolutionary algorithm to generate robot morphologies.

* `Grammar/`  
  Testing and scratch directory used during grammar development; this is not the main grammar source.

* `robotExpansion_DSGE/`  
  Utilities and experiments for testing and validating grammar-expansion behaviour (DSGE/grammar debugging workflows).

### Symmetry testing

* `SIMETRIA_WORKING/Simetric_Robot.py`  
  Script used to test and validate symmetry constraints in grammar-generated robots, confirming that the symmetry logic is applied correctly.

### URDF building blocks and robot construction

* `URDFs_set/`  
  Contains the URDF components (links and joints) used to construct evolved robots, plus scripts/utilities that assemble robot URDFs from grammar output.

### Parameters and configuration

* `parameters/standard.yml`  
  Main configuration file used by the experiment runner, including settings such as population size, generations, mutation/crossover settings, evaluation settings, and terrain selection.

---

## Troubleshooting

### PyBullet GUI black screen / OpenGL issues

On some Linux setups, PyBullet GUI can fail due to OpenGL / Mesa driver resolution when using Conda. Conda may override system C++ runtime libraries. If you get a black window or “failed to create an OpenGL context”, a reliable workaround is to set these environment variables before running in a terminal or PyCharm:

```bash
PYTHONUNBUFFERED=1
PYTHONNOUSERSITE=1
DISPLAY=:1
LIBGL_DRIVERS_PATH=/usr/lib/x86_64-linux-gnu/dri
LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6
PYTHONPATH=.
```

Important: use `PYTHONPATH=.` from the project root instead of a full absolute path. This avoids hardcoding usernames/paths and makes the project more portable.

### “Cannot load SDF/URDF” on Mars assets

If loading SDF/mesh assets fails, ensure:

* mesh paths are correct; prefer relative paths and `setAdditionalSearchPath`
* the process working directory is the repository root
* the relevant files exist on disk

---

## Citation / Acknowledgements

* Mars terrain assets adapted from `aunefyren/mars_gazebo`. ([GitHub][1])
* Evolution engine based on `nunolourenco/sge3` Structured/Dynamic Structured Grammatical Evolution. ([GitHub][2])

---

## License

This repository is provided for academic and demonstration purposes. All rights reserved unless otherwise stated.

[1]: https://github.com/aunefyren/mars_gazebo "aunefyren/mars_gazebo: Trying to place a robot on Mars ..."
[2]: https://github.com/nunolourenco/sge3 "nunolourenco/sge3: Implementation of SGE Algorithm in Python ..."
