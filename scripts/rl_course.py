"""Assemble the 65-lesson RL manuscript from editable, local fragments."""
from pathlib import Path
from html import escape
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/courses/rl'
SLUG = 'robot-reinforcement-learning'
PHASES = [
    (1, 6, '从奖励到探索', '16–22 小时', '充电站侦察员', 'NumPy老虎机；比较随机、贪心、ε-greedy、UCB。报告累计奖励、遗憾与独立重复的波动，解释探索的代价。'),
    (7, 15, 'MDP 与贝尔曼方程', '32–40 小时', '有地图的快递机器人', '带滑移网格；实现策略评估、策略迭代、价值迭代。用线性方程与贝尔曼残差核对，手算一次更新。'),
    (16, 23, '从经验学习', '34–46 小时', '悬崖快递员', '未知转移网格；比较MC、TD、SARSA、Q-Learning。报告成功率、跌落、回报与样本效率，解释行为/目标策略差别。'),
    (24, 29, '深度价值学习', '30–42 小时', '扶住倒立摆', 'CartPole与自写DQN；检查终止、自举与目标梯度。固定预算完成Replay、Target、Double或Dueling的受控消融。'),
    (30, 39, '直接优化策略', '50–66 小时', '机器人驾驶学校', '自写REINFORCE、A2C与PPO；记录回报、熵、KL和裁剪比例。推导梯度并审查旧策略概率与优势。'),
    (40, 48, '连续控制与机器人', '50–68 小时', '快、稳、省电地到达', 'Pendulum到平面动力学；TD3/SAC与控制基线对照。报告误差、能量、扰动、约束违反和任务成功率。'),
    (49, 58, '模型、数据与结构', '44–62 小时', '先在脑中练习', '学习动力学并接入MPC；比较已知模型MPC和无模型策略。检验多步误差、交互量、规划延迟；另选一个研究分支。'),
    (59, 65, '可复现的研究', '60–88 小时', '学习何时值得？', '形成可证伪假设；复用并审查PPO/SAC，实现公平基线、消融与独立测试。交付代码、配置、负结果和研究报告。'),
]


def assemble():
    fragments = []
    titles = []
    for n in range(1, 66):
        path = ASSETS / 'chapters' / f'lesson-{n:02d}.htmlfrag'
        body = path.read_text(encoding='utf-8')
        # The reader owns the outer section; discard author-supplied wrappers.
        body = body.strip()
        if re.match(r'<section\b[^>]*class="rl-lesson"', body):
            body = re.sub(r'^<section\b[^>]*>\s*', '', body, count=1)
            body = re.sub(r'\s*</section>\s*$', '', body, count=1)
        match = re.search(r'<h2[^>]*>(.*?)</h2>', body, re.S)
        if not match:
            raise ValueError(f'Missing lesson title: {path}')
        title = re.sub('<[^>]+>', '', match[1])
        titles.append(title)
        if len(re.findall(r'<h3\b', body)) < 11:
            raise ValueError(f'Incomplete twelve-part structure: {path}')
        if '<svg' not in body or '<pre' not in body or '<details' not in body:
            raise ValueError(f'Missing diagram, code or answers: {path}')
        phase = next(i for i, (a, b, *_) in enumerate(PHASES, 1) if a <= n <= b)
        download = f'<p class="rl-download"><a download href="../assets/courses/rl/examples/lesson_{n:02d}.py">下载本课 Python 实验 ↓</a> · <a download href="../assets/courses/rl/rl-experiments.zip">完整实验包（含共用模块）↓</a></p>'
        body = body.replace('<pre', download + '<pre', 1)
        record = f'''<aside class="rl-record" data-record="{n}"><h3>学习记录 · 第 {n} 讲</h3>
        <p>阅读、解释与独立实现分别记录。请在备注中保留你的推导、实验结果及仍不确定的地方。</p>
        <label><input type="checkbox" data-status="read"> 已阅读</label>
        <label><input type="checkbox" data-status="explain"> 能独立解释 / 推导</label>
        <label><input type="checkbox" data-status="implement"> 已独立完成本课实验</label>
        <label class="rl-note-label">证据与疑问<textarea rows="3" placeholder="例：手算结果……；修改参数后……；还不理解……" aria-label="第{n}讲学习记录"></textarea></label>
        <p class="rl-save-status" aria-live="polite">记录保存在此浏览器，可在课程首页导出。</p></aside>'''
        previous = f'<a href="#lecture-{n-1:02d}">← 上一讲</a>' if n > 1 else '<span></span>'
        following = f'<a href="#lecture-{n+1:02d}">下一讲 →</a>' if n < 65 else '<a href="#rl-overview">回到课程总览 →</a>'
        footer = f'<nav class="rl-lesson-footer" aria-label="第{n}讲前后导航">{previous}<a href="#rl-overview">课程总览</a>{following}</nav>'
        fragments.append(f'<section class="rl-lesson" data-lesson="{n}" data-phase="{phase}">{body}\n{record}{footer}</section>')

    options = ''.join(f'<option value="{n}">{escape(t)}</option>' for n, t in enumerate(titles, 1))
    phases = []
    for i, (a, b, name, hours, project, rubric) in enumerate(PHASES, 1):
        lessons = ''.join(f'<li><a href="#lecture-{n:02d}">{escape(titles[n-1])}</a></li>' for n in range(a, b+1))
        phases.append(f'<details class="rl-phase"><summary><span>0{i} · {name}</span><small>{b-a+1} 课 · {hours}</small></summary><ol start="{a}">{lessons}</ol><div class="rl-project"><strong>综合挑战：{project}</strong><p>{rubric}</p></div></details>')

    intro = f'''<div id="rl-course" class="rl-course">
    <section id="rl-overview" class="rl-home" aria-label="课程总览">
      <div class="rl-intro"><p class="rl-kicker">REINFORCEMENT LEARNING / A ROBOT'S JOURNEY</p>
      <h2>从第一次试错，到可信的自主控制研究</h2>
      <p>一台移动机器人，65 个有趣的问题。沿着“直觉 → 建模 → 推导 → 手算 → 实验”的路线，把强化学习与动力学、最优控制、运动规划连接起来。</p>
      <div class="rl-facts"><span><strong>65</strong> 讲完整阅读稿</span><span><strong>8</strong> 个阶段挑战</span><span><strong>316–434</strong> 小时建议投入</span></div>
      <p><a class="rl-primary" href="#lecture-01">从充电站门口开始 →</a> <a href="#rl-labs">打开交互实验室</a></p></div>
      <figure class="rl-map"><svg viewBox="0 0 720 380" role="img" aria-label="课程依赖图，从交互与回报，经MDP、经验学习、函数逼近和策略梯度，到机器人与研究"><defs><marker id="rl-map-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" fill="var(--accent)"/></marker></defs>
      <g fill="none" stroke="var(--accent)" stroke-width="2" marker-end="url(#rl-map-arrow)"><path d="M195 57H265"/><path d="M445 57H515"/><path d="M605 94V120H105V146"/><path d="M355 94V146"/><path d="M195 181H265"/><path d="M445 181H515"/><path d="M605 220V270H355V296"/><path d="M265 333H195"/></g>
      <g fill="var(--accent-soft)" stroke="var(--line)"><rect x="15" y="20" width="180" height="74" rx="10"/><rect x="265" y="20" width="180" height="74" rx="10"/><rect x="515" y="20" width="190" height="74" rx="10"/><rect x="15" y="146" width="180" height="74" rx="10"/><rect x="265" y="146" width="180" height="74" rx="10"/><rect x="515" y="146" width="190" height="74" rx="10"/><rect x="265" y="296" width="180" height="74" rx="10"/><rect x="15" y="296" width="180" height="74" rx="10"/></g>
      <g fill="var(--text)" text-anchor="middle" font-size="17"><text x="105" y="50">01 交互与探索</text><text x="105" y="76">回报 · 策略 · Bandit</text><text x="355" y="50">02 MDP 与贝尔曼</text><text x="355" y="76">V / Q · 动态规划</text><text x="610" y="50">03 从经验学习</text><text x="610" y="76">MC · TD · Q-Learning</text><text x="105" y="176">04 函数逼近</text><text x="105" y="203">DQN · 回放 · 目标网络</text><text x="355" y="176">05 策略梯度</text><text x="355" y="203">Actor-Critic · PPO</text><text x="610" y="176">06 连续机器人控制</text><text x="610" y="203">DDPG · TD3 · SAC</text><text x="355" y="326">07 模型、数据与结构</text><text x="355" y="353">MPC · Offline · Safe RL</text><text x="105" y="326">08 可复现的研究</text><text x="105" y="353">基线 · 消融 · 假设</text></g></svg>
      <figcaption>主要依赖：表格经验学习支撑函数逼近与 critic；策略梯度支撑 PPO 和连续控制。阶段七的方向可分别深入。</figcaption></figure>
      <div class="rl-route">{''.join(phases)}</div>
      <section class="rl-how"><h3>怎样使用这份课程</h3><p>每讲保留十二个环节与三级挑战。先尝试手算与思考，再展开参考答案；跑通代码后改变一个参数，用结果检验解释。数学结论注明假设，工程方法与经验建议分别说明。高级方向先做最小实验，再选一个分支深入。</p>
      <p>环境建议：Python 3.11–3.12；初期 NumPy，绘图使用 Matplotlib；深度阶段加入 PyTorch 与 Gymnasium。完整实验包包含安装说明与可复用模块。训练随机性需用多个训练种子评估；每个模型的多个评估回合不等于多个独立训练种子。</p>
      <p><a download href="../assets/courses/rl/rl-experiments.zip">下载完整 Python 实验包</a> · <a href="../assets/courses/rl/examples/README.md">环境与运行说明</a></p>
      <p class="rl-progress" aria-live="polite">学习记录尚未加载。</p><button type="button" id="rl-export">导出学习记录 JSON</button></section>
      <section id="rl-labs" class="rl-labs"><h3>交互实验室：先猜，再改变一个条件</h3><p>以下图形由明确的教学模型实时计算。浏览器中的小实验用于建立直觉，完整算法训练请运行各课 Python。</p>{lab_markup()}</section>
    </section>
    <nav class="rl-reader-nav" aria-label="课程阅读导航"><a href="#rl-overview">← 课程总览</a><label>跳到一讲<select id="rl-jump" aria-label="选择课程">{options}</select></label><button type="button" id="rl-prev">上一讲</button><button type="button" id="rl-next">下一讲</button><button type="button" id="rl-show-all">连续阅读</button></nav>
    {''.join(fragments)}
    </div>'''
    target = ROOT / 'content/courses' / SLUG / 'course.zh.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('''---
title: 从试错到自主：强化学习与机器人控制的 65 次探索
date: 2026-11-06
updated: 2026-11-06
lang: zh
translation_key: robot-reinforcement-learning
summary: 从充电站门口的奖励漏洞出发，经过65讲故事、图解、数学推导、手算与Python实验，建立强化学习理论、PPO/SAC实现和机器人研究能力。
tags: 强化学习, 机器人控制, 贝尔曼方程, PPO, SAC, 最优控制
slug: robot-reinforcement-learning
---
''' + intro, encoding='utf-8')
    package = ASSETS / 'rl-experiments.zip'
    with zipfile.ZipFile(package, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ASSETS / 'examples').glob('*')):
            if p.is_file() and p.suffix in {'.py', '.md', '.txt', '.json'} and 'authoring' not in p.name:
                z.write(p, 'rl-experiments/' + p.name)
    return titles


def lab_markup():
    labs = [
        ('reward', '奖励会鼓励怎样的行为？', '靠近一步 +1，后退 0，进入充电站奖励由你设置。比较12步内的门口循环和第3步进站。', '进站奖励', 0, 12, 1, 2),
        ('discount', '同样的奖励，晚一点还值多少？', '比较立即得到4分，与第4个时间项得到8分。时间从0开始，两条竖线都由折扣公式计算。', '折扣 γ', 0, 1, .01, .9),
        ('bandit', '只选看起来最好的站，会错过什么？', '三个固定Bernoulli收益率为0.35、0.55、0.70；500步，每次以相同种子比较纯贪心与ε-greedy。', '探索率 ε', 0, 1, .01, .1),
        ('bellman', '价值怎样从终点传回起点？', '四个非终止位置依次通向终点；仅最后一步奖励1，γ=0.9。从全零价值做同步Bellman备份。', '同步备份轮数', 0, 8, 1, 0),
        ('ppo', '裁剪究竟在哪一侧生效？', '固定旧动作概率0.4、ε=0.2。曲线表示正/负优势下的min代理目标，竖线由新旧概率比确定。', '新动作概率', .04, .96, .01, .6),
        ('entropy', '温度升高，动作分布会怎样变化？', '固定Q=[0,1,2]，通过softmax(Q/α)精确计算最大熵目标的最优离散分布。', '温度 α', .1, 3, .1, .6),
        ('model', '一个小小的模型误差，能积累多大？', '真实系统x[t+1]=1.02x[t]，模型使用1.02+偏差，无控制且x0=1。两条曲线是解析递推。', '模型系数偏差', -.1, .1, .005, .03),
    ]
    return ''.join(f'''<section class="rl-lab" data-lab="{kind}"><h4>{title}</h4><p>{desc}</p><label>{label} <output>{value}</output><input type="range" min="{lo}" max="{hi}" step="{step}" value="{value}" aria-label="{label}"></label><svg viewBox="0 0 680 260" role="img" aria-label="{title}"></svg><p class="rl-lab-result" aria-live="polite"></p></section>''' for kind, title, desc, label, lo, hi, step, value in labs)


if __name__ == '__main__':
    print(f'Assembled {len(assemble())} RL lessons and experiment archive')
