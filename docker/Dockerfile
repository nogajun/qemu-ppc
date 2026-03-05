FROM debian:trixie-slim

LABEL version="1.0"
LABEL maintainer="nogata@gm.himeji-du.ac.jp"
LABEL description="Docker container for running qemu-ppc."

# インタラクティブなインストールを回避
ENV DEBIAN_FRONTEND=noninteractive

# 必要なパッケージのインストール
# qemu-system-ppc: PPCエミュレータ
# websockify: WebSocket<->TCPブリッジ
# novnc: ブラウザ用VNCクライアント
RUN apt-get update && apt-get install -y \
  qemu-system-ppc \
  qemu-utils \
  websockify \
  novnc \
  && rm -rf /var/lib/apt/lists/*

# エントリーポイントスクリプトの配置
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# noVNC用ポート (6080) を公開
EXPOSE 6080

# エントリーポイント設定
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
