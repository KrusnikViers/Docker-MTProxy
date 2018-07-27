FROM python:3-slim

# Install dependencies.
# Clone MTProto server and build it from sources.
# Remove temporary files, source files, and dependencies that was needed only for building.
RUN pip3 install --no-cache-dir --upgrade python-crontab==2.3 requests==2.19 && \
    apt-get update                                                           && \
    apt-get install -y git build-essential libssl-dev zlib1g-dev cron curl   && \
    mkdir /build                                                             && \
    cd /build                                                                && \
    git clone https://github.com/TelegramMessenger/MTProxy .                 && \
    git reset --hard f9158e3129efd4ccdc291aefb840209791226a77                && \
    make                                                                     && \
    mkdir /server                                                            && \
    cp /build/objs/bin/* /server                                             && \
    cd /server                                                               && \
    rm -rf /build                                                            && \
    apt-get purge -y git build-essential libssl-dev zlib1g-dev               && \
    apt-get autoremove -y                                                    && \
    apt-get clean                                                            && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 443
COPY src /src
CMD ["/src/entry.sh"]
