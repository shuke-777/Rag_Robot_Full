# SQL 数据库基础教程

## 1. SQL 简介

SQL (Structured Query Language) 是用于管理关系型数据库的标准语言。

### 1.1 主要功能

- **数据查询 (DQL)**: SELECT
- **数据定义 (DDL)**: CREATE, ALTER, DROP
- **数据操作 (DML)**: INSERT, UPDATE, DELETE
- **数据控制 (DCL)**: GRANT, REVOKE

## 2. 数据库和表操作

### 2.1 创建数据库

```sql
-- 创建数据库
CREATE DATABASE company;

-- 使用数据库
USE company;

-- 删除数据库
DROP DATABASE company;
```

### 2.2 创建表

```sql
CREATE TABLE employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE,
    email VARCHAR(100) UNIQUE
);

-- 查看表结构
DESCRIBE employees;

-- 删除表
DROP TABLE employees;
```

## 3. 数据类型

### 3.1 常用数据类型

```sql
-- 数值类型
INT, BIGINT, DECIMAL(10, 2), FLOAT, DOUBLE

-- 字符串类型
CHAR(10), VARCHAR(255), TEXT

-- 日期时间类型
DATE, TIME, DATETIME, TIMESTAMP

-- 布尔类型
BOOLEAN (TINYINT(1))
```

## 4. 插入数据

```sql
-- 插入单条记录
INSERT INTO employees (name, age, department, salary, hire_date, email)
VALUES ('张三', 28, '技术部', 8000.00, '2023-01-15', 'zhangsan@example.com');

-- 插入多条记录
INSERT INTO employees (name, age, department, salary, hire_date, email)
VALUES
    ('李四', 32, '销售部', 7500.00, '2022-06-20', 'lisi@example.com'),
    ('王五', 25, '技术部', 6500.00, '2023-03-10', 'wangwu@example.com'),
    ('赵六', 35, '人事部', 9000.00, '2021-09-05', 'zhaoliu@example.com');
```

## 5. 查询数据

### 5.1 基本查询

```sql
-- 查询所有列
SELECT * FROM employees;

-- 查询指定列
SELECT name, age, department FROM employees;

-- 去重查询
SELECT DISTINCT department FROM employees;

-- 限制结果数量
SELECT * FROM employees LIMIT 5;

-- 排序
SELECT * FROM employees ORDER BY salary DESC;
SELECT * FROM employees ORDER BY department, salary DESC;
```

### 5.2 条件查询

```sql
-- WHERE 子句
SELECT * FROM employees WHERE age > 30;
SELECT * FROM employees WHERE department = '技术部';
SELECT * FROM employees WHERE salary BETWEEN 7000 AND 9000;
SELECT * FROM employees WHERE department IN ('技术部', '销售部');
SELECT * FROM employees WHERE name LIKE '张%';
SELECT * FROM employees WHERE email IS NOT NULL;

-- 多条件查询
SELECT * FROM employees
WHERE department = '技术部' AND salary > 7000;

SELECT * FROM employees
WHERE age < 30 OR salary > 8000;
```

## 6. 更新数据

```sql
-- 更新单个字段
UPDATE employees
SET salary = 8500.00
WHERE id = 1;

-- 更新多个字段
UPDATE employees
SET age = 29, salary = 9000.00
WHERE name = '张三';

-- 更新所有记录（危险操作）
UPDATE employees
SET department = '技术部'
WHERE department IS NULL;
```

## 7. 删除数据

```sql
-- 删除指定记录
DELETE FROM employees WHERE id = 5;

-- 删除满足条件的记录
DELETE FROM employees WHERE age > 60;

-- 删除所有记录（保留表结构）
DELETE FROM employees;

-- 清空表（更快，但不可回滚）
TRUNCATE TABLE employees;
```

## 8. 聚合函数

```sql
-- 计数
SELECT COUNT(*) FROM employees;
SELECT COUNT(DISTINCT department) FROM employees;

-- 求和
SELECT SUM(salary) FROM employees;

-- 平均值
SELECT AVG(salary) FROM employees;

-- 最大值和最小值
SELECT MAX(salary), MIN(salary) FROM employees;

-- 分组统计
SELECT department, COUNT(*) as emp_count, AVG(salary) as avg_salary
FROM employees
GROUP BY department;

-- HAVING 子句（对分组结果筛选）
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 7000;
```

## 9. 表连接

### 9.1 创建相关表

```sql
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    location VARCHAR(100)
);

INSERT INTO departments VALUES
    (1, '技术部', '北京'),
    (2, '销售部', '上海'),
    (3, '人事部', '广州');

-- 修改employees表添加外键
ALTER TABLE employees
ADD COLUMN department_id INT,
ADD FOREIGN KEY (department_id) REFERENCES departments(id);
```

### 9.2 连接类型

```sql
-- INNER JOIN（内连接）
SELECT e.name, e.salary, d.name as department, d.location
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;

-- LEFT JOIN（左连接）
SELECT e.name, d.name as department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- RIGHT JOIN（右连接）
SELECT e.name, d.name as department
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;

-- FULL OUTER JOIN（全外连接，MySQL不直接支持）
SELECT e.name, d.name as department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
UNION
SELECT e.name, d.name as department
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;
```

## 10. 子查询

```sql
-- 单行子查询
SELECT * FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- 多行子查询
SELECT * FROM employees
WHERE department_id IN (
    SELECT id FROM departments WHERE location = '北京'
);

-- EXISTS 子查询
SELECT * FROM employees e
WHERE EXISTS (
    SELECT 1 FROM departments d
    WHERE d.id = e.department_id AND d.location = '上海'
);
```

## 11. 视图

```sql
-- 创建视图
CREATE VIEW employee_summary AS
SELECT
    e.name,
    e.age,
    d.name as department,
    e.salary
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- 使用视图
SELECT * FROM employee_summary WHERE age > 30;

-- 删除视图
DROP VIEW employee_summary;
```

## 12. 索引

```sql
-- 创建索引
CREATE INDEX idx_name ON employees(name);
CREATE INDEX idx_dept_salary ON employees(department_id, salary);

-- 唯一索引
CREATE UNIQUE INDEX idx_email ON employees(email);

-- 查看索引
SHOW INDEX FROM employees;

-- 删除索引
DROP INDEX idx_name ON employees;
```

## 13. 事务

```sql
-- 开始事务
START TRANSACTION;

-- 执行操作
UPDATE employees SET salary = salary + 1000 WHERE department_id = 1;
INSERT INTO employees (name, age, department_id, salary)
VALUES ('新员工', 25, 1, 6000.00);

-- 提交事务
COMMIT;

-- 或者回滚事务
ROLLBACK;
```

## 14. 常用函数

### 14.1 字符串函数

```sql
SELECT
    CONCAT('Hello', ' ', 'World'),           -- Hello World
    LENGTH('Hello'),                          -- 5
    UPPER('hello'),                           -- HELLO
    LOWER('HELLO'),                           -- hello
    SUBSTRING('Hello World', 1, 5),           -- Hello
    TRIM('  Hello  '),                        -- Hello
    REPLACE('Hello World', 'World', 'SQL');   -- Hello SQL
```

### 14.2 数值函数

```sql
SELECT
    ABS(-10),        -- 10
    CEIL(4.3),       -- 5
    FLOOR(4.7),      -- 4
    ROUND(4.567, 2), -- 4.57
    MOD(10, 3);      -- 1
```

### 14.3 日期函数

```sql
SELECT
    NOW(),                                    -- 当前日期时间
    CURDATE(),                                -- 当前日期
    CURTIME(),                                -- 当前时间
    DATE_FORMAT(NOW(), '%Y-%m-%d'),          -- 格式化日期
    DATEDIFF('2024-01-01', '2023-01-01'),    -- 日期差
    DATE_ADD(NOW(), INTERVAL 7 DAY);         -- 日期加减
```

## 15. 约束

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    age INT CHECK (age >= 18),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_email CHECK (email LIKE '%@%.%')
);
```

## 16. 最佳实践

### 16.1 查询优化

```sql
-- 使用索引列进行查询
SELECT * FROM employees WHERE id = 100;

-- 避免SELECT *，只选择需要的列
SELECT name, salary FROM employees;

-- 使用LIMIT限制结果集
SELECT * FROM employees ORDER BY salary DESC LIMIT 10;

-- 避免在WHERE子句中使用函数
-- 不好：SELECT * FROM employees WHERE YEAR(hire_date) = 2023;
-- 好：SELECT * FROM employees WHERE hire_date BETWEEN '2023-01-01' AND '2023-12-31';
```

### 16.2 安全性

```sql
-- 使用参数化查询防止SQL注入（在应用层实现）
-- Python示例：cursor.execute("SELECT * FROM employees WHERE id = %s", (user_id,))

-- 最小权限原则
GRANT SELECT ON company.employees TO 'readonly_user'@'localhost';
```

## 17. 实际应用示例

```sql
-- 查询每个部门工资最高的员工
SELECT e.name, e.department_id, e.salary
FROM employees e
INNER JOIN (
    SELECT department_id, MAX(salary) as max_salary
    FROM employees
    GROUP BY department_id
) d ON e.department_id = d.department_id AND e.salary = d.max_salary;

-- 查询入职超过2年的员工
SELECT name, hire_date, DATEDIFF(CURDATE(), hire_date) as days_employed
FROM employees
WHERE hire_date < DATE_SUB(CURDATE(), INTERVAL 2 YEAR);

-- 统计每个部门的平均工资和人数
SELECT
    d.name as department,
    COUNT(e.id) as emp_count,
    ROUND(AVG(e.salary), 2) as avg_salary
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
ORDER BY avg_salary DESC;
```

## 总结

SQL是数据库操作的核心技能：
- **基础操作**: CREATE, INSERT, SELECT, UPDATE, DELETE
- **查询技巧**: WHERE, JOIN, GROUP BY, HAVING
- **高级功能**: 子查询, 视图, 索引, 事务
- **最佳实践**: 查询优化, 安全性, 规范命名

掌握SQL可以高效地管理和查询数据，是后端开发的必备技能。
