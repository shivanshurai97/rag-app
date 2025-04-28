FROM python:3.11-slim

ENV APPNAME="ragappbackend"
ENV HF_HOME="/code/.cache/huggingface"

# Create user and set up environment
RUN addgroup --gid 1001 $APPNAME && \
    adduser --uid 1001 --ingroup $APPNAME --disabled-password --home /code $APPNAME

# Set up working directory and copy requirements
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt

# Install dependencies and download models as root
RUN pip install --no-cache-dir --timeout=1000 --retries=10 torch==2.1.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html && \
    pip install --no-cache-dir --timeout=1000 --retries=10 -r /code/requirements.txt && \
    mkdir -p /code/.cache && \
    python -c "from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification; \
    AutoTokenizer.from_pretrained('BAAI/bge-base-en-v1.5'); \
    AutoModel.from_pretrained('BAAI/bge-base-en-v1.5'); \
    AutoTokenizer.from_pretrained('BAAI/bge-reranker-v2-m3'); \
    AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-v2-m3')" && \
    chown -R $APPNAME:$APPNAME /code/.cache

# Switch to non-root user
USER $APPNAME
ENV PATH="/code/.local/bin:${PATH}"
ENV PYTHONPATH="/code:${PYTHONPATH}"

# Copy application code
COPY --chown=$APPNAME:$APPNAME . .

EXPOSE 8080

# Verify Python environment
RUN echo "Python path: $PYTHONPATH" && \
    python -c "import sys; print(sys.path)" && \
    python -c "import uvicorn; print('Uvicorn version:', uvicorn.__version__)"

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]