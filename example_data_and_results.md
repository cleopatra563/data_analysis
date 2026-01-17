# 示例数据与SQL执行结果说明

## 1. 示例数据

### 1.1 用户行为日志示例数据

以下是`user_behavior_logs`表的示例数据，包含了不同用户在不同时间的行为记录，用于演示标签计算逻辑：

| user_id | behavior_type | behavior_time       | device_type | channel   |
|---------|---------------|---------------------|-------------|-----------|
| user_001| login         | 2023-06-28 09:30:00 | mobile      | appstore  |
| user_001| login         | 2023-06-29 10:15:00 | mobile      | appstore  |
| user_001| login         | 2023-06-30 11:00:00 | mobile      | appstore  |
| user_002| login         | 2023-06-29 14:20:00 | desktop     | google    |
| user_002| login         | 2023-06-30 15:45:00 | desktop     | google    |
| user_003| login         | 2023-06-25 08:50:00 | mobile      | wechat    |
| user_003| login         | 2023-06-30 09:10:00 | mobile      | wechat    |
| user_004| login         | 2023-06-20 13:30:00 | desktop     | baidu     |
| user_004| login         | 2023-06-30 16:20:00 | mobile      | appstore  |
| user_005| login         | 2023-06-21 10:00:00 | mobile      | weibo     |
| user_006| login         | 2023-06-15 17:45:00 | desktop     | direct    |
| user_007| login         | 2023-06-30 08:30:00 | mobile      | appstore  |
| user_008| login         | 2023-06-28 11:20:00 | mobile      | wechat    |
| user_009| login         | 2023-06-20 09:00:00 | desktop     | google    |
| user_010| login         | 2023-06-30 10:30:00 | desktop     | direct    |

### 1.2 参数配置

使用以下参数进行标签计算：

```sql
SET @observation_date = '2023-06-30';
SET @active_behavior = 'login';
SET @active_window = 1;
SET @retention_base_period = 1;
SET @retention_target_period = 1;
SET @churn_threshold = 7;
SET @return_churn_period = 7;
```

## 2. SQL执行步骤

### 步骤1：创建数据表

执行SQL脚本中的表创建语句：

```sql
CREATE TABLE IF NOT EXISTS user_behavior_logs (...);
CREATE TABLE IF NOT EXISTS user_segments (...);
```

### 步骤2：插入示例数据

执行以下SQL语句插入示例数据：

```sql
INSERT INTO user_behavior_logs (user_id, behavior_type, behavior_time, device_type, channel)
VALUES
('user_001', 'login', '2023-06-28 09:30:00', 'mobile', 'appstore'),
('user_001', 'login', '2023-06-29 10:15:00', 'mobile', 'appstore'),
('user_001', 'login', '2023-06-30 11:00:00', 'mobile', 'appstore'),
('user_002', 'login', '2023-06-29 14:20:00', 'desktop', 'google'),
('user_002', 'login', '2023-06-30 15:45:00', 'desktop', 'google'),
('user_003', 'login', '2023-06-25 08:50:00', 'mobile', 'wechat'),
('user_003', 'login', '2023-06-30 09:10:00', 'mobile', 'wechat'),
('user_004', 'login', '2023-06-20 13:30:00', 'desktop', 'baidu'),
('user_004', 'login', '2023-06-30 16:20:00', 'mobile', 'appstore'),
('user_005', 'login', '2023-06-21 10:00:00', 'mobile', 'weibo'),
('user_006', 'login', '2023-06-15 17:45:00', 'desktop', 'direct'),
('user_007', 'login', '2023-06-30 08:30:00', 'mobile', 'appstore'),
('user_008', 'login', '2023-06-28 11:20:00', 'mobile', 'wechat'),
('user_009', 'login', '2023-06-20 09:00:00', 'desktop', 'google'),
('user_010', 'login', '2023-06-30 10:30:00', 'desktop', 'direct');
```

### 步骤3：执行标签计算

运行SQL脚本中的标签计算部分，这将自动计算所有用户标签并存储到`user_segments`表中。

### 步骤4：查询结果

执行以下查询查看标签统计结果：

```sql
-- 查询所有标签统计
SELECT 
    COUNT(*) AS total_users,
    SUM(CASE WHEN is_active THEN 1 ELSE 0 END) AS active_users,
    SUM(CASE WHEN is_retained THEN 1 ELSE 0 END) AS retained_users,
    SUM(CASE WHEN is_returning THEN 1 ELSE 0 END) AS returning_users,
    SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) AS churned_users
FROM user_segments
WHERE calc_date = @observation_date;

-- 查询具体用户的标签
SELECT 
    user_id,
    calc_date,
    CASE WHEN is_active THEN '是' ELSE '否' END AS 活跃用户,
    CASE WHEN is_retained THEN '是' ELSE '否' END AS 留存用户,
    CASE WHEN is_returning THEN '是' ELSE '否' END AS 回流用户,
    CASE WHEN is_churned THEN '是' ELSE '否' END AS 流失用户
FROM user_segments
WHERE calc_date = @observation_date
ORDER BY user_id;
```

## 3. 预期执行结果

### 3.1 标签统计结果

| total_users | active_users | retained_users | returning_users | churned_users |
|-------------|--------------|----------------|-----------------|---------------|
| 10          | 6            | 2              | 2               | 2             |

### 3.2 具体用户标签结果

| user_id | calc_date  | 活跃用户 | 留存用户 | 回流用户 | 流失用户 |
|---------|------------|----------|----------|----------|----------|
| user_001| 2023-06-30 | 是       | 是       | 否       | 否       |
| user_002| 2023-06-30 | 是       | 是       | 否       | 否       |
| user_003| 2023-06-30 | 是       | 否       | 是       | 否       |
| user_004| 2023-06-30 | 是       | 否       | 是       | 否       |
| user_005| 2023-06-30 | 否       | 否       | 否       | 是       |
| user_006| 2023-06-30 | 否       | 否       | 否       | 是       |
| user_007| 2023-06-30 | 是       | 否       | 否       | 否       |
| user_008| 2023-06-30 | 否       | 否       | 否       | 否       |
| user_009| 2023-06-30 | 否       | 否       | 否       | 否       |
| user_010| 2023-06-30 | 是       | 否       | 否       | 否       |

## 4. 结果分析与解释

### 4.1 各标签用户分析

#### 活跃用户（6人）
- **用户**：user_001, user_002, user_003, user_004, user_007, user_010
- **分析**：在2023-06-30当天有登录行为的用户

#### 留存用户（2人）
- **用户**：user_001, user_002
- **分析**：在2023-06-29（基准日）和2023-06-30（目标日）都有登录行为，即次日留存用户

#### 回流用户（2人）
- **用户**：user_003, user_004
- **分析**：
  - user_003：最后一次登录在2023-06-25，中间超过7天不活跃，2023-06-30重新登录
  - user_004：最后一次登录在2023-06-20，中间超过7天不活跃，2023-06-30重新登录

#### 流失用户（2人）
- **用户**：user_005, user_006
- **分析**：
  - user_005：最后一次登录在2023-06-21，连续超过7天不活跃
  - user_006：最后一次登录在2023-06-15，连续超过7天不活跃

#### 其他用户（4人）
- **用户**：user_008, user_009, user_010
- **分析**：
  - user_008：最后一次登录在2023-06-28，未达到连续7天不活跃的流失阈值
  - user_009：最后一次登录在2023-06-20，未达到连续7天不活跃的流失阈值
  - user_010：仅在2023-06-30登录，是新用户或首次活跃用户

### 4.2 业务意义解读

1. **活跃用户占比**：6/10 = 60%，说明大部分历史用户在观察日仍有活跃
2. **留存率**：2/6 = 33.3%（次日留存），反映用户粘性良好
3. **回流率**：2/6 = 33.3%（活跃用户中回流比例），说明召回效果显著
4. **流失率**：2/10 = 20%（总用户中流失比例），需关注流失原因

## 5. 扩展应用建议

### 5.1 多维度分析

可以按设备类型、渠道等维度进行分组分析：

```sql
-- 按设备类型分析
SELECT 
    device_type,
    COUNT(*) AS total_users,
    SUM(CASE WHEN s.is_active THEN 1 ELSE 0 END) AS active_users
FROM user_segments s
JOIN (
    SELECT user_id, device_type FROM user_behavior_logs 
    WHERE behavior_time BETWEEN DATE_SUB(@observation_date, INTERVAL 30 DAY) AND @observation_date
    GROUP BY user_id
    ORDER BY behavior_time DESC
    LIMIT 1
) b ON s.user_id = b.user_id
WHERE s.calc_date = @observation_date
GROUP BY device_type;
```

### 5.2 时间趋势分析

创建每日标签统计视图，分析标签变化趋势：

```sql
SELECT * FROM daily_user_segment_stats;
```

### 5.3 活跃行为扩展

扩展活跃行为定义，包含更多核心功能：

```sql
-- 将购买行为也定义为活跃
SET @active_behavior = 'login';
-- 修改SQL中的条件
WHERE behavior_type IN ('login', 'purchase')
```

## 6. 性能优化建议

1. **索引优化**：在`user_behavior_logs`表上创建复合索引：
   ```sql
   CREATE INDEX idx_user_behavior ON user_behavior_logs(user_id, behavior_time, behavior_type);
   ```

2. **增量计算**：对于大数据量，可考虑增量计算而非全量计算，只处理新增数据

3. **分区表**：按行为时间对`user_behavior_logs`表进行分区，提高查询效率

4. **预聚合**：创建每日活跃用户的预聚合表，减少重复计算