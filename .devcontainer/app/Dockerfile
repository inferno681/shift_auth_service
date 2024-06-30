FROM debian:bookworm

ENV TERM xterm

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    libgl1-mesa-glx \
    libglib2.0-dev

# Настройки темы https://github.com/romkatv/powerlevel10k
COPY .p10k.zsh /root/
COPY .zshrc /root/
