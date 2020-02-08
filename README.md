# axe

`axe` 是一个基于 `pexpect` 的批量 SSH/SCP 命令行工具，适合一组机器共享相同登录方式时快速执行登录、批量命令和批量文件分发。

它支持：

- 单主机 SSH 登录
- 多主机批量执行命令
- 多主机批量 SCP
- 环境变量和命令行参数覆盖连接配置
- 私钥登录
- `--dry-run` 预览
- `--jobs N` 并发执行

## Requirements

- `python3`
- 本机可用的 `ssh` 和 `scp`

## Install

直接在仓库里运行：

```bash
./install.sh
```

这会把当前仓库中的 `axe` 写入 `~/.bashrc` 和 `~/.zshrc` 的 alias。

也可以安装成标准命令行包：

```bash
python3 -m pip install .
axe --help
```

## Quick Start

```bash
axe 1
axe 10.10.1.1
axe 2 3 4 -c 'uptime'
axe 2 3 4 -s './app.tar.gz' '/srv/app/'
```

默认规则：

- `1` 到 `250` 会被解析为 `192.222.1.x`
- 也支持直接传入 IPv4 地址或域名

## Configuration

默认配置来自环境变量：

```bash
export AXE_USER=root
export AXE_PASSWORD='donotuseroot!'
export AXE_PORT=22
export AXE_HOST_PREFIX='192.222.1.'
export AXE_CONNECT_TIMEOUT=15
export AXE_IDENTITY_FILE='~/.ssh/id_rsa'
```

说明：

- `AXE_USER`：登录用户名
- `AXE_PASSWORD`：密码登录时使用的密码
- `AXE_PORT`：SSH 端口
- `AXE_HOST_PREFIX`：短主机号前缀，例如 `192.222.1.`
- `AXE_CONNECT_TIMEOUT`：等待连接和密码提示的超时时间，单位秒
- `AXE_IDENTITY_FILE`：私钥路径，可选

命令行参数会覆盖环境变量，仅对当前一次执行生效。

## Usage

### SSH 登录

```bash
axe 1
axe example.com
axe --identity '~/.ssh/id_rsa' 12
```

### 批量执行命令

```bash
axe 2 3 4 -c 'hostname'
axe --jobs 4 2 3 4 -c 'uptime'
axe --dry-run 2 3 4 -c 'systemctl status nginx'
```

### 批量拷贝文件

```bash
axe 2 3 4 -s './test'
axe 2 3 4 -s './test' '/home/admin/'
axe --jobs 3 2 3 4 -s './build.tar.gz' '/srv/app/'
```

当 `-s` 只给一个源路径时，会默认拷贝到远端相同目录。

## Runtime Overrides

下面这些参数可以覆盖默认连接配置：

```bash
axe --user admin --port 2222 --host-prefix '10.20.30.' --timeout 10 12 -c 'hostname'
```

支持的覆盖参数：

- `--user`
- `--password`
- `--port`
- `--host-prefix`
- `--timeout`
- `--identity`
- `--dry-run`
- `--jobs`

## Notes

- `--dry-run` 只输出将要执行的目标和参数，不会真的连接远端。
- `--jobs N` 只作用于批量 `-c` 和 `-s` 场景。
- 批量执行结束后会输出成功/失败汇总。
- 如果远端仍要求密码，工具会继续按当前配置尝试密码交互。
