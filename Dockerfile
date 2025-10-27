FROM python:3.12.5-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY install-packages.sh /app/
RUN chmod +x /app/install-packages.sh
RUN sh /app/install-packages.sh || true

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py check || true

EXPOSE 8000

COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]