FROM python:3.9-slim

RUN useradd -m myuser

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN chown -R myuser:myuser /app

USER myuser

CMD ["python", "app.py"]