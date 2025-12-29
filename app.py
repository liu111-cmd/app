import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
import jieba.analyse
from collections import Counter
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Funnel, Radar
from streamlit_echarts import st_pyecharts
import re
from urllib.parse import urlparse

# 页面配置
st.set_page_config(
    page_title="文本分析可视化工具",
    page_icon="📊",
    layout="wide"
)

# 初始化jieba
jieba.setLogLevel(jieba.logging.INFO)

def fetch_web_content(url):
    """获取网页内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 获取正文文本
        text = soup.get_text()
        
        # 清理文本
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        st.error(f"获取网页内容失败: {str(e)}")
        return None

def process_text(text, min_freq=1):
    """处理文本并统计词频"""
    # 使用jieba进行分词
    words = jieba.lcut(text)
    
    # 过滤非中文字符和停用词
    stop_words = {'的', '了', '在', '是', '和', '有', '也', '都', '这', '个', '中', '到', '为',
                  '对', '与', '上', '或', '等', '于', '之', '而', '及', '就', '但', '并', '很',
                  '要', '从', '以', '将', '不', '我们', '他们', '可以', '一个', '没有', '不是',
                  '这个', '就是', '这样', '因为', '所以', '如果', '虽然', '但是', '而且', '然后'}
    
    # 过滤单个字符和非中文字符
    filtered_words = []
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
    
    for word in words:
        if (len(word) >= 2 and  # 至少2个字符
            word not in stop_words and
            chinese_pattern.search(word)):
            filtered_words.append(word)
    
    # 统计词频
    word_freq = Counter(filtered_words)
    
    # 过滤低频词
    word_freq = {word: freq for word, freq in word_freq.items() if freq >= min_freq}
    
    # 转换为DataFrame并按词频排序
    df = pd.DataFrame(list(word_freq.items()), columns=['词汇', '频率'])
    df = df.sort_values('频率', ascending=False).reset_index(drop=True)
    
    return df

def create_wordcloud(word_freq_dict, title="词云图"):
    """创建词云图"""
    wordcloud = (
        WordCloud()
        .add(
            series_name=title,
            data_pair=list(word_freq_dict.items()),
            word_size_range=[20, 100],
            shape="circle",
            rotate_step=45,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(font_size=20)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
    )
    return wordcloud

def create_bar_chart(df, title="词频柱状图", top_n=20):
    """创建柱状图"""
    top_df = df.head(top_n)
    bar = (
        Bar()
        .add_xaxis(top_df['词汇'].tolist())
        .add_yaxis("词频", top_df['频率'].tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(
                name="词汇",
                axislabel_opts=opts.LabelOpts(rotate=45)
            ),
            yaxis_opts=opts.AxisOpts(name="频率"),
            datazoom_opts=[opts.DataZoomOpts()],
        )
    )
    return bar

def create_pie_chart(df, title="词频饼图", top_n=20):
    """创建饼图"""
    top_df = df.head(top_n)
    pie = (
        Pie()
        .add(
            series_name="",
            data_pair=list(zip(top_df['词汇'], top_df['频率'])),
            radius=["30%", "75%"],
            center=["50%", "50%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(
                orient="vertical",
                pos_top="15%",
                pos_left="2%",
            ),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)")
        )
    )
    return pie

def create_line_chart(df, title="词频折线图", top_n=20):
    """创建折线图"""
    top_df = df.head(top_n)
    line = (
        Line()
        .add_xaxis(top_df['词汇'].tolist())
        .add_yaxis("词频", top_df['频率'].tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(
                name="词汇",
                axislabel_opts=opts.LabelOpts(rotate=45)
            ),
            yaxis_opts=opts.AxisOpts(name="频率"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
        )
    )
    return line

def create_scatter_chart(df, title="词频散点图", top_n=20):
    """创建散点图"""
    top_df = df.head(top_n)
    scatter = (
        Scatter()
        .add_xaxis(top_df['词汇'].tolist())
        .add_yaxis(
            "词频",
            top_df['频率'].tolist(),
            symbol_size=lambda data: data * 2,  # 根据频率调整点大小
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(
                name="词汇",
                axislabel_opts=opts.LabelOpts(rotate=45)
            ),
            yaxis_opts=opts.AxisOpts(name="频率"),
            tooltip_opts=opts.TooltipOpts(
                formatter="{a}: {c}<br/>{b}: {c}"
            ),
        )
    )
    return scatter

def create_funnel_chart(df, title="词频漏斗图", top_n=20):
    """创建漏斗图"""
    top_df = df.head(top_n)
    funnel = (
        Funnel()
        .add(
            series_name="",
            data_pair=list(zip(top_df['词汇'], top_df['频率'])),
            gap=2,
            label_opts=opts.LabelOpts(position="inside"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{a}<br/>{b}: {c}"
            ),
        )
    )
    return funnel

def create_radar_chart(df, title="词频雷达图", top_n=10):
    """创建雷达图"""
    top_df = df.head(top_n)
    
    # 准备雷达图数据
    schema = [
        opts.RadarIndicatorItem(name=word, max_=max(df['频率']))
        for word in top_df['词汇'].tolist()
    ]
    
    radar = (
        Radar()
        .add_schema(schema=schema)
        .add(
            series_name="词频分布",
            data=[top_df['频率'].tolist()],
            linestyle_opts=opts.LineStyleOpts(width=2),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.1),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(selected_mode="single"),
        )
    )
    return radar

# 主应用
def main():
    # 侧边栏
    st.sidebar.title("📊 可视化选项")
    
    # 图表类型选择
    chart_types = {
        "词云图": "wordcloud",
        "柱状图": "bar",
        "饼图": "pie",
        "折线图": "line",
        "散点图": "scatter",
        "漏斗图": "funnel",
        "雷达图": "radar"
    }
    
    selected_chart = st.sidebar.selectbox(
        "选择图表类型",
        list(chart_types.keys()),
        index=0
    )
    
    # 低频词过滤
    min_freq = st.sidebar.slider(
        "过滤低频词（最小频率）",
        min_value=1,
        max_value=50,
        value=2,
        help="只显示出现次数大于等于此值的词汇"
    )
    
    # 显示词汇数量
    top_n = st.sidebar.slider(
        "显示词汇数量",
        min_value=10,
        max_value=100,
        value=20,
        help="在图表中显示的词汇数量"
    )
    
    # 主界面
    st.title("📈 文本分析可视化工具")
    st.markdown("---")
    
    # URL输入区域
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input(
            "输入文章URL:",
            placeholder="https://example.com/article",
            value=""
        )
    
    with col2:
        st.markdown("")
        st.markdown("")
        fetch_button = st.button("🚀 开始分析")
    
    # 处理URL输入
    if url and fetch_button:
        with st.spinner("正在获取和分析内容..."):
            # 获取网页内容
            text = fetch_web_content(url)
            
            if text:
                # 显示原始文本预览
                with st.expander("📝 文本内容预览"):
                    st.text_area("", text[:1000] + "...", height=200)
                
                # 处理文本
                df = process_text(text, min_freq)
                
                if not df.empty:
                    # 显示词频表格
                    st.subheader(f"📊 词频统计（共 {len(df)} 个词汇）")
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.dataframe(
                            df.head(50),
                            use_container_width=True,
                            height=400
                        )
                    
                    with col2:
                        st.metric("总词汇数", len(df))
                        st.metric("最高频词汇", df.iloc[0]['词汇'])
                        st.metric("最高频率", df.iloc[0]['频率'])
                    
                    # 创建图表
                    st.subheader("📈 可视化图表")
                    
                    # 准备数据
                    top_df = df.head(top_n)
                    word_freq_dict = dict(zip(top_df['词汇'], top_df['频率']))
                    
                    # 根据选择的图表类型创建图表
                    chart_type = chart_types[selected_chart]
                    
                    if chart_type == "wordcloud":
                        chart = create_wordcloud(word_freq_dict, f"词云图 - {selected_chart}")
                    elif chart_type == "bar":
                        chart = create_bar_chart(df, f"词频柱状图 - {selected_chart}", top_n)
                    elif chart_type == "pie":
                        chart = create_pie_chart(df, f"词频饼图 - {selected_chart}", top_n)
                    elif chart_type == "line":
                        chart = create_line_chart(df, f"词频折线图 - {selected_chart}", top_n)
                    elif chart_type == "scatter":
                        chart = create_scatter_chart(df, f"词频散点图 - {selected_chart}", top_n)
                    elif chart_type == "funnel":
                        chart = create_funnel_chart(df, f"词频漏斗图 - {selected_chart}", top_n)
                    elif chart_type == "radar":
                        chart = create_radar_chart(df, f"词频雷达图 - {selected_chart}", min(top_n, 10))
                    else:
                        chart = create_wordcloud(word_freq_dict)
                    
                    # 显示图表
                    st_pyecharts(chart, height="600px")
                    
                    # 下载选项
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        csv = df.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="📥 下载词频数据 (CSV)",
                            data=csv,
                            file_name="word_frequency.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        st.download_button(
                            label="📥 下载原始文本",
                            data=text,
                            file_name="original_text.txt",
                            mime="text/plain"
                        )
                else:
                    st.warning("未找到足够的词汇数据，请尝试调整低频词过滤设置或使用其他URL。")
            else:
                st.error("无法获取网页内容，请检查URL是否正确可访问。")
    elif fetch_button and not url:
        st.warning("请输入URL地址")
    
    # 使用说明
    with st.expander("ℹ️ 使用说明"):
        st.markdown("""
        ### 使用方法：
        1. **输入URL**：在输入框中输入文章的URL地址
        2. **开始分析**：点击"开始分析"按钮获取并分析文本
        3. **选择图表**：在侧边栏选择想要查看的图表类型
        4. **调整参数**：
           - 过滤低频词：隐藏出现次数较少的词汇
           - 显示词汇数量：控制图表中显示的词汇数量
        
        ### 功能特点：
        - 🔗 **支持网页文本抓取**
        - 📊 **7种可视化图表**：词云、柱状图、饼图、折线图、散点图、漏斗图、雷达图
        - ⚙️ **交互过滤**：可调整低频词阈值
        - 📈 **词频统计**：显示前20个高频词汇
        - 💾 **数据导出**：支持下载词频数据和原始文本
        
        ### 技术栈：
        - **Streamlit**：Web应用框架
        - **PyEcharts**：可视化图表库
        - **Jieba**：中文分词工具
        - **BeautifulSoup**：网页解析库
        """)
    
    # 页脚
    st.markdown("---")
    st.caption("✨ 文本分析可视化工具 | 支持中文网页内容分析")

if __name__ == "__main__":
    main()