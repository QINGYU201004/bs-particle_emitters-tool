import csv
import json
import os


def _default_output_path(csv_path, output_path=None):
    if output_path:
        return output_path

    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    file_name = f"{base_name}_name.json"
    return os.path.join(os.path.dirname(os.path.abspath(csv_path)), file_name)


def _unique_non_empty(values):
    seen = set()
    ordered = []

    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)

    return ordered


def extract_particle_emitter_names(csv_path, input_json_path, output_path=None):
    if not os.path.exists(csv_path):
        print(f"❌ 错误: 找不到 CSV 文件 {csv_path}")
        return {"count": 0, "output": None, "missing": 0}

    if not os.path.exists(input_json_path):
        print(f"❌ 错误: 找不到 JSON 文件 {input_json_path}")
        return {"count": 0, "output": None, "missing": 0}

    print("🔍 正在读取 effects.csv 中的 ParticleEmitterName 列...")

    try:
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
    except Exception as e:
        print(f"❌ 错误: 读取 CSV 失败: {e}")
        return {"count": 0, "output": None, "missing": 0}

    if len(rows) < 3:
        print("❌ 错误: CSV 行数不足，至少需要表头行、类型行和数据行。")
        return {"count": 0, "output": None, "missing": 0}

    header = rows[0]
    try:
        emitter_idx = header.index("ParticleEmitterName")
    except ValueError:
        print("❌ 错误: CSV 表头中找不到 ParticleEmitterName 列。")
        return {"count": 0, "output": None, "missing": 0}

    emitter_names = _unique_non_empty(
        row[emitter_idx]
        for row in rows[2:]
        if len(row) > emitter_idx
    )

    if not emitter_names:
        print("❓ 未在 ParticleEmitterName 列中找到可提取的名称。")
        return {"count": 0, "output": None, "missing": 0}

    print("🔍 正在按键名匹配 particle_emitters_old.json...")

    try:
        with open(input_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 错误: 读取 JSON 失败: {e}")
        return {"count": 0, "output": None, "missing": 0}

    if not isinstance(data, dict):
        print("❌ 错误: 输入 JSON 顶层不是对象。")
        return {"count": 0, "output": None, "missing": 0}

    extracted = {}
    missing = []

    for name in emitter_names:
        effect = data.get(name)
        if effect is None:
            missing.append(name)
            continue
        # 保留完整键值数据，不只导出名称列表。
        extracted[name] = effect

    if not extracted:
        print("❓ 没有匹配到任何键名。")
        return {"count": 0, "output": None, "missing": len(missing)}

    final_output = _default_output_path(csv_path, output_path)

    try:
        with open(final_output, "w", encoding="utf-8") as f:
            json.dump(extracted, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ 错误: 保存输出文件失败: {e}")
        return {"count": 0, "output": None, "missing": len(missing)}

    preview = ", ".join(list(extracted.keys())[:5])

    print("✨ 提取完成！")
    print(f"📄 CSV 唯一名称数量: {len(emitter_names)}")
    print(f"✅ 匹配成功数量: {len(extracted)}")
    print(f"❔ 未匹配数量: {len(missing)}")
    print(f"🧩 示例: {preview}")
    print(f"📂 已保存至: {final_output}")

    if missing:
        print(f"⚠️ 未匹配示例: {', '.join(missing[:10])}")

    return {"count": len(extracted), "output": final_output, "missing": len(missing)}


if __name__ == "__main__":
    csv_path = input("输入 CSV 文件 (effects.csv): ").strip() or "effects.csv"
    json_path = input("输入 JSON 文件 (particle_emitters_old.json): ").strip() or "particle_emitters_old.json"
    output_path = input("输出文件 (默认自动命名): ").strip() or None
    extract_particle_emitter_names(csv_path, json_path, output_path)
