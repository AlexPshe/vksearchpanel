FROM ubuntu:16.04


# Set the working directory to /app
RUN mkdir /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

EXPOSE 80

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev python3-numpy libicu-dev python3-icu

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN pip3 install --upgrade pip setuptools flask vk_api polyglot pycld2 morfessor elasticsearch-dsl tqdm

RUN python3 download_sentiment.py
CMD python3 app.py
