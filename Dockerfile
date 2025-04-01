FROM python:3.12 as builder


RUN pip install --upgrade pip poetry

WORKDIR /app

ARG BLOCKCHAIN_NAME=""

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.in-project true && \
    INSTALL_CMD_BASE="poetry sync --no-root --no-interaction" && \
    GROUP_FLAGS="--with dev" && \
    EXTRAS_ARGS="" && \
    if [ -n "$BLOCKCHAIN_NAME" ]; then \
        EXTRAS_ARGS="--extras $BLOCKCHAIN_NAME"; \
    fi && \
    echo "Running install: $INSTALL_CMD_BASE $GROUP_FLAGS $EXTRAS_ARGS" && \
    $INSTALL_CMD_BASE $GROUP_FLAGS $EXTRAS_ARGS

COPY scripts ./scripts
COPY tx_pipe_ingest ./tx_pipe_ingest
COPY main.py .

RUN --mount=type=secret,id=dotenv,target=/app/.env \
    poetry run poe generate-protos


FROM python:3.12-slim as runtime

WORKDIR /app

ARG BLOCKCHAIN_NAME=""
ENV BLOCKCHAIN_NAME=${BLOCKCHAIN_NAME}

RUN useradd --create-home --shell /bin/bash appuser

COPY --from=builder --chown=appuser:appuser /app/.venv ./.venv

COPY --from=builder /app/tx_pipe_ingest ./tx_pipe_ingest
COPY --from=builder /app/main.py ./main.py

RUN chown -R appuser:appuser /app

USER appuser

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

CMD python main.py $BLOCKCHAIN_NAME
