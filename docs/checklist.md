# 考前复习清单

<div class="epigraph" markdown="1">

**「温故而知新，可以为师矣。」**

—— 《论语·为政》

</div>

## 一、必须能默写的计算结论

| 空间 | 基本群 / 同调 |
| --- | --- |
| $S^1$ | $\pi_1\cong\mathbb{Z}$；$H_1\cong\mathbb{Z}$，$H_q=0\ (q\ge2)$ |
| $S^n\ (n\ge2)$ | $\pi_1=0$；$\widetilde H_q(S^n)\cong\mathbb{Z}\ (q=n)$，其余 $0$ |
| $T^n=S^1\times\cdots\times S^1$ | $\pi_1\cong\mathbb{Z}^n$；$H_1\cong\mathbb{Z}^n$ |
| $\mathbb{R}P^{n}\ (n\ge2)$ | $\pi_1\cong\mathbb{Z}_2$（万有复迭 $S^n\to\mathbb{R}P^{n}$）；$H_1\cong\mathbb{Z}_2$ |
| 圆束 $\bigvee^n S^1$ | $\pi_1\cong F_n$（秩 $n$ 自由群）；$H_1\cong\mathbb{Z}^n$ |
| $nT^2$ | $\pi_1=\langle a_i,b_i\mid\prod[a_i,b_i]\rangle$；$H_1\cong\mathbb{Z}^{2n}$ |
| $m\mathbb{R}P^{2}$ | $\pi_1=\langle c_i\mid\prod c_i^2\rangle$；$H_1\cong\mathbb{Z}^{m-1}\oplus\mathbb{Z}_2$ |
| Klein 瓶 | $\pi_1\cong\langle a,b\mid a^2b^2\rangle\cong\langle c,d\mid cdc^{-1} d\rangle$ |
| Möbius 带 | $\simeq S^1$：$\pi_1\cong\mathbb{Z}$（强形变收缩到中圆） |
| 可缩空间（$\mathbb{R}^n$、$\overline{D^n}$） | $\pi_1=0$，$\widetilde H_*=0$ |
| 道路连通 $X$ | $H_0(X)\cong\mathbb{Z}$；一般 $H_0(X)\cong\mathbb{Z}^{\vert \pi_0(X)\vert }$ |
| $p:\mathbb{R}^1\to S^1$ 复迭 | $\mathcal D\cong\mathbb{Z}$；正规；万有 |

## 二、必须能独立复现的重要证明（按优先级）

- $\pi_1(S^1)\cong\mathbb{Z}$ 全套：引理1（不满 $\Rightarrow$ 提升）、引理2（道路提升存在唯一）、
引理3（处处不对径 $\Rightarrow$ 圈数相同，介值定理）、引理4（圈数相同 $\iff$ 定端同伦，
一致连续切片法）、定理（良定义 + 同态 + 满）；
- van Kampen 定理陈述 + 两个特例 + 应用（$\pi_1(S^n)=0$、圆束 $F_n$、曲面群、Klein 瓶 $\langle a,b\mid a^2b^2\rangle$）；
- 基本群同伦不变量：换基点公式（三段式同伦）与"$f_\pi$ 单满"论证；
$\pi_1(X\times Y)\cong\pi_1(X)\times\pi_1(Y)$；
- 复迭空间：提升唯一性（既开又闭）、道路/同伦提升（逐片构造）、提升判据、
$p_\pi$ 单、指数 $=$ 叶数、正规复迭 $\pi_1(B)\cong\mathcal D(E,p)$、万有复迭存在性；
- 链同伦 $\Rightarrow$ 同调相同；$\partial^2=0$ 的符号成对抵消；同伦映射诱导相同同调（棱柱构造）；
$H_0\cong\mathbb{Z}$（道路连通）；$H_1\cong\pi_1$ 交换化（引理 8.18 型证明）；
- Brouwer 不动点（径向投影 + 收缩不存在）；$\deg A=-1$（半球 M–V 归纳）；毛球定理（偶数维，引理 8.11）；
- 商映射判据（紧致 $\to$ Hausdorff 连续满 $\Rightarrow$ 商映射）；$\overline{D^n}/\partial\cong S^n$；
积流形边界公式（Homework 1）；强形变收缩核三例（$\mathbb{R}^n\setminus0\to S^{n-1}$、Möbius 带、圆柱）；
- Jordan–Brouwer 分离定理证明框架（引理 8.5 归纳 + 分支边界论证）；
区域不变性；曲面分类定理陈述及"两两不同胚"的交换化证明。

## 三、判断题自测（不变量辨析）

- 紧致性 **不是**同伦不变量（$\{0\}\simeq\mathbb{R}$）；道路连通性 **是**同伦不变量；
- 同胚 $\Rightarrow$ 同伦等价，反之不然（$\{0\}$ 与 $\mathbb{R}$ 同伦等价但不同胚）；
- $\pi_1(X,x_0)$ 依赖基点；道路连通时同构型不依赖基点（推送同构）；
- $H_1$ 只是 $\pi_1$ 的交换化：存在 $\pi_1$ 不同而 $H_1$ 相同的空间对；
- $S^n\not\simeq S^m\ (m\neq n)$，但同伦等价的空间维数可以不同；
- Hausdorff 不能从流形定义中去掉（线有两个原点的反例）；
- van Kampen 要求交**道路连通**（$\pi_1(S^1)$ 不能用它算）；
复迭存在性要求**半局部单连通**。

## 四、结语

从 Euler 公式走到相对同调，这份整理沿着“以代数量度空间”的主线复述了一遍课程：
定义给出语言，定理给出骨架，证明给出血肉。真正的掌握只有一个标准——
合上讲义，每个 $\square$ 都能亲手填满。

*形虽万变，不变者存；途虽千殊，同归者一。*
