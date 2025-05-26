# 1. Base image with CUDA runtime + Conda
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# 2. Install system deps
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      wget ca-certificates bzip2 \
      git build-essential && \
    rm -rf /var/lib/apt/lists/*

# 3. Install Miniconda
ENV CONDA_DIR=/opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/conda.sh && \
    bash /tmp/conda.sh -b -p $CONDA_DIR && \
    rm /tmp/conda.sh
ENV PATH=$CONDA_DIR/bin:$PATH

# 4. Copy & create your ppo environment
COPY environment.yml /workspace/environment.yml
RUN conda env create -f /workspace/environment.yml && \
    conda clean -afy

# 5. Make your PPO env the default
SHELL ["conda", "run", "-n", "ppo", "/bin/bash", "-lc"]

# 6. Copy your code into the image
WORKDIR /workspace
COPY . /workspace

# 7. Default to bash so you can exec or override
CMD ["bash"]

