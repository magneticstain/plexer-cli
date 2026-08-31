# syntax=docker/dockerfile:1

FROM python:3.13-slim@sha256:6771159cd4fa5d9bba1258caf0b82e6b73458c694d178ad97c5e925c2d0e1a91 AS build

WORKDIR /build

# we are unable to use the --require-hashes option as there is no local file defining the hashes
# this is what pip uses for comparison by default.
# However, it can compare the hash against PyPI's hash.
# Since PyPI sends requests over TLS, this should be secure enough for our threat model.
# https://pypi.org/project/pipx/
RUN pip install pipx==1.7.1 --hash=sha256:a575ced25c507c1b1c978269f5684b5b291e81e3cd14eb3cee196a3c5b304732
# https://pipx.pypa.io/latest/how-to/pin-packages.html
RUN pipx install hatch==1.13.0 && pipx pin hatch

COPY . .

ENV PATH="$PATH:/root/.local/bin"

RUN hatch build

########################

# linux/amd64 arch
FROM python:3.13-alpine@sha256:81362dd1ee15848b118895328e56041149e1521310f238ed5b2cdefe674e6dbf

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
