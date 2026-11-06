# 从试错到自主：65讲 Python 实验

解压完整实验包后，在 rl-experiments 目录运行。单独下载脚本时请留意：

- 第28、29讲依赖同目录 lesson_26.py。
- 第31、34、35、39讲依赖 rl_policy_common.py。
- 第42、43、45讲依赖 rl_continuous_common.py。
- 连续训练器使用 --env PointRobot-v0 时，还需要同目录 lesson_48.py。

## 安装

推荐 Python 3.11 或 3.12，新建独立环境：

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
~~~

Linux/macOS 激活命令为 source .venv/bin/activate。基础课程仅需 NumPy 和 Matplotlib；从深度学习阶段开始才需要 PyTorch 与 Gymnasium。无需强化学习框架、GPU或机器人硬件。

## 运行

~~~powershell
python lesson_01.py
python lesson_15.py
python lesson_26.py --smoke
python lesson_26.py --steps 20000 --seed 26 --plot
python lesson_39.py --smoke
python lesson_45.py --smoke
python lesson_45.py --env PointRobot-v0 --steps 20000 --seed 7 --plot
python lesson_65.py
~~~

支持 --smoke 的训练入口：26、28、29、31、34、35、39、42、43、45、48。用 --help 查看各训练器参数。非训练类脚本通常直接运行即可。

脚本保存的PNG/JSON/CSV写入当前工作目录。批量无界面运行时设置环境变量 MPLBACKEND=Agg。部分早期实验会显示图形窗口，关闭窗口后程序结束。

## 如何解读结果

每课的最小实验用来验证一个具体机制。短运行通过只说明采样、更新与评估流程可以执行，不能证明充分学习、算法优劣、安全性或稳定收敛。完整训练需重复独立训练种子，每个模型再用独立评估回合测量；训练种子与评估回合是不同统计单位。

第49—58讲包含线性辨识、潜表示、模仿数据聚合、保守估值、options、博弈、安全与Sim-to-Real的最小模型。它们不会伪装成完整Dreamer/CQL/多智能体或真机训练。第62讲数组是明确标注的合成统计示例。第63讲为控制基线，第65讲是标量系统的随机参数搜索研究原型。

## 版本与复现

本次验证环境：Python 3.12、NumPy 2.3.5、Matplotlib 3.11.2、Gymnasium 1.4.0、PyTorch 2.15.0+cpu。安装兼容版本后先运行短验证，再开始长训练；记录你的实际软件、硬件、代码版本、配置与随机种子。

课程正文、代码和图解可直接本地浏览。学习记录保存在浏览器本地，不会上报网站；建议定期从课程首页导出JSON。
