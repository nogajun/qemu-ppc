#!/bin/bash

# エラーハンドリング: エラーがあったら終了
set -e

# Websockifyをバックグラウンドで起動
# localhost:5900 (QEMUのVNC) <---> 0.0.0.0:6080 (ブラウザアクセス)
# --web=/usr/share/novnc でnovncのHTMLファイル配信場所を指定
echo "Starting websockify on port 6080..."
websockify 6080 localhost:5900 --web=/usr/share/novnc &

# 少し待機してwebsockifyの準備を確実にする（必須ではないが安定のため）
sleep 1

# 渡された引数 ($@) を使ってQEMUを起動
# 必ず VNCオプション (-vnc 127.0.0.1:0) を末尾に追加して、
# QEMUがlocalhostの5900番で待ち受けるようにします
echo "Starting QEMU-PPC with options: $@"

# 注意: ユーザーが自分で -vnc を指定した場合、QEMUは通常最後のオプションを優先します。
# ここではコンテナ内の通信に合わせて末尾に固定で追加しています。
qemu-system-ppc "$@" -vnc 127.0.0.1:0
