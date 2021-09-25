# Part of COMP90024 Project Team members are
# Ziyuan Xiao (940448)
# Pengyu Mu(890756)
# Dechao Sun (980546)
# Seehoi Chow(980301)
# Yuexin Li (959634)

from alpine:latest

ENV http_proxy http://wwwproxy.unimelb.edu.au:8000/
ENV https_proxy http://wwwproxy.unimelb.edu.au:8000/
ENV HTTP_PROXY http://wwwproxy.unimelb.edu.au:8000/
ENV HTTPS_PROXY http://wwwproxy.unimelb.edu.au:8000/
ENV no_proxy localhost,localaddress,.melbourne.rc.nectar.org.au,.storage.u nimelb.edu.au,.cloud.unimelb.edu.au
ENV NO_PROXY localhost,localaddress,.melbourne.rc.nectar.org.au,.storage.u nimelb.edu.au,.cloud.unimelb.edu.au


RUN apk add --no-cache python3-dev py-pip \
    && pip install --upgrade pip

WORKDIR /app

COPY . /app

RUN pip --no-cache install -r requirements.txt


ENV FLASK_APP=flaskr
ENV FLASK_ENV=development
ENV port=5000

EXPOSE $port

ENTRYPOINT ["python3", "-m"]
CMD ["flask", "run", "--host=0.0.0.0"]