# qemu-ppc仮想マシンを動かすためのホスト設定スクリプト

## これはなに?

これは、qemu-ppc仮想マシンを動かすためのセットアップスクリプトです。
[pyinfra](https://pyinfra.com/)で書かれているので、Python環境が必要です。

## 使い方

スクリプトは、Linux環境で動かすことを想定しています。

スクリプトを使用するためのパッケージなどをインストールします。また、Python環境には、uvを使っているので[uv](https://pyinfra.com/)もインストールします。

```bash
sudo apt -U install pipx python3-all python-is-python3 git extrepo
sudo sed -i 's/^# \(-.*\)/\1/g' /etc/extrepo/config.yaml
sudo extrepo update
sudo extrepo enable uv
sudo apt -U install uv
```

Pythonやuvをインストールしたら、このリポジトリをCloneして`uv sync`を実行すると環境は揃います。

```bash
git clone
uv sync  # Pythonのライブラリなどをインストール
```

`.env.example`というファイルがあるので、これを`.env`にコピーして、セットアップするホストマシンで作業するユーザーやSSH鍵などの情報などを編集します。

```bash
cp .env.example .env
nano .env   # ホストマシンの情報などを編集
```

編集が終わったら、スクリプトを実行しますが、実行前にvenvを有効にしてから、pyinfraを実行します。

```bash
. .venv/bin/activate
pyinfra -y inventory.py cockpit.py
```
