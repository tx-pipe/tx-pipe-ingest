FROM python:3.12 as builder

RUN pip install poetry

WORKDIR /app

ARG INSTALL_DEV=false
ARG BLOCKCHAIN_NAME=""

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.in-project true && \
    INSTALL_CMD_BASE="poetry install --no-root --no-interaction --sync" && \
    GROUP_FLAGS="" && \
    EXTRAS_ARGS="" && \
    if [ "$INSTALL_DEV" = "true" ]; then \
        GROUP_FLAGS="--with dev"; \
    else \
        GROUP_FLAGS="--only main"; \
    fi && \
    if [ -n "$BLOCKCHAIN_NAME" ]; then \
        EXTRAS_ARGS="--extras $BLOCKCHAIN_NAME"; \
    fi && \
    echo "Running: $INSTALL_CMD_BASE $GROUP_FLAGS $EXTRAS_ARGS" && \
    $INSTALL_CMD_BASE $GROUP_FLAGS $EXTRAS_ARGS


FROM python:3.12-slim as runtime

WORKDIR /app

ARG BLOCKCHAIN_NAME=""
ENV BLOCKCHAIN_NAME=${BLOCKCHAIN_NAME}

RUN useradd --create-home --shell /bin/bash appuser
USER appuser

COPY --from=builder --chown=appuser:appuser /app/.venv ./.venv

COPY --chown=appuser:appuser . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

CMD python main.py $BLOCKCHAIN_NAME
