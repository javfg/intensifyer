# Intensyfier dockerfile!
# 2020-04-28

FROM python:3.8.2-slim
LABEL maintainer="Javier Ferrer <javier.f.g@um.es>"

WORKDIR /home/intensyfier

ENV BUILD_DEPS="" \
  RUN_DEPS="libglib2.0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx curl"

RUN apt-get update \
  && apt-get install -y ${BUILD_DEPS} ${RUN_DEPS} --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* \
  && rm -rf /usr/share/doc && rm -rf /usr/share/man \
  && apt-get purge -y --auto-remove ${BUILD_DEPS} \
  && apt-get clean

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["./start.sh"]
