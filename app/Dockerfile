FROM condaforge/mambaforge

# Create and switch to non-root user
RUN useradd -m -s /bin/bash nonroot
WORKDIR /home/nonroot/app
USER nonroot

# copy application files to the container
COPY --chown=nonroot:nonroot . .

# This is where pip will be after the conda environment is created
# can't conda activate in dockerfile
ENV PIP=/home/nonroot/.conda/envs/coordinator/bin/pip

# Install dependencies in conda environment
RUN <<EOF
mamba create -n coordinator -y python=3.12.3
$PIP install --no-cache-dir -r requirements.txt
EOF

HEALTHCHECK --interval=2s --timeout=2s \
    CMD curl --silent --fail localhost/flask-health-check || exit 1

ENTRYPOINT ["/home/nonroot/.conda/envs/coordinator/bin/python"]

CMD ["-m", "gunicorn", "-w", "3", "-t", "60", "-b", "0.0.0.0:80", "main:app"]