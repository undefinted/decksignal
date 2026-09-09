# AI 演示文稿生成工具与方法全景调研

## 执行摘要

截至 2026 年 9 月，AI 演示文稿市场已经形成至少六条技术路线，而不是单一的“一句话生成 PPT”：原生办公套件内生成、独立在线生成器、设计协作平台、内容研究与排版分离的多工具流水线、代码或 Markdown 驱动的开源路线，以及论文/长文档专用 Agent。本轮建立了 32 个可测试对象的结构化长名单；它是按公开可发现性形成的版本化普查，不宣称穷尽所有区域性小工具。

真正影响选择的变量不是“能否生成”，而是输入资料忠实度、叙事结构、视觉质量、中文本地化、原生可编辑性、导出保真度、模板/品牌约束、迭代编辑、稳定性、成本和数据治理。网站因此不应发布一个脱离场景的万能总榜，而应同时提供场景榜、能力雷达和证据成熟度。

## 市场与方法分类

### 原生办公与插件路线

Microsoft Copilot、WPS AI、Plus AI、SlidesAI 和 MagicSlides 的共同优势是在 PowerPoint、WPS 或 Google Slides 工作流附近完成生成和修改。Microsoft 官方资料显示 Copilot 能从提示词或文件创建演示，并对现有页面进行增删、重组和图像处理；功能是否出现取决于订阅与组织设置。[Microsoft Support](https://support.microsoft.com/en-gb/copilot-powerpoint)

WPS 官方页面声明支持提示词、Word、PDF 和大纲输入，并可在 WPS Presentation 中继续原生编辑、导出 PPTX/PDF/图片。[WPS AI Slides](https://ai.wps.com/en-US/) Plus AI 与 SlidesAI 则分别强调在 Google Slides/PowerPoint 内生成、改写和重排；这些“原生”主张仍需要通过 OOXML 结构检查和跨软件回放验证。[Plus AI Marketplace](https://workspace.google.com/marketplace/app/plus_ai_for_google_slides_and_docs/214277172452) [SlidesAI Help](https://help.slidesai.io/generate-a-presentation-from-text-aj3nl)

### 独立生成平台

Gamma、Beautiful.ai、Presenton、Kimi PPT、百度文库智能 PPT、讯飞智文、Presentations.AI、SlideSpeak 和 AutoPPT 等平台覆盖从提示词或文档到完整演示草稿的流程。它们的差别集中在生成前是否允许审阅大纲、能否导入企业模板、导出后的对象是否仍为可编辑原生元素，以及是否支持私有部署。

Gamma 官方帮助中心确认可导出 PPTX、PDF 和 PNG，但网页卡片组件转为 PowerPoint 后的保真度需实测。[Gamma Help Center](https://help.gamma.app/en/articles/8022861-what-s-the-easiest-way-to-export-my-gamma) Beautiful.ai 使用“输入—大纲—设计—逐页迭代”的分阶段流程。[Beautiful.ai](https://www.beautiful.ai/text-to-presentation-ai) Presenton 同时提供云端和 Apache-2.0 开源实现，是私有化与可替换模型赛道的重要对照组。[Presenton GitHub](https://github.com/presenton/presenton)

Kimi 官方资料显示其输入范围包括 PDF、Word、PPTX、Excel、文本和图片，并提供自定义模板和图片复刻路径；页面对“完全可编辑”等描述属于厂商主张，必须用导出的 PPTX 验证。[Kimi PPT](https://www.kimi.com/zh-cn/features/slides) 百度千帆已提供文库智能 PPT 的接口文档，适合纳入 API 自动化赛道。[百度智能云](https://cloud.baidu.com/doc/qianfan/s/4mjcnolh6)

### 设计与空间演示路线

Canva、Adobe Express、Pitch、Prezi 和 Decktopus 更接近设计或协作工作空间。Canva Magic Design 从提示词生成候选视觉方案；Adobe Express 可从 PDF、Word、PowerPoint、TXT 和 Excel 文件生成可编辑草稿；Pitch Agent 支持提示词、上下文文件与模板；Prezi 输出空间化动态演示，因此不应只以传统分页 PPT 的指标衡量。[Canva](https://www.canva.com/create/ai-presentations/) [Adobe Express](https://helpx.adobe.com/express/web/documents-and-presentations/create-presentations-with-generative-ai.html) [Pitch Agent](https://help.pitch.com/en/articles/14981091-pitch-agent) [Prezi AI](https://prezi.com/ai-presentation-maker/)

### 多工具内容流水线

中文内容平台上大量教程本质上属于“模型做研究/大纲，专业生成器做排版”的两段式流程，例如 DeepSeek＋Kimi、DeepSeek＋讯飞智文。另一些方法把 AI 生图、模板选择和 PowerPoint 人工组装拆开。这类方法不应按每条视频重复收录，而应按输入、关键转换、工具链和输出格式去重；视频的速度与质量说法只作为待验证主张。

图像优先路线先生成整页视觉图，再使用 WPS、模型或代码恢复为可编辑 PPTX。它可能获得较高视觉一致性，却也容易在文本准确性、对象级编辑、无障碍和文件体积上付出代价，必须把“渲染观感”和“原生结构”分轨评分。

### 开源与代码路线

PptxGenJS、python-pptx、Marp、Slidev 和 reveal.js 不是完整的 AI 产品，但可作为模型生成演示的执行层。PptxGenJS 与 python-pptx 直接构建 OOXML/PPTX，更适合原生元素、数据图表和自动化；Marp、Slidev 与 reveal.js 更适合 Markdown 或 Web 演示。它们通常需要工程能力，但可以固定版本、记录代码和重复运行，是闭源产品的重要可复现基线。[PptxGenJS](https://github.com/gitbrent/PptxGenJS) [python-pptx](https://github.com/scanny/python-pptx) [Marp CLI](https://github.com/marp-team/marp-cli) [Slidev](https://github.com/slidevjs/slidev)

## Benchmark 组合设计

SlidesGen-Bench 将不同生成范式统一到内容、美学和可编辑性三个维度，并使用人类偏好数据校准，适合比较图像式、代码式和模板式输出。[SlidesGen-Bench paper](https://arxiv.org/abs/2601.09487) PresentBench包含 238 个实例，每个实例平均 54.1 个二元检查项，适合检验事实覆盖和任务特定要求。[PresentBench paper](https://arxiv.org/abs/2603.07244)

DECKBench同时考察论文到完整演示和多轮编辑，覆盖忠实度、连贯性、布局及指令遵循。[DECKBench paper](https://arxiv.org/abs/2602.13318) PPTC偏向通过 API 序列执行 PowerPoint 任务并用 PPTX-Match 评价，适合原子级创建和模板编辑。[PPTC GitHub](https://github.com/gydpku/PPTC) PPTArena进一步覆盖真实演示上的文本、图表、表格、动画和母版修改。[PPTArena GitHub](https://github.com/michaelofengenden/PPTArena)

因此首版实测采用五层证据，而不是把多个 benchmark 的原始分数直接相加：

1. 内容与事实：PresentBench 检查项、来源引用正确率和幻觉率。
2. 视觉与叙事：SlidesGen-Bench 指标、专家 rubric 和盲选偏好。
3. 原生可编辑性：OOXML 对象比例、文本/图表/表格可编辑性、字体与母版使用。
4. 生成与迭代：DECKBench、PPTC/PPTArena 的多轮修改成功率。
5. 实用性：成功率、耗时、人工操作分钟数、价格、语言、隐私和导出稳定性。

各 benchmark 的覆盖范围不同，报告保留分项分数与置信区间。只有完成相同任务、相同输入资产和公开运行记录的对象才进入同一排行榜；网页式演示、图片式演示和原生 PPTX 在共同视觉榜之外，还进入各自格式赛道。

## 首轮实测队列

P0 队列优先覆盖不同技术范式：Microsoft Copilot、WPS AI、Kimi PPT、Gamma、Canva、Plus AI、Beautiful.ai、Presenton、SlidesAI、PptxGenJS＋LLM，以及图像优先恢复路线。每个工具执行商业汇报、教学课件、论文答辩、产品发布、数据报告五类任务；每类至少一个中文任务和一个英文或双语任务。

P1 队列覆盖 Adobe Express、Pitch、Prezi、Decktopus、MagicSlides、百度文库智能 PPT、讯飞智文、NotebookLM、Marp、Slidev、AutoPresent、论文转演示 Agent，以及 DeepSeek 组合流程。P2 保留给证据尚未完全核实、访问受限或功能高度同质化的候选。

所有运行记录必须保存工具版本/日期、套餐、输入、设置、生成起止时间、原始输出、渲染图、结构指标、失败信息和人工干预。付费产品若未获得账户，标记为 access-blocked，不用演示视频代替实测。

## 局限与持续更新

小红书、B站和 YouTube 的搜索结果会受登录、地区、个性化与搜索引擎索引影响，无法用一次检索证明“全网穷尽”。市场中还存在大量换壳站点、短期活动页、区域产品和已转型产品。项目以版本化覆盖报告代替“全部收录”的绝对承诺：记录检索日期、平台、关键词、语言和结果数；新增来源进入去重队列；工具功能变化触发旧快照过期。

## Sources

完整机器可读候选表见 [`data/research/landscape-v0.1.json`](../data/research/landscape-v0.1.json)，逐方法版权与归属见 [`data/sources/catalog-v0.1.json`](../data/sources/catalog-v0.1.json)。本报告引用的 benchmark 与产品链接均指向论文、官方文档或官方仓库；内容平台教程只用于描述其提出的方法，不作为性能证明。
