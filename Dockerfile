# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:alpine3.23@sha256:7d1ef166503c3c123a51f17d4eeb4dc748c33ebf4ae3bfad54f1163e1c36afcb AS build

WORKDIR /build

COPY pyproject.toml uv.lock README.md LICENSE /build/
RUN mkdir -p /build/src
COPY src/ /build/src/

RUN uv sync --group build

RUN apk update && \
    apk add --no-cache libmagic pipx

# https://pipx.pypa.io/latest/how-to/pin-packages.html
RUN pipx install hatch==1.18.1 && pipx pin hatch
RUN PATH="$PATH:/root/.local/bin" hatch build

########################

FROM python:3.14-alpine3.23@sha256:e7cff362a12454395f8dc99607c21a602ea880cdce03538877b90c2ba932b16f

RUN addgroup --system --gid 1001 plexer && \
    adduser --system --uid 1001 --ingroup plexer plexer

COPY --chown=plexer:plexer --from=build /build/dist/ /app/dist/

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install /app/dist/plexer_cli-*.whl

USER plexer

ENTRYPOINT [ "/app/venv/bin/plexer" ]
CMD [ "--help" ]
