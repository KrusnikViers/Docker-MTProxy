FROM python:3-slim

# Install dependencies.
# Build MTProto Proxy itself.
# Clean everything after installations.
RUN pip3 install --no-cache-dir --upgrade python-crontab==2.3 requests==2.19 && \
    apt-get update                                                           && \
    apt-get install -y git build-essential libssl-dev zlib1g-dev cron        && \
    mkdir /server                                                            && \
    cd /server                                                               && \
    git clone https://github.com/TelegramMessenger/MTProxy .                 && \
    make                                                                     && \
    apt-get clean                                                            && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 443
COPY src /src
CMD ["/src/entry.sh"]
