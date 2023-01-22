FROM python:3.10-bullseye

ENV LANG=C.UTF-8 \
  PYTHONPATH="${PYTHONPATH}:/code" \
  POETRY_VERSION=1.3.1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on

# install rust and cargo
# TODO rust toolchain should be removed from final image using build stage
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

WORKDIR /code
COPY ./pyproject.toml /code/
COPY ./poetry.lock /code/

# install dependencies
RUN pip install "poetry==$POETRY_VERSION" && poetry install --no-dev

COPY ./Cargo.toml /code/
COPY ./Cargo.lock /code/
COPY ./src /code/src
# Build Rust binding code with cargo path
RUN /bin/bash -c "source $HOME/.cargo/env && poetry run maturin develop --locked --release"

COPY . /code/
