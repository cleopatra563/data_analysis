-- 用户人群标签计算SQL脚本
-- 支持：活跃用户、留存用户、回流用户、流失用户
-- 使用通用SQL语法，兼容主流数据库

-- =========================================
-- 1. 创建示例数据表结构
-- =========================================

-- 用户行为日志表
CREATE TABLE IF NOT EXISTS user_behavior_logs (
    user_id VARCHAR(50) NOT NULL,    -- 用户ID
    behavior_type VARCHAR(20) NOT NULL, -- 行为类型（如login, click, purchase等）
    behavior_time DATETIME NOT NULL,    -- 行为时间戳
    device_type VARCHAR(20),           -- 设备类型
    channel VARCHAR(20),               -- 渠道来源
    PRIMARY KEY (user_id, behavior_time, behavior_type)
);

-- 用户标签结果表
CREATE TABLE IF NOT EXISTS user_segments (
    user_id VARCHAR(50) NOT NULL,      -- 用户ID
    calc_date DATE NOT NULL,           -- 计算日期
    is_active BOOLEAN,                 -- 是否为活跃用户
    is_retained BOOLEAN,               -- 是否为留存用户
    is_returning BOOLEAN,              -- 是否为回流用户
    is_churned BOOLEAN,                -- 是否为流失用户
    PRIMARY KEY (user_id, calc_date)
);

-- =========================================
-- 2. 配置参数（可根据业务需求调整）
-- =========================================

-- 定义观察日期（这里使用动态参数，实际应用中可传入）
SET @observation_date = '2023-06-30';

-- 活跃行为定义：这里仅包含login行为，可根据业务扩展
SET @active_behavior = 'login';

-- 时间周期配置（单位：天）
SET @active_window = 1;          -- 活跃用户的观察窗口（日活）
SET @retention_base_period = 1;   -- 留存用户的基准周期（前一天）
SET @retention_target_period = 1; -- 留存用户的目标周期（次日）
SET @churn_threshold = 7;         -- 流失用户的连续不活跃天数阈值
SET @return_churn_period = 7;     -- 回流用户的流失观察窗口（至少7天不活跃）

-- =========================================
-- 3. 计算活跃用户
-- =========================================

WITH active_users AS (
    SELECT DISTINCT user_id
    FROM user_behavior_logs
    WHERE behavior_type = @active_behavior
    AND behavior_time BETWEEN 
        DATE_SUB(@observation_date, INTERVAL @active_window DAY)
        AND @observation_date
),

-- =========================================
-- 4. 计算留存用户（次日留存示例）
-- =========================================

-- 基准日活跃用户
base_period_active AS (
    SELECT DISTINCT user_id
    FROM user_behavior_logs
    WHERE behavior_type = @active_behavior
    AND behavior_time BETWEEN 
        DATE_SUB(@observation_date, INTERVAL (@retention_base_period + @retention_target_period) DAY)
        AND DATE_SUB(@observation_date, INTERVAL @retention_target_period DAY)
),

-- 目标日活跃用户
retention_users AS (
    SELECT DISTINCT b.user_id
    FROM base_period_active b
    INNER JOIN user_behavior_logs u ON b.user_id = u.user_id
    WHERE u.behavior_type = @active_behavior
    AND u.behavior_time BETWEEN 
        DATE_SUB(@observation_date, INTERVAL @retention_target_period DAY)
        AND @observation_date
),

-- =========================================
-- 5. 计算回流用户
-- =========================================

-- 观察周期活跃用户
obs_period_active AS (
    SELECT DISTINCT user_id
    FROM user_behavior_logs
    WHERE behavior_type = @active_behavior
    AND behavior_time BETWEEN 
        DATE_SUB(@observation_date, INTERVAL @active_window DAY)
        AND @observation_date
),

-- 流失观察窗口内的非活跃用户
churn_window_inactive AS (
    SELECT DISTINCT user_id
    FROM user_behavior_logs
    GROUP BY user_id
    HAVING 
        -- 在观察周期内活跃
        MAX(behavior_time) BETWEEN 
            DATE_SUB(@observation_date, INTERVAL @active_window DAY)
            AND @observation_date
        -- 在前@return_churn_period天内不活跃
        AND MAX(CASE WHEN behavior_time BETWEEN 
                DATE_SUB(@observation_date, INTERVAL (@active_window + @return_churn_period) DAY)
                AND DATE_SUB(@observation_date, INTERVAL @active_window DAY)
            THEN behavior_time END) IS NULL
        -- 更早的时间曾活跃过
        AND MAX(CASE WHEN behavior_time < 
                DATE_SUB(@observation_date, INTERVAL (@active_window + @return_churn_period) DAY)
            THEN behavior_time END) IS NOT NULL
),

-- 回流用户
returning_users AS (
    SELECT user_id
    FROM churn_window_inactive
),

-- =========================================
-- 6. 计算流失用户
-- =========================================

-- 流失用户
churned_users AS (
    SELECT user_id
    FROM user_behavior_logs
    GROUP BY user_id
    HAVING 
        -- 在观察周期内不活跃
        MAX(CASE WHEN behavior_time BETWEEN 
                DATE_SUB(@observation_date, INTERVAL @churn_threshold DAY)
                AND @observation_date
            THEN behavior_time END) IS NULL
        -- 更早的时间曾活跃过
        AND MAX(CASE WHEN behavior_time < 
                DATE_SUB(@observation_date, INTERVAL @churn_threshold DAY)
            THEN behavior_time END) IS NOT NULL
),

-- =========================================
-- 7. 整合所有标签
-- =========================================

-- 获取所有需要打标签的用户（去重）
all_users AS (
    SELECT DISTINCT user_id FROM user_behavior_logs
),

-- 生成用户标签
user_tags AS (
    SELECT 
        u.user_id,
        @observation_date AS calc_date,
        -- 活跃用户标签
        CASE WHEN a.user_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_active,
        -- 留存用户标签
        CASE WHEN r.user_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_retained,
        -- 回流用户标签
        CASE WHEN rt.user_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_returning,
        -- 流失用户标签
        CASE WHEN c.user_id IS NOT NULL THEN TRUE ELSE FALSE END AS is_churned
    FROM all_users u
    LEFT JOIN active_users a ON u.user_id = a.user_id
    LEFT JOIN retention_users r ON u.user_id = r.user_id
    LEFT JOIN returning_users rt ON u.user_id = rt.user_id
    LEFT JOIN churned_users c ON u.user_id = c.user_id
)

-- =========================================
-- 8. 插入或更新标签结果
-- =========================================

-- 删除旧数据（如果存在）
DELETE FROM user_segments 
WHERE calc_date = @observation_date;

-- 插入新的标签结果
INSERT INTO user_segments (
    user_id, calc_date, is_active, is_retained, is_returning, is_churned
) 
SELECT 
    user_id, calc_date, is_active, is_retained, is_returning, is_churned
FROM user_tags;

-- =========================================
-- 9. 查询示例
-- =========================================

-- 查询所有标签统计
SELECT 
    COUNT(*) AS total_users,
    SUM(CASE WHEN is_active THEN 1 ELSE 0 END) AS active_users,
    SUM(CASE WHEN is_retained THEN 1 ELSE 0 END) AS retained_users,
    SUM(CASE WHEN is_returning THEN 1 ELSE 0 END) AS returning_users,
    SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) AS churned_users,
    SUM(CASE WHEN is_active AND is_retained THEN 1 ELSE 0 END) AS active_retained_users,
    SUM(CASE WHEN is_active AND is_returning THEN 1 ELSE 0 END) AS active_returning_users
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
ORDER BY user_id
LIMIT 10;

-- =========================================
-- 10. 创建视图：按日统计各标签用户数量
-- =========================================

CREATE OR REPLACE VIEW daily_user_segment_stats AS
SELECT 
    calc_date,
    COUNT(*) AS total_users,
    SUM(CASE WHEN is_active THEN 1 ELSE 0 END) AS active_users,
    SUM(CASE WHEN is_retained THEN 1 ELSE 0 END) AS retained_users,
    SUM(CASE WHEN is_returning THEN 1 ELSE 0 END) AS returning_users,
    SUM(CASE WHEN is_churned THEN 1 ELSE 0 END) AS churned_users
FROM user_segments
GROUP BY calc_date
ORDER BY calc_date DESC;

-- 查询每日标签统计
SELECT * FROM daily_user_segment_stats;

-- =========================================
-- 11. 示例数据插入（用于测试）
-- =========================================

/*
-- 插入测试数据
INSERT INTO user_behavior_logs (user_id, behavior_type, behavior_time, device_type, channel)
VALUES
-- 活跃用户
('user_001', 'login', '2023-06-30 10:30:00', 'mobile', 'appstore'),
('user_002', 'login', '2023-06-30 11:45:00', 'desktop', 'google'),
-- 留存用户（6月29日和30日都活跃）
('user_001', 'login', '2023-06-29 09:20:00', 'mobile', 'appstore'),
('user_003', 'login', '2023-06-29 15:30:00', 'mobile', 'wechat'),
('user_003', 'login', '2023-06-30 14:20:00', 'mobile', 'wechat'),
-- 回流用户（6月22日之前活跃，6月23-29日不活跃，6月30日重新活跃）
('user_004', 'login', '2023-06-20 13:15:00', 'desktop', 'baidu'),
('user_004', 'login', '2023-06-30 16:40:00', 'mobile', 'appstore'),
-- 流失用户（6月22日之后一直不活跃）
('user_005', 'login', '2023-06-21 08:50:00', 'mobile', 'weibo'),
('user_006', 'login', '2023-06-20 17:25:00', 'desktop', 'direct');
*/

-- =========================================
-- 12. 清理测试数据（可选）
-- =========================================

-- DELETE FROM user_behavior_logs;
-- DELETE FROM user_segments;

-- =========================================
-- 13. 扩展说明
-- =========================================
-- 1. 活跃行为定义扩展：
--    可通过修改@active_behavior参数或在WHERE条件中添加更多行为类型来扩展活跃定义
--    例如：behavior_type IN ('login', 'purchase', 'play_video')

-- 2. 留存用户类型扩展：
--    可通过修改@retention_base_period和@retention_target_period参数来计算不同类型的留存
--    例如：
--    - 次日留存：base=1, target=1
--    - 7日留存：base=1, target=6
--    - 30日留存：base=1, target=29

-- 3. 性能优化建议：
--    - 在user_behavior_logs表的(user_id, behavior_time)字段上创建索引
--    - 对于大数据量，可考虑按时间分区
--    - 使用增量计算而非全量计算

-- 4. 多维度标签扩展：
--    可根据device_type、channel等维度进行分组计算
--    例如：按渠道统计各标签用户数量