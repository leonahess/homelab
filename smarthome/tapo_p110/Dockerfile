FROM alpine:3.19

RUN apk --update --no-cache add git python3 py3-pip

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "./src/tapo.py" ]
