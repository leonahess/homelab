FROM python:3.6

WORKDIR /usr/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src/enviroplus.py ./

RUN ls -la .

CMD ["python", "./enviroplus.py"]
