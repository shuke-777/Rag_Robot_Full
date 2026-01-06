import os
from zai import ZhipuAiClient
from dotenv import load_dotenv
from config.path_config import RAW_DATA_DIR

load_dotenv()

client = ZhipuAiClient(api_key=os.getenv("ZHIPUAI_API_KEY"))
def handwriting_ocr_example():
    """
    完整示例：提交图片进行识别并等待结果返回。
    """
    # 请修改为本地图片路径
    file_path = RAW_DATA_DIR / 'f3138946e4b4a42b951d86e105411ace.png'
    with open(file_path, 'rb') as f:
        print("正在提交手写识别任务 ...")
        response = client.ocr.handwriting_ocr(
            file=f,
            tool_type="hand_write",
            probability=True
        )
        print("任务创建成功，返回结果如下：")
        print(response)

    print("手写识别示例结束。")


if __name__ == "__main__":
    print("=== 手写识别快速演示 ===\n")
    handwriting_ocr_example()