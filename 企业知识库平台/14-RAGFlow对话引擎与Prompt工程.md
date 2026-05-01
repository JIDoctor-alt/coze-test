# RAGFlow 对话引擎与 Prompt 工程深度解析

> **文档版本**: v1.0  
> **源码版本**: RAGFlow (最新)  
> **目标读者**: 需要深入理解 RAGFlow 对话系统和 Prompt 工程的开发者  
> **前置知识**: 建议先阅读 [07-RAGFlow源码深度解析.md](./07-RAGFlow源码深度解析.md) 了解基础概念

---

## 目录

- [第一章：对话引擎架构](#第一章对话引擎架构)
- [第二章：Prompt 模板系统](#第二章prompt-模板系统)
- [第三章：LLM 集成详解](#第三章llm-集成详解)
- [第四章：检索增强对话流程](#第四章检索增强对话流程)
- [第五章：Agent 能力](#第五章agent-能力)
- [第六章：Prompt 工程最佳实践](#第六章prompt-工程最佳实践)
- [附录：关键代码索引](#附录关键代码索引)

---

## 第一章：对话引擎架构

### 1.1 核心组件全景图

RAGFlow 的对话引擎是整个系统的"大脑"，负责协调用户查询、知识检索、LLM 生成等环节。让我们用一张图来理解：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户发起对话                                   │
│                            │                                         │
│                            ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  API 层 (chat_api.py)                                        │   │
│  │  - 创建 Chat Assistant                                       │   │
│  │  - 管理 Session（会话）                                       │   │
│  │  - 流式/非流式响应                                           │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                            │                                         │
│                            ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  服务层 (dialog_service.py)                                  │   │
│  │  - async_chat(): 核心对话逻辑                                │   │
│  │  - 多轮对话上下文管理                                         │   │
│  │  - 引用标注与结果整合                                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                            │                                         │
│              ┌─────────────┼─────────────┐                          │
│              ▼             ▼             ▼                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  知识库检索   │  │  LLM 生成     │  │  流式处理    │             │
│  │  (retrieval) │  │  (chat_model) │  │  (streaming) │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 对话管理核心代码

#### 1.2.1 Chat 创建与配置

**代码位置**: `api/apps/restful_apis/chat_api.py`

```python
_DEFAULT_PROMPT_CONFIG = {
    "system": (
        'You are an intelligent assistant. Please summarize the content of the dataset '
        'to answer the question. '
        'Please list the data in the dataset and answer in detail. When all dataset content '
        'is irrelevant to the question, your answer must include the sentence '
        '"The answer you are looking for is not found in the dataset!" '
        "Answers need to consider chat history.\n"
        "      Here is the knowledge base:\n"
        "      {knowledge}\n"
        "      The above is the knowledge base."
    ),
    "prologue": "Hi! I'm your assistant. What can I do for you?",
    "parameters": [{"key": "knowledge", "optional": False}],
    "empty_response": "Sorry! No relevant content was found in the knowledge base!",
    "quote": True,
    "tts": False,
    "refine_multiturn": True,
}
```

**解读**：
- `system`: 系统提示词模板，`{knowledge}` 占位符用于注入检索结果
- `prologue`: 开场白
- `parameters`: 参数定义，告诉系统有哪些占位符需要填充
- `empty_response`: 空结果时的回复
- `quote`: 是否显示引用来源
- `refine_multiturn`: 是否支持多轮对话优化

#### 1.2.2 Session 管理

**代码位置**: `api/db/services/conversation_service.py`

```python
class ConversationService(CommonService):
    model = Conversation

    @classmethod
    def get_list(cls, dialog_id, page_number, items_per_page, orderby, desc, id, name, user_id=None):
        sessions = cls.model.select().where(cls.model.dialog_id == dialog_id)
        # ... 分页、排序逻辑
        return list(sessions.dicts())
```

**会话结构**：
```python
{
    "id": "session_uuid",
    "dialog_id": "chat_assistant_uuid",
    "name": "会话名称",
    "message": [
        {"role": "assistant", "content": "开场白", "created_at": timestamp},
        {"role": "user", "content": "用户问题"},
        {"role": "assistant", "content": "AI回答"}
    ],
    "reference": [
        {"chunks": [...], "doc_aggs": [...]}
    ],
    "user_id": "用户ID"
}
```

### 1.3 多轮对话上下文管理

#### 1.3.1 上下文构建流程

**代码位置**: `api/db/services/dialog_service.py`

```python
def _build_message(self, dia, msgs, parameters=None, **kwargs):
    """构建发送给 LLM 的消息列表"""
    
    # 1. 添加系统提示词
    sys_prompt = dia.prompt_config.get("system", "")
    
    # 2. 如果有检索结果，注入知识库内容
    if parameters and "knowledge" in dia.prompt_config.get("parameters", []):
        knowledges = parameters.get("knowledge", [])
        sys_prompt = sys_prompt.replace(
            "{knowledge}", 
            "\n".join(knowledges) if knowledges else dia.prompt_config.get("empty_response", "")
        )
    
    # 3. 添加历史消息
    messages = [{"role": "system", "content": sys_prompt}]
    
    # 4. 添加对话历史（排除首条助手消息）
    for m in msgs:
        if m["role"] == "system":
            continue
        if m["role"] == "assistant" and not messages:
            continue
        messages.append(m)
    
    return messages
```

#### 1.3.2 上下文长度控制

**代码位置**: `rag/prompts/generator.py`

```python
def message_fit_in(msg, max_length=4000):
    """智能裁剪消息，确保不超过 max_length"""
    
    def count():
        nonlocal msg
        tks_cnts = []
        for m in msg:
            tks_cnts.append({"role": m["role"], "count": num_tokens_from_string(m["content"])})
        total = sum(m["count"] for m in tks_cnts)
        return total

    c = count()
    if c < max_length:
        return c, msg

    # 策略：保留系统消息 + 最后一条用户消息
    msg_ = [m for m in msg if m["role"] == "system"]
    if len(msg) > 1:
        msg_.append(msg[-1])
    
    c = count()
    if c < max_length:
        return c, msg

    # 策略：如果系统消息太长，按比例裁剪
    ll = num_tokens_from_string(msg_[0]["content"])
    ll2 = num_tokens_from_string(msg_[-1]["content"])
    if ll / (ll + ll2) > 0.8:
        m = msg_[0]["content"]
        m = encoder.decode(encoder.encode(m)[: max_length - ll2])
        msg[0]["content"] = m
        return max_length, msg

    # 策略：裁剪用户消息
    m = msg_[-1]["content"]
    m = encoder.decode(encoder.encode(m)[: max_length - ll])
    msg[-1]["content"] = m
    return max_length, msg
```

### 1.4 对话历史存储

#### 1.4.1 数据库模型

**代码位置**: `api/db/db_models.py`

```python
class Conversation(Model):
    id = CharField(unique=True)
    dialog_id = CharField(index=True)  # 关联的 Chat Assistant
    name = CharField()
    message = JSONField()  # 消息历史列表
    reference = JSONField()  # 引用来源列表
    user_id = CharField()
    create_time = DateTimeField()
    update_time = DateTimeField()
```

#### 1.4.2 历史消息更新

**代码位置**: `api/db/services/conversation_service.py`

```python
def structure_answer(conv, ans, message_id, session_id):
    """结构化答案，用于更新会话历史"""
    reference = ans["reference"]
    ans["id"] = message_id
    ans["session_id"] = session_id

    # 流式输出时累积内容
    if not conv.message:
        conv.message = []
    
    content = ans["answer"]
    if ans.get("start_to_think"):
        content = "<think>"  # 开始思考标记
    elif ans.get("end_to_think"):
        content = "</think>"  # 结束思考标记

    if not conv.message or conv.message[-1].get("role", "") != "assistant":
        conv.message.append({
            "role": "assistant", 
            "content": content, 
            "created_at": time.time(), 
            "id": message_id
        })
    else:
        # 累积助手回复内容
        if is_final:
            if ans.get("answer"):
                conv.message[-1] = {
                    "role": "assistant", 
                    "content": ans["answer"], 
                    "created_at": time.time(), 
                    "id": message_id
                }
        else:
            conv.message[-1]["content"] = (conv.message[-1].get("content") or "") + content
    
    return ans
```

### 1.5 流式响应实现

#### 1.5.1 SSE 流式协议

**代码位置**: `api/db/services/conversation_service.py`

```python
async def async_completion(tenant_id, chat_id, question, ..., stream=True):
    """支持流式和非流式两种模式"""
    
    if stream:
        # SSE (Server-Sent Events) 格式
        try:
            async for ans in async_chat(dia, msg, True, **kwargs):
                ans = structure_answer(conv, ans, message_id, session_id)
                # 发送数据帧
                yield "data:" + json.dumps({
                    "code": 0, 
                    "data": ans
                }, ensure_ascii=False) + "\n\n"
            
            # 发送结束帧
            yield "data:" + json.dumps({"code": 0, "data": True}, ensure_ascii=False) + "\n\n"
        except Exception as e:
            yield "data:" + json.dumps({
                "code": 500, 
                "message": str(e),
                "data": {"answer": "**ERROR**: " + str(e), "reference": []}
            }, ensure_ascii=False) + "\n\n"
```

#### 1.5.2 Think 标签处理

**代码位置**: `api/db/services/dialog_service.py`

```python
class _ThinkStreamState:
    """处理 <think> 标签的状态机"""
    def __init__(self):
        self.full_text = ""
        self.last_idx = 0
        self.endswith_think = False
        self.last_full = ""
        self.last_model_full = ""
        self.in_think = False
        self.buffer = ""


def _extract_visible_answer(text: str) -> str:
    """提取可见答案，过滤思考过程"""
    if "</think>" not in text:
        return re.sub(r"</?think>", "", text)
    
    thought, answer = text.rsplit("</think>", 1)
    thought = re.sub(r"</?think>", "", thought).strip()
    answer = re.sub(r"</?think>", "", answer)
    
    if not thought:
        return answer
    return f"<think>{thought}</think>{answer}"
```

---

## 第二章：Prompt 模板系统

### 2.1 Prompt 模板架构

RAGFlow 使用 Jinja2 模板引擎处理 Prompt，支持灵活的变量替换和逻辑控制。

```
rag/prompts/
├── template.py           # 模板加载器
├── generator.py          # Prompt 生成器
├── citation_prompt.md    # 引用标注提示词
├── ask_summary.md       # 问答总结提示词
├── keyword_prompt.md      # 关键词提取提示词
├── meta_filter.md        # 元数据过滤提示词
└── ...                   # 其他专用提示词
```

### 2.2 模板加载机制

**代码位置**: `rag/prompts/template.py`

```python
PROMPT_DIR = os.path.dirname(__file__)
_loaded_prompts = {}

def load_prompt(name: str) -> str:
    """单例模式加载 Prompt 模板"""
    if name in _loaded_prompts:
        return _loaded_prompts[name]

    path = os.path.join(PROMPT_DIR, f"{name}.md")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Prompt file '{name}.md' not found")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        _loaded_prompts[name] = content
        return content
```

### 2.3 系统提示词结构

#### 2.3.1 默认知识库问答提示词

**代码位置**: `rag/prompts/ask_summary.md`

```markdown
Role: You're a smart assistant. Your name is Miss R.
Task: Summarize the information from knowledge bases and answer user's question.
Requirements and restriction:
  - DO NOT make things up, especially for numbers.
  - If the information from knowledge is irrelevant with user's question, 
    JUST SAY: Sorry, no relevant information provided.
  - Answer with markdown format text.
  - Answer in language of user's question.

### Information from knowledge bases

{{ knowledge }}

The above is information from knowledge bases.
```

**解读**：
- **Role 定义**: 明确 AI 的身份角色
- **Task 说明**: 清晰的任务描述
- **限制规则**: 防止幻觉的关键约束
- **{{ knowledge }}**: 动态注入检索结果

#### 2.3.2 引用标注提示词（重点）

**代码位置**: `rag/prompts/citation_prompt.md`

这是 RAGFlow 引用溯源的核心提示词，包含详细的技术规则和示例：

```markdown
Based on the provided document or chat history, add citations to the input text 
using the format specified later. 

# Citation Requirements:

## Technical Rules:
- Use format: [ID:i] or [ID:i] [ID:j] for multiple sources
- Place citations at the end of sentences, before punctuation
- Maximum 4 citations per sentence
- DO NOT cite content not from <context></context>
- DO NOT modify whitespace or original text

## What MUST Be Cited:
1. **Quantitative data**: Numbers, percentages, statistics
2. **Temporal claims**: Dates, timeframes
3. **Causal relationships**: Cause and effect
4. **Comparative statements**: Rankings, comparisons
5. **Technical definitions**: Specialized terms
6. **Direct attributions**: What someone said
7. **Predictions/forecasts**: Future projections
8. **Controversial claims**: Disputed facts

## What Should NOT Be Cited:
- Common knowledge
- Transitional phrases
- General introductions
- Your own analysis

# Examples:
[此处包含6个详细示例...]
```

### 2.4 知识库检索结果的注入方式

#### 2.4.1 Chunk 格式化

**代码位置**: `rag/prompts/generator.py`

```python
def kb_prompt(kbinfos, max_tokens, hash_id=False):
    """将检索结果格式化为 Prompt"""
    
    knowledges = []
    for i, ck in enumerate(kbinfos["chunks"][:chunks_num]):
        cnt = "\nID: {}".format(i if not hash_id else hash_str2int(...))
        cnt += draw_node("Title", get_value(ck, "docnm_kwd", "document_name"))
        cnt += draw_node("URL", ck.get('url', ''))
        
        # 文档元数据
        meta = ck.get("document_metadata", {})
        for k, v in meta.items():
            cnt += draw_node(k, v)
        
        cnt += "\n└── Content:\n"
        cnt += get_value(ck, "content", "content_with_weight")
        knowledges.append(cnt)

    return knowledges
```

**格式化输出示例**：
```
ID: 0
├── Title: 2024年度财务报告.pdf
├── URL: https://...
└── Content:
    2024年公司总收入达到1.2亿元，同比增长15%。
```

#### 2.4.2 Token 预算控制

```python
def kb_prompt(kbinfos, max_tokens, hash_id=False):
    """智能裁剪，确保不超过 Token 预算"""
    knowledges = [get_value(ck, "content", "content_with_weight") for ck in kbinfos["chunks"]]
    
    used_token_count = 0
    chunks_num = 0
    
    for i, c in enumerate(knowledges):
        if not c:
            continue
        used_token_count += num_tokens_from_string(c)
        chunks_num += 1
        
        # 保留 3% 余量
        if max_tokens * 0.97 < used_token_count:
            knowledges = knowledges[:i]
            logging.warning(f"Not all retrieval into prompt: {len(knowledges)}/{kwlg_len}")
            break

    return knowledges[:chunks_num]
```

### 2.5 引用溯源的 Prompt 设计

#### 2.5.1 引用标注执行流程

**代码位置**: `rag/app/resident.py`

```python
def _gen_answer_with_citation(...):
    """生成带引用的答案"""
    
    # 1. 构建 Prompt
    sys_prompt = PROMPT_JINJA_ENV.from_string(ASK_SUMMARY).render(
        knowledge="\n".join(knowledges)
    )
    msg = [{"role": "user", "content": question}]
    
    # 2. 调用 LLM 生成答案
    answer = await chat_mdl.async_chat(sys_prompt, msg, {"temperature": 0.1})
    
    # 3. 执行引用标注
    if do_refer and kbinfos["chunks"]:
        answer, idx = retriever.insert_citations(
            answer, 
            [ck["content_ltks"] for ck in kbinfos["chunks"]],  # 原文
            [ck["vector"] for ck in kbinfos["chunks"]],        # 向量
            embd_mdl,
            tkweight=0.7,   # 文本权重
            vtweight=0.3    # 向量权重
        )
```

#### 2.5.2 Citation Plus 模板

**代码位置**: `rag/prompts/citation_plus.md`

```markdown
Given the source information and a question, generate a response that 
incorporates citations from the provided sources.

Format the citations as [ID:x] or [ID:x][ID:y] for multiple sources.

Example:
<context>
ID: 0
└── Content: The capital of France is Paris.
ID: 1
└── Content: Paris has a population of 2.1 million.
</context>

USER: What is the capital of France?
ASSISTANT: The capital of France is Paris [ID:0], which has a population 
           of 2.1 million [ID:1].
```

---

## 第三章：LLM 集成详解

### 3.1 支持的 LLM 列表

#### 3.1.1 Provider 枚举

**代码位置**: `rag/llm/__init__.py`

```python
class SupportedLiteLLMProvider(StrEnum):
    # 国外主流
    OpenAI = "OpenAI"
    Anthropic = "Anthropic"           # Claude 系列
    Google = "Gemini"
    Cohere = "Cohere"
    
    # 国内主流
    Tongyi_Qianwen = "Tongyi-Qianwen"  # 通义千问
    DeepSeek = "DeepSeek"
    Moonshot = "Moonshot"              # 月之暗面 Kimi
    ZHIPU_AI = "ZHIPU-AI"              # 智谱
    HunYuan = "Tencent Hunyuan"         # 腾讯混元
    StepFun = "StepFun"                # 阶跃星辰
    
    # 开源/本地
    Ollama = "Ollama"                  # 本地模型
    GPUStack = "GPUStack"
    
    # 聚合平台
    OpenRouter = "OpenRouter"
    SiliconFlow = "SILICONFLOW"
    Bedrock = "Bedrock"                # AWS
```

#### 3.1.2 默认 Base URL 配置

```python
FACTORY_DEFAULT_BASE_URL = {
    SupportedLiteLLMProvider.Tongyi_Qianwen: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    SupportedLiteLLMProvider.DeepSeek: "https://api.deepseek.com/v1",
    SupportedLiteLLMProvider.OpenAI: "https://api.openai.com/v1",
    SupportedLiteLLMProvider.Anthropic: "https://api.anthropic.com/",
    SupportedLiteLLMProvider.Ollama: "",  # 本地，无需 URL
    # ...
}
```

### 3.2 LLM 调用流程

#### 3.2.1 LLMBundle 封装

**代码位置**: `api/db/services/llm_service.py`

```python
class LLMBundle(LLM4Tenant):
    def __init__(self, tenant_id: str, model_config: dict, lang="Chinese", **kwargs):
        super().__init__(tenant_id, model_config, lang, **kwargs)
    
    def chat(self, prompt, history=None, **kwargs):
        """同步调用"""
        return self.mdl.chat(prompt, history, **kwargs)
    
    async def async_chat(self, prompt, history=None, **kwargs):
        """异步调用"""
        return await self.mdl.async_chat(prompt, history, **kwargs)
    
    async def async_chat_streamly(self, prompt, history=None, **kwargs):
        """流式调用"""
        async for chunk in self.mdl.async_chat_streamly(prompt, history, **kwargs):
            yield chunk
```

#### 3.2.2 模型实例化

**代码位置**: `rag/llm/chat_model.py`

```python
class Base(ABC):
    def __init__(self, key, model_name, base_url, **kwargs):
        # 超时配置
        timeout = int(os.environ.get("LLM_TIMEOUT_SECONDS", 600))
        
        # 同步/异步客户端
        self.client = OpenAI(api_key=key, base_url=base_url, timeout=timeout)
        self.async_client = AsyncOpenAI(api_key=key, base_url=base_url, timeout=timeout)
        
        # 重试配置
        self.max_retries = kwargs.get("max_retries", int(os.environ.get("LLM_MAX_RETRIES", 5)))
        self.base_delay = kwargs.get("retry_interval", float(os.environ.get("LLM_BASE_DELAY", 2.0)))
        self.max_rounds = kwargs.get("max_rounds", 5)
```

### 3.3 流式 vs 非流式调用

#### 3.3.1 非流式调用

```python
async def async_chat(self, system: str, history: list, gen_conf: dict = {}) -> Tuple[str, int]:
    """非流式：等待完整响应"""
    
    # 构建请求
    if system and history and history[0].get("role") != "system":
        history.insert(0, {"role": "system", "content": system})
    
    request_kwargs = {
        "model": self.model_name,
        "messages": history,
        **gen_conf
    }
    
    # 发送请求
    response = await self.async_client.chat.completions.create(**request_kwargs)
    
    # 提取结果
    answer = response.choices[0].message.content
    total_tokens = response.usage.total_tokens
    
    return answer, total_tokens
```

#### 3.3.2 流式调用

```python
async def _async_chat_streamly(self, history, gen_conf, **kwargs):
    """流式：逐块返回"""
    
    request_kwargs = {
        "model": self.model_name,
        "messages": history,
        "stream": True,  # 关键参数
        **gen_conf
    }
    
    response = await self.async_client.chat.completions.create(**request_kwargs)
    
    # 逐块迭代
    async for resp in response:
        if not resp.choices:
            continue
        
        delta = resp.choices[0].delta
        if delta.content:
            yield delta.content  # 实时 yield
        
        # 处理思考内容（部分模型支持）
        _reasoning = getattr(delta, "reasoning_content", None)
        if _reasoning and kwargs.get("with_reasoning", True):
            yield f"<think>{_reasoning}</think>"
```

### 3.4 超时和重试机制

#### 3.4.1 错误分类

**代码位置**: `rag/llm/chat_model.py`

```python
class LLMErrorCode(StrEnum):
    ERROR_RATE_LIMIT = "RATE_LIMIT_EXCEEDED"      # 429
    ERROR_AUTHENTICATION = "AUTH_ERROR"            # 401
    ERROR_INVALID_REQUEST = "INVALID_REQUEST"     # 400
    ERROR_SERVER = "SERVER_ERROR"                 # 5xx
    ERROR_TIMEOUT = "TIMEOUT"
    ERROR_CONNECTION = "CONNECTION_ERROR"
    ERROR_QUOTA = "QUOTA_EXCEEDED"
    ERROR_MODEL = "MODEL_ERROR"
    ERROR_MAX_ROUNDS = "ERROR_MAX_ROUNDS"
    ERROR_CONTENT_FILTER = "CONTENT_FILTERED"
    ERROR_MAX_RETRIES = "MAX_RETRIES_EXCEEDED"
    ERROR_GENERIC = "GENERIC_ERROR"

def _classify_error(self, error):
    """根据错误信息关键词分类"""
    keywords_mapping = [
        (["quota", "capacity", "credit", "billing"], LLMErrorCode.ERROR_QUOTA),
        (["rate limit", "429", "too many requests"], LLMErrorCode.ERROR_RATE_LIMIT),
        (["auth", "401", "forbidden"], LLMErrorCode.ERROR_AUTHENTICATION),
        (["timeout", "timed out"], LLMErrorCode.ERROR_TIMEOUT),
        # ...
    ]
```

#### 3.4.2 指数退避重试

```python
def _get_delay(self):
    """计算重试延迟（指数退避 + 随机抖动）"""
    return self.base_delay * random.uniform(10, 150)

async def _exceptions_async(self, error, attempt):
    """异常处理与重试"""
    error_code = self._classify_error(error)
    
    # 不重试的错误
    if error_code in [LLMErrorCode.ERROR_AUTHENTICATION, LLMErrorCode.ERROR_MODEL]:
        return error
    
    # 达到最大重试次数
    if attempt >= self.max_retries:
        return LLMErrorCode.ERROR_MAX_RETRIES
    
    # 指数退避
    delay = self._get_delay()
    logging.warning(f"Retry {attempt + 1}/{self.max_retries} after {delay}s")
    await asyncio.sleep(delay)
    
    return None  # 返回 None 表示继续重试
```

### 3.5 Token 计数和成本控制

#### 3.5.1 Token 计算

**代码位置**: `common/token_utils.py`

```python
def num_tokens_from_string(text: str) -> int:
    """计算文本的 Token 数量"""
    encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 编码
    return len(encoding.encode(text))

def total_token_count_from_response(response) -> int:
    """从 API 响应中提取 Token 使用量"""
    if hasattr(response, 'usage') and response.usage:
        return response.usage.total_tokens
    return 0
```

#### 3.5.2 成本追踪

**代码位置**: `api/db/services/tenant_llm_service.py`

```python
class TenantLLMService:
    @classmethod
    def increase_usage_by_id(cls, model_id: str, tokens: int) -> bool:
        """记录 Token 使用量"""
        try:
            model = cls.model.get(cls.model.id == model_id)
            model.used_tokens += tokens
            model.save()
            return True
        except Exception as e:
            logging.error(f"Failed to update usage: {e}")
            return False
```

---

## 第四章：检索增强对话流程

### 4.1 完整流程图

```
用户问题
    │
    ▼
┌─────────────────┐
│  Query 预处理    │  - 关键词提取
│  (keyword)      │  - 查询扩展
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  向量检索        │  - Embedding 模型
│  (Vector Search)│  - Top-K 召回
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  混合评分        │  - 向量相似度 × 权重
│  (Hybrid Score) │  - 关键词匹配 × 权重
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Re-rank 精排    │  - 交叉编码器重排
│  (Rerank)       │  - Top-N 选择
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Prompt 构建    │  - 注入知识库内容
│  (Prompt Gen)   │  - 引用标注规则
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM 生成       │  - 流式输出
│  (Generation)   │  - 引用标注
└────────┬────────┘
         │
         ▼
    返回结果
```

### 4.2 检索结果选择策略

#### 4.2.1 Top-K 和相似度阈值

**代码位置**: `api/db/services/dialog_service.py`

```python
kbinfos = await retriever.retrieval(
    question=question,
    embd_mdl=embd_mdl,
    tenant_ids=tenant_ids,
    kb_ids=kb_ids,
    page=1,
    page_size=12,  # 检索 12 个 Chunk
    similarity_threshold=search_config.get("similarity_threshold", 0.1),  # 最低阈值
    vector_similarity_weight=search_config.get("vector_similarity_weight", 0.3),
    top=search_config.get("top_k", 1024),
    rerank_mdl=rerank_mdl,  # 可选的 Re-rank 模型
    rank_feature=label_question(question, kbs)  # 问题分类特征
)
```

#### 4.2.2 混合评分公式

```
final_score = vector_similarity_weight × vector_score 
             + (1 - vector_similarity_weight) × term_score
```

其中：
- `vector_score`: 向量余弦相似度 (0-1)
- `term_score`: BM25 关键词匹配得分
- 默认 `vector_similarity_weight = 0.3`（向量化权重较低）

### 4.3 空检索结果的处理

#### 4.3.1 空结果响应模板

**代码位置**: `api/apps/restful_apis/chat_api.py`

```python
_DEFAULT_PROMPT_CONFIG = {
    # ...
    "empty_response": "Sorry! No relevant content was found in the knowledge base!",
}
```

#### 4.3.2 Prompt 中的空结果处理

```python
def _build_knowledge_prompt(dia, kbinfos, max_tokens):
    """构建知识库提示词，处理空结果"""
    
    knowledges = kb_prompt(kbinfos, max_tokens)
    
    if not knowledges:
        # 使用默认的空结果提示词
        return dia.prompt_config.get("empty_response", "")
    
    # 构建完整提示词
    sys_prompt = dia.prompt_config.get("system", "")
    sys_prompt = sys_prompt.replace("{knowledge}", "\n".join(knowledges))
    
    return sys_prompt
```

### 4.4 混合检索实现

#### 4.4.1 检索器架构

**代码位置**: `rag/settings.py` / `rag/svr/__init__.py`

```python
class Retriever:
    def __init__(self):
        self.vector_search = VectorSearch()    # 向量检索
        self.bm25_search = BM25Search()       # 关键词检索
        self.hybrid_search = HybridSearch()    # 混合检索
    
    async def retrieval(self, question, embd_mdl, **kwargs):
        """统一检索入口"""
        
        # 1. 向量检索
        vector_results = await self.vector_search.search(
            question, embd_mdl, top_k=kwargs.get("top_k", 1024)
        )
        
        # 2. 关键词检索（可选）
        if kwargs.get("enable_keyword_search"):
            bm25_results = await self.bm25_search.search(question)
        
        # 3. 混合评分
        hybrid_results = self._hybrid_fusion(
            vector_results,
            bm25_results,
            vector_weight=kwargs.get("vector_similarity_weight", 0.3)
        )
        
        # 4. 过滤低分结果
        filtered = [r for r in hybrid_results 
                   if r["score"] >= kwargs.get("similarity_threshold", 0.1)]
        
        # 5. Re-rank（可选）
        if kwargs.get("rerank_mdl"):
            filtered = await self._rerank(filtered, kwargs["rerank_mdl"], question)
        
        return {"chunks": filtered, "doc_aggs": [...]}
```

---

## 第五章：Agent 能力

### 5.1 Agent 引擎概述

RAGFlow 的 Agent 引擎基于 **Canvas 编排** 机制，允许用户通过可视化拖拽构建复杂的工作流。

### 5.2 Canvas 编排机制

#### 5.2.1 Graph 数据结构

**代码位置**: `agent/canvas.py`

```python
class Graph:
    """
    Canvas 工作流图结构
    """
    dsl = {
        "components": {
            "begin": {
                "obj": {
                    "component_name": "Begin",
                    "params": {},
                },
                "downstream": ["retrieval_0"],  # 下游节点
                "upstream": [],                  # 上游节点
            },
            "retrieval_0": {
                "obj": {
                    "component_name": "Retrieval",
                    "params": {"kb_ids": [...]}
                },
                "downstream": ["generate_0"],
                "upstream": ["begin"],
            },
            "generate_0": {
                "obj": {
                    "component_name": "Generate",
                    "params": {"llm_id": "gpt-4"}
                },
                "downstream": ["end"],
                "upstream": ["retrieval_0"],
            }
        },
        "globals": {
            "sys.query": "",
            "sys.user_id": "",
            "sys.conversation_turns": 0,
        }
    }
```

#### 5.2.2 组件类型

**代码位置**: `agent/component/`

| 组件类型 | 说明 | 关键文件 |
|---------|------|---------|
| **Begin** | 工作流入口 | `begin.py` |
| **Retrieval** | 知识库检索 | `retrieval.py` |
| **Generate/LLM** | LLM 生成 | `llm.py` |
| **Agent** | Agent 推理 | `agent_with_tools.py` |
| **Categorize** | 条件分支 | `categorize.py` |
| **Iteration** | 循环迭代 | `iteration.py` |
| **Switch** | 多条件分支 | `switch.py` |
| **Invoke** | HTTP 调用 | `invoke.py` |
| **Message** | 消息输出 | `message.py` |
| **Variable** | 变量操作 | `variable_*.py` |

### 5.3 工具调用（Tool Use）

#### 5.3.1 Agent 定义

**代码位置**: `agent/component/agent_with_tools.py`

```python
class Agent(LLM, ToolBase):
    component_name = "Agent"
    
    def __init__(self, canvas, id, param: LLMParam):
        LLM.__init__(self, canvas, id, param)
        
        # 加载工具
        self.tools = {}
        for idx, cpn in enumerate(self._param.tools):
            cpn = self._load_tool_obj(cpn)
            indexed_name = f"{cpn.get_meta()['function']['name']}_{idx}"
            self.tools[indexed_name] = cpn
        
        # 配置支持工具调用的 LLM
        self.chat_mdl = LLMBundle(
            tenant_id,
            chat_model_config,
            max_retries=self._param.max_retries,
            max_rounds=self._param.max_rounds,  # 最大迭代轮次
        )
```

#### 5.3.2 工具调用循环

**代码位置**: `rag/llm/chat_model.py`

```python
async def async_chat_streamly_with_tools(self, system: str, history: list, gen_conf: dict = {}):
    """带工具调用的流式对话"""
    
    tools = self.tools
    
    for _round in range(self.max_rounds):
        # 1. 调用 LLM
        completion_args = self._construct_completion_args(
            history=history, 
            stream=True, 
            tools=True,  # 启用工具
            **gen_conf
        )
        response = await litellm.acompletion(**completion_args)
        
        # 2. 收集工具调用
        final_tool_calls = {}
        answer = ""
        
        async for resp in response:
            delta = resp.choices[0].delta
            
            # 处理工具调用
            if hasattr(delta, "tool_calls") and delta.tool_calls:
                for tool_call in delta.tool_calls:
                    index = tool_call.index
                    final_tool_calls[index] = tool_call
                continue
            
            # 处理普通文本
            if delta.content:
                answer += delta.content
                yield delta.content
        
        # 3. 执行工具
        if final_tool_calls:
            for tc in final_tool_calls.values():
                name = tc.function.name
                args = json_repair.loads(tc.function.arguments)
                
                # 执行工具
                result = await tool_call_session.tool_call_async(name, args)
                
                # 添加到历史
                history.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": name,
                    "content": str(result)
                })
            continue  # 继续下一轮
        
        # 4. 无工具调用，返回结果
        if answer:
            yield total_tokens
            return
    
    # 超过最大轮次
    yield "Exceed max rounds"
```

### 5.4 多 Agent 协作

#### 5.4.1 子 Agent 定义

**代码位置**: `agent/component/agent_with_tools.py`

```python
class AgentParam(LLMParam, ToolParamBase):
    def __init__(self):
        self.meta: ToolMeta = {
            "name": "agent",
            "description": "This is an agent for a specific task.",
            "parameters": {
                "user_prompt": {"type": "string", "required": True},
                "reasoning": {"type": "string", "required": True},
                "context": {"type": "string", "required": True},
            },
        }
        self.function_name = "agent"
        self.tools = []
        self.mcp = []
        self.max_rounds = 5
```

#### 5.4.2 协作模式

```
┌─────────────────────────────────────────────────────────────┐
│                      Supervisor Agent                        │
│  - 理解用户意图                                              │
│  - 分解任务                                                 │
│  - 调用子 Agent                                             │
│  - 整合结果                                                 │
└─────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │ Research    │       │ Analysis    │       │ Writing     │
    │ Agent       │       │ Agent       │       │ Agent       │
    │             │       │             │       │             │
    │ - 搜索信息  │       │ - 数据分析  │       │ - 撰写报告  │
    │ - 收集资料  │       │ - 趋势判断  │       │ - 格式整理  │
    └─────────────┘       └─────────────┘       └─────────────┘
```

---

## 第六章：Prompt 工程最佳实践

### 6.1 知识库问答的 Prompt 模板设计

#### 6.1.1 基础模板结构

```markdown
## 角色定义
你是一个专业的AI助手，名字是 [名字]。

## 任务描述
请根据以下知识库内容，回答用户的问题。

## 核心约束
1. **禁止编造**: 不要编造数字、日期、事实等具体信息
2. **诚实回答**: 如果知识库没有相关信息，明确告知用户
3. **语言一致**: 使用与问题相同的语言回答
4. **格式规范**: 使用 Markdown 格式化回答

## 知识库内容
{knowledge}

## 用户问题
{question}

## 回答
```

#### 6.1.2 进阶模板（带引用）

```markdown
## 角色
你是一个专业的知识库问答助手。

## 任务
基于提供的参考资料生成回答，并在适当位置添加引用标注 [ID:x]。

## 引用规则
- 数字、日期、统计数据必须引用
- 直接引用的内容必须引用
- 常识性内容不需要引用

## 参考资料
{knowledge}

## 问题
{question}

## 要求
1. 回答必须基于参考资料
2. 不确定的信息不要编造
3. 引用格式: [ID:0], [ID:1], [ID:0][ID:2]
```

### 6.2 减少幻觉的策略

#### 6.2.1 约束注入

```python
# 在 Prompt 中明确约束
CONSTRAINTS = """
### 约束规则
1. 如果知识库中没有相关信息，必须回答"对不起，知识库中没有找到相关信息"
2. 禁止编造任何数字、日期、统计数据
3. 对于不确定的信息，必须标注"根据现有资料无法确定"
4. 只使用知识库中的信息，不要添加外部知识
"""
```

#### 6.2.2 置信度评估

```python
async def check_confidence(question, answer, knowledge_chunks):
    """评估回答的置信度"""
    
    # 检查是否引用了知识库
    cited_ids = extract_citation_ids(answer)
    
    # 检查是否有过多未引用的陈述
    uncited_statements = count_uncited_claims(answer)
    
    # 检查是否包含不确定性语言
    uncertain_phrases = ["可能", "也许", "大概", "perhaps", "maybe"]
    has_uncertainty = any(p in answer.lower() for p in uncertain_phrases)
    
    # 综合评分
    confidence = 1.0
    if not cited_ids:
        confidence -= 0.3
    if uncited_statements > 3:
        confidence -= 0.2
    if not has_uncertainty and uncited_statements > 0:
        confidence -= 0.2
    
    return confidence
```

### 6.3 引用准确性的提升

#### 6.3.1 引用格式规范化

```markdown
## 引用标注规范

### 格式要求
- 单个引用: [ID:0]
- 多个引用: [ID:0][ID:1]（注意：不是逗号分隔）
- 位置: 句子末尾，标点符号之前

### 引用示例
✅ 正确: "公司2024年收入达到1.2亿元[ID:0]。"
❌ 错误: "公司收入[ID:0]达到1.2亿元。"

### 合并引用规则
- 同一来源的多个事实可以合并: [ID:0][ID:0]
- 不同来源支持同一观点: [ID:0][ID:1]
- 最多4个引用: [ID:0][ID:1][ID:2][ID:3]
```

#### 6.3.2 引用来源元数据

```python
def format_chunk_reference(chunk):
    """格式化 Chunk 为引用格式"""
    return f"""
ID: {chunk['chunk_id']}
├── Title: {chunk['document_name']}
├── Section: {chunk.get('section_title', 'N/A')}
└── Content:
{chunk['content']}
"""
```

### 6.4 不同场景的 Prompt 优化

#### 6.4.1 技术文档问答

```markdown
## 角色
你是一个技术文档助手，擅长解释技术概念和代码。

## 约束
- 使用技术术语时给出解释
- 代码块要标注语言
- API 说明要包含参数和返回值

## 知识库
{knowledge}

## 问题
{question}
```

#### 6.4.2 财务报告分析

```markdown
## 角色
你是一个财务分析师，擅长解读财务数据和报告。

## 约束
- 所有数字必须精确到小数点后两位
- 同比/环比变化必须标注
- 风险提示要明确

## 知识库
{knowledge}

## 问题
{question}
```

#### 6.4.3 客服对话

```markdown
## 角色
你是一个热情的客服代表，名字是小明。

## 风格
- 友好、专业、有耐心
- 使用"您"称呼用户
- 主动提供帮助

## 约束
- 涉及退款/投诉要转人工
- 不承诺无法兑现的事情
- 保护用户隐私

## 知识库
{knowledge}

## 问题
{question}
```

---

## 附录：关键代码索引

| 功能模块 | 代码位置 | 关键类/函数 |
|---------|---------|------------|
| 对话 API | `api/apps/restful_apis/chat_api.py` | `create()`, `completion()` |
| 对话服务 | `api/db/services/dialog_service.py` | `async_chat()` |
| 会话服务 | `api/db/services/conversation_service.py` | `ConversationService` |
| LLM 调用 | `rag/llm/chat_model.py` | `Base`, `async_chat_streamly()` |
| LLM Bundle | `api/db/services/llm_service.py` | `LLMBundle` |
| Prompt 模板 | `rag/prompts/generator.py` | `kb_prompt()`, `citation_prompt()` |
| 引用标注 | `rag/prompts/citation_prompt.md` | Citation 规则定义 |
| Canvas 引擎 | `agent/canvas.py` | `Graph` |
| Agent 组件 | `agent/component/agent_with_tools.py` | `Agent` |
| LLM 组件 | `agent/component/llm.py` | `LLM` |
| 工具基类 | `agent/tools/base.py` | `ToolBase` |
| 流式处理 | `api/db/services/dialog_service.py` | `_ThinkStreamState` |

---

## 术语表

| 术语 | 小白版解释 |
|------|-----------|
| **Prompt** | 给 AI 的"工作指令书"，告诉 AI 怎么回答 |
| **Token** | 文字的最小单位，大约 1 个中文 = 1-2 个 Token |
| **Embedding** | 把文字变成"数字指纹"，方便比较相似度 |
| **Vector Search** | 在"指纹库"里找相似的指纹 |
| **Re-rank** | 初筛后再精挑细选，确保最好的结果排前面 |
| **流式响应** | "说一句显示一句"，不用等全部说完 |
| **工具调用** | AI 不仅能回答，还能执行具体操作 |
| **Canvas** | 可视化画板，拖拖拽拽设计 AI 工作流 |
| **多轮对话** | 聊天不是一次性的，有上下文记忆 |
| **幻觉** | AI 胡说八道，编造不存在的知识 |

---

*文档生成时间: 2024年*  
*参考版本: RAGFlow 最新版本*
