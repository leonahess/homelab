FROM python:3.6

WORKDIR /usr/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY src/enviro_plus.py ./

RUN ls -la .

CMD ["python", "./enviro_plus.py"]
