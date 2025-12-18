#### 11/25/2025
- 项目架构初步搭建
- 整合supabase
- 注册、登录、鉴权功能完成

#### 11/26/2025
- 主要功能初步设计
  - Hacker News story schema
  - 查询 -> 提取网页关键内容（jina） -> AI 翻译，总结流程设计
  - PRD.md
- Hacker News 异步访问API获取best, top, new stories 逻辑完成

#### 11/27/2025
- 将表结构存入supabase
  - 根据 hn_id 查询article存在
  - 添加article进入db

#### 11/28/2025
- 并行从Jina获得markdown形式的网页信息
- 并行将md格式的信息发送给API

#### 11/29/2025
- hn service 中print输出统一化 [HN] -> [HNService]
- 参考Jina官方文档通过``"X-Retain-Images": "none"`` 关闭图片转化
- 更新prompt
- 在schemas/hn.py中实现AITranslatedResult类
  
#### 11/30/2025
- 发现问题：AI分析结果中没有加入title与作者写的内容

#### 12/01/2025
- 修改 `HNRaw` 类，补充 `kids`, `descendants` 等官方 API 返回的字段。
- 修改 `Article`类，让其符合更改的 `HNRaw`类
- 修改 `schema.sql` 表
- 实现  `news_ingestor.py` (未测试)
- 参考DDD进行部分重构：将Article等class移动至models/
- 解决问题：AI分析结果中没有加入title与作者写的内容-更新prompt与更改相关业务逻辑代码

#### 12/02/2025
- 迁移poetry至uv

#### 12/03/2025
- 测试 `news_ingestor.py` 并实现 Swagger 触发接口 (`POST /api/news/ingest`)
- BugFix: 从 Poetry 迁移至 uv 后，默认安装的最新版 `httpx` (0.28.1) / `httpcore` (1.0.9) 导致在 Windows 环境下连接 DeepSeek API 频繁出现 `RemoteProtocolError` (Peer closed connection)。
  - 尝试方案：降级 HTTP/1.1、禁用连接池 (Keep-Alive=0) 均未能根治（DeepSeek 服务端对连接关闭处理较激进）。
  - 最终方案：切换 LLM Provider 至 **Gemini** (配合 OpenAI SDK)，连接稳定，数据摄入流程跑通。
- logger.py 初始化
  - 尚未完成AOP decorators
  - 尚未修改服务将logger与AOP引入
  
#### 12/04/2025
- 完成AOP修饰器并在3个services以及pipeline中调用，定义error.log与news_ingestor.log
- 引入 **APScheduler** (`AsyncIOScheduler`) 完成定时任务调度功能

#### 12/05/2025
- supabase中清理rows(ai分析的score改为ai_score),并测试ingestor功能
- debug in ingestor pipeline

#### 12/06/2025
- 重构DDD
  - 移动 `app/schemas/contexts.py` -> `app/services/contexts/story_contexts.py` (Pipeline 上下文)
  - 保留 `HNRaw` 在 `app/schemas/external/hn.py` (外部 DTO)
- 构造 schemas/article.py (只定义了request model)

#### 12/07/2025
- 完成 articles 接口 （`GET /api/articles`）
- 修改README.md

#### 12/09/2025
- 向量数据库相关代码配置（未输入supabase）
- langchain配置

#### 12/10/2025
- supabase中配置向量数据库与相似度函数
- 实现chat_service (未测试)

#### 12/11/2025
- 实现chat_service + router
- 初始化RAG



TODO:
- RAG
- 提取模型到config，env
- 第三方登录 （github, google）
- 前端
- chat recommendation
- RAG chat recommendation
- 研究AI翻译总结的高性能prompt（prompt training）
- 用户收藏实现
- 评论
- 扫描更新文章
- （Post-MVP）：集成多模态视觉模型（Vision Model），对文章中的关键图片进行语义描述提取，并作为上下文输入给 LLM 以生成更完整的总结。