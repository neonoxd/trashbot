FROM localhost/pyffmpeg
ADD ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
ADD . /app

CMD [ "python", "main.py" ]
