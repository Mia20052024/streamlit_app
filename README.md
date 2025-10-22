# TMDB 5000 电影数据可视化与分析（Streamlit）

本项目是一个使用 Streamlit 构建的交互式数据分析应用，围绕 TMDB 5000 电影数据集进行探索。应用内置侧边栏筛选、关键指标卡片（KPI）、针对性业务问题分析以及多种 EDA 视图，帮助你从预算、票房、评分、类型、国家与语言等维度理解电影数据。

- 代码语言与框架：Python + Streamlit + Altair + Pandas
- 数据来源：Kaggle 公共数据集（通过 kagglehub 自动下载）
- 运行环境：已在 macOS、Python 3.13 验证（如遇依赖兼容问题，建议使用 Python 3.11/3.12）

---

## 功能亮点

- 侧边栏多维筛选：年份、类型、语言、评分区间、时长区间、ROI 下限、最小投票数、是否排除票房为 0/缺失、标题关键词。
- KPI 卡片：当前筛选下的影片数量、平均评分、中位数票房、中位数 ROI。
- 关键问题分析（Questions）：
  - Q1：更高预算是否带来更高票房/评分？（预算-票房回归、预算-评分回归、热度-票房）
  - Q2：哪些类型（Genre）拥有更高 ROI？（按中位 ROI 排名）
- 问题中心（Question Hub）内置多种图表，可在下拉框中快速切换：
  - 运行时长 vs 评分（按类型分面，LOESS 曲线）
  - 类型标签数量 vs 评分
  - 国家 × 语言 × ROI 热力图 / 分面柱状图
  - 上映月份与票房/评分的季节性（柱状/热力）
  - 按年代（Decade）趋势（预算/票房/评分）
  - 续集 vs 原创 对比（按 ROI 中位数）
  - 投票数分箱 vs 评分稳定性
  - 高 ROI Top-K vs 低 ROI Bottom-K 画像对比（柱状 / 归一化折线）
  - 预算分箱下 ROI 拐点
  - 类型 × 国家 协同热力图
  - 热度 vs 票房
  - 出品国家 ROI / 出品公司 ROI
  - 各年代类型占比变化
- EDA 视图：评分直方图、年份趋势（评分与热度）、热门类型时长箱线图、数值特征相关性热力图。
- 数据不足智能回退：若当前筛选使某视图无可绘数据，自动回退到“全量数据”绘制并提示。

---

## 目录结构

```
streamlit_app/
├── app.py                # 入口：页面框架与主流程
├── constants.py          # 页面标题/描述等常量
├── data_loader.py        # 数据加载与清洗（kagglehub 下载 + 特征工程）
├── filters.py            # 侧边栏筛选项与过滤逻辑
├── components.py         # KPI 卡片等可复用 UI 组件
├── charts.py             # Altair 图表封装（全部可视化）
├── sections.py           # 页面分区与“问题中心”组织
├── requirements.txt      # 依赖列表
└── README.md             # 本说明文档
```

---

## 数据来源与清洗

- 数据集：tmdb/tmdb-movie-metadata（Kaggle）
- 下载方式：`kagglehub.dataset_download("tmdb/tmdb-movie-metadata")`
- 自动识别文件：`tmdb_5000_movies.csv`（或兼容 `tmdb_5000_movies_2.csv`）
- 清洗与特征工程（data_loader.clean_movies）：
  - 日期解析：`release_date` → `release_year`
  - JSON 风格字符串列解析为列表：`genres_list`、`production_countries_list`、`production_companies_list`、`spoken_languages_list`
  - 数值列统一转为数值：`budget`、`revenue`、`runtime`、`vote_average`、`popularity`、`vote_count`
  - 派生指标：`profit = revenue - budget`、`roi = revenue / budget`（预算为 0 视作缺失）
  - 离群截断（用于绘图）：`budget_clip`、`revenue_clip` 以 99 分位裁剪
- 缓存：`@st.cache_data` 缓存下载和清洗后的 DataFrame，提升性能。

---

## 交互与页面结构

- 顶部：标题与说明（constants.PAGE_TITLE / PAGE_DESC）
- 侧边栏：`filters.build_sidebar(df)` 构建筛选项，`filters.apply_filters(df, f)` 应用过滤
- KPI：`components.kpi_cards(df_filtered)`
- 分析区：
  - `section_question_1/2`：针对预算-票房/评分、类型 ROI 等问题
  - `section_questions_hub`：汇集全部可切换的图表
  - `section_eda`：常规探索性分析视图
  - `section_leaderboard`：按票房或 ROI 排序的排行榜（可调 Top N）
- 智能回退：`st.session_state["df_full"]` 保存全量数据；当筛选后数据为空或不满足某图表条件时，回退使用全量数据并给出提示。

---

## 安装与运行

以下步骤以 macOS 为例，其他系统类似。

- 环境要求：
  - Python 3.11–3.13（已在 3.13 验证；若个别依赖不兼容，建议 3.11/3.12）
  - 网络可访问 Kaggle（首次下载需浏览器授权登录）

- 创建与激活虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

- 安装依赖：

```bash
pip install -U pip
pip install -r requirements.txt
```

- 运行应用：

```bash
streamlit run app.py
```

- 首次运行说明（kagglehub 认证与下载）：
  - 首次触发 `dataset_download` 时，kagglehub 可能自动打开浏览器进行 Kaggle 账户授权；完成后会在本地缓存数据。
  - 若网络/权限受限，应用会在“Data Loading (KaggleHub)”处给出错误提示并停止。

---

## 常见问题（FAQ）

- 没有任何图表显示/图表为空？
  - 当前筛选条件可能过严，导致无可绘数据。应用会自动回退到全量数据绘图并提示；也可放宽筛选条件。

- kagglehub 下载失败（网络或权限）怎么办？
  - 确保能访问 Kaggle，并按提示完成浏览器授权。
  - 需要代理的环境请配置系统/终端代理变量（如 `HTTPS_PROXY`）。
  - 也可在本地预先下载 CSV 并在 `data_loader.load_tmdb_via_kagglehub()` 中改为直接 `pd.read_csv(本地路径)`。

- Altair 图表在特定环境无法渲染？
  - 通过浏览器打开 Streamlit 页面，避免嵌套 WebView 的限制。
  - 更新浏览器与 Streamlit；或在命令行查看是否有相关错误输出。

- Python 版本兼容性
  - 若在 Python 3.13 下遇到第三方库兼容问题，建议切换到 3.11/3.12。

---

## 配置项

- `constants.py`
  - `PAGE_TITLE`：页面标题
  - `PAGE_DESC`：页面说明（首页 caption）

- `filters.py`
  - 调整默认筛选范围与控件，例如 ROI 上限、投票数默认值等。

---

## 代码设计与扩展指南

- 新增图表（推荐流程）：
  1. 在 `charts.py` 中新增绘图函数，输入为已过滤后的 DataFrame，输出 `alt.Chart`/`alt.VConcatChart` 等。
  2. 在 `sections.py` 的合适位置调用：
     - 若是通用探索图，加入 `section_questions_hub` 下拉选项；
     - 若是针对某业务问题，放入 `section_question_1/2`；
  3. 如需新的清洗/特征，补充到 `data_loader.clean_movies`。

- 新增筛选项：
  1. 在 `filters.build_sidebar` 内添加控件并扩展 `Filters` 数据类；
  2. 在 `filters.apply_filters` 内加入相应过滤逻辑。

- 替换/扩展数据源：
  - 若需使用本地 CSV 或其他数据集，可在 `load_tmdb_via_kagglehub` 内添加“本地优先”分支或新建加载函数。

---

## 部署建议

- Streamlit Community Cloud：
  - 直接推送到 Git 仓库并在 Cloud 上选择仓库即可。
  - 注意：Cloud 环境可能限制外网下载，kagglehub 首次下载可能失败。建议：
    - 方案 A：将 CSV 文件随仓库一并提交（注意数据许可）；
    - 方案 B：在构建步骤预下载并缓存，或改为公共 CDN。

- 容器化/服务器部署：
  - 使用 `requirements.txt` 安装依赖，开放默认端口 8501。
  - 需要代理/证书时，请配置系统环境变量与证书链。

---

## 许可与致谢

- 代码许可：本仓库未提供许可证文件（License）。如需开源分发，请补充适当的 License（例如 MIT）。
- 数据许可：TMDB 5000 数据来自 Kaggle，使用前请遵守其数据集条款与 TMDB 使用政策。
- 致谢：kagglehub、Streamlit、Altair、Pandas、NumPy 等开源项目。

