FROM python:3.13-bullseye

WORKDIR /app

COPY . .

RUN pip install .

EXPOSE 5000

ENV FLASK_APP=src

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]