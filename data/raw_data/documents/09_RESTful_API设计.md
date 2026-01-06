# RESTful API 设计指南

## 1. RESTful API 简介

REST (Representational State Transfer) 是一种软件架构风格，用于设计网络应用程序的API。

### 1.1 REST 核心原则

- **无状态 (Stateless)**: 每个请求都包含所有必要信息
- **客户端-服务器分离**: 前后端独立开发和部署
- **可缓存**: 响应可被标记为可缓存或不可缓存
- **统一接口**: 使用标准的HTTP方法
- **分层系统**: 可以有多层中间件

## 2. HTTP 方法

### 2.1 常用HTTP方法

| 方法 | 用途 | 幂等性 | 安全性 |
|------|------|--------|--------|
| GET | 获取资源 | 是 | 是 |
| POST | 创建资源 | 否 | 否 |
| PUT | 更新资源（完整） | 是 | 否 |
| PATCH | 更新资源（部分） | 否 | 否 |
| DELETE | 删除资源 | 是 | 否 |

### 2.2 使用示例

```python
# 获取所有用户
GET /api/users

# 获取单个用户
GET /api/users/123

# 创建用户
POST /api/users
{
    "name": "张三",
    "email": "zhangsan@example.com"
}

# 更新用户（完整）
PUT /api/users/123
{
    "name": "张三",
    "email": "new@example.com",
    "age": 25
}

# 更新用户（部分）
PATCH /api/users/123
{
    "email": "new@example.com"
}

# 删除用户
DELETE /api/users/123
```

## 3. URL 设计

### 3.1 命名规范

```bash
# 使用复数名词
GET /api/users          # 好
GET /api/user           # 不好

# 使用小写字母和连字符
GET /api/user-profiles  # 好
GET /api/userProfiles   # 不好
GET /api/user_profiles  # 不好

# 资源层级
GET /api/users/123/posts          # 获取用户123的所有文章
GET /api/users/123/posts/456      # 获取用户123的文章456
```

### 3.2 过滤、排序、分页

```bash
# 过滤
GET /api/users?age=25
GET /api/users?status=active&age=25

# 排序
GET /api/users?sort=created_at:desc
GET /api/users?sort=-created_at  # 降序

# 分页
GET /api/users?page=2&per_page=20
GET /api/users?offset=20&limit=20

# 字段选择
GET /api/users?fields=id,name,email

# 搜索
GET /api/users?q=张三
```

## 4. 状态码

### 4.1 常用状态码

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 OK | 成功 | GET, PUT, PATCH 成功 |
| 201 Created | 已创建 | POST 创建成功 |
| 204 No Content | 无内容 | DELETE 成功 |
| 400 Bad Request | 请求错误 | 参数验证失败 |
| 401 Unauthorized | 未认证 | 需要登录 |
| 403 Forbidden | 禁止访问 | 权限不足 |
| 404 Not Found | 未找到 | 资源不存在 |
| 409 Conflict | 冲突 | 资源冲突 |
| 500 Internal Server Error | 服务器错误 | 服务器异常 |

## 5. 请求和响应格式

### 5.1 JSON 格式

```json
// 请求
POST /api/users
Content-Type: application/json

{
    "name": "张三",
    "email": "zhangsan@example.com",
    "age": 25
}

// 成功响应
HTTP/1.1 201 Created
Content-Type: application/json

{
    "id": 123,
    "name": "张三",
    "email": "zhangsan@example.com",
    "age": 25,
    "created_at": "2024-01-01T10:00:00Z"
}

// 错误响应
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "邮箱格式不正确",
        "details": [
            {
                "field": "email",
                "message": "必须是有效的邮箱地址"
            }
        ]
    }
}
```

### 5.2 列表响应格式

```json
GET /api/users?page=1&per_page=20

{
    "data": [
        {
            "id": 1,
            "name": "张三",
            "email": "zhangsan@example.com"
        },
        {
            "id": 2,
            "name": "李四",
            "email": "lisi@example.com"
        }
    ],
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 100,
        "total_pages": 5
    },
    "links": {
        "self": "/api/users?page=1&per_page=20",
        "next": "/api/users?page=2&per_page=20",
        "last": "/api/users?page=5&per_page=20"
    }
}
```

## 6. 认证和授权

### 6.1 认证方式

```bash
# Basic Auth
Authorization: Basic base64(username:password)

# Bearer Token (JWT)
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API Key
X-API-Key: your-api-key-here
```

### 6.2 Python 实现示例 (Flask)

```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': '未提供认证信息'}), 401

        if not token.startswith('Bearer '):
            return jsonify({'error': '认证格式错误'}), 401

        # 验证token（简化示例）
        actual_token = token.split(' ')[1]
        if actual_token != 'valid-token':
            return jsonify({'error': '认证失败'}), 401

        return f(*args, **kwargs)

    return decorated_function

@app.route('/api/users', methods=['GET'])
@require_auth
def get_users():
    return jsonify({'data': []})
```

## 7. 版本控制

### 7.1 版本控制策略

```bash
# URL路径版本
GET /api/v1/users
GET /api/v2/users

# 请求头版本
GET /api/users
Accept: application/vnd.myapp.v1+json

# 查询参数版本
GET /api/users?version=1
```

## 8. 错误处理

### 8.1 统一错误格式

```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "人类可读的错误消息",
        "details": [
            {
                "field": "email",
                "message": "邮箱格式不正确"
            }
        ],
        "timestamp": "2024-01-01T10:00:00Z",
        "request_id": "abc-123-def"
    }
}
```

### 8.2 Python 实现

```python
class APIError(Exception):
    def __init__(self, message, code, status_code=400, details=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []

@app.errorhandler(APIError)
def handle_api_error(error):
    response = {
        'error': {
            'code': error.code,
            'message': error.message,
            'details': error.details,
            'timestamp': datetime.now().isoformat()
        }
    }
    return jsonify(response), error.status_code

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data.get('email'):
        raise APIError(
            message='邮箱不能为空',
            code='VALIDATION_ERROR',
            details=[{'field': 'email', 'message': '必填字段'}]
        )

    # 创建用户逻辑...
    return jsonify({'id': 123}), 201
```

## 9. 速率限制

### 9.1 响应头

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

### 9.2 Python 实现 (Flask-Limiter)

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/users', methods=['GET'])
@limiter.limit("10 per minute")
def get_users():
    return jsonify({'data': []})
```

## 10. CORS 跨域

```python
from flask_cors import CORS

# 允许所有域名
CORS(app)

# 配置特定域名
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://example.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## 11. 文档

### 11.1 OpenAPI (Swagger) 示例

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /api/users:
    get:
      summary: 获取用户列表
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
```

## 12. 最佳实践

### 12.1 设计原则

1. **保持一致性**: 命名、格式、错误处理统一
2. **使用名词而非动词**: `/users` 而非 `/getUsers`
3. **利用HTTP方法**: 不要在URL中包含动作
4. **版本控制**: 从v1开始，保持向后兼容
5. **提供详细文档**: 使用OpenAPI/Swagger
6. **安全优先**: HTTPS、认证、输入验证
7. **性能优化**: 缓存、分页、字段选择
8. **监控和日志**: 记录请求、错误、性能

### 12.2 完整示例 (FastAPI)

```python
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None

class User(UserCreate):
    id: int

# 模拟数据库
users_db = []

@app.get("/api/users", response_model=List[User])
def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """获取用户列表"""
    start = (page - 1) * per_page
    end = start + per_page
    return users_db[start:end]

@app.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: int):
    """获取单个用户"""
    for user in users_db:
        if user['id'] == user_id:
            return user
    raise HTTPException(status_code=404, detail="用户不存在")

@app.post("/api/users", response_model=User, status_code=201)
def create_user(user: UserCreate):
    """创建用户"""
    new_user = {
        "id": len(users_db) + 1,
        **user.dict()
    }
    users_db.append(new_user)
    return new_user

@app.put("/api/users/{user_id}", response_model=User)
def update_user(user_id: int, user: UserCreate):
    """更新用户"""
    for i, u in enumerate(users_db):
        if u['id'] == user_id:
            users_db[i] = {
                "id": user_id,
                **user.dict()
            }
            return users_db[i]
    raise HTTPException(status_code=404, detail="用户不存在")

@app.delete("/api/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    """删除用户"""
    for i, user in enumerate(users_db):
        if user['id'] == user_id:
            del users_db[i]
            return
    raise HTTPException(status_code=404, detail="用户不存在")
```

## 总结

设计良好的RESTful API需要：
- **遵循REST原则**: 无状态、统一接口、可缓存
- **合理使用HTTP方法**: GET, POST, PUT, PATCH, DELETE
- **规范的URL设计**: 复数名词、小写字母、层级清晰
- **标准状态码**: 200, 201, 400, 404, 500
- **统一的数据格式**: JSON、一致的错误响应
- **安全性**: 认证授权、HTTPS、输入验证
- **完善的文档**: OpenAPI/Swagger

掌握这些原则可以设计出易用、可维护的API。
