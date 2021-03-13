# Intensyfier dockerfile!
# 2020-04-28

FROM python:3.8.2-slim
LABEL maintainer="Javier Ferrer <javier.f.g@um.es>"

# Working directory
RUN mkdir -p /home/intensyfier
WORKDIR /home/intensyfier

# Install prerequisites
ADD ./requirements.txt /home/intensyfier
RUN pip install -r requirements.txt
RUN apt-get update && apt-get -y install libglib2.0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx

# Add app
ADD . /home/intensyfier

# Launch container
CMD ["./intensyfier_bot.py"]
