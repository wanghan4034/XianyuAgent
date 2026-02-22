FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY xianyu_agent ./xianyu_agent
COPY README.md ./README.md
RUN mkdir -p /app/uploads

ENTRYPOINT ["python", "-m", "xianyu_agent.cli"]
CMD ["iPhone 15", "--max-items", "10"]
