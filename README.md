# axe

基于 `pexpect` 的批量 SSH/SCP 小工具，适用于多台服务器共用同一组用户名、密码和端口的场景。

## Requirements

- `python3`
- 本机可用的 `ssh` 和 `scp`

## Configuration

默认配置如下：

```bash
export AXE_USER=root
export AXE_PASSWORD='donotuseroot!'
export AXE_PORT=22
```

如果不设置环境变量，脚本会使用内置默认值。

## Install

执行：

```bash
./install.sh
```

脚本会把当前仓库里的 `axe` 写入 `~/.bashrc` 和 `~/.zshrc` 的 alias。

## Usage

```text
axe 1
axe 10.10.1.1
axe 2 3 4 -c 'ls -lrt'
axe 2 3 4 -s './test' '/home/astute'
axe 2 3 4 -s './test'
```

其中：

- `1` 到 `250` 会被解析为 `192.222.1.x`
- 也支持直接传入 IPv4 地址或域名
