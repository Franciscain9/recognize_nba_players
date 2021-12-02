FROM joyzoursky/python-chromedriver:3.8-selenium
WORKDIR /app
COPY . .
RUN mkdir images \
    && pip install --upgrade pip \
    && pip install -r requirements.txt
CMD python3 ./src/main.py