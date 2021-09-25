# Part of COMP90024 Project Team members are
# Ziyuan Xiao (940448)
# Pengyu Mu(890756)
# Dechao Sun (980546)
# Seehoi Chow(980301)
# Yuexin Li (959634)

from python:3.8-slim

ENV http_proxy http://wwwproxy.unimelb.edu.au:8000/
ENV https_proxy http://wwwproxy.unimelb.edu.au:8000/
ENV HTTP_PROXY http://wwwproxy.unimelb.edu.au:8000/
ENV HTTPS_PROXY http://wwwproxy.unimelb.edu.au:8000/
ENV no_proxy localhost,localaddress,.melbourne.rc.nectar.org.au,.storage.u nimelb.edu.au,.cloud.unimelb.edu.au
ENV NO_PROXY localhost,localaddress,.melbourne.rc.nectar.org.au,.storage.u nimelb.edu.au,.cloud.unimelb.edu.au

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3"]
CMD ["dataAnalysis.py"]
