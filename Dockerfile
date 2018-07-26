FROM python:3.5

# Install python dependencies.
RUN pip3 install --no-cache-dir --upgrade \
         python-crontab==2.3              \
         requests==2.19

# Install dependencies
RUN apt-get update && apt-get install -y git build-essential libssl-dev zlib1g-dev cron

# Build MTProto
EXPOSE 443
RUN mkdir /server && cd /server                            && \
    git clone https://github.com/TelegramMessenger/MTProxy . && \
    make && cd ./objs/bin

# Clean up after installation.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy source files and create working directories.
COPY src /src
CMD ["/src/entry.sh"]
