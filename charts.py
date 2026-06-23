import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Funnel, Radar
from typing import Dict

def create_wordcloud(word_freq_dict: Dict[str, int], title: str = "词云图") -> WordCloud:
    wordcloud = (
        WordCloud()
        .add(
            series_name=title,
            data_pair=list(word_freq_dict.items()),
            word_size_range=[20, 120],
            shape="circle",
            rotate_step=45,
            word_gap=8,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title=title,
                title_textstyle_opts=opts.TextStyleOpts(font_size=22, font_weight="bold")
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True, formatter="{b}: {c}"),
        )
    )
    return wordcloud

def create_bar_chart(df: pd.DataFrame, title: str = "词频柱状图", top_n: int = 20) -> Bar:
    top_df = df.head(top_n)
    bar = (
        Bar()
        .add_xaxis(top_df['词汇'].tolist())
        .add_yaxis("词频", top_df['频率'].tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            datazoom_opts=[opts.DataZoomOpts()],
        )
    )
    return bar

def create_pie_chart(df: pd.DataFrame, title: str = "词频饼图", top_n: int = 20) -> Pie:
    top_df = df.head(top_n)
    pie = (
        Pie()
        .add(
            series_name="词频",
            data_pair=[(word, int(freq)) for word, freq in zip(top_df['词汇'], top_df['频率'])],
            radius=["35%", "70%"],
            center=["50%", "50%"],
            rosetype="radius",
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            legend_opts=opts.LegendOpts(orient="vertical", pos_top="10%", pos_left="5%"),
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"),
        )
    )
    return pie

def create_line_chart(df: pd.DataFrame, title: str = "词频折线图", top_n: int = 20) -> Line:
    top_df = df.head(top_n)
    line = (
        Line()
        .add_xaxis(top_df['词汇'].tolist())
        .add_yaxis("词频", top_df['频率'].tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            datazoom_opts=[opts.DataZoomOpts()],
        )
    )
    return line

def create_scatter_chart(df: pd.DataFrame, title: str = "词频散点图", top_n: int = 20) -> Scatter:
    top_df = df.head(top_n)
    scatter = (
        Scatter()
        .add_xaxis(top_df['词汇'].tolist())
        .add_yaxis("词频", top_df['频率'].tolist())
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
        )
    )
    return scatter

def create_funnel_chart(df: pd.DataFrame, title: str = "词频漏斗图", top_n: int = 20) -> Funnel:
    top_df = df.head(top_n)
    funnel = (
        Funnel()
        .add(
            series_name="词频",
            data_pair=[(word, int(freq)) for word, freq in zip(top_df['词汇'], top_df['频率'])],
            gap=3,
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
        )
    )
    return funnel

def create_radar_chart(df: pd.DataFrame, title: str = "词频雷达图", top_n: int = 10) -> Radar:
    top_df = df.head(min(top_n, 10))
    
    max_freq = float(max(df['频率'])) * 1.1
    schema = [
        opts.RadarIndicatorItem(name=word, max_=max_freq)
        for word in top_df['词汇'].tolist()
    ]
    
    radar = (
        Radar()
        .add_schema(schema=schema)
        .add(
            series_name="词频分布",
            data=[top_df['频率'].tolist()],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
        )
    )
    return radar