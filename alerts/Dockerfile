FROM python:3.10-buster as prod
ENV DEBIAN_FRONTEND=noninteractive

ENV CODE_PATH=/code
WORKDIR ${CODE_PATH}

COPY . ${CODE_PATH}
RUN pip install -r ${CODE_PATH}/requirements.txt

FROM prod as dev
RUN apt-get update && apt-get install -y git ssh
RUN pip install -r ${CODE_PATH}/requirements.dev.txt
