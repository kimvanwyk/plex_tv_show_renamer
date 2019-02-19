FROM registry.gitlab.com/kimvanwyk/python3-pipenv-container:latest

COPY app/* /app/

WORKDIR /io

ENTRYPOINT ["python", "/app/get_tv_show_details.py"]
