FROM ubuntu:latest

# Update the package list and install the necessary packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    iproute2 \
    iputils-ping \
    traceroute \
    iperf \
    vim \
    wget \
    make \
    gcc \
    build-essential \
    tcpdump \
    python3 \
    tmux \
    iperf3 \
    apache2 \
    apache2-bin \
    apt-utils \
    apt-transport-https \
    arping \
    arptables \
    bind9 \
    bind9-utils \
    bison \
    bridge-utils \
    build-essential \
    curl \
    diffutils \
    dnsutils \
    dublin-traceroute  \
    ethtool \
    expect \
    flex \
    geoip-database \
    git \
    gnupg \
    hping3 \
    ieee-data \
    ifupdown \
    iperf3 \
    iptables \
    iputils-ping \
    iputils-tracepath \
    less \
    libdublintraceroute-dev \
    libjsoncpp-dev \
    libpcap-dev \
    libtins-dev \
    links \
    lsb-base \
    lsb-release \
    make \
    man-db \
    mtr \
    nano \
    ndisc6 \
    net-tools \
    netbase \
    netcat-openbsd \
    openssh-client \
    openssh-server \
    openssh-sftp-server \
    openssl \
    pkg-config \
    python3-dev \
    python3-pip \
    radvd \
    rsync \
    screen \
    sed \
    tar \
    tcpdump \
    telnet \
    tmux \
    traceroute \
    wget \
    vim


# # From Kathara/base image
# RUN apt install -y \
#     apache2 \
#     apache2-bin \
#     apt-utils \
#     apt-transport-https \
#     arping \
#     arptables \
#     bind9 \
#     bind9-utils \
#     bison \
#     bridge-utils \
#     build-essential \
#     curl \
#     diffutils \
#     dnsutils \
#     dublin-traceroute  \
#     ethtool \
#     expect \
#     flex \
#     geoip-database \
#     git \
#     gnupg \
#     hping3 \
#     ieee-data \
#     ifupdown \
#     iperf3 \
#     iptables \
#     iputils-ping \
#     iputils-tracepath \
#     less \
#     libdublintraceroute-dev \
#     libjsoncpp-dev \
#     libpcap-dev \
#     libtins-dev \
#     links \
#     lsb-base \
#     lsb-release \
#     make \
#     man-db \
#     mtr \
#     nano \
#     ndisc6 \
#     net-tools \
#     netbase \
#     netcat-openbsd \
#     openssh-client \
#     openssh-server \
#     openssh-sftp-server \
#     openssl \
#     pkg-config \
#     python3-dev \
#     python3-pip \
#     radvd \
#     rsync \
#     screen \
#     sed \
#     systemd-userdbd \
#     tar \
#     tcpdump \
#     telnet \
#     tmux \
#     traceroute \
#     wget \
#     vim


# Install Pathneck
# RUN wget http://www.cs.cmu.edu/~hnn/pathneck/pathneck-1.3.tgz && \
#     tar -xf pathneck-1.3.tgz && \
#     cd pathneck-1.3 && \
#     make

#Install PTR
# RUN wget http://www.cs.cmu.edu/~hnn/igi/igi-ptr-2.1.tgz && \
#     tar -xf igi-ptr-2.1.tgz && \
#     cd igi-ptr-2.1 && \
#     make
#Clone modified PTR
#call 'docker builder prune' to delete cached repository
# RUN git clone https://github.com/ycjoung0829/igi-ptr-2.1.git && \
#     cd igi-ptr-2.1 && \
#     make

COPY /igi-ptr-2.1 /igi-ptr-2.1
RUN cd igi-ptr-2.1 && \
    make
COPY .bashrc /root/.bashrc
COPY .tmux.conf /root/.tmux.conf


# Start a shell and keep the container running
CMD ["tail", "-f", "/dev/null"]
