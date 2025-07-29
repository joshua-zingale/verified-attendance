FROM python:3.13-bullseye

WORKDIR /app

COPY . .

RUN pip install .

EXPOSE 5000

ENV FLASK_APP=src

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src:create_app()"]