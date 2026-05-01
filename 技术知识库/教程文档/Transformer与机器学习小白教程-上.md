# Transformer与机器学习小白教程（上）

![Transformer与机器学习](https://www.coze.cn/s/My3gR29PypA/)

本教程为Transformer与机器学习系列教程的上半部分，包含机器学习基础、深度学习基础、NLP基础和Transformer核心架构四个篇章。通过通俗易懂的语言、生活化的比喻和可运行的PyTorch代码，帮助零基础读者建立完整的知识体系。

---

## 第一篇：机器学习基础

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 1.1 什么是机器学习？

#### 一句话人话
机器学习就是让计算机像人类一样从例子中学习规律，而不是靠死记硬背规则。

#### 生活比喻
想象你教小孩认识什么是"猫"：
- 你不会说"猫是一种四条腿、有胡须、体长约40-50厘米的恒温脊椎动物"
- 你会给他看很多猫的图片，说"这是猫"
- 小孩看过足够多例子后，自己就能认出没见过的新猫

机器学习就是这个道理——不是程序员写死规则，而是让计算机自己从数据中发现规律。

#### 核心概念
**机器学习 (Machine Learning, ML)**：一种让计算机通过数据学习模式和规律的技术，无需明确编程每个规则。

传统编程 vs 机器学习：
```
传统编程：规则 + 数据 → 答案
机器学习：答案 + 数据 → 规则
```

#### 数学直觉
机器学习的本质是找到一个函数 f(x)，使得：
- 输入 x（数据特征）
- 输出 f(x)（预测结果）
- 目标：f(x) 尽可能接近真实标签 y

形式化表达：找到最优参数 θ，使得 Loss(y, f(x; θ)) 最小化。

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import numpy as np

# 简单线性回归示例
# 假设我们有一组数据：房屋面积 → 房价
# 我们想找到 y = w * x + b 这个线性关系

# 训练数据
X = np.array([50, 80, 100, 120, 150])  # 房屋面积（平方米）
y = np.array([150, 240, 300, 360, 450])  # 房价（万元）

# 初始参数
w = 0.0  # 权重
b = 0.0  # 偏置

# 学习率
lr = 0.01

# 训练过程
for epoch in range(1000):
    # 前向传播：计算预测值
    y_pred = w * X + b
    
    # 计算损失（均方误差）
    loss = np.mean((y_pred - y) ** 2)
    
    # 反向传播：计算梯度
    dw = 2 * np.mean((y_pred - y) * X)
    db = 2 * np.mean(y_pred - y)
    
    # 更新参数
    w = w - lr * dw
    b = b - lr * db
    
    if epoch % 200 == 0:
        print(f"Epoch {epoch}: loss = {loss:.2f}, w = {w:.2f}, b = {b:.2f}")

# 最终结果
print(f"\n学习到的函数: y = {w:.2f} * x + {b:.2f}")
print(f"\n预测100平方米房屋价格: {w * 100 + b:.2f}万元")
```

#### 常见坑点
- **数据质量比算法重要**：垃圾进，垃圾出（Garbage in, garbage out）
- **特征工程是关键**：好的特征能让简单模型也表现很好
- **不是越复杂越好**：简单模型往往更稳定、更易解释

---

### 1.2 机器学习的三大范式

机器学习根据学习方式可以分为三大类：监督学习、无监督学习和强化学习。

#### 1.2.1 监督学习（有老师教）

##### 一句话人话
监督学习就像有老师批改作业的学习——每个训练样本都有标准答案。

##### 生活比喻
想象你学车时的场景：
- 教练坐在副驾驶，告诉你每个时刻应该怎么操作
- "前面有车，加速太猛了，踩点刹车"
- "弯道要减速"
- 教练就是"监督者"，每个操作都有对错反馈

监督学习就是计算机有"老师"（标签）指导学习。

##### 核心概念
**监督学习 (Supervised Learning)**：每个训练样本都有对应的"标准答案"（标签），模型学习从输入到输出的映射关系。

两种主要任务：
- **分类 (Classification)**：预测离散的类别标签
  - 垃圾邮件识别：邮件 → [垃圾邮件, 正常邮件]
  - 图像分类：图片 → [猫, 狗, 鸟, ...]
- **回归 (Regression)**：预测连续的值
  - 房价预测：面积、位置 → 具体价格
  - 温度预测：日期、气压 → 具体温度

##### 数学直觉
分类：找到决策边界，将不同类别的数据分开
回归：拟合一条曲线/超平面，使预测值与真实值的误差最小

##### PyTorch代码
```python
import torch
import torch.nn as nn

# 分类任务示例：鸢尾花分类
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 加载数据
iris = load_iris()
X, y = iris.data, iris.target

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 标准化
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 转换为PyTorch张量
X_train_t = torch.FloatTensor(X_train)
y_train_t = torch.LongTensor(y_train)
X_test_t = torch.FloatTensor(X_test)
y_test_t = torch.LongTensor(y_test)

# 定义分类模型
class IrisClassifier(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=16, output_dim=3):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        return self.network(x)

# 初始化
model = IrisClassifier()
criterion = nn.CrossEntropyLoss()  # 分类用交叉熵损失
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# 训练
for epoch in range(200):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train_t)
    loss = criterion(outputs, y_train_t)
    loss.backward()
    optimizer.step()
    
    if (epoch + 1) % 50 == 0:
        # 验证
        model.eval()
        with torch.no_grad():
            outputs = model(X_test_t)
            _, predicted = torch.max(outputs, 1)
            accuracy = (predicted == y_test_t).float().mean()
            print(f"Epoch [{epoch+1}/200], Loss: {loss.item():.4f}, Accuracy: {accuracy:.4f}")

print("\n训练完成！")
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
# 回归任务示例：房价预测
import matplotlib.pyplot as plt

# 训练数据：房屋面积 vs 房价
X_train = torch.randn(100, 1) * 20 + 80  # 面积：均值80，标准差20
y_train = X_train * 2.5 + 10 + torch.randn(100, 1) * 5  # 价格 = 2.5*面积 + 10 + 噪声

# 定义简单线性回归模型
class LinearRegression(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(1, 1)
    
    def forward(self, x):
        return self.linear(x)

model = LinearRegression()
criterion = nn.MSELoss()  # 回归用均方误差
optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

# 训练
losses = []
for epoch in range(100):
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()
    losses.append(loss.item())

print(f"学习到的参数: weight = {model.linear.weight.item():.4f}, bias = {model.linear.bias.item():.4f}")
print(f"真实参数: weight = 2.5, bias = 10")
```

##### 常见坑点
- **类别不平衡**：如果猫的照片有10000张，狗的只有100张，模型会倾向于预测猫
- **过拟合**：模型把训练数据背下来了，但遇到新数据就傻眼
- **欠拟合**：模型太简单，连训练数据的主要规律都没学到

---

#### 1.2.2 无监督学习（自己摸索）

##### 一句话人话
无监督学习就像没人告诉你对错，自己从数据中发现规律和结构。

##### 生活比喻
想象你第一次去超市：
- 没人告诉你货架怎么摆
- 但你会自然发现：蔬菜在一起、水果在一起、调味品在一起
- 这是你自己发现的"规律"——没人事先教你，但你学到了结构

无监督学习就是让计算机自己发现数据中的隐藏结构。

##### 核心概念
**无监督学习 (Unsupervised Learning)**：训练数据没有标签，模型自动发现数据中的模式、结构或分布。

主要任务：
- **聚类 (Clustering)**：将相似的数据点分组
  - 客户分群：网购用户 → [高消费型, 浏览型, 比价型]
  - 图像压缩：相似像素合并
- **降维 (Dimensionality Reduction)**：减少特征数量，保留关键信息
  - PCA：主成分分析
  - t-SNE：可视化高维数据
- **异常检测 (Anomaly Detection)**：发现与众不同的数据点
  - 信用卡欺诈检测
  - 工业设备故障预警

##### 数学直觉
聚类：最小化簇内距离，最大化簇间距离
降维：找到高维数据在低维空间中的最优表示

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
from sklearn.datasets import make_blobs, make_moons
import matplotlib.pyplot as plt

# K-Means聚类示例
def kmeans_clustering(X, k=3, num_epochs=100):
    """手动实现K-Means聚类"""
    # 随机初始化k个中心点
    idx = torch.randperm(len(X))[:k]
    centers = X[idx].clone()
    
    for epoch in range(num_epochs):
        # 计算每个点到各中心的距离，分配到最近的簇
        distances = torch.cdist(X, centers)  # [n, k]
        labels = torch.argmin(distances, dim=1)  # [n]
        
        # 更新中心点
        new_centers = torch.zeros_like(centers)
        for i in range(k):
            mask = labels == i
            if mask.sum() > 0:
                new_centers[i] = X[mask].mean(dim=0)
        
        # 如果某个簇为空，随机重新初始化
        for i in range(k):
            if new_centers[i].sum() == 0:
                new_centers[i] = X[torch.randint(len(X), (1,))].clone()
        
        # 检查收敛
        if torch.allclose(centers, new_centers, atol=1e-4):
            centers = new_centers
            print(f"在第{epoch}轮收敛")
            break
        centers = new_centers
    
    return labels, centers

# 生成聚类数据
X, _ = make_blobs(n_samples=300, centers=3, cluster_std=1.0, random_state=42)
X = torch.FloatTensor(X)

# 执行聚类
labels, centers = kmeans_clustering(X, k=3)

# 可视化
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', alpha=0.6)
plt.scatter(centers[:, 0], centers[:, 1], c='red', marker='x', s=200, linewidths=3)
plt.title('K-Means聚类结果')
plt.xlabel('特征1')
plt.ylabel('特征2')

# 降维示例：PCA
from sklearn.decomposition import PCA

# 生成高维数据
X_high = torch.randn(200, 10)
X_high[:, 0] = X_high[:, 0] * 3 + X_high[:, 1]  # 特征相关
X_high[:, 2] = X_high[:, 2] * 2 + torch.randn(200) * 0.5

# PCA降维到2维
pca = PCA(n_components=2)
X_low = pca.fit_transform(X_high.numpy())

plt.subplot(1, 2, 2)
plt.scatter(X_low[:, 0], X_low[:, 1], alpha=0.6)
plt.title(f'PCA降维 (解释方差比: {pca.explained_variance_ratio_.sum():.2%})')
plt.xlabel('主成分1')
plt.ylabel('主成分2')
plt.tight_layout()
plt.savefig('unsupervised_learning.png', dpi=150)
print("\n无监督学习示例图已保存")
```

##### 常见坑点
- **聚类数量K的选择**：K-Means需要预先指定K，但通常我们不知道数据应该分成几类
- **初始化敏感**：随机初始化可能导致不同的聚类结果
- **解释困难**：发现的结构是否有意义需要领域知识判断

---

#### 1.2.3 强化学习（奖惩学习）

##### 一句话人话
强化学习就像训练小狗——做对了给零食奖励，做错了批评，最后它自己学会新技能。

##### 生活比喻
想象你学骑自行车：
- 没人告诉你具体怎么操作
- 你尝试各种动作
- 如果自行车倒了（惩罚），你调整动作
- 如果骑得稳（奖励），你记住这个动作
- 最终你学会了骑车

强化学习就是通过不断试错和反馈，让智能体学会最优策略。

##### 核心概念
**强化学习 (Reinforcement Learning, RL)**：智能体通过与环境交互，根据奖励信号学习最优策略。

核心要素：
- **智能体 (Agent)**：学习决策的主体（机器人、游戏AI）
- **环境 (Environment)**：智能体所处的外部世界
- **状态 (State)**：环境在某一时刻的描述
- **动作 (Action)**：智能体可以采取的行动
- **奖励 (Reward)**：对动作的即时反馈
- **策略 (Policy)**：状态→动作的映射关系

##### 数学直觉
强化学习的目标是最大化累计奖励：
- 即时奖励：当前动作获得的奖励
- 未来奖励：当前动作对后续状态的影响

价值函数 V(s)：在状态s下未来能获得的期望累计奖励
Q函数 Q(s, a)：在状态s下执行动作a后能获得的期望累计奖励

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
# 简单的Q-Learning示例：走迷宫
import numpy as np

# 定义迷宫环境
class Maze:
    def __init__(self):
        # 0=空地, 1=墙壁, 2=终点
        self.grid = np.array([
            [0, 0, 0, 0, 1],
            [1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 2]
        ])
        self.start = (0, 0)
        self.end = (4, 4)
        self.state = self.start
    
    def reset(self):
        self.state = self.start
        return self.state
    
    def step(self, action):
        # 动作: 0=上, 1=下, 2=左, 3=右
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        new_state = (
            self.state[0] + moves[action][0],
            self.state[1] + moves[action][1]
        )
        
        # 检查是否撞墙
        if (0 <= new_state[0] < 5 and 
            0 <= new_state[1] < 5 and 
            self.grid[new_state] != 1):
            self.state = new_state
        
        # 计算奖励
        if self.state == self.end:
            return self.state, 100, True  # 到达终点
        elif self.grid[self.state] == 1:
            return self.state, -10, False  # 撞墙
        
        # 距离终点的曼哈顿距离作为奖励引导
        dist = abs(self.state[0] - self.end[0]) + abs(self.state[1] - self.end[1])
        return self.state, -0.1, False  # 每步小惩罚，鼓励快速到达

# Q-Learning算法
def q_learning(env, num_episodes=500, alpha=0.1, gamma=0.95, epsilon=0.1):
    # 初始化Q表
    q_table = np.zeros((5, 5, 4))
    
    for episode in range(num_episodes):
        state = env.reset()
        done = False
        
        while not done:
            # Epsilon-greedy策略
            if np.random.random() < epsilon:
                action = np.random.randint(4)
            else:
                action = np.argmax(q_table[state[0], state[1]])
            
            # 执行动作
            next_state, reward, done = env.step(action)
            
            # Q-Learning更新
            current_q = q_table[state[0], state[1], action]
            max_next_q = np.max(q_table[next_state[0], next_state[1]])
            q_table[state[0], state[1], action] = current_q + alpha * (
                reward + gamma * max_next_q - current_q
            )
            
            state = next_state
        
        if (episode + 1) % 100 == 0:
            print(f"Episode {episode + 1}/{num_episodes} 完成")
    
    return q_table

# 运行Q-Learning
env = Maze()
q_table = q_learning(env)

# 展示学习结果
def show_path(env, q_table):
    state = env.reset()
    path = [state]
    print(f"起点: {state}")
    
    for _ in range(20):
        action = np.argmax(q_table[state[0], state[1]])
        next_state, reward, done = env.step(action)
        path.append(next_state)
        print(f" -> {next_state}", end="")
        
        if done:
            print("\n成功到达终点！")
            break
        state = next_state
    
    return path

print("\n学习到的最优路径:")
path = show_path(env, q_table)
```

##### 常见坑点
- **奖励稀疏**：有时候只有完成任务才有奖励，过程漫长难以学习
- **探索-利用权衡**：是一直尝试新方法（探索），还是用已知最好的方法（利用）
- **长期信用分配**：很难判断很久以前的一个动作对最终结果有多大贡献

---

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### ⚠️ 小白易懵点

**监督学习 vs 无监督学习 vs 强化学习的核心区别**

很多人容易混淆这三种学习方式，关键在于理解"有没有标签/反馈"：

| 类型 | 有没有"老师" | 有没有"反馈" | 典型任务 |
|------|-------------|-------------|---------|
| 监督学习 | 有（标签数据） | 有（每步都对错） | 分类、回归 |
| 无监督学习 | 无（无标签） | 无（自己发现结构） | 聚类、降维 |
| 强化学习 | 无（无标签） | 有（延迟的奖励/惩罚） | 游戏AI、机器人控制 |

简单记忆：
- 监督 = 有答案 + 每步反馈
- 无监督 = 没答案 + 也没反馈，自己找规律
- 强化 = 没答案 + 最终奖励反馈

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结

> 机器学习就是让计算机从数据中学习规律：监督学习有"标准答案"指导、无监督学习自己发现数据中的隐藏结构、强化学习通过试错和奖惩学习最优策略。

---


### 1.3 数据集划分：课本、模拟考与正式考

机器学习模型的训练和评估需要将数据划分为不同的集合，就像学习过程需要课本学习、模拟考试和正式考试一样。

#### 一句话人话
用一部分数据训练模型，一部分数据调参，最后用没见过的数据测试真实水平。

#### 生活比喻
想象学生备战高考：
- **训练集**：日常做作业、练习题，用来学习知识
- **验证集**：模拟考试，用来调整学习方法、选择最优策略
- **测试集**：最终高考，完全没见过的题，检验真实水平

如果在练习题上考得好，但高考考得差，说明只是"死记硬背"，没有真正学会。

#### 核心概念
**训练集 (Training Set)**：用于训练模型的数据，让模型学习参数
**验证集 (Validation Set)**：用于调参和模型选择的数据，防止过拟合
**测试集 (Test Set)**：最终评估模型性能的数据，代表真实场景

常见的划分比例：
- 小数据集：70% 训练 / 15% 验证 / 15% 测试
- 大数据集：98% 训练 / 1% 验证 / 1% 测试
- 交叉验证：小数据集常用k折交叉验证

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

# 创建示例数据集
X, y = make_classification(
    n_samples=1000,  # 1000个样本
    n_features=20,   # 20个特征
    n_informative=15,  # 15个有意义的特征
    n_redundant=5,    # 5个冗余特征
    n_classes=2,      # 二分类
    random_state=42
)

# 方法1：手动划分
X_train, X_temp = train_test_split(X, test_size=0.3, random_state=42)
X_val, X_test = train_test_split(X_temp, test_size=0.5, random_state=42)
y_train, y_temp = train_test_split(y, test_size=0.3, random_state=42)
y_val, y_test = train_test_split(y_temp, test_size=0.5, random_state=42)

print("手动划分结果:")
print(f"  训练集: {len(X_train)} 样本 ({len(X_train)/len(X)*100:.1f}%)")
print(f"  验证集: {len(X_val)} 样本 ({len(X_val)/len(X)*100:.1f}%)")
print(f"  测试集: {len(X_test)} 样本 ({len(X_test)/len(X)*100:.1f}%)")

# 方法2：sklearn的train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 方法3：K折交叉验证（适用于小数据集）
from sklearn.model_selection import KFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier

kfold = KFold(n_splits=5, shuffle=True, random_state=42)
model = RandomForestClassifier(n_estimators=10)

# 交叉验证
scores = cross_val_score(model, X, y, cv=kfold, scoring='accuracy')
print(f"\n5折交叉验证结果:")
print(f"  各折准确率: {scores}")
print(f"  平均准确率: {scores.mean():.4f} ± {scores.std()*2:.4f}")

# 转换为PyTorch张量
X_train_t = torch.FloatTensor(X_train)
y_train_t = torch.LongTensor(y_train)
X_test_t = torch.FloatTensor(X_test)
y_test_t = torch.LongTensor(y_test)
```

#### 常见坑点
- **数据泄露 (Data Leakage)**：测试集信息不小心混入训练集，导致评估结果虚高
- **验证集过拟合**：频繁在验证集上调整参数，可能对验证集过拟合
- **分布不一致**：训练集和测试集分布差异大，模型泛化能力差

---

### 1.4 损失函数：衡量"成绩差距"

损失函数是机器学习中的"评分标准"，衡量模型预测值与真实值之间的差距。

#### 一句话人话
损失函数就是计算"你预测的答案和标准答案差多少"的数学方法。

#### 生活比喻
考试结束后，老师批改试卷：
- 你的答案和标准答案对比
- 完全正确得0分（没差距）
- 错了就扣分（差距越大扣分越多）

损失函数就是这个"扣分规则"，我们的目标是最小化这个"损失"。

#### 核心概念
**损失函数 (Loss Function)**：衡量模型预测值与真实值之间差距的函数。

常用损失函数：

| 任务类型 | 损失函数 | 适用场景 |
|---------|---------|---------|
| 回归 | MSE（均方误差） | 连续值预测，如房价 |
| 回归 | MAE（平均绝对误差） | 对异常值鲁棒 |
| 二分类 | BCE（二值交叉熵） | 垃圾邮件检测 |
| 多分类 | CE（交叉熵） | 图像分类 |
| 排序 | Hinge Loss | SVM、支持向量机 |

##### 数学直觉
- **MSE**：误差的平方和，惩罚大误差更严重
  ```
  MSE = (1/n) * Σ(y_pred - y_true)²
  ```
- **MAE**：误差的绝对值和，对异常值不敏感
  ```
  MAE = (1/n) * Σ|y_pred - y_true|
  ```
- **交叉熵**：信息论角度衡量两个分布的差异
  ```
  CE = -Σ(y_true * log(y_pred))
  ```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# 可视化不同损失函数的特性
x = torch.linspace(-3, 3, 100)

# MSE Loss
mse = x ** 2

# MAE Loss
mae = torch.abs(x)

# Hinge Loss (for SVM)
hinge = torch.clamp(1 - x, min=0)

plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.plot(x.numpy(), mse.numpy(), 'b-', linewidth=2)
plt.title('MSE (均方误差)\n大误差惩罚严重', fontsize=12)
plt.xlabel('预测误差')
plt.ylabel('Loss')
plt.grid(True, alpha=0.3)
plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

plt.subplot(1, 3, 2)
plt.plot(x.numpy(), mae.numpy(), 'g-', linewidth=2)
plt.title('MAE (平均绝对误差)\n对异常值不敏感', fontsize=12)
plt.xlabel('预测误差')
plt.ylabel('Loss')
plt.grid(True, alpha=0.3)
plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

plt.subplot(1, 3, 3)
plt.plot(x.numpy(), hinge.numpy(), 'r-', linewidth=2)
plt.title('Hinge Loss\n只惩罚错误预测', fontsize=12)
plt.xlabel('预测误差')
plt.ylabel('Loss')
plt.grid(True, alpha=0.3)
plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

plt.tight_layout()
plt.savefig('loss_functions.png', dpi=150)

# PyTorch中的损失函数使用示例
print("=== 损失函数使用示例 ===\n")

# 模拟预测和真实值
y_true = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])  # 真实房价
y_pred = torch.tensor([1.2, 1.8, 3.2, 4.5, 4.8])  # 预测房价

# MSE Loss
mse_loss = nn.MSELoss()
print(f"MSE Loss: {mse_loss(y_pred, y_true):.4f}")

# MAE Loss
mae_loss = nn.L1Loss()
print(f"MAE Loss: {mae_loss(y_pred, y_true):.4f}")

# 分类任务损失函数
print("\n=== 分类损失函数示例 ===\n")

# 二分类
y_true_binary = torch.tensor([0, 1, 1, 0, 1])
y_pred_binary = torch.tensor([0.2, 0.8, 0.7, 0.3, 0.9])

bce_loss = nn.BCELoss()
sigmoid = nn.Sigmoid()
print(f"BCE Loss (二分类): {bce_loss(sigmoid(y_pred_binary), y_true_binary.float()):.4f}")

# 多分类
y_true_multi = torch.tensor([2, 0, 1, 3])  # 4个类别
y_pred_multi = torch.tensor([
    [0.1, 0.2, 0.6, 0.1],
    [0.7, 0.2, 0.05, 0.05],
    [0.3, 0.4, 0.2, 0.1],
    [0.1, 0.1, 0.2, 0.6]
])

ce_loss = nn.CrossEntropyLoss()
print(f"Cross Entropy Loss (多分类): {ce_loss(y_pred_multi, y_true_multi):.4f}")
```

#### 常见坑点
- **MSE对异常值敏感**：一个很大的误差会导致MSE突然变大
- **分类问题用MSE**：很多人误用MSE做分类，应该用交叉熵
- **损失函数与评估指标不一致**：训练用BCE，评估用准确率

---

### 1.5 梯度下降：蒙眼下山

梯度下降是机器学习中最核心的优化算法，让我们能够找到损失函数的最小值。

#### 一句话人话
梯度下降就像蒙着眼睛下山，每次都往坡度最陡的方向走，最终找到山谷底部。

#### 生活比喻
想象你被蒙眼放在山顶，要下山到谷底：
- 你脚下的地面有坡度（梯度）
- 你往最陡的下坡方向迈一步
- 重复这个过程，直到感觉不到下坡了

梯度下降就是这个过程，只不过是在"损失函数的曲面"上找最低点。

#### 核心概念
**梯度 (Gradient)**：函数在某一点的最陡上升方向
**梯度下降 (Gradient Descent)**：沿着梯度的反方向（最陡下降方向）更新参数

更新公式：
```
θ_new = θ_old - η * ∇L(θ)
```
其中：
- θ：模型参数
- η：学习率（步长）
- ∇L(θ)：损失函数的梯度

三种梯度下降变体：
- **批量梯度下降 (BGD)**：用所有样本算一次梯度
- **随机梯度下降 (SGD)**：每次用一个样本算梯度
- **小批量梯度下降 (Mini-batch GD)**：每次用一小批样本算梯度

##### 数学直觉
在一维情况下，梯度就是导数：
```
L(w) = (w - 2)² 的导数 = 2(w - 2)
```
在 w=5 处，梯度=6，意味着应该往负方向走才能减小损失。

在多维情况下，梯度是一个向量，指向最陡上升方向。

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import matplotlib.pyplot as plt
import numpy as np

# 手动实现梯度下降
def gradient_descent_1d(func, grad_func, initial_x, lr=0.1, num_steps=20):
    """一维梯度下降"""
    x = initial_x
    trajectory = [x]
    
    for _ in range(num_steps):
        gradient = grad_func(x)  # 计算梯度
        x = x - lr * gradient    # 更新参数
        trajectory.append(x)
    
    return x, trajectory

# 示例：最小化 y = (x - 3)²
def func(x):
    return (x - 3) ** 2

def grad_func(x):
    return 2 * (x - 3)

# 从不同起点开始
starts = [8.0, -2.0, 0.0]
colors = ['red', 'green', 'blue']

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
x_plot = np.linspace(-2, 10, 100)
plt.plot(x_plot, func(x_plot), 'k-', linewidth=2, label='目标函数')

for start, color in zip(starts, colors):
    final_x, trajectory = gradient_descent_1d(func, grad_func, start, lr=0.1, num_steps=30)
    plt.plot(trajectory, func(np.array(trajectory)), 'o-', color=color, 
             markersize=5, label=f'起点={start}')
    plt.plot(final_x, func(final_x), 's', color=color, markersize=10)

plt.xlabel('x')
plt.ylabel('Loss')
plt.title('梯度下降寻优过程')
plt.legend()
plt.grid(True, alpha=0.3)

# 学习率的影响
plt.subplot(1, 2, 2)
x_plot = np.linspace(-2, 10, 100)
plt.plot(x_plot, func(x_plot), 'k-', linewidth=2, label='目标函数')

learning_rates = [0.01, 0.1, 0.5, 0.9]
for lr in learning_rates:
    _, trajectory = gradient_descent_1d(func, grad_func, 8.0, lr=lr, num_steps=20)
    plt.plot(trajectory, func(np.array(trajectory)), 'o-', 
             markersize=4, label=f'lr={lr}')

plt.xlabel('x')
plt.ylabel('Loss')
plt.title('学习率的影响')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('gradient_descent.png', dpi=150)

# PyTorch自动微分示例
print("=== PyTorch自动微分 ===\n")

x = torch.tensor([2.0, 3.0, 4.0], requires_grad=True)
y = (x - 3) ** 2  # y = (x - 3)²

print(f"x = {x}")
print(f"y = {y}")
print(f"y.sum() = {y.sum()}")

# 反向传播
y.sum().backward()

print(f"\n梯度 dy/dx = {x.grad}")

# 用PyTorch优化器进行梯度下降
print("\n=== 使用优化器 ===\n")

# 定义模型参数
w = torch.tensor([5.0], requires_grad=True)
b = torch.tensor([1.0], requires_grad=True)

# 优化器
optimizer = torch.optim.SGD([w, b], lr=0.1)

# 模拟训练
X = torch.tensor([1.0, 2.0, 3.0, 4.0, 5.0])
y_true = torch.tensor([2.0, 4.0, 6.0, 8.0, 10.0])  # y = 2x

for epoch in range(50):
    optimizer.zero_grad()  # 清零梯度
    
    y_pred = w * X + b     # 前向传播
    loss = ((y_pred - y_true) ** 2).mean()  # 计算损失
    
    loss.backward()        # 反向传播
    optimizer.step()       # 更新参数
    
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}: loss = {loss.item():.4f}, w = {w.item():.4f}, b = {b.item():.4f}")

print(f"\n最终学习到的函数: y = {w.item():.4f} * x + {b.item():.4f}")
```

#### 常见坑点
- **学习率太大**：步子迈太大，会跳过最优点甚至发散
- **学习率太小**：步子太细，收敛太慢
- **局部最优**：可能卡在局部最低点，而不是全局最低点
- **梯度消失/爆炸**：深层网络中梯度太小或太大

---

### 1.6 过拟合与正则化：死记硬背 vs 理解规律

过拟合是机器学习中最常见的问题之一，正则化是解决过拟合的主要方法。

#### 一句话人话
过拟合就是"死记硬背"了训练数据，而正则化就是让模型学会"理解规律"而不是"背答案"。

#### 生活比喻
想象学生学习数学：
- **过拟合**：学生把课本上每一道题都背下来了，考试遇到类似的题但数字不同就不会了
- **欠拟合**：学生只学会了解加减法，连乘除法都不会
- **正则化**：老师在批改时提醒学生"不要死记硬背，要注意解题思路"

#### 核心概念
**过拟合 (Overfitting)**：模型在训练集上表现很好，但在测试集上表现差
**欠拟合 (Underfitting)**：模型在训练集和测试集上都表现不好
**正则化 (Regularization)**：通过添加约束防止过拟合的技术

正则化方法：
- **L1正则化 (Lasso)**：让参数稀疏化（自动特征选择）
- **L2正则化 (Ridge)**：让参数变小，防止参数过大
- **Dropout**：训练时随机丢弃一些神经元
- **Early Stopping**：验证集性能下降时停止训练

##### 数学直觉
在损失函数中添加正则项：
```
L_total = L_original + λ * R(θ)
```
- L1正则：R(θ) = Σ|θ|，惩罚参数绝对值
- L2正则：R(θ) = Σθ²，惩罚参数平方

L1正则化倾向于让参数变成0（特征稀疏），L2正则化倾向于让参数变小但不等于0。

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split

# 生成非线性数据
X, y = make_moons(n_samples=200, noise=0.2, random_state=42)
X = torch.FloatTensor(X)
y = torch.LongTensor(y)

# 划分数据
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 定义模型（不使用正则化）
class NoRegMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(2, 100),
            nn.ReLU(),
            nn.Linear(100, 100),
            nn.ReLU(),
            nn.Linear(100, 2)
        )
    
    def forward(self, x):
        return self.network(x)

# 定义模型（使用Dropout和L2正则）
class RegMLP(nn.Module):
    def __init__(self, dropout_rate=0.3):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(2, 100),
            nn.ReLU(),
            nn.Dropout(dropout_rate),  # Dropout
            nn.Linear(100, 100),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(100, 2)
        )
    
    def forward(self, x):
        return self.network(x)

# 训练函数
def train_model(model, X_train, y_train, X_test, y_test, epochs=200, weight_decay=0.0):
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=weight_decay)
    
    train_losses, test_losses = [], []
    train_accs, test_accs = [], []
    
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        output = model(X_train)
        loss = criterion(output, y_train)
        loss.backward()
        optimizer.step()
        
        # 评估
        model.eval()
        with torch.no_grad():
            train_pred = model(X_train).argmax(1)
            test_pred = model(X_test).argmax(1)
            
            train_acc = (train_pred == y_train).float().mean()
            test_acc = (test_pred == y_test).float().mean()
            
            train_losses.append(loss.item())
            test_losses.append(criterion(model(X_test), y_test).item())
            train_accs.append(train_acc.item())
            test_accs.append(test_acc.item())
    
    return train_losses, test_losses, train_accs, test_accs

# 训练不同模型
print("训练无正则化模型...")
model_no_reg = NoRegMLP()
train_loss_no, test_loss_no, train_acc_no, test_acc_no = train_model(
    model_no_reg, X_train, y_train, X_test, y_test
)

print("训练有正则化模型...")
model_reg = RegMLP(dropout_rate=0.3)
train_loss_reg, test_loss_reg, train_acc_reg, test_acc_reg = train_model(
    model_reg, X_train, y_train, X_test, y_test, weight_decay=0.01
)

# 可视化
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

axes[0, 0].plot(train_loss_no, label='训练损失')
axes[0, 0].plot(test_loss_no, label='测试损失')
axes[0, 0].set_title('无正则化 - 损失曲线')
axes[0, 0].set_xlabel('Epoch')
axes[0, 0].set_ylabel('Loss')
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].plot(train_loss_reg, label='训练损失')
axes[0, 1].plot(test_loss_reg, label='测试损失')
axes[0, 1].set_title('有正则化 - 损失曲线')
axes[0, 1].set_xlabel('Epoch')
axes[0, 1].set_ylabel('Loss')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

axes[1, 0].plot(train_acc_no, label='训练准确率')
axes[1, 0].plot(test_acc_no, label='测试准确率')
axes[1, 0].set_title('无正则化 - 准确率曲线')
axes[1, 0].set_xlabel('Epoch')
axes[1, 0].set_ylabel('Accuracy')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].plot(train_acc_reg, label='训练准确率')
axes[1, 1].plot(test_acc_reg, label='测试准确率')
axes[1, 1].set_title('有正则化 - 准确率曲线')
axes[1, 1].set_xlabel('Epoch')
axes[1, 1].set_ylabel('Accuracy')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('regularization.png', dpi=150)

print(f"\n最终结果对比:")
print(f"无正则化 - 测试准确率: {test_acc_no[-1]:.4f}")
print(f"有正则化 - 测试准确率: {test_acc_reg[-1]:.4f}")
```

#### 常见坑点
- **正则化系数λ的选择**：太大导致欠拟合，太小没效果
- **同时使用L1和L2**：不是总能让效果更好
- **Early Stopping时机**：过早停止会欠拟合，过晚停止会过拟合
- **Dropout只在训练时用**：测试时关闭Dropout

---

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### ⚠️ 小白易懵点

**验证集和测试集的区别**

很多人容易混淆验证集和测试集的作用：

| 集合 | 作用 | 使用频率 |
|------|------|---------|
| 训练集 | 学习参数 | 每轮训练都用 |
| 验证集 | 调超参数、选模型 | 训练过程中多次 |
| 测试集 | 最终评估 | 训练结束后一次 |

关键理解：
- **验证集是"模拟考试"**：考试前多做几套模拟卷，调整学习方法
- **测试集是"正式高考"**：只考一次，考完就知道真实水平

如果把测试集也拿来调参，就相当于"提前看了高考题"，成绩就不准了。

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结

> 数据集划分要分训练集（学习）、验证集（调参）、测试集（评估）；损失函数衡量预测与真实差距；梯度下降通过沿最陡下降方向迭代找到损失最小值；正则化通过惩罚复杂模型防止过拟合。

---



### 1.7 评估指标：模型的"考试成绩"

评估指标用来衡量模型的好坏，就像考试有各种评分标准一样。

#### 一句话人话
评估指标就是给模型打分的方式，不同任务需要不同的"评分标准"。

#### 生活比喻
高考不同科目有不同的评分：
- 语文：作文分、阅读理解分
- 数学：选择题、解答题
- 英语：听力、阅读、写作

不同任务也有不同的评估方式：分类任务看准确率，搜索任务看召回率，排序任务看AUC。

#### 核心概念
**混淆矩阵 (Confusion Matrix)**：
```
                 预测正例    预测反例
实际正例           TP         FN
实际反例           FP         TN
```

关键指标：
- **准确率 (Accuracy)** = (TP + TN) / Total
- **精确率 (Precision)** = TP / (TP + FP)
- **召回率 (Recall)** = TP / (TP + FN)
- **F1分数** = 2 × Precision × Recall / (Precision + Recall)
- **AUC-ROC**：ROC曲线下面积

##### 数学直觉
- **准确率**：所有预测中正确的比例
  ```
  Accuracy = (TP + TN) / (TP + TN + FP + FN)
  ```
- **精确率**：预测为正的样本中真正是正的比例（"我说是正的对不对"）
  ```
  Precision = TP / (TP + FP)
  ```
- **召回率**：所有正例中被正确预测的比例（"真正的正例找到了多少"）
  ```
  Recall = TP / (TP + FN)
  ```

精确率和召回率的权衡：
- 高精确率 = 宁可漏掉一些，也不乱预测
- 高召回率 = 宁可多预测一些，也不漏掉

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc, precision_recall_curve
)

# 模拟二分类问题
np.random.seed(42)
y_true = np.random.randint(0, 2, 1000)  # 真实标签
y_scores = np.random.rand(1000)         # 预测分数（0-1之间）

# 将预测分数转为二分类预测
y_pred = (y_scores > 0.5).astype(int)

# 计算各项指标
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)
f1 = f1_score(y_true, y_pred)

print("=== 评估指标 ===")
print(f"准确率 (Accuracy): {accuracy:.4f}")
print(f"精确率 (Precision): {precision:.4f}")
print(f"召回率 (Recall): {recall:.4f}")
print(f"F1分数 (F1-Score): {f1:.4f}")

# 混淆矩阵
cm = confusion_matrix(y_true, y_pred)
print(f"\n混淆矩阵:")
print(cm)

# 可视化混淆矩阵
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
plt.title('混淆矩阵')
plt.colorbar()
tick_marks = np.arange(2)
plt.xticks(tick_marks, ['负例', '正例'])
plt.yticks(tick_marks, ['负例', '正例'])
plt.xlabel('预测标签')
plt.ylabel('真实标签')

# 在矩阵中显示数字
for i in range(2):
    for j in range(2):
        plt.text(j, i, cm[i, j], ha='center', va='center', 
                color='white' if cm[i, j] > cm.max()/2 else 'black')

# ROC曲线
fpr, tpr, thresholds = roc_curve(y_true, y_scores)
roc_auc = auc(fpr, tpr)

plt.subplot(1, 3, 2)
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC曲线 (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='随机猜测')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('假阳性率 (FPR)')
plt.ylabel('真阳性率 (TPR)')
plt.title('ROC曲线')
plt.legend(loc='lower right')
plt.grid(True, alpha=0.3)

# 精确率-召回率曲线
precision_curve, recall_curve, _ = precision_recall_curve(y_true, y_scores)

plt.subplot(1, 3, 3)
plt.plot(recall_curve, precision_curve, color='green', lw=2)
plt.xlabel('召回率 (Recall)')
plt.ylabel('精确率 (Precision)')
plt.title('精确率-召回率曲线')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('evaluation_metrics.png', dpi=150)

# 多分类评估
print("\n=== 多分类评估示例 ===")
y_true_multi = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
y_pred_multi = np.array([0, 1, 2, 0, 2, 2, 1, 1, 2])

print(f"多分类准确率: {accuracy_score(y_true_multi, y_pred_multi):.4f}")
print(f"宏平均F1: {f1_score(y_true_multi, y_pred_multi, average='macro'):.4f}")
print(f"微平均F1: {f1_score(y_true_multi, y_pred_multi, average='micro'):.4f}")
print(f"加权F1: {f1_score(y_true_multi, y_pred_multi, average='weighted'):.4f}")

# PyTorch模型评估示例
print("\n=== PyTorch模型评估 ===")

class SimpleClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(10, 2)
    
    def forward(self, x):
        return self.linear(x)

model = SimpleClassifier()
model.eval()

# 模拟测试数据
X_test = torch.randn(100, 10)
y_test = torch.randint(0, 2, (100,))

with torch.no_grad():
    outputs = model(X_test)
    _, predictions = torch.max(outputs, 1)
    
    correct = (predictions == y_test).sum().item()
    accuracy = correct / len(y_test)
    
print(f"测试集准确率: {accuracy:.4f}")
```

#### 常见坑点
- **准确率悖论**：如果数据不平衡，99%都是正例，预测全正也有99%准确率
- **只看准确率**：对于不平衡数据集，精确率、召回率、F1更重要
- **混淆AUC和准确率**：AUC衡量排序能力，不受阈值影响

---

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### ⚠️ 小白易懵点

**精确率 vs 召回率：看病 vs 抓小偷**

想象两个场景帮助理解：

**场景1：癌症筛查**
- 目标：不能漏掉任何可能的病人
- 策略：宁可多检查，不能漏诊
- 关注：**召回率**（真正的病人找到了多少）

**场景2：垃圾邮件判断**
- 目标：不能误删重要邮件
- 策略：宁可放过垃圾邮件，不能误删正常邮件
- 关注：**精确率**（我说是垃圾邮件的真的有多少是垃圾）

简单记忆：
- **召回率 = 找全了吗**（宁可错杀，不可放过）
- **精确率 = 找对了吗**（宁缺毋滥）

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结

> 监督学习、无监督学习和强化学习是机器学习的三大范式；数据集划分要分训练/验证/测试集；损失函数衡量预测差距；梯度下降是最核心的优化算法；正则化防止过拟合；评估指标（准确率、精确率、召回率、F1、AUC）从不同角度衡量模型性能。

---

## 第二篇：深度学习基础

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 2.1 从感知机到MLP：投票员与委员会

感知机是神经网络的基础单元，多层感知机（MLP）是由多个感知机组成的网络。

#### 一句话人话
感知机就像一个投票员，根据多个证据做判断；MLP就像一个委员会，多层投票员一起决定。

#### 生活比喻
想象公司招聘面试：
- **单个投票员（感知机）**：看一个候选人的简历就决定录用
- **委员会投票（MLP）**：多个面试官分别打分，综合意见决定

单个面试官可能有偏见，多个面试官一起讨论更公平。

#### 核心概念
**感知机 (Perceptron)**：最简单的人工神经元
- 输入：x₁, x₂, ..., xₙ
- 权重：w₁, w₂, ..., wₙ
- 偏置：b
- 输出：y = activation(Σwᵢxᵢ + b)

**多层感知机 (MLP)**：由输入层、隐藏层、输出层组成
- 输入层：接收原始特征
- 隐藏层：提取抽象特征
- 输出层：产生最终预测

##### 数学直觉
单个感知机：
```
z = w₁x₁ + w₂x₂ + ... + wₙxₙ + b
y = step(z)  # 阶跃函数：z > 0 → 1, 否则 → 0
```

MLP的前向传播：
```
隐藏层: h = activation(W₁x + b₁)
输出层: y = softmax(W₂h + b₂)
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# 感知机实现
class Perceptron(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.linear = nn.Linear(input_dim, 1)
    
    def forward(self, x):
        return torch.sigmoid(self.linear(x))  # Sigmoid作为激活函数

# 演示感知机：逻辑运算
print("=== 感知机实现逻辑运算 ===\n")

# AND运算
X_and = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
y_and = torch.tensor([0., 0., 0., 1.])

# OR运算
X_or = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
y_or = torch.tensor([0., 1., 1., 1.])

# 训练感知机做AND运算
def train_perceptron(X, y, epochs=1000):
    model = Perceptron(2)
    criterion = nn.BCELoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.5)
    
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X).squeeze()
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()
    
    return model

and_model = train_perceptron(X_and, y_and)
print("AND运算学习后的权重:", list(and_model.parameters()))

# 测试AND
with torch.no_grad():
    and_pred = and_model(X_and).squeeze()
    print(f"AND预测: {and_pred.numpy().round(2)}")

# 演示MLP：XOR运算（感知机做不到的）
print("\n=== MLP解决XOR问题 ===")
print("XOR真值表:")
print("0 XOR 0 = 0")
print("0 XOR 1 = 1")
print("1 XOR 0 = 1")
print("1 XOR 1 = 0")

class MLP(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),  # 非线性激活
            nn.Linear(hidden_dim, output_dim),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.network(x)

# MLP解决XOR
X_xor = torch.tensor([[0., 0.], [0., 1.], [1., 0.], [1., 1.]])
y_xor = torch.tensor([0., 1., 1., 0.])

mlp = MLP(2, 8, 1)
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(mlp.parameters(), lr=0.1)

print("\n训练MLP解决XOR...")
for epoch in range(1000):
    optimizer.zero_grad()
    outputs = mlp(X_xor).squeeze()
    loss = criterion(outputs, y_xor)
    loss.backward()
    optimizer.step()
    
    if (epoch + 1) % 200 == 0:
        print(f"Epoch {epoch+1}: Loss = {loss.item():.4f}")

# 测试XOR
with torch.no_grad():
    xor_pred = mlp(X_xor).squeeze()
    print(f"\nXOR预测: {xor_pred.numpy().round(2)}")
    print(f"真实值: {y_xor.numpy()}")

# 可视化感知机与MLP
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 感知机只能学线性边界
x_range = np.linspace(-0.5, 1.5, 100)
y_range = np.linspace(-0.5, 1.5, 100)
xx, yy = np.meshgrid(x_range, y_range)
points = torch.FloatTensor(np.c_[xx.ravel(), yy.ravel()])

and_model.eval()
with torch.no_grad():
    Z = and_model(points).reshape(xx.shape)

axes[0].contourf(xx, yy, Z, alpha=0.3, cmap='RdYlGn')
axes[0].scatter([0, 1], [0, 1], c=['green'], s=100, label='正例')
axes[0].scatter([0, 1], [1, 0], c=['red'], s=100, label='负例')
axes[0].set_title('感知机：线性边界 (AND)')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# MLP可以学非线性边界
mlp.eval()
with torch.no_grad():
    Z = mlp(points).reshape(xx.shape)

axes[1].contourf(xx, yy, Z, alpha=0.3, cmap='RdYlGn')
axes[1].scatter([0, 1], [0, 1], c=['green'], s=100, label='正例')
axes[1].scatter([0, 1], [1, 0], c=['red'], s=100, label='负例')
axes[1].set_title('MLP：非线性边界 (XOR)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('perceptron_vs_mlp.png', dpi=150)
```

#### 常见坑点
- **感知机只能解决线性可分问题**：XOR问题需要MLP
- **隐藏层的重要性**：没有隐藏层 = 线性模型，无法处理复杂问题
- **激活函数的必要性**：没有激活函数，多层网络等于单层

---

### 2.2 激活函数：神经元的"开关"

激活函数给神经网络引入非线性，让网络能够学习复杂的模式。

#### 一句话人话
激活函数就像神经元的"开关"，决定是否"激活"这个神经元。

#### 生活比喻
想象大脑神经元的工作方式：
- **ReLU**：要么完全激活（开），要么不激活（关）
- **Sigmoid**：渐变激活，强弱程度不同
- **GELU**：智能激活，越相关的输入激活越强

#### 核心概念
**激活函数 (Activation Function)**：将神经元的线性输出转换为非线性输出。

常用激活函数：
| 函数 | 公式 | 特点 |
|------|------|------|
| Sigmoid | 1/(1+e⁻ˣ) | 输出0-1，易梯度消失 |
| Tanh | (eˣ-e⁻ˣ)/(eˣ+e⁻ˣ) | 输出-1到1，易梯度消失 |
| ReLU | max(0, x) | 计算快，Dead ReLU问题 |
| Leaky ReLU | max(0.01x, x) | 解决ReLU的Dead问题 |
| GELU | x * Φ(x) | Transformer常用 |
| Softmax | eˣⁱ/Σeˣʲ | 多分类输出 |

##### 数学直觉
- **ReLU**：简单但强大，将负值变0
  ```
  ReLU(x) = max(0, x)
  ```
- **Sigmoid**：将任意值压缩到(0,1)
  ```
  σ(x) = 1 / (1 + e⁻ˣ)
  ```
- **GELU**：基于高斯分布的平滑近似ReLU
  ```
  GELU(x) ≈ 0.5x(1 + tanh(√(2/π)(x + 0.044715x³)))
  ```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# 定义各种激活函数
x = torch.linspace(-5, 5, 100)

# ReLU
relu = nn.ReLU()
relu_y = relu(x)

# Leaky ReLU
leaky_relu = nn.LeakyReLU(0.1)
leaky_relu_y = leaky_relu(x)

# Sigmoid
sigmoid = nn.Sigmoid()
sigmoid_y = sigmoid(x)

# Tanh
tanh = nn.Tanh()
tanh_y = tanh(x)

# GELU
gelu = nn.GELU()
gelu_y = gelu(x)

# SiLU (Swish)
silu = nn.SiLU()
silu_y = silu(x)

# 可视化
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

axes[0, 0].plot(x.numpy(), relu_y.numpy(), 'b-', linewidth=2)
axes[0, 0].set_title('ReLU\n(max(0, x))', fontsize=12)
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
axes[0, 0].axvline(x=0, color='k', linestyle='-', linewidth=0.5)

axes[0, 1].plot(x.numpy(), leaky_relu_y.numpy(), 'g-', linewidth=2)
axes[0, 1].set_title('Leaky ReLU\n(max(0.1x, x))', fontsize=12)
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
axes[0, 1].axvline(x=0, color='k', linestyle='-', linewidth=0.5)

axes[0, 2].plot(x.numpy(), sigmoid_y.numpy(), 'r-', linewidth=2)
axes[0, 2].set_title('Sigmoid\n(1/(1+e^(-x)))', fontsize=12)
axes[0, 2].grid(True, alpha=0.3)
axes[0, 2].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
axes[0, 2].axhline(y=1, color='k', linestyle='--', linewidth=0.5)

axes[1, 0].plot(x.numpy(), tanh_y.numpy(), 'm-', linewidth=2)
axes[1, 0].set_title('Tanh\n((e^x-e^(-x))/(e^x+e^(-x)))', fontsize=12)
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].axhline(y=0, color='k', linestyle='-', linewidth=0.5)
axes[1, 0].axhline(y=1, color='k', linestyle='--', linewidth=0.5)
axes[1, 0].axhline(y=-1, color='k', linestyle='--', linewidth=0.5)

axes[1, 1].plot(x.numpy(), gelu_y.numpy(), 'c-', linewidth=2)
axes[1, 1].set_title('GELU\n(x * Φ(x))', fontsize=12)
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].axhline(y=0, color='k', linestyle='-', linewidth=0.5)

axes[1, 2].plot(x.numpy(), silu_y.numpy(), 'y-', linewidth=2)
axes[1, 2].set_title('SiLU (Swish)\n(x * sigmoid(x))', fontsize=12)
axes[1, 2].grid(True, alpha=0.3)
axes[1, 2].axhline(y=0, color='k', linestyle='-', linewidth=0.5)

plt.suptitle('常用激活函数', fontsize=16, y=1.02)
plt.tight_layout()
plt.savefig('activation_functions.png', dpi=150)

# Softmax示例
print("=== Softmax示例 ===\n")
logits = torch.tensor([2.0, 1.0, 0.1])
softmax = nn.Softmax(dim=0)
probs = softmax(logits)

print(f"原始分数: {logits}")
print(f"Softmax概率: {probs}")
print(f"概率和: {probs.sum():.4f}")

# 多分类Softmax
logits_multi = torch.tensor([[2.0, 1.0, 0.1],
                              [0.5, 3.0, 1.5]])
probs_multi = softmax(logits_multi)
print(f"\n多分类Softmax:")
print(probs_multi)
```

#### 常见坑点
- **Sigmoid梯度消失**：两端饱和，梯度接近0，深层网络难以训练
- **ReLU的Dead ReLU问题**：负输入永远输出0，对应梯度也是0
- **输出层激活选择**：分类用Softmax，回归不用激活函数

---



### 2.3 前向传播与反向传播：做题与批改

前向传播和反向传播是神经网络训练的两个核心过程，类似于学生做题和老师批改。

#### 一句话人话
前向传播是"做题"（输入→输出），反向传播是"批改"（计算每个答案错在哪里）。

#### 生活比喻
学习数学的过程：
1. **前向传播（做题）**：看一道题，按照学过的方法计算，得到答案
2. **反向传播（批改）**：老师批改作业，指出哪里错了、错多少
3. **参数更新**：根据错误，调整自己的解题方法

神经网络学习就是这个循环：前向传播→反向传播→更新参数→再前向传播...

#### 核心概念
**前向传播 (Forward Propagation)**：输入数据从输入层流向输出层，计算预测值。

**反向传播 (Backpropagation)**：根据损失函数，计算每个参数对错误的"责任"，为更新参数提供方向。

**链式法则 (Chain Rule)**：反向传播的数学基础
```
dL/dw = dL/dy * dy/dz * dz/dw
```
就像剥洋葱一样，一层一层往回算梯度。

##### 数学直觉
简单例子：y = w * x + b 的梯度
```
前向：z = w*x + b, y = relu(z)
反向：
- dL/dy：损失对输出的梯度
- dy/dz = relu'(z)：激活函数的梯度
- dz/dw = x：输入
- dL/dw = dL/dy * dy/dz * dz/dw
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn

# 演示前向传播和反向传播
print("=== 前向传播与反向传播 ===\n")

# 创建可求导的张量
x = torch.tensor([1.0, 2.0], requires_grad=True)
w = torch.tensor([0.5, -0.3], requires_grad=True)
b = torch.tensor(0.1, requires_grad=True)

print(f"输入 x: {x}")
print(f"权重 w: {w}")
print(f"偏置 b: {b}")

# 前向传播
z = torch.dot(x, w) + b  # z = sum(x_i * w_i) + b
y = torch.relu(z)        # y = max(0, z)

print(f"\n前向传播:")
print(f"  z = x·w + b = {z.item():.4f}")
print(f"  y = relu(z) = {y.item():.4f}")

# 定义损失（假设真实值是1.0）
y_true = torch.tensor(1.0)
loss = (y - y_true) ** 2

print(f"\n损失: L = (y - y_true)² = {loss.item():.4f}")

# 反向传播
loss.backward()

print(f"\n反向传播 (梯度):")
print(f"  dL/dy = {2 * (y - y_true).item():.4f}")
print(f"  dy/dz = {1.0 if z > 0 else 0.0:.4f}")
print(f"  dz/dw = x = {x.tolist()}")
print(f"  dz/db = 1")
print(f"  dL/dw = dL/dy * dy/dz * dz/dw = {w.grad.tolist()}")
print(f"  dL/db = {b.grad.item():.4f}")

# 完整MLP的前向传播和反向传播
print("\n=== MLP完整示例 ===\n")

class SimpleMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 8)
        self.fc2 = nn.Linear(8, 4)
        self.fc3 = nn.Linear(4, 2)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

model = SimpleMLP()
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# 模拟训练
for epoch in range(3):
    # 前向传播
    X = torch.randn(4, 10)
    y_true = torch.randint(0, 2, (4,))
    
    optimizer.zero_grad()
    y_pred = model(X)
    loss = criterion(y_pred, y_true)
    
    print(f"Epoch {epoch+1} - 训练损失: {loss.item():.4f}")
    
    # 反向传播
    loss.backward()
    
    # 查看梯度
    for name, param in model.named_parameters():
        if param.grad is not None:
            print(f"  {name}: grad norm = {param.grad.norm().item():.4f}")
    
    # 更新参数
    optimizer.step()
    print()

# 梯度检查
print("=== 梯度检查 ===")
x_check = torch.randn(10, requires_grad=True)
w_check = torch.randn(10, requires_grad=True)

# 数值梯度
eps = 1e-5
loss1 = torch.dot(x_check, w_check)
loss1.backward()

numerical_grad = torch.zeros_like(w_check)
for i in range(10):
    w_temp = w_check.data.clone()
    w_temp[i] += eps
    loss_plus = torch.dot(x_check.data, w_temp)
    loss_minus = torch.dot(x_check.data, w_check.data)
    numerical_grad[i] = (loss_plus - loss_minus) / eps

print(f"解析梯度: {w_check.grad}")
print(f"数值梯度: {numerical_grad}")
print(f"两者差异: {(w_check.grad - numerical_grad).abs().max().item():.6f}")
```

#### 常见坑点
- **梯度为None**：忘记设置`requires_grad=True`或忘记`backward()`
- **梯度累积**：没有在每次迭代前`optimizer.zero_grad()`
- **梯度消失/爆炸**：深层网络常见问题，需要BatchNorm或残差连接

---

### 2.4 优化器：下山策略

优化器决定了参数更新的方式和速度，是深度学习训练的关键。

#### 一句话人话
优化器就是"下山策略"——告诉你每次应该迈多大的步子、往哪个方向走。

#### 生活比喻
蒙眼下山，但地形不同：
- **SGD**：每次看看脚下，往最陡方向走
- **Adam**：不仅看脚下，还看历史经验，智能判断最优路径

#### 核心概念
常用优化器：

| 优化器 | 更新规则 | 特点 |
|--------|---------|------|
| SGD | θ = θ - lr * ∇L | 简单，可能震荡 |
| SGD+Momentum | θ = θ - lr * m_t | 加上惯性，冲过局部最优 |
| AdaGrad | 自适应学习率 | 稀疏数据好，但学习率单调递减 |
| RMSprop | 指数衰减平均 | 解决AdaGrad问题 |
| Adam | Momentum + RMSprop | 深度学习默认选择 |

##### 数学直觉
**SGD with Momentum**：
```
v_t = β * v_{t-1} + (1-β) * ∇L
θ = θ - lr * v_t
```
加入动量后，就像有一个"惯性"，不容易被困在局部最优。

**Adam**：
- **动量项 (m_t)**：类似Momentum，累积历史梯度
- **自适应学习率 (v_t)**：对每个参数自适应调整学习率

```
m_t = β₁ * m_{t-1} + (1-β₁) * ∇L  # 梯度的一阶矩估计
v_t = β₂ * v_{t-1} + (1-β₂) * (∇L)²  # 梯度二阶矩估计
m_hat = m_t / (1 - β₁^t)  # 偏差修正
v_hat = v_t / (1 - β₂^t)
θ = θ - lr * m_hat / (√v_hat + ε)
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# 优化器对比
def rosenbrock(x, y):
    """Rosenbrock函数 - 经典的优化测试函数"""
    return (1 - x)**2 + 100 * (y - x**2)**2

def grad_rosenbrock(x, y):
    """Rosenbrock的梯度"""
    dx = -2 * (1 - x) - 400 * x * (y - x**2)
    dy = 200 * (y - x**2)
    return np.array([dx, dy])

# 不同优化器的优化轨迹
def optimize_rosenbrock(optimizer_class, optimizer_params, lr, epochs=500):
    x, y = -1.0, -1.0  # 初始位置
    trajectory = [(x, y)]
    
    if optimizer_class == torch.optim.SGD:
        params = [torch.tensor([x, y], dtype=torch.float32, requires_grad=True)]
        opt = optimizer_class(params, lr=lr, **optimizer_params)
    else:
        params = [torch.tensor([x, y], dtype=torch.float32, requires_grad=True)]
        opt = optimizer_class(params, lr=lr, **optimizer_params)
    
    for _ in range(epochs):
        if optimizer_class == torch.optim.SGD:
            params[0].grad = None
            loss = rosenbrock(params[0][0].item(), params[0][1].item())
            grads = grad_rosenbrock(params[0][0].item(), params[0][1].item())
            params[0].grad = torch.tensor(grads, dtype=torch.float32)
            opt.step()
        else:
            params[0].grad = None
            loss = rosenbrock(params[0][0].item(), params[0][1].item())
            loss.backward()
            opt.step()
        
        trajectory.append((params[0][0].item(), params[0][1].item()))
    
    return np.array(trajectory)

# 准备优化器
optimizers = {
    'SGD': (torch.optim.SGD, {'momentum': 0}),
    'SGD+Momentum': (torch.optim.SGD, {'momentum': 0.9}),
    'Adam': (torch.optim.Adam, {}),
    'RMSprop': (torch.optim.RMSprop, {}),
}

lr = 0.001
epochs = 500

print("=== 优化器对比 ===\n")

# 可视化
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 左图：优化轨迹
x = np.linspace(-2, 2, 100)
y = np.linspace(-1, 3, 100)
X, Y = np.meshgrid(x, y)
Z = rosenbrock(X, Y)

axes[0].contour(X, Y, Z, levels=np.logspace(-1, 3, 20), cmap='viridis')
axes[0].set_xlim(-2, 2)
axes[0].set_ylim(-1, 3)

colors = ['red', 'green', 'blue', 'orange']
for (name, (opt_class, opt_params)), color in zip(optimizers.items(), colors):
    traj = optimize_rosenbrock(opt_class, opt_params, lr, epochs)
    axes[0].plot(traj[:, 0], traj[:, 1], color=color, label=name, alpha=0.8)
    axes[0].scatter(traj[-1, 0], traj[-1, 1], color=color, marker='*', s=100)

axes[0].scatter(1, 1, c='black', marker='x', s=200, label='最优点')
axes[0].set_xlabel('x')
axes[0].set_ylabel('y')
axes[0].set_title('不同优化器的优化轨迹')
axes[0].legend()

# 右图：损失曲线
for (name, (opt_class, opt_params)), color in zip(optimizers.items(), colors):
    traj = optimize_rosenbrock(opt_class, opt_params, lr, epochs)
    losses = [rosenbrock(p[0], p[1]) for p in traj]
    axes[1].plot(losses, color=color, label=name, alpha=0.8)

axes[1].set_xlabel('迭代次数')
axes[1].set_ylabel('损失')
axes[1].set_title('损失曲线对比')
axes[1].legend()
axes[1].set_yscale('log')

plt.tight_layout()
plt.savefig('optimizers.png', dpi=150)

# PyTorch优化器使用示例
print("=== PyTorch优化器使用 ===\n")

model = nn.Sequential(
    nn.Linear(10, 16),
    nn.ReLU(),
    nn.Linear(16, 2)
)

# 不同的优化器
sgd = torch.optim.SGD(model.parameters(), lr=0.1, momentum=0.9)
adam = torch.optim.Adam(model.parameters(), lr=0.001)
rmsprop = torch.optim.RMSprop(model.parameters(), lr=0.01)

print("SGD:      ", sgd)
print("Adam:     ", adam)
print("RMSprop:  ", rmsprop)

# 学习率调度示例
print("\n=== 学习率调度 ===")
scheduler = torch.optim.lr_scheduler.StepLR(adam, step_size=10, gamma=0.5)

for epoch in range(30):
    # 模拟训练
    if epoch % 10 == 0:
        print(f"Epoch {epoch}: 当前学习率 = {scheduler.get_last_lr()[0]:.6f}")
    scheduler.step()

# 不同学习率调度策略
print("\n=== 学习率调度策略 ===")
scheduler_types = {
    'StepLR': torch.optim.lr_scheduler.StepLR,
    'CosineAnnealingLR': torch.optim.lr_scheduler.CosineAnnealingLR,
    'ReduceLROnPlateau': torch.optim.lr_scheduler.ReduceLROnPlateau,
    'OneCycleLR': torch.optim.lr_scheduler.OneCycleLR,
}

for name, scheduler_cls in scheduler_types.items():
    print(f"  - {name}")
```

#### 常见坑点
- **学习率太大**：震荡不收敛
- **学习率太小**：收敛太慢
- **Adam不稳定**：有时不如SGD收敛到更好的解
- **优化器与任务匹配**：大模型常用AdamW

---

### 2.5 BatchNorm与LayerNorm：标准化

归一化技术是深度学习训练稳定性和性能的关键技巧。

#### 一句话人话
归一化就是把数据"标准化"——让不同范围的数据变成可以比较的统一尺度。

#### 生活比喻
不同科目的成绩比较：
- 数学：0-100分
- 百分制：平均分60，标准差10
- 竞赛：0-1000分

直接比较不公平，需要"标准化"到同一尺度，比如"超过了百分之多少的人"。

#### 核心概念
**BatchNorm**：在batch维度上标准化
- 对 batch 内同一特征的所有样本标准化
- 适合 CV 任务，大 batch 效果好

**LayerNorm**：在layer维度上标准化
- 对单个样本的所有特征标准化
- 适合 NLP 任务

**其他归一化**：
- **InstanceNorm**：每个样本、每个通道独立
- **GroupNorm**：通道分组

##### 数学直觉
```
BatchNorm: 对 batch 维度统计
  μ = mean(x, axis=0)        # 批均值
  σ² = var(x, axis=0)       # 批方差
  x_norm = (x - μ) / √(σ² + ε)
  y = γ * x_norm + β        # 可学习的缩放和平移

LayerNorm: 对特征维度统计
  对单个样本 x[i] 标准化
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# 手动实现BatchNorm
class BatchNorm1d(nn.Module):
    def __init__(self, num_features, eps=1e-5, momentum=0.1):
        super().__init__()
        self.eps = eps
        self.momentum = momentum
        
        # 可学习参数
        self.gamma = nn.Parameter(torch.ones(num_features))
        self.beta = nn.Parameter(torch.zeros(num_features))
        
        # 运行时的均值和方差（用于推理）
        self.running_mean = torch.zeros(num_features)
        self.running_var = torch.ones(num_features)
    
    def forward(self, x):
        if self.training:
            # 训练时：计算当前batch的均值和方差
            mean = x.mean(dim=0)
            var = x.var(dim=0, unbiased=False)
            
            # 更新running统计量
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mean
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var
        else:
            # 推理时：使用running统计量
            mean = self.running_mean
            var = self.running_var
        
        # 标准化
        x_norm = (x - mean) / torch.sqrt(var + self.eps)
        
        # 缩放和平移
        return self.gamma * x_norm + self.beta

# 测试BatchNorm vs 无BatchNorm
print("=== BatchNorm vs 无BatchNorm ===\n")

class SimpleNet(nn.Module):
    def __init__(self, use_bn=False):
        super().__init__()
        layers = [nn.Linear(10, 20), nn.ReLU()]
        if use_bn:
            layers.insert(1, nn.BatchNorm1d(20))
        layers.extend([nn.Linear(20, 20), nn.ReLU()])
        if use_bn:
            layers.insert(4, nn.BatchNorm1d(20))
        layers.append(nn.Linear(20, 2))
        self.net = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.net(x)

# 创建模型
net_with_bn = SimpleNet(use_bn=True)
net_without_bn = SimpleNet(use_bn=False)

# 测试梯度流
x = torch.randn(32, 10)
y = torch.randint(0, 2, (32,))

criterion = nn.CrossEntropyLoss()

def test_gradient_flow(net, x, y, name):
    out = net(x)
    loss = criterion(out, y)
    loss.backward()
    
    # 检查各层梯度
    print(f"\n{name}:")
    for i, param in enumerate(net.parameters()):
        grad_norm = param.grad.norm().item() if param.grad is not None else 0
        print(f"  Layer {i}: gradient norm = {grad_norm:.6f}")
    
    # 清零梯度
    net.zero_grad()

test_gradient_flow(net_with_bn, x, y, "有BatchNorm")
test_gradient_flow(net_without_bn, x, y, "无BatchNorm")

# LayerNorm示例
print("\n=== LayerNorm示例 ===\n")

layer_norm = nn.LayerNorm(normalized_shape=[10, 20])

x = torch.randn(5, 10, 20)  # batch=5, seq_len=10, hidden=20
y = layer_norm(x)

print(f"输入形状: {x.shape}")
print(f"输出形状: {y.shape}")
print(f"LayerNorm后均值（沿最后两维）: {y.mean(dim=[-2, -1]).tolist()}")
print(f"LayerNorm后方差（沿最后两维）: {y.var(dim=[-2, -1]).tolist()}")

# BatchNorm vs LayerNorm可视化
print("\n=== 归一化方法对比 ===")
print("BatchNorm: 对batch维度统计，适合CV")
print("LayerNorm: 对特征维度统计，适合NLP")
print("InstanceNorm: 对每个样本、每个通道独立，适合风格迁移")
print("GroupNorm: 通道分组，比BatchNorm对小batch更鲁棒")
```

#### 常见坑点
- **BatchNorm的batch size问题**：小batch下BatchNorm效果差
- **训练/推理模式混淆**：BatchNorm在训练和推理时行为不同
- **位置放错**：通常放在激活函数前面

---

### 2.6 Dropout：随机请假防依赖

Dropout是一种有效的正则化技术，通过随机丢弃神经元来防止过拟合。

#### 一句话人话
Dropout就像让每个员工随机"请假"，迫使团队不能依赖任何一个人。

#### 生活比喻
想象一个项目团队：
- **没有Dropout**：每个员工都参与讨论，容易形成"小圈子"
- **有Dropout**：随机让一些员工"请假"，其他员工必须学会补位

这样训练出来的模型，每个神经元都不会太依赖特定的队友。

#### 核心概念
**Dropout**：训练时随机将部分神经元输出置为0
- 训练时：以概率p丢弃神经元
- 推理时：所有神经元都参与，但输出要乘以(1-p)

##### 数学直觉
```
训练时:
  if random() < p:
      output = 0  # 丢弃
  else:
      output = x / (1-p)  # 缩放，保持期望不变

推理时:
  output = x  # 所有神经元参与，但输出期望相同
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# Dropout实现
class Dropout(nn.Module):
    def __init__(self, p=0.5):
        super().__init__()
        self.p = p
    
    def forward(self, x):
        if self.training:
            # 训练时：随机丢弃
            mask = torch.rand_like(x) > self.p
            return x * mask / (1 - self.p)  # 缩放保持期望
        else:
            # 推理时：所有神经元参与
            return x

# 测试Dropout
print("=== Dropout测试 ===\n")

dropout = nn.Dropout(p=0.5)
x = torch.ones(10)

print(f"原始输入: {x}")

# 训练模式
dropout.train()
out_train = dropout(x)
print(f"训练输出: {out_train}")

# 推理模式
dropout.eval()
out_eval = dropout(x)
print(f"推理输出: {out_eval}")

# 演示Dropout防止过拟合
print("\n=== Dropout防止过拟合示例 ===\n")

class NetWithDropout(nn.Module):
    def __init__(self, dropout_rate=0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),  # Dropout
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),  # Dropout
            nn.Linear(128, 2)
        )
    
    def forward(self, x):
        return self.net(x)

# 训练对比
from sklearn.datasets import make_moons

X, y = make_moons(n_samples=500, noise=0.2, random_state=42)
X = torch.FloatTensor(X)
y = torch.LongTensor(y)

# 模型1：无Dropout
model_no_dropout = nn.Sequential(
    nn.Linear(2, 128), nn.ReLU(),
    nn.Linear(128, 128), nn.ReLU(),
    nn.Linear(128, 2)
)

# 模型2：有Dropout
model_with_dropout = NetWithDropout(dropout_rate=0.3)

# 训练
optimizer1 = torch.optim.Adam(model_no_dropout.parameters(), lr=0.01)
optimizer2 = torch.optim.Adam(model_with_dropout.parameters(), lr=0.01)
criterion = nn.CrossEntropyLoss()

def train_model(model, optimizer, epochs=100):
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        output = model(X)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
    
    # 测试集评估
    model.eval()
    with torch.no_grad():
        output = model(X)
        pred = output.argmax(1)
        acc = (pred == y).float().mean()
    return acc.item()

print(f"无Dropout训练集准确率: {train_model(model_no_dropout, optimizer1):.4f}")
model_no_dropout.eval()
print(f"无Dropout测试集准确率: {train_model(model_no_dropout, optimizer1):.4f}")

print(f"有Dropout训练集准确率: {train_model(model_with_dropout, optimizer2):.4f}")
model_with_dropout.eval()
print(f"有Dropout测试集准确率: {train_model(model_with_dropout, optimizer2):.4f}")

# Dropout的变体
print("\n=== Dropout变体 ===")
print("Standard Dropout: 随机丢弃")
print("Alpha Dropout: 保持均值和方差")
print("Spatial Dropout (2D): 丢弃整个通道")
print("DropPath: 丢弃整个路径（ResNet常用）")

# 手动实现验证Dropout的期望保持
print("\n=== Dropout期望保持验证 ===")
dropout = nn.Dropout(p=0.5)
x = torch.randn(10000, 10)

# 多次采样看期望
outputs = []
for _ in range(100):
    out = dropout(x)
    outputs.append(out.mean().item())

print(f"输入均值: {x.mean().item():.4f}")
print(f"Dropout输出均值: {np.mean(outputs):.4f}")
print(f"期望保持: {'✓' if abs(np.mean(outputs) - x.mean().item()) < 0.1 else '✗'}")
```

#### 常见坑点
- **Dropout只在训练时用**：推理时要关掉（eval模式）
- **学习率调整**：Dropout可能导致需要更大的学习率
- **太高的Dropout率**：可能欠拟合

---

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### ⚠️ 小白易懵点

**BatchNorm vs LayerNorm vs Dropout**

| 技术 | 作用 | 应用场景 |
|------|------|---------|
| BatchNorm | 标准化batch维度 | CV、大batch |
| LayerNorm | 标准化特征维度 | NLP |
| Dropout | 随机丢弃防过拟合 | 通用 |

简单记忆：
- **BatchNorm = 统一尺度**（让batch内的样本可比）
- **LayerNorm = 统一风格**（让单个样本的特征可比）
- **Dropout = 防死记硬背**（让每个神经元都重要）

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结

> 感知机→MLP解决了线性不可分问题；激活函数引入非线性；前向传播是"做题"，反向传播是"批改"；优化器决定下山策略（Adam是目前最常用）；BatchNorm和LayerNorm标准化数据分布；Dropout通过随机丢弃防止过拟合。

---

## 第三篇：NLP基础

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 3.1 文本表示演进：从One-Hot到上下文词向量

文本表示是将文字转换为机器可处理的数字形式，是NLP的基础。

#### 一句话人话
文本表示就是把"文字"变成"数字"，让计算机能处理语言。

#### 生活比喻
想象图书馆的书籍分类：
- **One-Hot**：按大类分，同一类的书放一起
- **TF-IDF**：按重要性分，热门书单独放
- **词向量**：按内容相似度分，相似内容的书放隔壁

#### 核心概念
文本表示的演进：
```
One-Hot → TF-IDF → Word2Vec → 上下文词向量(ELMo/BERT)
```

**One-Hot编码**：每个词一个维度，只有一个位置是1
- 缺点：维度爆炸，无法表达相似性

**TF-IDF**：词频-逆文档频率
- 考虑词在文档中的重要程度

**词嵌入 (Word2Vec)**：将词映射到低维稠密向量
- 相似的词向量接近

**上下文词向量**：同一个词在不同上下文有不同的向量
- 解决多义词问题

##### 数学直觉
**One-Hot**：
```
"猫" = [1, 0, 0, 0, ...]  # 10万个词中的第1个
"狗" = [0, 1, 0, 0, ...]  # 第2个
```
问题：猫和狗都是动物，但向量正交（相似度=0）

**词嵌入**：
```
"猫" = [0.2, 0.8, -0.3, ...]  # 300维向量
"狗" = [0.25, 0.75, -0.28, ...]
相似度 = cos(猫, 狗) ≈ 0.98  # 很相似！
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# 1. One-Hot编码
print("=== One-Hot编码 ===\n")

# 假设词表有5个词
vocab = ['我', '喜欢', '学习', '机器学习', '深度学习']
word_to_id = {word: i for i, word in enumerate(vocab)}

def one_hot(word, vocab_size=5):
    vec = torch.zeros(vocab_size)
    vec[word_to_id[word]] = 1
    return vec

print("词表:", vocab)
print(f"'机器学习'的One-Hot: {one_hot('机器学习')}")
print(f"'深度学习'的One-Hot: {one_hot('深度学习')}")
print(f"相似度: {torch.cosine_similarity(one_hot('机器学习').unsqueeze(0), one_hot('深度学习').unsqueeze(0), dim=1).item():.4f}")
print("(应该相似但One-Hot无法表达！)")

# 2. TF-IDF
print("\n=== TF-IDF示例 ===\n")

from sklearn.feature_extraction.text import TfidfVectorizer

corpus = [
    '机器学习 是 使用数据学习规律',
    '深度学习 是 机器学习 的 一个分支',
    '自然语言处理 使用 深度学习'
]

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(corpus)

print("TF-IDF矩阵形状:", tfidf_matrix.shape)
print("词汇表:", vectorizer.get_feature_names_out())
print("\nTF-IDF矩阵:")
print(tfidf_matrix.toarray())

# 3. Word2Vec (简单演示)
print("\n=== Word2Vec词向量演示 ===\n")

# 使用预训练的GloVe向量（简化版）
# 这里用随机初始化的演示，实际应该用预训练向量
torch.manual_seed(42)

# 创建词向量（假设词表大小100，嵌入维度10）
embedding = nn.Embedding(num_embeddings=100, embedding_dim=10)

# 随机初始化但可学习
words = ['king', 'queen', 'man', 'woman', 'apple', 'orange']
word_ids = torch.randint(0, 100, (len(words),))

vectors = embedding(word_ids).detach().numpy()

print(f"词向量维度: {vectors.shape}")
print(f"\n词向量示例 (前3维):")
for word, vec in zip(words, vectors):
    print(f"  {word}: {vec[:3].round(2)}")

# 4. 上下文词向量演示
print("\n=== 上下文词向量示例 ===")
print("'bank' 在不同上下文的不同含义:")
print("  'bank river' → 河岸")
print("  'bank money' → 银行")
print("传统词向量：同一个向量")
print("上下文词向量：不同上下文不同向量 ✓")
```

#### 常见坑点
- **One-Hot维度爆炸**：大词表导致高维稀疏向量
- **忽略词序**：Bag-of-Words丢失顺序信息
- **多义词问题**：Word2Vec无法处理一词多义

---



### 3.2 词嵌入直觉：多维空间住址

词嵌入将每个词映射到一个稠密的向量空间中，让语义相似的词离得更近。

#### 一句话人话
词嵌入就像给每个词分配一个"住址"，语义相似的词住在隔壁。

#### 生活比喻
想象一个城市：
- **地址（向量）**：每个词有一个多维坐标
- **邻居（相似词）**：语义相近的词地理上接近
- **距离（相似度）**：用距离衡量语义的相近程度

"猫"和"狗"可能是邻居（都是宠物），"猫"和"汽车"可能离得很远。

#### 核心概念
**词嵌入 (Word Embedding)**：将词映射为固定维度的稠密向量

**词的语义关系**：
- **类比关系**：king - man + woman ≈ queen
- **相似关系**：cat 和 dog 向量相似
- **聚类关系**：同类词自然聚集

##### 数学直觉
```
词向量空间：
- dim=300（常用维度）
- 相似度 = cos(向量1, 向量2)
- king - man + woman ≈ queen
  (king向量 - man向量 + woman向量 ≈ queen向量)
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

print("=== 词嵌入直觉演示 ===\n")

# 简单词嵌入
class SimpleWordEmbedding(nn.Module):
    def __init__(self, vocab_size, embed_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
    
    def get_vector(self, word_id):
        return self.embedding(torch.tensor(word_id)).detach().numpy()
    
    def similarity(self, id1, id2):
        v1 = self.embedding(torch.tensor(id1))
        v2 = self.embedding(torch.tensor(id2))
        return torch.cosine_similarity(v1.unsqueeze(0), v2.unsqueeze(0)).item()

# 创建简单词表
word2id = {'the': 0, 'cat': 1, 'dog': 2, 'animal': 3, 'car': 4, 'tree': 5}
embed = SimpleWordEmbedding(vocab_size=6, embed_dim=5)

print("词表和ID映射:", word2id)
print(f"\n词向量维度: {embed.embedding.weight.shape}")

# 显示词向量
print("\n词向量 (前3维):")
for word, idx in word2id.items():
    vec = embed.get_vector(idx)[:3]
    print(f"  {word}: {vec.round(2)}")

# 计算相似度
print("\n词相似度:")
print(f"  cat vs dog: {embed.similarity(1, 2):.4f} (都是动物)")
print(f"  cat vs car: {embed.similarity(1, 4):.4f} (不同类别)")
print(f"  cat vs animal: {embed.similarity(1, 3):.4f} (包含关系)")

# 词类比演示
print("\n=== 词类比演示 ===")
print("king - man + woman ≈ queen")
print("北京 - 中国 + 法国 ≈ 巴黎")

# 简化演示：词向量偏移
print("\n词向量运算示例:")
print("假设 king = [0.8, 0.2, ...], man = [0.7, 0.3, ...]")
print("king - man = [0.1, -0.1, ...] ≈ queen - woman")
```

#### 常见坑点
- **维度选择**：太低表达不足，太高计算量大
- **未登录词**：遇到训练时没见过的词无法处理
- **上下文无关**：Word2Vec不考虑上下文

---

### 3.3 语言模型演进：从N-gram到Transformer

语言模型是NLP的核心，让我们能够理解和生成文本。

#### 一句话人话
语言模型就是预测下一个词的概率分布——给定"今天天气真"，预测下一个词是"好"。

#### 生活比喻
想象补全句子：
- 有人说"今天天气真___"
- 你的大脑会预测"好"、"不错"、"晴朗"
- 语言模型就是用数学方法做同样的事

#### 核心概念
语言模型演进：
```
N-gram → RNN → LSTM → Transformer
```

**N-gram模型**：
- 基于统计：P(好|今天天气真)
- 优点：简单
- 缺点：数据稀疏，泛化差

**RNN (循环神经网络)**：
- 能够处理变长序列
- 缺点：长依赖问题，梯度消失

**LSTM/GRU**：
- 引入门控机制，缓解梯度消失
- 能够学习长距离依赖

**Transformer**：
- 自注意力机制，并行计算
- 当前NLP主流架构

##### 数学直觉
**N-gram**：
```
P(w₁,w₂,...,wₙ) = P(w₁) × P(w₂|w₁) × ... × P(wₙ|w₁,...,wₙ₋₁)
≈ P(wₙ|wₙ₋₁,wₙ₋₂)  # 只看前两个词
```

**RNN前向传播**：
```
h_t = tanh(W_xh·x_t + W_hh·h_{t-1} + b)
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np

print("=== 语言模型演进 ===\n")

# 1. N-gram语言模型（简化版）
print("1. N-gram语言模型")
print("   基于统计的语言模型，计算词序列的概率")

# 2. RNN语言模型
print("\n2. RNN语言模型")
print("   循环结构处理序列，但有长依赖问题")

class RNNLM(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.rnn = nn.RNN(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
    
    def forward(self, x, hidden):
        x = self.embedding(x)
        out, hidden = self.rnn(x, hidden)
        out = self.fc(out)
        return out, hidden

# 3. LSTM语言模型
print("\n3. LSTM语言模型")
print("   引入门控机制，缓解梯度消失")

class LSTMLM(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
    
    def forward(self, x, hidden=None):
        x = self.embedding(x)
        out, hidden = self.lstm(x, hidden)
        out = self.fc(out)
        return out, hidden

# 4. Transformer语言模型（简化版）
print("\n4. Transformer语言模型")
print("   自注意力机制，并行计算，效果最好")

# 对比演示
print("\n=== 模型对比 ===")

vocab_size = 1000
embed_dim = 64
hidden_dim = 128
seq_len = 20
batch_size = 4

rnn_model = RNNLM(vocab_size, embed_dim, hidden_dim)
lstm_model = LSTMLM(vocab_size, embed_dim, hidden_dim)

x = torch.randint(0, vocab_size, (batch_size, seq_len))
h0 = torch.zeros(1, batch_size, hidden_dim)

# RNN前向传播
rnn_out, rnn_h = rnn_model(x, h0)
print(f"RNN输出形状: {rnn_out.shape}")

# LSTM前向传播
lstm_out, (lstm_h, lstm_c) = lstm_model(x)
print(f"LSTM输出形状: {lstm_out.shape}")

# 计算参数量
def count_params(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

print(f"\n模型参数量:")
print(f"  RNN: {count_params(rnn_model):,}")
print(f"  LSTM: {count_params(lstm_model):,}")
print(f"  (LSTM有门控机制，参数量约是RNN的4倍)")
```

#### 常见坑点
- **N-gram的平滑问题**：未见过的n-gram概率为0
- **RNN的梯度消失**：长序列训练困难
- **Transformer的计算量**：自注意力的O(n²)复杂度

---

### 3.4 Seq2Seq：翻译官流程

Seq2Seq是序列到序列模型，用于机器翻译、摘要生成等任务。

#### 一句话人话
Seq2Seq就是"翻译官"：先理解完整句话，再生成翻译结果。

#### 生活比喻
翻译员工作流程：
1. **理解阶段**：读完整个源语言句子
2. **表达阶段**：根据理解的意思，用目标语言表达

Seq2Seq的Encoder-Decoder架构就是这个流程。

#### 核心概念
**Seq2Seq (Sequence-to-Sequence)**：输入序列→输出序列

**Encoder（编码器）**：
- 处理输入序列
- 提取特征
- 生成上下文向量

**Decoder（解码器）**：
- 根据上下文向量
- 自回归生成输出序列

**注意力机制**：
- 让Decoder能"看到"输入的不同部分
- 解决长序列信息丢失问题

##### 数学直觉
```
Encoder:
  h₁, h₂, ..., hₙ = Encoder(x₁, x₂, ..., xₙ)
  c = hₙ  # 最终隐藏状态作为上下文

Decoder:
  y₁ = Decoder(c)
  y₂ = Decoder(c, y₁)
  y₃ = Decoder(c, y₁, y₂)
  ...
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn

print("=== Seq2Seq模型 ===\n")

# 简单的Seq2Seq模型
class Seq2Seq(nn.Module):
    def __init__(self, src_vocab_size, tgt_vocab_size, embed_dim, hidden_dim):
        super().__init__()
        self.src_embedding = nn.Embedding(src_vocab_size, embed_dim)
        self.tgt_embedding = nn.Embedding(tgt_vocab_size, embed_dim)
        self.encoder = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.decoder = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, tgt_vocab_size)
        
        self.hidden_dim = hidden_dim
    
    def forward(self, src, tgt, teacher_forcing_ratio=0.5):
        batch_size = src.size(0)
        tgt_len = tgt.size(1)
        
        # 编码
        src_embed = self.src_embedding(src)
        _, hidden = self.encoder(src_embed)
        
        # 解码
        outputs = []
        decoder_input = tgt[:, 0]  # <sos>
        decoder_hidden = hidden
        
        for t in range(tgt_len):
            decoder_input = self.tgt_embedding(decoder_input)
            decoder_output, decoder_hidden = self.decoder(decoder_input, decoder_hidden)
            prediction = self.fc(decoder_output.squeeze(1))
            outputs.append(prediction)
            
            # Teacher Forcing
            if torch.rand(1).item() < teacher_forcing_ratio:
                decoder_input = tgt[:, t]
            else:
                decoder_input = prediction.argmax(1)
        
        return torch.stack(outputs, dim=1)
    
    def translate(self, src, max_len=20):
        """推理时使用贪心解码"""
        self.eval()
        with torch.no_grad():
            # 编码
            src_embed = self.src_embedding(src)
            _, hidden = self.encoder(src_embed)
            
            # 解码
            results = []
            decoder_input = torch.tensor([[0]])  # <sos>
            decoder_hidden = hidden
            
            for _ in range(max_len):
                decoder_input = self.tgt_embedding(decoder_input)
                decoder_output, decoder_hidden = self.decoder(decoder_input, decoder_hidden)
                prediction = self.fc(decoder_output.squeeze(1))
                next_token = prediction.argmax(1).item()
                
                if next_token == 1:  # <eos>
                    break
                results.append(next_token)
                decoder_input = torch.tensor([[next_token]])
            
            return results

# 演示
vocab_size = 100
embed_dim = 64
hidden_dim = 128

model = Seq2Seq(vocab_size, vocab_size, embed_dim, hidden_dim)

# 模拟数据
src = torch.randint(1, vocab_size, (2, 10))  # batch=2, seq_len=10
tgt = torch.randint(1, vocab_size, (2, 8))    # batch=2, seq_len=8

output = model(src, tgt)
print(f"输入形状: {src.shape}")
print(f"目标形状: {tgt.shape}")
print(f"输出形状: {output.shape}")

# 参数量
params = sum(p.numel() for p in model.parameters())
print(f"\n模型参数量: {params:,}")
```

#### 常见坑点
- **信息瓶颈**：所有信息压缩到一个向量
- **曝光偏差**：训练和推理不一致
- **长序列问题**：需要注意力机制解决

---

### 3.5 注意力机制直觉：聚焦关键词

注意力机制让模型能够"关注"输入中最相关的部分。

#### 一句话人话
注意力机制就像人的注意力——看句子时会更关注关键词，而不是每个词都一样重视。

#### 生活比喻
阅读理解时：
- 问题："小明去哪里了？"
- 答案在文中找："小明今天**去了**学校，然后**去了**图书馆"
- 你的注意力会聚焦在"去"和"学校"、"图书馆"这些词上

注意力机制就是让模型做同样的事。

#### 核心概念
**注意力分数 (Attention Score)**：衡量两个位置的相关性

**注意力权重 (Attention Weight)**：归一化后的注意力分布

**上下文向量 (Context Vector)**：加权求和得到的表示

##### 数学直觉
```
注意力分数: score(q, k) = q · k / √d
注意力权重: α = softmax(score)
上下文向量: c = Σ αᵢ · vᵢ
```

三种注意力类型：
- **Self-Attention**：序列内部注意力
- **Encoder-Decoder Attention**：跨序列注意力
- **Multi-Head Attention**：多个注意力头

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import numpy as np

print("=== 注意力机制演示 ===\n")

# 手动实现Scaled Dot-Product Attention
def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q: query [batch, seq_len, d_k]
    K: key [batch, seq_len, d_k]
    V: value [batch, seq_len, d_v]
    """
    d_k = Q.size(-1)
    
    # 计算注意力分数
    scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(d_k)
    
    # 应用mask（如果有）
    if mask is not None:
        scores = scores.masked_fill(mask == 0, -1e9)
    
    # 归一化得到注意力权重
    attention_weights = F.softmax(scores, dim=-1)
    
    # 加权求和得到输出
    output = torch.matmul(attention_weights, V)
    
    return output, attention_weights

# 示例
batch_size = 1
seq_len = 5
d_model = 8

Q = torch.randn(batch_size, seq_len, d_model)
K = torch.randn(batch_size, seq_len, d_model)
V = torch.randn(batch_size, seq_len, d_model)

output, weights = scaled_dot_product_attention(Q, K, V)

print(f"Q/K/V形状: {Q.shape}")
print(f"注意力输出形状: {output.shape}")
print(f"注意力权重形状: {weights.shape}")

# 可视化注意力权重
print("\n注意力权重矩阵:")
print(weights.squeeze(0).numpy().round(3))

# 可视化
plt.figure(figsize=(8, 6))
plt.imshow(weights.squeeze(0).numpy(), cmap='Blues', aspect='auto')
plt.colorbar()
plt.xlabel('Key位置')
plt.ylabel('Query位置')
plt.title('注意力权重热力图')
plt.savefig('attention_weights.png', dpi=150)

# Multi-Head Attention示例
print("\n=== Multi-Head Attention ===")

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)
    
    def split_heads(self, x):
        # [batch, seq_len, d_model] -> [batch, num_heads, seq_len, d_k]
        batch_size, seq_len, _ = x.size()
        x = x.view(batch_size, seq_len, self.num_heads, self.d_k)
        return x.transpose(1, 2)
    
    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)
        
        # 线性变换并分头
        Q = self.split_heads(self.W_Q(Q))
        K = self.split_heads(self.W_K(K))
        V = self.split_heads(self.W_V(V))
        
        # Scaled Dot-Product Attention
        attn_output, attn_weights = scaled_dot_product_attention(Q, K, V, mask)
        
        # 合并多头
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch_size, -1, self.d_model)
        
        # 最终线性变换
        output = self.W_O(attn_output)
        
        return output, attn_weights

mha = MultiHeadAttention(d_model=64, num_heads=8)
print(f"Multi-Head Attention参数量: {sum(p.numel() for p in mha.parameters()):,}")
```

#### 常见坑点
- **计算复杂度**：O(n²)，长序列计算量大
- **内存消耗**：注意力矩阵存储需要O(n²)空间
- **多头数量选择**：通常8-16个头效果较好

---

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### ⚠️ 小白易懵点

**词嵌入 vs 上下文词向量**

| 特征 | Word2Vec | BERT |
|------|----------|------|
| 向量类型 | 静态 | 动态/上下文相关 |
| 多义词处理 | 不能 | 能 |
| 训练方式 | 无监督 | MLM预训练 |
| 位置编码 | 无 | 有 |

简单记忆：
- **Word2Vec**：一个词一个向量（"bank"永远一样）
- **BERT**：一个词在每个位置不同向量（"bank river" vs "bank money"不同）

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结

> 文本表示经历了从One-Hot到上下文词向量的演进；词嵌入将词映射到语义空间；语言模型从N-gram发展到Transformer；Seq2Seq通过Encoder-Decoder处理变长序列；注意力机制让模型能够聚焦关键信息。

---

## 第四篇：Transformer核心架构

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 4.1 Self-Attention：每个词都在"看"其他所有词

Self-Attention（自注意力）是Transformer的核心，让序列中的每个位置都能关注到其他所有位置。

#### 一句话人话
Self-Attention就是每个词都要看看句子中的其他词，根据相关性决定关注程度。

#### 生活比喻
读一段话时的思考过程：
- 读"它"时，你会想到前面提到的"猫"
- 读"银行"时，你会结合上下文判断是"河岸"还是"金融机构"
- Self-Attention就是这个"结合上下文"的过程

#### 核心概念
**Self-Attention**：Query、Key、Value都来自同一个序列

**核心思想**：
1. 每个词既"问问题"（Query）也"回答问题"（Key/Value）
2. 通过Q和K的匹配度决定关注程度
3. 用注意力权重对V加权求和

##### 数学直觉
```
Q = X · W_Q  # Query：从哪里关注
K = X · W_K  # Key：被关注的内容
V = X · W_V  # Value：实际的语义内容

注意力 = softmax(QK^T / √d_k) · V
```

为什么除以√d_k？
- 点积会随维度增大而变大
- 除以√d_k保持梯度稳定

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt

print("=== Self-Attention详解 ===\n")

def self_attention(Q, K, V, d_k):
    """手动实现Self-Attention"""
    # 1. 计算注意力分数
    scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(d_k)
    
    # 2. 归一化得到注意力权重
    attention_weights = F.softmax(scores, dim=-1)
    
    # 3. 加权求和
    output = torch.matmul(attention_weights, V)
    
    return output, attention_weights

# 示例："The cat sat on the mat"
seq_len = 6
d_model = 8
d_k = d_v = 4

# 模拟词嵌入
torch.manual_seed(42)
X = torch.randn(1, seq_len, d_model)  # [batch=1, seq_len=6, d_model=8]

# 模拟W_Q, W_K, W_V
W_Q = torch.randn(d_model, d_k)
W_K = torch.randn(d_model, d_k)
W_V = torch.randn(d_model, d_v)

# 计算Q, K, V
Q = torch.matmul(X, W_Q)  # [1, 6, 4]
K = torch.matmul(X, W_K)
V = torch.matmul(X, W_V)

# Self-Attention
output, attention_weights = self_attention(Q, K, V, d_k)

print(f"输入X形状: {X.shape}")
print(f"Q/K/V形状: {Q.shape}")
print(f"注意力输出形状: {output.shape}")
print(f"注意力权重形状: {attention_weights.shape}")

# 可视化注意力权重
words = ["The", "cat", "sat", "on", "the", "mat"]
plt.figure(figsize=(10, 8))
plt.imshow(attention_weights.squeeze(0).numpy(), cmap='Blues', aspect='auto')
plt.xticks(range(seq_len), words)
plt.yticks(range(seq_len), words)
plt.xlabel('Key (被关注)')
plt.ylabel('Query (关注者)')
plt.title('Self-Attention权重矩阵')
plt.colorbar()

# 添加数值标注
for i in range(seq_len):
    for j in range(seq_len):
        text = plt.text(j, i, f'{attention_weights[0, i, j].item():.2f}',
                       ha="center", va="center", color="white" if attention_weights[0, i, j] > 0.3 else "black")

plt.savefig('self_attention.png', dpi=150)

print("\n注意力权重解读:")
print("  'The' 更关注 'cat' 和 'mat'")
print("  'cat' 更关注 'sat' 和 'on'")
print("  这体现了词与词之间的语义关联")

# PyTorch内置实现
print("\n=== PyTorch MultiHeadAttention ===")
mha = nn.MultiheadAttention(embed_dim=8, num_heads=4, dropout=0.1)
query = torch.randn(6, 1, 8)  # [seq_len, batch, embed_dim]
key = torch.randn(6, 1, 8)
value = torch.randn(6, 1, 8)

output, attn_weights = mha(query, key, value)
print(f"PyTorch MHA输出形状: {output.shape}")
print(f"MHA注意力权重形状: {attn_weights.shape}")
```

#### 常见坑点
- **Q/K/V维度要匹配**：多头时注意维度分配
- **Mask必要性**：训练时需要mask防止看到未来信息
- **计算量O(n²)**：长序列计算量大

---

### 4.2 Q/K/V详解：查询器、索引卡与内容卡

Q（Query）、K（Key）、V（Value）是Attention的核心三元素。

#### 一句话人话
Q/K/V就像图书馆的检索系统：Q是查询词，K是索引卡，V是书籍内容。

#### 生活比喻
图书馆检索过程：
1. **Query（查询）**：你说"我想看机器学习的书"
2. **Key（索引）**：图书馆查"机器学习"对应哪些书架
3. **Value（内容）**：最终拿到的实际书籍

Attention就是根据Q找到相关的K，然后用K的权重提取V。

#### 核心概念
**Query (Q)**：
- 来自当前位置的"查询请求"
- "我需要什么信息"

**Key (K)**：
- 每个位置的"索引标签"
- "我包含什么信息"

**Value (V)**：
- 每个位置的实际"内容"
- "信息的具体内容"

##### 数学直觉
```
1. Q和K计算相似度：score = Q · K^T
2. 归一化：attention = softmax(score / √d_k)
3. 加权求和：output = attention · V
```

Q和K的点积衡量相关性：
- Q·K大 → 相关性强 → 关注多
- Q·K小 → 相关性弱 → 关注少

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import matplotlib.pyplot as plt
import numpy as np

print("=== Q/K/V详解 ===\n")

class QKVExplanation(nn.Module):
    def __init__(self, d_model, d_k):
        super().__init__()
        self.W_Q = nn.Linear(d_model, d_k)
        self.W_K = nn.Linear(d_model, d_k)
        self.W_V = nn.Linear(d_model, d_k)
    
    def forward(self, X):
        Q = self.W_Q(X)
        K = self.W_K(X)
        V = self.W_V(X)
        return Q, K, V

# 演示：分析"The cat sat on the mat"
d_model = 8
d_k = 4
seq_len = 6

torch.manual_seed(123)
X = torch.randn(1, seq_len, d_model)

qkv = QKVExplanation(d_model, d_k)
Q, K, V = qkv(X)

words = ["The", "cat", "sat", "on", "the", "mat"]

print("=== Query分析 ===")
print("Q表示'当前位置想知道什么'")
for i, word in enumerate(words):
    print(f"  '{word}'的Q: {Q[0, i].numpy().round(2)}")

print("\n=== Key分析 ===")
print("K表示'当前位置有什么特征'")
for i, word in enumerate(words):
    print(f"  '{word}'的K: {K[0, i].numpy().round(2)}")

print("\n=== Value分析 ===")
print("V表示'当前位置的实际内容'")
for i, word in enumerate(words):
    print(f"  '{word}'的V: {V[0, i].numpy().round(2)}")

# Q-K匹配度可视化
print("\n=== Q-K匹配度矩阵 ===")
scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(d_k)
scores_np = scores.squeeze(0).numpy()

print("分数矩阵（越大越相关）:")
for i, row in enumerate(scores_np):
    print(f"  {words[i]}: {row.round(2)}")

# 可视化
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Q可视化
axes[0].imshow(Q.squeeze(0).numpy().T, cmap='RdYlBu_r', aspect='auto')
axes[0].set_title('Query矩阵 Q')
axes[0].set_yticks([])
axes[0].set_xticks(range(len(words)))
axes[0].set_xticklabels(words, rotation=45)

# K可视化
axes[1].imshow(K.squeeze(0).numpy().T, cmap='RdYlBu_r', aspect='auto')
axes[1].set_title('Key矩阵 K')
axes[1].set_yticks([])
axes[1].set_xticks(range(len(words)))
axes[1].set_xticklabels(words, rotation=45)

# Q-K分数
axes[2].imshow(scores.squeeze(0).numpy(), cmap='Blues', aspect='auto')
axes[2].set_title('Q·K^T 匹配度分数')
axes[2].set_yticks(range(len(words)))
axes[2].set_xticks(range(len(words)))
axes[2].set_xticklabels(words, rotation=45)
axes[2].set_yticklabels(words)

plt.tight_layout()
plt.savefig('qkv_analysis.png', dpi=150)

# 实战：翻译场景中的QKV
print("\n=== 翻译场景示例 ===")
print("源语言: 'The cat'")
print("目标语言: '猫'")
print("\n在生成'猫'时：")
print("  Q = '猫'的查询向量")
print("  K = 'The', 'cat'的索引向量")
print("  V = 'The', 'cat'的内容向量")
print("  注意力会更多关注'cat'（因为语义更相关）")
```

#### 常见坑点
- **Q和K的维度要匹配**：才能做点积
- **V的维度可以不同**：但通常和K保持一致
- **Q≠K的场景**：Cross-Attention中Q来自Decoder，K/V来自Encoder

---

### 4.3 多头注意力：多个审稿人各看各的角度

Multi-Head Attention让模型能够同时关注不同类型的关系。

#### 一句话人话
多头注意力就像多个审稿人同时审稿，每人负责一个角度，最终综合所有意见。

#### 生活比喻
审稿论文时：
- **审稿人1（学术角度）**：关注创新性
- **审稿人2（实验角度）**：关注实验设计
- **审稿人3（写作角度）**：关注表述清晰度

每个审稿人给出不同维度的意见，综合后决定是否录用。

Multi-Head Attention就是这个原理，每个头关注不同的关系模式。

#### 核心概念
**Multi-Head Attention**：
- 将Q/K/V分成多个头
- 每个头独立计算注意力
- 最后拼接并线性变换

**头数设计**：
- 常用头数：8、12、16
- 每个头维度：d_k = d_model / num_heads
- 头数增加可以捕获更丰富的模式

##### 数学直觉
```
MultiHead(Q, K, V) = Concat(head₁, ..., headₕ) · W_O

where headᵢ = Attention(Q·W_Qᵢ, K·W_Kᵢ, V·W_Vᵢ)
```

每个头学习不同的注意力模式：
- 头1可能关注语法关系
- 头2可能关注语义相似
- 头3可能关注位置关系

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np

print("=== 多头注意力详解 ===\n")

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # 线性变换
        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)
    
    def split_heads(self, x):
        """将维度拆分为多头"""
        batch_size, seq_len, _ = x.size()
        x = x.view(batch_size, seq_len, self.num_heads, self.d_k)
        return x.permute(0, 2, 1, 3)  # [batch, heads, seq_len, d_k]
    
    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)
        
        # 线性变换并分头
        Q = self.split_heads(self.W_Q(Q))
        K = self.split_heads(self.W_K(K))
        V = self.split_heads(self.W_V(V))
        
        # 计算注意力（需要转置K）
        scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        attention_weights = torch.softmax(scores, dim=-1)
        
        # 加权求和
        attn_output = torch.matmul(attention_weights, V)
        
        # 合并多头
        attn_output = attn_output.permute(0, 2, 1, 3).contiguous()
        attn_output = attn_output.view(batch_size, -1, self.d_model)
        
        # 最终线性变换
        output = self.W_O(attn_output)
        
        return output, attention_weights

# 演示
d_model = 8
num_heads = 4
seq_len = 6
batch_size = 1

mha = MultiHeadAttention(d_model, num_heads)

# 输入
X = torch.randn(batch_size, seq_len, d_model)

# 前向传播
output, weights = mha(X, X, X)

print(f"输入形状: {X.shape}")
print(f"输出形状: {output.shape}")
print(f"注意力权重形状: {weights.shape}")  # [batch, heads, seq_len, seq_len]

# 可视化每个头的注意力
words = ["The", "cat", "sat", "on", "the", "mat"]
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes = axes.flatten()

for head_idx in range(num_heads):
    ax = axes[head_idx]
    head_weights = weights[0, head_idx].numpy()
    
    im = ax.imshow(head_weights, cmap='Blues', aspect='auto')
    ax.set_title(f'Head {head_idx + 1}', fontsize=12)
    ax.set_xticks(range(len(words)))
    ax.set_yticks(range(len(words)))
    ax.set_xticklabels(words, rotation=45)
    ax.set_yticklabels(words)
    
    plt.colorbar(im, ax=ax)

plt.suptitle('Multi-Head Attention: 4个头的注意力模式', fontsize=14)
plt.tight_layout()
plt.savefig('multi_head_attention.png', dpi=150)

# 分析不同头的特点
print("\n=== 不同头的注意力模式分析 ===")
print("Head 1: 可能更关注位置接近的词（如'sat'关注'the'）")
print("Head 2: 可能更关注语义相关的词（如'cat'关注'mat'）")
print("Head 3: 可能更关注语法关系")
print("Head 4: 可能捕捉其他模式")

# PyTorch内置实现
print("\n=== PyTorch nn.MultiheadAttention ===")
mha_torch = nn.MultiheadAttention(embed_dim=512, num_heads=8, dropout=0.1)
print(mha_torch)
```

#### 常见坑点
- **头数过多**：参数量增加，可能过拟合
- **头数过少**：捕获的模式可能不够丰富
- **维度不整除**：d_model必须能被num_heads整除

---



### 4.4 位置编码：给每个词发座位号

位置编码让Transformer能够感知词的顺序信息。

#### 一句话人话
Self-Attention本身不区分词的位置，位置编码就是给每个词发一个"座位号"。

#### 生活比喻
班级点名：
- 没有座位号：只知道"张三"、"李四"，但不知道谁坐哪
- 有座位号：知道张三坐第1排第3个，李四坐第2排第5个

Attention虽然能计算词之间的关系，但没有位置信息就像点名没有座位号。

#### 核心概念
**位置编码 (Positional Encoding)**：为序列中的每个位置分配一个独特的向量

**两种位置编码**：
1. **绝对位置编码**：每个位置有固定向量
2. **相对位置编码**：关注词之间的相对距离

**常见方法**：
- **正弦/余弦位置编码**（Transformer原版）
- **可学习位置编码**（BERT等使用）
- **RoPE（旋转位置编码）**：LLM常用
- **ALiBi**：新兴方法

##### 数学直觉
**正弦位置编码**：
```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

**RoPE旋转编码**：
```
q' = R(θ, m) · q  # 旋转Query
k' = R(θ, m) · k  # 旋转Key
Attention = (q'·k') / √d
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

print("=== 位置编码详解 ===\n")

# 1. 正弦位置编码 (Sinusoidal PE)
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        
        # 创建位置编码矩阵
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        
        # 频率参数
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model)
        )
        
        # 正弦余弦交替
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0)  # [1, max_len, d_model]
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        """x: [batch, seq_len, d_model]"""
        return x + self.pe[:, :x.size(1), :]

# 2. 可学习位置编码
class LearnablePositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        self.position_embedding = nn.Embedding(max_len, d_model)
    
    def forward(self, x):
        """x: [batch, seq_len, d_model]"""
        batch_size, seq_len, _ = x.size()
        position_ids = torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        return x + self.position_embedding(position_ids)

# 演示
d_model = 16  # 为了可视化方便用较小维度
max_len = 100

sin_pe = PositionalEncoding(d_model, max_len)
learn_pe = LearnablePositionalEncoding(d_model, max_len)

# 可视化位置编码
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 正弦位置编码热力图
pe_matrix = sin_pe.pe[0].numpy()
im1 = axes[0, 0].imshow(pe_matrix.T, cmap='RdBu_r', aspect='auto')
axes[0, 0].set_title('正弦位置编码 (Sinusoidal PE)')
axes[0, 0].set_xlabel('位置 (Position)')
axes[0, 0].set_ylabel('维度 (Dimension)')
plt.colorbar(im1, ax=axes[0, 0])

# 正弦位置编码曲线
axes[0, 1].plot(pe_matrix[0], label='位置0')
axes[0, 1].plot(pe_matrix[10], label='位置10')
axes[0, 1].plot(pe_matrix[50], label='位置50')
axes[0, 1].set_title('正弦位置编码 (不同位置)')
axes[0, 1].set_xlabel('维度')
axes[0, 1].set_ylabel('值')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# 可学习位置编码热力图
learn_pe_matrix = learn_pe.position_embedding.weight.detach().numpy()[:max_len]
im2 = axes[1, 0].imshow(learn_pe_matrix.T, cmap='RdBu_r', aspect='auto')
axes[1, 0].set_title('可学习位置编码 (Learnable PE)')
axes[1, 0].set_xlabel('位置 (Position)')
axes[1, 0].set_ylabel('维度 (Dimension)')
plt.colorbar(im2, ax=axes[1, 0])

# 位置编码的周期性
axes[1, 1].plot(pe_matrix[:, 0], label='维度0 (sin)')
axes[1, 1].plot(pe_matrix[:, 1], label='维度1 (cos)')
axes[1, 1].plot(pe_matrix[:, 2], label='维度2 (sin)')
axes[1, 1].set_title('正弦编码的周期性')
axes[1, 1].set_xlabel('位置')
axes[1, 1].set_ylabel('值')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('positional_encoding.png', dpi=150)

# 测试位置编码
print("=== 位置编码测试 ===\n")

seq_len = 20
d_model = 64
batch_size = 2

x = torch.randn(batch_size, seq_len, d_model)

# 正弦位置编码
sin_pe = PositionalEncoding(d_model)
x_with_sin_pe = sin_pe(x)

print(f"输入形状: {x.shape}")
print(f"加位置编码后: {x_with_sin_pe.shape}")
print(f"位置编码范围: [{sin_pe.pe.min():.4f}, {sin_pe.pe.max():.4f}]")

# RoPE (Rotary Position Embedding) 简介
print("\n=== RoPE (旋转位置编码) ===")
print("RoPE通过旋转Query和Key来实现位置编码")
print("优势：可以处理任意长度的序列（理论上）")
print("代表模型：LLaMA, ChatGLM, Qwen等")

# 简单RoPE演示
def rotate_half(x):
    """旋转一半维度"""
    x1, x2 = x[..., :x.shape[-1]//2], x[..., x.shape[-1]//2:]
    return torch.cat([-x2, x1], dim=-1)

def apply_rotary_pos_emb(q, k, cos, sin):
    """应用RoPE"""
    return (q * cos) + (rotate_half(q) * sin), (k * cos) + (rotate_half(k) * sin)

print("\nRoPE数学原理:")
print("q' = q * cos(θ) + rotate_half(q) * sin(θ)")
print("k' = k * cos(θ) + rotate_half(k) * sin(θ)")
```

#### 常见坑点
- **位置编码维度要匹配**：d_model必须一致
- **序列长度超限**：超过max_len需要调整
- **RoPE的旋转角度**：需要预计算cos/sin值

---

### 4.5 前馈网络(FFN)：消化吸收环节

FFN是Transformer中每个注意力层后面的前馈神经网络。

#### 一句话人话
FFN就像人的"消化系统"——Attention负责"吃"，FFN负责"消化吸收"。

#### 生活比喻
消化食物的过程：
- Attention：把各种食材（信息）都尝一遍，知道味道
- FFN：把食材真正消化成营养（提取更抽象的特征）

两者配合，才能真正"吸收"信息。

#### 核心概念
**FFN (Feed-Forward Network)**：
```
FFN(x) = max(0, x·W₁ + b₁)·W₂ + b₂
       = ReLU(Linear(x))·Linear
```

**FFN的作用**：
- 引入非线性变换
- 增加模型的表达能力
- 对注意力输出进行"二次加工"

**FFN设计**：
- 内维度通常是输入的4倍（d_ff = 4 * d_model）
- 两层全连接 + ReLU激活

##### 数学直觉
```
输入: [batch, seq_len, d_model]
     ↓ Linear(d_model → d_ff)
中间: [batch, seq_len, d_ff]
     ↓ ReLU
     ↓ Linear(d_ff → d_model)
输出: [batch, seq_len, d_model]
```

FFN可以看作两个"1x1卷积"：
- 第一个卷积：扩展维度
- 第二个卷积：压缩回原维度

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn

print("=== 前馈网络(FFN)详解 ===\n")

# 标准FFN实现
class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.ReLU()  # 或GELU
    
    def forward(self, x):
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear2(x)
        return x

# GELU版本的FFN（GPT-2, BERT等使用）
class GELUFeedForward(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.GELU()
    
    def forward(self, x):
        x = self.linear1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.linear2(x)
        return x

# 演示
d_model = 64
d_ff = 256  # 通常是d_model的4倍
seq_len = 20
batch_size = 2

ffn = FeedForward(d_model, d_ff)
ffn_gelu = GELUFeedForward(d_model, d_ff)

x = torch.randn(batch_size, seq_len, d_model)

output_relu = ffn(x)
output_gelu = ffn_gelu(x)

print(f"输入形状: {x.shape}")
print(f"FFN输出形状 (ReLU): {output_relu.shape}")
print(f"FFN输出形状 (GELU): {output_gelu.shape}")

# 参数量分析
params_1 = sum(p.numel() for p in ffn.parameters())
print(f"\nFFN参数量: {params_1:,}")
print(f"  Linear1: {ffn.linear1.weight.numel():,} 参数")
print(f"  Linear2: {ffn.linear2.weight.numel():,} 参数")
print(f"FFN占总参数比例约: {params_1 / (d_model * d_model * 12):.1%}")

# FFN和Attention的对比
print("\n=== FFN vs Attention ===")
print("FFN: 逐位置变换，不考虑其他位置")
print("      公式: FFN(x) = W₂·ReLU(W₁·x)")
print("      作用: 特征的'深度非线性变换'")
print()
print("Attention: 位置之间交互，考虑全局关系")
print("           公式: Attn(Q,K,V) = softmax(QK^T/√d)·V")
print("           作用: 建模'词与词之间的关系'")

# SwiGLU FFN（现代LLM常用）
print("\n=== SwiGLU FFN (LLaMA等使用) ===")

class SwiGLUFFN(nn.Module):
    """SwiGLU = SiLU(x) * Gate(x)"""
    def __init__(self, d_model, d_ff):
        super().__init__()
        self.w1 = nn.Linear(d_model, d_ff, bias=False)  # Swish线性变换
        self.w2 = nn.Linear(d_ff, d_model, bias=False)  # 输出
        self.w3 = nn.Linear(d_model, d_ff, bias=False)  # Gate线性变换
    
    def forward(self, x):
        return self.w2(nn.functional.silu(self.w1(x)) * self.w3(x))

swiglu_ffn = SwiGLUFFN(d_model, d_ff)
params_swiglu = sum(p.numel() for p in swiglu_ffn.parameters())
print(f"SwiGLU参数量: {params_swiglu:,} (比标准FFN多一组W3)")

output_swiglu = swiglu_ffn(x)
print(f"SwiGLU输出形状: {output_swiglu.shape}")
```

#### 常见坑点
- **FFN维度比例**：通常d_ff=4*d_model，比例太小表达能力不足
- **激活函数选择**：GELU通常比ReLU效果好
- **SwiGLU的参数**：需要3个线性层，参数量略大

---

### 4.6 残差连接+LayerNorm：保底通道与标准化

残差连接和LayerNorm是Transformer训练稳定性的关键。

#### 一句话人话
残差连接是"保命通道"——信息可以直接传过去不经过复杂变换；LayerNorm是"标准化"——让数据分布更稳定。

#### 生活比喻
组织架构中的"直通通道"：
- 正常流程：员工→组长→主管→经理（一级级传）
- 残差连接：员工可以直接给经理发消息（Shortcut）

这样即使中间某个层级出问题，信息也能传过去。

#### 核心概念
**残差连接 (Residual Connection)**：
```
output = LayerNorm(x + SubLayer(x))
```
- 让梯度直接流过，缓解梯度消失
- 让模型学习"残差"而非完整映射

**LayerNorm**：
```
μ = mean(x), σ² = var(x)
x_norm = (x - μ) / √(σ² + ε)
y = γ * x_norm + β
```

##### 数学直觉
**残差的作用**：
```
假设目标映射: H(x) = 5x
传统网络需要学习: F(x) = 5x
残差网络只需学习: F(x) = 5x - x = 4x (更容易)
```

**Transformer中的残差**：
```
LayerNorm(x + Attention(x))
LayerNorm(x + FFN(x))
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn

print("=== 残差连接与LayerNorm ===\n")

# Transformer Encoder Layer
class TransformerEncoderLayer(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(d_model, num_heads, dropout=dropout)
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        # 残差连接 + Self-Attention
        attn_output, _ = self.self_attn(x, x, x, attn_mask=mask)
        x = self.norm1(x + self.dropout1(attn_output))
        
        # 残差连接 + FFN
        ffn_output = self.ffn(x)
        x = self.norm2(x + self.dropout2(ffn_output))
        
        return x

# 演示残差连接的作用
print("=== 残差连接的作用 ===\n")

class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(10, 20)
        self.layer2 = nn.Linear(20, 10)
    
    def forward(self, x):
        return self.layer2(torch.relu(self.layer1(x)))

class ResidualNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(10, 20)
        self.layer2 = nn.Linear(20, 10)
    
    def forward(self, x):
        identity = x
        out = self.layer2(torch.relu(self.layer1(x)))
        return out + identity  # 残差连接

# 测试梯度流
simple_net = SimpleNet()
residual_net = ResidualNet()

x = torch.randn(5, 10)
y = torch.randn(5, 10)

# 简单网络
simple_net.zero_grad()
out1 = simple_net(x)
loss1 = nn.MSELoss()(out1, y)
loss1.backward()
grads1 = [p.grad.abs().mean().item() for p in simple_net.parameters() if p.grad is not None]

# 残差网络
residual_net.zero_grad()
out2 = residual_net(x)
loss2 = nn.MSELoss()(out2, y)
loss2.backward()
grads2 = [p.grad.abs().mean().item() for p in residual_net.parameters() if p.grad is not None]

print("梯度流对比（越大约等于梯度消失越轻）:")
print(f"  简单网络: {grads1}")
print(f"  残差网络: {grads2}")

# LayerNorm详解
print("\n=== LayerNorm详解 ===\n")

batch_size = 4
seq_len = 10
d_model = 8

ln = nn.LayerNorm([d_model])
x = torch.randn(batch_size, seq_len, d_model)

y = ln(x)

print(f"输入形状: {x.shape}")
print(f"LayerNorm参数: gamma={ln.weight.shape}, beta={ln.bias.shape}")
print(f"输出形状: {y.shape}")

# LayerNorm的均值和方差
print(f"\nLayerNorm后沿特征维度的统计量:")
print(f"  均值（每个样本）: {y.mean(dim=-1).tolist()}")
print(f"  方差（每个样本）: {y.var(dim=-1).tolist()}")

# Pre-LN vs Post-LN
print("\n=== Pre-LN vs Post-LN ===")
print("Post-LN (原版): LayerNorm在残差之后")
print("  output = LayerNorm(x + Sublayer(x))")
print()
print("Pre-LN: LayerNorm在残差之前")
print("  output = x + Sublayer(LayerNorm(x))")
print("  优点：训练更稳定，梯度更平滑")

class PreLNLayer(nn.Module):
    """Pre-LayerNorm"""
    def __init__(self, d_model):
        super().__init__()
        self.norm = nn.LayerNorm(d_model)
        self.linear = nn.Linear(d_model, d_model)
    
    def forward(self, x):
        x_norm = self.norm(x)
        out = self.linear(x_norm)
        return x + out  # 残差连接在Norm之后

preln = PreLNLayer(d_model)
x = torch.randn(batch_size, seq_len, d_model)
out = preln(x)

print(f"\nPre-LN输出: {out.shape}")
print("梯度对比: Pre-LN的梯度更稳定")
```

#### 常见坑点
- **残差连接的维度**：输入输出维度必须一致
- **LayerNorm位置**：Post-LN训练不稳定，Pre-LN更稳定
- **顺序不能错**：先残差相加，再LayerNorm

---

### 4.7 三种架构对比：阅读+作文 vs 只写作家 vs 只读评论家

Transformer有三种主要架构变体：Encoder-Decoder、Decoder-only、Encoder-only。

#### 一句话人话
三种架构就像三种职业：
- Encoder-Decoder：翻译官（阅读理解+写作）
- Decoder-only：作家（只负责写作）
- Encoder-only：评论家（只负责阅读理解）

#### 生活比喻
写论文的过程：
- **Encoder-only (BERT)**：读完文献，写摘要
- **Decoder-only (GPT)**：根据摘要，扩写成论文
- **Encoder-Decoder (T5)**：读完文献，理解后重写

#### 核心概念
**Encoder-Decoder（完整翻译）**：
- Encoder：理解输入
- Decoder：生成输出
- 代表：T5, BART, 原版Transformer

**Decoder-only（只生成）**：
- 只有Decoder
- 自回归生成
- 代表：GPT系列, LLaMA, ChatGLM

**Encoder-only（只理解）**：
- 只有Encoder
- 双向注意力
- 代表：BERT, RoBERTa

##### 数学直觉
```
Encoder: Bidirectional Attention (看全部)
  每个位置可以看到所有其他位置

Decoder: Masked Attention (只看过去)
  每个位置只能看到自己和之前的词

Cross Attention: Query来自Decoder，K/V来自Encoder
```

| 架构 | 注意力 | 任务 | 代表模型 |
|------|--------|------|---------|
| Encoder-Decoder | 双向+单向 | 翻译、摘要 | T5, BART |
| Decoder-only | 单向 | 对话、代码 | GPT, LLaMA |
| Encoder-only | 双向 | 分类、NER | BERT, RoBERTa |

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn

print("=== 三种Transformer架构对比 ===\n")

# 1. Encoder-Only (BERT风格)
class EncoderOnly(nn.Module):
    """双向注意力，可以看到所有位置"""
    def __init__(self, vocab_size, d_model, num_layers, num_heads):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Parameter(torch.randn(1, 512, d_model))
        self.layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model, num_heads, dim_feedforward=d_model*4, batch_first=True)
            for _ in range(num_layers)
        ])
        self.classifier = nn.Linear(d_model, 2)
    
    def forward(self, x):
        x = self.embedding(x) + self.pos_encoding[:, :x.size(1), :]
        for layer in self.layers:
            x = layer(x)
        # 使用[CLS] token的表示做分类
        return self.classifier(x[:, 0, :])

# 2. Decoder-Only (GPT风格)
class DecoderOnly(nn.Module):
    """单向注意力，只能看到当前位置和之前的位置"""
    def __init__(self, vocab_size, d_model, num_layers, num_heads):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Parameter(torch.randn(1, 512, d_model))
        self.layers = nn.ModuleList([
            nn.TransformerDecoderLayer(d_model, num_heads, dim_feedforward=d_model*4, batch_first=True)
            for _ in range(num_layers)
        ])
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
    
    def forward(self, x):
        # 创建mask，防止看到未来位置
        seq_len = x.size(1)
        mask = nn.Transformer.generate_square_subsequent_mask(seq_len).to(x.device)
        
        x = self.embedding(x) + self.pos_encoding[:, :x.size(1), :]
        for layer in self.layers:
            x = layer(x, x, tgt_mask=mask)
        return self.lm_head(x)
    
    def generate(self, x, max_len=50):
        """自回归生成"""
        self.eval()
        for _ in range(max_len):
            logits = self.forward(x)
            next_token = logits[:, -1, :].argmax(dim=-1, keepdim=True)
            x = torch.cat([x, next_token], dim=1)
            if next_token.item() == 2:  # EOS token
                break
        return x

# 3. Encoder-Decoder (T5风格)
class EncoderDecoder(nn.Module):
    """Encoder理解输入，Decoder生成输出"""
    def __init__(self, vocab_size, d_model, num_layers, num_heads):
        super().__init__()
        self.encoder_embedding = nn.Embedding(vocab_size, d_model)
        self.decoder_embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoding = nn.Parameter(torch.randn(1, 512, d_model))
        
        encoder_layer = nn.TransformerEncoderLayer(d_model, num_heads, dim_feedforward=d_model*4, batch_first=True)
        decoder_layer = nn.TransformerDecoderLayer(d_model, num_heads, dim_feedforward=d_model*4, batch_first=True)
        
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers)
        self.lm_head = nn.Linear(d_model, vocab_size)
    
    def forward(self, src, tgt):
        src_emb = self.encoder_embedding(src) + self.pos_encoding[:, :src.size(1), :]
        tgt_emb = self.decoder_embedding(tgt) + self.pos_encoding[:, :tgt.size(1), :]
        
        memory = self.encoder(src_emb)
        
        seq_len = tgt.size(1)
        tgt_mask = nn.Transformer.generate_square_subsequent_mask(seq_len).to(tgt.device)
        
        output = self.decoder(tgt_emb, memory, tgt_mask=tgt_mask)
        return self.lm_head(output)

# 对比演示
vocab_size = 1000
d_model = 64
num_layers = 2
num_heads = 4

encoder_only = EncoderOnly(vocab_size, d_model, num_layers, num_heads)
decoder_only = DecoderOnly(vocab_size, d_model, num_layers, num_heads)
enc_dec = EncoderDecoder(vocab_size, d_model, num_layers, num_heads)

# 测试输入
batch_size = 2
seq_len = 10

src = torch.randint(0, vocab_size, (batch_size, seq_len))
tgt = torch.randint(0, vocab_size, (batch_size, 5))

print("=== 架构对比 ===\n")

# Encoder-Only
encoder_only.eval()
with torch.no_grad():
    out_enc = encoder_only(src)
print(f"Encoder-Only:")
print(f"  输入: {src.shape}, 输出: {out_enc.shape}")
print(f"  用途: 文本分类、NER、情感分析")
print(f"  注意力: 双向（可以看到全部）")

# Decoder-Only
decoder_only.eval()
with torch.no_grad():
    out_dec = decoder_only(src)
print(f"\nDecoder-Only:")
print(f"  输入: {src.shape}, 输出: {out_dec.shape}")
print(f"  用途: 对话生成、代码生成、文本补全")
print(f"  注意力: 单向（只能看到过去）")

# Encoder-Decoder
enc_dec.eval()
with torch.no_grad():
    out_enc_dec = enc_dec(src, tgt)
print(f"\nEncoder-Decoder:")
print(f"  源输入: {src.shape}, 目标输入: {tgt.shape}, 输出: {out_enc_dec.shape}")
print(f"  用途: 机器翻译、文本摘要、问答")
print(f"  注意力: Encoder双向 + Decoder单向 + Cross Attention")

# 参数量对比
def count_params(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

print(f"\n参数量对比:")
print(f"  Encoder-Only: {count_params(encoder_only):,}")
print(f"  Decoder-Only: {count_params(decoder_only):,}")
print(f"  Encoder-Decoder: {count_params(enc_dec):,}")
```

#### 常见坑点
- **任务匹配**：不同架构适合不同任务
- **生成方式**：Decoder-only和Enc-Dec是自回归生成
- **注意力mask**：Decoder必须mask未来位置

---

### 4.8 Masked Attention：考试不能偷看后面答案

Masked Attention确保模型在预测时只能看到当前位置及之前的内容。

#### 一句话人话
Masked Attention就像闭卷考试——你只能根据前面的信息答题，不能偷看后面的答案。

#### 生活比喻
高考语文作文：
- 题目要求根据材料写作文
- 你必须根据已给材料（Encoder信息）来写
- 写的时候只能看自己写过的内容，不能偷看后面的内容

这就是为什么Decoder要用Masked Attention。

#### 核心概念
**Masked Attention (Causal Attention)**：
- 将当前位置之后的信息mask掉
- 预测第i个词时，只能用第1到第i个词的信息

**Padding Mask**：
- 处理变长序列
- 将padding位置mask掉

**注意力Mask类型**：
- **Causal Mask**：防止看到未来
- **Padding Mask**：忽略padding
- **Cross Mask**：Encoder输出中需要忽略的部分

##### 数学直觉
```
原始注意力:
  attention[i,j] = softmax(Q[i]·K[j])  # i可以看到所有j

Masked注意力:
  attention[i,j] = 0 if j > i else softmax(Q[i]·K[j])
  # i只能看到j <= i
```

Mask矩阵：
```
     j=0  j=1  j=2  j=3  j=4
i=0  1    0    0    0    0
i=1  1    1    0    0    0
i=2  1    1    1    0    0
i=3  1    1    1    1    0
i=4  1    1    1    1    1
(1=可以看到, 0=被mask掉)
```

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)
```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

print("=== Masked Attention详解 ===\n")

# 创建Causal Mask
def create_causal_mask(seq_len, device='cpu'):
    """创建下三角mask矩阵"""
    mask = torch.tril(torch.ones(seq_len, seq_len, device=device))
    return mask

# 创建Padding Mask
def create_padding_mask(seq, pad_idx=0):
    """创建padding位置的mask"""
    return seq != pad_idx

# 可视化Mask
seq_len = 10
causal_mask = create_causal_mask(seq_len).numpy()

plt.figure(figsize=(8, 6))
plt.imshow(causal_mask, cmap='Blues', aspect='auto')
plt.colorbar(label='Mask (1=可见, 0=不可见)')
plt.xlabel('Key位置 (j)')
plt.ylabel('Query位置 (i)')
plt.title('Causal Mask (下三角矩阵)')
plt.savefig('causal_mask.png', dpi=150)

# 手动实现Masked Self-Attention
class MaskedSelfAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)
    
    def forward(self, x, mask=None):
        batch_size, seq_len, _ = x.size()
        
        # Q, K, V
        Q = self.W_Q(x)
        K = self.W_K(x)
        V = self.W_V(x)
        
        # 分头
        Q = Q.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = K.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        V = V.view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        
        # 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(self.d_k)
        
        # 应用Causal Mask
        causal_mask = torch.tril(torch.ones(seq_len, seq_len, device=x.device))
        scores = scores.masked_fill(causal_mask == 0, -1e9)
        
        # 应用额外的mask（如padding mask）
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        # Softmax
        attention_weights = torch.softmax(scores, dim=-1)
        
        # 加权求和
        output = torch.matmul(attention_weights, V)
        
        # 合并多头
        output = output.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        
        return self.W_O(output), attention_weights

# PyTorch实现
print("=== PyTorch Masked Attention ===\n")

mha = nn.MultiheadAttention(embed_dim=64, num_heads=4, batch_first=True)
seq_len = 10
batch_size = 2

x = torch.randn(batch_size, seq_len, 64)

# 创建Causal Mask
causal_mask = nn.Transformer.generate_square_subsequent_mask(seq_len)
print(f"Causal Mask形状: {causal_mask.shape}")

# 前向传播
out, attn = mha(x, x, x, attn_mask=causal_mask)
print(f"输出形状: {out.shape}")
print(f"注意力权重形状: {attn.shape}")

# 可视化注意力权重（应该只有下三角）
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Causal Mask
axes[0].imshow(causal_mask.numpy(), cmap='Blues', aspect='auto')
axes[0].set_title('Causal Mask')
axes[0].set_xlabel('Key位置')
axes[0].set_ylabel('Query位置')

# 注意力权重示例
axes[1].imshow(attn[0].numpy(), cmap='Blues', aspect='auto')
axes[1].set_title('Masked Attention权重 (样本1)')
axes[1].set_xlabel('Key位置')
axes[1].set_ylabel('Query位置')

plt.tight_layout()
plt.savefig('masked_attention.png', dpi=150)

# 解码器生成过程演示
print("\n=== 自回归生成演示 ===")
print("预测下一个词的流程:")
print("  输入: '今天天气真好'")
print("  预测: '啊'")
print()
print("预测 '啊' 时的注意力：")
print("  可以看到: 今天, 天气, 真, 好")
print("  不能看: (后面还没生成)")

# 多头注意力的不同Mask模式
print("\n=== Decoder中不同层的Mask ===")
print("Layer 1-2: Causal Mask (只看过去)")
print("Layer 3-4: Causal Mask + Cross Mask (可以看Encoder)")
print("          但仍不能看Decoder的未来位置")
```

#### 常见坑点
- **Mask设置错误**：忘记mask会导致信息泄露
- **Mask形状不对**：需要和attention矩阵形状匹配
- **Decoder推理**：生成时每步都要重新计算mask

---

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### ⚠️ 小白易懵点

**三种架构到底怎么选？**

| 任务 | 推荐架构 | 原因 |
|------|---------|------|
| 文本分类 | Encoder-only | 双向理解，不需要生成 |
| 机器翻译 | Encoder-Decoder | 需要理解+生成 |
| 对话生成 | Decoder-only | 只需要生成 |
| 代码生成 | Decoder-only | 自回归生成代码 |
| 文本摘要 | Encoder-Decoder | 理解原文+生成摘要 |

简单记忆：
- **BERT系列** = Encoder-only = 理解任务
- **GPT系列** = Decoder-only = 生成任务
- **T5系列** = Encoder-Decoder = 理解+生成任务

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结

> Transformer核心组件包括：Self-Attention让每个词关注所有词；Q/K/V是注意力机制的三要素；多头注意力从多个角度捕捉关系；位置编码注入序列顺序信息；FFN对特征进行非线性变换；残差连接+LayerNorm保证训练稳定；Encoder-Decoder/Decoder-only/Encoder-only三种架构适配不同任务；Masked Attention防止看到未来信息。

---

## 附录：PyTorch基础速查

### A.1 张量操作

```python
import torch

# 创建张量
x = torch.tensor([1, 2, 3])
x = torch.randn(3, 4)  # 随机正态分布
x = torch.zeros(3, 4)  # 零矩阵
x = torch.ones(3, 4)    # 全1矩阵

# 张量形状
x.shape      # torch.Size([3, 4])
x.view(4, 3) # 改变形状（共享内存）
x.reshape(4, 3) # 改变形状（复制数据）

# 基本运算
y = x + 1
y = torch.matmul(A, B)  # 矩阵乘法
y = x * 2  # 逐元素乘法
```

### A.2 自动微分

```python
x = torch.tensor([1.0, 2.0], requires_grad=True)
y = x ** 2
y.sum().backward()  # 反向传播
print(x.grad)  # 梯度 = [2, 4]
```

### A.3 常用模块

```python
import torch.nn as nn

# 常用层
nn.Linear(in_features, out_features)  # 全连接层
nn.Conv2d(in_channels, out_channels, kernel_size)  # 卷积层
nn.LSTM(input_size, hidden_size, num_layers)  # LSTM
nn.MultiheadAttention(embed_dim, num_heads)  # 多头注意力
nn.Embedding(vocab_size, embed_dim)  # 词嵌入
nn.LayerNorm(normalized_shape)  # 层归一化
nn.BatchNorm2d(num_features)  # 批归一化
nn.Dropout(p)  # Dropout

# 激活函数
nn.ReLU()
nn.Sigmoid()
nn.Tanh()
nn.GELU()
nn.Softmax(dim)

# 损失函数
nn.CrossEntropyLoss()
nn.MSELoss()
nn.BCELoss()
```

### A.4 优化器

```python
import torch.optim as optim

optimizer = optim.SGD(model.parameters(), lr=0.1, momentum=0.9)
optimizer = optim.Adam(model.parameters(), lr=0.001)
optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)

# 训练循环
for epoch in range(100):
    optimizer.zero_grad()  # 清零梯度
    loss = criterion(model(x), y)  # 前向传播
    loss.backward()  # 反向传播
    optimizer.step()  # 更新参数
```

---

## 继续学习

本教程（上篇）到此结束。**下篇**将涵盖：

- Transformer代码实战：从零实现一个Mini Transformer
- BERT原理与实践
- GPT系列与大语言模型
- ChatGPT背后的技术
- 微调技术（Fine-tuning）
- Prompt Engineering
- RAG与Agent基础

敬请期待！

---

*本教程使用PyTorch 2.x编写，所有代码均可直接运行。*
*如有问题或建议，欢迎反馈！*
