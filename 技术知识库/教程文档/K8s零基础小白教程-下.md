# K8s零基础小白教程（下）

![K8s](https://www.coze.cn/s/JqVhDq6lmkg/)

## 教程概述

本教程专为Kubernetes（K8s）零基础小白设计，通过生动的比喻和实际案例，让你从零开始掌握K8s的核心知识。整个教程分为上、下两部分：

- **上半部分（第1-5篇）**：容器基础、K8s架构、核心资源对象、服务发现与网络、配置与存储
- **下半部分（第6-11篇）**：调度与伸缩、安全与权限、Helm包管理、监控与日志、运维排错、实战项目

### 学习路径图

```
容器基础 → K8s架构 → 核心资源对象 → 服务发现与网络 → 配置与存储
    ↓           ↓            ↓              ↓              ↓
 Docker命令  Master/Node   Pod/Deployment  Service/Ingress  ConfigMap/Secret
   Dockerfile   kubectl     StatefulSet     NetworkPolicy    PV/PVC
   Docker Compose             DaemonSet      CoreDNS         StorageClass
    ↓
 调度与伸缩 → 安全与权限 → Helm → 监控与日志 → 运维排错 → 实战
 NodeSelector   RBAC        Chart      Prometheus/Grafana  kubectl    项目
 Affinity       Service     自定义      EFK                常见故障    CI/CD
 HPA/VPA        NetworkPolicy           告警               升级备份    SpringBoot
 Taint/Toleration PodSecurity
```

---

## 目录

6. [第六篇：调度与伸缩](#第六篇调度与伸缩)
7. [第七篇：安全与权限](#第七篇安全与权限)
8. [第八篇：Helm](#第八篇helm)
9. [第九篇：监控与日志](#第九篇监控与日志)
10. [第十篇：运维排错](#第十篇运维排错)
11. [第十一篇：实战](#第十一篇实战)

---

# 第六篇：调度与伸缩

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

## 前言：智能调度的魔法

想象你是一家大型餐厅的老板，有10位服务员（节点）和成百上千的顾客请求（Pod）。谁来负责决定哪位服务员去服务哪张桌子呢？这就是K8s的调度器。

不仅如此，餐厅的高峰期和低谷期差别巨大。午餐时间人满为患，需要增加人手；下午三点门可罗雀，可以安排休息。这就是K8s的自动伸缩。

本篇我们将深入探索K8s如何智能分配Pod到节点，以及如何根据负载自动调整资源。

---

## 6.1 调度策略：Pod该去哪？

### 6.1.1 NodeSelector：硬性要求

### 一句话人话
**NodeSelector**是给Pod加的标签筛选器，强制Pod只能调度到符合标签要求的节点上。

### 生活比喻 🔥
就像**VIP客户的专属服务**：
- 某些高端客户（特殊的Pod）必须由金牌服务员（有特定标签的节点）服务
- 不是金牌服务员就不能接这个单
- 简单粗暴，要么满足，要么就挂起

### 核心概念
NodeSelector是Pod Spec中的一个字段，用于指定Pod必须调度到带有特定标签的节点上。这是最简单、最直接的调度策略。

### 实操步骤

**步骤1：给节点打标签**

```bash
# 查看当前节点
kubectl get nodes

# 给节点打标签
kubectl label nodes node-1 disktype=ssd
kubectl label nodes node-2 disktype=hdd

# 验证标签
kubectl get nodes --show-labels
```

**步骤2：创建使用NodeSelector的Pod**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ssd-pod
  labels:
    app: storage-app
spec:
  # 只能调度到带有disktype=ssd标签的节点
  nodeSelector:
    disktype: ssd
  containers:
  - name: nginx
    image: nginx:1.21
    resources:
      requests:
        memory: "256Mi"
        cpu: "250m"
      limits:
        memory: "512Mi"
        cpu: "500m"
```

**步骤3：应用并验证**

```bash
# 创建Pod
kubectl apply -f ssd-pod.yaml

# 查看Pod调度到哪个节点
kubectl get pods -o wide

# 查看详细信息
kubectl describe pod ssd-pod
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **NodeSelector的局限性**：
> - NodeSelector不支持复杂的逻辑（比如"或"关系）
> - 如果没有节点满足条件，Pod会一直处于Pending状态
> - NodeSelector只做硬性限制，不做软性偏好
>
> **解决方法**：如果需要更复杂的调度策略，应该使用NodeAffinity（节点亲和性）

---

### 6.1.2 NodeAffinity：软硬兼施

### 一句话人话
**NodeAffinity**是更强大的节点选择器，支持复杂的匹配规则和软硬两种要求。

### 生活比喻 🔥
就像**相亲软件的高级筛选**：
- **硬性要求（Required）**：必须在北京，必须工作稳定，如果不满足就直接pass
- **软性偏好（Preferred）**：最好有车，最好会做饭，如果没有也行，但优先匹配有的
- 可以组合多个条件，甚至设置优先级

### 核心概念
NodeAffinity分为两种类型：
1. **requiredDuringSchedulingIgnoredDuringExecution**：硬性要求，必须满足
2. **preferredDuringSchedulingIgnoredDuringExecution**：软性偏好，优先满足

操作符包括：
- `In`：在列表中
- `NotIn`：不在列表中
- `Exists`：标签存在
- `DoesNotExist`：标签不存在
- `Gt`：大于
- `Lt`：小于

### 实操步骤

**场景：希望Pod优先调度到SSD节点，如果没有SSD节点也可以调度到HDD节点**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: affinity-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: affinity-app
  template:
    metadata:
      labels:
        app: affinity-app
    spec:
      affinity:
        # 硬性要求：必须有zone标签
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: zone
                operator: In
                values:
                - east-1
                - east-2
          # 软性偏好：优先选择SSD节点
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            preference:
              matchExpressions:
              - key: disktype
                operator: In
                values:
                - ssd
          - weight: 50
            preference:
              matchExpressions:
              - key: cpu-type
                operator: In
                values:
                - high-performance
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **为什么叫IgnoredDuringExecution？**
> - 这意味着在Pod运行期间，即使节点的标签发生了变化，Pod也不会被驱逐
> - 比如：Pod调度到SSD节点后，节点的disktype标签被改成hdd，Pod不会自动迁移
> - 如果希望标签变化时Pod重新调度，需要结合其他机制（如Descheduler）
>
> **Weight的作用**：preferred规则的权重，范围1-100，权重越高优先级越高

---

### 6.1.3 PodAffinity与PodAntiAffinity：亲疏有别

### 一句话人话
**PodAffinity**让Pod和某些特定的Pod在一起（亲和），**PodAntiAffinity**让Pod远离某些Pod（反亲和）。

### 生活比喻 🔥

**PodAffinity = 志同道合的朋友**
- 爱打篮球的人喜欢住在一起（互相依赖，需要低延迟通信）
- 靠近点方便交流，效率更高

**PodAntiAffinity = 独来独往的孤狼**
- 容易吵架的人不能住同一层楼（避免单点故障）
- 硬盘密集型的应用不要和CPU密集型的应用争资源
- 同一个应用的不同实例最好分散到不同节点（高可用）

### 核心概念

| 类型 | 用途 | 典型场景 |
|------|------|----------|
| **PodAffinity** | 让Pod调度到特定Pod所在的节点 | 数据库应用和缓存放在一起 |
| **PodAntiAffinity** | 让Pod避开特定Pod所在的节点 | 多副本分散部署、资源隔离 |
| **NodeAffinity** | 基于节点标签调度 | 硬件资源选择、区域划分 |

### 实操步骤

**场景1：PodAffinity - Web应用和Redis必须部署在同一节点**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      affinity:
        podAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - redis
            topologyKey: kubernetes.io/hostname
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

**场景2：PodAntiAffinity - 多副本强制分散到不同节点**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: high-availability-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ha-app
  template:
    metadata:
      labels:
        app: ha-app
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - ha-app
            topologyKey: kubernetes.io/hostname
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**场景3：软性反亲和 - 尽量分散，但也可以集中**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: soft-anti-affinity-app
spec:
  replicas: 5
  selector:
    matchLabels:
      app: soft-ha-app
  template:
    metadata:
      labels:
        app: soft-ha-app
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - soft-ha-app
              topologyKey: kubernetes.io/hostname
      containers:
      - name: nginx
        image: nginx:1.21
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **TopologyKey是什么？**
> - TopologyKey定义了"亲疏关系的作用范围"
> - `kubernetes.io/hostname`：同一台服务器
> - `topology.kubernetes.io/zone`：同一个可用区
> - `topology.kubernetes.io/region`：同一个区域
>
> **PodAntiAffinity的问题**：
> - 如果副本数超过节点数，多余的Pod会无法调度
> - 例如：3个副本，2个节点 → 第3个副本永远Pending
>
> **解决方法**：使用软性反亲和，或者增加节点数

---

## 6.2 污点与容忍度：VIP专属通道

### 6.2.1 污点（Taint）：节点说"不"

### 一句话人话
**污点**是节点上的标记，给节点加限制条件，拒绝不符合条件的Pod调度上来。

### 生活比喻 🔥
就像**餐厅的VIP包间**：
- 普通顾客（普通Pod）不能进入VIP包间（有污点的节点）
- 只有VIP客户（有容忍度的Pod）才能进入
- 包间可能有特殊设备（GPU、专用硬件），只服务于特定需求

### 核心概念

污点由三个部分组成：
```
key=value:effect
```

| Effect | 效果 | 说明 |
|--------|------|------|
| **NoSchedule** | 不可调度 | 新Pod不能调度，已运行的Pod不受影响 |
| **PreferNoSchedule** | 尽量不调度 | 尽量不调度，但如果资源紧张也可以 |
| **NoExecute** | 驱逐 | 新Pod不能调度，已运行的Pod如果不匹配会被驱逐 |

### 实操步骤

**步骤1：给节点打污点**

```bash
# 查看节点当前污点
kubectl describe node node-1 | grep Taint

# 添加NoSchedule污点（普通Pod无法调度）
kubectl taint nodes node-1 dedicated=database:NoSchedule

# 添加NoExecute污点（会驱逐不匹配的Pod）
kubectl taint nodes node-2 special=gpu:NoExecute

# 添加PreferNoSchedule污点（软限制）
kubectl taint nodes node-3 preferred=true:PreferNoSchedule

# 删除污点（注意：key后面的-表示删除）
kubectl taint nodes node-1 dedicated:NoSchedule-

# 查看所有节点及其污点
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
```

**步骤2：创建普通Pod（无法调度到有污点的节点）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: normal-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.21
```

**验证**：如果只有一个节点且有NoSchedule污点，这个Pod会一直Pending。

**步骤3：创建有容忍度的Pod（可以调度到有污点的节点）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: database-pod
spec:
  # 匹配节点的dedicated=database:NoSchedule污点
  tolerations:
  - key: dedicated
    operator: Equal
    value: database
    effect: NoSchedule
  containers:
  - name: mysql
    image: mysql:8.0
    env:
    - name: MYSQL_ROOT_PASSWORD
      value: "password123"
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "1Gi"
        cpu: "500m"
```

**步骤4：更复杂的容忍度配置**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-toleration-pod
spec:
  tolerations:
  # 精确匹配污点
  - key: dedicated
    operator: Equal
    value: database
    effect: NoSchedule
  # 匹配所有key为special的污点，effect为NoExecute
  - key: special
    operator: Exists
    effect: NoExecute
  # 匹配所有key为gpu的污点，任何effect
  - key: gpu
    operator: Exists
  # 匹配所有污点（慎用！）
  - operator: Exists
  containers:
  - name: nginx
    image: nginx:1.21
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **Taint vs NodeSelector的区别？**
> - **NodeSelector**：Pod说"我要去A节点"（主动选择）
> - **Taint**：节点说"我不接收某些Pod"（被动拒绝）
> - 两者的配合：节点打Taint拒绝普通Pod，Pod加Toleration请求进入
>
> **常见的系统污点**：
> - `node.kubernetes.io/not-ready`：节点NotReady
> - `node.kubernetes.io/unreachable`：节点不可达
> - `node.kubernetes.io/memory-pressure`：内存压力
> - `node.kubernetes.io/disk-pressure`：磁盘压力
> - `node.kubernetes.io/pid-pressure`：PID压力
>
> 这些污点会让不匹配的Pod被驱逐，以保护集群稳定性

---

### 6.2.2 实战：GPU节点专用

### 一句话人话
**GPU节点配置污点**，只让AI/机器学习等需要GPU的应用调度到该节点。

### 生活比喻 🔥
就像**专业实验室**：
- 只有上过相关课程（有特定标签）的学生才能进入
- 实验室里昂贵的设备（GPU）不会被普通项目占用
- 资源利用率最大化，避免浪费

### 实操步骤

**步骤1：给GPU节点打污点**

```bash
# 假设node-gpu是GPU节点
kubectl taint nodes node-gpu gpu=true:NoSchedule
kubectl label nodes node-gpu hardware=gpu

# 验证
kubectl describe node node-gpu | grep -A 10 "Taints"
```

**步骤2：创建需要GPU的Pod**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tensorflow-pod
spec:
  # 1. 通过Toleration允许调度到GPU节点
  tolerations:
  - key: gpu
    operator: Equal
    value: "true"
    effect: NoSchedule
  
  # 2. 通过NodeSelector确保调度到GPU节点
  nodeSelector:
    hardware: gpu
  
  containers:
  - name: tensorflow
    image: tensorflow/tensorflow:latest-gpu
    command: ["python"]
    args: ["-c", "import tensorflow as tf; print('GPU:', tf.test.is_gpu_available())"]
    resources:
      requests:
        nvidia.com/gpu: 1
      limits:
        nvidia.com/gpu: 1
```

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结
调度是K8s的核心能力，NodeSelector简单粗暴，Affinity灵活强大，Taint/Toleration实现资源隔离。就像餐厅安排座位，有硬性要求、软性偏好，还有VIP包间。

---

## 6.3 资源限制：别让Pod吃撑了

### 6.3.1 Requests和Limits

### 一句话人话
**Requests**是Pod承诺需要的最少资源，**Limits**是Pod最多能使用的资源上限。

### 生活比喻 🔥

**Requests = 预订座位**
- 告诉餐厅（K8s）："我需要4个人位"
- 餐厅会预留这4个位子（资源预留）
- 其他Pod不能占用这部分资源

**Limits = 消费上限**
- 告诉餐厅："我们最多吃5个人"
- 超过了就不再给吃的（CPU会被限速，内存OOM会被杀）
- 防止某个Pod吃撑了影响其他Pod

### 核心概念

| 资源 | Requests | Limits | 说明 |
|------|----------|--------|------|
| **CPU** | 保证的最小CPU | 使用的最大CPU | 超过限速 |
| **Memory** | 保证的最小内存 | 使用的最大内存 | 超过被杀（OOM） |
| **Storage** | 保证的最小存储 | 无 | PVC申请时使用 |

**CPU单位**：
- `1` = 1个CPU核心（1000m）
- `100m` = 0.1个CPU核心（10%）
- `500m` = 0.5个CPU核心（50%）
- `2` = 2个CPU核心（200%）

**内存单位**：
- `128Mi` = 128兆字节
- `1Gi` = 1吉字节
- `1G` = 1000000000字节
- `1Gi` = 1073741824字节（推荐用Gi/Mi）

### 实操步骤

**场景1：设置Requests和Limits**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    resources:
      requests:
        cpu: "250m"      # 保证250毫核CPU
        memory: "256Mi"  # 保证256MB内存
      limits:
        cpu: "500m"      # 最多使用500毫核CPU
        memory: "512Mi"  # 最多使用512MB内存
  
  - name: redis
    image: redis:7
    resources:
      requests:
        cpu: "100m"
        memory: "128Mi"
      limits:
        cpu: "200m"
        memory: "256Mi"
```

**场景2：不设置Limit的风险**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# ❌ 危险配置：不设置Limits
apiVersion: v1
kind: Pod
metadata:
  name: dangerous-pod
spec:
  containers:
  - name: memory-hog
    image: ubuntu
    command: ["bash", "-c", "while true; do dd if=/dev/zero of=/dev/shm/fill bs=1M count=100; done"]
    resources:
      requests:
        memory: "128Mi"
      # 没有设置limits，可能会占用所有内存！
```

**场景3：CPU限速测试**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cpu-limit-demo
spec:
  containers:
  - name: stress
    image: polinux/stress
    command: ["stress"]
    args: ["--cpu", "2", "--timeout", "300s"]  # 请求2个CPU
    resources:
      requests:
        cpu: "100m"
      limits:
        cpu: "200m"  # 但限制只能用200m
```

验证：进入Pod查看CPU使用率，会发现CPU被限制在200m（20%）左右。

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **CPU vs Memory的超限处理**：
> - **CPU超限**：Pod不会被杀，只是CPU使用被限速（throttled），变慢
> - **Memory超限**：Pod会立即被OOM Killer杀死，重启
>
> **不设置Limit的后果**：
> - Pod可能占用节点所有资源
> - 影响同一节点的其他Pod
> - 甚至导致节点崩溃
>
> **Limit Range（资源配额）**：
> - 可以在Namespace级别设置默认的Requests和Limits
> - 强制所有Pod遵守资源约束

---

### 6.3.2 LimitRange：统一规范

### 一句话人话
**LimitRange**是命名空间级别的资源限制规则，为所有Pod设定默认和最大值。

### 生活比喻 🔥
就像**小区的装修规定**：
- 所有业主必须遵守（统一规范）
- 新装修的业主按标准执行（默认值）
- 不能超出限制（最大值）
- 避免某个业主过度装修影响整栋楼

### 实操步骤

**创建LimitRange**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: cpu-mem-limit-range
  namespace: default
spec:
  limits:
  - type: Container
    default:          # 默认的Limits
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:   # 默认的Requests
      cpu: "250m"
      memory: "256Mi"
    max:              # 最大的Limits
      cpu: "2"
      memory: "2Gi"
    min:              # 最小的Requests
      cpu: "50m"
      memory: "64Mi"
    maxLimitRequestRatio:  # Limit/Request的最大比率
      cpu: "2"
      memory: "1.5"
```

**验证LimitRange**

```bash
# 查看LimitRange
kubectl get limitrange

kubectl describe limitrange cpu-mem-limit-range

# 创建不设置资源的Pod（自动使用默认值）
kubectl run nginx-default --image=nginx:1.21 --restart=Never

# 查看Pod的资源（自动加上了Limits）
kubectl describe pod nginx-default | grep -A 5 "Limits"
```

**LimitRange的类型**

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: all-limits
spec:
  limits:
  - type: Container      # 限制容器
    max:
      cpu: "800m"
      memory: "1Gi"
  - type: Pod           # 限制Pod（所有容器总和）
    max:
      cpu: "2"
      memory: "4Gi"
  - type: PersistentVolumeClaim  # 限制PVC
    max:
      storage: "10Gi"
    min:
      storage: "1Gi"
```

---

### 6.3.3 ResourceQuota：总量控制

### 一句话人话
**ResourceQuota**限制命名空间可以使用的总资源量，防止过度消耗集群资源。

### 生活比喻 🔥
就像**家庭的月度预算**：
- 全家人这个月只能花5000元（总量限制）
- 买衣服最多2000元（特定资源限制）
- 每个人都有自己的额度（Pod级别）
- 总预算超了就不能再消费了

### 实操步骤

**创建ResourceQuota**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
  namespace: default
spec:
  hard:
    requests.cpu: "4"      # 该命名空间总共只能申请4核CPU
    requests.memory: "8Gi"  # 总共只能申请8GB内存
    limits.cpu: "8"         # 总共最多使用8核CPU
    limits.memory: "16Gi"   # 总共最多使用16GB内存
    pods: "10"              # 最多创建10个Pod
    requests.nvidia.com/gpu: "2"  # 最多申请2个GPU
```

**创建对象数量配额**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: object-counts
  namespace: default
spec:
  hard:
    configmaps: "10"        # 最多10个ConfigMap
    persistentvolumeclaims: "5"  # 最多5个PVC
    replicationcontrollers: "20" # 最多20个RC
    secrets: "10"            # 最多10个Secret
    services: "5"            # 最多5个Service
    services.loadbalancers: "1"  # 最多1个LoadBalancer类型的Service
```

**验证配额**

```bash
# 查看配额
kubectl get resourcequota

kubectl describe resourcequota compute-resources

# 尝试创建超过配额的Pod（会失败）
kubectl run test-pod --image=nginx:1.21 --requests=cpu=5 --restart=Never

# 错误信息：exceeded quota: compute-resources, requested: requests.cpu=5, used: requests.cpu=0, limited: requests.cpu=4
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **LimitRange vs ResourceQuota的区别？**
> - **LimitRange**：限制单个Pod/容器的资源
> - **ResourceQuota**：限制整个命名空间的总资源
>
> **配额的作用范围**：
> - 默认对整个命名空间生效
> - 可以通过`ScopeSelector`限定特定Pod（比如BestEffort的Pod不计入配额）
>
> **生产环境最佳实践**：
> 1. 每个Namespace设置ResourceQuota
> 2. 设置LimitRange提供默认值
> 3. 所有Pod显式设置资源请求和限制
> 4. 定期监控资源使用情况

---

## 6.4 自动伸缩：动态调整规模

### 6.4.1 HPA：水平自动伸缩

### 一句话人话
**HPA（Horizontal Pod Autoscaler）**根据Pod的CPU/内存使用率，自动增加或减少Pod的副本数。

### 生活比喻 🔥
就像**餐厅的动态排班**：
- 高峰期顾客多了，服务员不够，临时叫人手（扩容）
- 低谷期顾客少了，太多服务员闲着，安排休息（缩容）
- 根据当前排队人数（CPU使用率）决定增减多少人手
- 避免顾客等太久，也避免服务员闲置浪费

### 核心概念

HPA的工作流程：
```
1. Metrics Server采集Pod的CPU/内存使用率
2. HPA定期检查指标（默认15秒一次）
3. 计算需要的副本数 = 当前副本数 × (当前使用率 / 目标使用率)
4. 调用Deployment/StatefulSet的Scale接口调整副本数
5. 循环执行，持续监控和调整
```

**HPA关键参数**：
- `minReplicas`：最小副本数
- `maxReplicas`：最大副本数
- `targetCPUUtilizationPercentage`：目标CPU使用率
- `targetMemoryUtilizationPercentage`：目标内存使用率

### 实操步骤

**前提：安装Metrics Server**

```bash
# 检查Metrics Server是否已安装
kubectl get pods -n kube-system | grep metrics-server

# 如果没有，安装Metrics Server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 验证
kubectl top nodes
kubectl top pods
```

**步骤1：创建目标Deployment**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-apache
spec:
  selector:
    matchLabels:
      run: php-apache
  replicas: 1
  template:
    metadata:
      labels:
        run: php-apache
    spec:
      containers:
      - name: php-apache
        image: registry.k8s.io/hpa-example
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: "200m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

```bash
kubectl apply -f php-apache-deployment.yaml
kubectl expose deployment php-apache --port=80
```

**步骤2：创建HPA**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: php-apache-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50  # 目标CPU使用率50%
```

```bash
kubectl apply -f hpa.yaml

# 查看HPA
kubectl get hpa

kubectl describe hpa php-apache-hpa
```

**步骤3：压力测试**

```bash
# 开一个终端，持续请求
kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://php-apache; done"

# 另一个终端，观察HPA
watch kubectl get hpa php-apache-hpa

# 查看Pod数量变化
kubectl get pods -l run=php-apache -w
```

**停止压力后观察缩容**

```bash
# Ctrl+C停止压力请求后，等待几分钟
# Pod数量会自动缩回minReplicas（1个）
kubectl get pods -l run=php-apache
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **为什么HPA不工作？**
> - Pod没有设置resources.requests（HPA需要计算百分比）
> - Metrics Server未安装或异常
> - 当前使用率低于目标值，不会扩容
>
> **HPA的稳定窗口**：
> - 默认：扩容立即生效，缩容等待5分钟
> - 可通过`stabilizationWindowSeconds`调整
> - 避免频繁扩缩容（抖动）
>
> **HPA vs VPA的选择**：
> - **HPA**：增加Pod数量（横向），适合无状态应用
> - **VPA**：调整Pod资源（纵向），适合资源需求变化大的应用
> - **两者不能同时使用**：VPA调整requests，HPA基于requests计算，会冲突

---

### 6.4.2 VPA：垂直自动伸缩

### 一句话人话
**VPA（Vertical Pod Autoscaler）**根据Pod的历史资源使用情况，自动调整Pod的CPU和内存requests/limits。

### 生活比喻 🔥
就像**办公室的工位调整**：
- 观察员工（Pod）的工作量（资源使用）
- 发现经常加班（CPU/内存不足），升级配置（增加资源）
- 发现长期闲置，降级配置（减少资源）
- 同一个工位（Pod）调整大小，不是增加工位数量

### 核心概念

VPA由三个组件组成：
1. **Recommender**：监控资源使用，推荐合适的资源值
2. **Updater**：更新Pod的requests/limits（需要重启Pod）
3. **Admission Controller**：拦截Pod创建请求，应用推荐值

**VPA的四种模式**：
- `Off`：VPA仅计算推荐值，不应用
- `Initial`：只在Pod创建时应用推荐值
- `Recreate`：Pod重启时应用推荐值
- `Auto`：自动更新Pod（默认）

### 实操步骤

**前提：安装VPA**

```bash
# 克隆VPA仓库
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler

# 安装VPA
./hack/vpa-up.sh

# 验证
kubectl get pods -n kube-system | grep vpa
kubectl api-versions | grep autoscaling
```

**创建VPA**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: nginx-vpa
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind:       Deployment
    name:       nginx-deployment
  updatePolicy:
    updateMode: "Auto"  # Off, Initial, Recreate, Auto
  resourcePolicy:
    containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: "100m"
        memory: "256Mi"
      maxAllowed:
        cpu: "1"
        memory: "1Gi"
      controlledResources: ["cpu", "memory"]
```

```bash
kubectl apply -f vpa.yaml

# 查看VPA
kubectl get vpa

kubectl describe vpa nginx-vpa

# 查看推荐值
kubectl describe vpa nginx-vpa | grep -A 20 "Container Resource"
```

**查看VPA推荐**

```bash
# VPA会给出推荐的requests
kubectl describe vpa nginx-vpa

输出示例：
  Container Resource Usage:
    Lower Bound:
      cpu:    100m
      memory: 262144k
    Target:
      cpu:    587m
      memory: 262144k
    Uncapped Target:
      cpu:    587m
      memory: 262144k
    Upper Bound:
      cpu:    2
      memory: 2Gi
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **VPA会重启Pod吗？**
> - `Auto`模式下，会自动更新Pod的requests/limits，导致Pod重启
> - 生产环境建议用`Off`模式先观察推荐值
> - 手动调整后，再决定是否启用自动更新
>
> **VPA vs 手动调整资源**：
> - **优点**：自动监控、精准调整、避免资源浪费
> - **缺点**：Pod会重启、可能和HPA冲突
>
> **生产环境建议**：
> - 用VPA的`Off`模式观察推荐值
> - 根据推荐值手动调整requests/limits
> - 对于无状态应用，优先使用HPA
> - 对于有状态应用或资源需求变化大的应用，考虑VPA

---

### 6.4.3 Cluster Autoscaler：集群自动伸缩

### 一句话人话
**Cluster Autoscaler**根据集群的资源不足情况，自动增加或减少节点。

### 生活比喻 🔥
就像**连锁餐厅的门店管理**：
- 某个分店（节点）顾客多了，临时开新分店（增加节点）
- 分店生意冷清，关闭一些分店（减少节点）
- 根据整体需求调整分店数量
- 比只在一个分店增加服务员（HPA）更灵活

### 核心概念

Cluster Autoscaler的工作原理：
```
1. 检测到Pod处于Pending状态（资源不足）
2. 尝试调度失败，确认需要更多节点
3. 调用云厂商API创建新节点
4. 等待节点Ready
5. 重新调度Pending的Pod到新节点
6. 定期检查节点利用率，低利用率节点自动缩容
```

**适用场景**：
- 云厂商托管集群（GKE, EKS, AKS, ACK）
- 基于虚拟机节点的集群
- 节点池配置

### 实操步骤

**前提条件**：
1. 集群运行在云平台上
2. 有足够的配额创建新节点
3. 节点有正确的标签和污点

**配置Cluster Autoscaler（以GKE为例）**

```bash
# GKE上创建集群时启用autoscaler
gcloud container clusters create my-cluster \
  --num-nodes=1 \
  --min-nodes=1 \
  --max-nodes=5 \
  --enable-autoscaling
```

**配置YAML（适用于Kubeadm集群）**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler
  namespace: kube-system
data:
  cluster-autoscaler.yaml: |
    scaleDownEnabled: true
    scaleDownDelayAfterAdd: 10m
    scaleDownUnneededTime: 10m
    skipNodesWithLocalStorage: true
    maxNodeProvisionTime: 15m
    podsPerCore: 10
    maxPodsPerNode: 110
    balanceSimilarNodeGroups: true
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.27.0
        name: cluster-autoscaler
        resources:
          limits:
            cpu: 100m
            memory: 300Mi
          requests:
            cpu: 100m
            memory: 300Mi
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws  # 根据云厂商修改：aws, gce, azure
        - --skip-nodes-with-local-storage=false
        - --expander=priority
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/my-cluster
        env:
        - name: AWS_REGION
          value: us-west-2  # AWS区域
```

**测试自动扩容**

```bash
# 创建大量Pod，超过当前节点容量
kubectl create deployment stress-test --image=nginx:1.21 --replicas=20 --dry-run=client -o yaml | kubectl apply -f -

# 观察Pod状态
kubectl get pods -w

# 观察节点数量变化（等待几分钟）
kubectl get nodes -w

# 查看Cluster Autoscaler日志
kubectl logs -n kube-system deployment/cluster-autoscaler -f
```

**测试自动缩容**

```bash
# 删除大量Pod
kubectl delete deployment stress-test

# 等待10-15分钟，观察节点是否自动缩容
kubectl get nodes -w
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **Cluster Autoscaler不会缩容的情况**：
> - 节点上有系统Pod（kube-system namespace）
> - 节点上有使用本地存储的Pod
> - Pod有反亲和性要求，无法调度到其他节点
> - 节点刚加入集群不到10分钟
>
> **HPA vs Cluster Autoscaler的配合**：
> - **HPA**：调整Pod数量（微观）
> - **Cluster Autoscaler**：调整节点数量（宏观）
> - 两级联动：HPA先扩容Pod → 资源不足 → Cluster Autoscaler扩容节点
>
> **生产环境建议**：
> 1. 设置合理的min和max节点数
> 2. 配置节点池，区分不同规格的节点
> 3. 使用PodDisruptionBudget保护重要应用
> 4. 监控扩缩容事件，及时调整配置

---

## 本章小结

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结
K8s的调度与伸缩就像智能餐厅管理系统：NodeSelector和Affinity安排座位，Taint/Toleration实现VIP专区，资源限制防止浪费，HPA/VPA/Cluster Autoscaler实现动态调整。合理配置才能既保证服务质量，又提高资源利用率。

---

# 第七篇：安全与权限

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

## 前言：安全第一，权限分明

想象你是一家大公司的IT管理员，需要管理成百上千的员工和应用。如何确保：
- 每个人只能访问他们需要的资源？（最小权限原则）
- 敏感数据不被泄露？（数据安全）
- 恶意代码被隔离？（网络安全）

K8s提供了完善的安全机制：RBAC控制权限，ServiceAccount管理身份，NetworkPolicy实现网络隔离，Pod Security保护容器安全。

本篇我们将深入了解K8s的安全体系。

---

## 7.1 RBAC：基于角色的访问控制

### 7.1.1 RBAC的核心概念

### 一句话人话
**RBAC（Role-Based Access Control）**通过角色来管理权限，给用户或服务账号分配角色，从而控制它们能做什么。

### 生活比喻 🔥
就像**公司的门禁卡系统**：
- **角色（Role）**：定义了一组权限（比如"工程师"可以进入机房和办公室）
- **用户（User）**：具体的人（张三、李四）
- **绑定（RoleBinding）**：把用户和角色绑定（张三是工程师）
- **权限（Permission）**：具体能做什么（开门、读文件）

**RBAC的好处**：
- 张三离职了，删除用户即可，不需要修改角色
- 李四升职了，换个角色绑定，不需要重复授权
- 权限和角色分离，管理清晰

### 核心概念

RBAC的四个核心对象：

| 对象 | 作用 | 作用范围 |
|------|------|----------|
| **Role** | 定义角色和权限 | 单个命名空间 |
| **ClusterRole** | 定义角色和权限 | 整个集群 |
| **RoleBinding** | 绑定角色和主体 | 单个命名空间 |
| **ClusterRoleBinding** | 绑定ClusterRole和主体 | 整个集群 |

**主体（Subject）类型**：
- `User`：用户（外部管理，K8s不存储）
- `Group`：用户组（外部管理，K8s不存储）
- `ServiceAccount`：服务账号（K8s管理，Pod使用）

**API资源**和**动词（Verbs）**：

| 资源类型 | 说明 |
|----------|------|
| `pods`, `deployments`, `services` | 具体的K8s资源 |
| `configmaps`, `secrets` | 配置和密钥 |
| `persistentvolumeclaims` | 持久化存储 |
| `namespaces`, `nodes` | 集群级资源 |

| 动词 | 说明 |
|------|------|
| `get`, `list`, `watch` | 读取 |
| `create`, `update`, `patch` | 修改 |
| `delete` | 删除 |
| `*` | 所有权限 |

### 实操步骤

**场景1：创建开发人员的Role（只能管理Pod）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-manager
rules:
- apiGroups: [""]  # "" 表示核心API组（Pod, Service等）
  resources: ["pods", "pods/log", "pods/exec"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: [""]
  resources: ["pods/status"]
  verbs: ["get"]
```

**场景2：创建只读Role**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
```

**场景3：绑定Role到用户**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-pod-manager
  namespace: default
subjects:
- kind: User
  name: "alice@example.com"  # 用户名
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-manager
  apiGroup: rbac.authorization.k8s.io
```

**场景4：绑定Role到ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-sa-to-pod-reader
  namespace: default
subjects:
- kind: ServiceAccount
  name: my-app-sa
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**验证权限**

```bash
# 创建测试用户（使用kubectl的模拟功能）
kubectl auth can-i get pods --as=alice@example.com

# 模拟ServiceAccount
kubectl auth can-i create pods --as=system:serviceaccount:default:my-app-sa

# 查看所有Role
kubectl get roles -n default

kubectl describe role pod-manager

# 查看所有RoleBinding
kubectl get rolebindings -n default

kubectl describe rolebinding bind-pod-manager
```

---

### 7.1.2 ClusterRole和ClusterRoleBinding

### 一句话人话
**ClusterRole**和**ClusterRoleBinding**用于集群级别的权限控制，不受命名空间限制。

### 生活比喻 🔥
就像**公司的全局管理员**：
- 可以访问所有部门（所有命名空间）
- 可以创建新部门（创建命名空间）
- 可以管理服务器和基础设施（集群级资源）
- 比部门经理（Role）权限更大

### 实操步骤

**场景1：创建管理员ClusterRole**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-admin  # 内置的超级管理员角色（谨慎使用！）
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

**注意**：`cluster-admin`是K8s内置的超级管理员角色，拥有所有权限，谨慎分配！

**场景2：自定义ClusterRole - 集群级别的Pod查看权限**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-pod-viewer
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["namespaces"]
  verbs: ["get", "list"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets"]
  verbs: ["get", "list", "watch"]
```

**场景3：绑定ClusterRole到用户**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: bind-cluster-admin
subjects:
- kind: User
  name: "admin@example.com"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

**场景4：跨命名空间使用Role**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# ClusterRole定义在cluster级别
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: namespace-admin
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
---
# 在特定命名空间绑定
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: namespace-admin-binding
  namespace: development
subjects:
- kind: User
  name: "dev-lead@example.com"
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: namespace-admin
  apiGroup: rbac.authorization.k8s.io
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **Role vs ClusterRole的区别？**
> - **Role**：只在单个命名空间生效
> - **ClusterRole**：在整个集群生效
>
> **RoleBinding vs ClusterRoleBinding的区别？**
> - **RoleBinding**：绑定Role或ClusterRole到主体，作用范围是命名空间
> - **ClusterRoleBinding**：绑定ClusterRole到主体，作用范围是整个集群
>
> **常见的内置ClusterRole**：
> - `cluster-admin`：超级管理员（所有权限）
> - `admin`：命名空间管理员（命名空间内所有权限）
> - `edit`：编辑者（可以修改资源，但不能修改Role/Binding）
> - `view`：查看者（只读权限）
>
> **查看内置Role**：
> ```bash
> kubectl get clusterrole
> kubectl describe clusterrole cluster-admin
> kubectl describe clusterrole admin
> kubectl describe clusterrole edit
> kubectl describe clusterrole view
> ```

---

### 7.1.3 RBAC实战：CI/CD流水线权限

### 一句话人话
为CI/CD工具（如Jenkins、GitLab CI）创建最小权限的ServiceAccount，只让它能部署和更新应用。

### 生活比喻 🔥
就像**建筑公司的项目经理**：
- 可以在现场部署材料（部署应用）
- 可以查看施工进度（查看Pod状态）
- 但不能动公司的财务数据（不能访问Secret）
- 权限够用，但不多给

### 实操步骤

**步骤1：创建CI/CD专用的ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ci-cd-sa
  namespace: production
```

**步骤2：创建CI/CD专用的Role**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ci-cd-role
  namespace: production
rules:
# Deployment管理
- apiGroups: ["apps"]
  resources: ["deployments", "deployments/scale", "deployments/status"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

# Service管理
- apiGroups: [""]
  resources: ["services", "endpoints"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

# ConfigMap管理
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

# Secret管理（只允许创建，不允许读取其他Secret）
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["create"]
- apiGroups: [""]
  resourceNames: ["ci-cd-secret"]
  resources: ["secrets"]
  verbs: ["get", "update", "delete"]

# Pod管理（读取日志和状态）
- apiGroups: [""]
  resources: ["pods", "pods/log", "pods/status"]
  verbs: ["get", "list", "watch"]

# Ingress管理
- apiGroups: ["networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

**步骤3：绑定Role到ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-ci-cd
  namespace: production
subjects:
- kind: ServiceAccount
  name: ci-cd-sa
  namespace: production
roleRef:
  kind: Role
  name: ci-cd-role
  apiGroup: rbac.authorization.k8s.io
```

**步骤4：使用ServiceAccount的token**

```bash
# 获取ServiceAccount的token
kubectl get secret -n production | grep ci-cd-sa

TOKEN_NAME=$(kubectl get secret -n production | grep ci-cd-sa | awk '{print $1}')
TOKEN=$(kubectl get secret $TOKEN_NAME -n production -o jsonpath='{.data.token}' | base64 -d)

echo $TOKEN

# 使用token连接集群（模拟CI/CD工具）
kubectl config set-credentials ci-cd --token=$TOKEN
kubectl config set-context ci-cd-context --cluster=your-cluster --user=ci-cd
kubectl config use-context ci-cd-context

# 测试权限
kubectl get pods -n production  # 应该成功
kubectl delete pod -n production -l app=xxx  # 应该失败（没有删除Pod的权限）
```

---

## 7.2 ServiceAccount：Pod的身份凭证

### 7.2.1 ServiceAccount基础

### 一句话人话
**ServiceAccount**是Pod在K8s API中的身份，用于Pod与API Server通信。

### 生活比喻 🔥
就像**员工的工牌**：
- 每个员工（Pod）都有工牌（ServiceAccount）
- 进门刷卡（访问API Server）
- 不同级别的工牌权限不同（不同的ServiceAccount有不同的RBAC权限）
- 没工牌就不能进门（Pod没有ServiceAccount无法访问API）

### 核心概念

**默认ServiceAccount**：
- 每个命名空间自动创建一个`default` ServiceAccount
- 不指定ServiceAccount的Pod使用`default`
- `default`通常只有最低权限

**ServiceAccount和Pod的关系**：
```yaml
spec:
  serviceAccountName: my-custom-sa  # 指定ServiceAccount
```

**ServiceAccount的Secret**：
- 自动生成包含token的Secret
- 挂载到Pod的`/var/run/secrets/kubernetes.io/serviceaccount/`
- Pod自动使用这个token访问API Server

### 实操步骤

**场景1：创建自定义ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: default
  labels:
    app: my-application
```

```bash
# 创建ServiceAccount
kubectl apply -f sa.yaml

# 查看ServiceAccount
kubectl get sa

kubectl describe sa my-app-sa

# 查看自动生成的Secret
kubectl get secrets | grep my-app-sa
```

**场景2：Pod使用自定义ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-custom-sa
spec:
  serviceAccountName: my-app-sa  # 使用自定义ServiceAccount
  containers:
  - name: nginx
    image: nginx:1.21
    command:
    - /bin/sh
    - -c
    - |
      echo "ServiceAccount Token:"
      cat /var/run/secrets/kubernetes.io/serviceaccount/token
      sleep 3600
```

```bash
# 创建Pod
kubectl apply -f pod-with-sa.yaml

# 查看Pod的挂载（应该有serviceaccount token）
kubectl describe pod pod-with-custom-sa | grep -A 10 "Mounts"

# 进入Pod验证
kubectl exec -it pod-with-custom-sa -- sh

# 在Pod内
ls /var/run/secrets/kubernetes.io/serviceaccount/
# 输出：ca.crt  namespace  token

cat /var/run/secrets/kubernetes.io/serviceaccount/namespace
cat /var/run/secrets/kubernetes.io/serviceaccount/token
```

**场景3：禁用自动挂载token（安全实践）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-no-token
spec:
  serviceAccountName: default
  automountServiceAccountToken: false  # 不自动挂载token
  containers:
  - name: nginx
    image: nginx:1.21
```

**场景4：ServiceAccount级别的RBAC**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# 创建ServiceAccount
apiVersion: v1
kind: ServiceAccount
metadata:
  name: list-pods-sa
---
# 创建Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-list-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
# 绑定Role到ServiceAccount
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: bind-list-pods
subjects:
- kind: ServiceAccount
  name: list-pods-sa
roleRef:
  kind: Role
  name: pod-list-role
  apiGroup: rbac.authorization.k8s.io
---
# Pod使用ServiceAccount
apiVersion: v1
kind: Pod
metadata:
  name: test-list-pods
spec:
  serviceAccountName: list-pods-sa
  containers:
  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["kubectl", "get", "pods"]
```

---

### 7.2.2 IAM角色绑定（云厂商集成）

### 一句话人话
**IAM角色绑定**让Pod可以使用云厂商的IAM权限，访问S3、RDS等云资源。

### 生活比喻 🔥
就像**公司的跨部门协作**：
- 你的工牌（ServiceAccount）不仅能进公司门（K8s API）
- 还能访问财务部（S3）、人事部（RDS）等
- 通过统一的身份系统，管理跨部门权限
- 不用每个部门单独发工牌

### 实操步骤（以AWS EKS为例）

**步骤1：创建IAM OIDC Provider**

```bash
# 获取集群的OIDC issuer
CLUSTER_NAME=your-cluster
AWS_REGION=us-west-2

OIDC_ISSUER=$(aws eks describe-cluster \
  --name $CLUSTER_NAME \
  --region $AWS_REGION \
  --query "cluster.identity.oidc.issuer" \
  --output text)

echo $OIDC_ISSUER
# 输出：https://oidc.eks.us-west-2.amazonaws.com/id/EXAMPLE...

# 提取provider URL
OIDC_PROVIDER=$(echo $OIDC_ISSUER | cut -f 3 -d'/')
echo $OIDC_PROVIDER
```

**步骤2：创建IAM策略（S3读写权限）**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

保存为`s3-policy.json`，创建策略：

```bash
aws iam create-policy \
  --policy-name k8s-s3-policy \
  --policy-document file://s3-policy.json

POLICY_ARN=$(aws iam list-policies --query 'Policies[?PolicyName==`k8s-s3-policy`].Arn' --output text)
```

**步骤3：创建IAM Role并信任OIDC**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/OIDC_PROVIDER"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "OIDC_PROVIDER:sub": "system:serviceaccount:default:my-app-sa",
          "OIDC_PROVIDER:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
```

创建IAM Role：

```bash
aws iam create-role \
  --role-name k8s-s3-role \
  --assume-role-policy-document file://trust-policy.json

aws iam attach-role-policy \
  --role-name k8s-s3-role \
  --policy-arn $POLICY_ARN
```

**步骤4：添加IAM Role注解到ServiceAccount**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: default
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT_ID:role/k8s-s3-role
```

**步骤5：验证IAM权限**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-s3-access
spec:
  serviceAccountName: my-app-sa
  containers:
  - name: aws-cli
    image: amazon/aws-cli:latest
    command:
    - /bin/sh
    - -c
    - |
      echo "Testing S3 access..."
      aws s3 ls s3://my-bucket
      aws s3 cp /etc/hostname s3://my-bucket/test-$(date +%s)
      sleep 3600
```

```bash
# 创建Pod
kubectl apply -f test-s3.yaml

# 查看日志（应该能看到S3 bucket内容）
kubectl logs test-s3-access
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **ServiceAccount vs User的区别？**
> - **ServiceAccount**：K8s管理的，用于Pod访问API
> - **User**：外部管理的（如LDAP、OAuth），用于人类用户
>
> **什么时候需要创建自定义ServiceAccount？**
> - Pod需要访问K8s API（如Operator）
> - 需要不同的权限隔离
> - 需要访问云厂商资源（绑定IAM角色）
>
> **安全最佳实践**：
> 1. 不需要访问API的Pod，禁用token挂载
> 2. 为每个应用创建专用ServiceAccount
> 3. 遵循最小权限原则，只给必要的RBAC权限
> 4. 定期审查ServiceAccount和权限

---

## 7.3 NetworkPolicy：网络隔离

### 7.3.1 NetworkPolicy基础

### 一句话人话
**NetworkPolicy**定义Pod之间的网络访问规则，实现网络隔离。

### 生活比喻 🔥
就像**公司的防火墙**：
- 研发部（Namespace）不能访问财务部（Namespace）
- 只有特定员工（标签选择器）可以进入特定房间（Pod）
- 只允许特定端口（端口）通信
- 防止网络攻击和横向渗透

### 核心概念

**NetworkPolicy的工作方式**：
- 默认：所有Pod可以互相通信（非隔离状态）
- 应用NetworkPolicy后：只允许白名单中的通信
- 每条NetworkPolicy包含：
  - `podSelector`：选择要应用规则的Pod
  - `policyTypes`：`Ingress`（入站）和/或`Egress`（出站）
  - `ingress`：允许哪些来源访问
  - `egress`：允许访问哪些目标

**支持NetworkPolicy的CNI插件**：
- Calico（推荐，功能丰富）
- Cilium（eBPF，性能高）
- Weave Net
- Canal（Flannel + Calico）

### 实操步骤

**前提：安装支持NetworkPolicy的CNI插件（以Calico为例）**

```bash
# 安装Calico
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml

# 验证
kubectl get pods -n kube-system | grep calico
```

**场景1：默认拒绝所有入站流量（白名单模式）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: default
spec:
  podSelector: {}  # 空选择器 = 所有Pod
  policyTypes:
  - Ingress
  # 没有ingress规则 = 拒绝所有入站流量
```

**场景2：允许特定Pod访问（允许Web访问Backend）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web-to-backend
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: backend  # 应用到backend Pod
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: web  # 允许web Pod访问
    ports:
    - protocol: TCP
      port: 8080  # 只允许访问8080端口
```

**场景3：多命名空间隔离（默认拒绝跨命名空间）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# 在命名空间dev上：拒绝所有跨命名空间的入站
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-cross-namespace
  namespace: dev
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}  # 允许同一命名空间内的Pod访问
```

**场景4：允许访问特定命名空间**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# 允许dev命名空间访问prod命名服务的特定Pod
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dev-to-prod-api
  namespace: prod
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: dev  # 允许dev命名空间的Pod访问
    ports:
    - protocol: TCP
      port: 80
```

**场景5：出站流量控制（限制Pod只能访问特定服务）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: restrict-egress
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: restricted-pod
  policyTypes:
  - Egress
  egress:
  # 允许访问DNS（53端口UDP）
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53
  # 允许访问特定的backend服务
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 8080
```

**场景6：完整的双向规则（入站+出站）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-policy
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Ingress
  - Egress
  # 入站：允许来自ingress-nginx的流量
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
  # 出站：允许访问backend和DNS
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 8080
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: UDP
      port: 53
```

**验证NetworkPolicy**

```bash
# 创建测试Pod
kubectl run test-web --image=nginx:1.21 --labels=app=web --restart=Never
kubectl run test-backend --image=nginx:1.21 --labels=app=backend --port=8080 --restart=Never

# 测试连接
kubectl exec -it test-web -- curl http://test-backend:8080

# 查看NetworkPolicy
kubectl get networkpolicy

kubectl describe networkpolicy allow-web-to-backend
```

---

### 7.3.2 NetworkPolicy实战：多层应用隔离

### 一句话人话
为三层架构（Web → App → DB）应用创建网络隔离，防止横向攻击。

### 生活比喻 🔥
就像**银行的分区管理**：
- 大厅（Web层）：客户可以进来，但不能进入柜台
- 柜台（App层）：只处理业务，不能直接进入金库
- 金库（DB层）：只有特定的柜员可以进入
- 每层都有门禁（NetworkPolicy），防止越级访问

### 实操步骤

**步骤1：部署三层应用**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# Web层
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 2
  selector:
    matchLabels:
      tier: web
  template:
    metadata:
      labels:
        tier: web
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    tier: web
  ports:
  - port: 80
    targetPort: 80
---
# App层
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      tier: app
  template:
    metadata:
      labels:
        tier: app
    spec:
      containers:
      - name: app
        image: nginx:1.21
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: app
spec:
  selector:
    tier: app
  ports:
  - port: 8080
    targetPort: 8080
---
# DB层
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db
spec:
  replicas: 1
  selector:
    matchLabels:
      tier: db
  template:
    metadata:
      labels:
        tier: db
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "password123"
        ports:
        - containerPort: 3306
---
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  selector:
    tier: db
  ports:
  - port: 3306
    targetPort: 3306
```

**步骤2：应用网络隔离策略**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
# DB层：只允许App层访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-policy
spec:
  podSelector:
    matchLabels:
      tier: db
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: app
    ports:
    - protocol: TCP
      port: 3306
---
# App层：只允许Web层访问，允许出站到DB
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: app-policy
spec:
  podSelector:
    matchLabels:
      tier: app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          tier: web
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: db
    ports:
    - protocol: TCP
      port: 3306
---
# Web层：允许所有入站，只允许出站到App
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-policy
spec:
  podSelector:
    matchLabels:
      tier: web
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          tier: app
    ports:
    - protocol: TCP
      port: 8080
```

**步骤3：验证隔离效果**

```bash
# 创建测试Pod，尝试从各层访问
kubectl run test-pod --image=busybox:1.28 --rm -it --restart=Never -- sh

# 在Pod内测试
# 尝试直接访问DB（应该失败）
nslookup db
telnet db 3306

# 尝试从Web访问App（应该成功）
telnet app 8080

# 尝试从App访问DB（应该成功）
telnet db 3306
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **NetworkPolicy不生效？**
> - 确保CNI插件支持NetworkPolicy（如Calico、Cilium）
> - NetworkPolicy只适用于同一CNI网络内的Pod
> - NodePort/LoadBalancer的外部流量不受NetworkPolicy限制
>
> **白名单 vs 黑名单**：
> - **白名单（推荐）**：默认拒绝，明确允许（更安全）
> - **黑名单**：默认允许，明确拒绝（容易遗漏）
>
> **调试NetworkPolicy**：
> ```bash
> # 查看所有NetworkPolicy
> kubectl get networkpolicy -A
>
> # 查看Pod关联的NetworkPolicy
> kubectl describe pod <pod-name> | grep -A 10 "Network"
>
> # 使用工具测试连接（如curl、telnet、nc）
> ```

---

## 7.4 Pod安全策略

### 7.4.1 Pod Security Admission

### 一句话人话
**Pod Security Admission（PSA）**是K8s 1.25+的新安全标准，控制Pod的安全配置。

### 生活比喻 🔥
就像**机场的安检规则**：
- 所有人都要过安检（强制检查）
- 分三个等级：宽松（Privileged）、基准（Baseline）、受限（Restricted）
- 限制携带危险物品（特权容器、root用户等）
- 不同等级有不同限制

### 核心概念

**PSA的三种模式**：

| 模式 | 说明 | 适合场景 |
|------|------|----------|
| **Privileged** | 无限制 | 测试环境、系统级Pod |
| **Baseline** | 基础限制 | 生产环境（默认推荐） |
| **Restricted** | 严格限制 | 高安全要求环境 |

**PSA配置级别**：
- `cluster`：集群级别
- `namespace`：命名空间级别

**限制的内容**：
- 特权容器
- 宿主机路径挂载
- hostNetwork、hostPID、hostIPC
- root用户运行
- 容器Capabilities

### 实操步骤

**步骤1：给命名空间设置PSA级别**

```bash
# 设置为restricted模式（最严格）
kubectl label --overwrite ns production pod-security.kubernetes.io/enforce=restricted

# 设置为baseline模式
kubectl label --overwrite ns staging pod-security.kubernetes.io/enforce=baseline

# 设置warn模式（只警告，不拒绝）
kubectl label --overwrite ns development pod-security.kubernetes.io/warn=restricted

# 设置audit模式（审计，不拒绝）
kubectl label --overwrite ns development pod-security.kubernetes.io/audit=baseline
```

**步骤2：测试Pod Security Admission**

**特权Pod（会被拒绝）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
  namespace: production
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      privileged: true  # 特权模式
```

```bash
# 尝试创建（会被拒绝）
kubectl apply -f privileged-pod.yaml

# 错误信息：Pod violates PodSecurity "restricted:latest": privileged (container "nginx" must not set securityContext.privileged=true)
```

**安全的Pod（会被接受）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
  namespace: production
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

**查看命名空间的PSA设置**

```bash
kubectl get namespace production -o jsonpath='{.metadata.labels}' | jq .

# 输出示例：
{
  "kubernetes.io/metadata.name": "production",
  "pod-security.kubernetes.io/enforce": "restricted",
  "pod-security.kubernetes.io/warn": "baseline"
}
```

---

### 7.4.2 SecurityContext：容器安全配置

### 一句话人话
**SecurityContext**在Pod或容器级别设置安全参数，限制容器的权限。

### 生活比喻 🔥
就像**员工的工作权限配置**：
- 某些操作需要管理员权限（privileged）
- 某些人只能读不能写（readOnlyRootFilesystem）
- 禁止越权（allowPrivilegeEscalation）
- 剥离多余权限（drop capabilities）

### 实操步骤

**场景1：Pod级别的SecurityContext**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
    runAsUser: 1000          # 所有容器以1000用户运行
    runAsGroup: 3000         # 组ID
    fsGroup: 2000            # 文件系统组ID
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      allowPrivilegeEscalation: false  # 禁止提权
  - name: redis
    image: redis:7
```

**场景2：容器级别的SecurityContext（覆盖Pod级别）**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: override-security
spec:
  securityContext:
    runAsUser: 1000
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      runAsUser: 2000  # 覆盖Pod级别的设置
  - name: redis
    image: redis:7
    # 使用Pod级别的runAsUser: 1000
```

**场景3：Capabilities管理**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: capabilities-demo
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      capabilities:
        drop:
        - ALL        # 删除所有capabilities
        add:
        - NET_BIND_SERVICE  # 只添加绑定的权限
```

**场景4：只读根文件系统**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: readonly-root
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      readOnlyRootFilesystem: true  # 只读根文件系统
    volumeMounts:
    - name: tmp
      mountPath: /tmp  # 需要挂载可写目录
    - name: cache
      mountPath: /var/cache/nginx
  volumes:
  - name: tmp
    emptyDir: {}
  - name: cache
    emptyDir: {}
```

**场景5：禁止特权容器**

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: no-privilege
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    securityContext:
      privileged: false  # 禁止特权模式
      allowPrivilegeEscalation: false  # 禁止提权
```

### ⚠️ 小白易懵点

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

> **Pod Security vs SecurityContext的区别？**
> - **Pod Security Admission**：命名空间级别的强制规则（K8s 1.25+）
> - **SecurityContext**：Pod或容器级别的安全配置（所有版本）
>
> **为什么需要只读根文件系统？**
> - 防止恶意代码修改系统文件
> - 防止被入侵后植入后门
> - 增强安全性
>
> **常见的SecurityContext配置**：
> ```yaml
> securityContext:
>   runAsNonRoot: true              # 非root用户
>   allowPrivilegeEscalation: false  # 禁止提权
>   readOnlyRootFilesystem: true    # 只读根文件系统
>   capabilities:
>     drop:
>     - ALL                         # 删除所有capabilities
> ```

---

## 本章小结

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)

### 💡 一句话总结
K8s的安全体系层层设防：RBAC控制谁能做什么，ServiceAccount给Pod发身份卡，NetworkPolicy像防火墙隔离网络，Pod Security限制容器权限。遵循最小权限原则，才能既灵活又安全。

---
