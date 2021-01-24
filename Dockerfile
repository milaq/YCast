FROM python:3-slim
WORKDIR /src

COPY ycast/ ycast
COPY README.md .
COPY setup.py .
RUN python setup.py install

CMD ["python", "-m", "ycast", "-l", "0.0.0.0", "-p", "8010"]

EXPOSE 8010
