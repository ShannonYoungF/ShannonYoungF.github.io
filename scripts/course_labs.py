"""Small, bilingual experiments inserted into the ten-lecture DeepONet course."""

from html import escape
import re


# Copy lives beside the build code so reimporting the original reading edition
# does not remove the interactive teaching layer.
LABS = [
    {
        "kind": "cars",
        "zh": ("三辆小车，跑到哪里？", "同一辆小车可能每秒跑 0.9、1.0 或 1.1 米，三种情况机会相同。让三辆小车分别替它演一遍。", "先猜：跑的时间变成两倍，最前面和最后面的小车会离得更远吗？", "时间相同，速度的不同变成位置的不同。这就是不确定性传播。三辆车是三种可能情况，不是同一辆车同时出现在三个地方。", "S = V × T：位置 = 速度 × 时间。这里还没有给出真值，因此车之间的距离不是预测误差。"),
        "en": ("Where will the three little cars finish?", "One car might travel at 0.9, 1.0, or 1.1 metres per second, with equal chances. Three little cars act out these possibilities.", "Guess first: if they run for twice as long, will the first and last cars be farther apart?", "Different possible speeds become different possible positions. That is uncertainty propagation. These are three possibilities for one car, rather than three simultaneous locations.", "S = V × T: displacement = speed × time. No true position is supplied here, so the gap between cars is not prediction error."),
        "controls": [("time", "range", 2, 20, 1, 10, "跑多久（秒）", "Travel time (s)")],
    },
    {
        "kind": "spread",
        "zh": ("平均都是 5 颗糖，就一样了吗？", "每个圆点是一袋糖。三种糖果数量各占三分之一；把它们拉开，看看平均数是否会动。", "先猜：一袋有 1、5、9 颗，和一袋有 4、5、6 颗，哪组更难猜中？", "平均数告诉你中心在哪，分散程度告诉你可能离中心多远。只报平均数，会漏掉后半个故事。", "三种等可能数量是 5−d、5、5+d。均值为 5，标准差为 d × √(2/3)；这里算的是已知分布的标准差。"),
        "en": ("The average is five sweets. Is that the whole story?", "Each dot is a bag of sweets. Three possible counts have equal chances. Move them apart and watch the average.", "Guess first: is a bag with 1, 5, or 9 sweets harder to predict than one with 4, 5, or 6?", "The average gives the centre; spread tells us how far outcomes can be from it. Reporting only the average leaves out the second part.", "The equally likely counts are 5−d, 5, and 5+d. Mean = 5; standard deviation = d × √(2/3). This is the known distribution's standard deviation."),
        "controls": [("spread", "range", 1, 4, 1, 2, "离平均数多远（颗）", "Distance from the mean (sweets)")],
    },
    {
        "kind": "correlation",
        "zh": ("走两步：一起偏，还是互相抵消？", "每一步都可能向左或向右偏 1 米。每一步单独看完全一样，合起来却可能很不一样。虚线是第一步，实线是第二步。", "先猜：如果第一步向左，第二步总向右，最后还会偏离起点吗？", "除了知道每一步有多不准，还要知道它们怎样一起变化。这种关系会影响最后的总偏差。每一行是一种等可能情况。", "Var(X+Y) = Var(X) + Var(Y) + 2Cov(X,Y)。同向、独立、反向时，两步之和的方差分别为 4、2、0 平方米。"),
        "en": ("Two steps: add up or cancel out?", "Each step can be off by one metre left or right. Separately, the steps look identical. Their combined error depends on how they move together. Dashed: first step; solid: second step.", "Guess first: if a left error is always followed by a right error, will the final position miss the start?", "We need both the size of each error and how the errors vary together. Each row shows one equally likely case.", "Var(X+Y) = Var(X) + Var(Y) + 2Cov(X,Y). Same-direction, independent, and opposite errors give total variances of 4, 2, and 0 square metres."),
        "controls": [("relation", "select", [("same", "一起向同一边偏", "Always the same way"), ("independent", "各走各的，互不影响", "Independent steps"), ("opposite", "总是向相反方向偏", "Always opposite ways")], "两步的关系", "How the steps are related")],
    },
    {
        "kind": "machine",
        "zh": ("数字珠子，穿过一台小机器", "五颗珠子分别写着 −2、−1、0、1、2，机会相同。机器可以把数字翻倍，也可以把数字平方。", "先猜：负数平方会去哪里？先求平均再平方，和先平方再求平均，一样吗？", "机器把输入的每一种可能变成输出的一种可能。平方会把正负数送到同一个非负位置，输出的形状也跟着改变。", "一般 E[f(X)] ≠ f(E[X])。本例输入均值为 0；平方后输出均值为 2，而平均输入的平方为 0。"),
        "en": ("Number beads go through a little machine", "Five equally likely beads carry −2, −1, 0, 1, and 2. The machine can double or square each number.", "Guess first: where do negative numbers go when squared? Is squaring the average the same as averaging the squares?", "The machine maps each possible input to an output. Squaring sends positive and negative inputs to the same nonnegative value and changes the distribution's shape.", "In general E[f(X)] ≠ f(E[X]). Here the input mean is 0, the mean squared output is 2, and the square of the input mean is 0."),
        "controls": [("rule", "select", [("double", "翻倍：数字 × 2", "Double: number × 2"), ("square", "平方：数字 × 自己", "Square: number × itself")], "机器的规则", "Machine rule")],
    },
    {
        "kind": "bayes",
        "zh": ("找宝藏：新线索怎样改变猜测？", "你原先猜宝藏在 4 米附近，标准差是 2 米。探测器带来一个新读数。曲线越高，表示那个位置越受支持；越窄，表示猜测越集中。", "先猜：新线索很模糊时，要不要完全丢掉原来的猜测？", "把原来的猜测和新线索合起来，就得到更新后的猜测。更清楚的线索通常能把猜测拉得更近、收得更窄。", "在独立高斯模型中，后验精度 = 先验精度 + 观测精度；精度是方差的倒数。虚线表示各位置对读数的支持程度（似然），不把读数当成绝对真值。"),
        "en": ("Find the treasure: learn from a new clue", "You initially place the treasure near 4 m with a standard deviation of 2 m. A detector supplies a new reading. Taller curves support a location more; narrower curves describe a more concentrated guess.", "Guess first: should a blurry new clue make us throw away everything we already thought?", "Combine the original guess with the clue to make an updated guess. A clearer clue usually pulls the result closer and makes it narrower.", "For independent Gaussian models, posterior precision = prior precision + observation precision; precision is inverse variance. The dashed likelihood describes support for the reading, which is not assumed to be exact truth."),
        "controls": [("reading", "range", 0, 10, .5, 8, "探测器读数（米）", "Detector reading (m)"), ("noise", "range", .5, 3, .5, 1, "线索有多模糊（标准差，米）", "Clue uncertainty (standard deviation, m)")],
    },
    {
        "kind": "noise",
        "zh": ("位置猜得不准，尺子也会抖", "我们给位置保留两种等可能猜测（菱形）。测量时，尺子还可能向左或向右抖一下，于是读数有四种等可能情况（圆点）。", "先猜：把尺子换成完全不抖的，所有位置上的不确定性都会消失吗？", "关于位置的未知，和测量时新加的抖动，是两件事。预测真实位置与预测下一次读数，需要的范围可能不同。", "这个两点分布例子中，两种误差独立且均值为零：读数方差 = 位置方差 a² + 测量噪声方差 b²。"),
        "en": ("An uncertain position and a wobbly ruler", "Two diamonds show equally likely guesses about position. The ruler can wobble left or right independently, giving four equally likely possible readings, shown as circles.", "Guess first: would a perfectly steady ruler remove all uncertainty about the position?", "Uncertainty about position and fresh measurement wobble are separate. Predicting a true position and predicting a future reading can require different ranges.", "In this two-point example the independent errors have zero means: reading variance = position variance a² + measurement-noise variance b²."),
        "controls": [("model", "range", 0, 2, .5, 1, "位置猜测的偏移 a（米）", "Position offset a (m)"), ("noise", "range", 0, 2, .5, 1, "尺子抖动的幅度 b（米）", "Ruler wobble b (m)")],
    },
    {
        "kind": "operator",
        "zh": ("水龙头的曲线，变成水桶的曲线", "上图记录每秒流进多少水，下图记录桶里已经积了多少水。改变开水方式，再问“第几秒，桶里有多少水”。", "先猜：越开越大的水龙头，积水曲线会越走越陡吗？关心水量时，能只看最后一秒的流速吗？", "一个完整的输入过程，决定另一个完整的输出过程，这叫算子。Branch 读取进水曲线，Trunk 接收想查询的时间，再一起给出水量。", "本动画用积分直接计算 s(t)=∫₀ᵗu(τ)dτ，作为正确答案。DeepONet 学的是这种曲线到曲线的对应关系；这里没有运行已训练的神经网络。"),
        "en": ("Turn a tap's curve into a bucket's curve", "The top graph shows water entering each second. The bottom shows water collected so far. Change the flow pattern, then ask how much water is in the bucket at a chosen time.", "Guess first: does a tap opening wider make the collected-water curve steeper? Is the final flow rate alone enough to know the total water?", "A whole input process determines a whole output process: an operator. Branch reads the flow curve; Trunk receives the query time; together they predict the water collected.", "This animation directly integrates s(t)=∫₀ᵗu(τ)dτ to provide the correct answer. DeepONet learns an approximation to such curve-to-curve mappings; no trained network runs here."),
        "controls": [("shape", "select", [("steady", "一直开一样大", "Steady flow"), ("rising", "越开越大", "Gradually opening"), ("wave", "一会儿大，一会儿小", "Varying flow")], "怎么开水龙头", "Tap pattern"), ("query", "range", 0, 4, .1, 2, "想问第几秒", "Query time (s)")],
    },
    {
        "kind": "kalman",
        "zh": ("两个人报位置，该更相信谁？", "你原先估计在 4 米处，标准差为 2 米；传感器说在 8 米处。调一调传感器有多准，看看新估计往哪边走。横线标出均值两侧一个标准差。", "先猜：传感器越来越不准时，新估计会更靠近 4 米，还是 8 米？", "更新像一场有根据的折中：谁的信息更可靠，谁的权重就更大。不是把两个数字不加区别地平均。", "K = 4/(4+R)，更新均值 = 4 + K×(8−4)，其中 R 是传感器噪声方差。本例满足独立高斯、线性观测条件，与第 5 讲的后验计算一致。"),
        "en": ("Two reports: which should we trust more?", "Your original estimate is 4 m with a standard deviation of 2 m. A sensor reports 8 m. Change the sensor's uncertainty and watch the updated estimate. Bars show one standard deviation on either side of each mean.", "Guess first: as the sensor becomes less reliable, will the new estimate move toward 4 m or 8 m?", "The update is a reasoned compromise: more reliable information receives more weight. It is not an unweighted average.", "K = 4/(4+R); updated mean = 4 + K×(8−4), where R is the sensor-noise variance. Independent Gaussian errors and linear observations make this the same posterior calculation as Lecture 5."),
        "controls": [("noise", "range", .5, 4, .5, 1, "传感器有多不准（标准差，米）", "Sensor uncertainty (standard deviation, m)")],
    },
    {
        "kind": "eki",
        "zh": ("一队小模型，一起修正猜测", "每个圆点是一个小模型的参数猜测。先让它们稍微探索，再各自给出预测，最后根据同一条观测一起修正。点之间的位置变化，就是一轮学习。", "先猜：如果大家都挤在一起，没有分歧，就一定猜对了吗？把探索幅度设成 0，再连续更新几次看看。", "每轮依次经过：扰动参数 → 计算预测 → 比较观测 → 更新成员。点击一次播放一轮，可以接着播放下一轮。", "这里只用 h(θ)=2θ 和观测 d=6 演示随机 EKI 更新，R=1；Q=q² 是人为加入的参数扰动方差。论文把这个玩具模型换成 DeepONet。有限集合不会自动成为精确后验样本。"),
        "en": ("A team of little models revises its guesses", "Each dot is one model's parameter guess. Let them explore a little, make predictions, compare them with the same observation, then update together.", "Guess first: if everyone agrees closely, does that prove they are right? Set exploration to zero and run several rounds.", "One round: perturb parameters → predict → compare with data → update members. Each play runs one round; play again for the next.", "This toy stochastic EKI uses h(θ)=2θ, observation d=6, and R=1. Q=q² is artificial parameter-perturbation variance. The paper replaces this simple model with DeepONet. A finite ensemble is not automatically an exact posterior sample."),
        "controls": [("explore", "range", 0, .6, .05, .15, "探索幅度 q（参数标准差）", "Exploration q (parameter standard deviation)")],
    },
    {
        "kind": "coverage",
        "zh": ("范围像一把伞，能接住多少小点？", "每个点是一回预测的真实误差，横着排的是 12 回不同预测。绿带表示愿意给出的误差范围；落在外面的点用叉号标记。", "先猜：把范围画得特别宽，是不是就能接住所有点？那为什么不永远画得越宽越好？", "范围太窄会漏掉真实结果，太宽又说不清结果在哪里。看不确定性，要一起看覆盖率、宽度和预测误差。", "覆盖率 = 范围内的点数 / 总点数。这里的 12 个固定例子只用于观察权衡；正式评估要用未参与调参的数据，并比较多个名义覆盖水平，不能由这幅图宣称 95% 保证。"),
        "en": ("An uncertainty band is like an umbrella", "Each point is the true error of one prediction; the horizontal order represents 12 different cases. The green band is the allowed error range. Crosses mark points outside it.", "Guess first: could a very wide umbrella catch every point? Why not always draw the widest possible band?", "A narrow range misses outcomes; an enormous one says little about where they will be. Assess coverage, width, and prediction error together.", "Coverage = points inside / total points. These 12 fixed examples illustrate a tradeoff. Real evaluation requires data not used for tuning and checks at multiple nominal levels; this picture does not establish a 95% guarantee."),
        "controls": [("width", "range", .3, 3, .1, 1, "伞向两侧张多宽（半宽，米）", "Umbrella half-width (m)")],
    },
]


def controls_html(controls: list, lang: str, number: int) -> str:
    result = []
    for control in controls:
        key, kind, *values = control
        control_id = f"lab-{number:02d}-{key}"
        if kind == "range":
            low, high, step, value, zh, en = values
            label = zh if lang == "zh" else en
            widget = f'<input id="{control_id}" data-key="{key}" type="range" min="{low}" max="{high}" step="{step}" value="{value}">'
            label += f' <output for="{control_id}" data-value="{key}">{value}</output>'
        else:
            options, zh, en = values
            label = zh if lang == "zh" else en
            options_html = "".join(f'<option value="{key}">{escape(zh if lang == "zh" else en)}</option>' for key, zh, en in options)
            widget = f'<select id="{control_id}" data-key="{key}">{options_html}</select>'
        result.append(f'<label class="lab-control" for="{control_id}"><span>{label}</span>{widget}</label>')
    return "".join(result)


def lab_html(number: int, lab: dict, lang: str) -> str:
    title, story, question, takeaway, bridge = lab[lang]
    zh = lang == "zh"
    play = ("播放一轮更新" if number == 9 else "播放小实验") if zh else ("Play one update" if number == 9 else "Play experiment")
    reset = "重新开始" if zh else "Reset"
    if number < len(LABS):
        next_title = LABS[number][lang][0]
        next_link = f'<a class="lab-next" href="#lab-{number+1:02d}">{"下一站：" if zh else "Next: "}{escape(next_title)} →</a>'
    else:
        next_link = f'<a class="lab-next" href="#course-lab-path">{"十个实验完成，回到学习路线" if zh else "Ten experiments complete. Return to the learning path"} ↑</a>'
    return f'''<section class="intuition-lab" id="lab-{number:02d}" data-lab="{lab['kind']}" aria-labelledby="lab-{number:02d}-title">
  <p class="lab-eyebrow">{'先玩一分钟' if zh else 'A one-minute experiment'} · {number:02d} / 10</p>
  <h3 id="lab-{number:02d}-title">{escape(title)}</h3>
  <p class="lab-story">{escape(story)}</p>
  <p class="lab-question">{escape(question)}</p>
  <div class="lab-controls" hidden>{controls_html(lab['controls'], lang, number)}</div>
  <div class="lab-stage"><svg role="img" aria-label="{escape(title, quote=True)}"><title>{escape(title)}</title><desc>{escape(story)}</desc></svg></div>
  <div class="lab-actions" hidden><button type="button" data-lab-play>{play}</button><button type="button" data-lab-reset>{reset}</button><span class="lab-motion-note">{'按播放才会动，随时可暂停' if zh else 'Play to animate; pause any time'}</span></div>
  <p class="lab-result" role="status" aria-live="polite" aria-atomic="true">{escape(takeaway)}</p>
  <p class="lab-takeaway"><strong>{'记住这一点：' if zh else 'Take this with you: '}</strong>{escape(takeaway)}</p>
  <details class="lab-bridge"><summary>{'把直觉接回理论' if zh else 'Connect the intuition to the theory'}</summary><p>{escape(bridge)}</p></details>
  {next_link}
  <noscript><p>{'开启 JavaScript 可拖动和播放实验；上面的生活例子与下方理论仍可直接阅读。' if zh else 'Enable JavaScript to interact and animate. The everyday explanation and full theory remain readable.'}</p></noscript>
</section>'''


def enrich_course(body: str, lang: str) -> str:
    zh = lang == "zh"
    guide = f'''<aside class="lab-guide" id="course-lab-path" aria-label="{'动画学习路线' if zh else 'Animated learning path'}">
  <p class="lab-eyebrow">{'先看会动的，再读公式' if zh else 'See it move. Then read the mathematics.'}</p>
  <p>{'每讲开头都有一个可以拖动、播放的小实验。先用生活经验猜一猜，再看结果；不懂符号也能先抓住一个核心想法。' if zh else 'Each lecture opens with an experiment you can adjust and play. Make a guess, watch what changes, and grasp the main idea before tackling the symbols.'}</p>
  <p>{'第一次来，可以沿着每个实验底部的“下一站”走完十个生活例子。想知道为什么，再展开“把直觉接回理论”，或接着读本讲正文。' if zh else 'On a first visit, follow “Next” beneath each experiment through all ten everyday examples. When you want the mathematics, open the theory connection or continue into the lecture.'}</p>
  <a href="#lab-01">{'从小车比赛开始' if zh else 'Start with the little cars'} →</a>
</aside>'''
    for number, lab in enumerate(LABS, 1):
        pattern = rf'(<h2 id="lecture-{number:02d}">.*?</h2>)'
        body, count = re.subn(pattern, lambda match: match[0] + "\n" + lab_html(number, lab, lang), body, count=1)
        if count != 1:
            raise ValueError(f"Interactive experiment needs lecture {number} in {lang}")
    return guide + body
