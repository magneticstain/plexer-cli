# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13

FROM python:${PYTHON_VERSION}-slim AS build

WORKDIR /build

RUN pip install pipx==1.7.1
RUN pipx install hatch==1.13.0

COPY . .

ENV PATH="$PATH:/root/.local/bin"

RUN hatch build

########################

# linux/amd64 arch
FROM python:${PYTHON_VERSION}-alpine@sha256:81362dd1ee15848b118895328e56041149e1521310f238ed5b2cdefe674e6dbf

RUN apk update && \
    apk add --no-cache libmagic

RUN addgroup --system --gid 888 plexer && \
    adduser --system --uid 888 --ingroup plexer plexer

WORKDIR /app

COPY --chown=plexer:plexer --from=build /build/dist/ ./dist/

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN pip install ./dist/plexer_cli-*.whl

USER plexer

ENTRYPOINT [ "/app/venv/bin/plexer" ]
CMD [ "--help" ]
