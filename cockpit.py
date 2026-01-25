from io import StringIO

from pyinfra import host
from pyinfra.facts.files import File
from pyinfra.facts.hardware import NetworkDevices
from pyinfra.operations import apt, files, server, systemd

# qemu-ppc仮想マシン起動スクリプト
qemu_ppc_vm = StringIO(
    """
#!/bin/bash
/usr/bin/qemu-system-ppc \
-name "ppc-vm" \
-machine mac99,via=pmu \
-cpu G4 \
-m 1024 \
-L pc-bios \
-boot c \
-prom-env "boot-device=hd:,\yaboot" \
-prom-env "boot-args=conf=hd:,\yaboot.conf" \
-drive file=/var/lib/libvirt/images/seagate.qcow2,if=ide,index=0,media=disk,format=qcow2 \
-drive file=/var/lib/libvirt/images/wdc.qcow2,if=ide,index=1,media=disk,format=qcow2 \
-vnc :0 \
-vga std \
-g 1024x768x8 \
-netdev bridge,id=net0,br=br0 \
-device rtl8139,netdev=net0 \
-monitor unix:/tmp/qemu-ppc-monitor.sock,server,nowait \
-serial telnet:localhost:4444,server,nowait \
-pidfile /run/qemu-ppc.pid \
-daemonize
"""
)

# qemu-ppc起動ユニットファイル
qemu_ppc = StringIO(
    """
[Unit]
Description=QEMU PPC Virtual Machine
After=network.target

[Service]
Type=forking
# User=root
ExecStart=/usr/local/bin/qemu_ppc_vm.sh
ExecStop=/bin/sh -c "echo 'system_powerdown' | /usr/bin/socat - UNIX-CONNECT:/tmp/qemu-ppc-monitor.sock"
PIDFile=/run/qemu-ppc.pid
TimeoutStopSec=300
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
)


def setup_zram_tools():
    """
    zram-toolsをインストールして設定します
    """
    apt.packages(
        name="zram-toolsをインストール",
        packages=["zram-tools"],
        present=True,
    )

    files.replace(
        name="zramの圧縮方法をzstdに変更",
        path="/etc/default/zramswap",
        text=r"^\(ALGO=\).*",
        replace=r"\1zstd",
    )


def setup_qemu():
    """
    qemu仮想マシンのブリッジ設定と起動を設定します
    """
    files.file(
        name="qemu-bridge-helperを実行可能にする",
        path="/usr/lib/qemu/qemu-bridge-helper",
        mode="755",
    )

    files.file(
        name="/etc/qemu/bridge.confを作成",
        path="/etc/qemu/bridge.conf",
        present=True,
        mode="644",
        create_remote_dir=True,
    )

    files.line(
        name="/etc/qemu/bridge.confにブリッジデバイスを設定する",
        path="/etc/qemu/bridge.conf",
        present=True,
        line="^$",
        replace="allow br0",
    )

    files.template(
        name="qemu起動ファイルを作成",
        src=qemu_ppc_vm,
        dest="/usr/local/bin/qemu_ppc_vm.sh",
        mode="755",
    )

    files.template(
        name="systemdユニットファイルqemu-ppc.serviceを作成",
        src=qemu_ppc,
        dest="/etc/systemd/system/qemu-ppc.service",
    )

    systemd.daemon_reload(name="systemdデーモンをリロード")

    systemd.service(
        name="systemdにqemu-ppc.serviceを登録",
        service="qemu-ppc.service",
        enabled=True,
        running=False,
    )


def setup_bridge(ip, gateway, dns):
    """
    ホスト側のネットワークにブリッジを設定する

    :param ip: IPアドレス
    :param gateway: 説明
    :param dns: 説明
    """

    # https://linuxconfig.org/how-to-use-bridged-networking-with-libvirt-and-kvm
    files.block(
        name="ブリッジのnetfilter解除設定を作成",
        path="/etc/sysctl.d/99-netfilter-bridge.conf",
        present=True,
        content=[
            "net.bridge.bridge-nf-call-ip6tables = 0",
            "net.bridge.bridge-nf-call-iptables = 0",
            "net.bridge.bridge-nf-call-arptables = 0",
            "net.ipv4.ip_forward = 1",
        ],
    )

    files.line(
        name="br_netfilterモジュール読み込み設定を作成",
        path="/etc/modules-load.d/br_netfilter.conf",
        present=True,
        line="^$",
        replace="br_netfilter",
    )

    # ネットワークデバイス名を取得
    network_devices = host.get_fact(NetworkDevices)
    nic = list(network_devices.keys())

    server.shell(
        name="NetworkManagerでブリッジ作成",
        commands=[
            "nmcli con modify '有線接続 1' connection.id eth0",
            "nmcli con add type bridge con-name br0 ifname br0",
            "nmcli con modify br0 bridge.stp no",
            f"nmcli con add type bridge-slave ifname {nic[1]} master br0",
            f"nmcli con modify br0 ipv4.addresses {ip}",
            f"nmcli con modify br0 ipv4.gateway {gateway}",
            f"nmcli con modify br0 ipv4.dns {dns}",
            "nmcli con modify br0 ipv4.method manual",
            "nmcli con del eth0",
            "nmcli con up br0",
            "nmcli con reload",
        ],
    )


def setup_cockpit(ip, gateway, dns):
    """
    cockpitをインストールします
    """

    apt.update(name="aptリポジトリを更新する")
    apt.upgrade(name="パッケージを更新する")

    # cockpitをインストールする
    apt.packages(
        name="cockpit関連パッケージをインストール",
        packages=[
            "cockpit",
            "cockpit-machines",
            "cockpit-podman",
            "qemu-system",
            "qemu-utils",
            "bridge-utils",
            "firmware-linux",
            "ripgrep",
            "lv",
            "realmd",
            "vim",
            "nano",
            "socat",
        ],
        present=True,
    )

    setup_zram_tools()  # zramを設定する
    setup_qemu()  # qemuのVM起動設定をする

    # systemd-networkdで管理するためにinterfacesを無効化する
    interfaces = "/etc/network/interfaces"
    if host.get_fact(File, interfaces):
        server.shell(
            name="/etc/network/interfacesを無効化",
            commands=[f"mv {interfaces} {interfaces}.save"],
        )

    systemd.service(
        name="NetworkManagerを再起動する",
        service="NetworkManager.service",
        restarted=True,
    )

    setup_bridge()  # bridge周りのネットワークを設定をする


# cockpitを設定する setup_cockpit(ip, gateway, dns)
setup_cockpit(
    "192.168.0.200/24",
    "192.168.0.254",
    "192.168.0.253",
)
