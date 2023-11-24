FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ENV DATABASE_URL='mysql+pymysql://admin:13579pipe@database-1.czxqqzb2ykig.us-east-1.rds.amazonaws.com:3306/DES427'

COPY . .

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
