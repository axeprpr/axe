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

从当前版本开始，`pexpect` 作为外部依赖提供，不再 vendoring 到仓库中。

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

如果你在系统包环境中安装 `.deb` 或 `.rpm`，对应包会声明 `python3-pexpect` 依赖，而不是把第三方源码直接打进项目源码目录。

如果你需要在离线环境里部署，也可以使用发布流程生成的离线 `tar.gz` 包。它会把 Python 依赖一起打进去，但目标机器仍需要可用的 `python3`。

## Release

仓库现在包含 GitHub Actions：

- `CI`：在 `push` 和 `pull_request` 时运行测试并验证 Python 构建
- `Release`：在推送 `v*` tag 时自动构建发布产物

发布流程会生成：

- Python `sdist`
- Python `wheel`
- `.deb` 包
- `.rpm` 包
- 离线自包含 `tar.gz` 包

Linux 包发布会输出常见架构标签：

- Debian: `amd64`, `arm64`
- RPM: `x86_64`, `aarch64`

版本变化记录见 [CHANGELOG.md](./CHANGELOG.md)。

触发方式示例：

```bash
git tag v0.1.1
git push origin v0.1.1
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
export AXE_PASSWORD='your-password'
export AXE_PORT=22
export AXE_HOST_PREFIX='192.222.1.'
export AXE_CONNECT_TIMEOUT=15
export AXE_IDENTITY_FILE='~/.ssh/id_rsa'
```

说明：

- `AXE_USER`：登录用户名
- `AXE_PASSWORD`：密码登录时使用的密码，不提供时不会自动发送空密码
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

## Common Scenarios

### 登录单台短主机号机器

```bash
axe 12
```

等价于连接：

```text
ssh $AXE_USER@192.222.1.12 -p $AXE_PORT
```

### 给一组机器执行同一条巡检命令

```bash
axe 2 3 4 5 -c 'uptime'
```

### 先预览，再真正执行批量命令

```bash
axe --dry-run 2 3 4 -c 'df -h'
axe 2 3 4 -c 'df -h'
```

### 通过私钥连接一组机器

```bash
axe --identity '~/.ssh/id_rsa' 2 3 4 -c 'hostname'
```

### 并发分发构建产物

```bash
axe --jobs 4 2 3 4 5 -s './release.tar.gz' '/srv/app/'
```

## Notes

- `--dry-run` 只输出将要执行的目标和参数，不会真的连接远端。
- `--jobs N` 只作用于批量 `-c` 和 `-s` 场景。
- 批量执行结束后会输出成功/失败汇总。
- 如果远端仍要求密码，工具会继续按当前配置尝试密码交互。
- 不再提供任何内置默认密码，需要显式设置 `AXE_PASSWORD` 或传入 `--password`。

## FAQ

### 为什么 `axe 12` 会连到 `192.222.1.12`？

因为默认会把 `1` 到 `250` 的短主机号拼接到 `AXE_HOST_PREFIX` 后面。默认前缀是 `192.222.1.`。

### 如果我想换成别的网段前缀怎么办？

设置环境变量或命令行参数：

```bash
export AXE_HOST_PREFIX='10.20.30.'
axe 12
```

或者：

```bash
axe --host-prefix '10.20.30.' 12
```

### 如果我不想真的执行，只想看会发生什么？

使用 `--dry-run`：

```bash
axe --dry-run 2 3 4 -c 'systemctl restart nginx'
```

### 如果批量机器很多，执行太慢怎么办？

可以提高并发数：

```bash
axe --jobs 8 2 3 4 5 6 7 8 9 -c 'uptime'
```

### 支持密码和私钥混用吗？

可以。配置了 `--identity` 或 `AXE_IDENTITY_FILE` 时会优先带上私钥；如果远端仍然要求密码，工具会继续处理密码交互。
