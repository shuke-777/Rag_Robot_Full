# Web 开发基础知识

## 1. Web 开发概述

Web开发是指创建网站和Web应用程序的过程，包括前端（客户端）和后端（服务器端）开发。

### 1.1 Web技术栈

**前端三剑客**:
- HTML (结构)
- CSS (样式)
- JavaScript (行为)

**后端常用技术**:
- Python: Django, Flask, FastAPI
- JavaScript: Node.js, Express
- Java: Spring Boot
- PHP: Laravel

## 2. HTML 基础

### 2.1 HTML 结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网页标题</title>
</head>
<body>
    <h1>这是一级标题</h1>
    <p>这是一个段落</p>
</body>
</html>
```

### 2.2 常用HTML标签

```html
<!-- 标题 -->
<h1>一级标题</h1>
<h2>二级标题</h2>

<!-- 段落和文本 -->
<p>这是一个段落</p>
<strong>粗体文本</strong>
<em>斜体文本</em>
<br>  <!-- 换行 -->

<!-- 链接 -->
<a href="https://example.com">链接文本</a>
<a href="https://example.com" target="_blank">新窗口打开</a>

<!-- 图片 -->
<img src="image.jpg" alt="图片描述">

<!-- 列表 -->
<ul>
    <li>无序列表项1</li>
    <li>无序列表项2</li>
</ul>

<ol>
    <li>有序列表项1</li>
    <li>有序列表项2</li>
</ol>

<!-- 表格 -->
<table>
    <thead>
        <tr>
            <th>姓名</th>
            <th>年龄</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>张三</td>
            <td>25</td>
        </tr>
    </tbody>
</table>

<!-- 表单 -->
<form action="/submit" method="POST">
    <input type="text" name="username" placeholder="用户名">
    <input type="password" name="password" placeholder="密码">
    <input type="email" name="email" placeholder="邮箱">
    <button type="submit">提交</button>
</form>

<!-- 容器 -->
<div>块级容器</div>
<span>行内容器</span>
```

### 2.3 语义化标签

```html
<header>页头</header>
<nav>导航</nav>
<main>
    <article>文章</article>
    <section>章节</section>
    <aside>侧边栏</aside>
</main>
<footer>页脚</footer>
```

## 3. CSS 基础

### 3.1 CSS 选择器

```css
/* 元素选择器 */
p {
    color: blue;
}

/* 类选择器 */
.my-class {
    color: red;
}

/* ID选择器 */
#my-id {
    color: green;
}

/* 后代选择器 */
div p {
    color: orange;
}

/* 子元素选择器 */
div > p {
    color: purple;
}

/* 伪类 */
a:hover {
    color: red;
}

input:focus {
    border-color: blue;
}

/* 伪元素 */
p::first-line {
    font-weight: bold;
}

p::before {
    content: ">> ";
}
```

### 3.2 盒模型

```css
.box {
    /* 内容宽高 */
    width: 200px;
    height: 100px;

    /* 内边距 */
    padding: 10px;
    padding-top: 10px;
    padding-right: 15px;
    padding-bottom: 10px;
    padding-left: 15px;

    /* 边框 */
    border: 1px solid black;
    border-radius: 5px;

    /* 外边距 */
    margin: 20px;
    margin: 10px 20px;  /* 上下 左右 */
    margin: 10px 20px 30px 40px;  /* 上 右 下 左 */
}

/* 盒模型类型 */
.content-box {
    box-sizing: content-box;  /* 默认，宽高不包含padding和border */
}

.border-box {
    box-sizing: border-box;   /* 宽高包含padding和border */
}
```

### 3.3 布局

```css
/* Flexbox 布局 */
.flex-container {
    display: flex;
    justify-content: center;     /* 主轴对齐 */
    align-items: center;         /* 交叉轴对齐 */
    flex-direction: row;         /* 主轴方向 */
    flex-wrap: wrap;             /* 换行 */
}

.flex-item {
    flex: 1;                     /* 伸缩比例 */
}

/* Grid 布局 */
.grid-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);  /* 3列等宽 */
    grid-gap: 10px;
}

/* 定位 */
.relative {
    position: relative;
    top: 10px;
    left: 20px;
}

.absolute {
    position: absolute;
    top: 0;
    right: 0;
}

.fixed {
    position: fixed;
    bottom: 0;
    right: 0;
}
```

### 3.4 响应式设计

```css
/* 媒体查询 */
/* 默认样式（移动优先） */
.container {
    width: 100%;
    padding: 10px;
}

/* 平板 */
@media (min-width: 768px) {
    .container {
        width: 750px;
        margin: 0 auto;
    }
}

/* 桌面 */
@media (min-width: 1024px) {
    .container {
        width: 970px;
    }
}

/* 大屏幕 */
@media (min-width: 1440px) {
    .container {
        width: 1200px;
    }
}
```

## 4. JavaScript 基础

### 4.1 变量和数据类型

```javascript
// 变量声明
let name = "张三";
const age = 25;
var city = "北京";  // 不推荐使用

// 数据类型
let number = 42;
let string = "Hello";
let boolean = true;
let array = [1, 2, 3];
let object = { name: "张三", age: 25 };
let nullValue = null;
let undefinedValue = undefined;
```

### 4.2 函数

```javascript
// 函数声明
function greet(name) {
    return `Hello, ${name}!`;
}

// 箭头函数
const greet = (name) => `Hello, ${name}!`;

// 回调函数
function fetchData(callback) {
    setTimeout(() => {
        callback("数据");
    }, 1000);
}

fetchData((data) => {
    console.log(data);
});
```

### 4.3 DOM 操作

```javascript
// 获取元素
const element = document.getElementById('myId');
const elements = document.getElementsByClassName('myClass');
const element = document.querySelector('.myClass');
const elements = document.querySelectorAll('.myClass');

// 修改内容
element.textContent = "新文本";
element.innerHTML = "<strong>HTML内容</strong>";

// 修改样式
element.style.color = "red";
element.style.fontSize = "20px";

// 添加/删除类
element.classList.add('newClass');
element.classList.remove('oldClass');
element.classList.toggle('active');

// 事件监听
element.addEventListener('click', (event) => {
    console.log('点击了元素');
});

// 创建和插入元素
const newDiv = document.createElement('div');
newDiv.textContent = "新元素";
document.body.appendChild(newDiv);
```

### 4.4 事件处理

```javascript
// 点击事件
button.addEventListener('click', function(event) {
    event.preventDefault();  // 阻止默认行为
    console.log('按钮被点击');
});

// 表单提交
form.addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(form);
    console.log(formData.get('username'));
});

// 键盘事件
input.addEventListener('keyup', function(event) {
    if (event.key === 'Enter') {
        console.log('按下回车键');
    }
});

// 鼠标事件
element.addEventListener('mouseover', function() {
    this.style.backgroundColor = 'yellow';
});

element.addEventListener('mouseout', function() {
    this.style.backgroundColor = '';
});
```

### 4.5 异步操作

```javascript
// Promise
function fetchData() {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve("数据");
        }, 1000);
    });
}

fetchData()
    .then(data => console.log(data))
    .catch(error => console.error(error));

// async/await
async function getData() {
    try {
        const response = await fetch('https://api.example.com/data');
        const data = await response.json();
        console.log(data);
    } catch (error) {
        console.error(error);
    }
}

// Fetch API
fetch('https://api.example.com/users')
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));

// POST 请求
fetch('https://api.example.com/users', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        name: '张三',
        age: 25
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 5. HTTP 基础

### 5.1 HTTP 方法

- **GET**: 获取资源
- **POST**: 创建资源
- **PUT**: 更新资源（完整）
- **PATCH**: 更新资源（部分）
- **DELETE**: 删除资源

### 5.2 HTTP 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | OK - 成功 |
| 201 | Created - 已创建 |
| 204 | No Content - 无内容 |
| 400 | Bad Request - 请求错误 |
| 401 | Unauthorized - 未认证 |
| 403 | Forbidden - 禁止访问 |
| 404 | Not Found - 未找到 |
| 500 | Internal Server Error - 服务器错误 |

## 6. 前端框架简介

### 6.1 React 示例

```javascript
import React, { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);

    return (
        <div>
            <p>Count: {count}</p>
            <button onClick={() => setCount(count + 1)}>
                增加
            </button>
        </div>
    );
}
```

### 6.2 Vue 示例

```vue
<template>
    <div>
        <p>Count: {{ count }}</p>
        <button @click="increment">增加</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            count: 0
        };
    },
    methods: {
        increment() {
            this.count++;
        }
    }
};
</script>
```

## 7. 后端开发基础

### 7.1 Python Flask 示例

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify({'users': []})

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    return jsonify({'user': data}), 201

if __name__ == '__main__':
    app.run(debug=True)
```

### 7.2 数据库操作

```python
import sqlite3

# 连接数据库
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# 创建表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE
    )
''')

# 插入数据
cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)',
               ('张三', 'zhangsan@example.com'))

# 查询数据
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()

# 提交和关闭
conn.commit()
conn.close()
```

## 8. Web 安全基础

### 8.1 常见安全问题

**XSS (跨站脚本攻击)**:
```javascript
// 不安全
element.innerHTML = userInput;

// 安全
element.textContent = userInput;
```

**CSRF (跨站请求伪造)**:
```python
# 使用 CSRF Token
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```

**SQL注入**:
```python
# 不安全
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# 安全（使用参数化查询）
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

## 9. 开发工具

### 9.1 浏览器开发者工具

- **Elements**: 检查HTML和CSS
- **Console**: JavaScript控制台
- **Network**: 网络请求
- **Application**: 存储和缓存

### 9.2 版本控制

```bash
# Git 基础命令
git init
git add .
git commit -m "提交信息"
git push origin main
```

## 10. 最佳实践

1. **代码规范**: 遵循ESLint、Prettier等代码规范
2. **语义化HTML**: 使用合适的HTML标签
3. **响应式设计**: 移动优先，使用媒体查询
4. **性能优化**: 压缩资源、懒加载、CDN
5. **安全性**: 输入验证、HTTPS、CSRF保护
6. **可访问性**: 使用语义化标签、ARIA属性
7. **SEO优化**: 合理的title、meta标签、语义化

## 总结

Web开发需要掌握：
- **前端三剑客**: HTML, CSS, JavaScript
- **前端框架**: React, Vue, Angular
- **后端技术**: Python, Node.js, Java
- **数据库**: SQL, NoSQL
- **安全性**: XSS, CSRF, SQL注入防护
- **工具**: Git, 浏览器开发者工具

持续学习和实践是成为优秀Web开发者的关键！
