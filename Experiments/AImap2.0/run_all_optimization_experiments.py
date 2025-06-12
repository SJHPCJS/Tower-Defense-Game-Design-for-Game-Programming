#!/usr/bin/env python3
"""
运行所有路径优化实验的脚本
Run all path optimization experiments and compare results
"""

import os
import sys
import time
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def run_experiment_script(script_name):
    """运行单个实验脚本"""
    print(f"\n{'='*50}")
    print(f"运行实验: {script_name}")
    print(f"{'='*50}")
    
    try:
        start_time = time.time()
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"✅ {script_name} 成功完成，用时 {duration:.2f} 秒")
            print("输出:")
            print(result.stdout)
        else:
            print(f"❌ {script_name} 运行失败")
            print("错误输出:")
            print(result.stderr)
            
        return result.returncode == 0, duration
        
    except Exception as e:
        print(f"❌ 运行 {script_name} 时发生异常: {e}")
        return False, 0

def load_results(algorithm_name):
    """加载算法的实验结果"""
    results = {}
    for strategy in ['optimal', 'reasonable']:
        csv_file = f"{algorithm_name}_optimization_{strategy}_results.csv"
        if os.path.exists(csv_file):
            try:
                df = pd.read_csv(csv_file)
                results[strategy] = df
            except Exception as e:
                print(f"警告: 无法加载 {csv_file}: {e}")
        else:
            print(f"警告: 文件不存在 {csv_file}")
    return results

def create_comparison_charts():
    """创建算法间的对比图表"""
    print("\n创建算法对比图表...")
    
    algorithms = ['tower_path', 'maze_loops', 'prim_loops']
    algorithm_names = ['Tower Path', 'Maze Loops', 'Prim Loops']
    strategies = ['optimal', 'reasonable']
    
    # 收集所有数据
    all_data = {}
    for algo in algorithms:
        all_data[algo] = load_results(algo)
    
    # 为每个策略创建对比图
    for strategy in strategies:
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'算法对比 - {strategy.title()} Strategy', fontsize=16)
        
        # 数据收集
        algo_results = {}
        for algo in algorithms:
            if strategy in all_data[algo]:
                df = all_data[algo][strategy]
                if not df.empty:
                    algo_results[algo] = df
        
        if not algo_results:
            print(f"没有找到 {strategy} 策略的有效数据")
            plt.close(fig)
            continue
        
        # Chart 1: 平均路径瓦片数对比
        ax1 = axes[0, 0]
        original_data = []
        optimized_data = []
        labels = []
        
        for algo in algorithms:
            if algo in algo_results:
                df = algo_results[algo]
                original_row = df[df['Algorithm'] == 'Original']
                optimized_row = df[df['Algorithm'] == 'Optimized']
                
                if not original_row.empty and not optimized_row.empty:
                    original_data.append(original_row['Avg Path Tiles'].iloc[0])
                    optimized_data.append(optimized_row['Avg Path Tiles'].iloc[0])
                    labels.append(algorithm_names[algorithms.index(algo)])
        
        if original_data and optimized_data:
            x = np.arange(len(labels))
            width = 0.35
            
            bars1 = ax1.bar(x - width/2, original_data, width, label='Original', alpha=0.8, color='lightcoral')
            bars2 = ax1.bar(x + width/2, optimized_data, width, label='Optimized', alpha=0.8, color='lightblue')
            
            ax1.set_xlabel('算法')
            ax1.set_ylabel('平均路径瓦片数')
            ax1.set_title('平均路径瓦片数对比')
            ax1.set_xticks(x)
            ax1.set_xticklabels(labels)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 添加数值标签
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax1.annotate(f'{height:.1f}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),  # 3 points vertical offset
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)
        
        # Chart 2: 分支点数对比
        ax2 = axes[0, 1]
        original_branches = []
        optimized_branches = []
        
        for algo in algorithms:
            if algo in algo_results:
                df = algo_results[algo]
                original_row = df[df['Algorithm'] == 'Original']
                optimized_row = df[df['Algorithm'] == 'Optimized']
                
                if not original_row.empty and not optimized_row.empty:
                    original_branches.append(original_row['Avg Branch Points'].iloc[0])
                    optimized_branches.append(optimized_row['Avg Branch Points'].iloc[0])
        
        if original_branches and optimized_branches:
            x = np.arange(len(labels))
            bars1 = ax2.bar(x - width/2, original_branches, width, label='Original', alpha=0.8, color='lightgreen')
            bars2 = ax2.bar(x + width/2, optimized_branches, width, label='Optimized', alpha=0.8, color='orange')
            
            ax2.set_xlabel('算法')
            ax2.set_ylabel('平均分支点数')
            ax2.set_title('平均分支点数对比')
            ax2.set_xticks(x)
            ax2.set_xticklabels(labels)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax2.annotate(f'{height:.1f}',
                               xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3),
                               textcoords="offset points",
                               ha='center', va='bottom', fontsize=8)
        
        # Chart 3: 清理的瓦片数对比
        ax3 = axes[1, 0]
        cleaned_data = []
        
        for algo in algorithms:
            if algo in algo_results:
                df = algo_results[algo]
                optimized_row = df[df['Algorithm'] == 'Optimized']
                
                if not optimized_row.empty:
                    cleaned_data.append(optimized_row['Avg Cleaned Tiles'].iloc[0])
        
        if cleaned_data:
            bars = ax3.bar(labels, cleaned_data, alpha=0.8, color='purple')
            ax3.set_xlabel('算法')
            ax3.set_ylabel('平均清理瓦片数')
            ax3.set_title('平均清理瓦片数对比')
            ax3.grid(True, alpha=0.3)
            
            for bar in bars:
                height = bar.get_height()
                ax3.annotate(f'{height:.1f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8)
        
        # Chart 4: 优化效果 (减少百分比)
        ax4 = axes[1, 1]
        reduction_percentages = []
        
        for algo in algorithms:
            if algo in algo_results:
                df = algo_results[algo]
                original_row = df[df['Algorithm'] == 'Original']
                optimized_row = df[df['Algorithm'] == 'Optimized']
                
                if not original_row.empty and not optimized_row.empty:
                    original_tiles = original_row['Avg Path Tiles'].iloc[0]
                    optimized_tiles = optimized_row['Avg Path Tiles'].iloc[0]
                    reduction_pct = ((original_tiles - optimized_tiles) / original_tiles) * 100
                    reduction_percentages.append(reduction_pct)
        
        if reduction_percentages:
            bars = ax4.bar(labels, reduction_percentages, alpha=0.8, color='gold')
            ax4.set_xlabel('算法')
            ax4.set_ylabel('路径瓦片减少百分比 (%)')
            ax4.set_title('优化效果对比')
            ax4.grid(True, alpha=0.3)
            
            for bar in bars:
                height = bar.get_height()
                ax4.annotate(f'{height:.1f}%',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        # 保存图表
        chart_path = os.path.join("figures", f"algorithm_comparison_{strategy}.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"保存对比图表: {chart_path}")

def main():
    """主函数"""
    print("开始运行所有路径优化实验...")
    print(f"当前工作目录: {os.getcwd()}")
    
    # 确保在正确的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 实验脚本列表
    experiments = [
        "e_tower_path_optimization_correct.py",
        "e_maze_loops_optimization_correct.py", 
        "e_prim_loops_optimization_correct.py"
    ]
    
    # 运行所有实验
    results = {}
    total_start_time = time.time()
    
    for script in experiments:
        if os.path.exists(script):
            success, duration = run_experiment_script(script)
            results[script] = {'success': success, 'duration': duration}
        else:
            print(f"⚠️  脚本文件不存在: {script}")
            results[script] = {'success': False, 'duration': 0}
    
    total_duration = time.time() - total_start_time
    
    # 输出总结
    print(f"\n{'='*50}")
    print("实验总结")
    print(f"{'='*50}")
    
    successful_experiments = 0
    for script, result in results.items():
        status = "✅ 成功" if result['success'] else "❌ 失败"
        print(f"{script}: {status} (用时: {result['duration']:.2f}s)")
        if result['success']:
            successful_experiments += 1
    
    print(f"\n成功完成的实验: {successful_experiments}/{len(experiments)}")
    print(f"总用时: {total_duration:.2f} 秒")
    
    # 如果有成功的实验，创建对比图表
    if successful_experiments > 1:
        try:
            create_comparison_charts()
            print("\n✅ 算法对比图表已生成")
        except Exception as e:
            print(f"\n❌ 生成对比图表时出错: {e}")
    
    print(f"\n实验完成！查看各个算法的结果文件和图表。")

if __name__ == "__main__":
    main() 