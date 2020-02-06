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
export AXE_HOST_PREFIX='192.222.1.'
export AXE_CONNECT_TIMEOUT=15
export AXE_IDENTITY_FILE='~/.ssh/id_rsa'
```

如果不设置环境变量，脚本会使用内置默认值。

## Install

执行：

```bash
./install.sh
```

脚本会把当前仓库里的 `axe` 写入 `~/.bashrc` 和 `~/.zshrc` 的 alias。

或者直接安装成命令行包：

```bash
python3 -m pip install .
axe --help
```

## Usage

```text
axe 1
axe 10.10.1.1
axe 2 3 4 -c 'ls -lrt'
axe 2 3 4 -s './test' '/home/astute'
axe 2 3 4 -s './test'
axe --user admin --port 2222 --host-prefix '10.20.30.' --timeout 10 12 -c 'hostname'
axe --identity '~/.ssh/id_rsa' 12
axe --dry-run 2 3 4 -c 'uptime'
axe --jobs 4 2 3 4 -c 'uptime'
```

其中：

- `1` 到 `250` 会被解析为 `192.222.1.x`
- 也支持直接传入 IPv4 地址或域名
- 可以通过 `AXE_HOST_PREFIX` 切换短主机号的网段前缀
- 可以通过 `AXE_CONNECT_TIMEOUT` 调整等待密码提示和连接建立的超时时间
- 可以通过 `AXE_IDENTITY_FILE` 配置私钥登录
- 可以通过 `--dry-run` 先预览将要执行的 SSH/SCP 目标和参数
- 可以通过 `--jobs N` 控制批量命令和批量拷贝的并发数
- 也可以通过 `--user`、`--password`、`--port`、`--host-prefix`、`--timeout`、`--identity`、`--dry-run`、`--jobs` 仅对当前一次执行做覆盖
