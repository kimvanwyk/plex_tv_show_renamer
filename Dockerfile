FROM registry.gitlab.com/kimvanwyk/python3-pipenv-container:latest

COPY app/* /app/

ENTRYPOINT ["python", "get_tv_show_details.py"]
