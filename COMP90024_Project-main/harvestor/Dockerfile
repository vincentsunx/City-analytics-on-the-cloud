FROM python:3

ENV HTTP_PROXY="http://wwwproxy.unimelb.edu.au:8000/"
ENV HTTPS_PROXY="http://wwwproxy.unimelb.edu.au:8000/"
ENV http_proxy="http://wwwproxy.unimelb.edu.au:8000/"
ENV https_proxy="http://wwwproxy.unimelb.edu.au:8000/"
ENV no_proxy="localhost,127.0.0.1,localaddress,172.16.0.0/12,.melbourne.rc.nectar.o>"

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./harvestor.py" ]
