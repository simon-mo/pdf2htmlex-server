FROM pdf2htmlex/pdf2htmlex:0.18.8.rc2-master-20200820-ubuntu-20.04-x86_64

RUN apt update
RUN apt install -y python3 python-is-python3 python3-pip

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py app.py

ENTRYPOINT ["uvicorn", "app:app", "--host=0.0.0.0"]