import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 设置随机种子以确保结果可重现
np.random.seed(42)

# 生成模拟的时间序列数据
def generate_time_series_data(start_date='2023-01-01', end_date='2023-12-31', freq='D'):
    """生成模拟的时间序列数据"""
    # 创建日期范围
    date_range = pd.date_range(start=start_date, end=end_date, freq=freq)
    
    # 生成基础数据（趋势 + 季节性 + 噪声）
    n = len(date_range)
    trend = np.linspace(0, 100, n)  # 线性趋势
    seasonal = 20 * np.sin(np.linspace(0, 4 * np.pi, n))  # 季节性波动
    noise = np.random.normal(0, 5, n)  # 随机噪声
    
    # 组合生成数据
    values = trend + seasonal + noise
    
    # 创建DataFrame
    df = pd.DataFrame({
        'date': date_range,
        'value': values
    })
    
    # 设置日期为索引
    df.set_index('date', inplace=True)
    
    return df

# 计算时间序列统计
def time_series_statistics(df):
    """计算时间序列的各种统计信息"""
    print("=== 时间序列基本信息 ===")
    print(df.info())
    print("\n=== 描述性统计 ===")
    print(df.describe())
    
    print("\n=== 时间序列特有统计 ===")
    print(f"时间范围: {df.index.min()} 到 {df.index.max()}")
    print(f"数据点数量: {len(df)}")
    print(f"均值: {df['value'].mean():.2f}")
    print(f"中位数: {df['value'].median():.2f}")
    print(f"标准差: {df['value'].std():.2f}")
    print(f"最小值: {df['value'].min():.2f}")
    print(f"最大值: {df['value'].max():.2f}")
    print(f"25%分位数: {df['value'].quantile(0.25):.2f}")
    print(f"75%分位数: {df['value'].quantile(0.75):.2f}")
    
    # 计算移动平均
    df['rolling_mean_7'] = df['value'].rolling(window=7).mean()
    df['rolling_mean_30'] = df['value'].rolling(window=30).mean()
    print("\n=== 移动平均（最近7天和30天）===")
    print(df[['value', 'rolling_mean_7', 'rolling_mean_30']].tail())
    
    # 计算日环比和同比（如果数据频率允许）
    if df.index.freq in ['D', 'B']:
        df['daily_change'] = df['value'].pct_change() * 100
        print("\n=== 日环比变化率（%）===")
        print(df[['value', 'daily_change']].tail())
    
    return df

# 可视化时间序列
def visualize_time_series(df):
    """可视化时间序列数据"""
    plt.figure(figsize=(12, 6))
    
    # 绘制原始数据
    plt.plot(df.index, df['value'], label='原始数据', alpha=0.7)
    
    # 绘制移动平均线
    if 'rolling_mean_7' in df.columns:
        plt.plot(df.index, df['rolling_mean_7'], label='7天移动平均', color='red', linewidth=2)
    if 'rolling_mean_30' in df.columns:
        plt.plot(df.index, df['rolling_mean_30'], label='30天移动平均', color='green', linewidth=2)
    
    plt.title('时间序列数据及其移动平均线')
    plt.xlabel('日期')
    plt.ylabel('数值')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('time_series_plot.png')
    plt.close()
    print("\n时间序列图表已保存为 'time_series_plot.png'")

# 主函数
def main():
    print("生成模拟时间序列数据...")
    df = generate_time_series_data()
    
    print("\n计算时间序列统计...")
    df = time_series_statistics(df)
    
    print("\n可视化时间序列...")
    visualize_time_series(df)
    
    # 保存处理后的数据
    df.to_csv('time_series_data.csv')
    print("\n处理后的数据已保存为 'time_series_data.csv'")

if __name__ == "__main__":
    main()