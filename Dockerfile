# 1. Base image with CUDA runtime
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# 2. System deps
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget ca-certificates bzip2 \
    git build-essential \
    libgl1 libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# 3. Install Miniconda
ENV CONDA_DIR=/opt/conda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/conda.sh && \
    bash /tmp/conda.sh -b -p $CONDA_DIR && \
    rm /tmp/conda.sh
ENV PATH=$CONDA_DIR/bin:$PATH

# 4. Workdir
WORKDIR /workspace

# 5. Copy env file first (better layer caching)
COPY environment.yml /workspace/environment.yml

# 6. Create env
RUN conda env create -f /workspace/environment.yml && conda clean -afy

# 7. Make env default (set PATH to env bin)
# IMPORTANT: must match the "name:" inside environment.yml (recommended: ppo5090)
ENV CONDA_DEFAULT_ENV=ppo5090
ENV PATH=$CONDA_DIR/envs/$CONDA_DEFAULT_ENV/bin:$PATH

# 8. Copy code
COPY . /workspace

# 9. Default command
CMD ["bash"]