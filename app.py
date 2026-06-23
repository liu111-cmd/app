import streamlit as st
import pandas as pd
from typing import Optional
from utils import fetch_web_content, process_text, extract_keywords
from charts import (
    create_wordcloud,
    create_bar_chart,
    create_pie_chart,
    create_line_chart,
    create_scatter_chart,
    create_funnel_chart,
    create_radar_chart,
)

st.set_page_config(
    page_title="文本分析可视化工具",
    page_icon="📊",
    layout="wide"
)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_fetch_web_content(url: str) -> Optional[str]:
    return fetch_web_content(url)

@st.cache_data(ttl=3600, show_spinner=False)
def cached_process_text(text: str, min_freq: int) -> pd.DataFrame:
    return process_text(text, min_freq)

def main():
    st.sidebar.title("📊 可视化选项")
    
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
    
    min_freq = st.sidebar.slider(
        "过滤低频词（最小频率）",
        min_value=1,
        max_value=50,
        value=2,
        help="只显示出现次数大于等于此值的词汇"
    )
    
    top_n = st.sidebar.slider(
        "显示词汇数量",
        min_value=10,
        max_value=100,
        value=20,
        help="在图表中显示的词汇数量"
    )
    
    analysis_mode = st.sidebar.radio(
        "分析模式",
        ["URL分析", "文本输入"],
        index=0,
        help="选择分析网页内容还是直接输入文本"
    )
    
    st.title("📈 文本分析可视化工具")
    st.markdown("---")
    
    text_input = ""
    url_input = ""
    
    if analysis_mode == "URL分析":
        col1, col2 = st.columns([3, 1])
        with col1:
            url_input = st.text_input(
                "输入文章URL:",
                placeholder="https://example.com/article",
                value=""
            )

        with col2:
            st.markdown("")
            st.markdown("")
            fetch_button = st.button("🚀 开始分析")
    else:
        text_input = st.text_area(
            "输入要分析的文本:",
            placeholder="请在此输入需要分析的中文文本...",
            height=200
        )
        fetch_button = st.button("🚀 开始分析")
    
    if fetch_button:
        if analysis_mode == "URL分析" and not url_input:
            st.warning("⚠️ 请输入URL地址")
            return
        
        if analysis_mode == "文本输入" and not text_input.strip():
            st.warning("⚠️ 请输入要分析的文本")
            return
        
        with st.spinner("🔄 正在获取和分析内容..."):
            try:
                if analysis_mode == "URL分析":
                    text = cached_fetch_web_content(url_input)
                else:
                    text = text_input
                
                if not text:
                    st.error("❌ 无法获取内容，请检查输入是否正确")
                    return
                
                with st.expander("📝 文本内容预览", expanded=False):
                    preview_text = text[:1500] + "..." if len(text) > 1500 else text
                    st.text_area("", preview_text, height=200)
                
                df = cached_process_text(text, min_freq)
                
                if df.empty:
                    st.warning("⚠️ 未找到足够的词汇数据，请尝试调整低频词过滤设置")
                    return
                
                st.subheader(f"📊 词频统计（共 {len(df)} 个词汇）")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.dataframe(
                        df.head(50),
                        use_container_width=True,
                        height=400
                    )
                
                with col2:
                    st.metric("📚 总词汇数", len(df))
                    st.metric("🔝 最高频词汇", df.iloc[0]['词汇'])
                    st.metric("📊 最高频率", df.iloc[0]['频率'])
                    
                    top_keywords = extract_keywords(text, top_n=8)
                    st.subheader("🎯 关键词提取")
                    max_weight = max([w for _, w in top_keywords]) if top_keywords else 1
                    for keyword, weight in top_keywords:
                        normalized_weight = min(int((weight / max_weight) * 100), 100)
                        st.progress(normalized_weight, text=keyword)
                
                st.subheader("📈 可视化图表")
                
                top_df = df.head(top_n)
                word_freq_dict = dict(zip(top_df['词汇'], top_df['频率']))
                
                chart_type = chart_types[selected_chart]
                
                if chart_type == "wordcloud":
                    chart = create_wordcloud(word_freq_dict, f"词云图")
                elif chart_type == "bar":
                    chart = create_bar_chart(df, f"词频柱状图", top_n)
                elif chart_type == "pie":
                    chart = create_pie_chart(df, f"词频饼图", top_n)
                elif chart_type == "line":
                    chart = create_line_chart(df, f"词频折线图", top_n)
                elif chart_type == "scatter":
                    chart = create_scatter_chart(df, f"词频散点图", top_n)
                elif chart_type == "funnel":
                    chart = create_funnel_chart(df, f"词频漏斗图", top_n)
                elif chart_type == "radar":
                    chart = create_radar_chart(df, f"词频雷达图", min(top_n, 10))
                else:
                    chart = create_wordcloud(word_freq_dict)
                
                from streamlit_echarts import st_pyecharts
                st_pyecharts(chart, height="600px")
                
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
                
                with col3:
                    json_data = df.to_json(orient='records', force_ascii=False)
                    st.download_button(
                        label="📥 下载词频数据 (JSON)",
                        data=json_data,
                        file_name="word_frequency.json",
                        mime="application/json"
                    )
            
            except Exception as e:
                st.error(f"❌ 分析过程出错: {str(e)}")
    
    with st.expander("ℹ️ 使用说明"):
        st.markdown("""
        ### 使用方法：
        
        **模式一：URL分析**
        1. 在输入框中输入文章的URL地址
        2. 点击"开始分析"按钮获取并分析网页文本
        
        **模式二：文本输入**
        1. 在文本框中直接输入要分析的中文文本
        2. 点击"开始分析"按钮进行分析
        
        3. **选择图表**：在侧边栏选择想要查看的图表类型
        4. **调整参数**：
           - 过滤低频词：隐藏出现次数较少的词汇
           - 显示词汇数量：控制图表中显示的词汇数量
        
        ### 功能特点：
        - 🔗 **支持网页文本抓取**
        - 📝 **支持直接文本输入**
        - 📊 **7种可视化图表**：词云、柱状图、饼图、折线图、散点图、漏斗图、雷达图
        - ⚙️ **交互过滤**：可调整低频词阈值
        - 📈 **词频统计**：显示完整词频表格
        - 🎯 **关键词提取**：基于TF-IDF算法提取关键词
        - 💾 **数据导出**：支持CSV、JSON、TXT多种格式下载
        
        ### 技术栈：
        - **Streamlit**：Web应用框架
        - **PyEcharts**：可视化图表库
        - **Jieba**：中文分词工具
        - **BeautifulSoup**：网页解析库
        """)
    
    st.markdown("---")
    st.caption("✨ 文本分析可视化工具 | 支持中文文本分析")

if __name__ == "__main__":
    main()