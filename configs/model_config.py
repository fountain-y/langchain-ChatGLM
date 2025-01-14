import torch.cuda
import torch.backends
import os
import logging
import uuid

LOG_FORMAT = "%(levelname) -5s %(asctime)s" "-1d: %(message)s"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(format=LOG_FORMAT)

# 在以下字典中修改属性值，以指定本地embedding模型存储位置
# 如将 "text2vec": "GanymedeNil/text2vec-large-chinese" 修改为 "text2vec": "User/Downloads/text2vec-large-chinese"
# 此处请写绝对路径
embedding_model_dict = {
    "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
    "ernie-base": "nghuyong/ernie-3.0-base-zh",
    "text2vec-base": "shibing624/text2vec-base-chinese",
    "text2vec": "GanymedeNil/text2vec-large-chinese",
    "text2vec-base-multilingual": "shibing624/text2vec-base-multilingual",
    "text2vec-base-chinese-sentence": "shibing624/text2vec-base-chinese-sentence",
    "text2vec-base-chinese-paraphrase": "shibing624/text2vec-base-chinese-paraphrase",
    "m3e-small": "moka-ai/m3e-small",
    "m3e-base": "/data/yuanrz/model/m3e-base",
    "all-MiniLM-L6-v2": "/data/yuanrz/model/all-MiniLM-L6-v2",
}

# Embedding model name
# EMBEDDING_MODEL = "text2vec"
# EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_MODEL = "m3e-base"

# Embedding running device
# EMBEDDING_DEVICE = "cuda:3" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
EMBEDDING_DEVICE = "cuda:6" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

# supported LLM models
# llm_model_dict 处理了loader的一些预设行为，如加载位置，模型名称，模型处理器实例
# 在以下字典中修改属性值，以指定本地 LLM 模型存储位置
# 如将 "chatglm-6b" 的 "local_model_path" 由 None 修改为 "User/Downloads/chatglm-6b"
# 此处请写绝对路径,且路径中必须包含repo-id的模型名称，因为FastChat是以模型名匹配的
llm_model_dict = {
    "chatglm-6b-int4-qe": {
        "name": "chatglm-6b-int4-qe",
        "pretrained_model_name": "THUDM/chatglm-6b-int4-qe",
        "local_model_path": None,
        "provides": "ChatGLMLLMChain"
    },
    "chatglm-6b-int4": {
        "name": "chatglm-6b-int4",
        "pretrained_model_name": "THUDM/chatglm-6b-int4",
        "local_model_path": None,
        "provides": "ChatGLMLLMChain"
    },
    "chatglm-6b-int8": {
        "name": "chatglm-6b-int8",
        "pretrained_model_name": "THUDM/chatglm-6b-int8",
        "local_model_path": None,
        "provides": "ChatGLMLLMChain"
    },
    "chatglm-6b": {
        "name": "chatglm-6b",
        "pretrained_model_name": "THUDM/chatglm-6b",
        "local_model_path": None,
        "provides": "ChatGLMLLMChain"
    },
    "Qwen-7B-Chat": {
        "name": "Qwen-7B-Chat",
        "pretrained_model_name": "Qwen/Qwen-7B-Chat",
        "local_model_path": "/data/yuanrz/work_dirs/llm/model/Qwen-7B-Chat",
        "provides": "ChatGLMLLMChain"
    },
    # langchain-ChatGLM 用户“帛凡” @BoFan-tunning 基于ChatGLM-6B 训练并提供的权重合并模型和 lora 权重文件 chatglm-fitness-RLHF
    # 详细信息见 HuggingFace 模型介绍页 https://huggingface.co/fb700/chatglm-fitness-RLHF
    # 使用该模型或者lora权重文件，对比chatglm-6b、chatglm2-6b、百川7b，甚至其它未经过微调的更高参数的模型，在本项目中，总结能力可获得显著提升。
    "chatglm-fitness-RLHF": {
        "name": "chatglm-fitness-RLHF",
        "pretrained_model_name": "fb700/chatglm-fitness-RLHF",
        "local_model_path": None,
        "provides": "ChatGLMLLMChain"
    },
    "chatglm2-6b": {
        "name": "chatglm2-6b",
        "pretrained_model_name": "THUDM/chatglm2-6b",
        "local_model_path": "/data/yuanrz/model/chatglm2-6b",
        "provides": "ChatGLMLLMChain"
    },
    "chatglm2-6b-32k": {
        "name": "chatglm2-6b-32k",
        "pretrained_model_name": "THUDM/chatglm2-6b-32k",
        "local_model_path": '/data/yuanrz/model/chatglm2-6b-32k',
        "provides": "ChatGLMLLMChain"
    },
    # 注：chatglm2-cpp已在mac上测试通过，其他系统暂不支持
    "chatglm2-cpp": {
        "name": "chatglm2-cpp",
        "pretrained_model_name": "cylee0909/chatglm2cpp",
        "local_model_path": None,
        "provides": "ChatGLMCppLLMChain"
    },
    "chatglm2-6b-int4": {
        "name": "chatglm2-6b-int4",
        "pretrained_model_name": "THUDM/chatglm2-6b-int4",
        "local_model_path": None,
        "provides": "ChatGLMLLMChain"
    },
    "chatglm2-6b-int8": {
        "name": "chatglm2-6b-int8",
        "pretrained_model_name": "THUDM/chatglm2-6b-int8",
        "local_model_path": None,
        "provides": "ChatGLMLLMChain"
    },
    "chatyuan": {
        "name": "chatyuan",
        "pretrained_model_name": "ClueAI/ChatYuan-large-v2",
        "local_model_path": None,
        "provides": "MOSSLLMChain"
    },
    "moss": {
        "name": "moss",
        "pretrained_model_name": "fnlp/moss-moon-003-sft",
        "local_model_path": None,
        "provides": "MOSSLLMChain"
    },
    "moss-int4": {
        "name": "moss",
        "pretrained_model_name": "fnlp/moss-moon-003-sft-int4",
        "local_model_path": None,
        "provides": "MOSSLLM"
    },
    "vicuna-13b-hf": {
        "name": "vicuna-13b-hf",
        "pretrained_model_name": "vicuna-13b-hf",
        "local_model_path": None,
        "provides": "LLamaLLMChain"
    },
    "vicuna-7b-hf": {
        "name": "vicuna-13b-hf",
        "pretrained_model_name": "vicuna-13b-hf",
        "local_model_path": None,
        "provides": "LLamaLLMChain"
    },
    # 直接调用返回requests.exceptions.ConnectionError错误，需要通过huggingface_hub包里的snapshot_download函数
    # 下载模型，如果snapshot_download还是返回网络错误，多试几次，一般是可以的，
    # 如果仍然不行，则应该是网络加了防火墙(在服务器上这种情况比较常见)，基本只能从别的设备上下载，
    # 然后转移到目标设备了.
    "bloomz-7b1": {
        "name": "bloomz-7b1",
        "pretrained_model_name": "bigscience/bloomz-7b1",
        "local_model_path": None,
        "provides": "MOSSLLMChain"

    },
    # 实测加载bigscience/bloom-3b需要170秒左右，暂不清楚为什么这么慢
    # 应与它要加载专有token有关
    "bloom-3b": {
        "name": "bloom-3b",
        "pretrained_model_name": "bigscience/bloom-3b",
        "local_model_path": None,
        "provides": "MOSSLLMChain"

    },
    "baichuan-7b": {
        "name": "baichuan-7b",
        "pretrained_model_name": "baichuan-inc/baichuan-7B",
        "local_model_path": None,
        "provides": "MOSSLLMChain"
    },
    "baichuan-13b": {
        "name": "baichuan-13b",
        "pretrained_model_name": "baichuan-inc/baichuan-13B",
        "local_model_path": "/data/yuanrz/model/Baichuan-13B-Chat",
        "provides": "MOSSLLMChain"
    },
    # llama-cpp模型的兼容性问题参考https://github.com/abetlen/llama-cpp-python/issues/204
    "ggml-vicuna-13b-1.1-q5": {
        "name": "ggml-vicuna-13b-1.1-q5",
        "pretrained_model_name": "lmsys/vicuna-13b-delta-v1.1",
        # 这里需要下载好模型的路径,如果下载模型是默认路径则它会下载到用户工作区的
        # /.cache/huggingface/hub/models--vicuna--ggml-vicuna-13b-1.1/
        # 还有就是由于本项目加载模型的方式设置的比较严格，下载完成后仍需手动修改模型的文件名
        # 将其设置为与Huggface Hub一致的文件名
        # 此外不同时期的ggml格式并不兼容，因此不同时期的ggml需要安装不同的llama-cpp-python库，且实测pip install 不好使
        # 需要手动从https://github.com/abetlen/llama-cpp-python/releases/tag/下载对应的wheel安装
        # 实测v0.1.63与本模型的vicuna/ggml-vicuna-13b-1.1/ggml-vic13b-q5_1.bin可以兼容
        "local_model_path": f'''{"/".join(os.path.abspath(__file__).split("/")[:3])}/.cache/huggingface/hub/models--vicuna--ggml-vicuna-13b-1.1/blobs/''',
        "provides": "LLamaLLMChain"
    },

    # 通过 fastchat 调用的模型请参考如下格式
    "fastchat-chatglm-6b": {
        "name": "chatglm-6b",  # "name"修改为fastchat服务中的"model_name"
        "pretrained_model_name": "chatglm-6b",
        "local_model_path": None,
        "provides": "FastChatOpenAILLMChain",  # 使用fastchat api时，需保证"provides"为"FastChatOpenAILLMChain"
        "api_base_url": "http://localhost:8000/v1",  # "name"修改为fastchat服务中的"api_base_url"
        "api_key": "EMPTY"
    },
    "fastchat-baichuan-13b": {
        "name": "Baichuan-13B-Chat",
        "pretrained_model_name": "Baichuan-13B-Chat",
        "local_model_path": "/data/yuanrz/model/Baichuan-13B-Chat",
        "provides": "FastChatOpenAILLMChain",
        "api_base_url": "http://localhost:8000/v1",  # "name"修改为fastchat服务中的"api_base_url"
        "api_key": "EMPTY"
    },
        # 通过 fastchat 调用的模型请参考如下格式
    "fastchat-chatglm-6b-int4": {
        "name": "chatglm-6b-int4",  # "name"修改为fastchat服务中的"model_name"
        "pretrained_model_name": "chatglm-6b-int4",
        "local_model_path": None,
        "provides": "FastChatOpenAILLMChain",  # 使用fastchat api时，需保证"provides"为"FastChatOpenAILLMChain"
        "api_base_url": "http://localhost:8001/v1",  # "name"修改为fastchat服务中的"api_base_url"
        "api_key": "EMPTY"
    },
    "fastchat-chatglm2-6b": {
        "name": "chatglm2-6b-32k",  # "name"修改为fastchat服务中的"model_name"
        "pretrained_model_name": "chatglm2-6b",
        "local_model_path": '/data/yuanrz/model/chatglm2-6b-32k',
        "provides": "FastChatOpenAILLMChain",  # 使用fastchat api时，需保证"provides"为"FastChatOpenAILLMChain"
        "api_base_url": "http://localhost:8000/v1",  # "name"修改为fastchat服务中的"api_base_url"
        "api_key": "EMPTY"
    },

    # 通过 fastchat 调用的模型请参考如下格式
    "fastchat-vicuna-13b-hf": {
        "name": "vicuna-13b-hf",  # "name"修改为fastchat服务中的"model_name"
        "pretrained_model_name": "vicuna-13b-hf",
        "local_model_path": None,
        "provides": "FastChatOpenAILLMChain",  # 使用fastchat api时，需保证"provides"为"FastChatOpenAILLMChain"
        "api_base_url": "http://localhost:8000/v1",  # "name"修改为fastchat服务中的"api_base_url"
        "api_key": "EMPTY"
    },
    # 调用chatgpt时如果报出： urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='api.openai.com', port=443):
    #  Max retries exceeded with url: /v1/chat/completions
    # 则需要将urllib3版本修改为1.25.11
    # 如果依然报urllib3.exceptions.MaxRetryError: HTTPSConnectionPool，则将https改为http
    # 参考https://zhuanlan.zhihu.com/p/350015032

    # 如果报出：raise NewConnectionError(
    # urllib3.exceptions.NewConnectionError: <urllib3.connection.HTTPSConnection object at 0x000001FE4BDB85E0>:
    # Failed to establish a new connection: [WinError 10060]
    # 则是因为内地和香港的IP都被OPENAI封了，需要切换为日本、新加坡等地
    "openai-chatgpt-3.5": {
        "name": "gpt-3.5-turbo",
        "pretrained_model_name": "gpt-3.5-turbo",
        "provides": "FastChatOpenAILLMChain",
        "local_model_path": None,
        "api_base_url": "https://api.openai.com/v1",
        "api_key": ""
    },

}

# LLM 名称
# LLM_MODEL = "chatglm2-6b-32k"
LLM_MODEL = "fastchat-baichuan-13b"
# LLM_MODEL = "fastchat-chatglm2-6b"
# LLM_MODEL = "Qwen-7B-Chat"
# LLM_MODEL = "chatglm2-6b"
# 量化加载8bit 模型
LOAD_IN_8BIT = False
# Load the model with bfloat16 precision. Requires NVIDIA Ampere GPU.
BF16 = False
# 本地lora存放的位置
LORA_DIR = "loras/"

# LORA的名称，如有请指定为列表

LORA_NAME = ""
USE_LORA = True if LORA_NAME else False

# LLM streaming reponse
STREAMING = True

# Use p-tuning-v2 PrefixEncoder
USE_PTUNING_V2 = False
PTUNING_DIR='./ptuning-v2'
# LLM running device
LLM_DEVICE = "cuda:6" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
# LLM_DEVICE = "cuda:5" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

# 知识库默认存储路径
KB_ROOT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")

# 基于上下文的prompt模版，请务必保留"{question}"和"{context}"
# PROMPT_TEMPLATE = """已知信息：
# {context} 

# 根据上述已知信息，简洁和专业的来回答用户的问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题” 或 “没有提供足够的相关信息”，不允许在答案中添加编造成分，答案请使用中文。 问题是：{question}"""
PROMPT_TEMPLATE = """
请根据下述已知信息回答目标问题。根据上述已知信息，详细和专业的来回答用户的问题。如果能够检索到答案，需要保证回答完整。如果无法从中得到答案，请回答 “根据已知信息无法回答该问题，但根据理解，” 或 “没有提供足够的相关信息，但根据理解，”，然后根据理解生成答案，答案请使用中文。

###已知信息：
{context} 
###问题是：{question}。
###答：

"""

# PROMPT_TEMPLATE = """
# 请根据下述已知信息回答目标问题。根据上述已知信息，详细和专业的来回答用户的问题。如果能够检索到答案，需要保证回答完整。如果无法从中得到答案，请回答 “根据已知信息无法回答该问题，但根据理解，” 或 “没有提供足够的相关信息，但根据理解，”，然后根据理解生成答案，答案请使用中文。 接下来首先是一些相关示例，然后是您的问题和答案。请注意，示例中的答案可能不是正确的答案，但是它们可以帮助您更好地理解问题。

# 示例1：
# ###已知信息：
# 第六十三条 商业银行对视同我国主权的公共部门实体风险暴露的风险权重。 （一）对我国中央政府投资的金融资产管理公司为收购国有银行不良贷款而定向发行的债券的风险权重为0%。 （二）对省级（直辖市、自治区）及计划单列市人民政府风险暴露的风险权重根据债券类型确定。一般债券风险权重为10%，专项债券风险权重为20%。 （三）对除财政部和中国人民银行外，其他收入主要源于中央财政的公共部门风险暴露的风险权重为20%。 （四）对其他经国务院批准可视同我国主权的公共部门实体风险暴露的风险权重另行规定。 商业银行对前款所列视同我国主权的公共部门实体投资的工商企业的风险暴露不适用上述风险权重。 
# ###问题是：对省级（直辖市、自治区）及计划单列市人民政府的风险暴露。
# ###答：
# 对省级（直辖市、自治区）及计划单列市人民政府风险暴露的风险权重根据债券类型确定。一般债券风险权重为10%，专项债券风险权重为20%。

# 示例2：
# ###已知信息：
# （一）对有短期评级、或未评级但有推测评级的风险暴露，可按表2确定风险权重。 表2 短期评级风险权重表 | 外部信用评级 | A–1/P–1 | A–2/P–2 | A–3/P–3 | 其他评级 |\n| ---- | ---- | ---- | ---- | ---- |\n| 风险权重 | 15% | 50% | 100% | 1250% | 如果符合“简单、透明、可比”标准，则按表3确定风险权重。 表3 符合“简单、透明、可比”标准的短期评级风险权重表 | 外部信用评级 | A–1/P–1 | A–2/P–2 | A–3/P–3 | 其他评级 |\n| ---- | ---- | ---- | ---- | ---- |\n| 风险权重 | 10% | 30% | 60% | 1250% |
# ###问题是：符合“简单、透明、可比”标准的短期评级风险权重，以表格形式展现。
# ###答：
# 已知信息中，表3的表头：符合“简单、透明、可比”标准的短期评级风险权重表，与目标问题“符合“简单、透明、可比”标准的短期评级风险权重，以表格形式展现”符合，因此可以直接使用表3的表格形式展现。
# | 外部信用评级 | A–1/P–1 | A–2/P–2 | A–3/P–3 | 其他评级 |
# | ---- | ---- | ---- | ---- | ---- |
# | 风险权重 | 10% | 30% | 60% | 1250% |

# 示例3：
# ###已知信息：
# （一）对有短期评级、或未评级但有推测评级的风险暴露，可按表2确定风险权重。 表2 短期评级风险权重表 | 外部信用评级 | A–1/P–1 | A–2/P–2 | A–3/P–3 | 其他评级 |\n| ---- | ---- | ---- | ---- | ---- |\n| 风险权重 | 15% | 50% | 100% | 1250% | 如果符合“简单、透明、可比”标准，则按表3确定风险权重。 表3 符合“简单、透明、可比”标准的短期评级风险权重表 | 外部信用评级 | A–1/P–1 | A–2/P–2 | A–3/P–3 | 其他评级 |\n| ---- | ---- | ---- | ---- | ---- |\n| 风险权重 | 10% | 30% | 60% | 1250% |
# ###问题是：短期评级风险权重，以表格形式展现。
# ###答：
# 已知信息中，表2的表头短期评级风险权重表，与目标问题“短期评级风险权重，以表格形式展现”符合，因此可以直接使用表2的表格形式展现。
# | 外部信用评级 | A–1/P–1 | A–2/P–2 | A–3/P–3 | 其他评级 |
# | ---- | ---- | ---- | ---- | ---- |
# | 风险权重 | 15% | 50% | 100% | 1250% |


# ###已知信息：
# {context} 
# ###问题是：{question}。
# ###答：

# """


# 缓存知识库数量,如果是ChatGLM2,ChatGLM2-int4,ChatGLM2-int8模型若检索效果不好可以调成’10’
CACHED_VS_NUM = 10

# 文本分句长度
SENTENCE_SIZE = 100
# SENTENCE_SIZE = 100

# 匹配后单段上下文长度
CHUNK_SIZE = 300

# 传入LLM的历史记录长度
LLM_HISTORY_LEN = 1

# 知识库检索时返回的匹配内容条数
VECTOR_SEARCH_TOP_K = 5
# VECTOR_SEARCH_TOP_K = 10

# 知识检索内容相关度 Score, 数值范围约为0-1100，如果为0，则不生效，建议设置为500左右，经测试设置为小于500时，匹配结果更精准
VECTOR_SEARCH_SCORE_THRESHOLD = 500
# VECTOR_SEARCH_SCORE_THRESHOLD = 500

NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nltk_data")

FLAG_USER_NAME = uuid.uuid4().hex

logger.info(f"""
loading model config
llm device: {LLM_DEVICE}
embedding device: {EMBEDDING_DEVICE}
dir: {os.path.dirname(os.path.dirname(__file__))}
flagging username: {FLAG_USER_NAME}
""")

# 是否开启跨域，默认为False，如果需要开启，请设置为True
# is open cross domain
OPEN_CROSS_DOMAIN = False

# Bing 搜索必备变量
# 使用 Bing 搜索需要使用 Bing Subscription Key,需要在azure port中申请试用bing search
# 具体申请方式请见
# https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/create-bing-search-service-resource
# 使用python创建bing api 搜索实例详见:
# https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/quickstarts/rest/python
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"
# 注意不是bing Webmaster Tools的api key，

# 此外，如果是在服务器上，报Failed to establish a new connection: [Errno 110] Connection timed out
# 是因为服务器加了防火墙，需要联系管理员加白名单，如果公司的服务器的话，就别想了GG
BING_SUBSCRIPTION_KEY = ""

# 是否开启中文标题加强，以及标题增强的相关配置
# 通过增加标题判断，判断哪些文本为标题，并在metadata中进行标记；
# 然后将文本与往上一级的标题进行拼合，实现文本信息的增强。
ZH_TITLE_ENHANCE = False
# ZH_TITLE_ENHANCE = True
