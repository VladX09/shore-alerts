FROM python:3.10-buster
ENV DEBIAN_FRONTEND=noninteractive

ENV CODE_PATH=/code

COPY ./insights ${CODE_PATH}
RUN pip install -r ${CODE_PATH}/requirements.txt

WORKDIR ${CODE_PATH}/insights
