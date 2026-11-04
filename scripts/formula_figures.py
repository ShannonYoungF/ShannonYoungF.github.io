"""Bilingual, progressively enhanced formula diagrams for the reading course.

SVGs are built here, so the figures also work without JavaScript and in print.
All numbers are small teaching examples, not experiments from the paper.
"""

from html import escape
from math import cos, exp, pi, sin, sqrt
import re


def item(section, kind, title, terms, expression, steps, caption, axes):
    return dict(section=section, kind=kind, title=title, terms=terms,
                expression=expression, steps=steps, caption=caption, axes=axes)


FIGURES = [
    item("1.2", "distance", ("乘法为什么是一块面积", "Why multiplication is an area"),
         ["2 m/s", "3 s", "6 m"], "S = {0} × {1} = {2}",
         (["先看高度：每秒走 2 米，所以速度线的高度是 2。", "再看宽度：走 3 秒，就把时间轴上 0 到 3 秒的范围选出来。", "长方形面积是 2×3=6。每一小段时间走的距离加起来，就是总位移。"],
          ["Height: travelling 2 metres each second gives a constant speed of 2.", "Width: select the first 3 seconds on the time axis.", "Area = 2×3 = 6. Adding the distance travelled in each small time interval gives total displacement."]),
         ("恒定速度时，速度曲线下的面积等于位移。", "At constant speed, the area under the speed curve is displacement."), ("时间（秒） · 纵轴：速度（米/秒）", "Time (s) · vertical axis: speed (m/s)")),
    item("1.5", "error", ("绝对值：只量距离，不分左右", "Absolute value measures a gap, regardless of direction"),
         ["ŝ = 10", "s = 12", "|s − ŝ| = 2"], "{2}; {0}, {1}",
         (["先把预测值 10 放在数轴上。", "再标出真实值 12。只有拿到真值，才能比较预测错了多少。", "从 10 到 12 相隔 2 米。绝对值只保留这段距离，反过来相减也还是 2。"],
          ["Put the prediction, 10, on the number line.", "Add the true value, 12. Measuring prediction error requires truth.", "The gap is 2 metres. Absolute value keeps its size, so reversing the subtraction still gives 2."]),
         ("预测误差是预测与真值的距离；它不等于一群预测之间的分散程度。", "Prediction error is distance from truth; it differs from spread among predictions."), ("位置（米）", "Position (m)")),
    item("2.2", "expectation", ("期望：按机会大小分配重量", "Expectation is a probability-weighted balance point"),
         ["xₖ", "P(X=xₖ)", "Σₖ xₖP(X=xₖ)"], "E[X] = {2}; {0} × {1}",
         (["三种可能位置是 9、10、11 米。", "三种情况各占 1/3，所以每个位置放同样的重量。", "加权相加：(9+10+11)/3=10 米。虚线标出平衡点，它概括中心，不代表每次都走到那里。"],
          ["The possible positions are 9, 10, and 11 metres.", "Each has probability 1/3, so the three weights are equal.", "Their weighted sum is (9+10+11)/3 = 10 m. The dashed balance point describes the centre, not every outcome."]),
         ("横轴是可能取值，柱高是概率；本例的均值为 10 米。", "Possible values on the horizontal axis; bar heights are probabilities. The mean is 10 m."), ("位置（米） · 纵轴：概率", "Position (m) · vertical axis: probability")),
    item("2.3", "variance", ("方差：先看离多远，再把距离平方", "Variance: square the distances, then average"),
         ["X−μ", "(X−μ)²", "2/3"], "Var(X) = E[{1}] = {2}; {0} → {1}",
         (["9、10、11 距离均值 10，分别是 −1、0、1。正负偏移相加会抵消。", "平方以后得到 1、0、1。图中的两个同样大的小方块，各表示 1 平方米。", "按三个等可能结果平均：(1+0+1)/3=2/3 平方米；再开平方才得到标准差，约 0.816 米。"],
          ["The deviations of 9, 10, and 11 from mean 10 are −1, 0, and 1. Signed deviations would cancel.", "Squaring gives 1, 0, and 1. The two equal squares each represent 1 square metre.", "Average over the three equally likely outcomes: 2/3 m². Taking its square root gives standard deviation, about 0.816 m."]),
         ("平方避免左右抵消，并让较大的偏离占更大分量。", "Squaring prevents cancellation and gives larger deviations more weight."), ("取值（米） · 方块面积：偏差平方（平方米）", "Value (m) · square areas: squared deviation (m²)")),
    item("2.5", "gaussian", ("正态分布：中心、宽度与高度一起看", "A Gaussian's centre, width, and height"),
         ["μ", "σ", "1/(√(2π)σ)"], "p(x) = {2} exp(−(x−{0})²/(2{1}²))",
         (["虚点线：均值 μ=0，标准差 σ=1，曲线围绕 0 对称。", "虚线：把 μ 改为 1，整条曲线向右平移，宽度不变。", "实线：保持 μ=1，把 σ 改为 2，曲线更宽、峰更低。前面的归一化系数使总面积仍为 1。"],
          ["Dotted: μ=0 and σ=1, symmetric around zero.", "Dashed: change μ to 1. The curve shifts right without changing width.", "Solid: keep μ=1 and change σ to 2. The curve widens and its peak falls. The normalization factor keeps total area equal to 1."]),
         ("点线 N(0,1)、虚线 N(1,1)、实线 N(1,4)；括号中第二项是方差。", "Dotted N(0,1), dashed N(1,1), solid N(1,4); the second parameter is variance."), ("取值 x · 纵轴：概率密度", "Value x · vertical axis: probability density")),
    item("3.2", "covariance", ("协方差里的乘积，什么时候是正的？", "When is the covariance product positive?"),
         ["X−μₓ", "Y−μᵧ", "E[(X−μₓ)(Y−μᵧ)]"], "Cov(X,Y) = {2}; {0} × {1}",
         (["用四个等可能点 (±2,±1) 作例子，两个均值都为 0。先看横向偏移。", "再看纵向偏移。同在均值的右上或左下，两个偏移相乘为正；在另外两象限则为负。", "四个乘积是 +2、−2、−2、+2，平均为 0。正负共同变化会抵消；一般不能由协方差为 0 推出独立。"],
          ["Use four equally likely points (±2,±1). Both means are zero. First inspect horizontal deviations.", "Now inspect vertical deviations. Upper-right and lower-left products are positive; the other quadrants give negative products.", "The products +2, −2, −2, +2 average to zero. Positive and negative contributions cancel. Zero covariance does not generally establish independence."]),
         ("圆点与加号表示正乘积，叉号表示负乘积；本例协方差为 0。", "Circles with plus signs contribute positively; crosses contribute negatively. Covariance is zero here."), ("X 的偏移 · 纵轴：Y 的偏移", "Deviation in X · vertical axis: deviation in Y")),
    item("3.3", "matrix", ("协方差矩阵：看宽度，也看倾斜", "Covariance matrices describe width and tilt"),
         ["Σ₁₁ = 1", "Σ₂₂ = 1", "Σ₁₂ = Σ₂₁ = 0.8"], "Σ : {0}; {1}; {2}",
         (["第一个对角元素给 X 的方差。本例 Var(X)=1。", "第二个对角元素给 Y 的方差。本例 Var(Y)=1。灰色圆表示二者协方差为 0 的对照。", "非对角元素 0.8 使等密度轮廓沿右上方向倾斜：X 偏大时，Y 倾向于也偏大。它不会改变这里的两个边际方差。"],
          ["The first diagonal entry gives Var(X)=1.", "The second gives Var(Y)=1. The grey circle is a zero-covariance reference.", "Off-diagonal entries of 0.8 tilt the density contour upward: larger X tends to accompany larger Y. The two marginal variances remain 1."]),
         ("绿色椭圆为二维高斯的一条等密度轮廓，不是所有点必定落在其中的边界。", "The green ellipse is one equal-density Gaussian contour, not a boundary containing every outcome."), ("X · 纵轴：Y（均值均为 0）", "X · vertical axis: Y (both means zero)")),
    item("3.5", "kernel", ("核函数：隔得越远，联系怎样变弱", "A kernel describes how similarity decays with distance"),
         ["a²", "(t−t′)²", "ℓ²"], "C(t,t′) = {0} exp(−{1}/(2{2}))",
         (["本例 a=1。同一位置的间隔为 0，协方差达到 a²=1。", "取 ℓ=0.2，两点相隔 0.4 时，协方差 exp(−2)≈0.135。", "把长度尺度改为 ℓ=0.5，同样间隔 0.4 下，协方差约 0.726；联系随距离减弱得更慢。"],
          ["Set a=1. At zero separation, covariance is a²=1.", "With ℓ=0.2 and distance 0.4, covariance is exp(−2)≈0.135.", "With ℓ=0.5 at the same distance, covariance is about 0.726. A longer length scale makes the decay slower."]),
         ("虚线 ℓ=0.2，实线 ℓ=0.5；都是教学参数，a 固定为 1。", "Dashed ℓ=0.2; solid ℓ=0.5. Teaching parameters, with a fixed at 1."), ("间隔 |t−t′| · 纵轴：协方差", "Separation |t−t′| · vertical axis: covariance")),
    item("4.2", "linear", ("为什么方差要乘 a 的平方", "Why variance scales by a squared"),
         ["μᵧ = aμₓ+b", "σᵧ = |a|σₓ", "Var(Y) = a²Var(X)"], "{0}; {1}; {2}",
         (["输入取 X~N(0,1)，令 Y=2X+1。加 1 让中心从 0 移到 1。", "每个离中心的距离都被乘 2，所以标准差从 1 变成 2。", "方差是标准差的平方，因此从 1 变成 4。实线输出比虚线输入宽，密度峰更低。"],
          ["Let X~N(0,1) and Y=2X+1. Adding 1 shifts the centre from 0 to 1.", "Every distance from the centre doubles, so standard deviation changes from 1 to 2.", "Variance is squared standard deviation: 1 becomes 4. The solid output is wider and has a lower density peak than the dashed input."]),
         ("虚线输入 N(0,1)，实线输出 N(1,4)。一般线性矩公式不要求输入是高斯。", "Dashed input N(0,1); solid output N(1,4). The affine moment formulas themselves do not require Gaussian input."), ("取值 · 纵轴：概率密度", "Value · vertical axis: probability density")),
    item("4.3", "jensen", ("弯曲的函数，会改变平均的顺序", "A curved function makes the order of averaging matter"),
         ["E[X] = 0", "f(E[X]) = 0", "E[f(X)] = 1"], "{0}; {1} ≠ {2}",
         (["用 X=−1 或 +1、各占一半的离散例子；平均输入是 0。", "先平均再平方，得到 f(0)=0，图中是底部的菱形。", "先平方，两种输入都变成 1；再平均仍是 1。圆点对应曲线上的实际输出，不能用平均输入代替。"],
          ["Take the discrete example X=−1 or +1 with equal probabilities. Its mean is zero.", "Average first, then square: f(0)=0, shown by the bottom diamond.", "Square first: both outputs are 1, so their average is 1. The circles are actual outputs on the curve; evaluating the mean input is different."]),
         ("本图使用两点分布演示 x²；正文的标准正态例子也给出 0 与 1 的差别。", "This two-point example illustrates x². The text's standard-normal example also gives 0 versus 1."), ("输入 x · 纵轴：f(x)=x²", "Input x · vertical axis: f(x)=x²")),
    item("4.5", "tangent", ("一阶近似：在附近，用切线代替曲线", "A first-order approximation follows a local tangent"),
         ["f(μ)", "f′(μ)", "X−μ"], "f(X) ≈ {0} + {1} × {2}",
         (["取 f(x)=x²，展开点 μ=1。先站在点 (1,1) 上。", "这一点的斜率是 f′(1)=2，虚线切线为 y=1+2(x−1)。", "往右走 0.3，切线给出 1.6，真实曲线是 1.69。距离近时可能好用，不能把局部直线当成处处准确。"],
          ["Use f(x)=x² and expand at μ=1, starting at (1,1).", "The slope is f′(1)=2, giving the dashed tangent y=1+2(x−1).", "Move 0.3 to the right: the tangent gives 1.6, while the curve gives 1.69. A local approximation need not remain accurate far away."]),
         ("实线是真实曲线，虚线是切线；在 μ=0 处，一阶方法还会遗漏 x² 的全部方差。", "Solid: true curve. Dashed: tangent. At μ=0, first-order propagation would miss all variance of x²."), ("输入 x · 纵轴：输出 y", "Input x · vertical axis: output y")),
    item("5.3", "bayes", ("贝叶斯公式：先相乘，再归一化", "Bayes' rule: multiply, then normalize"),
         ["p(θ)", "p(d|θ)", "p(θ|d)"], "{2} = {1} × {0} / p(d)",
         (["点线先验为 θ~N(0,1)，表达看到这次数据以前的认识。", "观察 d=1，噪声标准差 0.5。虚线似然比较每个 θ 对这个读数的解释程度。", "把先验和似然逐点相乘，再除以共同常数 p(d)，得到实线后验 N(0.8,0.2)。总面积重新变成 1。"],
          ["Dotted prior θ~N(0,1) describes knowledge before this observation.", "Observe d=1 with noise standard deviation 0.5. The dashed likelihood measures how each θ explains this reading.", "Multiply point by point and divide by the common evidence p(d). The solid posterior is N(0.8,0.2), normalized to area 1."]),
         ("点线：先验；虚线：似然；实线：后验。似然作为 θ 的函数使用，通常不是 θ 的概率密度。", "Dotted prior; dashed likelihood; solid posterior. A likelihood is a function of θ and is not generally a density over θ."), ("参数 θ · 纵轴：密度 / 似然", "Parameter θ · vertical axis: density / likelihood")),
    item("5.5", "precision", ("先加精度，再按精度分配权重", "Add precisions, then use them as weights"),
         ["1", "4", "0.2"], "Cpost = 1/({0}+{1}) = {2}",
         (["先验方差为 1，所以精度是 1；先验均值为 0。", "观测噪声方差为 0.25，所以精度是 4。更小的方差带来更大的权重。", "总精度为 5，后验方差是 1/5=0.2。均值按 1:4 加权：(1×0+4×1)/5=0.8。"],
          ["Prior variance is 1, so prior precision is 1; the prior mean is 0.", "Observation-noise variance is 0.25, so observation precision is 4. Smaller variance gives greater weight.", "Total precision is 5; posterior variance is 1/5=0.2. The weighted mean is (1×0+4×1)/5=0.8."]),
         ("条形长度表示精度；数轴上的圆点表示按精度加权后的均值。", "Bar lengths show precision; the point on the number line is the precision-weighted mean."), ("上图：信息精度 · 下图：参数值", "Top: information precision · bottom: parameter value")),
    item("5.6", "map", ("MAP：拟合数据与偏离先验的代价相加", "MAP adds data misfit and the prior penalty"),
         ["(1−θ)²/(2×0.25)", "θ²/2", "Φ(θ)"], "{2} = {0} + {1}",
         (["虚线数据项在 θ=1 时最小：只看读数，最愿意选 1。", "点线先验项在 θ=0 时最小：偏离原先中心越远，代价越大。", "实线把两项相加，在 θ=0.8 达到最小。这个最优点是后验的一个摘要，不能代替整条后验曲线。"],
          ["The dashed data term is minimized at θ=1, the observation.", "The dotted prior term is minimized at θ=0; moving away costs more.", "The solid sum is minimized at θ=0.8. This optimum summarizes the posterior but does not replace the entire distribution."]),
         ("本图沿用上一小节的一维高斯模型，实线最低点为 MAP=0.8。", "The same scalar Gaussian example gives the solid objective's MAP minimum at 0.8."), ("参数 θ · 纵轴：代价 Φ", "Parameter θ · vertical axis: objective value")),
    item("6.2", "mixture", ("预测积分：把许多条件预测按权重叠起来", "A predictive integral combines weighted conditional predictions"),
         ["p(θ|D)", "p(d*|θ)", "∫ p(d*|θ)p(θ|D)dθ"], "p(d*|D) = {2}; {0} × {1}",
         (["把参数简化为 −1、0、1 三种可能，权重为 1/4、1/2、1/4。", "令读数 d*=2+θ+η，η~N(0,0.16)。三条细线是已经乘上各自权重的条件预测。", "逐点相加得到实线混合分布，均值为 2，方差为 0.5+0.16=0.66。连续参数的积分可理解为更细的加权相加。"],
          ["Simplify the parameter to −1, 0, and 1 with weights 1/4, 1/2, and 1/4.", "Use d*=2+θ+η, with η~N(0,0.16). The thin curves are the weighted conditional predictions.", "Their pointwise sum is the solid mixture, with mean 2 and variance 0.5+0.16=0.66. Continuous integration is the corresponding weighted combination over parameters."]),
         ("这是三点参数分布的离散类比，不是论文的实际后验样本或实验结果。", "A discrete three-parameter analogy, not posterior samples or experimental results from the paper."), ("未来读数 d* · 纵轴：密度", "Future reading d* · vertical axis: density")),
    item("6.3", "totalvariance", ("总方差：相加的是方差，不是标准差", "Add variances, not standard deviations"),
         ["0.2", "0.25", "0.45"], "Var(D*) = {0} + {1} = {2}",
         (["绿色部分是参数未知带来的输出方差 0.2。", "虚框部分是未来独立测量噪声的方差 0.25。它不是又一份参数未知。", "在独立加性噪声模型下相加，得到 0.45；总标准差是 √0.45≈0.671，而不是 √0.2+√0.25。"],
          ["The green part is output variance 0.2 from uncertain parameters.", "The outlined part is variance 0.25 from independent future measurement noise.", "Independent additive noise gives total variance 0.45 and standard deviation √0.45≈0.671, not √0.2+√0.25."]),
         ("沿用正文手算：潜在量的标准差约 0.447，未来读数约 0.671。", "In the text's example, latent-output standard deviation is about 0.447; future-reading standard deviation is about 0.671."), ("横向长度：方差（平方米）", "Horizontal length: variance (m²)")),
    item("7.2", "integral", ("积分：把许多窄条的面积加起来", "Integration adds the areas of many thin strips"),
         ["u(τ)", "dτ", "∫₀ᵗu(τ)dτ"], "s(t) = {2}; u(τ) = 2+τ; {0} × {1}",
         (["曲线高度 u(τ)=2+τ 表示那个时刻的流速。", "把 0 到 0.5 秒分成小段，每个窄条的面积约为高度乘时间宽度。", "把窄条面积相加，得到累计水量；精确积分为 2×0.5+0.5×0.5²=1.125 升。本例线性函数的中点矩形和也恰好精确。"],
          ["The height u(τ)=2+τ is the flow rate at that time.", "Split 0 to 0.5 seconds into small intervals. Each strip contributes approximately height times time width.", "Add the strip areas: the exact integral is 2×0.5+0.5×0.5²=1.125 L. For this linear function, the midpoint rectangle sum is also exact."]),
         ("绿色区域为 0 到 0.5 秒的累计水量；流速值 2.5 升/秒与水量 1.125 升是不同量。", "The green area is water collected by 0.5 s. Flow 2.5 L/s differs from volume 1.125 L."), ("时间 τ（秒） · 纵轴：流速（升/秒）", "Time τ (s) · vertical axis: flow (L/s)")),
    item("7.4", "dotproduct", ("Branch × Trunk：逐项相乘，再加起来", "Branch × Trunk: multiply matching entries, then add"),
         ["b = [2, 0.5]", "t(ξ) = [ξ, ξ²]", "Σₖ bₖtₖ(ξ)"], "G(u)(ξ) = {2}; {0}, {1}",
         (["用两个教学系数 b=[2,0.5] 表示 Branch 的输出。虚线第一项是 2ξ。", "用 t(ξ)=[ξ,ξ²] 表示两项 Trunk 特征。点线第二项是 0.5ξ²。", "逐项相乘再求和得到实线。在 ξ=0.5 处，2×0.5+0.5×0.25=1.125。这里用解析特征演示点积，真实网络的两组特征共同训练。"],
          ["Use the teaching Branch coefficients b=[2,0.5]. The dashed first contribution is 2ξ.", "Use Trunk features t(ξ)=[ξ,ξ²]. The dotted second contribution is 0.5ξ².", "Add the products to obtain the solid output. At ξ=0.5, 2×0.5+0.5×0.25=1.125. These analytic features illustrate the dot product; real Branch and Trunk features are learned jointly."]),
         ("虚线 2ξ，点线 0.5ξ²，实线两者之和；本图不运行训练好的 DeepONet。", "Dashed 2ξ, dotted 0.5ξ², solid their sum. This figure does not run a trained DeepONet."), ("查询位置 ξ · 纵轴：各项贡献 / 输出", "Query ξ · vertical axis: contributions / output")),
    item("7.6", "ensemble", ("一组网络输出，怎样变成均值与带宽", "From an ensemble of outputs to a mean and band"),
         ["s⁽ʲ⁾(x)", "s̄(x)", "s̄(x) ± 2σ̂(x)"], "{0} → {1} → {2}",
         (["用三条教学预测曲线 9x、10x、11x，表示三个成员对同一输入的输出。", "在每个查询点，先把三个输出平均，得到中间的 10x。", "按 J−1 计算样本标准差，得到 σ̂(x)=x（x≥0）。在 x=1 时，均值 10、标准差 1，带为 [8,12]；这本身不保证 95% 覆盖。"],
          ["Three teaching predictions, 9x, 10x, and 11x, represent outputs from three members at the same input.", "Average at each query to obtain the centre curve, 10x.", "Using denominator J−1 gives sample standard deviation σ̂(x)=x for x≥0. At x=1, mean 10 and standard deviation 1 give [8,12]. This alone does not guarantee 95% coverage."]),
         ("三条细线是成员，虚线是均值，阴影为均值 ± 两倍样本标准差。", "Thin lines: members. Dashed: mean. Shading: mean ± twice the sample standard deviation."), ("查询位置 x · 纵轴：预测输出", "Query x · vertical axis: predicted output")),
    item("8.1", "gain", ("卡尔曼增益：把残差打几折", "The Kalman gain weights the residual"),
         ["K=C/(C+R)=0.8", "d−μ=1", "μ⁺=0+0.8×1=0.8"], "{0}; {1}; {2}",
         (["先验方差 C=1，观测噪声方差 R=0.25，所以 K=1/1.25=0.8。曲线显示 R 增大时 K 会减小。", "观测是 1，旧均值是 0，残差为 1。", "只走残差的 80%，新均值就到 0.8；不是直接把旧估计换成观测值。"],
          ["With C=1 and R=0.25, K=1/1.25=0.8. The curve shows K decreasing as observation noise variance R grows.", "Observation 1 minus old mean 0 gives residual 1.", "Move 80% of the residual to reach 0.8. The update does not simply replace the old estimate with the observation."]),
         ("上图：增益随噪声方差变化；下图：本例的均值更新。", "Top: gain versus noise variance. Bottom: the example's mean update."), ("上图横轴 R、纵轴 K · 下图：位置", "Top: R versus K · bottom: position")),
    item("8.4", "crosscov", ("集合协方差：从成员共同变化中找方向", "Ensemble covariance learns a direction from joint variation"),
         ["z−z̄", "h−h̄", "Czh = Σ(z−z̄)(h−h̄)/(J−1)"], "{2}; {0} × {1}",
         (["参数成员 z=[0,1,2]，均值为 1，偏移是 −1、0、1。", "模型 h(z)=2z 给出 [0,2,4]，均值为 2，偏移是 −2、0、2。", "乘积相加后除以 J−1=2，得 Czh=2；同样算得 Chh=4。若 R=1，则 K=2/(4+1)=0.4。"],
          ["Members z=[0,1,2] have mean 1 and deviations −1, 0, 1.", "Model h(z)=2z gives [0,2,4], mean 2, and deviations −2, 0, 2.", "Sum the products and divide by J−1=2: Czh=2. Similarly Chh=4. With R=1, the gain is 2/(4+1)=0.4."]),
         ("散点在右上方向排列，所以这里的交叉协方差为正，残差为正时参数向更大方向修正。", "The upward scatter gives positive cross-covariance, so a positive residual pushes parameters upward."), ("参数 z · 纵轴：模型预测 h(z)", "Parameter z · vertical axis: model prediction h(z)")),
    item("9.3", "ekiupdate", ("把 EKI 更新拆成一条可跟随的算式", "Follow one member through the EKI update"),
         ["θ̂ = 1", "d−h(θ̂)+η = 1.5", "θ⁺ = 1+0.4×1.5 = 1.6"], "{0}; {1}; {2}",
         (["沿用 h(θ)=2θ、K=0.4，选一个预测步后的成员 θ̂=1，所以模型预测是 2。", "观测 d=3，取一次人工观测扰动 η=0.5，带扰动的残差为 3−2+0.5=1.5。", "乘上增益得到参数修正 0.6，更新到 θ⁺=1.6；它的新预测是 3.2。一次扰动不要求单个成员刚好命中观测。"],
          ["Use h(θ)=2θ and K=0.4. Choose a predicted member θ̂=1, whose model output is 2.", "Observation d=3 and one artificial observation perturbation η=0.5 give residual 3−2+0.5=1.5.", "The correction is 0.4×1.5=0.6, so θ⁺=1.6 and its new prediction is 3.2. A perturbed update need not make an individual member hit the observation exactly."]),
         ("一维手算，只展示已给定增益后的一次成员更新；Q 的参数扰动发生在这条式子之前。", "Scalar arithmetic for one member with a given gain; the Q parameter perturbation occurs before this update."), ("上图：参数 θ · 下图：模型输出 2θ", "Top: parameter θ · bottom: model output 2θ")),
    item("9.7", "adaptive", ("自适应 Q：先比较尺度，再调整探索", "Adaptive Q compares scales before changing exploration"),
         ["κ‖s‖", "‖d−μ‖", "f̄"], "f = ({0}−{1})/‖d‖; {2} → ωnext",
         (["看第一个窗口：设 ‖d‖=10、κ=2，预测标准差向量范数为 0.5，则带的尺度为 1。", "残差范数为 2，所以该窗口的指标均值取 −0.1，低于 −τ=−0.05；探索标准差从 0.1 增到 0.101。", "另外两个教学窗口均值为 0.02、0.1，分别保持 0.1、降到 0.099。三个窗口都从同一个 ω=0.1 比较；协方差尺度是 ω²，而不是 ω。"],
          ["In the first window, take ‖d‖=10 and κ=2. A spread norm of 0.5 gives a band scale of 1.", "Residual norm 2 gives window mean −0.1, below −τ=−0.05. Exploration standard deviation rises from 0.1 to 0.101.", "Two further teaching window means, 0.02 and 0.1, keep 0.1 or reduce it to 0.099. Each case starts at ω=0.1 for comparison; covariance scales as ω², not ω."]),
         ("示意窗口均值 −0.1、0.02、0.1；τ=0.05、α=0.01。这是启发式调节，不是后验正确性的证明。", "Illustrative window means −0.1, 0.02, 0.1; τ=0.05, α=0.01. This heuristic does not prove posterior correctness."), ("教学窗口编号 · 纵轴：指标窗口均值 f̄", "Illustrative window · vertical axis: window mean f̄")),
    item("10.3", "metrics", ("同一组预测，三把不同的尺子", "Three different measurements of the same predictions"),
         ["e ≈ 0.1558", "q ≈ 0.0707", "c = 3/4 = 75%"], "{0}; {1}; {2}",
         (["绿色圆点为均值预测，橙色菱形为真值。平方误差之和为 0.34，真值平方和为 14，所以相对误差为 √0.34/√14。", "竖线表示均值 ±2σ。标准差平方和是 0.07，所以 q=√0.07/√14；它不等于 e。", "前三个真值被区间包含，第四个漏掉，故 c=75%。第二点恰在边界，也算覆盖。"],
          ["Green circles are predicted means; orange diamonds are truth. Squared errors sum to 0.34 and squared truths to 14, giving e=√0.34/√14.", "Vertical bars show mean ±2σ. Squared standard deviations sum to 0.07, so q=√0.07/√14, a different quantity from e.", "The first three truths are covered; the fourth is missed, giving c=75%. The second point is on the boundary and counts as covered."]),
         ("完全沿用本小节的四点数据；圆点是预测均值，菱形是真值，竖线是两倍标准差区间。", "Uses the text's four-point data exactly: circles are means, diamonds are truth, and bars are two-standard-deviation intervals."), ("查询点编号 · 纵轴：输出值", "Query index · vertical axis: output value")),
    item("10.5", "joint", ("每个点大多盖住，不等于整条都盖住", "Pointwise coverage differs from whole-curve coverage"),
         ["P(Aₖ)", "P(∩ₖ Aₖ)", "0.95⁴ ≈ 81.45%"], "{1} ≤ {0}; {2}",
         (["图中六行是六条曲线，四列是四个时刻。每列有 5/6 被盖住，点态覆盖率约 83.3%。", "前四行各漏掉一个点，只有后两行全部被盖住，所以整条曲线覆盖率只有 2/6≈33.3%。", "另外，若四个覆盖事件独立、每个概率都是 95%，整条同时覆盖概率才可算为 0.95⁴≈81.45%。实际曲线通常相关，不能直接套独立公式。"],
          ["Six rows represent six curves and four columns four times. Each column covers 5/6 of its cases, about 83.3%.", "Each of the first four rows misses one point. Only two complete rows are covered, so whole-curve coverage is 2/6≈33.3%.", "Separately, four independent coverage events, each of probability 95%, would give 0.95⁴≈81.45% jointly. Real curves are usually correlated, so independence cannot simply be assumed."]),
         ("网格是六条曲线的教学例子；公式中的 95% 独立事件是另一个假设例子。", "The grid is a six-curve teaching example; the 95% independent-event calculation is a separate hypothetical example."), ("列：时刻 · 行：不同曲线（× 表示漏掉）", "Columns: times · rows: curves (× means missed)")),
    item("10.6", "calibration", ("校准曲线：说到的概率，做到了吗", "Calibration: do the stated probabilities match outcomes?"),
         ["p = 95%", "ĉ(p) = 78%", "ĉ(p)−p = −17 pp"], "{0} → {1}; {2}",
         (["横轴是事先声明的覆盖水平，例如 95%。它是承诺的概率，不是看到测试答案后再挑的数字。", "纵轴是在独立测试数据上实际测到的覆盖率。教学曲线在 95% 处只有 78%。", "参考对角线表示声明与实际相同。本例低了 17 个百分点，提示过度自信；还要结合有限样本误差、区间宽度和分组表现。"],
          ["The horizontal axis is a stated nominal level, such as 95%, chosen before inspecting test outcomes.", "The vertical axis is coverage on independent test data. The illustrative curve achieves only 78% at nominal 95%.", "The diagonal represents matching nominal and observed levels. A gap of 17 percentage points suggests overconfidence; also consider sampling error, widths, and subgroup performance."]),
         ("虚线是理想参考，实线为人为构造的教学曲线，不是论文实测数据。pp 指百分点。", "Dashed: ideal reference. Solid: a constructed teaching curve, not paper results. pp means percentage points."), ("声明的覆盖水平（%） · 纵轴：实际覆盖率（%）", "Nominal level (%) · vertical axis: empirical coverage (%)")),
]


def node(tag, content="", **attrs):
    attributes = " ".join(f'{key.replace("_", "-")}="{escape(str(value), quote=True)}"' for key, value in attrs.items())
    return f"<{tag} {attributes}>{content}</{tag}>"


def line(x1, y1, x2, y2, cls="ff-axis"):
    return node("line", x1=x1, y1=y1, x2=x2, y2=y2, **{"class": cls})


def text(x, y, value, anchor="middle", cls=""):
    return node("text", escape(str(value)), x=x, y=y, text_anchor=anchor, **{"class": cls})


def point(x, y, cls="", shape="circle"):
    if shape == "diamond":
        return node("path", d=f"M{x} {y-6}l6 6-6 6-6-6Z", **{"class": f"ff-dot {cls}"})
    if shape == "cross":
        return node("path", d=f"M{x-5} {y-5}l10 10m0-10-10 10", **{"class": f"ff-cross {cls}"})
    return node("circle", cx=x, cy=y, r=5, **{"class": f"ff-dot {cls}"})


def rect(x, y, width, height, cls="ff-area"):
    return node("rect", x=x, y=y, width=width, height=height, **{"class": cls})


def group(step, content):
    return node("g", content, data_ff_layer=step)


class Plot:
    def __init__(self, xmin, xmax, ymin, ymax, box=(64, 24, 500, 186)):
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.left, self.top, self.width, self.height = box

    def xy(self, x, y):
        return (round(self.left + (x-self.xmin)/(self.xmax-self.xmin)*self.width, 2),
                round(self.top + (self.ymax-y)/(self.ymax-self.ymin)*self.height, 2))

    def segment(self, x1, y1, x2, y2, cls="ff-axis"):
        return line(*self.xy(x1, y1), *self.xy(x2, y2), cls)

    def dot(self, x, y, cls="", shape="circle"):
        return point(*self.xy(x, y), cls, shape)

    def label(self, x, y, value, anchor="middle", dy=-12):
        px, py = self.xy(x, y)
        return text(px, py+dy, value, anchor)

    def curve(self, function, cls="", lo=None, hi=None):
        low = self.xmin if lo is None else lo
        high = self.xmax if hi is None else hi
        points = [self.xy(low+(high-low)*i/100, function(low+(high-low)*i/100)) for i in range(101)]
        d = "M" + " L".join(f"{x} {y}" for x, y in points)
        return node("path", d=d, pathLength=1, **{"class": f"ff-curve {cls}"})

    def area(self, upper, lower=lambda x: 0, lo=None, hi=None):
        low = self.xmin if lo is None else lo
        high = self.xmax if hi is None else hi
        xs = [low+(high-low)*i/80 for i in range(81)]
        pts = [self.xy(x, upper(x)) for x in xs] + [self.xy(x, lower(x)) for x in reversed(xs)]
        return node("path", d="M"+" L".join(f"{x} {y}" for x, y in pts)+"Z", **{"class": "ff-area"})

    def axes(self, xticks, yticks, zero=False):
        xaxis = 0 if zero and self.ymin <= 0 <= self.ymax else self.ymin
        yaxis = 0 if zero and self.xmin <= 0 <= self.xmax else self.xmin
        result = self.segment(self.xmin, xaxis, self.xmax, xaxis) + self.segment(yaxis, self.ymin, yaxis, self.ymax)
        for x in xticks:
            px, py = self.xy(x, self.ymin)
            result += line(px, py, px, py+5) + text(px, py+25, f"{x:g}")
        for y in yticks:
            px, py = self.xy(self.xmin, y)
            label = "1/3" if abs(y-1/3) < 1e-10 else f"{y:g}"
            result += line(px-5, py, px, py) + text(px-12, py+4, label, "end")
        return result


def normal(x, mu=0, variance=1):
    return exp(-(x-mu)**2/(2*variance))/sqrt(2*pi*variance)


def scene(kind):
    """Three semantic layers, shared by the bilingual HTML renderings."""
    p = Plot(0, 1, 0, 1)
    if kind == "distance":
        p = Plot(0, 4, 0, 3)
        return (p.axes([0, 1, 2, 3, 4], [1, 2, 3]) +
                group(0, p.segment(0, 2, 4, 2, "ff-curve")+p.label(3.6, 2, "2")) +
                group(1, p.segment(3, 0, 3, 2, "ff-dashed ff-alt")+p.dot(3, 0)) +
                group(2, p.area(lambda x: 2, hi=3)+p.label(1.5, 1, "2 × 3 = 6", dy=0)))
    if kind == "error":
        p = Plot(8, 14, 0, 1)
        return (p.segment(8, .35, 14, .35) +
                "".join(p.label(x, .35, x, dy=30) for x in [8, 10, 12, 14]) +
                group(0, p.dot(10, .35)+p.label(10, .35, "ŝ=10", dy=-35)) +
                group(1, p.dot(12, .35, "ff-alt", "diamond")+p.label(12, .35, "s=12", dy=-35)) +
                group(2, p.segment(10, .68, 12, .68, "ff-curve")+p.label(11, .68, "|12−10|=2")))
    if kind in {"expectation", "variance"}:
        p = Plot(8, 12, 0, .5)
        base = p.axes([9, 10, 11], [0, 1/3] if kind == "expectation" else [])
        if kind == "expectation":
            bars = "".join(rect(p.xy(x, 1/3)[0]-18, p.xy(x, 1/3)[1], 36, p.height*2/3) for x in [9, 10, 11])
            return (base+group(0, "".join(p.dot(x, 0) for x in [9, 10, 11])) +
                    group(1, bars+text(564, 38, "p=1/3", "end")) +
                    group(2, p.segment(10, 0, 10, .44, "ff-dashed ff-alt")+p.label(10, .46, "μ=10", dy=-2)))
        base += "".join(p.segment(x, 0, 10, 0, "ff-dashed") for x in [9, 11])
        return (base+group(0, "".join(p.label(x, .05, label, dy=-5) for x, label in [(9, "−1"), (10, "0"), (11, "+1")]))+
                group(1, rect(147, 60, 70, 70)+rect(397, 60, 70, 70)+text(182, 104, "1²")+text(307, 104, "0²")+text(432, 104, "1²"))+
                group(2, text(310, 32, "(1+0+1)/3 = 2/3")))
    if kind in {"gaussian", "linear", "bayes"}:
        p = Plot(-4, 6, 0, 1.05 if kind == "bayes" else .46)
        result = p.axes([-4, -2, 0, 2, 4, 6], [0, .2, .4] if kind != "bayes" else [0, .5, 1])
        if kind == "gaussian":
            values = [(0, 1, "ff-muted ff-dotted"), (1, 1, "ff-alt ff-dashed"), (1, 4, "")]
        elif kind == "linear":
            values = [(0, 1, "ff-muted ff-dashed"), (1, 4, "ff-alt ff-dotted"), (1, 4, "")]
        else:
            p = Plot(-3, 3, 0, 1.05)
            result = p.axes([-3, -1, 1, 3], [0, .5, 1])
            values = [(0, 1, "ff-muted ff-dotted"), (1, .25, "ff-alt ff-dashed"), (.8, .2, "")]
        for step, (mu, var, cls) in enumerate(values):
            s = p.curve(lambda x: normal(x, mu, var), cls)
            if kind == "linear" and step == 1:
                s = p.segment(-1, .1, 3, .1, "ff-alt ff-dashed") + p.label(1, .1, "σ=2")
            result += group(step, s)
        return result
    if kind == "covariance":
        p = Plot(-3, 3, -2, 2)
        base = p.axes([-2, 0, 2], [-1, 1], True)
        rows = [(2, 1), (-2, 1), (2, -1), (-2, -1)]
        return (base+group(0, "".join(p.segment(0, 0, x, 0, "ff-dashed") for x in [-2, 2]))+
                group(1, "".join(p.segment(x, 0, x, y, "ff-alt ff-dashed") for x, y in rows))+
                group(2, "".join(p.dot(x, y, "" if x*y>0 else "ff-alt", "circle" if x*y>0 else "cross")+
                                p.label(x, y, "+2" if x*y>0 else "−2") for x, y in rows)))
    if kind == "matrix":
        # Equal scales keep the identity contour circular.
        p = Plot(-1.6, 1.6, -1.6, 1.6, (200, 22, 188, 188))
        base = p.axes([-1, 1], [-1, 1], True)
        pts = [p.xy((sqrt(1.8)*cos(i*pi/50)+sqrt(.2)*sin(i*pi/50))/sqrt(2),
                    (sqrt(1.8)*cos(i*pi/50)-sqrt(.2)*sin(i*pi/50))/sqrt(2)) for i in range(101)]
        ellipse = node("path", d="M"+" L".join(f"{x} {y}" for x, y in pts)+"Z", pathLength=1, **{"class": "ff-curve"})
        return (base+group(0, p.segment(-1, 0, 1, 0, "ff-curve"))+
                group(1, node("circle", cx=294, cy=116, r=58.75, **{"class": "ff-curve ff-muted ff-dashed"}))+
                group(2, ellipse+text(450, 65, "Σ₁₂=0.8")))
    if kind == "kernel":
        p = Plot(0, 1, 0, 1.1)
        return (p.axes([0, .4, .8], [0, .5, 1])+group(0, p.dot(0, 1)+p.label(.08, 1, "a²=1", "start"))+
                group(1, p.curve(lambda x: exp(-x*x/(2*.2**2)), "ff-alt ff-dashed")+p.dot(.4, exp(-2), "ff-alt")+p.label(.46, .16, "0.135", "start", dy=0))+
                group(2, p.curve(lambda x: exp(-x*x/(2*.5**2)))+p.dot(.4, exp(-.32))+p.label(.4, exp(-.32), "0.726")))
    if kind in {"jensen", "tangent"}:
        p = Plot(-1.5, 1.5, 0, 2.3) if kind == "jensen" else Plot(.2, 1.8, 0, 3.3)
        base = p.axes([-1, 0, 1] if kind == "jensen" else [.5, 1, 1.5], [0, 1, 2, 3] if kind == "tangent" else [0, 1, 2])
        if kind == "jensen":
            return (base+p.curve(lambda x: x*x)+group(0, p.dot(-1, 0)+p.dot(1, 0))+
                    group(1, p.dot(0, 0, "ff-alt", "diamond")+p.label(.05, .13, "f(0)=0", "start"))+
                    group(2, p.dot(-1, 1)+p.dot(1, 1)+p.segment(-1, 1, 1, 1, "ff-dashed")+p.dot(0, 1)+p.label(0, 1, "E[X²]=1")))
        return (base+p.curve(lambda x: x*x)+group(0, p.dot(1, 1)+p.label(1, 1, "(1,1)"))+
                group(1, p.curve(lambda x: 2*x-1, "ff-alt ff-dashed", lo=.5)+p.label(.75, .5, "f′(1)=2"))+
                group(2, p.dot(1.3, 1.6, "ff-alt", "diamond")+p.dot(1.3, 1.69)+p.label(1.32, 1.8, "1.69", "start")+p.label(1.3, 1.5, "1.6", dy=26)))
    if kind == "precision":
        p = Plot(0, 1, 0, 1, (80, 160, 440, 24))
        return (p.segment(0, .5, 1, .5)+p.label(0, .5, "0", dy=28)+p.label(1, .5, "1", dy=28)+
                group(0, rect(80, 40, 88, 42)+text(124, 68, "1"))+
                group(1, rect(168, 40, 352, 42, "ff-area ff-alt-fill")+text(344, 68, "4"))+
                group(2, text(300, 118, "1+4=5; Cpost=0.2")+p.dot(.8, .5)+p.label(.8, .5, "0.8")))
    if kind == "map":
        p = Plot(-.5, 2, 0, 5)
        return (p.axes([0, .8, 1.5, 2], [0, 2, 4])+
                group(0, p.curve(lambda x: 2*(1-x)**2, "ff-alt ff-dashed"))+
                group(1, p.curve(lambda x: .5*x*x, "ff-muted ff-dotted"))+
                group(2, p.curve(lambda x: 2*(1-x)**2+.5*x*x, hi=1.9)+p.dot(.8, .4)+p.label(.8, .4, "θMAP=0.8", dy=-24)))
    if kind == "mixture":
        p = Plot(-.2, 4.2, 0, .65)
        component = lambda x, m, w: w*normal(x, m, .16)
        return (p.axes([0, 1, 2, 3, 4], [0, .3, .6])+
                group(0, "".join(p.dot(m, 0)+p.label(m, 0, str(w), dy=-28) for m, w in [(1, .25), (2, .5), (3, .25)]))+
                group(1, "".join(p.curve(lambda x, m=m, w=w: component(x, m, w), "ff-alt ff-dashed") for m, w in [(1, .25), (2, .5), (3, .25)]))+
                group(2, p.curve(lambda x: sum(component(x, m, w) for m, w in [(1, .25), (2, .5), (3, .25)]))))
    if kind == "totalvariance":
        return (line(80, 192, 530, 192)+text(80, 222, "0")+text(530, 222, "0.45")+
                group(0, rect(80, 70, 200, 55)+text(180, 105, "0.2"))+
                group(1, rect(280, 70, 250, 55, "ff-area ff-outline")+text(405, 105, "0.25"))+
                group(2, line(80, 145, 530, 145, "ff-curve")+text(300, 176, "σ = √0.45 ≈ 0.671")))
    if kind == "integral":
        p = Plot(0, 1, 0, 3.2)
        strips = ""
        for i in range(8):
            x, y = p.xy(i/16, 2+(i+.5)/16)
            strips += rect(x, y, p.width/16, p.xy(0, 0)[1]-y, "ff-area ff-outline")
        return (p.axes([0, .5, 1], [0, 1, 2, 3])+group(0, p.curve(lambda x: 2+x))+
                group(1, strips)+group(2, p.area(lambda x: 2+x, hi=.5)+p.label(.25, 1, "1.125 L", dy=0)+p.segment(.5, 0, .5, 2.5, "ff-dashed")))
    if kind == "dotproduct":
        p = Plot(0, 1, 0, 2.7)
        return (p.axes([0, .5, 1], [0, 1, 2])+
                group(0, p.curve(lambda x: 2*x, "ff-alt ff-dashed"))+
                group(1, p.curve(lambda x: .5*x*x, "ff-muted ff-dotted"))+
                group(2, p.curve(lambda x: 2*x+.5*x*x)+p.dot(.5, 1.125)+p.label(.5, 1.125, "1.125", dy=-22)))
    if kind == "ensemble":
        p = Plot(0, 1, 0, 13)
        return (p.axes([0, .5, 1], [0, 5, 10])+
                group(0, "".join(p.curve(lambda x, k=k: k*x, "ff-muted ff-thin") for k in [9, 10, 11]))+
                group(1, p.curve(lambda x: 10*x, "ff-dashed"))+
                group(2, p.area(lambda x: 12*x, lambda x: 8*x)+p.segment(1, 8, 1, 12, "ff-curve")+p.label(.75, 12*.75, "±2σ̂")))
    if kind == "gain":
        p = Plot(0, 3, 0, 1.1, (80, 20, 460, 105))
        q = Plot(0, 1, 0, 1, (80, 190, 460, 10))
        return (p.axes([0, 1, 2, 3], [0, 1])+q.segment(0, .5, 1, .5)+
                group(0, p.curve(lambda r: 1/(1+r))+p.dot(.25, .8)+p.label(.32, .8, "K=0.8", "start"))+
                group(1, q.dot(0, .5, "ff-muted")+q.label(0, .5, "0", dy=30)+q.dot(1, .5, "ff-alt", "diamond")+q.label(1, .5, "d=1", dy=30))+
                group(2, q.segment(0, .5, .8, .5, "ff-curve")+q.dot(.8, .5)+q.label(.8, .5, "μ⁺=0.8", dy=-14)))
    if kind == "crosscov":
        p = Plot(-.2, 2.2, -.3, 4.8)
        return (p.axes([0, 1, 2], [0, 2, 4])+p.curve(lambda x: 2*x, "ff-muted ff-dotted", lo=0, hi=2)+
                group(0, p.segment(1, 0, 0, 0, "ff-alt ff-dashed")+p.segment(1, 0, 2, 0, "ff-alt ff-dashed"))+
                group(1, p.segment(0, 0, 0, 2, "ff-alt ff-dashed")+p.segment(2, 2, 2, 4, "ff-alt ff-dashed"))+
                group(2, "".join(p.dot(z, 2*z) for z in [0, 1, 2])+text(95, 40, "Czh=2; K=0.4", "start")))
    if kind == "ekiupdate":
        p = Plot(.6, 2, 0, 1, (80, 25, 450, 50))
        q = Plot(1.2, 4, 0, 1, (80, 145, 450, 50))
        return (p.segment(.6, .5, 2, .5)+q.segment(1.2, .5, 4, .5)+
                group(0, p.dot(1, .5)+p.label(1, .5, "θ̂=1")+q.dot(2, .5)+q.label(2, .5, "h=2", dy=30))+
                group(1, q.dot(3, .5, "ff-alt", "diamond")+q.label(3, .5, "d=3", dy=30)+q.dot(3.5, .5, "ff-muted", "cross")+q.label(3.5, .5, "d+η=3.5"))+
                group(2, p.segment(1, .5, 1.6, .5, "ff-curve")+p.dot(1.6, .5)+p.label(1.6, .5, "θ⁺=1.6")+q.dot(3.2, .5)+q.label(3.2, .5, "3.2", dy=64)))
    if kind == "adaptive":
        p = Plot(.5, 3.5, -.15, .15)
        base = p.axes([1, 2, 3], [-.1, 0, .1])
        base += p.segment(.5, .05, 3.5, .05, "ff-muted ff-dashed")+p.segment(.5, -.05, 3.5, -.05, "ff-muted ff-dashed")
        return (base+group(0, p.dot(1, -.1, "ff-alt")+p.label(1, -.1, "−0.1", dy=27))+
                group(1, p.label(1, -.1, "ω→0.101", dy=-26))+
                group(2, p.dot(2, .02)+p.label(2, .02, "0.1", dy=-22)+p.dot(3, .1)+p.label(3, .1, "0.099", dy=-15)))
    if kind == "metrics":
        p = Plot(.5, 4.5, -.3, 3.5)
        means, truth, std = [.1, .8, 2.2, 2.5], [0, 1, 2, 3], [.1, .1, .2, .1]
        base = p.axes([1, 2, 3, 4], [0, 1, 2, 3])
        pairs = "".join(p.dot(i+1, m)+p.dot(i+1, t, "ff-alt", "diamond") for i, (m, t) in enumerate(zip(means, truth)))
        bars = ""
        for i, (m, s) in enumerate(zip(means, std)):
            bars += p.segment(i+1, m-2*s, i+1, m+2*s, "ff-curve")
            bars += p.segment(i+.9, m-2*s, i+1.1, m-2*s, "ff-curve")+p.segment(i+.9, m+2*s, i+1.1, m+2*s, "ff-curve")
        return (base+group(0, pairs)+group(1, bars)+group(2, p.label(2, 2.8, "3/4 = 75%")+p.dot(4, 3, "ff-alt", "cross")))
    if kind == "joint":
        cells = ""
        for row in range(6):
            for col in range(4):
                x, y = 150+85*col, 25+30*row
                missed = row == col
                cells += rect(x, y, 63, 23, "ff-cell ff-missed" if missed else "ff-cell")
                if missed:
                    cells += point(x+31, y+11, "ff-alt", "cross")
        return (group(0, cells+"".join(text(182+i*85, 230, i+1) for i in range(4)))+
                group(1, rect(138, 141, 342, 68, "ff-area ff-outline")+text(510, 183, "2/6"))+
                group(2, text(300, 269, "0.95⁴ ≈ 81.45%")))
    if kind == "calibration":
        p = Plot(0, 100, 0, 100)
        return (p.axes([0, 50, 95], [0, 50, 100])+
                group(0, p.segment(95, 0, 95, 78, "ff-muted ff-dotted"))+
                group(1, p.curve(lambda x: 78*(x/95)**1.18, hi=100)+p.dot(95, 78)+p.label(90, 72, "(95,78)", "end", dy=20))+
                group(2, p.curve(lambda x: x, "ff-alt ff-dashed")+p.segment(95, 78, 95, 95, "ff-alt ff-dashed")+p.label(75, 95, "−17 pp")))
    raise ValueError(f"Unknown formula scene: {kind}")


def render_figure(figure, lang):
    index = 0 if lang == "zh" else 1
    title, caption, axes = (figure[key][index] for key in ["title", "caption", "axes"])
    anchor = "formula-" + "-".join(f"{int(n):02d}" for n in figure["section"].split("."))
    terms = [f'<span data-ff-term="{i}">{escape(term)}</span>' for i, term in enumerate(figure["terms"])]
    formula = figure["expression"].format(*terms)
    steps = "".join(f'<li data-ff-step="{i}"><span class="ff-step-number">{i+1}</span><span>{escape(step)}</span></li>' for i, step in enumerate(figure["steps"][index]))
    zh = lang == "zh"
    return f'''<figure class="formula-figure" id="{anchor}" data-formula="{figure['kind']}" aria-labelledby="{anchor}-title">
<figcaption><a class="ff-eyebrow" href="#{anchor}">{"公式图解" if zh else "FORMULA IN PICTURES"} · {figure['section']}</a><h4 id="{anchor}-title">{escape(title)}</h4></figcaption>
<div class="ff-equation" aria-label="{"公式" if zh else "Formula"}">{formula}</div>
<svg class="ff-scene" viewBox="0 0 600 280" role="img" aria-labelledby="{anchor}-svg-title {anchor}-svg-desc"><title id="{anchor}-svg-title">{escape(title)}</title><desc id="{anchor}-svg-desc">{escape(caption)} {escape(axes)}</desc>{scene(figure['kind'])}</svg>
<p class="ff-axes">{escape(axes)}</p>
<p class="ff-caption">{escape(caption)}</p>
<div class="ff-controls" hidden><button type="button" data-ff-play aria-pressed="false">{"播放三步" if zh else "Play 3 steps"}</button><button type="button" data-ff-next>{"下一步" if zh else "Next step"}</button><button type="button" data-ff-reset>{"查看全图" if zh else "Show all"}</button><span data-ff-status role="status" aria-live="polite">{"全图 · 可分三步阅读" if zh else "Full view · explore in 3 steps"}</span></div>
<ol class="ff-explanation">{steps}</ol>
</figure>'''


def enrich_formulas(body, lang):
    figures = {entry["section"]: entry for entry in FIGURES}
    inserted = set()

    def add(match):
        section = match[1]
        if section not in figures:
            return match[0]
        if section in inserted:
            raise ValueError(f"Duplicate formula target {lang} {section}")
        inserted.add(section)
        return match[0].rstrip()+"\n"+render_figure(figures[section], lang)+"\n"

    body = re.sub(r'<h3\b[^>]*>\s*(\d+\.\d+)\b.*?</h3>.*?(?=<h[23]\b|\Z)', add, body, flags=re.S)
    if inserted != figures.keys():
        raise ValueError(f"Missing formula targets in {lang}: {figures.keys()-inserted}")
    guide = ('<p>正文另有 26 处“公式图解”，可查看完整曲线，或播放、暂停、单步阅读公式与图形的对应过程。试试：<a href="#formula-02-03">方差</a> · <a href="#formula-07-04">Branch × Trunk</a> · <a href="#formula-09-03">EKI 更新</a>。</p>'
             if lang == "zh" else
             '<p>There are also 26 formula diagrams throughout the text. View the complete curves, or play, pause, and step through the links between symbols and pictures. Try <a href="#formula-02-03">variance</a>, <a href="#formula-07-04">Branch × Trunk</a>, or <a href="#formula-09-03">an EKI update</a>.</p>')
    body = body.replace('</aside>', guide+'\n</aside>', 1)
    return body
