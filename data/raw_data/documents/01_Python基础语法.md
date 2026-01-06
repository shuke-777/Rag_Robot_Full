# Python 基础语法教程

## 1. Python 简介

Python 是一种高级、解释型、交互式和面向对象的脚本语言。Python 的设计哲学强调代码的可读性和简洁的语法（尤其是使用空格缩进来表示代码块）。

### Python 的特点

- **易于学习**: Python 有相对较少的关键字，结构简单，语法清晰
- **易于维护**: Python 的成功在于它的源代码相当容易维护
- **可移植**: Python 可以运行在多种硬件平台上，并且在所有平台上具有相同的接口
- **丰富的库**: Python 标准库非常庞大，可以帮助处理各种工作

## 2. 变量和数据类型

### 变量定义

Python 中的变量不需要声明类型，变量的赋值操作既定义了变量又确定了类型。

```python
# 整数
age = 25
# 浮点数
height = 1.75
# 字符串
name = "Alice"
# 布尔值
is_student = True
```

### 基本数据类型

Python 有六个标准的数据类型：

1. **数字 (Number)**
   - int (整型)
   - float (浮点型)
   - complex (复数)

2. **字符串 (String)**
3. **列表 (List)**
4. **元组 (Tuple)**
5. **集合 (Set)**
6. **字典 (Dictionary)**

## 3. 字符串操作

### 字符串定义

```python
str1 = 'Hello'
str2 = "World"
str3 = """多行
字符串"""
```

### 常用字符串方法

```python
text = "Hello, World!"

# 转换为大写
print(text.upper())  # HELLO, WORLD!

# 转换为小写
print(text.lower())  # hello, world!

# 替换
print(text.replace("World", "Python"))  # Hello, Python!

# 分割
words = text.split(",")  # ['Hello', ' World!']

# 去除空格
text2 = "  trim me  "
print(text2.strip())  # "trim me"
```

### 字符串格式化

```python
name = "Alice"
age = 25

# 使用 f-string (Python 3.6+)
message = f"My name is {name} and I'm {age} years old"

# 使用 format()
message = "My name is {} and I'm {} years old".format(name, age)

# 使用 % 格式化
message = "My name is %s and I'm %d years old" % (name, age)
```

## 4. 控制流语句

### if 语句

```python
age = 18

if age < 18:
    print("未成年")
elif age == 18:
    print("刚好成年")
else:
    print("已成年")
```

### for 循环

```python
# 遍历列表
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# 使用 range()
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# 使用 enumerate() 获取索引
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```

### while 循环

```python
count = 0
while count < 5:
    print(count)
    count += 1

# 使用 break 退出循环
while True:
    user_input = input("Enter 'q' to quit: ")
    if user_input == 'q':
        break
```

## 5. 函数定义

### 基本函数

```python
def greet(name):
    """问候函数"""
    return f"Hello, {name}!"

result = greet("Alice")
print(result)  # Hello, Alice!
```

### 默认参数

```python
def power(base, exponent=2):
    """计算幂次方，默认为平方"""
    return base ** exponent

print(power(3))      # 9
print(power(3, 3))   # 27
```

### 可变参数

```python
def sum_all(*args):
    """接受任意数量的参数并求和"""
    return sum(args)

print(sum_all(1, 2, 3, 4, 5))  # 15

def print_info(**kwargs):
    """接受任意数量的关键字参数"""
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25, city="Beijing")
```

## 6. 列表操作

### 列表创建和访问

```python
# 创建列表
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True]

# 访问元素
print(numbers[0])   # 1
print(numbers[-1])  # 5 (最后一个元素)

# 切片
print(numbers[1:4])   # [2, 3, 4]
print(numbers[:3])    # [1, 2, 3]
print(numbers[2:])    # [3, 4, 5]
```

### 列表方法

```python
fruits = ["apple", "banana"]

# 添加元素
fruits.append("cherry")          # ['apple', 'banana', 'cherry']
fruits.insert(1, "orange")       # ['apple', 'orange', 'banana', 'cherry']

# 删除元素
fruits.remove("banana")          # 删除指定值
popped = fruits.pop()            # 删除并返回最后一个元素
del fruits[0]                    # 删除指定索引

# 其他操作
fruits.sort()                    # 排序
fruits.reverse()                 # 反转
length = len(fruits)             # 获取长度
```

### 列表推导式

```python
# 创建平方数列表
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 带条件的列表推导式
even_squares = [x**2 for x in range(10) if x % 2 == 0]
# [0, 4, 16, 36, 64]
```

## 7. 字典操作

### 字典创建和访问

```python
# 创建字典
person = {
    "name": "Alice",
    "age": 25,
    "city": "Beijing"
}

# 访问值
print(person["name"])           # Alice
print(person.get("age"))        # 25
print(person.get("email", "N/A"))  # N/A (提供默认值)
```

### 字典方法

```python
# 添加/修改
person["email"] = "alice@example.com"
person.update({"age": 26, "country": "China"})

# 删除
del person["city"]
removed_value = person.pop("email")

# 遍历
for key in person:
    print(f"{key}: {person[key]}")

for key, value in person.items():
    print(f"{key}: {value}")

# 获取所有键、值
keys = person.keys()
values = person.values()
```

## 8. 异常处理

### try-except 语句

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零！")
except Exception as e:
    print(f"发生错误: {e}")
else:
    print("没有发生异常")
finally:
    print("无论如何都会执行")
```

### 抛出异常

```python
def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

try:
    result = divide(10, 0)
except ValueError as e:
    print(e)
```

## 9. 文件操作

### 读取文件

```python
# 使用 with 语句（推荐）
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)

# 逐行读取
with open("file.txt", "r") as f:
    for line in f:
        print(line.strip())
```

### 写入文件

```python
# 写入模式（覆盖）
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, World!\n")
    f.write("Python 文件操作")

# 追加模式
with open("output.txt", "a") as f:
    f.write("\n新的一行")
```

## 10. 模块导入

### 导入方式

```python
# 导入整个模块
import math
print(math.sqrt(16))

# 导入特定函数
from math import sqrt, pow
print(sqrt(16))

# 导入并重命名
import numpy as np
array = np.array([1, 2, 3])

# 导入所有（不推荐）
from math import *
```

## 总结

本教程涵盖了 Python 的基础语法，包括：
- 变量和数据类型
- 字符串操作
- 控制流（if、for、while）
- 函数定义
- 列表和字典
- 异常处理
- 文件操作
- 模块导入

掌握这些基础知识后，你就可以开始编写简单的 Python 程序了。继续学习面向对象编程、装饰器、生成器等高级特性，可以让你的 Python 技能更上一层楼。
