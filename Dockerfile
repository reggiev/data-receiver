FROM gcr.io/distroless/python3

WORKDIR /home/data_receiver
COPY . /home/data_receiver

RUN python get_pip.py && pip install -r requirements.txt

CMD ["-m", "src.data-receiver"]