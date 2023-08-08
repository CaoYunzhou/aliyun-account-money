FROM python:3.7-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories
RUN apk add --no-cache musl-dev openssl-dev libffi-dev tzdata gcc
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
COPY . /app/
WORKDIR /app
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
CMD ["python3", "account-money.py"]
