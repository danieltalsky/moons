# Use the latest Ubuntu image
FROM ubuntu:latest

# Install OS packages
RUN apt-get update && apt-get install -y apt-utils
# shell uses bc = "basic calculator"
# gfortran is a compiler for the Fortran language
RUN apt-get update && apt-get install -y --upgrade \
    bc \
    gfortran

# Python / MercModule setup
# Install uv python package manager and install dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1
ENV VIRTUAL_ENV=/opt/merc_module/venv
ENV UV_PROJECT_ENVIRONMENT=/opt/merc_module/venv
RUN uv venv $VIRTUAL_ENV
COPY ./ /app/
WORKDIR /app/merc_module
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Ready the installation script
WORKDIR /app/

CMD ["sh", "/app/jupiter_collision_multi_core_runner.sh"]