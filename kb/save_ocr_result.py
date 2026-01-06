import os
import json
from zai import ZhipuAiClient
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

load_dotenv()
client = ZhipuAiClient(api_key=os.getenv("ZHIPUAI_API_KEY"))


def save_ocr_result():
    """
    OCR识别并保存结果到JSON文件
    """
    # 图片路径
    file_path = '/private项目/rag-chatbot/data/raw_data/f3138946e4b4a42b951d86e105411ace.png'

    # 执行OCR
    print("正在提交手写识别任务...")
    with open(file_path, 'rb') as f:
        response = client.ocr.handwriting_ocr(
            file=f,
            tool_type="hand_write",
            probability=True,
            language_type='ENG'
        )

    print(f"识别成功！识别到 {response.words_result_num} 个文本区域\n")

    # 转换为可保存的字典格式
    result_dict = {
        "task_id": response.task_id,
        "message": response.message,
        "status": response.status,
        "words_result_num": response.words_result_num,
        "image_path": file_path,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "words_result": []
    }

    # 提取每个文本块的信息
    for idx, word_result in enumerate(response.words_result, 1):
        word_dict = {
            "index": idx,
            "location": {
                "left": word_result.location.left,
                "top": word_result.location.top,
                "width": word_result.location.width,
                "height": word_result.location.height
            },
            "words": word_result.words,
            "probability": {
                "average": word_result.probability.average,
                "variance": word_result.probability.variance,
                "min": word_result.probability.min
            }
        }
        result_dict["words_result"].append(word_dict)

    # 保存到JSON文件
    output_dir = Path("/private项目/rag-chatbot/data/ocr_results")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"ocr_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2)

    print(f"✅ OCR结果已保存到: {output_file}\n")

    # 同时保存一个纯文本版本（只包含识别的文字）
    text_file = output_dir / f"ocr_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        for idx, word_result in enumerate(response.words_result, 1):
            f.write(f"{idx}. {word_result.words}\n")

    print(f"✅ 纯文本版本已保存到: {text_file}\n")

    # 打印一些统计信息
    print("=" * 60)
    print("OCR 识别统计")
    print("=" * 60)
    print(f"识别文本块数量: {response.words_result_num}")

    avg_confidence = sum(w.probability.average for w in response.words_result) / len(response.words_result)
    print(f"平均置信度: {avg_confidence:.2%}")

    high_conf = sum(1 for w in response.words_result if w.probability.average > 0.95)
    print(f"高置信度块数 (>95%): {high_conf} ({high_conf/len(response.words_result)*100:.1f}%)")

    low_conf = sum(1 for w in response.words_result if w.probability.average < 0.80)
    print(f"低置信度块数 (<80%): {low_conf} ({low_conf/len(response.words_result)*100:.1f}%)")
    print("=" * 60)

    # 打印前5个识别结果作为示例
    print("\n前5个识别结果示例:")
    for idx, word_result in enumerate(response.words_result[:5], 1):
        print(f"\n[{idx}] 位置: ({word_result.location.left}, {word_result.location.top})")
        print(f"    内容: {word_result.words}")
        print(f"    置信度: {word_result.probability.average:.2%}")

    return output_file


if __name__ == "__main__":
    print("=== OCR 识别并保存结果 ===\n")
    output_path = save_ocr_result()
    print(f"\n完成！结果已保存到: {output_path}")
