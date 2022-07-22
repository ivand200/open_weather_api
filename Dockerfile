FROM python:3.8.10

WORKDIR /src

COPY ./requirements.txt /src

RUN pip install -r requirements.txt

COPY . /src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]