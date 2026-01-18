# 数据分析仓库

这个仓库包含用于数据分析的各种工具和脚本，主要分为**时间序列分析**和**用户行为分析**两个模块。

## 目录结构

```
data_analysis/
├── calculate_user_segments.py    # 用户分群计算脚本
├── create_sqlite_db.py           # SQLite数据库创建脚本
├── example_data_and_results.md   # 示例数据和SQL执行结果说明
├── test_mysql_connection.py      # MySQL连接测试脚本
├── time_series_data.csv          # 生成的时间序列数据文件
├── time_series_plot.png          # 时间序列可视化图表
├── time_series_statistics.py     # 时间序列分析主脚本
├── user_behavior_analysis.db     # 用户行为分析数据库
├── user_segment_definitions.md   # 用户分群定义说明
├── user_segment_flowchart.md     # 用户分群流程图
└── user_segment_sql.sql          # 用户分群SQL脚本
```

## 模块介绍

### 1. 时间序列分析模块

#### 功能
- 生成模拟时间序列数据（包含趋势、季节性和噪声）
- 计算时间序列的各种统计信息
- 可视化时间序列数据及其移动平均线

#### 文件
- `time_series_statistics.py`: 时间序列分析的主脚本
- `time_series_data.csv`: 生成的时间序列数据文件
- `time_series_plot.png`: 生成的可视化图表

#### 使用方法

```bash
# 运行时间序列分析脚本
python time_series_statistics.py
```

该脚本将：
1. 生成2023年全年的模拟时间序列数据
2. 计算基本统计信息、描述性统计和移动平均
3. 生成包含原始数据和移动平均线的图表
4. 将处理后的数据保存为CSV文件

### 2. 用户行为分析模块

#### 功能
- 分析用户行为日志数据
- 自动计算用户标签（活跃、留存、回流、流失）
- 提供标签统计和分析

#### 定义的用户标签

| 标签类型 | 定义 |
|---------|------|
| **活跃用户** | 在观察日有指定活跃行为（如登录）的用户 |
| **留存用户** | 在基准日和目标日都有活跃行为的用户 |
| **回流用户** | 曾经流失后又重新活跃的用户 |
| **流失用户** | 连续超过指定天数不活跃的用户 |

#### 文件
- `user_segment_sql.sql`: 用户分群计算的核心SQL脚本
- `create_sqlite_db.py`: 创建SQLite数据库和表结构
- `example_data_and_results.md`: 示例数据和执行结果说明
- `user_behavior_analysis.db`: SQLite数据库文件
- `user_segment_definitions.md`: 用户分群详细定义
- `user_segment_flowchart.md`: 用户分群逻辑流程图

#### 使用方法

1. **创建数据库和表结构**:
```bash
python create_sqlite_db.py
```

2. **执行用户分群SQL脚本**:
   - 在SQLite客户端中打开`user_behavior_analysis.db`
   - 执行`user_segment_sql.sql`中的SQL语句
   - 查看`user_segments`表获取用户标签结果

3. **分析结果**:
   - 查看`example_data_and_results.md`了解预期结果和分析方法
   - 使用`calculate_user_segments.py`进行更高级的分析

## 技术栈

- **编程语言**: Python 3.x
- **数据分析**: pandas, numpy, matplotlib
- **数据库**: SQLite, MySQL
- **版本控制**: Git

## 安装依赖

```bash
pip install pandas numpy matplotlib
```

## 项目特点

1. **模块化设计**: 各功能模块独立，便于扩展和维护
2. **可重现性**: 所有分析结果都可通过脚本重现
3. **可视化输出**: 提供直观的数据可视化图表
4. **详细文档**: 包含示例数据、结果说明和用户分群定义

## 使用场景

- **时间序列预测**: 分析业务指标的趋势和季节性
- **用户行为分析**: 了解用户活跃、留存、回流和流失情况
- **业务决策支持**: 基于数据分析结果制定运营策略

## 扩展建议

1. 添加更多时间序列模型（如ARIMA、LSTM）
2. 支持更多数据源（如CSV、API、数据库）
3. 开发Web界面用于交互式分析
4. 添加自动化报告生成功能

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

本项目采用MIT许可证。
