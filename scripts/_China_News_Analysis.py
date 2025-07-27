# WSJ中国相关新闻数据分析

# 这个Python脚本用于分析筛选后的中国相关新闻数据，包括：
# 1. 数据基本统计信息
# 2. 时间分布分析
# 3. 关键词类型分布
# 4. 数据质量检查

# Block 1: 导入必要的库
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import re
from collections import Counter

# 设置图形显示参数
plt.rcParams['figure.figsize'] = (12, 8)

# 设置字体为英文，避免中文字体问题
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Bitstream Vera Sans', 'Lucida Grande', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

sns.set_style("whitegrid")

# 设置pandas显示选项
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 100)

print("✅ 必要的库已导入完成")

# Block 2: 设置文件路径和全局变量

# 文件路径配置
ALIYUN_OSS_PATH = ''
FINAL_CHINA_NEWS_FILE = ALIYUN_OSS_PATH + 'data_processed/final_china_news.csv'  # 精筛后的最终结果
KEYWORD_JSON_PATH = ALIYUN_OSS_PATH + 'data_raw/china_keywords_collection.json'  # 关键词 JSON 文件
REJECTED_FILE = ALIYUN_OSS_PATH + 'data_processed/china_news_rejected_articles.csv'  # 被拒绝的文章

# 新闻列名
NEWS_COLUMN = 'CONTENT'
DATE_COLUMN = 'DATE'  # 假设日期列名为DATE

print("✅ 文件路径和全局变量设置完成")


# 块3: 加载数据

def load_data(file_path):
    """
    加载CSV数据文件
    """
    try:
        df = pd.read_csv(file_path, low_memory=False)
        print(f"✅ 成功加载数据文件: {file_path}")
        print(f"   数据形状: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"❌ 错误: 文件未找到 {file_path}")
        return None
    except Exception as e:
        print(f"❌ 加载数据时发生错误: {e}")
        return None


# 加载最终的中国相关新闻数据
df_china_news = load_data(FINAL_CHINA_NEWS_FILE)

# 加载被拒绝的文章数据
df_rejected = load_data(REJECTED_FILE)


# 加载关键词数据
def load_keywords(json_path):
    """
    加载关键词JSON文件
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            keywords_data = json.load(f)
        print(f"✅ 成功加载关键词文件: {json_path}")
        print(f"   关键词数量: {len(keywords_data)}")
        return keywords_data
    except FileNotFoundError:
        print(f"❌ 错误: 关键词文件未找到 {json_path}")
        return None
    except Exception as e:
        print(f"❌ 加载关键词时发生错误: {e}")
        return None


keywords_data = load_keywords(KEYWORD_JSON_PATH)


# 块4: 数据基本统计信息

def basic_statistics(df, name="数据集"):
    """
    显示数据集的基本统计信息
    """
    if df is None:
        print(f"❌ {name} 数据为空")
        return

    print(f"\n=== {name} 基本统计信息 ===")
    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    print(f"\n前5行数据:")
    print(df.head())

    print(f"\n数据类型:")
    print(df.dtypes)

    print(f"\n缺失值统计:")
    missing_data = df.isnull().sum()
    missing_data = missing_data[missing_data > 0]
    if len(missing_data) > 0:
        print(missing_data)
    else:
        print("无缺失值")


# 显示最终中国新闻数据的基本统计信息
if df_china_news is not None:
    basic_statistics(df_china_news, "最终中国相关新闻")

# 显示被拒绝文章的基本统计信息
if df_rejected is not None:
    basic_statistics(df_rejected, "被拒绝的文章")


# 块5: 时间分布分析

def analyze_time_distribution(df, date_column=DATE_COLUMN, name="数据集"):
    """
    分析数据的时间分布
    """
    if df is None or date_column not in df.columns:
        print(f"❌ {name} 中缺少日期列 {date_column}")
        return

    # 转换日期列
    try:
        df['parsed_date'] = pd.to_datetime(df[date_column], errors='coerce')
    except Exception as e:
        print(f"❌ 日期转换失败: {e}")
        return

    # 检查转换后的日期
    valid_dates = df['parsed_date'].notna().sum()
    print(f"\n=== {name} 时间分布分析 ===")
    print(f"有效日期数量: {valid_dates}/{len(df)} ({valid_dates / len(df) * 100:.2f}%)")

    if valid_dates == 0:
        print("没有有效的日期数据")
        return

    # 按年统计，包括没有数据的年份
    df['year'] = df['parsed_date'].dt.year
    yearly_counts = df['year'].value_counts().sort_index()

    # 创建完整年份范围，包括没有数据的年份
    if len(yearly_counts) > 0:
        min_year = int(yearly_counts.index.min())
        max_year = int(yearly_counts.index.max())
        all_years = pd.Series(0, index=range(min_year, max_year + 1))
        yearly_counts = yearly_counts.combine(all_years, lambda x, y: x if not pd.isna(x) else y, fill_value=0)
        yearly_counts = yearly_counts.sort_index()

    print(f"\n年份分布:")
    print(yearly_counts)

    # 绘制年度分布图
    plt.figure(figsize=(15, 6))
    ax = yearly_counts.plot(kind='bar')
    plt.title('Final China News - Annual Distribution')
    plt.xlabel('Year')
    plt.ylabel('Number of Articles')
    plt.xticks(rotation=45)
    
    # 在柱状图上添加数值标签
    for i, v in enumerate(yearly_counts.values):
        if v > 0:  # 只为有数据的年份添加标签
            ax.text(i, v + 0.5, str(v), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()

    # 按月统计
    df['year_month'] = df['parsed_date'].dt.to_period('M')
    recent_months = df['year_month'].value_counts().sort_index()

    plt.figure(figsize=(15, 6))
    recent_months.plot(kind='line', marker='o')
    plt.title('Final China News - All Months Distribution')
    plt.xlabel('Year-Month')
    plt.ylabel('Number of Articles')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


# 分析最终中国新闻的时间分布
if df_china_news is not None:
    analyze_time_distribution(df_china_news, DATE_COLUMN, "Final China News")


# 块6: 关键词分析准备

def prepare_keyword_analysis(keywords_data):
    """
    准备关键词分析所需的数据结构
    """
    if keywords_data is None:
        print("❌ 关键词数据为空")
        return None, None, None

    # 创建关键词到信息的映射
    keyword_to_info = {}
    all_aliases = set()

    for item in keywords_data:
        main_keyword = item['keyword'].lower()
        keyword_to_info[main_keyword] = item
        all_aliases.add(main_keyword)

        # 添加别名
        for alias in item.get('aliases', []):
            alias_lower = alias.lower()
            keyword_to_info[alias_lower] = item
            all_aliases.add(alias_lower)

    print(f"✅ 关键词分析准备完成")
    print(f"   唯一关键词/别名数量: {len(all_aliases)}")

    return keyword_to_info, all_aliases, keywords_data


# 准备关键词分析
keyword_to_info, all_aliases, keywords_data = prepare_keyword_analysis(keywords_data)


# 块7: 简单关键词匹配分析

def simple_keyword_matching(df, all_aliases, keyword_to_info, news_column=NEWS_COLUMN, top_n=20):
    """
    通过简单的字符串匹配分析关键词出现频率
    """
    if df is None or all_aliases is None or keyword_to_info is None:
        print("❌ 数据不完整，无法进行关键词匹配分析")
        return

    print(f"\n=== 简单关键词匹配分析 ===")
    print(f"正在分析 {len(df)} 篇文章中的关键词...")

    # 统计关键词出现次数
    keyword_counts = Counter()
    category_counts = Counter()
    type_counts = Counter()
    tier_counts = Counter()

    # 按文章进行分析
    for idx, row in df.iterrows():
        if news_column not in row:
            continue

        content = str(row[news_column]).lower()
        found_keywords = []

        # 查找匹配的关键词
        for alias in all_aliases:
            if alias in content:
                keyword_counts[alias] += 1
                found_keywords.append(alias)

        # 记录找到的关键词的分类、类型和层级
        for keyword in found_keywords:
            if keyword in keyword_to_info:
                info = keyword_to_info[keyword]
                category_counts[info.get('category', 'Unknown')] += 1
                type_counts[info.get('type', 'Unknown')] += 1
                tier_counts[info.get('relevance_tier', 'Unknown')] += 1

    # 显示最常见的关键词
    print(f"\n最常见的 {min(top_n, len(keyword_counts))} 个关键词:")
    for keyword, count in keyword_counts.most_common(top_n):
        info = keyword_to_info.get(keyword, {})
        main_keyword = info.get('keyword', keyword)
        category = info.get('category', 'Unknown')
        print(f"  {keyword} ({main_keyword}) - {count} 次 - 分类: {category}")

    # 绘制分类分布
    plt.figure(figsize=(12, 6))
    categories = list(category_counts.keys())
    counts = list(category_counts.values())
    bars = plt.bar(range(len(categories)), counts)
    plt.title('Keyword Category Distribution')
    plt.xlabel('Category')
    plt.ylabel('Frequency')
    plt.xticks(range(len(categories)), categories, rotation=45, ha='right')

    # 在柱状图上添加数值标签
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 str(count), ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

    # 显示类型分布
    print(f"\n关键词类型分布:")
    for type_name, count in type_counts.most_common():
        print(f"  {type_name}: {count} 次")

    # 绘制类型分布
    plt.figure(figsize=(10, 6))
    types = list(type_counts.keys())
    counts = list(type_counts.values())
    bars = plt.bar(range(len(types)), counts)
    plt.title('Keyword Type Distribution')
    plt.xlabel('Type')
    plt.ylabel('Frequency')
    plt.xticks(range(len(types)), types, rotation=45, ha='right')

    # 在柱状图上添加数值标签
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 str(count), ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

    # 显示相关性层级分布
    print(f"\n相关性层级分布:")
    for tier, count in sorted(tier_counts.items()):
        print(f"  层级 {tier}: {count} 次")

    # 绘制相关性层级分布
    plt.figure(figsize=(8, 6))
    tiers = sorted(list(tier_counts.keys()))
    counts = [tier_counts[t] for t in tiers]
    bars = plt.bar(range(len(tiers)), counts)
    plt.title('Keyword Relevance Tier Distribution')
    plt.xlabel('Relevance Tier')
    plt.ylabel('Frequency')
    plt.xticks(range(len(tiers)), [f'Tier {t}' for t in tiers])

    # 在柱状图上添加数值标签
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 str(count), ha='center', va='bottom')

    plt.tight_layout()
    plt.show()


# 执行简单关键词匹配分析
if df_china_news is not None and keyword_to_info is not None and all_aliases is not None:
    simple_keyword_matching(df_china_news, all_aliases, keyword_to_info, NEWS_COLUMN)


# 块8: 数据质量检查

def data_quality_check(df, news_column=NEWS_COLUMN):
    """
    检查数据质量
    """
    if df is None:
        print("❌ 数据为空，无法进行质量检查")
        return

    print(f"\n=== 数据质量检查 ===")

    # 检查重复文章
    if news_column in df.columns:
        duplicate_articles = df.duplicated(subset=[news_column]).sum()
        print(f"重复文章数量: {duplicate_articles}/{len(df)} ({duplicate_articles / len(df) * 100:.2f}%)")

    # 检查文章长度分布
    if news_column in df.columns:
        df['content_length'] = df[news_column].astype(str).apply(len)
        print(f"\n文章长度统计:")
        print(f"  最短: {df['content_length'].min()} 字符")
        print(f"  最长: {df['content_length'].max()} 字符")
        print(f"  平均: {df['content_length'].mean():.1f} 字符")
        print(f"  中位数: {df['content_length'].median():.1f} 字符")

        # 绘制文章长度分布
        plt.figure(figsize=(10, 6))
        plt.hist(df['content_length'], bins=50, edgecolor='black', alpha=0.7)
        plt.title('Article Length Distribution')
        plt.xlabel('Characters')
        plt.ylabel('Number of Articles')
        plt.axvline(df['content_length'].mean(), color='red', linestyle='--',
                    label=f"Average: {df['content_length'].mean():.1f}")
        plt.legend()
        plt.tight_layout()
        plt.show()

    # 检查异常短文
    if 'content_length' in df.columns:
        short_articles = (df['content_length'] < 50).sum()
        print(f"\n异常短文数量 (<50字符): {short_articles}")


# 执行数据质量检查
if df_china_news is not None:
    data_quality_check(df_china_news, NEWS_COLUMN)


# 块9: 被拒绝文章分析

# def analyze_rejected_articles(df_rejected, keyword_to_info, all_aliases):
#     """
#     分析被拒绝的文章及其拒绝原因
#     """
#     if df_rejected is None:
#         print("❌ 被拒绝文章数据为空")
#         return
#
#     print(f"\n=== 被拒绝文章分析 ===")
#     print(f"被拒绝文章总数: {len(df_rejected)}")
#
#     # 检查拒绝原因
#     if 'rejection_reason' in df_rejected.columns:
#         reason_counts = df_rejected['rejection_reason'].value_counts()
#         print(f"\n拒绝原因分布:")
#         for reason, count in reason_counts.items():
#             print(f"  {reason}: {count} 篇")
#
#         # 绘制拒绝原因分布
#         plt.figure(figsize=(10, 6))
#         reason_counts.plot(kind='bar')
#         plt.title('Rejected Articles Reason Distribution')
#         plt.xlabel('Rejection Reason')
#         plt.ylabel('Number of Articles')
#         plt.xticks(rotation=45, ha='right')
#         plt.tight_layout()
#         plt.show()
#
#     # 分析被拒绝文章中的关键词
#     if 'CONTENT' in df_rejected.columns and all_aliases:
#         print(f"\n分析被拒绝文章中的关键词...")
#         rejected_keyword_counts = Counter()
#
#         for idx, row in df_rejected.iterrows():
#             content = str(row['CONTENT']).lower()
#             for alias in all_aliases:
#                 if alias in content:
#                     rejected_keyword_counts[alias] += 1
#
#         print(f"被拒绝文章中最常见的10个关键词:")
#         for keyword, count in rejected_keyword_counts.most_common(10):
#             info = keyword_to_info.get(keyword, {})
#             main_keyword = info.get('keyword', keyword)
#             print(f"  {keyword} ({main_keyword}) - {count} 次")
#
#
# # 分析被拒绝的文章
# if df_rejected is not None and keyword_to_info is not None and all_aliases is not None:
#     analyze_rejected_articles(df_rejected, keyword_to_info, all_aliases)


# 块10: 总结报告

def generate_summary_report(df_china_news, df_rejected, keywords_data):
    """
    生成数据分析总结报告
    """
    print(f"\n=== 数据分析总结报告 ===")

    print(f"1. 数据集概况:")
    if df_china_news is not None:
        print(f"   - 最终中国相关新闻: {len(df_china_news)} 篇")
    if df_rejected is not None:
        print(f"   - 被拒绝文章: {len(df_rejected)} 篇")
    if keywords_data is not None:
        print(f"   - 关键词总数: {len(keywords_data)} 个")

    print(f"\n2. 时间覆盖范围:")
    if df_china_news is not None and DATE_COLUMN in df_china_news.columns:
        try:
            df_china_news['parsed_date'] = pd.to_datetime(df_china_news[DATE_COLUMN], errors='coerce')
            valid_dates = df_china_news['parsed_date'].dropna()
            if len(valid_dates) > 0:
                print(f"   - 最早日期: {valid_dates.min().strftime('%Y-%m-%d')}")
                print(f"   - 最晚日期: {valid_dates.max().strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"   - 日期解析失败: {e}")

    print(f"\n3. 数据质量评估:")
    if df_china_news is not None:
        if 'content_length' in df_china_news.columns:
            avg_length = df_china_news['content_length'].mean()
            print(f"   - 平均文章长度: {avg_length:.0f} 字符")

        if NEWS_COLUMN in df_china_news.columns:
            duplicate_rate = df_china_news.duplicated(subset=[NEWS_COLUMN]).sum() / len(df_china_news) * 100
            print(f"   - 重复率: {duplicate_rate:.2f}%")

    print(f"\n4. 关键词分析:")
    if df_china_news is not None and all_aliases is not None:
        # 简单统计关键词出现情况
        total_keywords_found = 0
        for idx, row in df_china_news.iterrows():
            if NEWS_COLUMN in row:
                content = str(row[NEWS_COLUMN]).lower()
                for alias in all_aliases:
                    if alias in content:
                        total_keywords_found += 1
                        break  # 每篇文章只计数一次

        print(f"   - 包含关键词的文章比例: {total_keywords_found / len(df_china_news) * 100:.2f}%")

    print(f"\n数据分析完成！")


# 生成总结报告
generate_summary_report(df_china_news, df_rejected, keywords_data)
