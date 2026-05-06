FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=6060

WORKDIR /srv

COPY backend/sqx-edge-relay/requirements.txt /srv/sqx-edge-relay/requirements.txt
RUN pip install --no-cache-dir -r /srv/sqx-edge-relay/requirements.txt

COPY backend/sqx-edge-relay /srv/sqx-edge-relay
COPY backend/sqx-edge-tool/core/fulfillment_normalizer.py /srv/sqx-edge-tool/core/fulfillment_normalizer.py
RUN touch /srv/sqx-edge-tool/__init__.py /srv/sqx-edge-tool/core/__init__.py

WORKDIR /srv/sqx-edge-relay
EXPOSE 6060

CMD ["sh", "-c", "gunicorn api.server:app --bind 0.0.0.0:${PORT:-6060} --workers ${WEB_CONCURRENCY:-1} --threads ${WEB_THREADS:-4} --timeout ${WEB_TIMEOUT:-60}"]
