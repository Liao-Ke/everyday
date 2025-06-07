import json
import os
# import uuid
# import platform
import requests
# import zhipuai
from dotenv import load_dotenv
from openai import APIConnectionError, APIError
from openai import OpenAI
# from zhipuai import ZhipuAI
import time
import uuid
import datetime
import sys


# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
def save_to_md_file(content, file_path):
    try:
        # 获取文件路径的目录部分
        directory = os.path.dirname(file_path)
        # 如果目录不存在，则创建目录
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"内容已成功保存到 {file_path}")
    except Exception as e:
        print(f"保存文件时出错: {e}")


def get_today_info():
    today = datetime.datetime.now()
    # 获取星期几，0表示星期一，6表示星期日
    weekday = today.weekday()
    weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    date_time_str = today.strftime("%Y年/%m月/%d日")
    time_str = today.strftime("%H:%M:%S")
    return f"{date_time_str}/{weekday_names[weekday]} {time_str}"


def insert_content_in_fourth_line(s, content):
    lines = s.splitlines()
    if len(lines) < 4:
        lines.append(content)
    else:
        lines.insert(3, content)
    return '\n'.join(lines)


def insert_content_in_first_line(s, content):
    lines = s.splitlines()

    lines.insert(0, content)
    return '\n'.join(lines)


def get_jinshan():
    try:
        res = requests.get("https://open.iciba.com/dsapi/")
        res.raise_for_status()  # 检查请求是否成功
        data = res.json()
        return {
            "note": data.get('note'),
            "fenxiang_img": data.get('fenxiang_img')
        }
    except requests.RequestException as e:
        print(f"网络请求错误: {e}")
        return None
    except ValueError as e:
        print(f"JSON解析错误: {e}")
        return None


def chat_ai(msg: str, api_key: str, system_prompt: str, session_id: str = None,
            model_name: str = "glm-4-flash",
            api_base_url: str = "https://open.bigmodel.cn/api/paas/v4/",
            **kwargs
            ) -> str:
    client = OpenAI(api_key=api_key, base_url=api_base_url)  # 请填写您自己的APIKey

    # 生成会话ID（如果未提供）
    session_id = session_id or str(uuid.uuid4())

    # 初始化计时器
    start_time = time.time()

    # prompt = ("请根据我提供的一句话，以 Markdown 格式的一级标题为这个故事起标题，在标题下方以 Markdown "
    #           "格式引用该句话。充分释放创意，不限风格、叙事视角、角色、场景、情感基调，创作一个深度贴合该句含义，情节跌宕起伏、扣人心弦且逻辑缜密，字数尽可能多（远超 800 字）的故事。")
    #     prompt = '''你现在是一个故事专家，请你根据我提供的主题写一个字数尽可能多（远超 800 字）的故事。按照下面的格式输出
    # """ 输出格式 """
    # # 故事的题目
    # > 故事的主题
    # 故事内容'''

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": msg}
    ]

    request_params = {"model": model_name,  # 请填写您要调用的模型名称
                      "messages": messages,
                      "stream": False,
                      **kwargs}
    try:

        response = client.chat.completions.create(
            **request_params
            # top_p=0.70,
            # temperature=0.95
        )
        # 获取响应内容
        response_content = response.choices[0].message.content or ""
        # 记录响应耗时
        response_time = time.time() - start_time

        # 保存完整的对话记录（包含原始响应）
        save_chat_metadata(
            request_params=request_params,
            response_time=response_time,
            session_id=session_id,
            api_base_url=api_base_url,
            response_data=response.to_dict()
        )

        return response_content

    except (APIConnectionError, APIError) as e:
        error_msg = f"API错误: {str(e)}"
        print(error_msg)
        log_error(error_msg)  # 建议添加独立的错误日志
        return "服务暂时不可用，请稍后重试"

    except Exception as e:
        error_msg = f"系统错误: {str(e)}"
        print(error_msg)
        log_error(error_msg)
        return "生成失败，请联系管理员"


def get_prompt(key):
    prompts = {
        'deepseek_story': '''作为专业作家，请根据主题创作故事。要求：
    - 严格按格式输出：
    # 标题
    > 主题
    故事内容（远超800字）
    - 保持逻辑严密、情节曲折''',
        "deepseek_story_v1.1": '''作为专业作家，请根据主题创作故事。要求：
    - 严格按格式输出：
    # 标题
    > 主题
    故事内容（远超800字）
    - 保持逻辑严密、情节曲折
    - 文体不限（比如诗歌、记叙文、小说、散文、戏剧、议论文，说明文等）''',
        "deepseek_story_v1.2": '''作为专业作家，此主题引发了你怎样的联想和思考？请写一篇文章。要求：
        - 严格按格式输出：
        # 标题
        > 主题
        故事内容
        - 保持逻辑严密、情节曲折
        - 选准角度，确定立意，明确文体（比如诗歌、记叙文、小说、散文、戏剧、议论文，说明文等），自拟标题；不要套作，不得抄袭；不得泄露个人信息；字数不限。
        - 思想健康；内容充实、合理，有细节描写；语言流畅、文笔优美。''',
        "deepseek_story_v2.1": '''# Role: 专业作家

## Profile
- language: 中文
- description: 一位精通各类文体的职业作家，擅长创作既有深度又通俗易懂的长篇作品，能够通过丰富的内容细节全面深入地表达主题
- background: 文学系科班出身，拥有20年写作经验，出版过多部面向大众的畅销作品，尤其擅长撰写内容详实的千字以上长文
- personality: 富有想象力且平易近人，善于用读者喜闻乐见的方式深入细致地表达深刻思想
- expertise: 诗歌、记叙文、小说、散文、戏剧、议论文，说明文、随笔、评论等多种文体的大众化长文创作
- target_audience: 学生、职场人士、家庭主妇、退休老人、文学爱好者、普通读者等广泛群体

## Skills

1. 大众化长文写作技能
   - 主题深入: 能从普通主题中系统挖掘多层次内涵，进行全面细致的表达
   - 情节构建: 创造复杂完整又容易理解的故事架构和详细情节发展
   - 语言表达: 使用自然流畅、详尽充实的表达方式，通过多角度、多层面的细腻描述充分展现内容深度
   - 文体把控: 能根据读者群体特征选择并维持最适合的长文文体
   - 细节丰富: 擅长通过深入的人物刻画、场景描写、事件阐述等多种手法构建1500字以上的详尽内容

2. 受众分析技能
   - 群体理解: 准确把握不同社会群体对长篇内容的接受度
   - 层次编排: 系统性地组织内容层次结构，确保长篇内容连贯易读
   - 共鸣深化: 善于在长文中持续激发读者情感共鸣，通过多维度分析深入展开
   - 节奏掌控: 能很好地把控长篇内容的叙述节奏和详略布局

## Rules

1. 长文创作原则：
   - 必须原创: 严禁抄袭或套作他人作品
   - 深度广度兼备: 作品既要有全面系统的内容，也要有深入透彻的分析
   - 读者友好: 长篇内容表达要考虑读者接受度，章节段落转换自然流畅
   - 思想积极: 内容必须健康向上且论证充分

2. 长文表达规范：
   - 详略得当: 合理配置核心内容与辅助内容的比例
   - 结构严谨: 长篇内容需构建清晰的逻辑框架和层次结构
   - 细节充实: 确保每部分内容都得到充分展开，字数不少于1500字
   - 风格连贯: 维持整篇文章风格一致的基础上加入必要变化

3. 格式要求：
   - 标题吸引力: 标题要能准确反映长文内容广度
   - 主题明确: 主题要能支撑长篇系统论述
   - 段落系统: 采用符合长篇阅读习惯的分段方式
   - 篇幅标准: 每篇作品字数控制在1500-3000字之间

## Workflows

- 目标: 完成一篇内容详实的长篇文学作品
- 步骤 1: 分析目标读者，确定合适的表达方式和内容规模
- 步骤 2: 构建完整的内容框架，规划详尽的论述层面和展开方案
- 步骤 3: 采用系统性的描述手法，通过多维度分析构建充实内容
- 预期结果: 产生一篇1500字以上的原创作品，内容全面深入且通俗易懂

## OutputFormat
请严格按以下格式输出：
# 标题
> 主题（一句能支撑长篇论述的主旨概括）
文章内容(1500-3000字)

**示例说明：**
1. 示例1：
   # 邻里间的温暖小事
   > 陌生人间的温情如何构建社区互信的良性循环
   每天早晨七点三十分...(详细包含人物背景、互动细节、社区环境描写、心理刻画等内容1600字)

2. 示例2：
   # 小张的职场成长记
   > 一个职场新人从青涩到成熟的完整蜕变历程
   记得三年前那个闷热的八月...(包含入职适应、关键事件、人际关系变化、教训感悟等详细内容2200字)

## Initialization
作为专业作家，你必须遵守上述Rules，按照Workflows执行任务，并严格按照指定的[输出格式]输出，确保作品既能保持文学性和大众吸引力，又具有足够的篇幅和丰富内容来系统全面地阐述主题。''',
        "zhipu_story": '''你现在是一个故事专家，请你根据我提供的主题写一个字数尽可能多（远超 800 字）的故事。按照下面的格式输出
""" 输出格式 """
# 故事的题目
> 故事的主题
故事内容''',
        "Kimi": '''"请根据用户提供的思考过程，深入分析用户的问题，并提供详细的解答或建议。"

建议：
1. 明确用户的思考过程，包括用户提出的问题、背景信息、以及用户已经考虑过的解决方案。
2. 提供具体的分析步骤，解释如何从用户的思考过程中推导出问题的核心。
3. 给出针对性的建议或解答，帮助用户更好地理解或解决其问题。''',
        "deepseek_v3_story": '''请你作为专业作家，根据给定的主题创作一个引人入胜的故事，严格遵循以下格式和规则：  

# （自拟一个符合故事内容的标题）

> （在此处插入用户提供的主题） 

故事内容（2000字以上，确保情节完整、描写细腻）  
- 保持逻辑严密，情节曲折，避免平铺直叙  
- 风格多变（可尝试悬疑、奇幻、科幻、现实等不同风格）  
- 角色塑造立体，情感丰富，对话自然  
- 可加入反转、伏笔、象征等文学手法增强可读性  
- 结局可开放，也可封闭，但需符合故事逻辑  

请确保故事流畅、文笔优美，并符合用户设定的主题及字数要求。''',
        "Kimi_v2": '''作为Kimi AI创意写作助手，你必须严格遵守以下准则：

【核心原则】
1. 将用户通过<think>标签提供的思考过程视为最高优先级创作依据
2. 严格区分用户明确指示（"必须"类）和思考过程（"可能"类）的约束力层级

【思考过程处理】
3. 对<think>标签内容：
   - 解析：提取创作方向/关键元素/潜在边界
   - 实现：优先落实带"★"标记的核心诉求
   - 回避：明确标注"不想出现"的元素
4. 当<think>存在矛盾时：
   - 时间最近优先
   - 明确表述优先于模糊表述
   - 通过提问确认而非自行裁决

【创作执行】
5. 严格保持：
   - 叙事节奏（通过<think>中的节奏描述）
   - 情绪曲线（根据<think>中的情绪标记）
   - 文学密度（匹配<think>中的详略指示）
6. 对未在<think>中覆盖的细节：
   - 保持最小化补充
   - 补充内容必须与现有<think>逻辑自洽''',
        "deepseek_story_v2": '''请作为专业作家根据指定主题创作故事，严格遵循以下要求：

1. 格式要求：
   # 标题（体现核心冲突或主题）
   > 主题
   故事正文（远超800字）

2. 内容要求：
   - 包含明确转折点
   - 埋设3处以上伏笔并在后期回收
   - 关键情节需有前因后果闭环
   - 人物动机需有心理描写支撑
   - 最终结局应出人意料但合乎逻辑
   - 风格多变（可尝试不同风格）
   - 不需要分割线、分章节''',
        "doubao_story": '''<optimized_prompt>
<task>创意撰写一篇符合要求的主题文章</task>

<context>
请发挥创意写一篇文章。
要求：选准角度，确定立意，自拟有趣标题；不要套作，不得抄袭；不得泄露个人信息；不少于1500字；严格按照格式输出。

输出格式：
# 标题
正文
</context>

<instructions>
1. 创意确定主题：
   - 发掘独特有趣且适合故事化表达的主题方向
   - 选择能讲述完整故事的切入点
   - 确保主题既新颖又有叙事深度

2. 创意规划结构：
   - 采用经典故事结构（起承转合）或创新叙事方式
   - 设计引人入胜的情节发展
   - 塑造鲜明的人物形象
   - 构建完整的叙事弧线

3. 创意表达内容：
   - 用富有张力的场景描写开头
   - 融入戏剧性冲突和转折
   - 创造性地发展故事情节
   - 达到不少于1500字的要求

4. 完善创意细节：
   - 拟订一个暗示故事性的标题
   - 增强场景描写和人物刻画
   - 确保故事连贯性和吸引力
   - 移除任何个人信息

5. 创意格式化输出：
   - 通过段落节奏强化故事张力
   - 确保标题前有#标记
   - 使用对话和描写增强故事性
</instructions>

<output_format>
# 一个引人入胜的故事标题
文章正文内容，不少于1500字，包含完整的故事元素，格式规范且富有叙事魅力
</output_format>
</optimized_prompt>'''
    }
    default_prompt = 'The requested prompt is not available. Please use a valid key.'
    return prompts.get(key, default_prompt)


def save_chat_metadata(request_params: dict[str, list[dict[str, str] | dict[str, str]] | str], response_time: float,
                       session_id: str,
                       api_base_url: str,
                       response_data: dict):
    """修复后的元数据保存"""
    metadata = {
        "session_id": session_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "response_time": round(response_time, 3),
        "request_params": request_params,
        "api_base_url": api_base_url,
        "system_metrics": {
            "platform": os.name,
            "python_version": sys.version.split()[0]
        },
        "response_data": response_data

    }

    # 使用固定路径测试
    _save_to_json(metadata, "chat_logs/story_records.json")


def log_error(error_msg: str):
    """独立的错误日志记录"""
    error_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "error": error_msg,
        "level": "ERROR"
    }
    _save_to_json(error_entry, "error_logs/ai_errors.json")


def _save_to_json(data: dict, filename: str):
    """修复后的通用存储方法"""
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        existing = []

        # 更健壮的文件读取方式
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except json.JSONDecodeError as e:
                print(f"检测到损坏日志文件，尝试修复: {str(e)}")
                # 备份损坏文件
                corrupted_name = f"{filename}.corrupted_{datetime.datetime.now().timestamp()}"
                os.rename(filename, corrupted_name)

        # 追加新数据
        existing.append(data)

        # 原子写入操作
        temp_file = f"{filename}.tmp"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        os.replace(temp_file, filename)

    except Exception as e:
        print(f"严重错误: 数据保存失败 - {str(e)}")
        # 这里可以添加将错误数据暂存到内存的逻辑


def chat_ai_reasoning(msg: str, api_key: str, system_prompt: str, session_id: str = None,
                      model_name: str = "deepseek-reasoner",
                      api_base_url: str = "https://api.deepseek.com",
                      **kwargs) -> tuple:
    client = OpenAI(api_key=api_key, base_url=api_base_url)  # 请填写您自己的APIKey

    # 生成会话ID（如果未提供）
    session_id = session_id or str(uuid.uuid4())

    # 初始化计时器
    start_time = time.time()

    # prompt = ("请根据我提供的一句话，以 Markdown 格式的一级标题为这个故事起标题，在标题下方以 Markdown "
    #           "格式引用该句话。充分释放创意，不限风格、叙事视角、角色、场景、情感基调，创作一个深度贴合该句含义，情节跌宕起伏、扣人心弦且逻辑缜密，字数尽可能多（远超 800 字）的故事。")
    #     prompt = '''你现在是一个故事专家，请你根据我提供的主题写一个字数尽可能多（远超 800 字）的故事。按照下面的格式输出
    # """ 输出格式 """
    # # 故事的题目
    # > 故事的主题
    # 故事内容'''
    # prompt = '''作为专业作家，请根据主题创作故事。要求：
    # - 严格按格式输出：
    # # 标题
    # > 主题
    # 故事内容（远超800个字）
    # - 保持逻辑严密、情节曲折'''

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": msg}
    ]
    request_params = {"model": model_name,  # 请填写您要调用的模型名称
                      "messages": messages,
                      "stream": False,
                      **kwargs}
    try:

        response = client.chat.completions.create(
            **request_params
        )

        # 获取响应内容
        reasoning_content = response.choices[0].message.reasoning_content or ""
        response_content = response.choices[0].message.content or ""
        # 记录响应耗时
        response_time = time.time() - start_time

        # 保存完整的对话记录（包含原始响应）
        save_chat_metadata(
            request_params=request_params,
            response_time=response_time,
            api_base_url=api_base_url,
            session_id=session_id,
            response_data=response.to_dict()
        )

        return reasoning_content, response_content

    except (APIConnectionError, APIError) as e:
        error_msg = f"API错误: {str(e)}"
        print(error_msg)
        log_error(error_msg)  # 建议添加独立的错误日志
        return "思考失败", "服务暂时不可用，请稍后重试"

    except Exception as e:
        error_msg = f"系统错误: {str(e)}"
        print(error_msg)
        log_error(error_msg)
        return "思考失败", "生成失败，请联系管理员"


def ensure_first_line_is_h1(markdown_text):
    """
    确保输入字符串的第一行是 Markdown 格式的一级标题。

    参数:
    markdown_text (str): 输入的 Markdown 文本。

    返回:
    str: 调整后的 Markdown 文本，确保第一行是一级标题。
    """
    lines = markdown_text.splitlines()
    if lines:
        first_line = lines[0]

        # 检查第一行是否是标题，并确定其级别
        if first_line.startswith('# '):
            # 已经是一级标题，不做改动
            pass
        elif first_line.startswith('## '):
            # 二级标题，降为一级标题
            lines[0] = '#' + first_line[2:]
        elif first_line.startswith('### '):
            # 三级标题，降为一级标题
            lines[0] = '#' + first_line[3:]
        else:
            # 不是标题，则直接添加一级标题格式
            lines.insert(0, '# ' + first_line)

    # 重新组合成字符串返回
    return '\n'.join(lines)


def estimate_tokens(api_key, model, messages, url="https://api.moonshot.cn/v1/tokenizers/estimate-token-count"):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": messages
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # 检查请求是否成功

    token_data = response.json()
    return token_data['data']['total_tokens']


def download_image(url, save_dir):
    """
    下载图片并保存到指定目录，返回图片保存路径。

    参数:
    url (str): 图片的 URL。
    save_dir (str): 保存图片的目录。

    返回:
    str: 保存的图片文件的路径。
    """

    # 检查保存目录是否存在，如果不存在则创建
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # 发送 HTTP 请求获取图片数据
    response = requests.get(url)
    response.raise_for_status()  # 如果请求失败，则引发 HTTPError 异常

    # 生成一个唯一的文件名，避免文件名冲突
    unique_file_name = f"{uuid.uuid4().hex}.jpg"  # 默认使用 .jpg 扩展名，你可以根据需要修改
    file_path = os.path.join(save_dir, unique_file_name)

    # 将图片数据写入文件
    with open(file_path, 'wb') as file:
        file.write(response.content)

    return file_path


def convert_path(path):
    new_path = path.replace('./story', '')
    return new_path


def modify_link(file_path, text):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if 'link:' in line:
            parts = line.split('link: ')
            parts[1] = text
            lines[i] = '      link: ' + text + '\n'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def process_string(original_str, first_content, last_content, log_file_path):
    original_lines = original_str.splitlines()
    original_line_count = len(original_lines)

    delete_first = False
    delete_last = False

    # 检查是否需要删除第一行和最后一行
    if original_line_count >= 1:
        if original_lines[0] == first_content:
            delete_first = True
        if original_lines[-1] == last_content:
            delete_last = True

    # 处理删除操作
    new_lines = original_lines.copy()
    if delete_first and len(new_lines) >= 1:
        new_lines = new_lines[1:]
    if delete_last and len(new_lines) >= 1:
        new_lines = new_lines[:-1]

    # 生成处理后的字符串
    processed_str = '\n'.join(new_lines)

    # 生成日志条目
    log_entries = []
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if delete_first:
        log_entries.append(f"[{timestamp}] 删除了第一行: '{first_content}'")
    if delete_last:
        log_entries.append(f"[{timestamp}] 删除了最后一行: '{last_content}'")

    # 将日志写入文件（自动创建目录）
    if log_entries:
        log_dir = os.path.dirname(log_file_path)
        if log_dir:  # 确保目录路径非空
            os.makedirs(log_dir, exist_ok=True)
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            for entry in log_entries:
                log_file.write(entry + '\n')

    return processed_str


# 按装订区域中的绿色按钮以运行脚本。
if __name__ == '__main__':
    load_dotenv()
    # save_to_md_file(chat_ai("你的生活不会因偶然变好，而是因改变变好。", os.environ.get("API_KEY")), f"./test/{get_today_info()}.md")
    jinshan = get_jinshan()

    # 智谱
    img_path = download_image(jinshan.get('fenxiang_img'), './story/images')
    file_name = f"{get_today_info()}.md"
    story = chat_ai(f"我提供的主题是：{jinshan.get('note')}", os.environ.get("API_KEY"),
                    system_prompt=get_prompt("zhipu_story"))
    story = process_string(story, "```markdown", "```", f"./story/{file_name}.log")
    story = ensure_first_line_is_h1(story)
    story = insert_content_in_fourth_line(story, f"\n![{jinshan.get('note')}]({convert_path(img_path)})\n")

    save_to_md_file(story, f"./story/{file_name}")
    modify_link("./story/index.md", f"/{file_name}")

    # DeepSeek
    deepseek_system_prompt = get_prompt("deepseek_story_v2.1")
    deepseek_msg = f"我提供的主题是：{jinshan.get('note')}"
    ds_reasoning_content, ds_story = chat_ai_reasoning(deepseek_msg,
                                                       os.environ.get("API_KEY_DS"),
                                                       system_prompt=deepseek_system_prompt)

    ds_story = insert_content_in_first_line(ds_story, f"<ReasoningChainRenderer>\n"
                                                      f"{ds_reasoning_content}"
                                                      f"\n</ReasoningChainRenderer>\n")

    file_name = f"{get_today_info()}.md"
    save_to_md_file(ds_story, f"./story/{file_name}")

    # Kimi -> DeepSeek think
    kimi_api_key = os.environ.get("API_KEY_KIMI")
    kimi_model_name = "kimi-latest"
    kimi_system_prompt = get_prompt("Kimi_v2")
    kimi_msg = f"""{deepseek_system_prompt}

    {deepseek_msg}

<think>
{ds_reasoning_content}
</think>"""
    kimi_token_count = estimate_tokens(kimi_api_key, kimi_model_name, [
        {"role": "system", "content": kimi_system_prompt},
        {"role": "user", "content": kimi_msg}
    ])
    kimi_story = chat_ai(kimi_msg, kimi_api_key,
                         system_prompt=kimi_system_prompt, api_base_url="https://api.moonshot.cn/v1",
                         model_name=kimi_model_name, max_tokens=8192-kimi_token_count)

    file_name = f"{get_today_info()}.md"
    save_to_md_file(kimi_story, f"./story/{file_name}")

    # DeepSeek-V3
    ds_v3_story = chat_ai(f"我提供的主题是：{jinshan.get('note')}", os.environ.get("API_KEY_DS"),
                          system_prompt=get_prompt("deepseek_v3_story"), api_base_url="https://api.deepseek.com",
                          model_name="deepseek-chat",
                          max_tokens=8192,
                          temperature=1.5
                          )

    file_name = f"{get_today_info()}.md"
    save_to_md_file(ds_v3_story, f"./story/{file_name}")

    # 豆包
    doubao_system_prompt = get_prompt("doubao_story")
    doubao_msg = f"主题：{jinshan.get('note')}"
    db_reasoning_content, db_story = chat_ai_reasoning(doubao_msg,
                                                       os.environ.get("API_KEY_DOUBAO"),
                                                       system_prompt=doubao_system_prompt,
                                                       api_base_url="https://ark.cn-beijing.volces.com/api/v3",
                                                       model_name="doubao-1-5-thinking-pro-250415")

    db_story = insert_content_in_first_line(db_story, f"<ReasoningChainRenderer>\n"
                                                      f"{db_reasoning_content}"
                                                      f"\n</ReasoningChainRenderer>\n")

    file_name = f"{get_today_info()}.md"
    save_to_md_file(db_story, f"./story/{file_name}")

    # Kimi -> 豆包 think

    # kimi_msg = f"""{doubao_system_prompt}
    #
    # {doubao_msg}
    #
    # <think>
    # {db_reasoning_content}
    # </think>"""
    # kimi_token_count = estimate_tokens(kimi_api_key, kimi_model_name, [
    #     {"role": "system", "content": kimi_system_prompt},
    #     {"role": "user", "content": kimi_msg}
    # ])
    # kimi_story = chat_ai(kimi_msg, kimi_api_key,
    #                      system_prompt=kimi_system_prompt, api_base_url="https://api.moonshot.cn/v1",
    #                      model_name=kimi_model_name, max_tokens=8192 - kimi_token_count)
    #
    # file_name = f"{get_today_info()}.md"
    # save_to_md_file(kimi_story, f"./story/{file_name}")
