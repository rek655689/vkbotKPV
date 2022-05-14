FROM python:3.10

COPY . /app/vkbotkpv
WORKDIR /app/vkbotkpv

RUN pip3 install -r requirements.txt

EXPOSE 5000 3306