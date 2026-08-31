# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:alpine3.23@sha256:7d1ef166503c3c123a51f17d4eeb4dc748c33ebf4ae3bfad54f1163e1c36afcb AS build

WORKDIR /build

# we are unable to use the --require-hashes option as there is no local file defining the hashes
# this is what pip uses for comparison by default.
# However, it can compare the hash against PyPI's hash.
# Since PyPI sends requests over TLS, this should be secure enough for our threat model.
# https://pypi.org/project/pipx/
# RUN pip install pipx==1.7.1 --hash=sha256:a575ced25c507c1b1c978269f5684b5b291e81e3cd14eb3cee196a3c5b304732
RUN uv sync --group build
# https://pipx.pypa.io/latest/how-to/pin-packages.html
RUN pipx install hatch==1.13.0 && pipx pin hatch

COPY . .

ENV PATH="$PATH:/root/.local/bin"

RUN hatch build

########################

# Google distroless Python 3.13 Alpine image
FROM gcr.io/distroless/python3-debian13:nonroot-arm64@sha256:92f92e538766c4550670d0a0909068d8f7968286e183157de67d8068cd147dcc

RUN apk update && \
    apk add --no-cache libmagic

RUN addgroup --system --gid 1001 plexer && \
    adduser --system --uid 1001 --ingroup plexer plexer

WORKDIR /app

COPY --chown=plexer:plexer --from=build /build/dist/ ./dist/

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install ./dist/plexer_cli-*.whl

USER plexer

ENTRYPOINT [ "/app/venv/bin/plexer" ]
CMD [ "--help" ]
