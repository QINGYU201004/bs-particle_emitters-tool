import json
import os

def physical_merge_safe(base_path, append_path, output_path):
    """
    1. 读取大文件和小文件的键值
    2. 过滤掉小文件中与大文件重复的键
    3. 物理删除大文件末尾的 '}'，拼接小文件内容
    """
    if not os.path.exists(base_path) or not os.path.exists(append_path):
        print("❌ 错误: 找不到输入文件。")
        return

    try:
        print("🔍 正在扫描大文件的键值...")
        with open(base_path, 'r', encoding='utf-8') as f:
            base_data = json.load(f)
            base_keys = set(base_data.keys())

        print("🔍 正在读取小文件并过滤重复项...")
        with open(append_path, 'r', encoding='utf-8') as f:
            append_data = json.load(f)
            # 只保留大文件里没有的键
            filtered_append = {k: v for k, v in append_data.items() if k not in base_keys}
            
        skipped_count = len(append_data) - len(filtered_append)
        if skipped_count > 0:
            print(f"⚠️ 跳过了 {skipped_count} 个重复的键值对，防止引擎闪退。")

        if not filtered_append:
            print("止步：没有新内容可以添加（全部重复）。")
            return

        # 将过滤后的内容转为字符串，去掉开头和结尾的大括号
        # indent=2 保证格式整齐，ensure_ascii=False 保证中文正常
        append_str = json.dumps(filtered_append, indent=2, ensure_ascii=False)
        # 去掉最外层的 { 和 }
        append_content = append_str.strip().strip('{}').strip()

        print("📝 正在进行物理拼接...")
        with open(base_path, 'r', encoding='utf-8') as f:
            full_content = f.read().strip()

        # 找到大文件最后一个 '}' 的位置并切掉
        if full_content.endswith('}'):
            # 找到最后一个大括号，并确保前面有一个逗号
            base_main = full_content[:full_content.rfind('}')].strip()
            
            # 检查末尾是否有逗号，没有就补一个
            connector = "," if not base_main.endswith(',') else ""
            
            # 组合：[原内容切掉括号] + [逗号] + [新内容] + [新括号]
            final_json = base_main + connector + "\n  " + append_content + "\n}"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_json)
            
            print(f"✨ 物理合并完成！")
            print(f"📂 已保存至: {output_path}")
            
            # 最后验证一下结构
            try:
                json.loads(final_json)
                print("✅ 验证通过：生成的文件结构合法。")
            except Exception as e:
                print(f"❌ 警告：拼接后的结构仍有异常: {e}")
        else:
            print("❌ 错误：基础文件格式似乎不是标准的 JSON（结尾不是 }）。")

    except Exception as e:
        print(f"💥 发生错误: {e}")

if __name__ == "__main__":
    base = input("请输入基础大文件名: ").strip()
    patch = input("请输入待添加的小文件名: ").strip()
    out = input("请输入输出文件名 (例如 final.json): ").strip()
    
    if base and patch and out:
        physical_merge_safe(base, patch, out)
