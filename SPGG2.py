import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import random
import matplotlib
import os
import time
from mpl_toolkits.axes_grid1 import make_axes_locatable
from multiprocessing import Pool, cpu_count
from scipy.ndimage import zoom
import warnings

warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# ======================
# 基本设置
# ======================
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

random.seed(42)
np.random.seed(42)

# ======================
# 参数设置
# ======================
N_SIDE = 50  # 网络边长
N = N_SIDE * N_SIDE  # 节点总数
iterations = 3000  # 总迭代步数
steps = 2000  # 稳定态数据取最后steps步
reps_initial_range = [0, 20]  # 声誉初始化范围
a_values = [0.6, 0.7, 0.8, 0.9, 1.0]  # 分配系数a
c = 1  # 合作成本
R_max = 20.0  # 最大声誉值
beta1=0.5 #实验1的β取值？
beta = 0.25  # 默认声誉影响系数（时间演化图beta取值）

# 模拟次数参数
FAST_SIMULATIONS = 10  # 每个点的模拟次数（图一，图二）
TIME_SIMULATIONS = 10  # 时间演化曲线的重复次数（图五）
HEATMAP_SIMULATIONS = 10  # 热力图每个点的模拟次数（图六）

# 参数列表
beta_values = [0.0, 0.25, 0.5, 0.75, 1.0]  # 声誉影响系数

# 采样点数
R_VALUES_NUM = 30  # r值的采样点数
HEATMAP_RESOLUTION = 12  # 热力图分辨率

# 固定参数
R_FIXED = 3  # 固定r值
A_FIXED = 0.8  # 固定a值（用于图2）
SNAPSHOT_TIMES = [0, 10, 100, 1000]  # 快照时间点

# 小世界网络参数
SW_K = 4  # 初始邻居数
SW_P = 0.1  # 重连概率

# 网络类型常量
NETWORK_GRID = "grid"
NETWORK_SW = "sw"

# 颜色设置
strategy_cmap = ListedColormap(['red', 'blue'])  # 红=背叛，蓝=合作
reputation_cmap = plt.cm.viridis

# 邻居缓存
_GRID_NEIGHBORS_CACHE = None
_SW_NEIGHBORS_CACHE = None


# ======================
# 邻居缓存工具
# ======================
def get_neighbors(i, j, N_SIDE):
    """获取冯·诺依曼邻域（周期性边界）"""
    neighbors = []
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        ni, nj = (i + di) % N_SIDE, (j + dj) % N_SIDE
        neighbors.append((ni, nj))
    return neighbors


def build_grid_neighbors_cache():
    """构建规则网格邻居缓存"""
    global _GRID_NEIGHBORS_CACHE
    if _GRID_NEIGHBORS_CACHE is None:
        cache = {}
        for i in range(N_SIDE):
            for j in range(N_SIDE):
                cache[(i, j)] = get_neighbors(i, j, N_SIDE)
        _GRID_NEIGHBORS_CACHE = cache
    return _GRID_NEIGHBORS_CACHE


def build_small_world_enhanced(verbose=False, use_cache=True):
    """构建小世界网络，返回邻居字典"""
    global _SW_NEIGHBORS_CACHE
    if use_cache and _SW_NEIGHBORS_CACHE is not None:
        return _SW_NEIGHBORS_CACHE
    G = nx.watts_strogatz_graph(N, SW_K, SW_P, seed=42)
    neighbors = {i: list(G.neighbors(i)) for i in range(N)}
    _SW_NEIGHBORS_CACHE = neighbors
    return neighbors


def get_sw_neighbors_ij(i, j, sw_neighbors_dict):
    """获取小世界网络中节点的邻居坐标"""
    idx = i * N_SIDE + j
    neighbor_idxs = sw_neighbors_dict[idx]
    if not neighbor_idxs:
        return [(i, j)]
    return [divmod(n_idx, N_SIDE) for n_idx in neighbor_idxs]


def get_neighbors_by_network(i, j, network, sw_neighbors_dict=None):
    """根据网络类型获取邻居"""
    if network == NETWORK_GRID:
        return _GRID_NEIGHBORS_CACHE[(i, j)]
    else:
        if sw_neighbors_dict is None:
            return [(i, j)]
        return get_sw_neighbors_ij(i, j, sw_neighbors_dict)


# ======================
# 核心函数（修改：去掉n参数，不再对低声誉个体折扣）
# ======================
def calculate_reputation_score(j, i, strategies, reputations, global_avg_rep, network, sw_neighbors_dict):
    """计算邻居j对i的评价 ε(j→i) - 无折扣版本"""
    neighbors_j = get_neighbors_by_network(j[0], j[1], network, sw_neighbors_dict)
    group_j = neighbors_j + [j]
    coop_count = sum([strategies[m[0], m[1]] == 1 for m in group_j])
    defect_count = len(group_j) - coop_count
    coop_ratio = coop_count / len(group_j)
    defect_ratio = defect_count / len(group_j)

    # 无论声誉高低，评价规则相同（去掉n折扣）
    if strategies[i[0], i[1]] == 1:
        score = coop_ratio
    else:
        score = -defect_ratio
    return score


def calculate_performance_scores(strategies, reputations, network, sw_neighbors_dict):
    """计算所有节点的绩效考核分 - 无折扣版本"""
    performance_scores = np.zeros((N_SIDE, N_SIDE))
    global_avg_rep = np.mean(reputations)
    for i in range(N_SIDE):
        for j in range(N_SIDE):
            neighbors_i = get_neighbors_by_network(i, j, network, sw_neighbors_dict)
            scores = []
            for neighbor in neighbors_i:
                score = calculate_reputation_score(
                    neighbor, (i, j), strategies, reputations,
                    global_avg_rep, network, sw_neighbors_dict
                )
                scores.append(score)
            performance_scores[i, j] = np.mean(scores) if scores else 0
    return performance_scores


def calculate_group_payoff(center, strategies, performance_scores, a, r, network, sw_neighbors_dict):
    """计算g小组中个体i的收益"""
    i, j = center
    neighbors = get_neighbors_by_network(i, j, network, sw_neighbors_dict)
    group = neighbors + [(i, j)]
    if not group:
        return {}
    coop_count = sum([strategies[m[0], m[1]] == 1 for m in group])
    Pg = r * coop_count
    G = len(group)

    scores = {m: performance_scores[m[0], m[1]] for m in group}
    s_vals = list(scores.values())
    s_min, s_max = min(s_vals), max(s_vals)

    if s_max - s_min < 1e-10:
        weights = {m: 1 / G for m in group}
    else:
        normalized_scores = {m: (scores[m] - s_min) / (s_max - s_min) for m in group}
        norm = sum(normalized_scores.values())
        if norm < 1e-10:
            weights = {m: 1 / G for m in group}
        else:
            weights = {m: normalized_scores[m] / norm for m in group}

    payoffs = {}
    for m in group:
        equal_part = a * Pg / G
        weighted_part = (1 - a) * Pg * weights[m]
        payoff = equal_part + weighted_part
        if strategies[m[0], m[1]] == 1:
            payoff -= c
        payoffs[m] = payoff
    return payoffs


def calculate_total_payoffs(strategies, performance_scores, a, r, network, sw_neighbors_dict):
    """计算所有节点总收益"""
    payoffs = np.zeros((N_SIDE, N_SIDE))
    for i in range(N_SIDE):
        for j in range(N_SIDE):
            group_payoffs = calculate_group_payoff(
                (i, j), strategies, performance_scores, a, r, network, sw_neighbors_dict
            )
            for (ni, nj), val in group_payoffs.items():
                payoffs[ni, nj] += val
    return payoffs


def calculate_fitness(payoff, reputation, global_avg_rep, Rmax=20, beta=0.5):
    """计算适应度函数"""
    if Rmax <= 0:
        Rmax = 20
    factor = 1 + beta * (reputation - global_avg_rep) / Rmax
    return payoff * factor


def update_strategy(i, strategies, payoffs, reputations, network, sw_neighbors_dict, K=0.1, beta=0.5):
    """适应度函数更新策略"""
    neighbors_i = get_neighbors_by_network(i[0], i[1], network, sw_neighbors_dict)
    if not neighbors_i:
        return strategies[i[0], i[1]]

    j = random.choice(neighbors_i)
    global_avg_rep = np.mean(reputations)

    Fi = calculate_fitness(payoffs[i[0], i[1]], reputations[i[0], i[1]], global_avg_rep, R_max, beta)
    Fj = calculate_fitness(payoffs[j[0], j[1]], reputations[j[0], j[1]], global_avg_rep, R_max, beta)

    prob = 1 / (1 + np.exp(-(Fj - Fi) / K))
    if np.random.rand() < prob:
        return strategies[j[0], j[1]]
    else:
        return strategies[i[0], i[1]]


def update_reputations(reputations, performance_scores):
    """更新声誉"""
    new_reputations = reputations + performance_scores
    new_reputations = np.clip(new_reputations, 0, 20)
    return new_reputations


# ======================
# 模拟主函数（修改：去掉n参数）
# ======================
def run_simulation(args):
    """运行单次模拟 - 用于并行计算"""
    a, r, network, record_snapshots, seed, beta_val = args

    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    sw_neighbors_dict = None
    if network == NETWORK_SW:
        sw_neighbors_dict = build_small_world_enhanced(use_cache=True)
    else:
        build_grid_neighbors_cache()

    strategies = np.random.choice([0, 1], size=(N_SIDE, N_SIDE), p=[0.5, 0.5])
    reputations = np.random.uniform(0, 20, size=(N_SIDE, N_SIDE))

    cooperation_history = []
    reputation_history = []
    snapshots = {} if record_snapshots else None

    for t in range(iterations + 1):
        cooperation_history.append(np.mean(strategies))
        reputation_history.append(np.mean(reputations))

        if record_snapshots and t in SNAPSHOT_TIMES:
            snapshots[t] = {
                'strategy': strategies.copy(),
                'reputation': reputations.copy(),
                'cooperation_rate': np.mean(strategies)
            }

        if t < iterations:
            performance_scores = calculate_performance_scores(
                strategies, reputations, network, sw_neighbors_dict
            )
            payoffs = calculate_total_payoffs(
                strategies, performance_scores, a, r, network, sw_neighbors_dict
            )

            new_strategies = np.zeros_like(strategies)
            for i in range(N_SIDE):
                for j in range(N_SIDE):
                    new_strategies[i, j] = update_strategy(
                        (i, j), strategies, payoffs, reputations,
                        network, sw_neighbors_dict, 0.1, beta_val
                    )

            reputations = update_reputations(reputations, performance_scores)
            strategies = new_strategies

    if record_snapshots:
        return cooperation_history, reputation_history, snapshots
    else:
        return cooperation_history, reputation_history


def run_multiple_simulations_parallel(args):
    """运行多次模拟取平均合作率和平均声誉 - 用于并行计算"""
    a, r, network, sim_count, beta_val, return_both = args
    coop_rates = []
    rep_values = []
    for sim in range(sim_count):
        seed = random.randint(1, 10000) + sim
        coop_hist, rep_hist = run_simulation((a, r, network, False, seed, beta_val))
        final_coop = np.mean(coop_hist[-steps:])
        final_rep = np.mean(rep_hist[-steps:])
        coop_rates.append(final_coop)
        rep_values.append(final_rep)

    if return_both:
        return np.mean(coop_rates), np.mean(rep_values)
    else:
        return np.mean(coop_rates)


def run_time_evolution_parallel(args):
    """运行时间演化模拟 - 用于并行计算"""
    a, r, network, sim_id, beta_val = args
    seed = random.randint(1, 10000) + sim_id
    coop_hist, rep_hist = run_simulation((a, r, network, False, seed, beta_val))
    return {
        'coop': coop_hist,
        'rep': rep_hist,
        'params': (a, r, network, beta_val)
    }


# ======================
# 数据计算函数（修改：去掉n参数）
# ======================

def compute_figure1_data():
    print("计算图1数据分配系数a对合作率的影响")

    r_values = np.linspace(1.0, 5.0, 41)

    params_list = []
    for a in a_values:
        for r in r_values:
            params_list.append((a, r, NETWORK_GRID, FAST_SIMULATIONS, beta1, True))

    with Pool(processes=max(1, cpu_count() - 1)) as pool:
        results = pool.map(run_multiple_simulations_parallel, params_list)

    coop_matrix = np.array([r[0] for r in results]).reshape(len(a_values), len(r_values))
    rep_matrix = np.array([r[1] for r in results]).reshape(len(a_values), len(r_values))

    np.savez('fig1_data2.npz',
             r=r_values,
             coop=coop_matrix,
             rep=rep_matrix,
             a_values=a_values)

    print("✓ fig1_data.npz 已保存")


def compute_figure2_data():
    """图2：不同β下合作频率/平均声誉 vs 增强因子r (a=0.8固定，规则网格)"""
    print("计算图2数据...")

    r_values = np.linspace(1.0, 4.5, 36)  # 原来是 r_range = [1.0, 5.0]

    params_list = []
    for beta_val in beta_values:
        for r in r_values:
            params_list.append((A_FIXED, r, NETWORK_GRID, FAST_SIMULATIONS, beta_val, True))

    with Pool(processes=max(1, cpu_count() - 1)) as pool:
        results = pool.map(run_multiple_simulations_parallel, params_list)

    coop_matrix = np.array([r[0] for r in results]).reshape(len(beta_values), len(r_values))
    rep_matrix = np.array([r[1] for r in results]).reshape(len(beta_values), len(r_values))

    np.savez('fig2_data2.npz',
             r=r_values,
             coop=coop_matrix,
             rep=rep_matrix,
             beta_values=beta_values)

    print("✓ fig2_data.npz 已保存")


def compute_figure4_data():
    """计算并保存图4的快照数据"""
    print("计算图4数据并保存...")

    build_grid_neighbors_cache()
    snapshots_data = {}

    for a in a_values:
        print(f"  模拟 a={a}...")
        start = time.time()
        _, _, snapshots = run_simulation((a, R_FIXED, NETWORK_GRID, True, 42, beta))
        elapsed = time.time() - start
        snapshots_data[a] = snapshots
        print(f"    完成，耗时{elapsed:.1f}s")

    # 保存快照数据
    save_dict = {'a_values': a_values, 'snapshot_times': SNAPSHOT_TIMES}
    for a in a_values:
        for t in SNAPSHOT_TIMES:
            if t in snapshots_data[a]:
                save_dict[f'a_{a}_t_{t}_strategy'] = snapshots_data[a][t]['strategy']
                save_dict[f'a_{a}_t_{t}_reputation'] = snapshots_data[a][t]['reputation']
                save_dict[f'a_{a}_t_{t}_coop_rate'] = snapshots_data[a][t]['cooperation_rate']

    np.savez('fig4_data.npz', **save_dict)
    print("✓ fig4_data.npz 已保存")


def compute_figure5_data():
    """图5：规则格子vs小世界网络下不同a值随时间演化的合作频率/平均声誉"""
    print("计算图5数据...")

    networks = [NETWORK_GRID, NETWORK_SW]
    results_all = {}

    for network in networks:
        print(f"  网络类型: {network}")

        params_list = []
        sim_id = 0

        for a in a_values:
            for run in range(TIME_SIMULATIONS):
                params_list.append((a, R_FIXED, network, sim_id, beta))
                sim_id += 1

        with Pool(processes=max(1, cpu_count() - 1)) as pool:
            results = pool.map(run_time_evolution_parallel, params_list)

        coop_data = []
        rep_data = []

        for idx, a in enumerate(a_values):
            all_coop = []
            all_rep = []

            for run in range(TIME_SIMULATIONS):
                r = results[idx * TIME_SIMULATIONS + run]
                all_coop.append(r['coop'])
                all_rep.append(r['rep'])

            coop_data.append(np.mean(all_coop, axis=0))
            rep_data.append(np.mean(all_rep, axis=0))

        results_all[network] = {
            'coop': np.array(coop_data),
            'rep': np.array(rep_data)
        }

    np.savez('fig5_data.npz',
             grid_coop=results_all[NETWORK_GRID]['coop'],
             grid_rep=results_all[NETWORK_GRID]['rep'],
             sw_coop=results_all[NETWORK_SW]['coop'],
             sw_rep=results_all[NETWORK_SW]['rep'],
             a_values=a_values)

    print("✓ fig5_data.npz 已保存")


def compute_figure6_data():
    """图6：a-β参数空间合作频率/平均声誉热力图"""
    print("计算图6数据...")

    a_values_dense = np.linspace(0.5, 1.0, HEATMAP_RESOLUTION)
    beta_values_dense = np.linspace(0, 1.0, HEATMAP_RESOLUTION)

    params_list = []
    for beta_val in beta_values_dense:
        for a in a_values_dense:
            params_list.append((a, R_FIXED, NETWORK_GRID, HEATMAP_SIMULATIONS, beta_val, True))

    with Pool(processes=max(1, cpu_count() - 1)) as pool:
        results = pool.map(run_multiple_simulations_parallel, params_list)

    coop_data = np.array([r[0] for r in results]).reshape(len(beta_values_dense), len(a_values_dense))
    rep_data = np.array([r[1] for r in results]).reshape(len(beta_values_dense), len(a_values_dense))

    np.savez('fig6_data.npz',
             coop=coop_data,
             rep=rep_data,
             a_values=a_values_dense,
             beta_values=beta_values_dense)

    print("✓ fig6_data.npz 已保存")



# ======================
# 图7：不同a值下评分分布快照（a=0.6,0.7,0.8,0.9,1.0, r=3.0, β=0.5）
# ======================
def compute_figure7_data():
    """计算图7数据：不同a值下策略、声誉、收益、评分的空间分布快照"""
    print("=" * 60)
    print("计算图7数据（不同a值下评分分布快照）")
    print("=" * 60)

    r = 3.0
    beta_val = 0.5
    network = NETWORK_GRID

    # 使用全局的 a_values = [0.6, 0.7, 0.8, 0.9, 1.0]
    a_list = a_values

    # 构建邻居缓存
    build_grid_neighbors_cache()

    snapshots_data = {}

    for a in a_list:
        print(f"  模拟 a={a}...")
        start = time.time()

        # 初始化
        np.random.seed(42)
        random.seed(42)

        strategies = np.random.choice([0, 1], size=(N_SIDE, N_SIDE), p=[0.5, 0.5])
        reputations = np.random.uniform(0, 20, size=(N_SIDE, N_SIDE))

        # 存储快照
        strategy_snapshots = {}
        reputation_snapshots = {}
        payoff_snapshots = {}
        performance_snapshots = {}
        coop_rate_snapshots = {}

        for t in range(iterations + 1):
            # 计算当前时间点的评分和收益
            performance_scores = calculate_performance_scores(
                strategies, reputations, network, None
            )
            payoffs = calculate_total_payoffs(
                strategies, performance_scores, a, r, network, None
            )

            # 在指定时间点记录快照
            if t in SNAPSHOT_TIMES:
                strategy_snapshots[t] = strategies.copy()
                reputation_snapshots[t] = reputations.copy()
                payoff_snapshots[t] = payoffs.copy()
                performance_snapshots[t] = performance_scores.copy()
                coop_rate_snapshots[t] = np.mean(strategies)

                print(
                    f"    T={t}: 合作率={coop_rate_snapshots[t]:.3f}, "
                    f"平均声誉={np.mean(reputations):.2f}, "
                    f"平均收益={np.mean(payoffs):.2f}, "
                    f"平均评分={np.mean(performance_scores):.3f}"
                )

            if t < iterations:
                new_strategies = np.zeros_like(strategies)
                for i in range(N_SIDE):
                    for j in range(N_SIDE):
                        new_strategies[i, j] = update_strategy(
                            (i, j), strategies, payoffs, reputations,
                            network, None, 0.1, beta_val
                        )

                reputations = update_reputations(reputations, performance_scores)
                strategies = new_strategies

        snapshots_data[a] = {
            'strategy': strategy_snapshots,
            'reputation': reputation_snapshots,
            'payoff': payoff_snapshots,
            'performance': performance_snapshots,
            'coop_rate': coop_rate_snapshots
        }

        elapsed = time.time() - start
        print(f"    完成，耗时{elapsed:.1f}s")

    # 保存数据
    save_dict = {
        'a_values': a_list,
        'snapshot_times': SNAPSHOT_TIMES,
        'r': r,
        'beta': beta_val
    }

    for a in a_list:
        for t in SNAPSHOT_TIMES:
            if t in snapshots_data[a]['strategy']:
                save_dict[f'a_{a}_t_{t}_strategy'] = snapshots_data[a]['strategy'][t]
                save_dict[f'a_{a}_t_{t}_reputation'] = snapshots_data[a]['reputation'][t]
                save_dict[f'a_{a}_t_{t}_payoff'] = snapshots_data[a]['payoff'][t]
                save_dict[f'a_{a}_t_{t}_performance'] = snapshots_data[a]['performance'][t]
                save_dict[f'a_{a}_t_{t}_coop_rate'] = snapshots_data[a]['coop_rate'][t]

    np.savez('fig7_data.npz', **save_dict)
    print("✓ fig7_data.npz 已保存")


# ======================
# 图8：不同β值下评分分布快照（β=0.0,0.25,0.5,0.75,1.0, r=3.0, a=0.8）
# ======================
def compute_figure8_data():
    """计算图8数据：不同β值下策略、声誉、收益、评分的空间分布快照"""
    print("=" * 60)
    print("计算图8数据（不同β值下策略、声誉、收益、评分分布快照）")
    print("=" * 60)

    r = 3.0
    a = 0.7  # 固定a=0.7
    network = NETWORK_GRID

    # 使用全局的 beta_values = [0.0, 0.25, 0.5, 0.75, 1.0]
    beta_list = beta_values

    # 构建邻居缓存
    build_grid_neighbors_cache()

    snapshots_data = {}

    for beta_val in beta_list:
        print(f"  模拟 β={beta_val}...")
        start = time.time()

        # 初始化
        np.random.seed(42)
        random.seed(42)

        strategies = np.random.choice([0, 1], size=(N_SIDE, N_SIDE), p=[0.5, 0.5])
        reputations = np.random.uniform(0, 20, size=(N_SIDE, N_SIDE))

        # 存储快照
        strategy_snapshots = {}
        reputation_snapshots = {}
        payoff_snapshots = {}
        performance_snapshots = {}
        coop_rate_snapshots = {}

        for t in range(iterations + 1):
            # 计算当前时间点的评分和收益
            performance_scores = calculate_performance_scores(
                strategies, reputations, network, None
            )
            payoffs = calculate_total_payoffs(
                strategies, performance_scores, a, r, network, None
            )

            # 在指定时间点记录快照
            if t in SNAPSHOT_TIMES:
                strategy_snapshots[t] = strategies.copy()
                reputation_snapshots[t] = reputations.copy()
                payoff_snapshots[t] = payoffs.copy()
                performance_snapshots[t] = performance_scores.copy()
                coop_rate_snapshots[t] = np.mean(strategies)

                print(
                    f"    T={t}: 合作率={coop_rate_snapshots[t]:.3f}, "
                    f"平均声誉={np.mean(reputations):.2f}, "
                    f"平均收益={np.mean(payoffs):.2f}, "
                    f"平均评分={np.mean(performance_scores):.3f}"
                )

            if t < iterations:
                new_strategies = np.zeros_like(strategies)
                for i in range(N_SIDE):
                    for j in range(N_SIDE):
                        new_strategies[i, j] = update_strategy(
                            (i, j), strategies, payoffs, reputations,
                            network, None, 0.1, beta_val
                        )

                reputations = update_reputations(reputations, performance_scores)
                strategies = new_strategies

        snapshots_data[beta_val] = {
            'strategy': strategy_snapshots,
            'reputation': reputation_snapshots,
            'payoff': payoff_snapshots,
            'performance': performance_snapshots,
            'coop_rate': coop_rate_snapshots
        }

        elapsed = time.time() - start
        print(f"    完成，耗时{elapsed:.1f}s")

    # 保存数据
    save_dict = {
        'beta_values': beta_list,
        'snapshot_times': SNAPSHOT_TIMES,
        'r': r,
        'a': a
    }

    for beta_val in beta_list:
        for t in SNAPSHOT_TIMES:
            if t in snapshots_data[beta_val]['strategy']:
                save_dict[f'beta_{beta_val}_t_{t}_strategy'] = snapshots_data[beta_val]['strategy'][t]
                save_dict[f'beta_{beta_val}_t_{t}_reputation'] = snapshots_data[beta_val]['reputation'][t]
                save_dict[f'beta_{beta_val}_t_{t}_payoff'] = snapshots_data[beta_val]['payoff'][t]
                save_dict[f'beta_{beta_val}_t_{t}_performance'] = snapshots_data[beta_val]['performance'][t]
                save_dict[f'beta_{beta_val}_t_{t}_coop_rate'] = snapshots_data[beta_val]['coop_rate'][t]

    np.savez('fig8_data.npz', **save_dict)
    print("✓ fig8_data.npz 已保存")


# ======================
# 图9：固定参数下策略、声誉、收益、评分分布快照（a=0.7, β=0.25, r=3.0）
# ======================
def compute_figure9_data():
    """计算图9数据：固定参数下策略、声誉、收益、评分的空间分布快照（一幅图）"""
    print("=" * 60)
    print("计算图9数据（a=0.95, β=0.6, r=3.0）")
    print("=" * 60)

    a = 0.95
    r = 3.0
    beta_val = 0.6
    network = NETWORK_GRID

    # 构建邻居缓存
    build_grid_neighbors_cache()

    # 初始化
    np.random.seed(42)
    random.seed(42)

    strategies = np.random.choice([0, 1], size=(N_SIDE, N_SIDE), p=[0.5, 0.5])
    reputations = np.random.uniform(0, 20, size=(N_SIDE, N_SIDE))

    # 存储快照
    strategy_snapshots = {}
    reputation_snapshots = {}
    payoff_snapshots = {}
    performance_snapshots = {}
    coop_rate_snapshots = {}

    for t in range(iterations + 1):
        # 计算当前时间点的评分和收益
        performance_scores = calculate_performance_scores(
            strategies, reputations, network, None
        )
        payoffs = calculate_total_payoffs(
            strategies, performance_scores, a, r, network, None
        )

        # 在指定时间点记录快照
        if t in SNAPSHOT_TIMES:
            strategy_snapshots[t] = strategies.copy()
            reputation_snapshots[t] = reputations.copy()
            payoff_snapshots[t] = payoffs.copy()
            performance_snapshots[t] = performance_scores.copy()
            coop_rate_snapshots[t] = np.mean(strategies)

            print(
                f"    T={t}: 合作率={coop_rate_snapshots[t]:.3f}, "
                f"平均声誉={np.mean(reputations):.2f}, "
                f"平均收益={np.mean(payoffs):.2f}, "
                f"平均评分={np.mean(performance_scores):.3f}"
            )

        if t < iterations:
            new_strategies = np.zeros_like(strategies)
            for i in range(N_SIDE):
                for j in range(N_SIDE):
                    new_strategies[i, j] = update_strategy(
                        (i, j), strategies, payoffs, reputations,
                        network, None, 0.1, beta_val
                    )

            reputations = update_reputations(reputations, performance_scores)
            strategies = new_strategies

    # 保存数据
    save_dict = {
        'a': a,
        'r': r,
        'beta': beta_val,
        'snapshot_times': SNAPSHOT_TIMES
    }

    for t in SNAPSHOT_TIMES:
        if t in strategy_snapshots:
            save_dict[f't_{t}_strategy'] = strategy_snapshots[t]
            save_dict[f't_{t}_reputation'] = reputation_snapshots[t]
            save_dict[f't_{t}_payoff'] = payoff_snapshots[t]
            save_dict[f't_{t}_performance'] = performance_snapshots[t]
            save_dict[f't_{t}_coop_rate'] = coop_rate_snapshots[t]

    np.savez('fig9_data2_a95beta0.6.npz', **save_dict)
    print("✓ fig9_data2_a7beta65.npz 已保存")


# 在主函数的main()中添加调用：



# ======================
# 主程序
# ======================
def main():
    """主函数：执行所有绘图"""
    print("=" * 60)
    print("声誉机制公共品博弈模拟（无折扣版本）")
    print("=" * 60)

    # 预生成网络缓存
    build_small_world_enhanced()
    build_grid_neighbors_cache()

    total_start = time.time()

    # 执行所有数据计算
    # compute_figure1_data()
    # compute_figure2_data()
    # compute_figure4_data()
    # compute_figure5_data()
    # compute_figure6_data()
    # compute_figure7_data()
    # compute_figure8_data()
    compute_figure9_data()

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 60)
    print(f"全部完成！总耗时: {total_elapsed / 60:.1f} 分钟")
    print("=" * 60)


if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()
    main()