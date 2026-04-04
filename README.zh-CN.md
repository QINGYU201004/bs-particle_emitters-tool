# bs-particle_emitters-tool

一个用于处理 `particle_emitters` JSON 文件的命令行工具集。

## 功能

- 修复宽松/非标准 JSON 格式，并输出排序后的美化 JSON。
- 将新版粒子发射器格式转换为旧版兼容格式。
- 按特效键名与 `movieclip`（`swf` / `name`）关键词进行搜索提取。
- 从 `movieclip.swf` 提取唯一 SC 名，并导出为带表头的 CSV 文件。
- 安全合并 JSON，自动跳过重复键，减少冲突风险。
- 菜单支持多语言：英语、中文、俄语。

## 环境要求

- Python 3.8+

## 快速开始

```bash
python3 main.py
```

启动后在菜单中选择功能：

- `1`：修复 JSON（`fix.py`）
- `2`：新版转旧版（`old.py`）
- `3`：搜索/提取特效（`search.py`）
- `4`：物理合并 JSON（`add.py`）
- `5`：切换语言
- `6`：提取 `movieclip.swf` 的 SC 名（`sc_extract.py`）

## 项目结构

```text
.
├── main.py
└── lib
    ├── add.py
    ├── fix.py
    ├── language.py
    ├── old.py
    ├── sc_extract.py
    └── search.py
```

## 说明

- 输出文件名可在 CLI 提示时自定义。
- 处理大体积 JSON 时，耗时与设备性能有关。

## 许可证

当前仓库尚未附带许可证文件。
