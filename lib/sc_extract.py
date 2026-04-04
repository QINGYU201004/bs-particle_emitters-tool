import csv
import json
import os


def _safe_output_path(input_path, output_path=None):
    if output_path:
        return output_path

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    file_name = f"{base_name}_movieclip_sc_names.csv"
    return os.path.join(os.path.dirname(os.path.abspath(input_path)), file_name)


def _extract_sc_parts(raw_swf):
    if not raw_swf:
        return "", ""

    normalized = str(raw_swf).replace("\\", "/").strip()
    if not normalized:
        return "", ""

    sc_file = os.path.basename(normalized)
    sc_name, _ = os.path.splitext(sc_file)
    return sc_name, normalized


def extract_movieclip_sc_names(input_path, output_path=None):
    if not os.path.exists(input_path):
        print(f"❌ 错误: 找不到输入文件 {input_path}")
        return {"count": 0, "output": None}

    print("🔍 正在提取 movieclip.swf 中的 SC 名...")

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 错误: 读取或解析文件失败: {e}")
        return {"count": 0, "output": None}

    if not isinstance(data, dict):
        print("❌ 错误: 输入 JSON 顶层不是对象。")
        return {"count": 0, "output": None}

    sc_map = {}
    total_refs = 0

    for effect in data.values():
        if not isinstance(effect, dict):
            continue

        clips = effect.get("movieclip", [])
        if not isinstance(clips, list):
            continue

        for clip in clips:
            if not isinstance(clip, dict):
                continue

            sc_name, swf_path = _extract_sc_parts(clip.get("swf"))
            if not sc_name:
                continue

            total_refs += 1
            item = sc_map.setdefault(
                sc_name,
                {
                    "count": 0,
                    "swf_path": swf_path,
                },
            )
            item["count"] += 1

    if not sc_map:
        print("❓ 未找到任何带 movieclip.swf 的 SC 名。")
        return {"count": 0, "output": None}

    final_output = _safe_output_path(input_path, output_path)
    try:
        with open(final_output, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["sc_name", "count", "swf_path"])

            for sc_name in sorted(sc_map):
                info = sc_map[sc_name]
                writer.writerow([sc_name, info["count"], info["swf_path"]])
    except Exception as e:
        print(f"❌ 错误: 保存输出文件失败: {e}")
        return {"count": 0, "output": None}

    preview = ", ".join(sorted(sc_map)[:5])

    print("✨ 提取完成！")
    print(f"📊 唯一 SC 名数量: {len(sc_map)}")
    print(f"🎞️ movieclip.swf 引用总数: {total_refs}")
    print(f"🧩 示例: {preview}")
    print(f"📂 已保存至: {final_output}")
    return {"count": len(sc_map), "output": final_output}


if __name__ == "__main__":
    src = input("输入源文件 (particle_emitters_old.json): ").strip() or "particle_emitters_old.json"
    out = input("输出文件 (默认自动命名): ").strip() or None
    extract_movieclip_sc_names(src, out)
