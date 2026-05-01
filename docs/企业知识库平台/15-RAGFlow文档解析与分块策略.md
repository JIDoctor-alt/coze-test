# RAGFlow DeepDoc 文档解析引擎与分块策略深度解析

> **文档解析 = 把各种格式的文件翻译成AI能理解的文本**  
> **分块 = 把一本书拆成一页页卡片**  
> **OCR = 让电脑识字，把图片里的文字读出来**

---

## 目录

1. [DeepDoc 引擎架构](#part-1-deepdoc引擎架构)
2. [各格式解析详解](#part-2-各格式解析详解)
3. [分块策略详解](#part-3-分块策略详解)
4. [OCR 集成](#part-4-ocr集成)
5. [表格提取专题](#part-5-表格提取专题)
6. [MinerU vs DeepDoc 详细对比](#part-6-mineru-vs-deepdoc详细对比)

---

## Part 1: DeepDoc 引擎架构

### 1.1 目录结构总览

```
/deepdoc/
├── __init__.py              # 包入口，导出核心类
├── vision/                  # 视觉处理模块（OCR + 布局分析）
│   ├── __init__.py
│   ├── ocr.py              # OCR 引擎核心实现
│   ├── recognizer.py        # 通用识别器基类
│   ├── layout_recognizer.py # 页面布局识别（YOLO系列）
│   ├── table_structure_recognizer.py  # 表格结构识别
│   ├── operators.py         # 图像预处理算子
│   ├── postprocess.py       # 后处理工具
│   ├── seeit.py            # 可视化工具
│   ├── t_ocr.py            # 文本方向 OCR
│   └── t_recognizer.py     # 文本方向识别
└── parser/                  # 文档解析器模块
    ├── __init__.py          # 解析器统一导出
    ├── pdf_parser.py        # PDF 解析器 (2079行，核心)
    ├── docx_parser.py       # Word 文档解析器
    ├── excel_parser.py      # Excel 解析器
    ├── ppt_parser.py        # PPT 解析器
    ├── markdown_parser.py   # Markdown 解析器
    ├── html_parser.py       # HTML 解析器
    ├── txt_parser.py        # 纯文本解析器
    ├── json_parser.py       # JSON 解析器
    ├── epub_parser.py       # EPUB 电子书解析器
    ├── tcadp_parser.py      # CAD图纸解析器
    ├── mineru_parser.py     # MinerU 后端解析器
    ├── docling_parser.py    # Docling 后端解析器
    ├── paddleocr_parser.py  # PaddleOCR 封装
    ├── figure_parser.py     # 图片解析器
    ├── utils.py             # 工具函数
    └── resume/              # 简历解析模块
        ├── step_one.py      # 简历解析第一步
        └── step_two.py      # 简历解析第二步
```

### 1.2 核心模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| **OCR引擎** | `vision/ocr.py` | 文字检测 + 识别，文字方向自动校正 |
| **布局识别** | `vision/layout_recognizer.py` | 识别页面元素类型（标题/正文/表格/图片等）|
| **表格识别** | `vision/table_structure_recognizer.py` | 表格行列结构、合并单元格检测 |
| **PDF解析** | `parser/pdf_parser.py` | PDF文件解析核心，文字+布局+表格联合处理 |
| **分块策略** | `rag/nlp/__init__.py` | 多种分块算法实现 |

### 1.3 文件处理流水线

```
┌─────────────────────────────────────────────────────────────────────┐
│                        文件上传                                      │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     格式识别与路由                                   │
│  ┌────────┬────────┬────────┬────────┬────────┬────────┐           │
│  │  PDF   │  DOCX  │  XLSX  │  PPT   │  MD    │  IMG   │           │
│  └────────┴────────┴────────┴────────┴────────┴────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     DeepDoc 解析引擎                                 │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │ PyMuPDF/ │ →  │ 布局识别 │ →  │   OCR    │ →  │ 表格识别 │      │
│  │ pdfplumber│    │(YOLO)   │    │(Paddle)  │    │ (TSR)   │      │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘      │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                      │
│  │ 乱码检测 │ →  │ 文字合并 │ →  │ 双向连接 │                      │
│  │          │    │          │    │ (XGBoost)│                      │
│  └──────────┘    └──────────┘    └──────────┘                      │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     分块处理 (Chunking)                              │
│  ┌────────┬────────┬────────┬────────┬────────┬────────┬────────┐  │
│  │ naive  │ manual │  q&a   │ table  │ paper  │ book   │ laws   │  │
│  └────────┴────────┴────────┴────────┴────────┴────────┴────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     向量化与索引                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.4 核心类关系图

```
RAGFlowPdfParser (pdf_parser.py)
    │
    ├── __init__()
    │   ├── self.ocr = OCR()                           # OCR 引擎
    │   ├── self.layouter = LayoutRecognizer()         # 布局识别器
    │   └── self.tbl_det = TableStructureRecognizer()  # 表格结构识别器
    │
    ├── __call__(fnm, need_image, zoomin, return_html, auto_rotate_tables)
    │   │
    │   └── parse_into_bboxes() → _parse_loaded_window_into_bboxes()
    │
    ├── 解析流程方法
    │   ├── __images__()         # PDF转图片 + pdfplumber提取字符
    │   ├── _layouts_rec()       # 布局识别
    │   ├── _table_transformer_job()  # 表格结构分析
    │   ├── _text_merge()        # 文字合并
    │   ├── _concat_downward()   # 跨行合并（XGBoost模型）
    │   ├── _filter_forpages()   # 目录页过滤
    │   └── _extract_table_figure()  # 表格/图片提取
    │
    └── 辅助方法
        ├── _is_garbled_text()    # 乱码检测
        ├── _evaluate_table_orientation()  # 表格方向评估
        └── crop()                # 区域裁剪
```

---

## Part 2: 各格式解析详解

### 2.1 PDF 解析（PyMuPDF + 自研布局分析）

**核心文件**: `deepdoc/parser/pdf_parser.py` (2079行)

#### 2.1.1 解析流程源码分析

```python
# 入口方法 __call__ 定义
def __call__(self, fnm, need_image=True, zoomin=3, return_html=False, auto_rotate_tables=None):
    """
    解析PDF文件的主入口
    - fnm: PDF文件路径或二进制内容
    - need_image: 是否提取图片
    - zoomin: 图片放大倍数（默认3倍）
    - return_html: 表格是否返回HTML格式
    - auto_rotate_tables: 表格自动旋转校正
    """
    self.outlines = extract_pdf_outlines(fnm)  # 提取书签目录
    self.__images__(fnm, zoomin)              # PDF转图片
    self._layouts_rec(zoomin)                 # 布局识别
    self._table_transformer_job(zoomin, auto_rotate=auto_rotate_tables)  # 表格处理
    self._text_merge()                       # 文字合并
    self._concat_downward()                  # 双向连接
    self._filter_forpages()                  # 目录过滤
    tbls = self._extract_table_figure(need_image, zoomin, return_html, False)
    return self.__filterout_scraps(deepcopy(self.boxes), zoomin), tbls
```

#### 2.1.2 乱码检测机制

DeepDoc 实现了**两层乱码检测策略**：

**策略1: PUA/CID字符检测**
```python
# 检测私有使用区(PUA)字符和未映射的CID
@staticmethod
def _is_garbled_char(ch):
    """检查单个字符是否为乱码"""
    cp = ord(ch)
    # 私有使用区: E000-F8FF
    if 0xE000 <= cp <= 0xF8FF:
        return True
    # 补充私有使用区
    if 0xF0000 <= cp <= 0xFFFFD or 0x100000 <= cp <= 0x10FFFF:
        return True
    # Unicode替换字符
    if cp == 0xFFFD:
        return True
    # CID占位符模式 (cid:数字)
    # ... 更多检测
```

**策略2: 字体编码乱码检测**
```python
# 检测子集字体映射到ASCII导致的乱码
@staticmethod
def _is_garbled_by_font_encoding(page_chars, min_chars=20):
    """检测因PDF字体编码错误导致的乱码"""
    for c in page_chars:
        fontname = c.get("fontname", "")
        # 检查是否子集字体（6字母+加号前缀）
        if _has_subset_font_prefix(fontname):
            subset_font_count += 1
        
        # 检测CJK字符占比
        if 0x2E80 <= cp <= 0x9FFF:  # CJK统一表意文字
            cjk_like += 1
        elif 0x21 <= cp <= 0x7E:    # ASCII标点符号
            ascii_punct_sym += 1
    
    # 乱码条件：子集字体占比>30% 且 CJK占比<5% 且 标点占比>40%
    return cjk_ratio < 0.05 and punct_ratio > 0.4
```

#### 2.1.3 表格自动方向校正

```python
def _evaluate_table_orientation(self, table_img, sample_ratio=0.3):
    """评估表格最佳旋转角度"""
    rotations = [(0, "original"), (90, "rotate_90"), (180, "rotate_180"), (270, "rotate_270")]
    
    for angle, name in rotations:
        # 旋转后进行OCR
        rotated_img = table_img.rotate(-angle, expand=True)
        ocr_results = self.ocr(rotated_img)
        
        # 计算平均置信度 + 区域数量
        scores = [conf for _, (_, conf) in ocr_results]
        combined_score = avg_score * (1 + 0.1 * min(total_regions, 50) / 50)
    
    # 选择最优角度
    # 绝对阈值规则：非0°必须比0°高0.2以上，且0°分数低于0.8
    if best_score - score_0 > 0.2 and score_0 < 0.8:
        best_angle = angle
```

### 2.2 Word 解析（python-docx）

**核心文件**: `deepdoc/parser/docx_parser.py`

```python
class RAGFlowDocxParser:
    def __call__(self, fnm, from_page=0, to_page=MAXIMUM_PAGE_NUMBER):
        self.doc = Document(fnm) if isinstance(fnm, str) else Document(BytesIO(fnm))
        
        # 1. 解析段落
        for p in self.doc.paragraphs:
            # 处理分页符
            if 'lastRenderedPageBreak' in run._element.xml:
                pn += 1
            # 提取段落文本和样式
            runs_within_single_paragraph.append(run.text)
            secs.append(("".join(runs_within_single_paragraph), p.style.name))
        
        # 2. 解析表格
        tbls = [self.__extract_table_content(tb) for tb in self.doc.tables]
        
        return secs, tbls
```

**表格内容提取逻辑**:
```python
def __compose_table_content(self, df):
    """根据列类型智能判断表头位置"""
    # 统计每列数据类型
    block_types = ["Dt"(日期), "Nu"(数字), "Tx"(文本), "Lx"(长文本), "Nr"(专名)]
    max_type = Counter([blockType(cell) for cell in df.iloc[1:, :]])
    
    # 如果数字最多，第一行为表头
    if max_type == "Nu":
        for r in range(1, len(df)):
            # 统计该行数字占比，非数字则加入表头行
            if types != max_type:
                hdrows.append(r)
```

### 2.3 Excel 解析（openpyxl + pandas）

**核心文件**: `deepdoc/parser/excel_parser.py`

```python
class RAGFlowExcelParser:
    def __call__(self, fnm):
        wb = RAGFlowExcelParser._load_excel_to_workbook(fnm)
        
        for sheetname in wb.sheetnames:
            ws = wb[sheetname]
            rows = RAGFlowExcelParser._get_rows_limited(ws)
            
            # 第一行为表头
            ti = list(rows[0])
            for r in rows[1:]:
                # 拼接: "表头名: 单元格值"
                fields.append(f"{ti[i].value}：{c.value}")
        
        return res  # ["年份：2023; 销售额：100万", ...]
```

**多引擎兜底策略**:
```python
@staticmethod
def _load_excel_to_workbook(file_like_object):
    # 1. 尝试 openpyxl（支持xlsx）
    try:
        return load_workbook(file_like_object, data_only=True)
    except Exception as e:
        logging.info(f"openpyxl error: {e}")
    
    # 2. 兜底 pandas
    try:
        dfs = pd.read_excel(file_like_object, sheet_name=None)
        return _dataframe_to_workbook(dfs)
    except Exception as e:
        logging.info(f"pandas error: {e}")
    
    # 3. 最后兜底 calamine 引擎
    df = pd.read_excel(file_like_object, engine="calamine")
```

### 2.4 PPT 解析

**核心文件**: `deepdoc/parser/ppt_parser.py`

```python
class RAGFlowPptParser:
    def __call__(self, fnm, from_page, to_page, callback=None):
        ppt = Presentation(fnm)
        
        for i, slide in enumerate(ppt.slides):
            if i < from_page or i >= to_page:
                continue
            
            for shape in self.__sort_shapes(slide.shapes):
                txt = self.__extract(shape)
                # 处理表格 (shape_type == 19)
                if shape_type == 19:
                    tb = shape.table
                    rows.append("; ".join([f"{tb.cell(0,j).text}: {tb.cell(i,j).text}"]))
                
                # 处理组合形状 (shape_type == 6)
                if shape_type == 6:
                    for p in shape.shapes:
                        t = self.__extract(p)
```

### 2.5 Markdown 解析

**核心文件**: `deepdoc/parser/markdown_parser.py`

```python
class MarkdownElementExtractor:
    """提取Markdown元素：标题、代码块、列表、引用等"""
    
    def extract_elements(self, delimiter=None, include_meta=False):
        sections = []
        while i < len(self.lines):
            line = self.lines[i]
            
            if re.match(r"^#{1,6}\s+.*$", line):
                # 标题
                element = self._extract_header(i)
            elif line.strip().startswith("```"):
                # 代码块
                element = self._extract_code_block(i)
            elif re.match(r"^\s*[-*+]\s+.*$", line):
                # 列表
                element = self._extract_list_block(i)
            elif line.strip().startswith(">"):
                # 引用
                element = self._extract_blockquote(i)
            else:
                # 文本段落
                element = self._extract_text_block(i)
```

---

## Part 3: 分块策略详解

### 3.1 分块策略总览

RAGFlow 支持 **7种分块模式**，定义在 `rag/nlp/__init__.py` 中：

| 模式 | 适用场景 | 分块逻辑 |
|------|----------|----------|
| **naive** | 通用文档 | 按固定token数切分，句号/换行为边界 |
| **manual** | 手动标注 | 按层级标题（目录结构）分块 |
| **q&a** | 问答对 | 识别问答对，提取问答模式 |
| **table** | 表格文档 | 保持表格行列结构 |
| **paper** | 学术论文 | 按摘要/引言/方法/结果/讨论分块 |
| **book** | 书籍 | 按章节结构分块 |
| **laws** | 法律条文 | 按条款编号分块 |

### 3.2 Naive 模式：简单分块

**naive分块 = 暴力拆，按固定长度切**

```python
def naive_merge(sections, chunk_token_num=128, delimiter="\n。；！？", overlapped_percent=0):
    """
    朴素分块算法
    
    参数:
        sections: 文本段落列表
        chunk_token_num: 每个chunk的token数量上限（默认128）
        delimiter: 分隔符（默认中文句号和换行）
        overlapped_percent: 相邻chunk的重叠百分比
    """
    cks = [""]
    tk_nums = [0]
    
    def add_chunk(t, pos):
        tnum = num_tokens_from_string(t)
        
        # 检查当前chunk是否已满
        if cks[-1] == "" or tk_nums[-1] > chunk_token_num * (100 - overlapped_percent) / 100:
            # 创建新chunk，包含前一个chunk的尾部（重叠部分）
            if cks:
                overlapped = RAGFlowPdfParser.remove_tag(cks[-1])
                t = overlapped[int(len(overlapped) * (100 - overlapped_percent) / 100):] + t
            cks.append(t)
            tk_nums.append(tnum)
        else:
            # 追加到当前chunk
            cks[-1] += t
            tk_nums[-1] += tnum
    
    # 自定义分隔符处理（如代码块标记 `---`）
    custom_delimiters = [m.group(1) for m in re.finditer(r"`([^`]+)`", delimiter)]
    if custom_delimiters:
        # 按自定义分隔符分割
        for sec, pos in sections:
            split_sec = re.split(r"(%s)" % custom_pattern, sec, flags=re.DOTALL)
            # ...
    
    for sec, pos in sections:
        add_chunk("\n" + sec, pos)
    
    return cks
```

**分块示例**:
```
原文: "今天天气很好。我们去公园吧。明天还要上班。"

chunk_token_num=10, delimiter="。！？":
  chunk1: "今天天气很好。"
  chunk2: "我们去公园吧。"
  chunk3: "明天还要上班。"
```

### 3.3 Manual 模式：手动标注/层级标题

**manual模式 = 按文档结构（标题层级）分块**

```python
# 标题匹配模式（BULLET_PATTERN）
BULLET_PATTERN = [
    # 中文书籍模式
    [
        r"第[零一二三四五六七八九十百0-9]+(分?编|部分)",
        r"第[零一二三四五六七八九十百0-9]+章",
        r"第[零一二三四五六七八九十百0-9]+节",
        r"第[零一二三四五六七八九十百0-9]+条",
    ],
    # 阿拉伯数字模式
    [
        r"第[0-9]+章",
        r"第[0-9]+节",
        r"[0-9]{,2}[\.、]",
        r"[0-9]{,2}\.[0-9]{,2}[^a-zA-Z/%~-]",
    ],
    # Markdown模式
    [
        r"^#[^#]",      # # 标题1
        r"^##[^#]",     # ## 标题2
        r"^###.*",      # ### 标题3
        r"^####.*",     # #### 标题4
    ]
]

def tree_merge(bull, sections, depth):
    """
    按标题层级构建文档树
    
    参数:
        bull: 标题模式索引（0=中文，1=数字，2=中文序号，3=英文，4=Markdown）
        sections: 文本段落列表
        depth: 分块深度（1=最高级标题，2=二级标题，...）
    """
    # 1. 为每个段落分配层级
    for section in sections:
        level, text = get_level(bull, section)
        lines.append((level, text))
    
    # 2. 构建树结构
    root = Node(level=0, depth=target_level, texts=[])
    root.build_tree(lines)
    
    # 3. 提取树节点
    return [element for element in root.get_tree() if element]
```

**分块示例（Markdown模式，depth=2）**:
```markdown
# 第一章 入门
## 1.1 安装
正文内容...
## 1.2 配置
正文内容...

# 第二章 进阶
## 2.1 高级特性
正文内容...
```

```
chunk1: "# 第一章 入门\n## 1.1 安装\n正文内容..."
chunk2: "# 第一章 入门\n## 1.2 配置\n正文内容..."
chunk3: "# 第二章 进阶\n## 2.1 高级特性\n正文内容..."
```

### 3.4 Q&A 模式：问答对提取

**q&a分块 = 识别问答对，自动提取问题和答案**

```python
# 问答识别模式
QUESTION_PATTERN = [
    r"第([零一二三四五六七八九十百0-9]+)问",     # "第一章问"
    r"第([零一二三四五六七八九十百0-9]+)条",     # "第X条"
    r"[\\(（]([零一二三四五六七八九十百]+)[\\)）]",  # "（一）"
    r"第([0-9]+)问",                             # "第1问"
    r"([0-9]{1,2})[\.、]",                       # "1. 2."
    r"QUESTION (ONE|TWO|THREE|...)",            # 英文大写
]

def has_qbullet(reg, box, last_box, last_index, last_bull, bull_x0_list):
    """检测是否为问答段落"""
    # 匹配问题模式
    has_bull = re.match(full_reg, section)
    if has_bull:
        # 提取问题编号
        index_str = has_bull.group(1)
        index = index_int(index_str)  # 中文数字转整数
        return has_bull, index
```

### 3.5 Table 模式：表格专项

**table分块 = 专门处理表格，保持行列结构**

```python
def tokenize_table(tbls, doc, eng, batch_size=10):
    """表格分块，保留表格结构"""
    res = []
    for (img, rows), poss in tbls:
        if isinstance(rows, str):
            # 简单表格，直接返回
            d = copy.deepcopy(doc)
            tokenize(d, rows, eng)
            d["doc_type_kwd"] = "table"
            res.append(d)
            continue
        
        # 复杂表格，按batch_size分行处理
        for i in range(0, len(rows), batch_size):
            d = copy.deepcopy(doc)
            r = "; ".join(rows[i:i + batch_size])  # 用分号拼接行
            tokenize(d, r, eng)
            d["doc_type_kwd"] = "table"
            res.append(d)
```

### 3.6 Paper 模式：学术论文

**paper分块 = 按论文结构（摘要/引言/方法/结果/讨论）分块**

```python
# 学术论文标题模式
PAPER_PATTERN = [
    r"abstract",           # 摘要
    r"introduction",       # 引言
    r"related work",       # 相关工作
    r"methodology?",      # 方法
    r"experiment",        # 实验
    r"results?",          # 结果
    r"discussion",        # 讨论
    r"conclusion",        # 结论
    r"references?",        # 参考文献
]
```

### 3.7 Book 模式：书籍

**book分块 = 按章节结构分块，适合长文档**

```python
# 书籍模式使用 hierarchical_merge
def hierarchical_merge(bull, sections, depth):
    """
    层次化分块
    
    depth=1: 每个一级标题一个chunk
    depth=2: 一级标题+二级标题作为chunk
    ...
    """
    # 统计每层标题出现次数
    for i, (txt, layout) in enumerate(sections):
        for j, p in enumerate(BULLET_PATTERN[bull]):
            if re.match(p, txt.strip()):
                levels[j].append(i)
    
    # 二分搜索合并
    for j in range(depth):
        # 合并指定深度范围内的内容
        pass
```

### 3.8 Laws 模式：法律条文

**laws分块 = 按条款/条文拆，法律文件专用**

```python
# 法律条文模式
LAWS_PATTERN = [
    r"第[零一二三四五六七八九十百0-9]+条",      # 第X条
    r"第[零一二三四五六七八九十百0-9]+款",      # 第X款
    r"[\\(（][零一二三四五六七八九十百]+[\\)）]",  # （一）（二）
    r"^[0-9]+\.",                              # 1. 2.
]
```

---

## Part 4: OCR 集成

### 4.1 OCR 引擎选择

DeepDoc 支持两种 OCR 引擎：

| 引擎 | 配置 | 特点 |
|------|------|------|
| **PaddleOCR** | 默认 | 集成在 `vision/ocr.py` 中，支持多语言 |
| **Tesseract** | 需安装 | 可通过 `paddleocr_parser.py` 调用 |

### 4.2 OCR 流程详解

**核心文件**: `deepdoc/vision/ocr.py`

```python
class OCR:
    def __init__(self, model_dir=None):
        # 1. 加载检测模型 (det.onnx)
        self.text_detector = TextDetector(model_dir)
        
        # 2. 加载识别模型 (rec.onnx)
        self.text_recognizer = TextRecognizer(model_dir)
        
        # 3. 支持多GPU并行
        if settings.PARALLEL_DEVICES > 1:
            for device_id in range(settings.PARALLEL_DEVICES):
                self.text_detector.append(TextDetector(model_dir, device_id))
                self.text_recognizer.append(TextRecognizer(model_dir, device_id))
    
    def __call__(self, img, device_id=0, cls=True):
        """完整OCR流程"""
        # Step 1: 文字检测
        dt_boxes, elapse = self.text_detector(img)
        
        # Step 2: 排序文本框（从上到下、从左到右）
        dt_boxes = self.sorted_boxes(dt_boxes)
        
        # Step 3: 裁剪并识别
        for bno in range(len(dt_boxes)):
            tmp_box = copy.deepcopy(dt_boxes[bno])
            img_crop = self.get_rotate_crop_image(ori_im, tmp_box)
            img_crop_list.append(img_crop)
        
        # Step 4: 批量识别
        rec_res, elapse = self.text_recognizer(img_crop_list)
        
        # Step 5: 过滤低置信度结果
        for box, rec_result in zip(dt_boxes, rec_res):
            text, score = rec_result
            if score >= self.drop_score:
                filter_boxes.append(box)
                filter_rec_res.append(rec_result)
        
        return list(zip(filter_boxes, filter_rec_res))
```

### 4.3 文字方向自动校正

```python
def get_rotate_crop_image(self, img, points):
    """对裁剪区域进行方向校正"""
    # ... 裁剪逻辑 ...
    
    dst_img_height, dst_img_width = dst_img.shape[0:2]
    
    # 如果图片高度大于宽度的1.5倍，可能需要旋转
    if dst_img_height * 1.0 / dst_img_width >= 1.5:
        # 尝试4个方向
        rotations = [dst_img, rot90(dst_img, 1), rot90(dst_img, 2), rot90(dst_img, 3)]
        
        best_score = 0
        best_img = dst_img
        
        for rotated in rotations:
            text, score = self.text_recognizer[0]([rotated])[0]
            if score > best_score:
                best_score = score
                best_img = rotated
        
        dst_img = best_img
    
    return dst_img
```

### 4.4 表格 OCR

表格 OCR 使用 `TableStructureRecognizer` 配合 OCR：

```python
def _table_transformer_job(self, ZM, auto_rotate=True):
    """表格结构识别 + OCR"""
    
    # 1. 收集所有表格区域
    for p, tbls in enumerate(self.page_layout):
        for tb in tbls:
            if tb["type"] == "table":
                # 裁剪表格图片
                table_img = self.page_images[p].crop((left, top, right, bottom))
                
                # 2. 表格方向校正
                if auto_rotate:
                    best_angle, rotated_img, _ = self._evaluate_table_orientation(table_img)
                
                # 3. 表格结构识别 (TSR)
                recos = self.tbl_det(imgs)  # 返回行列结构
    
    # 4. 为每个单元格执行OCR
    # ...
```

---

## Part 5: 表格提取专题

### 5.1 表格识别算法

**核心文件**: `deepdoc/vision/table_structure_recognizer.py`

```python
class TableStructureRecognizer(Recognizer):
    labels = [
        "table",                    # 整个表格
        "table column",             # 列
        "table row",                # 行
        "table column header",      # 表头列
        "table projected row header", # 行表头
        "table spanning cell",      # 跨行跨列单元格
    ]
    
    def __call__(self, images, thr=0.2):
        """表格结构识别"""
        # 使用ONNX模型或Ascend加速
        tbls = super().__call__(images, thr)
        
        # 对识别结果进行边界对齐
        for tbl in tbls:
            # 列边界对齐：取所有行的x0/x1均值
            left = np.mean([b["x0"] for b in lts if "row" in b["label"]])
            right = np.mean([b["x1"] for b in lts if "row" in b["label"]])
            
            # 行边界对齐：取所有列的top/bottom中值
            top = np.median([b["top"] for b in lts if b["label"] == "table column"])
```

### 5.2 合并单元格处理

```python
@staticmethod
def construct_table(boxes, is_english=False, html=True, **kwargs):
    """构建表格，处理合并单元格"""
    
    # 1. 分离表头行和数据行
    max_type = Counter([b["btype"] for b in boxes]).most_common(1)[0][0]
    
    if max_type == "Nu":  # 数字类型最多，第一行为表头
        for r in range(1, len(df)):
            if row_type != max_type:
                hdrows.append(r)  # 非数字行加入表头
    
    # 2. 按行分组
    rows = [[boxes[0]]]
    for b in boxes[1:]:
        if b["R"] != rows[-1][-1].get("R"):  # 新行
            rows.append([b])
        else:
            rows[-1].append(b)  # 同一行
    
    # 3. 按列排序
    cols = [[boxes[0]]]
    for b in boxes[1:]:
        cols[-1].append(b)
```

### 5.3 表格→文本转换策略

```python
def __compose_table_content(self, df):
    """将表格转换为文本"""
    
    # 列类型识别
    block_types = {
        "Dt": "日期",
        "Nu": "数字",
        "Tx": "短文本",
        "Lx": "长文本",
        "En": "英文",
        "Nr": "专名",
        "Ca": "代码",
        "NE": "数字英文混合",
    }
    
    # 智能拼接：表头:值;表头:值
    for i in range(1, len(df)):
        if i in hdrows:  # 表头行跳过
            continue
        
        cells = []
        for j in range(len(df.iloc[i, :])):
            # 获取该列的表头
            headers = []
            for h in hr:  # hdrows中的表头行
                x = str(df.iloc[i + h, j]).strip()
                if x and x not in headers:
                    headers.append(x)
            header = ", ".join(headers)
            
            # 拼接
            value = str(df.iloc[i, j])
            if header:
                cells.append(f"{header}: {value}")
            else:
                cells.append(value)
        
        lines.append("; ".join(cells))
    
    return lines
```

### 5.4 HTML 表格输出

```python
def _extract_table_figure(self, need_image, ZM, return_html, need_position):
    """提取表格并转为HTML"""
    
    for k, bxs in tables.items():
        # 构造表格HTML
        tb = "<table><caption>Sheet1</caption>"
        
        # 表头行
        tb += "<tr>"
        for t in rows[0]:
            tb += f"<th>{escape(t.value)}</th>"
        tb += "</tr>"
        
        # 数据行
        for r in rows[1:]:
            tb += "<tr>"
            for c in r:
                tb += f"<td>{escape(c.value)}</td>"
            tb += "</tr>"
        
        tb += "</table>"
```

---

## Part 6: MinerU vs DeepDoc 详细对比

### 6.1 架构差异

| 特性 | **DeepDoc** | **MinerU** |
|------|-------------|------------|
| **架构风格** | 轻量级、模块化 | 一体化Pipeline |
| **布局识别** | YOLO + 自研后处理 | PP-StructureV2 |
| **OCR引擎** | PaddleOCR (集成) | 多种可选 (PaddleOCR/Tesseract) |
| **表格识别** | 自研TSR | TableMaster/PaddleOCR |
| **语言支持** | 中英文为主 | 100+语言 |
| **代码复杂度** | ~2000行Python | 更复杂的Pipeline |
| **部署复杂度** | 简单（单一服务）| 复杂（多模型协同）|

### 6.2 MinerU 集成

RAGFlow 在 0.15.x 版本引入了 MinerU 作为可选后端：

**核心文件**: `deepdoc/parser/mineru_parser.py`

```python
class MinerUParser(RAGFlowPdfParser):
    """MinerU 后端解析器，继承自 RAGFlowPdfParser"""
    
    def parse_pdf(self, filepath, binary, **kwargs):
        """调用 MinerU 进行解析"""
        
        # 1. 准备选项
        options = MinerUParseOptions(
            backend=MinerUBackend.PIPELINE,
            lang=MinerULanguage.CH,  # 中文
            method=MinerUParseMethod.AUTO,
            parse_method=parse_method,  # naive/manual/paper等
            formula_enable=True,
            table_enable=True,
        )
        
        # 2. 运行 MinerU
        final_out_dir = self._run_mineru(pdf, out_dir, options)
        
        # 3. 读取输出
        outputs = self._read_output(final_out_dir, pdf.stem)
        
        # 4. 转换为 RAGFlow 格式
        return self._transfer_to_sections(outputs, parse_method)
```

### 6.3 解析效果对比

| 格式 | **DeepDoc** | **MinerU** |
|------|-------------|------------|
| **纯文本PDF** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **扫描件PDF** | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **复杂表格** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **合并单元格** | ⭐⭐ | ⭐⭐⭐⭐ |
| **数学公式** | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **多栏布局** | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **脚注/页眉** | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **手写文字** | ⭐ | ⭐⭐ |

### 6.4 GPU 需求对比

| 场景 | **DeepDoc** | **MinerU** |
|------|-------------|------------|
| **CPU模式** | 支持 | 支持（较慢）|
| **GPU加速** | 可选 (CUDA) | 推荐 (CUDA) |
| **显存需求** | 2GB+ | 4GB+ |
| **多GPU** | 支持 (PARALLEL_DEVICES) | 部分支持 |
| **ARM支持** | 有限 | 良好 |

### 6.5 替换方案详解

#### 6.5.1 使用 MinerU 替换 DeepDoc

```python
# 在 knowledgebase_service.py 或 file_service.py 中

# 方式1: 直接使用 MinerU
from deepdoc.parser.mineru_parser import MinerUParser

parser = MinerUParser(
    mineru_path="/path/to/mineru",
    mineru_api="",  # 本地模式
    mineru_server_url="http://localhost:8080"  # 服务器模式
)

# 检查安装
ok, reason = parser.check_installation()
if not ok:
    raise RuntimeError(f"MinerU not available: {reason}")

# 解析
sections, tables = parser.parse_pdf(
    filepath=file_path,
    binary=None,
    backend="pipeline",  # 或 "vlm-http-client"
    parse_method="paper",  # naive/manual/paper/book/laws
)
```

#### 6.5.2 使用 Docling 替换

```python
# deepdoc/parser/docling_parser.py (RAGFlow已支持)

from deepdoc.parser.docling_parser import DoclingParser

parser = DoclingParser()
sections, tables = parser.parse_pdf(
    filepath=file_path,
    binary=None,
    parse_method="naive"
)
```

#### 6.5.3 使用 PaddleOCR 独立方案

```python
# deepdoc/parser/paddleocr_parser.py

from deepdoc.parser.paddleocr_parser import PaddleOCRParser

parser = PaddleOCRParser(
    use_angle_cls=True,
    lang='ch',
    use_gpu=True
)

# 识别图片中的文字
results = parser.ocr(image_path)
```

### 6.6 选型建议

| 场景 | 推荐方案 |
|------|----------|
| **企业知识库（中文为主）** | DeepDoc (默认) |
| **学术论文/多语言文档** | MinerU |
| **表格密集型文档** | MinerU + TableMaster |
| **实时性要求高** | DeepDoc (轻量) |
| **资源受限环境** | DeepDoc + CPU模式 |
| **复杂排版文档** | MinerU (PP-StructureV2) |

---

## 附录：关键源码文件索引

| 功能 | 源码路径 |
|------|----------|
| PDF解析核心 | `deepdoc/parser/pdf_parser.py` |
| OCR引擎 | `deepdoc/vision/ocr.py` |
| 布局识别 | `deepdoc/vision/layout_recognizer.py` |
| 表格识别 | `deepdoc/vision/table_structure_recognizer.py` |
| 分块策略 | `rag/nlp/__init__.py` |
| Word解析 | `deepdoc/parser/docx_parser.py` |
| Excel解析 | `deepdoc/parser/excel_parser.py` |
| Markdown解析 | `deepdoc/parser/markdown_parser.py` |
| MinerU集成 | `deepdoc/parser/mineru_parser.py` |
| Docling集成 | `deepdoc/parser/docling_parser.py` |

---

*本文档基于 RAGFlow 源码版本分析，代码行数和功能可能随版本更新而变化。*
