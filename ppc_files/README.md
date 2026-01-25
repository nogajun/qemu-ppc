# libvirt用ファイル（未使用）

これはlibvirt用XMLファイルです。
libvirtが、x86系以外はまともに対応しないので使いませんでした。

- `ppc32-debian5.xml`: PowerPCマシン登録用XML
- `bridged-network.xml`: ブリッジネットワーク設定用XML

使い方は次のような形で登録します。

```console
sudo virsh define ppc32-debian5.xml
sudo virsh net-define bridged-network.xml
```
