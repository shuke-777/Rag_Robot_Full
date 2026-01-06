# Python 数据结构详解

## 1. 列表 (List)

列表是 Python 中最常用的数据结构之一，它是一个有序的可变序列。

### 1.1 列表的特点

- **有序**: 元素按照插入顺序排列
- **可变**: 可以修改、添加、删除元素
- **允许重复**: 可以包含重复的元素
- **异构**: 可以包含不同类型的元素

### 1.2 列表的创建

```python
# 空列表
empty_list = []
empty_list2 = list()

# 包含元素的列表
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True, [1, 2]]

# 使用 range 创建
numbers = list(range(10))  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 列表推导式
squares = [x**2 for x in range(10)]
```

### 1.3 列表的常用操作

```python
fruits = ["apple", "banana", "cherry"]

# 添加元素
fruits.append("orange")           # 末尾添加
fruits.insert(1, "grape")         # 指定位置插入
fruits.extend(["mango", "kiwi"])  # 添加多个元素

# 删除元素
fruits.remove("banana")           # 删除指定值
popped = fruits.pop()             # 删除并返回最后一个
popped = fruits.pop(0)            # 删除并返回指定索引
del fruits[0]                     # 删除指定索引
fruits.clear()                    # 清空列表

# 查找
index = fruits.index("apple")     # 查找元素索引
count = fruits.count("apple")     # 统计出现次数
exists = "apple" in fruits        # 检查是否存在

# 排序
fruits.sort()                     # 原地排序
fruits.sort(reverse=True)         # 降序排序
sorted_fruits = sorted(fruits)    # 返回新的排序列表

# 反转
fruits.reverse()                  # 原地反转
reversed_fruits = fruits[::-1]    # 返回新的反转列表

# 复制
copy = fruits.copy()
copy2 = fruits[:]
```

### 1.4 列表切片

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# 基本切片
print(numbers[2:5])     # [2, 3, 4]
print(numbers[:5])      # [0, 1, 2, 3, 4]
print(numbers[5:])      # [5, 6, 7, 8, 9]
print(numbers[-3:])     # [7, 8, 9]

# 步长切片
print(numbers[::2])     # [0, 2, 4, 6, 8]
print(numbers[1::2])    # [1, 3, 5, 7, 9]
print(numbers[::-1])    # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
```

## 2. 元组 (Tuple)

元组与列表类似，但是不可变的。

### 2.1 元组的特点

- **有序**: 元素按照定义顺序排列
- **不可变**: 创建后不能修改
- **允许重复**: 可以包含重复元素
- **异构**: 可以包含不同类型元素

### 2.2 元组的创建

```python
# 空元组
empty_tuple = ()
empty_tuple2 = tuple()

# 单元素元组（注意逗号）
single = (1,)
single2 = 1,

# 多元素元组
numbers = (1, 2, 3, 4, 5)
mixed = (1, "hello", 3.14, True)

# 元组解包
a, b, c = (1, 2, 3)
```

### 2.3 元组的操作

```python
tuple1 = (1, 2, 3)
tuple2 = (4, 5, 6)

# 连接
combined = tuple1 + tuple2  # (1, 2, 3, 4, 5, 6)

# 重复
repeated = tuple1 * 3       # (1, 2, 3, 1, 2, 3, 1, 2, 3)

# 访问
first = tuple1[0]           # 1
last = tuple1[-1]           # 3

# 切片
slice_result = tuple1[1:]   # (2, 3)

# 查找
index = tuple1.index(2)     # 1
count = tuple1.count(1)     # 1

# 长度
length = len(tuple1)        # 3
```

### 2.4 命名元组

```python
from collections import namedtuple

# 定义命名元组
Point = namedtuple('Point', ['x', 'y'])
Person = namedtuple('Person', 'name age city')

# 创建实例
p = Point(10, 20)
person = Person("Alice", 25, "Beijing")

# 访问
print(p.x, p.y)                    # 10 20
print(person.name, person.age)     # Alice 25

# 也可以通过索引访问
print(p[0], p[1])                  # 10 20
```

## 3. 集合 (Set)

集合是无序的不重复元素序列。

### 3.1 集合的特点

- **无序**: 元素没有固定顺序
- **唯一**: 自动去除重复元素
- **可变**: 可以添加删除元素
- **成员测试快**: O(1) 时间复杂度

### 3.2 集合的创建

```python
# 空集合
empty_set = set()

# 从列表创建
numbers = {1, 2, 3, 4, 5}
unique = set([1, 2, 2, 3, 3, 4])  # {1, 2, 3, 4}

# 集合推导式
squares = {x**2 for x in range(10)}
```

### 3.3 集合的操作

```python
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

# 添加元素
set1.add(5)
set1.update([6, 7, 8])

# 删除元素
set1.remove(5)        # 如果不存在会报错
set1.discard(5)       # 如果不存在不会报错
popped = set1.pop()   # 随机删除并返回

# 集合运算
union = set1 | set2              # 并集: {1, 2, 3, 4, 5, 6}
intersection = set1 & set2       # 交集: {3, 4}
difference = set1 - set2         # 差集: {1, 2}
sym_diff = set1 ^ set2           # 对称差集: {1, 2, 5, 6}

# 使用方法
union = set1.union(set2)
intersection = set1.intersection(set2)
difference = set1.difference(set2)
sym_diff = set1.symmetric_difference(set2)

# 子集和超集
is_subset = {1, 2}.issubset(set1)
is_superset = set1.issuperset({1, 2})
is_disjoint = set1.isdisjoint({7, 8})
```

## 4. 字典 (Dictionary)

字典是键值对的无序集合。

### 4.1 字典的特点

- **键值对**: 每个元素由键和值组成
- **无序**: Python 3.7+ 保持插入顺序
- **键唯一**: 键不能重复，值可以重复
- **可变**: 可以修改、添加、删除键值对

### 4.2 字典的创建

```python
# 空字典
empty_dict = {}
empty_dict2 = dict()

# 直接创建
person = {
    "name": "Alice",
    "age": 25,
    "city": "Beijing"
}

# 使用 dict() 构造
person2 = dict(name="Bob", age=30, city="Shanghai")

# 从键值对列表创建
items = [("name", "Charlie"), ("age", 35)]
person3 = dict(items)

# 字典推导式
squares = {x: x**2 for x in range(5)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

### 4.3 字典的操作

```python
person = {"name": "Alice", "age": 25}

# 访问
name = person["name"]              # 如果键不存在会报错
age = person.get("age")            # 如果键不存在返回 None
email = person.get("email", "N/A") # 提供默认值

# 添加/修改
person["email"] = "alice@example.com"
person.update({"age": 26, "city": "Beijing"})

# 删除
del person["email"]
age = person.pop("age")            # 删除并返回值
item = person.popitem()            # 删除并返回最后一个键值对
person.clear()                     # 清空字典

# 检查键是否存在
exists = "name" in person
not_exists = "email" not in person

# 获取所有键、值、键值对
keys = person.keys()
values = person.values()
items = person.items()

# 遍历
for key in person:
    print(key, person[key])

for key, value in person.items():
    print(key, value)

# 复制
copy = person.copy()

# setdefault - 如果键不存在则设置默认值
email = person.setdefault("email", "default@example.com")
```

### 4.4 defaultdict

```python
from collections import defaultdict

# 默认值为 0
counter = defaultdict(int)
words = ["apple", "banana", "apple", "cherry", "banana"]
for word in words:
    counter[word] += 1
# defaultdict(<class 'int'>, {'apple': 2, 'banana': 2, 'cherry': 1})

# 默认值为列表
groups = defaultdict(list)
data = [("fruit", "apple"), ("vegetable", "carrot"), ("fruit", "banana")]
for category, item in data:
    groups[category].append(item)
# defaultdict(<class 'list'>, {'fruit': ['apple', 'banana'], 'vegetable': ['carrot']})
```

### 4.5 OrderedDict

```python
from collections import OrderedDict

# 保持插入顺序（Python 3.7+ 普通字典也保持顺序）
ordered = OrderedDict()
ordered["a"] = 1
ordered["b"] = 2
ordered["c"] = 3

# 移动到末尾
ordered.move_to_end("a")
# OrderedDict([('b', 2), ('c', 3), ('a', 1)])

# 移动到开头
ordered.move_to_end("c", last=False)
# OrderedDict([('c', 3), ('b', 2), ('a', 1)])
```

## 5. 数据结构选择指南

| 需求 | 推荐数据结构 | 原因 |
|------|-------------|------|
| 有序集合，需要频繁修改 | List | 支持索引访问和修改 |
| 有序集合，不需要修改 | Tuple | 不可变，更安全高效 |
| 需要去重、集合运算 | Set | 自动去重，集合运算快 |
| 键值对映射 | Dictionary | O(1) 查找速度 |
| 需要快速查找元素是否存在 | Set | O(1) 成员测试 |
| 需要保持元素顺序且去重 | OrderedDict | 保持顺序的字典 |
| 需要默认值的字典 | defaultdict | 避免KeyError |

## 6. 性能对比

### 时间复杂度

| 操作 | List | Tuple | Set | Dictionary |
|------|------|-------|-----|------------|
| 索引访问 | O(1) | O(1) | N/A | O(1) |
| 查找元素 | O(n) | O(n) | O(1) | O(1) |
| 添加元素 | O(1)* | N/A | O(1) | O(1) |
| 删除元素 | O(n) | N/A | O(1) | O(1) |
| 遍历 | O(n) | O(n) | O(n) | O(n) |

*注: List 的 append 是 O(1)，但 insert 是 O(n)

## 总结

Python 提供了丰富的内置数据结构：
- **List**: 有序可变序列，适合需要频繁修改的场景
- **Tuple**: 有序不可变序列，适合固定数据
- **Set**: 无序唯一集合，适合去重和集合运算
- **Dictionary**: 键值对映射，适合快速查找

选择合适的数据结构可以大大提高程序效率和代码可读性。
