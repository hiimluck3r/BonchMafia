FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR ~/BonchMafiaAdmin

COPY . ./admin
RUN pip install --no-cache-dir -r ./admin/requirements.txt

CMD ["python", "-m", "admin"]