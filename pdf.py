import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ======================
# 图1：不同分配系数a下合作频率/平均声誉 vs r
# ======================
def plot_figure1_from_data(fig1_file='fig1_data.npz'):
    """图1：不同分配系数a下合作频率/平均声誉 vs 增强因子r"""
    data = np.load(fig1_file)

    r_values = data['r']
    coop_matrix = data['coop']  # shape: (len(a_values), len(r_values))
    rep_matrix = data['rep']
    a_values = data['a_values']

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    # 左图：合作频率
    for idx, a in enumerate(a_values):
        axes[0].plot(r_values, coop_matrix[idx], 'o-', linewidth=2, markersize=8,
                     color=colors[idx], label=f'$α$={a}')
    axes[0].set_xlabel('$r$', fontsize=22)
    axes[0].set_ylabel(r'$f_c$', fontsize=22)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=13, frameon=False)
    axes[0].set_xlim(0.875, 5.125)
    axes[0].set_ylim(-0.05, 1.05)
    axes[0].tick_params(axis='both', labelsize=17)  # 同时放大x轴和y轴刻度数字

    # 添加子图标签到下方
    axes[0].text(0.5, -0.18, '(a)',
                 transform=axes[0].transAxes, fontsize=19,
                 fontweight='bold', ha='center')

    # 右图：平均声誉
    for idx, a in enumerate(a_values):
        axes[1].plot(r_values, rep_matrix[idx], '*-', linewidth=2, markersize=12,
                     color=colors[idx], label=f'$α$={a}')
    axes[1].set_xlabel('$r$', fontsize=22)
    axes[1].set_ylabel(r'$\bar{R}$', fontsize=22)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=13, frameon=False)
    axes[1].set_xlim(0.875, 5.125)
    axes[1].set_ylim(-1, 21)
    axes[1].tick_params(axis='both', labelsize=17)  # 同时放大x轴和y轴刻度数字

    # 添加子图标签到下方
    axes[1].text(0.5, -0.18, '(b)' ,
                 transform=axes[1].transAxes, fontsize=19,
                 fontweight='bold', ha='center')

    # 调整底部边距，为下方标签留出空间
    plt.subplots_adjust(bottom=0.12, wspace=0.2)

    # plt.suptitle('图1：不同分配系数a下合作频率和平均声誉随增强因子r的变化\n(β=0.5, 规则格点网络)',
    #              fontsize=16, y=1.02)
    plt.tight_layout()#自动优化布局使子图紧贴
    plt.savefig('fig1_from_data.pdf', dpi=600, bbox_inches='tight', format='pdf')
    plt.show()
    print("✓ 图1已保存为 'fig1_from_data.pdf'")


# ======================
# 图2：不同β下合作频率/平均声誉 vs r
# ======================
def plot_figure2_from_data(fig2_file='fig2_data.npz'):
    """图2：不同β下合作频率/平均声誉 vs 增强因子r (a=0.8固定)"""
    data = np.load(fig2_file)

    r_values = data['r']
    coop_matrix = data['coop']  # shape: (len(beta_values), len(r_values))
    rep_matrix = data['rep']
    beta_values = data['beta_values']

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    # 左图：合作频率
    for idx, beta_val in enumerate(beta_values):
        axes[0].plot(r_values, coop_matrix[idx], 'o-', linewidth=2, markersize=8,
                     color=colors[idx], label=f'$β$={beta_val}')
    axes[0].set_xlabel('$r$', fontsize=22)
    axes[0].set_ylabel(r'$f_c$', fontsize=22)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(fontsize=13, frameon=False)
    axes[0].set_xlim(0.875, 4.625)
    axes[0].set_ylim(-0.05, 1.05)
    axes[0].tick_params(axis='both', labelsize=17)  # 同时放大x轴和y轴刻度数字

    # 添加子图标签到下方 - (a) f_c
    axes[0].text(0.5, -0.18, '(a)', transform=axes[0].transAxes,
                 fontsize=19, fontweight='bold', ha='center')

    # 右图：平均声誉
    for idx, beta_val in enumerate(beta_values):
        axes[1].plot(r_values, rep_matrix[idx], '*-', linewidth=2, markersize=12,
                     color=colors[idx], label=f'$β$={beta_val}')
    axes[1].set_xlabel('$r$', fontsize=22)
    axes[1].set_ylabel(r'$\bar{R}$', fontsize=22)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(fontsize=13, frameon=False)
    axes[1].set_xlim(0.875, 4.625)
    axes[1].set_ylim(-1, 21)
    axes[1].tick_params(axis='both', labelsize=17) # 同时放大x轴和y轴刻度数字

    # 添加子图标签到下方
    axes[1].text(0.5, -0.18, '(b) ', transform=axes[1].transAxes,
                 fontsize=19, fontweight='bold', ha='center')

    # 调整底部边距，为下方标签留出空间
    plt.subplots_adjust(bottom=0.12)

    # plt.suptitle('图2：不同声誉影响系数β下合作频率和平均声誉随增强因子r的变化\n(a=0.8, 规则格点网络)',
    #              fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig('fig2_from_data.pdf', dpi=600, bbox_inches='tight', format='pdf')
    plt.show()
    print("✓ 图2已保存为 'fig2_from_data.pdf'")


# ======================
# 图5：网络结构对比（从fig5_data.npz）
# ======================
def plot_figure5_from_data(fig5_file='fig5_data.npz'):
    """图5：规则格子vs小世界网络下不同a值随时间演化的合作频率/平均声誉"""
    data = np.load(fig5_file)

    grid_coop = data['grid_coop']
    grid_rep = data['grid_rep']
    sw_coop = data['sw_coop']
    sw_rep = data['sw_rep']
    a_values = data['a_values']

    # 刻度设置
    x_tick_positions = [1, 10, 100, 1000, 3000]  # 添加替换后的小值位置
    x_tick_labels = [r'$10^0$', r'$10^1$', r'$10^2$', r'$10^3$', '']

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

    network_names = ['$SL$', '$WS$']
    coop_data_list = [grid_coop, sw_coop]
    rep_data_list = [grid_rep, sw_rep]

    subplot_labels = ['(a)', '(b)', '(c)', '(d)']

    label_idx = 0
    for net_idx, (coop_data, rep_data) in enumerate(zip(coop_data_list, rep_data_list)):
        # 左列：合作频率
        ax_left = axes[net_idx, 0]
        for idx, a in enumerate(a_values):
            mean_hist = coop_data[idx]
            plot_steps = min(3000, len(mean_hist))
            x_data = np.arange(plot_steps)
            ax_left.plot(x_data, mean_hist[:plot_steps], linewidth=2.5,
                         color=colors[idx], label=f'$α$={a}')

        # 使用对数坐标，去掉网格
        ax_left.set_xscale('log')
        ax_left.set_xticks(x_tick_positions)
        ax_left.set_xticklabels(x_tick_labels)
        ax_left.set_xlabel('$T$', fontsize=16)
        ax_left.set_ylabel(r'$f_c$', fontsize=16)
        ax_left.tick_params(axis='both', labelsize=15)
        ax_left.grid(False)  # 关闭网格
        ax_left.legend(fontsize=11, frameon=False, loc='center right')
        ax_left.set_xlim(6e-1, 3000)
        ax_left.set_ylim(-0.05, 1.05)

        ax_left.text(0.5, -0.25, f'{subplot_labels[label_idx]} {network_names[net_idx]}',
                     transform=ax_left.transAxes, fontsize=16, fontweight='bold', ha='center')
        label_idx += 1

        # 右列：平均声誉
        ax_right = axes[net_idx, 1]
        for idx, a in enumerate(a_values):
            mean_hist = rep_data[idx]
            plot_steps = min(3000, len(mean_hist))
            x_data = np.arange(plot_steps)
            ax_right.plot(x_data, mean_hist[:plot_steps], linewidth=2.5,
                          color=colors[idx], label=f'$α$={a}')

        # 使用对数坐标，去掉网格
        ax_right.set_xscale('log')
        ax_right.set_xticks(x_tick_positions)
        ax_right.set_xticklabels(x_tick_labels)
        ax_right.set_xlabel('$T$', fontsize=16)
        ax_right.set_ylabel(r'$\bar{R}$', fontsize=16)
        ax_right.tick_params(axis='both', labelsize=15)
        ax_right.grid(False)  # 关闭网格
        ax_right.legend(fontsize=11, frameon=False, loc='center right')
        ax_right.set_xlim(6e-1, 3000)
        ax_right.set_ylim(-1, 21)

        ax_right.text(0.5, -0.25, f'{subplot_labels[label_idx]} {network_names[net_idx]}',
                      transform=ax_right.transAxes, fontsize=16, fontweight='bold', ha='center')
        label_idx += 1

    plt.subplots_adjust(left=0.5, right=0.95, top=1, bottom=0.12,
                        hspace=0.35, wspace=0.3)
    plt.tight_layout()
    plt.savefig('fig5_from_data.pdf', dpi=600, bbox_inches='tight', format='pdf')
    plt.show()
    print("✓ 图5已保存为 'fig5_from_data.pdf'")


# ======================
# 图6：a-β参数空间热力图（从fig6_data.npz）
# ======================
def plot_figure6_from_data(fig6_file='fig6_data.npz'):
    """图6：a-β参数空间合作频率和平均声誉热力图 - 双图风格"""
    data = np.load(fig6_file)

    coop_data = data['coop']  # shape: (len(beta_values), len(a_values))
    rep_data = data['rep']
    a_values = data['a_values']
    beta_values = data['beta_values']

    # 创建左右两个子图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

    # 左图：合作频率热力图
    im1 = ax1.imshow(coop_data, cmap='jet', interpolation='spline16',
                     aspect='auto', origin='lower',
                     extent=[a_values.min(), a_values.max(),
                             beta_values.min(), beta_values.max()])
    ax1.set_xlabel('$α$', fontsize=23)
    ax1.set_ylabel('$β$', fontsize=23)
    a_ticks = np.linspace(a_values.min(), a_values.max(), 6)
    beta_ticks = np.linspace(beta_values.min(), beta_values.max(), 6)
    ax1.set_xticks(a_ticks)
    ax1.set_yticks(beta_ticks)
    ax1.tick_params(labelsize=20)
    ax1.grid(False)

    # 添加子图标签到下方 - (a) f_c
    ax1.text(0.5, -0.20, '(a)', transform=ax1.transAxes,
             fontsize=24, fontweight='bold', ha='center')

    # 左图颜色条
    cbar1 = plt.colorbar(im1, ax=ax1)
    cbar1.ax.tick_params(labelsize=20)
    cbar1.set_label(r'$f_c$', fontsize=24)

    # 右图：平均声誉热力图
    im2 = ax2.imshow(rep_data, cmap='jet', interpolation='spline16',
                     aspect='auto', origin='lower',
                     extent=[a_values.min(), a_values.max(),
                             beta_values.min(), beta_values.max()])
    ax2.set_xlabel('$α$', fontsize=25)
    ax2.set_ylabel('$β$', fontsize=25)
    ax2.set_xticks(a_ticks)
    ax2.set_yticks(beta_ticks)
    ax2.tick_params(labelsize=20)
    ax2.grid(False)

    # 添加子图标签到下方 - (b) \bar{R}
    ax2.text(0.5, -0.20, '(b)', transform=ax2.transAxes,
             fontsize=24, fontweight='bold', ha='center')

    # 右图颜色条
    cbar2 = plt.colorbar(im2, ax=ax2)
    cbar2.ax.tick_params(labelsize=20)
    cbar2.set_label(r'$\bar{R}$', fontsize=24)

    # 调整底部边距，为下方标签留出空间
    plt.subplots_adjust(bottom=0.12)

    # plt.suptitle(f'图6：a-β参数空间热力图 (r=3, 规则格点网络)',
    #              fontsize=28, y=1.05)
    plt.tight_layout()
    plt.savefig('fig6_both_heatmap_style.pdf', dpi=600, bbox_inches='tight', format='pdf')
    plt.show()
    print("✓ 图6双图已保存为 'fig6_both_heatmap_style.pdf'")


def plot_figure8_from_data(fig9_file='fig9_data2_a75beta0.6.npz'):
    """图8：固定参数下策略、声誉、收益、评分空间分布快照（放在一幅图中，每行独立颜色条）"""
    print("\n" + "=" * 60)
    print("绘制图8：固定参数下策略、声誉、收益、评分空间分布快照")
    print("=" * 60)

    data = np.load(fig9_file, allow_pickle=True)
    snapshot_times = data['snapshot_times']
    a = float(data['a'])
    r = float(data['r'])
    beta = float(data['beta'])

    print(f"参数: a={a}, r={r}, β={beta}")
    print(f"快照时间点: {snapshot_times}")

    n_times = len(snapshot_times)  # 4列
    n_rows = 4  # 4行：策略、声誉、收益、评分

    # 创建一幅大图，4行×4列
    fig, axes = plt.subplots(n_rows, n_times, figsize=(3.5 * n_times, 3.5 * n_rows))

    # 确保axes是2D数组
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    if n_times == 1:
        axes = axes.reshape(-1, 1)

    # 颜色映射
    strategy_cmap = ListedColormap(['darkblue', 'white'])  # 深蓝=背叛(0), 白=合作(1)
    reputation_cmap = plt.cm.viridis
    payoff_cmap = plt.cm.RdYlBu_r
    performance_cmap = plt.cm.coolwarm  # 评分用发散色，范围[-1,1]

    # 为每行单独计算颜色范围
    # 声誉范围固定为0-20
    rep_min, rep_max = 0, 20

    # 收益范围固定为0-15
    payoff_min, payoff_max = 0, 15

    # 评分范围固定为[-1, 1]
    perf_min, perf_max = -1, 1

    # 存储每行的图像对象用于颜色条
    im_rep = None
    im_pay = None
    im_perf = None

    for row in range(n_rows):
        for col, t in enumerate(snapshot_times):
            ax = axes[row, col]

            if row == 0:  # 策略
                strat_key = f't_{t}_strategy'
                if strat_key in data:
                    strategy = data[strat_key]
                    ax.imshow(strategy, cmap=strategy_cmap, vmin=0, vmax=1)
                    ax.set_title(f'T={t}', fontsize=11)
                ax.set_xticks([])
                ax.set_yticks([])

            elif row == 1:  # 声誉
                rep_key = f't_{t}_reputation'
                if rep_key in data:
                    reputation = data[rep_key]
                    im_rep = ax.imshow(reputation, cmap=reputation_cmap, vmin=rep_min, vmax=rep_max)
                    ax.set_title(f'T={t}', fontsize=11)
                ax.set_xticks([])
                ax.set_yticks([])

            elif row == 2:  # 收益
                payoff_key = f't_{t}_payoff'
                if payoff_key in data:
                    payoff = data[payoff_key]
                    # 将收益值限制在0-15范围内显示（超出部分显示为边界颜色）
                    im_pay = ax.imshow(payoff, cmap=payoff_cmap, vmin=payoff_min, vmax=payoff_max)
                    ax.set_title(f'T={t}', fontsize=11)
                ax.set_xticks([])
                ax.set_yticks([])

            else:  # row == 3, 评分
                perf_key = f't_{t}_performance'
                if perf_key in data:
                    performance = data[perf_key]
                    im_perf = ax.imshow(performance, cmap=performance_cmap, vmin=perf_min, vmax=perf_max)
                    ax.set_title(f'T={t}', fontsize=11)
                ax.set_xticks([])
                ax.set_yticks([])

    # 添加总标题
    # plt.suptitle(f'图8：策略、声誉、收益、评分空间分布演化快照\n(a={a}, r={r}, β={beta})',
    #              fontsize=16, y=1.02)

    # 调整布局（为颜色条留出空间）
    plt.tight_layout()
    plt.subplots_adjust(left=0.10, right=0.88, top=0.92, bottom=0.05, hspace=0.25, wspace=0.2)

    # ========== 为每行添加独立的颜色条 ==========
    # 策略图不需要颜色条（离散值）

    # 声誉行（第2行）的颜色条
    if im_rep is not None:
        ax_last_rep = axes[1, -1]
        bbox = ax_last_rep.get_position()
        cax_rep = fig.add_axes([bbox.x1 + 0.01, bbox.y0, 0.015, bbox.height])
        cbar_rep = plt.colorbar(im_rep, cax=cax_rep)
        cbar_rep.set_label('Reputation', fontsize=12)
        cbar_rep.ax.tick_params(labelsize=8)

    # 收益行（第3行）的颜色条
    if im_pay is not None:
        ax_last_pay = axes[2, -1]
        bbox = ax_last_pay.get_position()
        cax_pay = fig.add_axes([bbox.x1 + 0.01, bbox.y0, 0.015, bbox.height])
        cbar_pay = plt.colorbar(im_pay, cax=cax_pay)
        cbar_pay.set_label('Payoff', fontsize=12)
        cbar_pay.ax.tick_params(labelsize=8)
        # 设置颜色条的刻度范围为0-15
        cbar_pay.set_ticks([0, 5, 10, 15])

    # 评分行（第4行）的颜色条
    if im_perf is not None:
        ax_last_perf = axes[3, -1]
        bbox = ax_last_perf.get_position()
        cax_perf = fig.add_axes([bbox.x1 + 0.01, bbox.y0, 0.015, bbox.height])
        cbar_perf = plt.colorbar(im_perf, cax=cax_perf)
        cbar_perf.set_label('Performance', fontsize=12)
        cbar_perf.ax.tick_params(labelsize=8)

    # plt.savefig('fig8_all_snapshots.pdf', dpi=600, bbox_inches='tight', format='pdf')
    plt.savefig('fig5.png', dpi=300, bbox_inches='tight')
    plt.show()
    plt.close(fig)

    print("✓ 图8已保存为 'fig8_all_snapshots.pdf'")



def plot_figure9_from_data(fig9_file='fig9_data2_a0.95beta0.6.npz'):
    """图9：固定参数下策略、声誉、收益、评分空间分布快照（放在一幅图中，每行独立颜色条）"""
    print("\n" + "=" * 60)
    print("绘制图9：固定参数下策略、声誉、收益、评分空间分布快照")
    print("=" * 60)

    data = np.load(fig9_file, allow_pickle=True)
    snapshot_times = data['snapshot_times']
    a = float(data['a'])
    r = float(data['r'])
    beta = float(data['beta'])

    print(f"参数: a={a}, r={r}, β={beta}")
    print(f"快照时间点: {snapshot_times}")

    n_times = len(snapshot_times)  # 4列
    n_rows = 4  # 4行：策略、声誉、收益、评分

    # 创建一幅大图，4行×4列
    fig, axes = plt.subplots(n_rows, n_times, figsize=(3.5 * n_times, 3.5 * n_rows))

    # 确保axes是2D数组
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    if n_times == 1:
        axes = axes.reshape(-1, 1)

    # 颜色映射
    strategy_cmap = ListedColormap(['darkblue', 'white'])  # 深蓝=背叛(0), 白=合作(1)
    reputation_cmap = plt.cm.viridis
    payoff_cmap = plt.cm.RdYlBu_r
    performance_cmap = plt.cm.coolwarm  # 评分用发散色，范围[-1,1]

    # 为每行单独计算颜色范围
    # 声誉范围固定为0-20
    rep_min, rep_max = 0, 20

    # 收益范围固定为0-15
    payoff_min, payoff_max = 0, 15

    # 评分范围固定为[-1, 1]
    perf_min, perf_max = -1, 1

    # 存储每行的图像对象用于颜色条
    im_rep = None
    im_pay = None
    im_perf = None

    for row in range(n_rows):
        for col, t in enumerate(snapshot_times):
            ax = axes[row, col]

            if row == 0:  # 策略
                strat_key = f't_{t}_strategy'
                if strat_key in data:
                    strategy = data[strat_key]
                    ax.imshow(strategy, cmap=strategy_cmap, vmin=0, vmax=1)
                    ax.set_title(f'T={t}', fontsize=11)
                ax.set_xticks([])
                ax.set_yticks([])

            elif row == 1:  # 声誉
                rep_key = f't_{t}_reputation'
                if rep_key in data:
                    reputation = data[rep_key]
                    im_rep = ax.imshow(reputation, cmap=reputation_cmap, vmin=rep_min, vmax=rep_max)
                    ax.set_title(f'T={t}', fontsize=11)
                ax.set_xticks([])
                ax.set_yticks([])

            elif row == 2:  # 收益
                payoff_key = f't_{t}_payoff'
                if payoff_key in data:
                    payoff = data[payoff_key]
                    # 将收益值限制在0-15范围内显示（超出部分显示为边界颜色）
                    im_pay = ax.imshow(payoff, cmap=payoff_cmap, vmin=payoff_min, vmax=payoff_max)
                    ax.set_title(f'T={t}', fontsize=11)
                ax.set_xticks([])
                ax.set_yticks([])

            else:  # row == 3, 评分
                perf_key = f't_{t}_performance'
                if perf_key in data:
                    performance = data[perf_key]
                    im_perf = ax.imshow(performance, cmap=performance_cmap, vmin=perf_min, vmax=perf_max)
                    ax.set_title(f'T={t}', fontsize=11)
                ax.set_xticks([])
                ax.set_yticks([])

    # 添加总标题
    # plt.suptitle(f'图9：策略、声誉、收益、评分空间分布演化快照\n(a={a}, r={r}, β={beta})',
    #              fontsize=16, y=1.02)

    # 调整布局（为颜色条留出空间）
    plt.tight_layout()
    plt.subplots_adjust(left=0.10, right=0.88, top=0.92, bottom=0.05, hspace=0.25, wspace=0.2)

    # ========== 为每行添加独立的颜色条 ==========
    # 策略图不需要颜色条（离散值）

    # 声誉行（第2行）的颜色条
    if im_rep is not None:
        ax_last_rep = axes[1, -1]
        bbox = ax_last_rep.get_position()
        cax_rep = fig.add_axes([bbox.x1 + 0.01, bbox.y0, 0.015, bbox.height])
        cbar_rep = plt.colorbar(im_rep, cax=cax_rep)
        cbar_rep.set_label('Reputation', fontsize=12)
        cbar_rep.ax.tick_params(labelsize=8)

    # 收益行（第3行）的颜色条
    if im_pay is not None:
        ax_last_pay = axes[2, -1]
        bbox = ax_last_pay.get_position()
        cax_pay = fig.add_axes([bbox.x1 + 0.01, bbox.y0, 0.015, bbox.height])
        cbar_pay = plt.colorbar(im_pay, cax=cax_pay)
        cbar_pay.set_label('Payoff', fontsize=12)
        cbar_pay.ax.tick_params(labelsize=8)
        # 设置颜色条的刻度范围为0-15
        cbar_pay.set_ticks([0, 5, 10, 15])

    # 评分行（第4行）的颜色条
    if im_perf is not None:
        ax_last_perf = axes[3, -1]
        bbox = ax_last_perf.get_position()
        cax_perf = fig.add_axes([bbox.x1 + 0.01, bbox.y0, 0.015, bbox.height])
        cbar_perf = plt.colorbar(im_perf, cax=cax_perf)
        cbar_perf.set_label('Performance', fontsize=12)
        cbar_perf.ax.tick_params(labelsize=8)

    # plt.savefig('fig9_all_snapshots.pdf', dpi=600, bbox_inches='tight', format='pdf')
    plt.savefig('fig6', dpi=300, bbox_inches='tight')
    plt.show()
    plt.close(fig)

    print("✓ 图9已保存为 'fig9_all_snapshots.pdf'")


# ======================
# 主函数：执行所有绘图
# ======================
def main():
    """从保存的.npz文件绘制所有图形"""
    print("=" * 60)
    print("从保存的数据文件绘制图形（无折扣版本）")
    print("=" * 60)

    try:
        plot_figure1_from_data('fig1_data2.npz')
    except FileNotFoundError:
        print("警告: fig1_data.npz 未找到，跳过图1")

    try:
        plot_figure2_from_data('fig2_data2.npz')
    except FileNotFoundError:
        print("警告: fig2_data.npz 未找到，跳过图2")

    try:
        plot_figure5_from_data('fig5_data.npz')
    except FileNotFoundError:
        print("警告: fig5_data.npz 未找到，跳过图5")

    # try:
    #     plot_figure6_from_data('fig6_data.npz')
    # except FileNotFoundError:
    #     print("警告: fig6_data.npz 未找到，跳过图6")

    # try:
    #     plot_figure8_from_data('fig9_data2_a75beta6.npz')
    # except FileNotFoundError:
    #     print("警告: fig9_data2_a75beta6.npz 未找到，跳过图8")
    #
    # try:
    #     plot_figure9_from_data('fig9_data2_a95beta0.6.npz')
    # except FileNotFoundError:
    #     print("警告: fig9_data2_a0.95beta0.6.npz 未找到，跳过图9")

    print("\n" + "=" * 60)
    print("所有可用图形已绘制完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()