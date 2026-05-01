# Java零基础小白教程（上）

![Java](https://www.coze.cn/s/Ixa1MS_kV0A/)

> 📚 本教程专为编程零基础小白设计，用最通俗易懂的方式带你走进Java的世界！

---

## 第一篇：Java基础入门

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 1.1 写给零基础的你：Java是什么？

**一句话人话解释：** Java是一门让电脑听你话的编程语言，你告诉它"做什么"，它就帮你做好。

**生活比喻 🏠：**
想象你要开一家餐厅。你不需要自己炒菜，而是招聘厨师（程序）来帮你做。你只需要写一份"菜谱"（代码），厨师就会按照菜谱做出美味的菜肴。Java就是这份"菜谱"的书写规范，让全世界的厨师（电脑）都能看懂并执行。

**技术核心 📖：**
Java由Sun公司（现Oracle）的詹姆斯·高斯林等人于1995年发明。它的核心理念是"Write Once, Run Anywhere"（一次编写，到处运行）。这意味着你用Java写的程序，可以在Windows电脑上运行，也可以在Mac电脑上运行，还可以在手机上运行——只要那个设备安装了Java虚拟机（JVM）。

**代码示例 💻：**

```java
/**
 * 这是你的第一个Java程序
 * 不用太纠结语法，先感受一下
 */
public class HelloWorld {
    public static void main(String[] args) {
        // 这行代码会在屏幕上打印文字
        System.out.println("Hello, World! 你好，世界！");
    }
}
```

**运行结果：**
```
Hello, World! 你好，世界！
```

**⚠️ 小白易懵点：**

1. **文件名必须和类名一致！** 如果你的类名叫`HelloWorld`，那么文件名必须是`HelloWorld.java`，否则编译会报错。
2. **大小写敏感！** `String`和`string`在Java里是两个完全不同的东西。
3. **每条语句以分号结尾！** 忘了分号，程序就会报错。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 1.2 JVM/JRE/JDK：三兄弟傻傻分不清？

**一句话人话解释：**
- **JVM** = 翻译官（把Java话翻译成电脑能听懂的话）
- **JRE** = 舞台（演员演戏需要舞台）
- **JDK** = 工具箱（开发Java程序需要的全套工具）

**生活比喻 🎭：**

想象你要拍一部电影：

- **JDK（Java Development Kit）** = 整个电影制片厂，包括导演、编剧、演员、摄像机、剪辑软件等全套设备。作为开发者，你需要这个。
- **JRE（Java Runtime Environment）** = 电影放映厅。拍好的电影需要在放映厅里播放，观众只需要放映厅，不需要制片厂。
- **JVM（Java Virtual Machine）** = 同声传译员。电影有普通话版、粤语版、英语版等各种版本，但无论哪个版本，观众只需要一个翻译就能听懂。JVM就是那个翻译，确保Java程序能在任何电脑上运行。

**技术核心 📖：**

| 组件 | 全称 | 作用 | 你需不需要 |
|------|------|------|------------|
| JDK | Java Development Kit | Java开发工具包 | ✅ 开发人员必备 |
| JRE | Java Runtime Environment | Java运行时环境 | 运行时需要 |
| JVM | Java Virtual Machine | Java虚拟机 | JVM内嵌在JRE中 |

它们的关系是：**JDK ⊇ JRE ⊇ JVM**

**⚠️ 小白易懵点：**

1. **下载JDK时会自带JRE和JVM**，不需要单独下载。
2. **开发需要JDK，运行只需要JRE**。但现在很多电脑预装的是JRE，如果想开发Java程序，需要确保安装了JDK。
3. **不同JDK版本底层JVM不同**，但对我们编写代码来说，用法是一样的。

**💡 一句话总结：** JDK是工具箱，JRE是舞台，JVM是翻译官。开发用JDK，运行用JRE，翻译靠JVM。

---

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 1.3 基本数据类型：Java的积木世界

**一句话人话解释：** 数据类型就是给数据贴标签，告诉电脑这个数据是什么"口味"的。

**生活比喻 🧱：**

想象你有一个乐高玩具箱：
- 有些积木是红色的（整数）
- 有些积木是蓝色的（小数）
- 有些积木是黄色的（文字）

Java里的数据类型就像这些不同颜色的积木，告诉电脑这个数据占用多大空间、能存什么内容。

**技术核心 📖：**

Java有8种基本数据类型，分为4类：

| 类型 | 所占空间 | 取值范围 | 示例 |
|------|----------|----------|------|
| **byte** | 1字节 | -128 ~ 127 | `byte age = 25;` |
| **short** | 2字节 | -32768 ~ 32767 | `short population = 3200;` |
| **int** | 4字节 | 约±21亿 | `int salary = 5000;` |
| **long** | 8字节 | 很大很大 | `long bigNumber = 999999999L;` |
| **float** | 4字节 | 单精度小数 | `float price = 19.99f;` |
| **double** | 8字节 | 双精度小数 | `double pi = 3.1415926;` |
| **char** | 2字节 | 单个字符 | `char grade = 'A';` |
| **boolean** | 1位 | true/false | `boolean isStudent = true;` |

**代码示例 💻：**

```java
public class DataTypesDemo {
    public static void main(String[] args) {
        // 整数类型
        byte smallNumber = 100;        // 小数字
        int normalNumber = 1000000;     // 普通整数（最常用）
        long bigNumber = 92233720368L;  // 大数字，记得加L
        
        // 浮点类型（小数）
        float price = 19.99f;           // 单精度，要加f
        double score = 99.5;            // 双精度（更精确）
        
        // 字符类型
        char grade = 'A';               // 单个字符，用单引号
        
        // 布尔类型
        boolean isHuman = true;         // 要么true，要么false
        
        // 打印出来看看
        System.out.println("我的年龄：" + smallNumber);
        System.out.println("我的存款：" + normalNumber);
        System.out.println("圆周率：" + score);
        System.out.println("成绩等级：" + grade);
        System.out.println("是人吗：" + isHuman);
        
        // 字符串（注意：String不是基本类型，是引用类型）
        String name = "蜡笔小新";
        System.out.println("我是：" + name);
    }
}
```

**⚠️ 小白易懵点：**

1. **整数默认是int类型**，所以写`long num = 100;`是可以的，但如果数字超过int范围，必须加`L`。
2. **小数默认是double类型**，所以写`float f = 3.14;`会报错，必须加`f`或`F`。
3. **char用单引号，String用双引号**。`'A'`是字符，"A"是字符串，完全不同！
4. **boolean只能是true或false**，不能是0或1（这和C语言不同！）。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 1.4 变量与运算符：Java的计算器

**一句话人话解释：** 变量就是存储数据的"盒子"，运算符就是操作这些盒子的"动作"。

**生活比喻 📦：**

想象你有多个收纳盒：
- 一个盒子写着"名字"，里面放着"蜡笔小新"
- 一个盒子写着"年龄"，里面放着5
- 一个盒子写着"是否爱吃青椒"，里面放着"是"

变量就是这些盒子，盒子有名字（变量名），有标签（数据类型），里面有东西（值）。

**技术核心 📖：**

**变量的声明和赋值：**

```java
// 声明一个变量
数据类型 变量名;

// 声明并赋值
数据类型 变量名 = 值;

// 先声明，后赋值
数据类型 变量名;
变量名 = 值;
```

**运算符分类：**

| 类型 | 运算符 | 说明 |
|------|--------|------|
| 算术运算符 | + - * / % | 加减乘除取模 |
| 比较运算符 | == != > < >= <= | 比较大小 |
| 逻辑运算符 | && \|\| ! | 与或非 |
| 赋值运算符 | = += -= *= /= | 赋值 |
| 三元运算符 | ? : | 条件判断 |

**代码示例 💻：**

```java
public class VariableAndOperatorDemo {
    public static void main(String[] args) {
        // ===== 变量声明 =====
        String name = "小新";
        int age = 5;
        double height = 1.1;
        boolean likesVeggies = false;
        
        // ===== 算术运算符 =====
        int a = 10, b = 3;
        System.out.println("10 + 3 = " + (a + b));   // 13
        System.out.println("10 - 3 = " + (a - b));   // 7
        System.out.println("10 * 3 = " + (a * b));  // 30
        System.out.println("10 / 3 = " + (a / b));  // 3（整数除法）
        System.out.println("10 % 3 = " + (a % b));  // 1（取余数）
        
        // ===== 比较运算符 =====
        System.out.println("10 > 3 吗？" + (10 > 3));     // true
        System.out.println("10 == 3 吗？" + (10 == 3));   // false
        System.out.println("'A' == 65 吗？" + ('A' == 65)); // true（字符对应ASCII码）
        
        // ===== 逻辑运算符 =====
        boolean isSmart = true, isLazy = false;
        System.out.println("聪明且懒？" + (isSmart && isLazy));   // false
        System.out.println("聪明或懒？" + (isSmart || isLazy));   // true
        System.out.println("不聪明？" + (!isSmart));              // false
        
        // ===== 三元运算符 =====
        int score = 85;
        String result = score >= 60 ? "及格啦！" : "不及格，要加油！";
        System.out.println(score + "分：" + result);
        
        // ===== 赋值运算符 =====
        int x = 10;
        x += 5;  // 等同于 x = x + 5，现在x是15
        System.out.println("x += 5 后，x = " + x);
        
        // ===== 自增自减 =====
        int i = 5;
        System.out.println("i++ = " + i++);  // 先用后加，输出5，i变成6
        System.out.println("++i = " + ++i);  // 先加后用，输出7，i变成7
    }
}
```

**⚠️ 小白易懵点：**

1. **`=`是赋值，`==`是比较**。`a = b`是把b的值给a，`a == b`是问a和b相等吗。
2. **`/`和`%`的区别**：`10/3=3`（取整数部分），`10%3=1`（取余数部分）。
3. **`++i`和`i++`**：`++i`是先加后用，`i++`是先用后加。如果单独一行没区别，在表达式里有区别！
4. **字符串用`+`拼接**： `"Hello" + "World"`结果是`"HelloWorld"`；`"年龄：" + 5`结果是`"年龄：5"`。

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

### 1.5 流程控制：Java的红绿灯

**一句话人话解释：** 流程控制就是让程序学会"做选择"和"重复干活"。

**生活比喻 🚦：**

想象你每天早上出门：
1. **如果**下雨了，就带伞（选择）
2. **否则**，就不带伞（另一种选择）
3. **循环**：每天早上都要刷牙，刷完一次不够，要刷到干净为止

程序也是这样，需要根据条件做选择，或者重复做某些事情。

**技术核心 📖：**

**选择结构：**
- `if...else`：如果...就...否则...
- `switch`：多选一

**循环结构：**
- `for`：已知循环次数
- `while`：未知循环次数，先判断后执行
- `do...while`：未知循环次数，先执行后判断

**跳转语句：**
- `break`：跳出整个循环
- `continue`：跳过本次循环，继续下次

**代码示例 💻：**

```java
public class ControlFlowDemo {
    public static void main(String[] args) {
        
        // ===== if-else 选择结构 =====
        int age = 5;
        
        if (age < 6) {
            System.out.println("上幼儿园");
        } else if (age < 12) {
            System.out.println("上小学");
        } else if (age < 15) {
            System.out.println("上初中");
        } else {
            System.out.println("上高中或更大");
        }
        
        // ===== switch 多选一 =====
        String day = "周一";
        switch (day) {
            case "周一":
            case "周二":
            case "周三":
            case "周四":
            case "周五":
                System.out.println("今天上班日");
                break;
            case "周六":
            case "周日":
                System.out.println("今天休息日");
                break;
            default:
                System.out.println("什么日子？");
        }
        
        // ===== for 循环（已知次数） =====
        System.out.println("\n=== for循环：打印1到5 ===");
        for (int i = 1; i <= 5; i++) {
            System.out.println("第" + i + "次：加油！");
        }
        
        // ===== while 循环（未知次数） =====
        System.out.println("\n=== while循环：猜数字 ===");
        int target = 7;
        int guess = 0;
        while (guess != target) {
            System.out.println("猜一个数字：" + guess);
            guess++;  // 假装在猜
        }
        System.out.println("猜对了！答案是" + guess);
        
        // ===== do-while 循环（至少执行一次） =====
        System.out.println("\n=== do-while循环 ===");
        int count = 1;
        do {
            System.out.println("第" + count + "次执行");
            count++;
        } while (count <= 3);
        
        // ===== break 和 continue =====
        System.out.println("\n=== break：找到第一个偶数就停下 ===");
        for (int i = 1; i <= 10; i++) {
            if (i % 2 == 0) {
                System.out.println("找到偶数：" + i);
                break;  // 跳出整个循环
            }
        }
        
        System.out.println("\n=== continue：跳过所有偶数 ===");
        for (int i = 1; i <= 5; i++) {
            if (i % 2 == 0) {
                continue;  // 跳过本次循环，继续下次
            }
            System.out.println("奇数：" + i);
        }
        
        // ===== 嵌套循环：打印九九乘法表 =====
        System.out.println("\n=== 九九乘法表 ===");
        for (int i = 1; i <= 9; i++) {
            for (int j = 1; j <= i; j++) {
                System.out.print(j + "×" + i + "=" + (i*j) + "\t");
            }
            System.out.println();  // 换行
        }
    }
}
```

**⚠️ 小白易懵点：**

1. **if后面的括号里必须是boolean值**：`if(x = 5)`是错误的，应该是`if(x == 5)`。
2. **switch只能判断byte、short、int、char、String（Java7+）、enum**。不能判断double、boolean！
3. **每个case后面要加break**，否则会"穿透"到下一个case（有时候可以利用这个特性）。
4. **for循环的三个部分都可以省略**，但分号不能省：`for(;;)`表示无限循环。
5. **while和do...while的区别**：while先判断后执行，可能一次都不执行；do...while先执行后判断，至少执行一次。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 1.6 数组：Java的集装箱

**一句话人话解释：** 数组就是一组排排坐的数据，用同一个名字，但每个位置有编号。

**生活比喻 📦：**

想象一个火车车厢：
- 车厢有固定数量的座位（比如8个）
- 每个座位都有编号（0号、1号、2号...）
- 所有人坐同一节车厢，但坐在不同的座位上

数组就像这节车厢，是一个固定大小的、连续的数据集合。

**技术核心 📖：**

```java
// 声明数组
数据类型[] 数组名;

// 创建数组
数组名 = new 数据类型[长度];

// 声明并创建
数据类型[] 数组名 = new 数据类型[长度];

// 直接赋值（知道具体内容）
数据类型[] 数组名 = {值1, 值2, 值3, ...};
```

**代码示例 💻：**

```java
public class ArrayDemo {
    public static void main(String[] args) {
        
        // ===== 创建数组 =====
        int[] scores = new int[5];  // 创建一个能存5个整数的数组
        scores[0] = 90;            // 给第一个位置赋值
        scores[1] = 85;
        // 其他位置默认是0
        
        // ===== 直接赋值 =====
        String[] fruits = {"苹果", "香蕉", "橙子", "葡萄"};
        
        // ===== 数组属性：length =====
        System.out.println("分数数组长度：" + scores.length);  // 5
        System.out.println("水果数组长度：" + fruits.length);  // 4
        
        // ===== 遍历数组 =====
        System.out.println("\n=== 打印所有水果 ===");
        for (int i = 0; i < fruits.length; i++) {
            System.out.println("第" + i + "个水果：" + fruits[i]);
        }
        
        // ===== 增强for循环 =====
        System.out.println("\n=== 增强for循环 ===");
        for (String fruit : fruits) {
            System.out.println("水果：" + fruit);
        }
        
        // ===== 数组工具类 Arrays =====
        int[] numbers = {3, 1, 4, 1, 5, 9, 2, 6};
        java.util.Arrays.sort(numbers);  // 排序
        System.out.println("\n排序后：" + java.util.Arrays.toString(numbers));
        
        // ===== 二维数组 =====
        System.out.println("\n=== 二维数组：打印矩阵 ===");
        int[][] matrix = {
            {1, 2, 3},
            {4, 5, 6},
            {7, 8, 9}
        };
        for (int i = 0; i < matrix.length; i++) {
            for (int j = 0; j < matrix[i].length; j++) {
                System.out.print(matrix[i][j] + "\t");
            }
            System.out.println();
        }
        
        // ===== 常见操作：求最大值 =====
        System.out.println("\n=== 求最大值 ===");
        int[] nums = {12, 45, 67, 23, 89, 34};
        int max = nums[0];
        for (int i = 1; i < nums.length; i++) {
            if (nums[i] > max) {
                max = nums[i];
            }
        }
        System.out.println("最大值是：" + max);
        
        // ===== 常见操作：数组反转 =====
        System.out.println("\n=== 数组反转 ===");
        int[] original = {1, 2, 3, 4, 5};
        int left = 0, right = original.length - 1;
        while (left < right) {
            int temp = original[left];
            original[left] = original[right];
            original[right] = temp;
            left++;
            right--;
        }
        System.out.println("反转后：" + java.util.Arrays.toString(original));
    }
}
```

**⚠️ 小白易懵点：**

1. **数组下标从0开始！** 第一个元素是`arr[0]`，不是`arr[1]`。
2. **数组长度固定不变！** 创建后不能增加或减少长度。如果需要动态大小，用`ArrayList`。
3. **数组下标不能越界！** 如果数组长度是5，访问`arr[5]`会报`ArrayIndexOutOfBoundsException`。
4. **数组是引用类型！** `int[] arr`声明的是一个引用，指向堆内存中的实际数组。

![编码](https://www.coze.cn/s/PIa3Uh8C3zw/)

### 1.7 字符串：Java的文字魔法

**一句话人话解释：** 字符串就是用双引号包起来的一串字符，Java里字符串是对象，有超多功能。

**生活比喻 📝：**

想象你有一本日记本：
- 日记本就是字符串
- 日记本的每一页就是一个字符
- 日记本有页码（索引）
- 日记本有各种功能：查字数、找错字、剪贴复制等

**技术核心 📖：**

String类的常用方法：

| 方法 | 说明 | 示例 |
|------|------|------|
| length() | 获取长度 | `"hello".length()` → 5 |
| charAt(index) | 获取指定位置字符 | `"hello".charAt(1)` → 'e' |
| substring(start, end) | 截取子串 | `"hello".substring(1,3)` → "el" |
| indexOf(str) | 查找位置 | `"hello".indexOf("l")` → 2 |
| equals(str) | 比较内容 | `"hello".equals("hello")` → true |
| toUpperCase() | 转大写 | `"hello".toUpperCase()` → "HELLO" |
| toLowerCase() | 转小写 | `"Hello".toLowerCase()` → "hello" |
| trim() | 去除首尾空格 | `" hello ".trim()` → "hello" |
| split(regex) | 分割字符串 | `"a,b,c".split(",")` → ["a","b","c"] |
| replace(old, new) | 替换 | `"hello".replace("l","L")` → "heLLo" |

**代码示例 💻：**

```java
public class StringDemo {
    public static void main(String[] args) {
        
        // ===== 创建字符串 =====
        String s1 = "Hello";              // 直接赋值（推荐）
        String s2 = new String("Hello");  // 用构造器创建（不推荐）
        
        // ===== 常用方法 =====
        String str = "  Hello, World!  ";
        System.out.println("原字符串：'" + str + "'");
        System.out.println("长度：" + str.length());
        System.out.println("去空格后：'" + str.trim() + "'");
        System.out.println("转大写：" + str.trim().toUpperCase());
        System.out.println("转小写：" + str.trim().toLowerCase());
        
        // ===== 字符串查找 =====
        String text = "Java is great! I love Java!";
        System.out.println("\n原文字：" + text);
        System.out.println("indexOf('Java')：" + text.indexOf("Java"));  // 0
        System.out.println("lastIndexOf('Java')：" + text.lastIndexOf("Java"));  // 18
        System.out.println("包含'love'吗：" + text.contains("love"));  // true
        System.out.println("以'Java'开头吗：" + text.startsWith("Java"));  // true
        System.out.println("以'!'结尾吗：" + text.endsWith("!"));  // true
        
        // ===== 字符串截取 =====
        String url = "https://www.example.com/index.html";
        System.out.println("\nURL：" + url);
        System.out.println("协议：" + url.substring(0, 5));
        System.out.println("域名：" + url.substring(8, 22));
        
        // ===== 字符串分割 =====
        String csv = "苹果,香蕉,橙子,葡萄";
        String[] fruits = csv.split(",");
        System.out.println("\n分割后的水果：");
        for (String fruit : fruits) {
            System.out.println("- " + fruit);
        }
        
        // ===== 字符串替换 =====
        String sentence = "I like cat";
        System.out.println("\n原句：" + sentence);
        System.out.println("替换后：" + sentence.replace("cat", "dog"));
        
        // ===== 字符串拼接 =====
        String s3 = "Hello";
        String s4 = "World";
        // 方式1：用 + （最常用）
        System.out.println("\n用+拼接：" + s3 + ", " + s4 + "!");
        // 方式2：用 concat
        System.out.println("用concat：" + s3.concat(", ").concat(s4).concat("!"));
        
        // ===== 字符串比较 =====
        String a = "hello";
        String b = "hello";
        String c = new String("hello");
        System.out.println("\n=== 字符串比较 ===");
        System.out.println("a == b：" + (a == b));      // true（常量池）
        System.out.println("a == c：" + (a == c));      // false（不同对象）
        System.out.println("a.equals(c)：" + a.equals(c)); // true（内容相同）
        
        // ===== StringBuilder（可变字符串，高效拼接） =====
        System.out.println("\n=== StringBuilder 高效拼接 ===");
        long startTime = System.currentTimeMillis();
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 10000; i++) {
            sb.append("item");
        }
        long endTime = System.currentTimeMillis();
        System.out.println("拼接10000次耗时：" + (endTime - startTime) + "ms");
        System.out.println("结果长度：" + sb.length());
    }
}
```

**⚠️ 小白易懵点：**

1. **String是引用类型，但用起来像基本类型**。`String s = "hello"`这种直接赋值，会复用字符串常量池。
2. **字符串比较用equals()，不要用==**！`==`比较的是地址（是否同一个对象），`equals()`比较的是内容。
3. **String是不可变对象**！每次"修改"都会创建新对象。如果需要频繁修改，用`StringBuilder`。
4. **split()要注意特殊字符**。用`.`、`|`、`\`等做分隔符时需要转义。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 1.8 方法：Java的独立王国

**一句话人话解释：** 方法就是一段可以重复使用的代码，给它起个名字，下次想用直接叫名字就行。

**生活比喻 🏠：**

想象你家的厨房：
- 有一个"煮面"的方法：放水→烧开→放面→煮熟→捞出
- 每次想吃面，不用重新说一遍步骤，只需要喊一声"煮面！"
- 方法可以接受参数（想吃什么面），也可以返回结果（煮好的一碗面）

**技术核心 📖：**

```java
// 方法的基本结构
访问修饰符 返回类型 方法名(参数列表) {
    // 方法体
    return 结果;
}
```

**代码示例 💻：**

```java
public class MethodDemo {
    
    // ===== 无参数无返回值 =====
    public static void sayHello() {
        System.out.println("你好！我是方法！");
    }
    
    // ===== 有参数无返回值 =====
    public static void greet(String name) {
        System.out.println("你好，" + name + "！");
    }
    
    // ===== 有参数有返回值 =====
    public static int add(int a, int b) {
        return a + b;
    }
    
    // ===== 方法重载：同名不同参数 =====
    public static int add(int a, int b, int c) {
        return a + b + c;
    }
    
    public static double add(double a, double b) {
        return a + b;
    }
    
    // ===== 可变参数 =====
    public static int sum(int... numbers) {
        int total = 0;
        for (int n : numbers) {
            total += n;
        }
        return total;
    }
    
    // ===== 主方法 =====
    public static void main(String[] args) {
        
        // 调用无参数方法
        sayHello();
        
        // 调用有参数方法
        greet("蜡笔小新");
        greet("风间彻");
        
        // 调用有返回值方法
        int result = add(10, 20);
        System.out.println("10 + 20 = " + result);
        
        // 调用重载方法
        System.out.println("三个数相加：" + add(1, 2, 3));
        System.out.println("小数相加：" + add(1.5, 2.5));
        
        // 调用可变参数方法
        System.out.println("可变参数求和：" + sum(1, 2, 3, 4, 5));
        System.out.println("可变参数求和：" + sum(10, 20));
        
        // ===== 递归：方法调用自己 =====
        System.out.println("\n=== 递归：计算阶乘 ===");
        System.out.println("5! = " + factorial(5));  // 5*4*3*2*1 = 120
    }
    
    // 递归方法：计算阶乘
    public static int factorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * factorial(n - 1);
    }
}
```

**⚠️ 小白易懵点：**

1. **方法重载只看参数列表**，和返回类型、参数名无关。`add(int a, int b)`和`add(int x, int y)`是同一个方法。
2. **return只能返回一个值**，如果需要返回多个，用数组或自定义对象。
3. **可变参数要放在最后**，一个方法只能有一个可变参数。
4. **递归要有终止条件**，否则会无限递归导致栈溢出（StackOverflowError）。

**💡 一句话总结：** 方法是代码的封装体，让你一次编写、多次使用。重载让同名方法处理不同参数，递归是方法自己调用自己。

---

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

## 第二篇：面向对象编程

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 2.1 类与对象：Java的造物主

**一句话人话解释：** 类是图纸，对象是根据图纸造出来的实物。

**生活比喻 🏗️：**

想象你要造一辆汽车：
- **类**就是汽车设计图纸，上面写着：汽车有4个轮子、1个发动机、1个方向盘，能前进、后退、刹车...
- **对象**就是根据这张图纸造出来的真实汽车，你可以开来开去
- 一张图纸可以造很多辆汽车，它们都是同一类，但各有各的车牌号（身份）

**技术核心 📖：**

```java
// 定义一个类
public class 类名 {
    // 属性（特征）
    数据类型 属性名;
    
    // 方法（行为）
    public 返回类型 方法名() {
        // 方法体
    }
    
    // 构造器（创建对象）
    public 类名() {
    }
}

// 创建对象
类名 对象名 = new 类名();
```

**代码示例 💻：**

```java
/**
 * 定义一个"学生"类
 */
public class Student {
    
    // ===== 属性（特征） =====
    String name;      // 姓名
    int age;          // 年龄
    String school;   // 学校
    static String teacherName = "美伢老师";  // 静态属性，全班共享
    
    // ===== 构造器 =====
    // 无参构造器
    public Student() {
        System.out.println("创建了一个学生！");
    }
    
    // 有参构造器
    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // ===== 方法（行为） =====
    public void study() {
        System.out.println(name + "正在学习...");
    }
    
    public void play() {
        System.out.println(name + "在玩耍...");
    }
    
    public String introduce() {
        return "大家好，我叫" + name + "，今年" + age + "岁，来自" + school;
    }
    
    // ===== getter和setter =====
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public int getAge() {
        return age;
    }
    
    public void setAge(int age) {
        if (age > 0 && age < 150) {  // 简单校验
            this.age = age;
        }
    }
    
    // ===== main方法用于测试 =====
    public static void main(String[] args) {
        // 创建对象
        Student xiaoXin = new Student("蜡笔小新", 5);
        Student fengJian = new Student("风间彻", 5);
        
        // 设置属性
        xiaoXin.school = "双叶幼稚园";
        fengJian.school = "双叶幼稚园";
        
        // 调用方法
        xiaoXin.study();
        xiaoXin.play();
        
        System.out.println(xiaoXin.introduce());
        System.out.println(fengJian.introduce());
        
        // 访问静态属性
        System.out.println("老师是：" + Student.teacherName);
        
        // 使用setter
        xiaoXin.setAge(6);
        System.out.println("小新长大了，现在是" + xiaoXin.getAge() + "岁");
    }
}
```

**⚠️ 小白易懵点：**

1. **类名首字母大写**，方法名和变量名首字母小写，这是Java的命名规范。
2. **`this`关键字**表示当前对象，用于区分局部变量和成员变量同名的情况。
3. **构造器没有返回类型**，连void都没有！
4. **每个类都应该有无参构造器**，即使你定义了有参构造器，编译器也不会自动生成无参构造器。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 2.2 封装：Java的保险箱

**一句话人话解释：** 封装就是给数据加把锁，不想让你直接改，我就给你提供专门的开关。

**生活比喻 🔐：**

想象你的手机：
- 你的手机有一个"电池"（属性）
- 但你不应该直接拆开手机去改电池电量
- 相反，你有"充电"功能（方法）来增加电量，有"设置低电量模式"来减少消耗
- 这样手机厂商就保护了内部数据，只让你通过安全的方式操作

**技术核心 📖：**

封装的三步走：
1. **属性私有化**：`private`修饰属性
2. **提供getter和setter**：`public`修饰的方法
3. **setter里可以加校验**：保护数据安全

**代码示例 💻：**

```java
/**
 * 银行账户类 - 演示封装
 */
public class BankAccount {
    
    // ===== 第一步：属性私有化 =====
    private String accountNumber;  // 账号（私有，外部不能直接访问）
    private double balance;        // 余额（私有）
    private String password;       // 密码（私有）
    
    // ===== 第二步：构造器 =====
    public BankAccount(String accountNumber, String password) {
        this.accountNumber = accountNumber;
        this.password = password;
        this.balance = 0.0;  // 新账户余额为0
    }
    
    // ===== 第三步：提供公共方法 =====
    
    // 存钱（带校验）
    public void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            System.out.println("存款成功！当前余额：" + balance);
        } else {
            System.out.println("存款金额必须大于0！");
        }
    }
    
    // 取钱（带校验）
    public void withdraw(double amount, String pwd) {
        // 校验密码
        if (!this.password.equals(pwd)) {
            System.out.println("密码错误！取款失败！");
            return;
        }
        
        // 校验金额
        if (amount <= 0) {
            System.out.println("取款金额必须大于0！");
        } else if (amount > balance) {
            System.out.println("余额不足！当前余额：" + balance);
        } else {
            balance -= amount;
            System.out.println("取款成功！取出：" + amount + "，当前余额：" + balance);
        }
    }
    
    // 查询余额（需要密码）
    public void checkBalance(String pwd) {
        if (this.password.equals(pwd)) {
            System.out.println("账号：" + accountNumber + "，余额：" + balance);
        } else {
            System.out.println("密码错误！");
        }
    }
    
    // ===== getter方法（只读某些属性） =====
    public String getAccountNumber() {
        return accountNumber;
    }
    
    // 注意：没有提供setAccountNumber方法，因为账号不应该被修改
    
    // ===== 金额的getter和setter被省略，只提供专门的存钱取钱方法 =====
    // 这是因为金额需要业务逻辑保护
}
```

**测试类：**

```java
public class BankAccountTest {
    public static void main(String[] args) {
        // 创建账户
        BankAccount account = new BankAccount("6222021234567890", "123456");
        
        // 存款
        account.deposit(1000);
        
        // 取钱
        account.withdraw(500, "123456");
        
        // 查余额
        account.checkBalance("123456");
        
        // 尝试错误密码
        account.withdraw(100, "wrong");
        
        // 尝试取太多钱
        account.withdraw(10000, "123456");
        
        // 直接访问会报错！
        // account.balance = 1000000;  // 编译错误！balance是私有的
    }
}
```

**⚠️ 小白易懵点：**

1. **private不是"没有"，而是"不让外部访问"**。同一个类里仍然可以访问。
2. **getter和setter不是必须的**，根据业务需要决定是否提供、提供哪些。
3. **封装不只是private+getter/setter**，更重要的是在方法里加业务逻辑校验。
4. **可以用IDE自动生成**getter/setter，不用手写。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 2.3 继承：Java的家族传承

**一句话人话解释：** 继承就是儿子继承父亲的特征，不用重新说一遍，天然的。

**生活比喻 👨‍👦：**

想象一个家庭：
- 爸爸会走路、吃饭、说话
- 儿子出生后，自然就会走路、吃饭、说话（继承）
- 儿子还可以学新技能，比如骑自行车（扩展）
- 儿子也可以改进爸爸的方法，比如走路更快（重写）

**技术核心 📖：**

```java
// 父类
public class 父类 {
    // 公共属性和方法
}

// 子类
public class 子类 extends 父类 {
    // 子类特有的属性和方法
}
```

**代码示例 💻：**

```java
/**
 * 父类：动物
 */
public class Animal {
    protected String name;  // 名字（protected：子类可以访问）
    protected int age;      // 年龄
    
    public Animal(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    // 动物的行为
    public void eat() {
        System.out.println(name + "在吃东西...");
    }
    
    public void sleep() {
        System.out.println(name + "在睡觉...");
    }
    
    public void showInfo() {
        System.out.println(name + "，" + age + "岁");
    }
    
    // 父类的方法，子类可以重写
    public void makeSound() {
        System.out.println(name + "发出声音...");
    }
}

/**
 * 子类：狗
 */
class Dog extends Animal {
    private String breed;  // 品种
    
    public Dog(String name, int age, String breed) {
        super(name, age);  // 调用父类构造器
        this.breed = breed;
    }
    
    // 子类特有的方法
    public void bark() {
        System.out.println(name + "汪汪叫！");
    }
    
    public void fetch() {
        System.out.println(name + "在捡球...");
    }
    
    // 重写父类的方法
    @Override  // @Override注解不是必须的，但加上可以检查是否真的重写了
    public void makeSound() {
        System.out.println(name + "汪汪汪！");
    }
    
    // 重写父类的方法，保留父类行为
    @Override
    public void eat() {
        super.eat();  // 调用父类的eat
        System.out.println(name + "吃完了狗粮...");
    }
}

/**
 * 子类：猫
 */
class Cat extends Animal {
    private boolean indoor;  // 是否室内猫
    
    public Cat(String name, int age, boolean indoor) {
        super(name, age);
        this.indoor = indoor;
    }
    
    // 猫特有的方法
    public void meow() {
        System.out.println(name + "喵呜~");
    }
    
    public void scratch() {
        System.out.println(name + "在挠痒痒...");
    }
    
    // 重写父类的方法
    @Override
    public void makeSound() {
        System.out.println(name + "喵喵喵！");
    }
}

/**
 * 测试继承
 */
public class InheritanceDemo {
    public static void main(String[] args) {
        // 创建子类对象
        Dog dog = new Dog("旺财", 3, "金毛");
        Cat cat = new Cat("咪咪", 2, true);
        
        // 调用继承来的方法
        dog.eat();      // 来自父类
        dog.sleep();    // 来自父类
        dog.showInfo(); // 来自父类
        
        // 调用子类自己的方法
        dog.bark();     // 狗自己的
        dog.fetch();    // 狗自己的
        
        // 调用重写的方法
        dog.makeSound();  // 输出"旺财汪汪汪！"（子类重写后的）
        
        System.out.println("\n--- 猫的信息 ---");
        cat.meow();
        cat.scratch();
        cat.makeSound();
        
        // ===== 多态的体现：父类引用指向子类对象 =====
        System.out.println("\n--- 多态演示 ---");
        Animal animal1 = new Dog("大黄", 2, "土狗");
        Animal animal2 = new Cat("小白", 1, false);
        
        // 编译时看左边类型，运行时看右边对象
        animal1.makeSound();  // 输出"大黄汪汪汪！"
        animal2.makeSound();  // 输出"小白喵喵喵！"
    }
}
```

**⚠️ 小白易懵点：**

1. **Java只有单继承**！一个类只能有一个父类，但可以有多个子类。
2. **`extends`关键字表示继承**，不是"扩展"，不要用错。
3. **子类构造器必须调用父类构造器**，用`super()`。如果父类有无参构造器，可以省略`super()`。
4. **private成员不能被继承**，但可以通过父类的public/protected方法访问。
5. **`@Override`注解**建议加上，它能帮你检查是否真的重写了父类方法。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 2.4 多态：Java的一面千人

**一句话人话解释：** 多态就是同一个方法调用，不同对象有不同的反应。

**生活比喻 🎭：**

想象一个"发令枪响"场景：
- 短跑运动员听到枪响 → 起跑
- 裁判听到枪响 → 发指令
- 观众听到枪响 → 欢呼
- 小孩听到枪响 → 捂住耳朵

都是"听到枪响"这个方法，但不同的人反应不同！

**技术核心 📖：**

多态的三种形式：
1. **编译时多态**：方法重载（同一个类，同名不同参）
2. **运行时多态**：方法重写 + 父类引用指向子类对象
3. **接口多态**：后面讲接口时再说

**代码示例 💻：**

```java
/**
 * 演示多态：不同形状的面积计算
 */

// 父类：形状
abstract class Shape {
    protected String color;
    
    public Shape(String color) {
        this.color = color;
    }
    
    // 抽象方法：计算面积（子类必须实现）
    public abstract double calculateArea();
    
    // 具体方法：显示颜色
    public void showColor() {
        System.out.println("颜色：" + color);
    }
}

// 子类：圆形
class Circle extends Shape {
    private double radius;
    
    public Circle(String color, double radius) {
        super(color);
        this.radius = radius;
    }
    
    @Override
    public double calculateArea() {
        return Math.PI * radius * radius;
    }
}

// 子类：矩形
class Rectangle extends Shape {
    private double width;
    private double height;
    
    public Rectangle(String color, double width, double height) {
        super(color);
        this.width = width;
        this.height = height;
    }
    
    @Override
    public double calculateArea() {
        return width * height;
    }
}

// 子类：三角形
class Triangle extends Shape {
    private double base;
    private double height;
    
    public Triangle(String color, double base, double height) {
        super(color);
        this.base = base;
        this.height = height;
    }
    
    @Override
    public double calculateArea() {
        return 0.5 * base * this.height;
    }
}

/**
 * 多态测试
 */
public class PolymorphismDemo {
    
    // 方法参数使用父类类型，可以接受任何子类对象
    public static void printArea(Shape shape) {
        System.out.println("形状：" + shape.getClass().getSimpleName());
        shape.showColor();
        System.out.println("面积：" + shape.calculateArea());
        System.out.println("---");
    }
    
    public static void main(String[] args) {
        // 正常创建对象
        Circle circle = new Circle("红色", 5);
        Rectangle rect = new Rectangle("蓝色", 4, 6);
        Triangle triangle = new Triangle("黄色", 3, 4);
        
        // ===== 多态：父类引用指向子类对象 =====
        Shape shape1 = new Circle("绿色", 10);
        Shape shape2 = new Rectangle("紫色", 5, 8);
        
        // 调用的是子类重写后的方法
        System.out.println("圆形面积：" + shape1.calculateArea());  // 实际调用Circle的
        System.out.println("矩形面积：" + shape2.calculateArea());  // 实际调用Rectangle的
        
        // ===== 多态数组 =====
        System.out.println("\n=== 多态数组 ===");
        Shape[] shapes = {
            new Circle("红色", 3),
            new Rectangle("蓝色", 4, 5),
            new Triangle("黄色", 6, 8)
        };
        
        for (Shape s : shapes) {
            System.out.println(s.getClass().getSimpleName() + 
                             " 面积 = " + s.calculateArea());
        }
        
        // ===== 多态参数 =====
        System.out.println("\n=== 多态参数 ===");
        printArea(new Circle("白色", 2));
        printArea(new Rectangle("黑色", 3, 4));
        printArea(new Triangle("粉色", 5, 6));
    }
}
```

**⚠️ 小白易懵点：**

1. **多态的前提是继承或实现关系**，没有父子类关系就不会有多态。
2. **父类引用只能调用父类有的方法**，子类特有的方法不能直接调用。
3. **成员变量没有多态**，看的是左边类型；方法才有运行时多态，看的是右边对象。
4. **不能访问子类新增的属性**。`Animal a = new Dog()`，`a.breed`是编译错误的。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 2.5 抽象类与接口：Java的契约

**一句话人话解释：** 抽象类和接口都是用来定义规范的，区别是抽象类是"不完全的类"，接口是"纯规范"。

**生活比喻 📋：**

**抽象类**像是一个**半成品模具**：
- 已经有了形状和部分功能
- 但还有一些没完成，需要子类来补全
- 例如：手机模具已经有屏幕和按键的形状，但CPU型号可以不同

**接口**像是一份**职位要求清单**：
- 只规定要会什么，不规定怎么实现
- 一个类可以实现多个接口（就像一个人可以应聘多个职位）
- 例如：要求"会英语、会开车、会游泳"，具体怎么学是你自己的事

**技术核心 📖：**

| 对比项 | 抽象类 | 接口 |
|--------|--------|------|
| 关键字 | `abstract class` | `interface` |
| 继承/实现 | `extends`（单继承） | `implements`（可多实现） |
| 属性 | 可以有各种属性 | 只能是`public static final`常量 |
| 方法 | 抽象方法+具体方法 | JDK7前只能是抽象方法，JDK8+可有default |
| 构造器 | 可以有 | 不能有 |
| 多继承 | 不支持 | 支持 |

**代码示例 💻：**

```java
/**
 * 接口示例：会飞的
 */
interface Flyable {
    // 接口中的属性默认是 public static final（常量）
    int MAX_SPEED = 1000;
    
    // JDK7及以前：抽象方法
    void fly();
    
    // JDK8+：default方法（有默认实现）
    default void land() {
        System.out.println("安全着陆！");
    }
    
    // JDK8+：静态方法
    static void checkSpeed() {
        System.out.println("检查速度限制...");
    }
}

/**
 * 接口示例：会叫的
 */
interface Speakable {
    void speak();
}

/**
 * 抽象类：动物
 */
abstract class Animal {
    protected String name;
    
    public Animal(String name) {
        this.name = name;
    }
    
    // 抽象方法：子类必须实现
    public abstract void eat();
    
    // 具体方法
    public void sleep() {
        System.out.println(name + "在睡觉...");
    }
}

/**
 * 鸟类：继承抽象类 + 实现接口
 */
class Bird extends Animal implements Flyable, Speakable {
    public Bird(String name) {
        super(name);
    }
    
    @Override
    public void eat() {
        System.out.println(name + "在吃虫子...");
    }
    
    @Override
    public void fly() {
        System.out.println(name + "在天空飞翔...");
    }
    
    @Override
    public void speak() {
        System.out.println(name + "在唱歌：叽叽喳喳~");
    }
}

/**
 * 飞机：只实现接口（不继承任何类）
 */
class Airplane implements Flyable {
    private String model;
    
    public Airplane(String model) {
        this.model = model;
    }
    
    @Override
    public void fly() {
        System.out.println(model + "在万米高空飞行...");
    }
}

/**
 * 测试抽象类和接口
 */
public class AbstractInterfaceDemo {
    public static void main(String[] args) {
        // 创建实现类的对象
        Bird bird = new Bird("小燕子");
        
        // 调用继承自抽象类的方法
        bird.eat();
        bird.sleep();
        
        // 调用实现自接口的方法
        bird.fly();
        bird.speak();
        bird.land();  // 使用接口的default方法
        
        // ===== 多态：接口引用指向实现类对象 =====
        System.out.println("\n=== 多态 ===");
        Flyable f1 = new Bird("老鹰");
        Flyable f2 = new Airplane("波音747");
        
        f1.fly();  // 调用的是Bird的fly
        f2.fly();  // 调用的是Airplane的fly
        
        // 使用接口的静态方法
        Flyable.checkSpeed();
        
        // ===== 面向接口编程 =====
        System.out.println("\n=== 面向接口编程 ===");
        printFlying(new Bird("麻雀"));
        printFlying(new Airplane("歼20"));
    }
    
    // 参数是接口类型，可以接受任何实现类
    public static void printFlying(Flyable f) {
        System.out.println("---");
        f.fly();
        f.land();
    }
}
```

**⚠️ 小白易懵点：**

1. **抽象类不能实例化**！`new Animal()`是错误的，但`new Bird()`是可以的。
2. **抽象方法必须被实现**，除非子类也是抽象类。
3. **接口的实现类必须实现所有抽象方法**，除非实现类也是抽象的。
4. **一个类可以同时继承一个类和实现多个接口**：
   ```java
   class MyClass extends ParentClass implements Interface1, Interface2 {
       // ...
   }
   ```
5. **接口没有构造器**，所以`implements`时不需要调用父接口的构造器。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 2.6 内部类与匿名类：Java的套娃

**一句话人话解释：** 内部类就是定义在另一个类里面的类，匿名类就是没有名字的临时类。

**生活比喻 🎁：**

想象一个俄罗斯套娃：
- 大娃娃里套着小娃娃
- 小娃娃只知道自己的事，也能看到大娃娃的事
- 有时候你不想给娃娃起名字，就是临时用一下

**技术核心 📖：**

内部类的四种类型：
1. **成员内部类**：写在类中间，作为成员
2. **静态内部类**：用static修饰的内部类
3. **局部内部类**：写在方法里
4. **匿名内部类**：没有名字的内部类，常用于回调

**代码示例 💻：**

```java
/**
 * 外部类
 */
public class OuterClass {
    private String outerName = "外部类";
    public int outerNum = 100;
    
    // ===== 1. 成员内部类 =====
    public class InnerClass {
        private String innerName = "内部类";
        
        public void innerMethod() {
            System.out.println("我是内部类！");
            // 内部类可以访问外部类的所有成员
            System.out.println("外部类名称：" + outerName);
        }
    }
    
    // ===== 2. 静态内部类 =====
    public static class StaticInnerClass {
        public void method() {
            System.out.println("我是静态内部类！");
            // 静态内部类只能访问外部类的静态成员
            // System.out.println(outerName); // 错误！
            System.out.println("外部类静态成员：" + outerNum);
        }
    }
    
    // ===== 外部类的方法 =====
    public void outerMethod() {
        // 在外部类的方法里创建内部类对象
        InnerClass inner = new InnerClass();
        inner.innerMethod();
    }
    
    // ===== 3. 方法内的局部内部类 =====
    public void localClassMethod() {
        class LocalClass {
            public void print() {
                System.out.println("我是局部内部类，只在这个方法里有效");
            }
        }
        LocalClass lc = new LocalClass();
        lc.print();
    }
    
    // ===== 4. 匿名内部类 =====
    public void anonymousClassDemo() {
        // 创建一个匿名类，实现接口
        Runnable runnable = new Runnable() {
            @Override
            public void run() {
                System.out.println("匿名内部类：Runnable实现");
            }
        };
        runnable.run();
        
        // 匿名内部类实现抽象类
        AbstractAnimal animal = new AbstractAnimal("匿名动物") {
            @Override
            public void eat() {
                System.out.println("匿名动物在吃东西...");
            }
        };
        animal.eat();
        
        // 常用场景：线程
        Thread t = new Thread(new Runnable() {
            @Override
            public void run() {
                System.out.println("匿名内部类创建线程");
            }
        });
        t.start();
        
        // JDK8+ lambda简化（Runnable是函数式接口）
        Thread t2 = new Thread(() -> System.out.println("Lambda简化线程"));
        t2.start();
    }
    
    public static void main(String[] args) {
        OuterClass outer = new OuterClass();
        
        // ===== 访问成员内部类 =====
        System.out.println("=== 成员内部类 ===");
        // 方式1：在外部类内部直接访问
        outer.outerMethod();
        
        // 方式2：在外部类外部访问
        OuterClass.InnerClass inner = outer.new InnerClass();
        inner.innerMethod();
        
        // ===== 访问静态内部类 =====
        System.out.println("\n=== 静态内部类 ===");
        OuterClass.StaticInnerClass staticInner = new OuterClass.StaticInnerClass();
        staticInner.method();
        
        // ===== 局部内部类 =====
        System.out.println("\n=== 局部内部类 ===");
        outer.localClassMethod();
        
        // ===== 匿名内部类 =====
        System.out.println("\n=== 匿名内部类 ===");
        outer.anonymousClassDemo();
    }
}

/**
 * 用于匿名内部类演示的抽象类
 */
abstract class AbstractAnimal {
    protected String name;
    
    public AbstractAnimal(String name) {
        this.name = name;
    }
    
    public abstract void eat();
}
```

**⚠️ 小白易懵点：**

1. **内部类可以访问外部类的所有成员**，包括private成员。
2. **外部类访问内部类**，需要先创建内部类对象。
3. **匿名内部类只能使用一次**，适合一次性使用的场景（如事件监听）。
4. **匿名内部类不能有构造器**，参数只能传给父类的构造器。
5. **匿名内部类会悄悄继承一个类或实现一个接口**。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 2.7 设计模式入门：Java的套路

**一句话人话解释：** 设计模式就是前辈们总结的编程"套路"，遇到特定问题用特定套路解决。

**生活比喻 🎯：**

想象你要组装家具：
- 说明书上有步骤1、2、3...你照着做就行
- 设计模式就是编程的"说明书"，告诉你什么场景用什么方法

**技术核心 📖：**

常见的设计模式：
1. **单例模式**：确保只有一个实例
2. **工厂模式**：统一创建对象
3. **观察者模式**：一对多的依赖关系
4. **策略模式**：可以互换的算法

**代码示例 💻：**

```java
/**
 * ===== 1. 单例模式：确保只有一个实例 =====
 * 场景：数据库连接池、配置管理器
 */
class Singleton {
    // 1. 私有构造器，不让外部new
    private Singleton() {
        System.out.println("创建Singleton实例（只会有一次）");
    }
    
    // 2. 私有静态实例（类加载时就创建）
    private static Singleton instance = new Singleton();
    
    // 3. 公共静态方法获取实例
    public static Singleton getInstance() {
        return instance;
    }
    
    public void showMessage() {
        System.out.println("Singleton方法被调用");
    }
}

/**
 * 懒汉式单例（延迟加载）
 */
class LazySingleton {
    private static LazySingleton instance;
    
    private LazySingleton() {
        System.out.println("懒汉式实例被创建");
    }
    
    // 注意：多线程下需要加synchronized
    public static synchronized LazySingleton getInstance() {
        if (instance == null) {
            instance = new LazySingleton();
        }
        return instance;
    }
}

/**
 * ===== 2. 工厂模式：统一创建对象 =====
 * 场景：对象的创建过程复杂、需要统一管理
 */
interface Phone {
    void call();
}

class Xiaomi implements Phone {
    @Override
    public void call() {
        System.out.println("用小米手机打电话");
    }
}

class Huawei implements Phone {
    @Override
    public void call() {
        System.out.println("用华为手机打电话");
    }
}

class Apple implements Phone {
    @Override
    public void call() {
        System.out.println("用苹果手机打电话");
    }
}

/**
 * 简单工厂
 */
class SimplePhoneFactory {
    public static Phone createPhone(String brand) {
        switch (brand) {
            case "xiaomi":
                return new Xiaomi();
            case "huawei":
                return new Huawei();
            case "apple":
                return new Apple();
            default:
                throw new IllegalArgumentException("不支持的品牌：" + brand);
        }
    }
}

/**
 * ===== 3. 观察者模式：一对多依赖 =====
 * 场景：消息订阅、事件监听
 */
interface Observer {
    void update(String message);
}

class UserA implements Observer {
    @Override
    public void update(String message) {
        System.out.println("用户A收到消息：" + message);
    }
}

class UserB implements Observer {
    @Override
    public void update(String message) {
        System.out.println("用户B收到消息：" + message);
    }
}

class NewsOffice {
    private List<Observer> observers = new ArrayList<>();
    
    public void addObserver(Observer o) {
        observers.add(o);
    }
    
    public void removeObserver(Observer o) {
        observers.remove(o);
    }
    
    public void notifyAll(String message) {
        for (Observer o : observers) {
            o.update(message);
        }
    }
}

/**
 * ===== 4. 策略模式：可以互换的算法 =====
 * 场景：多种算法可以互换使用
 */
interface SortStrategy {
    int[] sort(int[] array);
}

class BubbleSort implements SortStrategy {
    @Override
    public int[] sort(int[] array) {
        System.out.println("使用冒泡排序");
        int[] arr = array.clone();
        for (int i = 0; i < arr.length - 1; i++) {
            for (int j = 0; j < arr.length - 1 - i; j++) {
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
        return arr;
    }
}

class QuickSort implements SortStrategy {
    @Override
    public int[] sort(int[] array) {
        System.out.println("使用快速排序");
        // 简化实现，实际用Arrays.sort
        int[] arr = array.clone();
        Arrays.sort(arr);
        return arr;
    }
}

class Sorter {
    private SortStrategy strategy;
    
    public void setStrategy(SortStrategy strategy) {
        this.strategy = strategy;
    }
    
    public int[] sort(int[] array) {
        return strategy.sort(array);
    }
}

/**
 * 测试设计模式
 */
public class DesignPatternDemo {
    public static void main(String[] args) {
        // ===== 1. 单例模式 =====
        System.out.println("=== 单例模式 ===");
        Singleton s1 = Singleton.getInstance();
        Singleton s2 = Singleton.getInstance();
        System.out.println("s1 == s2 ? " + (s1 == s2));  // true
        
        // ===== 2. 工厂模式 =====
        System.out.println("\n=== 工厂模式 ===");
        Phone phone1 = SimplePhoneFactory.createPhone("xiaomi");
        phone1.call();
        
        Phone phone2 = SimplePhoneFactory.createPhone("apple");
        phone2.call();
        
        // ===== 3. 观察者模式 =====
        System.out.println("\n=== 观察者模式 ===");
        NewsOffice office = new NewsOffice();
        office.addObserver(new UserA());
        office.addObserver(new UserB());
        office.notifyAll("有新消息：Java是世界上最好的语言！");
        
        // ===== 4. 策略模式 =====
        System.out.println("\n=== 策略模式 ===");
        int[] data = {5, 2, 8, 1, 9};
        
        Sorter sorter = new Sorter();
        sorter.setStrategy(new BubbleSort());
        System.out.println("冒泡排序结果：" + Arrays.toString(sorter.sort(data)));
        
        sorter.setStrategy(new QuickSort());
        System.out.println("快速排序结果：" + Arrays.toString(sorter.sort(data)));
    }
}
```

**⚠️ 小白易懵点：**

1. **单例模式有两种**：饿汉式（类加载时创建）和懒汉式（第一次使用时创建）。
2. **工厂模式的优点**：解耦，客户端不需要知道具体类名，只需要知道工厂。
3. **观察者模式的核心**：发布-订阅机制，发布者和订阅者解耦。
4. **策略模式的核心**：把算法封装成类，可以运行时切换。
5. **不要过度设计**！设计模式是好东西，但不需要处处都用。

**💡 一句话总结：** 类是图纸对象是车，封装是保险箱保护数据，继承是家族传承特性，多态是一面千人，抽象类和接口是契约规范，内部类是套娃，設計模式是编程套路。

---

## 第三篇：核心API与集合

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 3.1 String三兄弟：String/StringBuilder/StringBuffer

**一句话人话解释：** 
- String是不可变的，每次"修改"都创建新对象，适合不变的数据
- StringBuilder可变且高效，但线程不安全，适合单线程
- StringBuffer可变且线程安全，但稍慢，适合多线程

**生活比喻 🍱：**

想象你要写一本日记：
- **String**：每写一个字就印一本书，然后把书给你（太浪费！）
- **StringBuilder**：在草稿纸上写，随便改，最后定稿了再印书（高效）
- **StringBuffer**：多人同时在草稿纸上写，需要锁门保证安全（线程安全）

**技术核心 📖：**

| 类 | 线程安全 | 可变性 | 性能 | 使用场景 |
|----|----------|--------|------|----------|
| String | 安全 | 不可变 | 最慢（每次创建新对象） | 不需要改变的字符串 |
| StringBuilder | 不安全 | 可变 | 最快 | 单线程字符串拼接 |
| StringBuffer | 安全 | 可变 | 较快 | 多线程字符串拼接 |

**代码示例 💻：**

```java
public class StringBuilderBufferDemo {
    public static void main(String[] args) {
        
        // ===== String 的不可变性 =====
        System.out.println("=== String 不可变性 ===");
        String s = "Hello";
        String s2 = s.concat(" World");  // 创建了新对象
        System.out.println("s = " + s);        // Hello（不变）
        System.out.println("s2 = " + s2);      // Hello World
        
        // 看似修改，实际创建了新对象
        s += " World";  // 创建了新的String对象
        System.out.println("s += 后 = " + s);
        
        // ===== StringBuilder 的可变性 =====
        System.out.println("\n=== StringBuilder 可变性 ===");
        StringBuilder sb = new StringBuilder("Hello");
        sb.append(" World");      // 直接在原对象上追加
        sb.insert(5, ",");        // 在指定位置插入
        sb.replace(0, 5, "Hi");   // 替换指定范围的内容
        sb.delete(0, 2);          // 删除指定范围的内容
        System.out.println("StringBuilder结果：" + sb.toString());
        
        // ===== StringBuffer（线程安全） =====
        System.out.println("\n=== StringBuffer ===");
        StringBuffer sbf = new StringBuffer("Hello");
        sbf.append(" World");
        System.out.println("StringBuffer结果：" + sbf.toString());
        
        // ===== 性能对比 =====
        System.out.println("\n=== 性能对比 ===");
        
        // 用String拼接（不推荐）
        long start = System.currentTimeMillis();
        String str = "";
        for (int i = 0; i < 10000; i++) {
            str += "a";
        }
        long end = System.currentTimeMillis();
        System.out.println("String拼接10000次耗时：" + (end - start) + "ms");
        
        // 用StringBuilder（推荐）
        start = System.currentTimeMillis();
        StringBuilder sbFast = new StringBuilder();
        for (int i = 0; i < 100000; i++) {  // 10万次
            sbFast.append("a");
        }
        end = System.currentTimeMillis();
        System.out.println("StringBuilder拼接100000次耗时：" + (end - start) + "ms");
        
        // ===== 常用方法 =====
        System.out.println("\n=== StringBuilder常用方法 ===");
        StringBuilder sb2 = new StringBuilder("Hello");
        System.out.println("长度：" + sb2.length());
        System.out.println("容量：" + sb2.capacity());  // 初始16+5=21
        
        sb2.setCharAt(0, 'h');  // 设置指定位置字符
        System.out.println("setCharAt后：" + sb2);
        
        sb2.reverse();  // 反转
        System.out.println("反转后：" + sb2);
        
        sb2.reverse();  // 再反转回来
        
        // 链式调用（方法返回this）
        sb2.append(" World")
           .append("!")
           .insert(0, "Say: ");
        System.out.println("链式调用：" + sb2);
    }
}
```

**⚠️ 小白易懵点：**

1. **String不是基本类型**，是引用类型，但用起来像基本类型。
2. **String不可变不是缺点**，是优点！适合作为Map的key、并发环境下使用。
3. **频繁字符串拼接用StringBuilder**，单行简单拼接用+也无所谓（编译器会优化）。
4. **StringBuffer几乎不用了**，因为现在的Web开发大多是单线程。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 3.2 集合框架全景图

**一句话人话解释：** Java集合就是给你的数据找个"容器"，不同容器有不同的特点，选择对了事半功倍。

**生活比喻 🏪：**

想象你去超市买东西：
- **List（列表）** = 排队结账，按顺序排，有编号
- **Set（集合）** = 去超市前检查清单，只关心"有没有"，不关心顺序
- **Map（映射）** = 超市储物柜，每个柜子有编号（key），里面放东西（value）

**技术核心 📖：**

```
Collection (接口)
├── List (接口，有序、可重复)
│   ├── ArrayList（数组实现，随机访问快）
│   ├── LinkedList（链表实现，插入删除快）
│   └── Vector（线程安全，效率低）
│
├── Set (接口，无序、去重)
│   ├── HashSet（哈希表，最常用）
│   ├── LinkedHashSet（保持插入顺序）
│   └── TreeSet（自动排序）
│
└── Queue (接口，队列)
    ├── LinkedList（也实现了Queue）
    └── PriorityQueue（优先级队列）

Map (接口，键值对)
├── HashMap（哈希表，最常用）
├── LinkedHashMap（保持插入顺序）
├── TreeMap（按键自动排序）
└── Hashtable（线程安全，已过时）
```

**代码示例 💻：**

```java
import java.util.*;

public class CollectionFrameworkDemo {
    public static void main(String[] args) {
        
        // ===== List：有序、可重复 =====
        System.out.println("=== List ===");
        List<String> fruits = new ArrayList<>();
        fruits.add("苹果");
        fruits.add("香蕉");
        fruits.add("橙子");
        fruits.add("苹果");  // 可以重复
        
        System.out.println("水果列表：" + fruits);
        System.out.println("第2个水果：" + fruits.get(1));
        System.out.println("苹果在第几个：" + fruits.indexOf("苹果"));
        
        // 遍历List
        System.out.println("\n遍历方式1：普通for");
        for (int i = 0; i < fruits.size(); i++) {
            System.out.println(fruits.get(i));
        }
        
        System.out.println("遍历方式2：增强for");
        for (String fruit : fruits) {
            System.out.println(fruit);
        }
        
        System.out.println("遍历方式3：迭代器");
        Iterator<String> it = fruits.iterator();
        while (it.hasNext()) {
            String f = it.next();
            System.out.println(f);
        }
        
        // ===== Set：无序、去重 =====
        System.out.println("\n=== Set ===");
        Set<String> animalSet = new HashSet<>();
        animalSet.add("狗");
        animalSet.add("猫");
        animalSet.add("狗");  // 重复的不会被添加
        animalSet.add("鸟");
        
        System.out.println("动物集合：" + animalSet);  // 顺序可能和添加顺序不同
        System.out.println("集合大小：" + animalSet.size());  // 3，不是4
        
        // Set的用途：去重
        System.out.println("\n去重演示：");
        List<Integer> numbersWithDup = Arrays.asList(1, 2, 3, 2, 1, 4, 3);
        Set<Integer> numbersWithoutDup = new HashSet<>(numbersWithDup);
        System.out.println("有重复：" + numbersWithDup);
        System.out.println("去重后：" + numbersWithoutDup);
        
        // ===== Map：键值对 =====
        System.out.println("\n=== Map ===");
        Map<String, Integer> scoreMap = new HashMap<>();
        scoreMap.put("语文", 90);
        scoreMap.put("数学", 85);
        scoreMap.put("英语", 92);
        scoreMap.put("数学", 88);  // key相同，会覆盖
        
        System.out.println("成绩map：" + scoreMap);
        System.out.println("数学成绩：" + scoreMap.get("数学"));
        System.out.println("有体育吗：" + scoreMap.containsKey("体育"));
        System.out.println("所有成绩：" + scoreMap.values());
        System.out.println("所有科目：" + scoreMap.keySet());
        
        // 遍历Map
        System.out.println("\n遍历Map：");
        for (Map.Entry<String, Integer> entry : scoreMap.entrySet()) {
            System.out.println(entry.getKey() + " = " + entry.getValue());
        }
        
        // ===== 实际应用示例 =====
        System.out.println("\n=== 实际应用 ===");
        
        // 1. 统计单词出现次数
        String text = "apple banana apple orange apple banana apple";
        Map<String, Integer> wordCount = new HashMap<>();
        for (String word : text.split(" ")) {
            wordCount.put(word, wordCount.getOrDefault(word, 0) + 1);
        }
        System.out.println("单词统计：" + wordCount);
        
        // 2. List去重
        List<String> names = Arrays.asList("张三", "李四", "王五", "张三", "赵六");
        List<String> uniqueNames = new ArrayList<>(new HashSet<>(names));
        System.out.println("去重后姓名：" + uniqueNames);
    }
}
```

**⚠️ 小白易懵点：**

1. **List、Set、Map都是接口**，不能直接实例化，需要用实现类。
2. **HashSet保证不了顺序**，如果需要顺序用LinkedHashSet或TreeSet。
3. **Map不是Collection的子接口**，它是独立的。
4. **集合只能存对象**，基本类型会自动装箱（int → Integer）。
5. **ArrayList查询快但增删慢**，LinkedList增删快但查询慢。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 3.3 ArrayList vs LinkedList：数组和链表的对决

**一句话人话解释：** ArrayList像排排坐的格子，LinkedList像手拉手的小朋友。

**生活比喻 🏃：**

- **ArrayList**：教室里的固定座位。每个座位有编号（索引），找第10个同学很快，直接数格子。但要插队进第5和第6之间，需要让6-10号都往后挪一位。

- **LinkedList**：老师带着小朋友手拉手围成圈。要在5号和6号之间插入新人，只需要让5号松开6号的手，拉住新人，新人再拉住6号。但如果要找第10个人，必须从第1个开始数。

**技术核心 📖：**

| 操作 | ArrayList | LinkedList |
|------|-----------|------------|
| 按索引查询 | O(1) 极快 | O(n) 较慢 |
| 头部插入/删除 | O(n) 较慢 | O(1) 极快 |
| 尾部插入/删除 | O(1) 极快 | O(1) 极快 |
| 中间插入/删除 | O(n) 较慢 | O(n) 较慢（需先找到位置） |
| 内存占用 | 连续，节省 | 每个节点存指针，较费 |

**代码示例 💻：**

```java
import java.util.*;

public class ArrayListVsLinkedListDemo {
    public static void main(String[] args) {
        
        List<Integer> arrayList = new ArrayList<>();
        List<Integer> linkedList = new LinkedList<>();
        
        // ===== 1. 性能测试：尾部添加 =====
        System.out.println("=== 尾部添加100000个元素 ===");
        
        long start = System.currentTimeMillis();
        for (int i = 0; i < 100000; i++) {
            arrayList.add(i);
        }
        long end = System.currentTimeMillis();
        System.out.println("ArrayList尾部添加：" + (end - start) + "ms");
        
        start = System.currentTimeMillis();
        for (int i = 0; i < 100000; i++) {
            linkedList.add(i);
        }
        end = System.currentTimeMillis();
        System.out.println("LinkedList尾部添加：" + (end - start) + "ms");
        
        // ===== 2. 性能测试：按索引查询 =====
        System.out.println("\n=== 按索引查询10000次 ===");
        
        start = System.currentTimeMillis();
        for (int i = 0; i < 10000; i++) {
            arrayList.get(i % arrayList.size());
        }
        end = System.currentTimeMillis();
        System.out.println("ArrayList查询：" + (end - start) + "ms");
        
        start = System.currentTimeMillis();
        for (int i = 0; i < 10000; i++) {
            linkedList.get(i % linkedList.size());
        }
        end = System.currentTimeMillis();
        System.out.println("LinkedList查询：" + (end - start) + "ms");
        
        // ===== 3. 性能测试：按索引插入 =====
        System.out.println("\n=== 按索引插入1000次（在中间位置）===");
        int mid = 50000;
        
        List<Integer> al = new ArrayList<>();
        for (int i = 0; i < 100000; i++) al.add(i);
        
        List<Integer> ll = new LinkedList<>();
        for (int i = 0; i < 100000; i++) ll.add(i);
        
        start = System.currentTimeMillis();
        for (int i = 0; i < 1000; i++) {
            al.add(mid, -1);
        }
        end = System.currentTimeMillis();
        System.out.println("ArrayList中间插入：" + (end - start) + "ms");
        
        start = System.currentTimeMillis();
        for (int i = 0; i < 1000; i++) {
            ll.add(mid, -1);
        }
        end = System.currentTimeMillis();
        System.out.println("LinkedList中间插入：" + (end - start) + "ms");
        
        // ===== 4. LinkedList特有功能 =====
        System.out.println("\n=== LinkedList特有功能 ===");
        LinkedList<String> queue = new LinkedList<>();
        
        // 当队列使用
        queue.offer("第一");    // 入队
        queue.offer("第二");
        queue.offer("第三");
        
        System.out.println("出队：" + queue.poll());  // 第一
        System.out.println("查看队首：" + queue.peek());
        
        // 当栈使用
        LinkedList<Integer> stack = new LinkedList<>();
        stack.push(1);  // 入栈
        stack.push(2);
        stack.push(3);
        System.out.println("\n栈演示：");
        System.out.println("弹栈：" + stack.pop());  // 3
        System.out.println("弹栈：" + stack.pop());  // 2
        
        // ===== 结论 =====
        System.out.println("\n=== 选择建议 ===");
        System.out.println("查询多、增删少 → ArrayList");
        System.out.println("增删多、查询少 → LinkedList");
        System.out.println("需要队列/栈功能 → LinkedList");
    }
}
```

**⚠️ 小白易懵点：**

1. **ArrayList不是数组**，但底层是用数组实现的，所以有数组的优点。
2. **大多数情况下用ArrayList就够了**，除非你有性能问题或明确需要LinkedList的特性。
3. **LinkedList.get(n)很慢**，因为每次都要从头遍历。
4. **扩容机制**：ArrayList满了会扩容1.5倍，LinkedList不需要扩容。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 3.4 HashMap原理：数组+链表+红黑树

**一句话人话解释：** HashMap像一个超大型图书馆的图书管理系统，通过"编号"快速找到"书"。

**生活比喻 📚：**

想象一个图书馆：
- **哈希函数** = 图书编号规则（比如：作者姓氏首字母+年份）
- **数组** = 图书馆的书架，每个书架有固定位置
- **链表/红黑树** = 同一个位置书太多时的排列方式

当你知道书名时，通过哈希函数算出编号（hash），直接去对应书架找。如果书架上书太多（哈希冲突），就用链表或树来管理。

**技术核心 📖：**

1. **哈希计算**：key的hashCode() → 数组下标
2. **哈希冲突**：不同key算出相同下标，用链表（或JDK8+红黑树）解决
3. **扩容**：当元素超过负载因子（默认0.75）× 容量时，扩容2倍并重新哈希
4. **树化**：当单个桶链表长度超过8且数组长度≥64时，转为红黑树

**代码示例 💻：**

```java
import java.util.*;

public class HashMapPrincipleDemo {
    public static void main(String[] args) {
        
        // ===== 基本使用 =====
        System.out.println("=== HashMap基本使用 ===");
        Map<String, Integer> map = new HashMap<>();
        
        // 添加元素
        map.put("苹果", 3);
        map.put("香蕉", 5);
        map.put("橙子", 2);
        
        // 获取元素
        System.out.println("苹果有" + map.get("苹果") + "个");
        System.out.println("葡萄有" + map.get("葡萄"));  // null
        
        // 使用getOrDefault
        System.out.println("葡萄（默认0）：" + map.getOrDefault("葡萄", 0));
        
        // ===== 遍历方式 =====
        System.out.println("\n=== 遍历HashMap ===");
        
        // 方式1：遍历key
        for (String key : map.keySet()) {
            System.out.println("水果：" + key + "，数量：" + map.get(key));
        }
        
        // 方式2：遍历entry（推荐，性能更好）
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            System.out.println(entry.getKey() + " = " + entry.getValue());
        }
        
        // 方式3：遍历values（只关心值）
        System.out.println("所有数量：");
        for (Integer value : map.values()) {
            System.out.println(value);
        }
        
        // ===== 常用方法 =====
        System.out.println("\n=== 常用方法 ===");
        System.out.println("是否包含key：" + map.containsKey("苹果"));
        System.out.println("是否包含value：" + map.containsValue(3));
        System.out.println("元素个数：" + map.size());
        
        map.remove("香蕉");
        System.out.println("删除香蕉后：" + map);
        
        // ===== 底层原理演示 =====
        System.out.println("\n=== HashMap原理演示 ===");
        
        // 演示hash碰撞
        String key1 = "Aa";
        String key2 = "BB";
        System.out.println("key1 hash: " + key1.hashCode());
        System.out.println("key2 hash: " + key2.hashCode());
        System.out.println("两个key的hash相等吗：" + (key1.hashCode() == key2.hashCode()));
        
        // 演示put过程
        Map<Integer, String> intMap = new HashMap<>();
        intMap.put(1, "一");
        intMap.put(2, "二");
        intMap.put(3, "三");
        
        System.out.println("\nput过程：");
        System.out.println("初始map：" + intMap);
        
        // 覆盖已有key
        intMap.put(2, "两");
        System.out.println("覆盖key=2后：" + intMap);
        
        // ===== HashMap的线程安全问题 =====
        System.out.println("\n=== HashMap线程不安全 ===");
        System.out.println("多线程环境下使用 ConcurrentHashMap");
        
        // ===== 负载因子演示 =====
        System.out.println("\n=== HashMap参数 ===");
        HashMap<String, Integer> customMap = new HashMap<>(16, 0.75f);
        System.out.println("初始容量：16");
        System.out.println("负载因子：0.75");
        System.out.println("扩容阈值：16 * 0.75 = 12");
        System.out.println("当元素达到12个时会扩容");
        
        // ===== 实际应用 =====
        System.out.println("\n=== 实际应用：统计字符出现次数 ===");
        String str = "abracadabra";
        Map<Character, Integer> charCount = new HashMap<>();
        
        for (char c : str.toCharArray()) {
            // 方式1：getOrDefault
            charCount.put(c, charCount.getOrDefault(c, 0) + 1);
        }
        
        System.out.println("字符统计：" + charCount);
    }
}
```

**⚠️ 小白易懵点：**

1. **HashMap允许key为null**，但只能有一个null key。
2. **HashMap不是线程安全的**，多线程下用ConcurrentHashMap。
3. **重写hashCode和equals**：自定义类作为key时，必须同时重写这两个方法。
4. **HashMap遍历的顺序不确定**，如果需要顺序用LinkedHashMap。
5. **HashMap的扩容代价很高**，如果能预估容量，创建时指定初始容量可以提升性能。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 3.5 泛型：Java的安全带

**一句话人话解释：** 泛型就是给集合装的"安全带"，让你在编译时就发现类型错误，而不是运行时崩溃。

**生活比喻 🎽：**

想象你去超市买水果：
- **没用泛型**：买回来一箱东西，打开才发现有水果、蔬菜、零食混在一起，还要一个个检查类型
- **用了泛型**：标签写着"水果箱"，那里面只能装水果，装错了超市不让你放进去

**技术核心 📖：**

```java
// 泛型类
class Box<T> {  // T是类型参数
    private T item;
    public void set(T item) { this.item = item; }
    public T get() { return item; }
}

// 泛型方法
public <T> void print(T item) { }

// 泛型接口
interface Container<T> {
    void add(T item);
    T get(int index);
}

// 限定类型
class NumberBox<T extends Number> {  // T必须是Number的子类
    private T value;
}

// 通配符
void printList(List<?> list);           // 任意类型
void printNumbers(List<? extends Number> list);  // Number及其子类
void addNumbers(List<? super Integer> list);      // Integer及其父类
```

**代码示例 💻：**

```java
import java.util.*;

/**
 * 泛型类
 */
class Box<T> {
    private T content;
    
    public void put(T content) {
        this.content = content;
    }
    
    public T get() {
        return content;
    }
}

/**
 * 限定类型的泛型类
 */
class NumberBox<T extends Number> {
    private T value;
    
    public void set(T value) {
        this.value = value;
    }
    
    public T get() {
        return value;
    }
    
    public int intValue() {
        return value.intValue();  // Number类的方法
    }
}

/**
 * 泛型方法
 */
class GenericMethods {
    public static <T> void printArray(T[] array) {
        for (T item : array) {
            System.out.print(item + " ");
        }
        System.out.println();
    }
    
    public static <T> T getFirst(List<T> list) {
        if (list == null || list.isEmpty()) {
            return null;
        }
        return list.get(0);
    }
    
    // 可变参数泛型方法
    @SafeVarargs
    public static <T> List<T> asList(T... elements) {
        return Arrays.asList(elements);
    }
}

/**
 * 泛型接口
 */
interface Generator<T> {
    T generate();
}

class StringGenerator implements Generator<String> {
    @Override
    public String generate() {
        return "Generated String";
    }
}

class IntegerGenerator implements Generator<Integer> {
    @Override
    public Integer generate() {
        return 42;
    }
}

/**
 * 通配符演示
 */
class WildcardDemo {
    // ? extends Number：可以读取（上限）
    public static void printNumbers(List<? extends Number> list) {
        for (Number n : list) {
            System.out.println(n.doubleValue());
        }
        // list.add(1);  // 编译错误！不能添加
    }
    
    // ? super Integer：可以写入（下限）
    public static void addNumbers(List<? super Integer> list) {
        list.add(1);
        list.add(2);
        // Number n = list.get(0);  // 编译错误！只能当Object读取
    }
}

/**
 * 泛型测试
 */
public class GenericDemo {
    public static void main(String[] args) {
        
        // ===== 泛型类 =====
        System.out.println("=== 泛型类 ===");
        Box<String> stringBox = new Box<>();
        stringBox.put("Hello");
        String s = stringBox.get();
        System.out.println("String Box: " + s);
        
        Box<Integer> intBox = new Box<>();
        intBox.put(100);
        Integer i = intBox.get();
        System.out.println("Integer Box: " + i);
        
        // ===== 泛型方法 =====
        System.out.println("\n=== 泛型方法 ===");
        String[] names = {"Alice", "Bob", "Charlie"};
        GenericMethods.printArray(names);
        
        Integer[] nums = {1, 2, 3, 4, 5};
        GenericMethods.printArray(nums);
        
        // ===== 泛型接口 =====
        System.out.println("\n=== 泛型接口 ===");
        Generator<String> strGen = new StringGenerator();
        Generator<Integer> intGen = new IntegerGenerator();
        System.out.println(strGen.generate());
        System.out.println(intGen.generate());
        
        // ===== 通配符 =====
        System.out.println("\n=== 通配符 ===");
        List<Double> doubles = Arrays.asList(1.1, 2.2, 3.3);
        List<Integer> integers = Arrays.asList(1, 2, 3);
        
        WildcardDemo.printNumbers(doubles);  // OK
        WildcardDemo.printNumbers(integers);  // OK
        
        List<Number> numbers = new ArrayList<>();
        WildcardDemo.addNumbers(numbers);  // OK
        System.out.println("numbers: " + numbers);
        
        // ===== 限定类型 =====
        System.out.println("\n=== 限定类型 ===");
        NumberBox<Integer> nb1 = new NumberBox<>();
        nb1.set(123);
        System.out.println("intValue: " + nb1.intValue());
        
        NumberBox<Double> nb2 = new NumberBox<>();
        nb2.set(3.14);
        System.out.println("double转int: " + nb2.intValue());
        
        // NumberBox<String> nb3;  // 编译错误！String不是Number的子类
        
        // ===== 类型擦除 =====
        System.out.println("\n=== 类型擦除 ===");
        List<String> list1 = new ArrayList<>();
        List<Integer> list2 = new ArrayList<>();
        System.out.println("list1 == list2: " + (list1.getClass() == list2.getClass()));
        System.out.println("泛型在运行时会被擦除！");
    }
}
```

**⚠️ 小白易懵点：**

1. **泛型是编译时检查**，运行时会被擦除（类型擦除）。
2. **泛型不能用于基本类型**，只能用包装类（`ArrayList<int>`是错的，要用`ArrayList<Integer>`）。
3. **`T[]`创建数组需要特殊处理**，因为运行时类型擦除后不知道T是什么。
4. **`<?>`和`<T>`的区别**：`<?>`是通配符，用于接收；`<T>`是类型参数，用于定义。
5. **`extends`和`super`的使用场景**：读取用extends，写入用super（PECS原则）。

**💡 一句话总结：** String/StringBuilder/StringBuffer选Builder，集合List/Set/Map按需选，ArrayList查快LinkedList删快，HashMap用key算哈希存值，泛型让代码更安全。

![顿悟](https://www.coze.cn/s/PtHn-lhw7Dg/)


![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 3.6 Stream API：Java的流水线

**一句话人话解释：** Stream API就是Java给你的数据开的"流水线"，让数据加工变得更简洁、更函数式。

**生活比喻 🏭：**

想象你要做一杯果汁：
1. **原料（源头）**：一筐水果
2. **第一步（过滤）**：挑出烂的
3. **第二步（转换）**：切成块
4. **第三步（收集）**：榨成汁装杯

Stream API就是这样的流水线：`原料.stream().过滤().转换().收集()`

**技术核心 📖：**

Stream操作分三类：
- **中间操作**：返回Stream，可以链式调用（filter、map、distinct、sorted...）
- **终端操作**：返回结果或副作用（collect、forEach、count、reduce...）
- **短路操作**：减少计算量（findFirst、anyMatch...）

**代码示例 💻：**

```java
import java.util.*;
import java.util.stream.*;

public class StreamAPIDemo {
    public static void main(String[] args) {
        
        // ===== 数据准备 =====
        List<Dish> menu = Arrays.asList(
            new Dish("宫保鸡丁", 500, Type.MEAT),
            new Dish("番茄炒蛋", 300, Type.VEGETABLE),
            new Dish("红烧肉", 800, Type.MEAT),
            new Dish("清炒时蔬", 150, Type.VEGETABLE),
            new Dish("清蒸鱼", 400, Type.MEAT),
            new Dish("水果沙拉", 200, Type.OTHER),
            new Dish("可乐", 150, Type.OTHER),
            new Dish("米饭", 200, Type.OTHER)
        );
        
        // ===== 1. filter：过滤 =====
        System.out.println("=== filter：过滤 ===");
        
        // 找出热量大于400的菜
        List<Dish> highCalorie = menu.stream()
            .filter(d -> d.getCalories() > 400)
            .collect(Collectors.toList());
        highCalorie.forEach(d -> System.out.println(d.getName()));
        
        // ===== 2. map：转换 =====
        System.out.println("\n=== map：转换 ===");
        
        // 提取所有菜名
        List<String> dishNames = menu.stream()
            .map(Dish::getName)
            .collect(Collectors.toList());
        System.out.println("所有菜名：" + dishNames);
        
        // 提取所有单词长度
        List<String> words = Arrays.asList("Hello", "World", "Java");
        List<Integer> lengths = words.stream()
            .map(String::length)
            .collect(Collectors.toList());
        System.out.println("单词长度：" + lengths);
        
        // ===== 3. flatMap：扁平化 =====
        System.out.println("\n=== flatMap：扁平化 ===");
        
        String[] poems = {"床前明月光", "疑是地上霜"};
        List<String[]> chars = Arrays.stream(poems)
            .map(p -> p.split(""))
            .collect(Collectors.toList());
        System.out.println("普通map（嵌套）：" + chars);
        
        List<String> flatChars = Arrays.stream(poems)
            .flatMap(p -> Arrays.stream(p.split("")))
            .distinct()
            .collect(Collectors.toList());
        System.out.println("flatMap后去重：" + flatChars);
        
        // ===== 4. limit和skip：截取 =====
        System.out.println("\n=== limit和skip ===");
        
        // 取前3个
        List<Dish> first3 = menu.stream()
            .limit(3)
            .collect(Collectors.toList());
        System.out.println("前3道菜：" + first3.stream().map(Dish::getName).collect(Collectors.toList()));
        
        // 跳过前2个，取后面的
        List<Dish> skip2 = menu.stream()
            .skip(2)
            .collect(Collectors.toList());
        System.out.println("跳过前2：" + skip2.stream().map(Dish::getName).collect(Collectors.toList()));
        
        // ===== 5. sorted：排序 =====
        System.out.println("\n=== sorted ===");
        
        // 按热量排序
        List<Dish> byCalories = menu.stream()
            .sorted(Comparator.comparing(Dish::getCalories))
            .collect(Collectors.toList());
        byCalories.forEach(d -> System.out.println(d.getName() + "：" + d.getCalories() + "卡"));
        
        // ===== 6. distinct：去重 =====
        System.out.println("\n=== distinct ===");
        List<Integer> nums = Arrays.asList(1, 2, 3, 2, 1, 4, 3, 5);
        List<Integer> distinctNums = nums.stream()
            .distinct()
            .collect(Collectors.toList());
        System.out.println("去重前：" + nums);
        System.out.println("去重后：" + distinctNums);
        
        // ===== 7. 终端操作 =====
        System.out.println("\n=== 终端操作 ===");
        
        // count
        long meatCount = menu.stream()
            .filter(d -> d.getType() == Type.MEAT)
            .count();
        System.out.println("荤菜数量：" + meatCount);
        
        // anyMatch / allMatch / noneMatch
        boolean hasVegetarian = menu.stream()
            .anyMatch(d -> d.getType() == Type.VEGETABLE);
        System.out.println("有素菜吗：" + hasVegetarian);
        
        boolean allHealthy = menu.stream()
            .allMatch(d -> d.getCalories() < 1000);
        System.out.println("所有菜都低于1000卡吗：" + allHealthy);
        
        // findFirst / findAny
        Optional<Dish> firstMeat = menu.stream()
            .filter(d -> d.getType() == Type.MEAT)
            .findFirst();
        System.out.println("第一道荤菜：" + firstMeat.map(Dish::getName).orElse("没有"));
        
        // ===== 8. reduce：聚合 =====
        System.out.println("\n=== reduce ===");
        
        // 求和
        int totalCalories = menu.stream()
            .map(Dish::getCalories)
            .reduce(0, Integer::sum);
        System.out.println("总热量：" + totalCalories);
        
        // 找出最高热量的菜
        Optional<Dish> mostCaloric = menu.stream()
            .reduce((d1, d2) -> d1.getCalories() > d2.getCalories() ? d1 : d2);
        System.out.println("最高热量：" + mostCaloric.map(Dish::getName).orElse("没有"));
        
        // ===== 9. collect：收集 =====
        System.out.println("\n=== collect ===");
        
        // 收集成List
        List<String> meatDishes = menu.stream()
            .filter(d -> d.getType() == Type.MEAT)
            .map(Dish::getName)
            .collect(Collectors.toList());
        
        // 收集成Set
        Set<Type> types = menu.stream()
            .map(Dish::getType)
            .collect(Collectors.toSet());
        
        // 收集成Map
        Map<String, Integer> dishMap = menu.stream()
            .collect(Collectors.toMap(Dish::getName, Dish::getCalories));
        System.out.println("菜名-热量Map：" + dishMap);
        
        // 分组
        Map<Type, List<Dish>> byType = menu.stream()
            .collect(Collectors.groupingBy(Dish::getType));
        System.out.println("按类型分组：" + byType.keySet());
        
        // ===== 10. 并行流 =====
        System.out.println("\n=== 并行流 ===");
        
        // 普通流
        long start = System.currentTimeMillis();
        long sum1 = LongStream.rangeClosed(1, 100000000)
            .sum();
        System.out.println("普通流求和：" + sum1 + "，耗时：" + (System.currentTimeMillis() - start) + "ms");
        
        // 并行流（多核CPU并行计算）
        start = System.currentTimeMillis();
        long sum2 = LongStream.rangeClosed(1, 100000000)
            .parallel()
            .sum();
        System.out.println("并行流求和：" + sum2 + "，耗时：" + (System.currentTimeMillis() - start) + "ms");
    }
}

// ===== 辅助类 =====
enum Type { MEAT, VEGETABLE, OTHER }

class Dish {
    private String name;
    private int calories;
    private Type type;
    
    public Dish(String name, int calories, Type type) {
        this.name = name;
        this.calories = calories;
        this.type = type;
    }
    
    public String getName() { return name; }
    public int getCalories() { return calories; }
    public Type getType() { return type; }
}
```

**⚠️ 小白易懵点：**

1. **Stream不是数据结构**，是数据加工的视图，不会改变原数据。
2. **Stream只能用一次**，用完就"消费"了，不能重复使用。
3. **中间操作是惰性的**，不调用终端操作，中间操作不会执行。
4. **并行流不保证顺序**，如果需要顺序用`forEachOrdered()`。
5. **不要滥用Stream**，简单循环能解决的问题不要硬用Stream。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 3.7 异常处理：Java的错误处理中心

**一句话人话解释：** 异常就是程序运行时的"意外状况"，Java让你用try-catch-finally优雅地处理这些意外。

**生活比喻 🏥：**

想象你点外卖：
- **正常流程**：下单→商家接单→制作→配送→收货
- **异常情况**：商家接不了单（缺货）、配送失败（下雨）、收货人不在家
- **处理方式**：商家会告诉你"接不了单"，配送员会"改天再送"

异常处理就是让你的程序在出问题时优雅地"告诉用户"或"尝试恢复"，而不是直接崩溃。

**技术核心 📖：**

```
异常继承树：
Throwable
├── Error（错误，程序无法处理）
│   ├── OutOfMemoryError
│   └── StackOverflowError
│
└── Exception（异常）
    ├── RuntimeException（运行时异常，编译器不强制处理）
    │   ├── NullPointerException
    │   ├── ArrayIndexOutOfBoundsException
    │   └── ClassCastException
    │
    └── 其他异常（受检异常，编译器强制处理）
        ├── IOException
        ├── SQLException
        └── FileNotFoundException
```

**代码示例 💻：**

```java
import java.io.*;
import java.util.*;

public class ExceptionHandlingDemo {
    
    // ===== 1. 基本try-catch =====
    public static void basicTryCatch() {
        try {
            int[] arr = {1, 2, 3};
            System.out.println("访问arr[5]：" + arr[5]);  // 会抛出ArrayIndexOutOfBoundsException
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("捕获到数组越界异常！");
            System.out.println("异常信息：" + e.getMessage());
            e.printStackTrace();  // 打印堆栈信息
        }
        System.out.println("程序继续执行...");
    }
    
    // ===== 2. 多重catch =====
    public static void multiCatch() {
        try {
            Scanner sc = new Scanner(System.in);
            System.out.print("请输入数字：");
            int num = sc.nextInt();
            
            int result = 100 / num;  // 可能除以0
            System.out.println("100 / " + num + " = " + result);
            
            String s = null;
            s.length();  // NullPointerException
        } catch (InputMismatchException e) {
            System.out.println("输入类型错误！请输入数字！");
        } catch (ArithmeticException e) {
            System.out.println("除数不能为0！");
        } catch (NullPointerException e) {
            System.out.println("空指针异常！");
        } catch (Exception e) {
            System.out.println("其他异常：" + e.getMessage());
        }
    }
    
    // ===== 3. try-catch-finally =====
    public static void tryCatchFinally() {
        FileInputStream fis = null;
        try {
            fis = new FileInputStream("test.txt");  // 可能FileNotFoundException
            int data;
            while ((data = fis.read()) != -1) {
                System.out.print((char) data);
            }
        } catch (FileNotFoundException e) {
            System.out.println("文件不存在！");
        } catch (IOException e) {
            System.out.println("读取文件失败！");
        } finally {
            // finally块无论是否异常都会执行
            System.out.println("\nfinally块执行：释放资源");
            try {
                if (fis != null) {
                    fis.close();  // 关闭文件流
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
    
    // ===== 4. try-with-resources（自动关闭资源） =====
    public static void tryWithResources() {
        // Java7+支持，资源会自动关闭
        try (FileReader reader = new FileReader("test.txt")) {
            int data;
            while ((data = reader.read()) != -1) {
                System.out.print((char) data);
            }
        } catch (IOException e) {
            System.out.println("文件操作失败：" + e.getMessage());
        }  // 这里会自动调用close()
    }
    
    // ===== 5. throws和throw =====
    public static void divide(int a, int b) throws ArithmeticException {
        if (b == 0) {
            throw new ArithmeticException("除数不能为0！");  // 手动抛出异常
        }
        System.out.println(a + " / " + b + " = " + (a / b));
    }
    
    // ===== 6. 自定义异常 =====
    public static void validateAge(int age) throws InvalidAgeException {
        if (age < 0 || age > 150) {
            throw new InvalidAgeException("年龄必须在0-150之间！");
        }
        System.out.println("年龄有效：" + age);
    }
    
    // ===== main方法 =====
    public static void main(String[] args) {
        
        // 测试基本try-catch
        System.out.println("=== 基本try-catch ===");
        basicTryCatch();
        
        // 测试throws
        System.out.println("\n=== throws演示 ===");
        try {
            divide(10, 0);
        } catch (ArithmeticException e) {
            System.out.println("捕获除零异常：" + e.getMessage());
        }
        
        // 测试自定义异常
        System.out.println("\n=== 自定义异常 ===");
        try {
            validateAge(25);
            validateAge(-5);
        } catch (InvalidAgeException e) {
            System.out.println("年龄验证失败：" + e.getMessage());
        }
        
        // ===== 常见异常处理场景 =====
        System.out.println("\n=== 常见场景 ===");
        
        // 场景1：处理可能的null
        String str = null;
        Optional<String> opt = Optional.ofNullable(str);
        String result = opt.orElse("默认值");
        System.out.println("处理null：" + result);
        
        // 场景2：异常链
        try {
            try {
                throw new RuntimeException("原始异常");
            } catch (RuntimeException e) {
                throw new RuntimeException("包装后的异常", e);  // 保留原始异常
            }
        } catch (RuntimeException e) {
            System.out.println("异常：" + e.getMessage());
            System.out.println("原始异常：" + e.getCause());
        }
    }
}

/**
 * 自定义异常
 */
class InvalidAgeException extends Exception {
    public InvalidAgeException(String message) {
        super(message);
    }
}
```

**⚠️ 小白易懵点：**

1. **Error和Exception的区别**：Error是JVM错误，无法处理；Exception是可以处理的异常。
2. **RuntimeException不需要throws声明**，也不需要try-catch，但其他Exception需要。
3. **finally块一定会执行**，即使try或catch里有return，finally仍会在return之前执行。
4. **throw和throws的区别**：throw是抛出异常对象，throws是声明方法可能抛出的异常。
5. **捕获异常要具体**，不要用`catch(Exception e)`捕获所有异常然后什么都不做。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 3.8 常用工具类：Java的好帮手

**一句话人话解释：** Java提供了一系列工具类，让常见操作变得简单。

**生活比喻 🧰：**

想象你家的工具箱：
- 螺丝刀用来拧螺丝
- 锤子用来敲钉子
- 万能钥匙能开很多锁

Java的工具类就是编程世界的"工具箱"，Arrays、Collections、Objects、Math等都是常用工具。

**代码示例 💻：**

```java
import java.util.*;
import java.time.*;

public class UtilityClassDemo {
    public static void main(String[] args) {
        
        // ===== Arrays：数组工具 =====
        System.out.println("=== Arrays工具 ===");
        
        int[] nums = {5, 2, 8, 1, 9, 3};
        System.out.println("原数组：" + Arrays.toString(nums));
        
        // 排序
        Arrays.sort(nums);
        System.out.println("排序后：" + Arrays.toString(nums));
        
        // 二分查找（必须先排序）
        int index = Arrays.binarySearch(nums, 5);
        System.out.println("5在第" + index + "个位置");
        
        // 填充
        int[] filled = new int[5];
        Arrays.fill(filled, 100);
        System.out.println("填充后：" + Arrays.toString(filled));
        
        // 比较
        int[] a1 = {1, 2, 3};
        int[] a2 = {1, 2, 3};
        System.out.println("数组相等：" + Arrays.equals(a1, a2));
        
        // 转List
        List<Integer> list = Arrays.asList(1, 2, 3);
        System.out.println("Arrays.asList：" + list);
        
        // ===== Collections：集合工具 =====
        System.out.println("\n=== Collections工具 ===");
        
        List<String> names = new ArrayList<>(Arrays.asList("Charlie", "Alice", "Bob"));
        System.out.println("原集合：" + names);
        
        // 排序
        Collections.sort(names);
        System.out.println("排序后：" + names);
        
        // 反转
        Collections.reverse(names);
        System.out.println("反转后：" + names);
        
        // 洗牌
        Collections.shuffle(names);
        System.out.println("洗牌后：" + names);
        
        // 最大最小
        System.out.println("最大：" + Collections.max(names));
        System.out.println("最小：" + Collections.min(names));
        
        // 不可变集合
        List<String> immutable = Collections.unmodifiableList(names);
        // immutable.add("Test");  // 会抛出UnsupportedOperationException
        
        // ===== Objects：对象工具 =====
        System.out.println("\n=== Objects工具 ===");
        
        String s1 = null;
        String s2 = "Hello";
        
        // 安全比较
        System.out.println("s1 == null：" + Objects.isNull(s1));
        System.out.println("s2 != null：" + Objects.nonNull(s2));
        
        // requireNonNull：参数校验
        try {
            printName(null);
        } catch (NullPointerException e) {
            System.out.println("捕获异常：" + e.getMessage());
        }
        
        // equals深度比较
        int[] arr1 = {1, 2, 3};
        int[] arr2 = {1, 2, 3};
        System.out.println("Objects.equals(arr1, arr2)：" + Objects.equals(arr1, arr2));
        
        // ===== Math：数学工具 =====
        System.out.println("\n=== Math工具 ===");
        
        System.out.println("绝对值：Math.abs(-10) = " + Math.abs(-10));
        System.out.println("最大值：Math.max(3, 7) = " + Math.max(3, 7));
        System.out.println("最小值：Math.min(3, 7) = " + Math.min(3, 7));
        System.out.println("向上取整：Math.ceil(3.2) = " + Math.ceil(3.2));
        System.out.println("向下取整：Math.floor(3.8) = " + Math.floor(3.8));
        System.out.println("四舍五入：Math.round(3.5) = " + Math.round(3.5));
        System.out.println("开方：Math.sqrt(16) = " + Math.sqrt(16));
        System.out.println("幂：Math.pow(2, 3) = " + Math.pow(2, 3));
        System.out.println("随机数：Math.random() = " + Math.random());
        System.out.println("0-100随机整数：" + (int)(Math.random() * 101));
        
        // ===== LocalDateTime：日期时间（Java8+） =====
        System.out.println("\n=== LocalDateTime ===");
        
        // 当前时间
        LocalDateTime now = LocalDateTime.now();
        System.out.println("当前时间：" + now);
        
        // 创建指定时间
        LocalDateTime birthday = LocalDateTime.of(2024, 1, 1, 0, 0);
        System.out.println("指定时间：" + birthday);
        
        // 格式化
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy年MM月dd日 HH:mm:ss");
        System.out.println("格式化后：" + now.format(formatter));
        
        // 时间计算
        LocalDateTime nextWeek = now.plusWeeks(1);
        LocalDateTime yesterday = now.minusDays(1);
        System.out.println("一周后：" + nextWeek);
        System.out.println("昨天：" + yesterday);
        
        // ===== StringJoiner：字符串拼接 =====
        System.out.println("\n=== StringJoiner ===");
        
        StringJoiner sj = new StringJoiner(", ", "[", "]");
        sj.add("Apple");
        sj.add("Banana");
        sj.add("Orange");
        System.out.println("StringJoiner拼接：" + sj);
        
        // String.join
        String joined = String.join("-", "A", "B", "C");
        System.out.println("String.join：" + joined);
    }
    
    public static void printName(String name) {
        Objects.requireNonNull(name, "名字不能为空");
        System.out.println("名字是：" + name);
    }
}
```

**💡 一句话总结：** Stream是流水线处理数据，异常处理让你的程序优雅应对错误，工具类Arrays/Collections/Objects/Math是编程好帮手。

---

## 第四篇：进阶核心

![学习](https://www.coze.cn/s/Mbcs8udf-Ho/)

### 4.1 IO流：Java的文件读写

**一句话人话解释：** IO流就是Java程序和外接设备（文件、网络等）交换数据的"管道"。

**生活比喻 🚰：**

想象自来水公司供水：
- **输入流（InputStream）**：从水源到你家的水管，把数据"读进来"
- **输出流（OutputStream）**：从你家到下水道的管，把数据"写出去"
- **字节流**：水流原装（未经处理）
- **字符流**：水流经过滤网（处理成字符）

**技术核心 📖：**

```
IO流分类：
├── 字节流（处理二进制数据）
│   ├── InputStream（输入）
│   └── OutputStream（输出）
│
├── 字符流（处理文本数据）
│   ├── Reader（输入）
│   └── Writer（输出）
│
└── 缓冲流（加速读写）
    ├── BufferedInputStream/BufferedOutputStream
    └── BufferedReader/BufferedWriter
```

**代码示例 💻：**

```java
import java.io.*;
import java.nio.charset.StandardCharsets;

public class IODemo {
    
    // ===== 1. 字节流：FileInputStream/FileOutputStream =====
    public static void byteStreamDemo() throws IOException {
        String filePath = "test_byte.txt";
        
        // 写入字节
        System.out.println("=== 字节流写入 ===");
        FileOutputStream fos = new FileOutputStream(filePath);
        String content = "Hello, Java IO! 你好，Java IO！";
        fos.write(content.getBytes(StandardCharsets.UTF_8));  // 字符串转字节数组
        fos.close();
        System.out.println("写入完成");
        
        // 读取字节
        System.out.println("\n=== 字节流读取 ===");
        FileInputStream fis = new FileInputStream(filePath);
        byte[] buffer = new byte[1024];
        int length;
        StringBuilder sb = new StringBuilder();
        while ((length = fis.read(buffer)) != -1) {
            sb.append(new String(buffer, 0, length, StandardCharsets.UTF_8));
        }
        fis.close();
        System.out.println("读取内容：" + sb);
        
        // ===== 2. 字符流：FileReader/FileWriter =====
        System.out.println("\n=== 字符流 ===");
        String textFile = "test_char.txt";
        
        // 写入字符
        FileWriter fw = new FileWriter(textFile);
        fw.write("这是用字符流写入的内容\n");
        fw.write("第二行内容");
        fw.close();
        System.out.println("字符流写入完成");
        
        // 读取字符
        FileReader fr = new FileReader(textFile);
        char[] charBuffer = new char[1024];
        int charLength;
        while ((charLength = fr.read(charBuffer)) != -1) {
            System.out.print(new String(charBuffer, 0, charLength));
        }
        fr.close();
        
        // ===== 3. 缓冲流（高效） =====
        System.out.println("\n=== 缓冲流 ===");
        String bufferFile = "test_buffer.txt";
        
        long start = System.currentTimeMillis();
        
        // 不带缓冲
        FileOutputStream fos2 = new FileOutputStream("no_buffer.txt");
        for (int i = 0; i < 10000; i++) {
            fos2.write(("第" + i + "行内容\n").getBytes());
        }
        fos2.close();
        long noBuffer = System.currentTimeMillis() - start;
        
        // 带缓冲
        start = System.currentTimeMillis();
        BufferedWriter bw = new BufferedWriter(new FileWriter(bufferFile));
        for (int i = 0; i < 10000; i++) {
            bw.write("第" + i + "行内容");
            bw.newLine();  // 换行
        }
        bw.close();
        long withBuffer = System.currentTimeMillis() - start;
        
        System.out.println("无缓冲耗时：" + noBuffer + "ms");
        System.out.println("有缓冲耗时：" + withBuffer + "ms");
        
        // 读取缓冲流
        BufferedReader br = new BufferedReader(new FileReader(bufferFile));
        String line;
        int lineCount = 0;
        while ((line = br.readLine()) != null) {  // readLine是BufferedReader特有的
            lineCount++;
        }
        br.close();
        System.out.println("共读取" + lineCount + "行");
        
        // ===== 4. 转换流：InputStreamReader/OutputStreamWriter =====
        System.out.println("\n=== 转换流 ===");
        // 字节流 -> 字符流，指定编码
        FileInputStream fis3 = new FileInputStream("test_char.txt");
        InputStreamReader isr = new InputStreamReader(fis3, StandardCharsets.UTF_8);
        BufferedReader reader = new BufferedReader(isr);
        System.out.println(reader.readLine());
        reader.close();
        
        // ===== 5. 数据流：DataInputStream/DataOutputStream =====
        System.out.println("\n=== 数据流 ===");
        String dataFile = "test_data.dat";
        
        // 写入各种类型的数据
        DataOutputStream dos = new DataOutputStream(new FileOutputStream(dataFile));
        dos.writeInt(100);
        dos.writeDouble(3.14159);
        dos.writeUTF("Hello Java");  // UTF格式字符串
        dos.close();
        
        // 读取各种类型的数据
        DataInputStream dis = new DataInputStream(new FileInputStream(dataFile));
        int num = dis.readInt();
        double pi = dis.readDouble();
        String str = dis.readUTF();
        dis.close();
        System.out.println("读取数据：int=" + num + ", double=" + pi + ", String=" + str);
        
        // ===== 6. 对象流：序列化/反序列化 =====
        System.out.println("\n=== 对象流（序列化） ===");
        String objFile = "test_object.txt";
        
        // 序列化（写入对象）
        User user = new User("蜡笔小新", 5, "双叶幼稚园");
        ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(objFile));
        oos.writeObject(user);
        oos.close();
        System.out.println("对象已序列化");
        
        // 反序列化（读取对象）
        ObjectInputStream ois = new ObjectInputStream(new FileInputStream(objFile));
        User readUser = (User) ois.readObject();
        ois.close();
        System.out.println("对象已反序列化：" + readUser);
        
        // ===== 7. try-with-resources自动关闭 =====
        System.out.println("\n=== try-with-resources ===");
        String resourceFile = "test_resource.txt";
        
        try (BufferedReader br2 = new BufferedReader(new FileReader(resourceFile))) {
            String line2;
            while ((line2 = br2.readLine()) != null) {
                System.out.println("读取：" + line2);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    public static void main(String[] args) {
        try {
            byteStreamDemo();
        } catch (IOException e) {
            System.out.println("IO异常：" + e.getMessage());
            e.printStackTrace();
        }
    }
}

/**
 * 可序列化的用户类
 */
class User implements Serializable {
    private static final long serialVersionUID = 1L;  // 版本号
    private String name;
    private int age;
    private String school;
    
    public User(String name, int age, String school) {
        this.name = name;
        this.age = age;
        this.school = school;
    }
    
    @Override
    public String toString() {
        return "User{name='" + name + "', age=" + age + ", school='" + school + "'}";
    }
}
```

**⚠️ 小白易懵点：**

1. **流使用完必须关闭**，否则会资源泄漏。用try-with-resources更安全。
2. **字符流只能用于文本文件**，图片、视频等要用字节流。
3. **read()返回-1表示读完了**，不要用0判断。
4. **序列化需要实现Serializable接口**， transient修饰的字段不会被序列化。
5. **中文乱码问题**：读写时要用统一的编码（推荐UTF-8）。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 4.2 NIO：Java的高效IO

**一句话人话解释：** NIO是Java 4引入的"新版IO"，比传统IO更高效，特别适合高并发场景。

**生活比喻 🍽️：**

传统IO vs NIO，就像餐厅点餐：
- **传统IO（阻塞）**：你去餐厅，点完餐就一直等着，直到菜做好端上来（服务员阻塞等待）
- **NIO（非阻塞）**：你去餐厅，领了一个号码（Selector），去逛街（做其他事），等菜好了会通知你来取（Channel通知）

**技术核心 📖：**

| 传统IO | NIO |
|--------|-----|
| 面向流（Stream） | 面向缓冲区（Buffer） |
| 阻塞IO | 非阻塞IO，支持多路复用 |
| 单向（Input/Output分开） | 双向（Channel可读可写） |

NIO三要素：
- **Channel**：通道，类似IO的Stream，但可读可写
- **Buffer**：缓冲区，数据先放这里
- **Selector**：选择器，一个线程管理多个通道

**代码示例 💻：**

```java
import java.io.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class NIODemo {
    
    // ===== 1. Buffer基本操作 =====
    public static void bufferDemo() {
        System.out.println("=== Buffer基本操作 ===");
        
        // 创建Buffer
        ByteBuffer buffer = ByteBuffer.allocate(10);
        System.out.println("初始状态：");
        System.out.println("  position=" + buffer.position() + 
                         ", limit=" + buffer.limit() + 
                         ", capacity=" + buffer.capacity());
        
        // 写入数据
        buffer.put((byte) 1);
        buffer.put((byte) 2);
        buffer.put((byte) 3);
        System.out.println("\n写入3字节后：");
        System.out.println("  position=" + buffer.position() + 
                         ", limit=" + buffer.limit());
        
        // 切换为读取模式
        buffer.flip();
        System.out.println("\nflip()后：");
        System.out.println("  position=" + buffer.position() + 
                         ", limit=" + buffer.limit());
        
        // 读取数据
        while (buffer.hasRemaining()) {
            System.out.print(buffer.get() + " ");
        }
        
        // 清除缓冲区（数据还在，可以覆盖）
        buffer.clear();
        System.out.println("\n\nclear()后：");
        System.out.println("  position=" + buffer.position() + 
                         ", limit=" + buffer.limit());
        
        // ===== CharBuffer =====
        System.out.println("\n=== CharBuffer ===");
        CharBuffer charBuffer = CharBuffer.allocate(20);
        charBuffer.put("Hello NIO");
        charBuffer.flip();
        
        while (charBuffer.hasRemaining()) {
            System.out.print(charBuffer.get());
        }
        System.out.println();
        
        // ===== 直接缓冲区（堆外内存，性能更好） =====
        System.out.println("\n=== 直接缓冲区 ===");
        ByteBuffer directBuffer = ByteBuffer.allocateDirect(1024);
        System.out.println("是否直接缓冲区：" + directBuffer.isDirect());
    }
    
    // ===== 2. Channel基本操作 =====
    public static void channelDemo() throws IOException {
        System.out.println("\n=== Channel基本操作 ===");
        
        String testFile = "nio_test.txt";
        
        // 写入文件
        try (FileOutputStream fos = new FileOutputStream(testFile);
             FileChannel channel = fos.getChannel()) {
            
            ByteBuffer writeBuffer = ByteBuffer.allocate(1024);
            writeBuffer.put("Hello from NIO Channel!".getBytes(StandardCharsets.UTF_8));
            writeBuffer.flip();
            
            channel.write(writeBuffer);
            System.out.println("写入完成");
        }
        
        // 读取文件
        try (FileInputStream fis = new FileInputStream(testFile);
             FileChannel channel = fis.getChannel()) {
            
            ByteBuffer readBuffer = ByteBuffer.allocate(1024);
            channel.read(readBuffer);
            
            readBuffer.flip();
            String content = StandardCharsets.UTF_8.decode(readBuffer).toString();
            System.out.println("读取内容：" + content);
        }
    }
    
    // ===== 3. 文件通道 + Scatter/Gather =====
    public static void scatterGatherDemo() throws IOException {
        System.out.println("\n=== Scatter/Gather ===");
        
        String testFile = "scatter_gather.txt";
        
        // Gather写入（多个Buffer写入一个Channel）
        try (FileOutputStream fos = new FileOutputStream(testFile);
             FileChannel channel = fos.getChannel()) {
            
            ByteBuffer header = ByteBuffer.allocate(10);
            header.put("Header---".getBytes());
            header.flip();
            
            ByteBuffer body = ByteBuffer.allocate(20);
            body.put("Body of the file".getBytes());
            body.flip();
            
            ByteBuffer[] buffers = {header, body};
            channel.write(buffers);
            System.out.println("Gather写入完成");
        }
        
        // Scatter读取（一个Channel读取到多个Buffer）
        try (FileInputStream fis = new FileInputStream(testFile);
             FileChannel channel = fis.getChannel()) {
            
            ByteBuffer header2 = ByteBuffer.allocate(10);
            ByteBuffer body2 = ByteBuffer.allocate(20);
            
            ByteBuffer[] buffers = {header2, body2};
            channel.read(buffers);
            
            // 读取后需要flip才能正确解析
            header2.flip();
            body2.flip();
            
            System.out.print("Header: ");
            while (header2.hasRemaining()) {
                System.out.print((char) header2.get());
            }
            System.out.print("\nBody: ");
            while (body2.hasRemaining()) {
                System.out.print((char) body2.get());
            }
            System.out.println();
        }
    }
    
    // ===== 4. 内存映射文件 =====
    public static void memoryMappedDemo() throws IOException {
        System.out.println("\n=== 内存映射文件 ===");
        
        String testFile = "mapped_file.txt";
        
        // 创建文件
        RandomAccessFile raf = new RandomAccessFile(testFile, "rw");
        FileChannel channel = raf.getChannel();
        
        // 映射到内存
        MappedByteBuffer mappedBuffer = channel.map(
            FileChannel.MapMode.READ_WRITE, 0, 1024);
        
        // 像操作内存一样操作文件
        mappedBuffer.put(0, (byte) 'H');
        mappedBuffer.put(1, (byte) 'i');
        mappedBuffer.put(2, (byte) '!');
        
        // 强制写入磁盘
        mappedBuffer.force();
        
        // 读取
        mappedBuffer.flip();
        byte[] data = new byte[3];
        mappedBuffer.get(data);
        System.out.println("内存映射读取：" + new String(data));
        
        raf.close();
    }
    
    // ===== 5. 文件复制（高效方式） =====
    public static void fileCopyDemo() throws IOException {
        System.out.println("\n=== 高效文件复制 ===");
        
        String source = "nio_test.txt";
        String dest = "nio_copy.txt";
        
        long start = System.currentTimeMillis();
        
        try (FileInputStream fis = new FileInputStream(source);
             FileOutputStream fos = new FileOutputStream(dest);
             FileChannel inChannel = fis.getChannel();
             FileChannel outChannel = fos.getChannel()) {
            
            // 使用transferTo直接传输（零拷贝）
            long size = inChannel.size();
            long transferred = 0;
            while (transferred < size) {
                transferred += inChannel.transferTo(
                    transferred, size - transferred, outChannel);
            }
        }
        
        long elapsed = System.currentTimeMillis() - start;
        System.out.println("文件复制完成，耗时：" + elapsed + "ms");
        
        // 读取验证
        String content = new String(Files.readAllBytes(Paths.get(dest)), StandardCharsets.UTF_8);
        System.out.println("复制内容验证：" + content);
    }
    
    // ===== 6. Path和Files工具 =====
    public static void pathAndFilesDemo() throws IOException {
        System.out.println("\n=== Path和Files ===");
        
        // Path
        Path path = Paths.get("test_dir", "sub_dir", "file.txt");
        System.out.println("路径：" + path);
        System.out.println("文件名前缀：" + path.getFileName());
        System.out.println("父路径：" + path.getParent());
        
        // Files工具
        Path dir = Paths.get("demo_dir");
        Files.createDirectories(dir);
        
        Path file = dir.resolve("demo.txt");
        Files.write(file, "Hello Files API!".getBytes(StandardCharsets.UTF_8));
        
        List<String> lines = Files.readAllLines(file, StandardCharsets.UTF_8);
        System.out.println("读取文件：" + lines);
        
        // 遍历目录
        Files.list(dir).forEach(p -> System.out.println("目录内容：" + p.getFileName()));
        
        // 清理
        Files.deleteIfExists(file);
        Files.deleteIfExists(dir);
    }
    
    public static void main(String[] args) {
        try {
            bufferDemo();
            channelDemo();
            scatterGatherDemo();
            memoryMappedDemo();
            fileCopyDemo();
            pathAndFilesDemo();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

**⚠️ 小白易懵点：**

1. **NIO不是替代IO**，是补充。普通文件操作IO就够了，高并发网络编程用NIO。
2. **Buffer的position/limit/capacity**：position是当前位置，limit是可读/写上限，capacity是总容量。
3. **flip()和clear()的区别**：flip切换到读模式，clear清空但保留数据（覆盖时用）。
4. **ByteBuffer.allocate vs allocateDirect**：allocate在堆上，allocateDirect更快但需额外内存。
5. **Selector适合服务端**，处理大量低并发连接；客户端直连用传统IO更简单。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 4.3 多线程：Java的并发世界

**一句话人话解释：** 多线程就是让程序同时做多件事，就像你一边听歌一边下载电影。

**生活比喻 🍳：**

想象你做早餐：
- **单线程**：先煮粥（等10分钟）→ 再煎蛋（等3分钟）→ 再烤面包（等2分钟）= 总共15分钟
- **多线程**：同时煮粥、煎蛋、烤面包 = 总共10分钟（最长那个）

**技术核心 📖：**

| 创建方式 | 说明 |
|----------|------|
| extends Thread | 继承Thread类，重写run() |
| implements Runnable | 实现Runnable接口 |
| implements Callable | 实现Callable接口，有返回值 |
| 线程池 | 复用线程，避免频繁创建销毁 |

**代码示例 💻：**

```java
import java.util.concurrent.*;

public class MultiThreadDemo {
    
    // ===== 1. 继承Thread =====
    static class MyThread extends Thread {
        private String name;
        
        public MyThread(String name) {
            this.name = name;
        }
        
        @Override
        public void run() {
            for (int i = 0; i < 3; i++) {
                System.out.println(name + "正在执行，计数：" + i);
                try {
                    Thread.sleep(100);  // 休眠100毫秒
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }
    
    // ===== 2. 实现Runnable =====
    static class MyRunnable implements Runnable {
        private String name;
        
        public MyRunnable(String name) {
            this.name = name;
        }
        
        @Override
        public void run() {
            for (int i = 0; i < 3; i++) {
                System.out.println(name + "正在执行，计数：" + i);
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }
    
    // ===== 3. 实现Callable（可以有返回值） =====
    static class MyCallable implements Callable<Integer> {
        private int n;
        
        public MyCallable(int n) {
            this.n = n;
        }
        
        @Override
        public Integer call() throws Exception {
            int sum = 0;
            for (int i = 1; i <= n; i++) {
                sum += i;
                Thread.sleep(10);
            }
            return sum;
        }
    }
    
    // ===== 4. 线程同步：synchronized =====
    static class Counter {
        private int count = 0;
        
        // synchronized方法：锁定当前对象
        public synchronized void increment() {
            count++;
        }
        
        public synchronized int getCount() {
            return count;
        }
    }
    
    static class CounterThread extends Thread {
        private Counter counter;
        
        public CounterThread(Counter counter) {
            this.counter = counter;
        }
        
        @Override
        public void run() {
            for (int i = 0; i < 1000; i++) {
                counter.increment();
            }
        }
    }
    
    // ===== 5. Lock锁 =====
    static class LockCounter {
        private int count = 0;
        private Lock lock = new ReentrantLock();
        
        public void increment() {
            lock.lock();
            try {
                count++;
            } finally {
                lock.unlock();  // 必须在finally中释放
            }
        }
        
        public int getCount() {
            return count;
        }
    }
    
    // ===== 6. volatile保证可见性 =====
    static class VolatileDemo extends Thread {
        // volatile保证可见性：一个线程修改后，其他线程立即可见
        private volatile boolean running = true;
        
        public void stopRunning() {
            running = false;
        }
        
        @Override
        public void run() {
            int count = 0;
            while (running) {
                count++;
            }
            System.out.println("线程停止，计数：" + count);
        }
    }
    
    // ===== 7. 线程间通信：wait/notify =====
    static class SharedResource {
        private int data;
        private boolean hasData = false;
        
        public synchronized void produce(int value) {
            while (hasData) {
                try {
                    wait();  // 数据还没被消费，等待
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            data = value;
            hasData = true;
            System.out.println("生产了：" + data);
            notify();  // 通知消费者
        }
        
        public synchronized int consume() {
            while (!hasData) {
                try {
                    wait();  // 没有数据，等待
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            hasData = false;
            System.out.println("消费了：" + data);
            notify();  // 通知生产者
            return data;
        }
    }
    
    // ===== 8. 线程池 =====
    static class Task implements Runnable {
        private int taskId;
        
        public Task(int taskId) {
            this.taskId = taskId;
        }
        
        @Override
        public void run() {
            System.out.println("任务" + taskId + "正在执行，线程：" + Thread.currentThread().getName());
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            System.out.println("任务" + taskId + "执行完成");
        }
    }
    
    // ===== main方法 =====
    public static void main(String[] args) throws ExecutionException, InterruptedException {
        
        // ===== 1. Thread基本使用 =====
        System.out.println("=== Thread基本使用 ===");
        MyThread t1 = new MyThread("线程A");
        MyThread t2 = new MyThread("线程B");
        t1.start();  // 调用start()而不是run()
        t2.start();
        
        // ===== 2. Runnable使用 =====
        System.out.println("\n=== Runnable使用 ===");
        Thread t3 = new Thread(new MyRunnable("线程C"));
        Thread t4 = new Thread(new MyRunnable("线程D"));
        t3.start();
        t4.start();
        
        // ===== 3. Callable使用 =====
        System.out.println("\n=== Callable使用 ===");
        ExecutorService executor = Executors.newFixedThreadPool(2);
        Future<Integer> future = executor.submit(new MyCallable(100));
        System.out.println("正在计算1+2+...+100...");
        Integer result = future.get();  // 阻塞等待结果
        System.out.println("计算结果：" + result);
        
        // ===== 4. 线程同步测试 =====
        System.out.println("\n=== 线程同步测试 ===");
        Counter counter = new Counter();
        Thread[] threads = new Thread[10];
        for (int i = 0; i < 10; i++) {
            threads[i] = new CounterThread(counter);
            threads[i].start();
        }
        for (Thread t : threads) {
            t.join();  // 等待所有线程结束
        }
        System.out.println("最终计数（应该是10000）：" + counter.getCount());
        
        // ===== 5. Lock锁测试 =====
        System.out.println("\n=== Lock锁测试 ===");
        LockCounter lockCounter = new LockCounter();
        Thread[] lockThreads = new Thread[10];
        for (int i = 0; i < 10; i++) {
            lockThreads[i] = new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    lockCounter.increment();
                }
            });
            lockThreads[i].start();
        }
        for (Thread t : lockThreads) {
            t.join();
        }
        System.out.println("Lock最终计数（应该是10000）：" + lockCounter.getCount());
        
        // ===== 6. volatile使用 =====
        System.out.println("\n=== volatile使用 ===");
        VolatileDemo volatileThread = new VolatileDemo();
        volatileThread.start();
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        volatileThread.stopRunning();  // 请求停止
        System.out.println("主线程请求停止");
        
        // ===== 7. 线程池使用 =====
        System.out.println("\n=== 线程池 ===");
        ExecutorService pool = Executors.newFixedThreadPool(3);
        for (int i = 1; i <= 5; i++) {
            pool.submit(new Task(i));
        }
        pool.shutdown();  // 关闭线程池，不再接受新任务
        pool.awaitTermination(10, TimeUnit.SECONDS);  // 等待所有任务完成
        System.out.println("所有任务完成");
        
        // ===== 8. 线程间通信 =====
        System.out.println("\n=== 线程间通信 ===");
        SharedResource resource = new SharedResource();
        
        Thread producer = new Thread(() -> {
            for (int i = 1; i <= 3; i++) {
                resource.produce(i);
            }
        }, "生产者");
        
        Thread consumer = new Thread(() -> {
            for (int i = 1; i <= 3; i++) {
                resource.consume();
            }
        }, "消费者");
        
        producer.start();
        consumer.start();
        
        // 关闭executor
        executor.shutdown();
    }
}
```

**⚠️ 小白易懵点：**

1. **调用start()而不是run()**！run()只是普通方法调用，不会创建新线程。
2. **Thread.sleep()会阻塞当前线程**，不会释放锁。
3. **synchronized会自动释放锁**，Lock必须手动释放（推荐在finally中）。
4. **volatile不能保证原子性**，只能保证可见性。++操作不是原子的。
5. **不要直接创建太多线程**，用线程池管理。`Executors`工具类提供多种线程池。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 4.4 JVM内存模型：Java的内存管理

**一句话人话解释：** JVM内存分为几块区域，程序运行时数据就存在这些区域里，理解它们能帮你写出更好的代码。

**生活比喻 🏠：**

想象一个大型仓库+工厂：
- **堆（Heap）**：公共大仓库，所有人都往里面放东西、拿东西。垃圾回收在这里进行。
- **栈（Stack）**：每个工人的工作台，只能自己用。方法调用、局部变量在这里。
- **方法区（Method Area）**：存放所有产品的说明书（类信息），所有工人都能查阅。
- **程序计数器（PC Register）**：工人当前正在看的说明书页码。
- **本地方法栈**：工人用非Java语言（如C）交流的地方。

**技术核心 📖：**

```
JVM内存区域：

堆（Heap）← 垃圾回收的主要战场
├── Young Generation（年轻代）
│   ├── Eden（伊甸园区）
│   └── Survivor（S0, S1 幸存者区）
└── Old Generation（老年代）

非堆区域
├── 方法区（Method Area）← 类的信息、常量
├── 程序计数器（PC Register）
├── 虚拟机栈（VM Stack）← 方法调用栈
└── 本地方法栈（Native Stack）

直接内存（Off-Heap）
└── NIO使用的直接缓冲区
```

**代码示例 💻：**

```java
import java.util.*;

/**
 * JVM内存演示
 */
public class JVMMemoryDemo {
    
    // 类变量（存在方法区）
    private static int classVariable = 100;
    
    // 实例变量（存在堆中）
    private int instanceVariable;
    private String name;
    
    public JVMMemoryDemo(String name) {
        this.name = name;
        this.instanceVariable = 0;
    }
    
    // ===== 方法（存在虚拟机栈） =====
    public void methodWithLocalVariables() {
        // 局部变量（存在栈中）
        int localVar = 10;
        String localStr = "局部字符串";
        
        // 对象引用（引用本身在栈中，对象在堆中）
        List<String> list = new ArrayList<>();
        list.add("元素1");
        list.add("元素2");
        
        System.out.println("方法内局部变量：" + localVar);
        System.out.println("方法内list：" + list);
        
        // 局部变量随方法结束而销毁
    }
    
    // ===== 递归调用（栈帧） =====
    public static int recursive(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * recursive(n - 1);
    }
    
    // ===== 对象创建和垃圾回收演示 =====
    public static void gcDemo() {
        System.out.println("\n=== 垃圾回收演示 ===");
        
        // 创建对象（在堆中分配内存）
        for (int i = 1; i <= 5; i++) {
            JVMMemoryDemo obj = new JVMMemoryDemo("对象" + i);
            obj.instanceVariable = i * 10;
            System.out.println("创建了：" + obj.name + ", 值：" + obj.instanceVariable);
        }
        
        // 此时之前的5个对象已经失去引用，可能被回收
        
        // 手动建议GC（不保证立即执行）
        System.gc();
        
        // 创建一个对象并保持引用
        JVMMemoryDemo retained = new JVMMemoryDemo("保留对象");
        retained.instanceVariable = 999;
        System.out.println("保留对象：" + retained.name);
        
        // 引用消失
        retained = null;  // 之前的对象现在没有引用了
        
        // null引用可以被回收
    }
    
    // ===== 内存泄漏示例 =====
    public static void memoryLeakDemo() {
        System.out.println("\n=== 内存泄漏示例 ===");
        
        // 场景1：集合类未清理
        List<Object> cache = new ArrayList<>();
        for (int i = 0; i < 100000; i++) {
            cache.add(new Object());  // 不断添加，不清理
        }
        System.out.println("cache大小：" + cache.size());
        // cache.clear();  // 需要手动清理
        // cache = null;    // 或置空
        
        // 场景2：静态集合
        // static Map<String, Object> staticMap = new HashMap<>();
        // 静态集合除非手动清理，否则会一直占用内存
        
        // 场景3：监听器和回调
        // listenerList.add(new Listener() {...});
        // 记得在不需要时remove
        
        System.out.println("注意：实际开发中要避免内存泄漏");
    }
    
    // ===== String的驻留池（方法区） =====
    public static void stringPoolDemo() {
        System.out.println("\n=== String驻留池 ===");
        
        // 字面量字符串会被放入常量池
        String s1 = "Hello";
        String s2 = "Hello";
        
        System.out.println("s1 == s2：" + (s1 == s2));  // true（同一个对象）
        
        // new出来的对象在堆中
        String s3 = new String("Hello");
        System.out.println("s1 == s3：" + (s1 == s3));  // false（不同对象）
        
        // intern()可以把堆中的对象加入常量池
        String s4 = s3.intern();
        System.out.println("s1 == s4（intern后）：" + (s1 == s4));  // true
        
        // ===== 字符串拼接 =====
        String a = "a" + "b";       // 编译时优化为 "ab"
        String b = "ab";
        System.out.println("字面量拼接 == 常量：" + (a == b));  // true
        
        // 变量拼接会创建新对象
        String c = new String("a") + new String("b");
        System.out.println("new String + == 常量：" + (c == b));  // false
        System.out.println("new String + intern == 常量：" + (c.intern() == b));  // true
    }
    
    // ===== 逃逸分析演示 =====
    public static void escapeAnalysisDemo() {
        System.out.println("\n=== 逃逸分析 ===");
        
        // 创建大量小对象
        long start = System.currentTimeMillis();
        List<JVMMemoryDemo> list = new ArrayList<>();
        for (int i = 0; i < 1000000; i++) {
            JVMMemoryDemo demo = new JVMMemoryDemo("obj" + i);
            // 如果demo没有逃逸出方法，JIT可能优化为栈上分配
            // demo.instanceVariable = i;
            // 简化处理，不保留引用
        }
        long end = System.currentTimeMillis();
        System.out.println("创建100万个对象耗时：" + (end - start) + "ms");
    }
    
    // ===== 模拟栈溢出 =====
    public static void stackOverflowDemo() {
        System.out.println("\n=== 栈溢出模拟 ===");
        System.out.println("当前栈深度测试...");
        
        // 递归没有终止条件会导致StackOverflowError
        // recursive(10000);  // 取消注释会导致栈溢出
        
        try {
            // 模拟大量方法调用
            simulateDeepStack(0);
        } catch (StackOverflowError e) {
            System.out.println("捕获到StackOverflowError！");
        }
    }
    
    private static void simulateDeepStack(int depth) {
        if (depth > 10000) {
            System.out.println("达到深度：" + depth);
            return;
        }
        simulateDeepStack(depth + 1);
    }
    
    public static void main(String[] args) {
        System.out.println("=== JVM内存模型演示 ===");
        System.out.println("JVM参数：-Xms256m -Xmx512m -Xss2m");
        
        // 基本调用
        JVMMemoryDemo demo = new JVMMemoryDemo("主对象");
        demo.methodWithLocalVariables();
        
        // 递归
        System.out.println("\n递归计算5! = " + recursive(5));
        
        // GC演示
        gcDemo();
        
        // String池
        stringPoolDemo();
        
        // 逃逸分析
        escapeAnalysisDemo();
        
        // 栈溢出
        stackOverflowDemo();
        
        // 打印内存信息
        Runtime rt = Runtime.getRuntime();
        System.out.println("\n=== JVM内存信息 ===");
        System.out.println("最大内存：" + rt.maxMemory() / 1024 / 1024 + "MB");
        System.out.println("总内存：" + rt.totalMemory() / 1024 / 1024 + "MB");
        System.out.println("空闲内存：" + rt.freeMemory() / 1024 / 1024 + "MB");
        System.out.println("可用处理器：" + rt.availableProcessors());
    }
}
```

**⚠️ 小白易懵点：**

1. **堆是GC的主要区域**，所有new出来的对象都在这里。
2. **栈存储方法调用和局部变量**，每个线程有自己的栈。
3. **方法区存储类信息**（Java8后改为元空间，在本地内存中）。
4. **直接内存是堆外内存**，NIO的DirectByteBuffer使用这块内存。
5. **Minor GC vs Full GC**：Minor GC清理年轻代，快；Full GC清理整个堆，慢。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 4.5 Lambda与函数式接口：Java的简洁之道

**一句话人话解释：** Lambda表达式就是Java的"匿名函数"，让你写更少的代码表达同样的意思。

**生活比喻 📝：**

普通写法 vs Lambda，就像：
- **普通写法**："请这位穿蓝色衣服、戴眼镜、身高1米7的人过来"（完整描述）
- **Lambda写法**："那个"（指向那个人，简短直接）

**技术核心 📖：**

```java
// 匿名内部类
Runnable r1 = new Runnable() {
    @Override
    public void run() {
        System.out.println("Hello");
    }
};

// Lambda表达式（简洁）
Runnable r2 = () -> System.out.println("Hello");

// 有参数
Comparator<String> c1 = new Comparator<String>() {
    @Override
    public int compare(String s1, String s2) {
        return s1.length() - s2.length();
    }
};

// Lambda
Comparator<String> c2 = (s1, s2) -> s1.length() - s2.length();

// 有方法体
Comparator<String> c3 = (s1, s2) -> {
    int result = s1.length() - s2.length();
    return result;
};
```

**代码示例 💻：**

```java
import java.util.*;
import java.util.function.*;
import java.util.stream.*;

public class LambdaDemo {
    
    // ===== 1. 函数式接口（只有一个抽象方法的接口） =====
    @FunctionalInterface  // 编译检查，确保是函数式接口
    interface MathOperation {
        int calculate(int a, int b);
    }
    
    // ===== 2. Lambda基本使用 =====
    public static void basicLambda() {
        System.out.println("=== Lambda基本使用 ===");
        
        // 无参数
        Runnable r = () -> System.out.println("Hello Lambda!");
        r.run();
        
        // 一个参数（括号可省略）
        Consumer<String> consumer = s -> System.out.println("收到：" + s);
        consumer.accept("消息");
        
        // 多个参数
        MathOperation add = (a, b) -> a + b;
        MathOperation multiply = (a, b) -> a * b;
        
        System.out.println("5 + 3 = " + add.calculate(5, 3));
        System.out.println("5 * 3 = " + multiply.calculate(5, 3));
        
        // 带方法体
        MathOperation div = (a, b) -> {
            if (b == 0) return 0;
            return a / b;
        };
        System.out.println("10 / 2 = " + div.calculate(10, 2));
    }
    
    // ===== 3. Java内置函数式接口 =====
    public static void builtInInterfaces() {
        System.out.println("\n=== Java内置函数式接口 ===");
        
        // Predicate<T>：T -> boolean（断言）
        Predicate<Integer> isEven = n -> n % 2 == 0;
        System.out.println("10是偶数吗：" + isEven.test(10));
        System.out.println("7是偶数吗：" + isEven.test(7));
        
        // Predicate组合
        Predicate<Integer> isPositive = n -> n > 0;
        System.out.println("10是偶数且正数：" + isEven.and(isPositive).test(10));
        System.out.println("-10是偶数且正数：" + isEven.and(isPositive).test(-10));
        
        // Function<T, R>：T -> R（转换）
        Function<String, Integer> strToLength = String::length;
        System.out.println("'Hello'长度：" + strToLength.apply("Hello"));
        
        Function<String, String> toUpperCase = String::toUpperCase;
        System.out.println("'hello'大写：" + toUpperCase.apply("hello"));
        
        // Function组合
        Function<String, Integer> strToLengthAndDouble = strToLength.andThen(n -> n * 2);
        System.out.println("'Java'长度*2：" + strToLengthAndDouble.apply("Java"));
        
        // Consumer<T>：T -> void（消费）
        Consumer<String> printer = s -> System.out.println("打印：" + s);
        printer.accept("测试消息");
        
        // Supplier<T>：() -> T（生产）
        Supplier<List<String>> listSupplier = () -> new ArrayList<>();
        List<String> list = listSupplier.get();
        list.add("元素");
        System.out.println("Supplier创建的列表：" + list);
        
        // UnaryOperator<T>：T -> T（一元操作）
        UnaryOperator<Integer> doubleValue = n -> n * 2;
        System.out.println("5翻倍：" + doubleValue.apply(5));
        
        // BinaryOperator<T>：(T, T) -> T（二元操作）
        BinaryOperator<Integer> max = Integer::max;
        System.out.println("max(3, 7)：" + max.apply(3, 7));
    }
    
    // ===== 4. 方法引用 =====
    public static void methodReference() {
        System.out.println("\n=== 方法引用 ===");
        
        // 静态方法引用
        Function<Double, Long> f1 = Math::round;
        System.out.println("round(3.7) = " + f1.apply(3.7));
        
        // 实例方法引用（特定对象）
        String str = "Hello";
        Function<Integer, Character> f2 = str::charAt;
        System.out.println("charAt(1) = " + f2.apply(1));
        
        // 实例方法引用（任意对象）
        Function<String, String> f3 = String::toUpperCase;
        System.out.println("'hello'大写 = " + f3.apply("hello"));
        
        // 构造器引用
        Supplier<ArrayList<String>> listSupplier = ArrayList::new;
        ArrayList<String> list = listSupplier.get();
        list.add("new ArrayList");
        System.out.println("构造器创建的列表：" + list);
        
        // 数组构造器引用
        Function<Integer, String[]> arrayCreator = String[]::new;
        String[] array = arrayCreator.apply(5);
        System.out.println("创建了长度为" + array.length + "的数组");
    }
    
    // ===== 5. Lambda与集合 =====
    public static void lambdaWithCollections() {
        System.out.println("\n=== Lambda与集合 ===");
        
        List<String> names = Arrays.asList("Charlie", "Alice", "Bob", "David");
        
        // forEach
        System.out.println("遍历列表：");
        names.forEach(name -> System.out.println("  " + name));
        
        // 简化为方法引用
        names.forEach(System.out::println);
        
        // removeIf
        List<Integer> numbers = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5, 6));
        numbers.removeIf(n -> n % 2 == 0);  // 删除偶数
        System.out.println("删除偶数后：" + numbers);
        
        // sort with lambda
        names.sort((a, b) -> a.length() - b.length());
        System.out.println("按长度排序：" + names);
        
        // 简化为Comparator方法引用
        names.sort(Comparator.comparingInt(String::length));
        System.out.println("按长度排序（方法引用）：" + names);
        
        // Map操作
        Map<String, Integer> scores = new HashMap<>();
        scores.put("Alice", 90);
        scores.put("Bob", 85);
        scores.put("Charlie", 95);
        
        scores.forEach((name, score) -> System.out.println(name + " = " + score));
    }
    
    // ===== 6. Lambda与Stream =====
    public static void lambdaWithStream() {
        System.out.println("\n=== Lambda与Stream ===");
        
        List<Student> students = Arrays.asList(
            new Student("张三", 85),
            new Student("李四", 92),
            new Student("王五", 78),
            new Student("赵六", 95),
            new Student("钱七", 88)
        );
        
        // 过滤
        List<Student> topStudents = students.stream()
            .filter(s -> s.getScore() >= 90)
            .collect(Collectors.toList());
        System.out.println("90分以上的学生：" + 
            topStudents.stream().map(Student::getName).collect(Collectors.toList()));
        
        // 转换
        List<String> names = students.stream()
            .map(Student::getName)
            .collect(Collectors.toList());
        System.out.println("所有学生姓名：" + names);
        
        // 求平均分
        double avgScore = students.stream()
            .mapToInt(Student::getScore)
            .average()
            .orElse(0);
        System.out.println("平均分：" + avgScore);
        
        // 分组
        Map<String, List<Student>> grouped = students.stream()
            .collect(Collectors.groupingBy(s -> 
                s.getScore() >= 90 ? "优秀" : s.getScore() >= 80 ? "良好" : "及格"));
        grouped.forEach((level, list) -> 
            System.out.println(level + "：" + list.stream().map(Student::getName).collect(Collectors.toList())));
    }
    
    // ===== 7. 闭包与Effectively Final =====
    public static void closureDemo() {
        System.out.println("\n=== 闭包 ===");
        
        int factor = 2;  // effectively final（虽然不是final，但值没变过）
        
        Function<Integer, Integer> multiplier = n -> n * factor;
        System.out.println("10 * 2 = " + multiplier.apply(10));
        
        // factor++;  // 编译错误！Lambda引用的变量必须是effectively final
    }
    
    // ===== 8. 实际应用场景 =====
    public static void realWorldScenarios() {
        System.out.println("\n=== 实际应用场景 ===");
        
        // 场景1：线程
        new Thread(() -> {
            System.out.println("Lambda创建线程");
        }).start();
        
        // 场景2：GUI事件处理
        // button.addActionListener(e -> System.out.println("按钮点击"));
        
        // 场景3：排序
        List<String> list = new ArrayList<>(Arrays.asList("banana", "apple", "cherry"));
        list.sort((a, b) -> a.compareTo(b));
        System.out.println("排序后：" + list);
        
        // 场景4：延迟执行
        Supplier<String> lazyMessage = () -> {
            System.out.println("计算中...");
            return "Hello";
        };
        System.out.println("准备获取值");
        System.out.println("获取值：" + lazyMessage.get());  // 这里才真正计算
    }
    
    public static void main(String[] args) {
        basicLambda();
        builtInInterfaces();
        methodReference();
        lambdaWithCollections();
        lambdaWithStream();
        closureDemo();
        realWorldScenarios();
    }
}

/**
 * 学生类
 */
class Student {
    private String name;
    private int score;
    
    public Student(String name, int score) {
        this.name = name;
        this.score = score;
    }
    
    public String getName() { return name; }
    public int getScore() { return score; }
}
```

**⚠️ 小白易懵点：**

1. **Lambda表达式必须有函数式接口对应**，不能随便写。
2. **Lambda外部的变量必须是effectively final**（或显式final），不能修改。
3. **方法引用不是Lambda**，但效果类似，更简洁。
4. **`this`在Lambda中指外围类**，不像匿名内部类那样有自己的this。
5. **不要过度使用Lambda**，简单逻辑用Lambda，复杂逻辑用普通方法。

![困惑](https://www.coze.cn/s/J7Uf5Y3nAA8/)

### 4.6 注解：Java的元数据标签

**一句话人话解释：** 注解就是给你的代码贴标签，告诉编译器、工具或框架"这段代码是干什么的"。

**生活比喻 🏷️：**

想象你给文件贴便签：
- 普通便签：@重要 @待办 @紧急
- 编程便签：@Override @Deprecated @Autowired

这些"便签"告诉别人（或工具）这个文件/方法是干什么用的。

**技术核心 📖：**

```java
// 注解定义
public @interface 注解名 {
    // 注解属性
    String value() default "默认值";
    int count() default 1;
}

// 注解使用
@注解名(value = "test", count = 5)
public class MyClass { }

// 元注解（注解的注解）
@Retention(RetentionPolicy.RUNTIME)  // 什么时候有效
@Target(ElementType.METHOD)          // 用在哪里
@Documented                          // 是否生成文档
@Inherited                           // 是否可继承
```

**代码示例 💻：**

```java
import java.lang.annotation.*;
import java.lang.reflect.*;

// ===== 1. 内置注解 =====
class BuiltInAnnotations {
    
    // @Override：重写方法
    @Override
    public String toString() {
        return "MyClass";
    }
    
    // @Deprecated：标记过时
    @Deprecated
    public void oldMethod() {
        System.out.println("这是一个过时的方法");
    }
    
    // @SuppressWarnings：抑制警告
    @SuppressWarnings("unchecked")
    public void rawTypeDemo() {
        java.util.List list = new java.util.ArrayList();  // raw type
        list.add("item");
    }
    
    // @FunctionalInterface：函数式接口
    @FunctionalInterface
    interface MyFunction {
        int apply(int a, int b);
    }
}

// ===== 2. 自定义注解 =====
/**
 * 水果颜色注解
 */
@Retention(RetentionPolicy.RUNTIME)  // 运行时保留，可通过反射读取
@Target(ElementType.FIELD)           // 只能用在字段上
@interface FruitColor {
    String color() default "unknown";  // 带默认值
}

/**
 * 水果名称注解
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface FruitName {
    String value();  // 不带默认值，使用时必须指定
}

/**
 * 水果供应者注解
 */
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.FIELD, ElementType.METHOD})  // 可用于字段和方法
@interface FruitProvider {
    String provider() default "未知";
    String address() default "未知地址";
    String phone() default "无";
}

/**
 * 水果信息类（使用注解）
 */
class FruitInfo {
    @FruitName("Apple")
    private String appleName;
    
    @FruitColor(color = "Red")
    @FruitProvider(provider = "红富士农场", address = "山东烟台")
    private String appleProvider;
    
    @FruitName("Banana")
    private String bananaName;
    
    @FruitColor(color = "Yellow")
    private String bananaProvider;
}

// ===== 3. 注解处理器（反射读取注解） =====
public class AnnotationProcessor {
    
    public static void main(String[] args) throws Exception {
        
        // ===== 读取类上的注解 =====
        System.out.println("=== 读取类注解 ===");
        
        Class<MyAnnotation> clazz = MyAnnotation.class;
        if (clazz.isAnnotationPresent(MyAnnotation.class)) {
            MyAnnotation annotation = clazz.getAnnotation(MyAnnotation.class);
            System.out.println("类名：" + annotation.name());
            System.out.println("描述：" + annotation.description());
            System.out.println("优先级：" + annotation.priority());
        }
        
        // ===== 读取方法注解 =====
        System.out.println("\n=== 读取方法注解 ===");
        
        Method[] methods = clazz.getMethods();
        for (Method method : methods) {
            if (method.isAnnotationPresent(MethodInfo.class)) {
                MethodInfo info = method.getAnnotation(MethodInfo.class);
                System.out.println("方法：" + method.getName());
                System.out.println("  作者：" + info.author());
                System.out.println("  版本：" + info.version());
                System.out.println("  日期：" + info.date());
            }
        }
        
        // ===== 读取字段注解 =====
        System.out.println("\n=== 读取字段注解 ===");
        
        Class<FruitInfo> fruitClass = FruitInfo.class;
        Field[] fields = fruitClass.getDeclaredFields();
        for (Field field : fields) {
            if (field.isAnnotationPresent(FruitName.class)) {
                FruitName name = field.getAnnotation(FruitName.class);
                System.out.println("字段：" + field.getName() + "，名称注解：" + name.value());
            }
            if (field.isAnnotationPresent(FruitColor.class)) {
                FruitColor color = field.getAnnotation(FruitColor.class);
                System.out.println("字段：" + field.getName() + "，颜色注解：" + color.color());
            }
            if (field.isAnnotationPresent(FruitProvider.class)) {
                FruitProvider provider = field.getAnnotation(FruitProvider.class);
                System.out.println("字段：" + field.getName() + "，供应者：" + provider.provider());
            }
        }
        
        // ===== 读取所有注解 =====
        System.out.println("\n=== 读取所有注解 ===");
        
        Annotation[] annotations = clazz.getAnnotations();
        for (Annotation ann : annotations) {
            System.out.println("注解：" + ann.annotationType().getSimpleName());
        }
        
        // ===== 使用注解控制逻辑 =====
        System.out.println("\n=== 注解控制逻辑 ===");
        
        UserService service = new UserService();
        User user = new User();
        
        // 模拟检查权限
        if (user.getClass().isAnnotationPresent(RequirePermission.class)) {
            RequirePermission rp = user.getClass().getAnnotation(RequirePermission.class);
            System.out.println("需要权限：" + Arrays.toString(rp.permissions()));
            // 这里可以检查用户是否有相应权限
        }
        
        // ===== 常用框架注解示例 =====
        System.out.println("\n=== 框架注解示例 ===");
        System.out.println("常见框架注解：");
        System.out.println("- Spring: @Component, @Service, @Autowired, @RequestMapping");
        System.out.println("- JPA: @Entity, @Table, @Column, @Id");
        System.out.println("- Lombok: @Data, @Getter, @Setter, @Builder");
        System.out.println("- JUnit: @Test, @Before, @After");
        
        // ===== 注解与单元测试 =====
        System.out.println("\n=== 注解与单元测试 ===");
        
        Calculator calc = new Calculator();
        int result = calc.add(2, 3);
        System.out.println("2 + 3 = " + result);
        
        // 简单的断言
        assert result == 5 : "计算错误！";
        System.out.println("测试通过！");
    }
}

// ===== 自定义注解示例 =====

/**
 * 类级别注解
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface MyAnnotation {
    String name() default "未命名";
    String description() default "无描述";
    int priority() default 1;
}

/**
 * 方法级别注解
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface MethodInfo {
    String author() default "未知";
    String version() default "1.0";
    String date() default "2024-01-01";
}

/**
 * 权限注解
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface RequirePermission {
    String[] permissions();
}

/**
 * 用户类（带权限注解）
 */
@RequirePermission(permissions = {"USER_READ", "USER_WRITE"})
class User {
    private String name;
    public String getName() { return name; }
}

/**
 * 用户服务类
 */
class UserService {
    @MethodInfo(author = "张三", version = "2.0", date = "2024-01-15")
    public void createUser(User user) {
        System.out.println("创建用户：" + user.getName());
    }
}

/**
 * 计算器类（用于测试）
 */
class Calculator {
    @MethodInfo(author = "李四", version = "1.0")
    public int add(int a, int b) {
        return a + b;
    }
}
```

**⚠️ 小白易懵点：**

1. **注解本身不是功能**，只是标记。需要配合注解处理器（如反射、框架）才有意义。
2. **@Retention决定注解何时有效**：
   - SOURCE：只在源码中，编译后丢弃
   - CLASS：编译时保留，运行时丢弃（JDK默认）
   - RUNTIME：一直保留，可通过反射读取
3. **@Target决定注解用在哪里**，用错会编译错误。
4. **注解属性只能是基本类型、String、Class、枚举、注解及其数组**。
5. **注解属性名是value且只有一个时**，可以省略`value=`，直接写值。

**💡 一句话总结：** IO流是数据读写管道，NIO是非阻塞高效IO，线程池管理并发，JVM内存分堆栈方法区，Lambda让代码更简洁，注解是代码的标签。

---

## 📚 学习资源推荐

1. **官方文档**：https://docs.oracle.com/javase/
2. **在线教程**：https://www.tutorialspoint.com/java/
3. **练习平台**：LeetCode、杭电OJ、牛客网
4. **经典书籍**：《Java核心技术卷》《Effective Java》《深入理解Java虚拟机》

---

## 🎯 下篇预告

Java小白教程下半部分将包含：
- **数据库访问**：JDBC、连接池、事务管理
- **Web开发基础**：Servlet、JSP、MVC模式
- **框架入门**：Spring、Spring Boot
- **项目实战**：完整项目开发流程

敬请期待！

---

*本教程由AI助手编写，如有疏漏欢迎指正！*
