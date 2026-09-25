FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY agent_telepathy_bus/ ./agent_telepathy_bus/
COPY tests/ ./tests/

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["agent-telepathy-bus"]
CMD ["mesh-sync"]
