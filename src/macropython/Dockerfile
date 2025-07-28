FROM python:3.13-slim

# Set environment variables
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install venv and pip
RUN python -m venv $VIRTUAL_ENV \
    && pip install --upgrade pip \
    && pip install debugpy

CMD ["python"]
