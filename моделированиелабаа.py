import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.patches import Rectangle
import warnings
warnings.filterwarnings('ignore')
import time

ENTRY_FEE = 20
initial_banks = [1000, 10000, 1000000] 

def play_one_round():
    tosses = 0
    
    while True:
        tosses += 1
        if random.random() < 0.5: 
            win_amount = 2 ** (tosses - 1)
            return win_amount, tosses

def play_saint_petersburg_game(initial_bank, max_rounds=200000):
    bank = initial_bank
    total_rounds = 0
    total_tosses = 0

    bank_history = [bank]
    rounds_history = [0]

    while bank >= ENTRY_FEE and total_rounds < max_rounds:
        total_rounds += 1
        bank -= ENTRY_FEE

        win_amount, tosses_in_round = play_one_round()
        total_tosses += tosses_in_round
        bank += win_amount

        bank_history.append(bank)
        rounds_history.append(total_rounds)

        if bank > initial_bank:
            stop_reason = "Выход в плюс"
            is_winner = True
            break

    net_profit = bank - initial_bank

    if 'is_winner' not in locals():
        if bank < ENTRY_FEE:
            stop_reason = "Нет денег на ставку"
            is_winner = False
        elif total_rounds >= max_rounds and bank <= initial_bank:
            stop_reason = "Нет денег на ставку (лимит раундов)"
            is_winner = False
        else:
            stop_reason = "Нет денег на ставку"
            is_winner = False
    
    return {
        'final_bank': bank,
        'initial_bank': initial_bank,
        'total_rounds': total_rounds,
        'total_tosses': total_tosses,
        'net_profit': net_profit,
        'bank_history': bank_history,
        'rounds_history': rounds_history,
        'profit_percentage': (net_profit / initial_bank * 100) if initial_bank > 0 else 0,
        'stop_reason': stop_reason,
        'is_winner': is_winner,
        'can_play_again': bank >= ENTRY_FEE
    }

def plot_single_game_dynamics():
    print("Генерация графиков динамики одной игры...")
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    
    examples = []
    
    for initial_bank in initial_banks:
        for _ in range(50):
            result = play_saint_petersburg_game(initial_bank, max_rounds=200000)
            if not result['is_winner']:
                examples.append(('Проигрыш', result))
                break
        
        for _ in range(20):
            result = play_saint_petersburg_game(initial_bank, max_rounds=200000)
            if result['is_winner']:
                examples.append(('Выигрыш', result))
                break
    
    for idx, (result_type, result) in enumerate(examples[:6]):
        row = idx // 3
        col = idx % 3
        
        ax = axes[row, col]
        initial_bank = result['initial_bank']
        
        color = 'green' if result_type == 'Выигрыш' else 'red'
        
        ax.step(result['rounds_history'], result['bank_history'], 
                where='post', linewidth=2, color=color)
        ax.scatter(result['rounds_history'], result['bank_history'], 
                  color='dark' + color, zorder=5, s=20, alpha=0.7)
        
        last_round = result['rounds_history'][-1]
        last_bank = result['bank_history'][-1]
        ax.scatter([last_round], [last_bank], color=color, s=100, zorder=10,
                  edgecolors='black', linewidth=2, marker='s')
        
        ax.axhline(y=initial_bank, color='blue', linestyle='--', alpha=0.7,
                  label=f'Начало: {initial_bank:,} руб')
        
        if result_type == 'Проигрыш':
            ax.axhline(y=ENTRY_FEE, color='red', linestyle=':', alpha=0.6,
                      label=f'Минимум для ставки: {ENTRY_FEE} руб')
        
        ax.set_xlabel('Раунд игры', fontsize=10)
        ax.set_ylabel('Сумма (руб)', fontsize=10)
        
        profit_text = f'{result["net_profit"]:+,.0f} руб ({result["profit_percentage"]:+.1f}%)'
        ax.set_title(f'{result_type}\n'
                    f'Начало: {initial_bank:,} руб → Финал: {result["final_bank"]:,.0f} руб\n'
                    f'Прибыль: {profit_text}\n'
                    f'Раундов: {result["total_rounds"]}',
                    fontsize=9, fontweight='bold', color=color)
        
        ax.grid(True, alpha=0.3)
        
        ax.ticklabel_format(axis='y', style='plain')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        ax.legend(loc='best', fontsize=7)
    
    for i in range(len(examples[:6]), 6):
        row = i // 3
        col = i % 3
        axes[row, col].axis('off')
    
    plt.suptitle('Динамика игр Санкт-Петербургского парадокса\nЗЕЛЁНЫЙ = выигрыш (выход в плюс), КРАСНЫЙ = проигрыш (нет денег на ставку)', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()

def plot_20_players():
    print("\nГенерация графиков для 20 игроков...")
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 15))
    
    all_results = {}
    
    for idx, initial_bank in enumerate(initial_banks):
        ax = axes[idx]
        
        results = []
        final_banks = []
        profits = []
        is_winners = []
        
        print(f"  Моделирование 20 игроков с банком {initial_bank:,} руб...")
        for player in range(20):
            result = play_saint_petersburg_game(initial_bank, max_rounds=200000)
            results.append(result)
            final_banks.append(result['final_bank'])
            profits.append(result['net_profit'])
            is_winners.append(result['is_winner'])
        
        all_results[initial_bank] = results
        
        players = list(range(1, 21))
        
        colors = ['green' if win else 'red' for win in is_winners]
        
        bars = ax.bar(players, final_banks, color=colors, edgecolor='black', alpha=0.8)
        ax.set_ylabel('Сумма (руб)', fontsize=11)
        
        for i, (bar, bank, profit, win) in enumerate(zip(bars, final_banks, profits, is_winners)):
            height = bar.get_height()
            
            if bank >= 1000000:
                bank_text = f'{bank/1000000:.1f}M'
            elif bank >= 1000:
                bank_text = f'{bank/1000:.0f}K'
            else:
                bank_text = f'{bank:,.0f}'
            
            if profit >= 1000000:
                profit_text = f'+{profit/1000000:.1f}M'
            elif profit >= 1000:
                profit_text = f'+{profit/1000:.0f}K'
            elif profit >= 0:
                profit_text = f'+{profit:,.0f}'
            elif profit <= -1000000:
                profit_text = f'{profit/1000000:.1f}M'
            elif profit <= -1000:
                profit_text = f'{profit/1000:.0f}K'
            else:
                profit_text = f'{profit:,.0f}'
            
            text_height = height + max(final_banks) * 0.01
            
            ax.text(bar.get_x() + bar.get_width()/2., text_height,
                   f'{bank_text}\n{profit_text}', 
                   ha='center', va='bottom', 
                   fontsize=7 if initial_bank >= 10000 else 8,
                   bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7))
        
        ax.axhline(y=initial_bank, color='blue', linestyle='--', alpha=0.7,
                  linewidth=2, label=f'Начальная сумма: {initial_bank:,} руб')
        
        wins = sum(is_winners)
        losses = 20 - wins
        
        avg_profit = np.mean(profits)
        max_profit = max(profits) if profits else 0
        min_profit = min(profits) if profits else 0
        
        stats_text = (f'Выиграли: {wins} ({wins/20*100:.0f}%)\n'
                     f'Проиграли: {losses} ({losses/20*100:.0f}%)\n'
                     f'Средняя прибыль: {avg_profit:,.0f} руб')
        
        if initial_bank >= 10000:
            ax.annotate(stats_text, xy=(0.98, 0.98), xycoords='axes fraction',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.9),
                       fontsize=9, va='top', ha='right')
        else:
            ax.annotate(stats_text, xy=(0.02, 0.98), xycoords='axes fraction',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.9),
                       fontsize=9, va='top')
        
        ax.set_xlabel('Игрок', fontsize=11)
        ax.set_title(f'20 игроков, начальный банк: {initial_bank:,} руб',
            fontsize=13, fontweight='bold', pad=25, y=0.9)
        
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_xticks(players)
        ax.set_xticklabels([f'P{i}' for i in players], fontsize=9)
        
        ax.ticklabel_format(axis='y', style='plain')
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        win_patch = Rectangle((0, 0), 1, 1, fc="green", edgecolor='black', alpha=0.8)
        lose_patch = Rectangle((0, 0), 1, 1, fc="red", edgecolor='black', alpha=0.8)
        
        ax.legend([win_patch, lose_patch,
                  plt.Line2D([0], [0], color='blue', linestyle='--')],
                 ['Выиграл (выход в плюс)', 'Проиграл (нет денег на ставку)',
                  'Начальная сумма'],
                 loc='upper left' if initial_bank >= 10000 else 'upper right', 
                 fontsize=9)
        
        if final_banks:
            max_bank = max(final_banks)
            min_bank = min(final_banks)
            margin = max_bank * 0.1
            ax.set_ylim([min(0, min_bank) - margin, max_bank + margin])
    
    plt.suptitle('Результаты 20 игроков в Санкт-Петербургском парадоксе',
                fontsize=14, fontweight='bold', y=1.02)
    plt.subplots_adjust(hspace=0.60)
    plt.tight_layout()
    plt.show()
    
    return all_results

def simulate_1000_games():
    print("\n" + "="*80)
    print("СИМУЛЯЦИЯ 1000 ИГР ДЛЯ КАЖДОЙ НАЧАЛЬНОЙ СУММЫ")
    print("="*80)
    print("ДВА условия остановки:")
    print("1. Выход в любой плюс - ВЫИГРЫШ")
    print("2. Нет денег на ставку (20 рублей) - ПРОИГРЫШ")
    print("="*80)

    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    
    detailed_stats = {}
    
    for row_idx, initial_bank in enumerate(initial_banks):
        print(f"\nНачальная сумма: {initial_bank:,} руб")
        print("-" * 60)

        final_banks = []
        profits = []
        total_rounds_list = []
        is_winners_list = []
        
        print(f"  Прогресс: ", end='')
        for game in range(1000):
            result = play_saint_petersburg_game(initial_bank, max_rounds=200000)
            
            final_banks.append(result['final_bank'])
            profits.append(result['net_profit'])
            total_rounds_list.append(result['total_rounds'])
            is_winners_list.append(result['is_winner'])
            
            if (game + 1) % 100 == 0:
                print(f"{game + 1}...", end=' ')
        
        print("\n")
        
        detailed_stats[initial_bank] = {
            'final_banks': final_banks,
            'profits': profits,
            'total_rounds': total_rounds_list,
            'is_winners': is_winners_list
        }
        
        ax = axes[row_idx]
        
        wins_count = sum(is_winners_list)
        losses_count = 1000 - wins_count
        
        labels = ['Выиграл', 'Проиграл']
        sizes = [wins_count, losses_count]
        colors = ['#2ecc71', '#e74c3c']
        
        if sum(sizes) > 0:
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                  startangle=90, textprops={'fontsize': 11})
            
            for autotext in autotexts:
                autotext.set_fontweight('bold')
        
        ax.set_title(f'Результаты 1000 игр (Начальный банк: {initial_bank:,} руб)\nВыиграли: {wins_count} ({wins_count/10:.1f}%)\nПроиграли: {losses_count} ({losses_count/10:.1f}%)',
                    fontsize=13, fontweight='bold', pad=20)
        
        print(f"Статистика по 1000 играм:")
        print(f"  Выиграли (выход в плюс): {wins_count} ({wins_count/10:.1f}%)")
        print(f"  Проиграли (нет денег на ставку): {losses_count} ({losses_count/10:.1f}%)")
        print(f"  Средняя прибыль: {np.mean(profits):,.0f} руб")
        
        losing_banks = [fb for fb, win in zip(final_banks, is_winners_list) if not win]
        if losing_banks:
            print(f"\n  Среди проигравших:")
            print(f"  Средний финальный банк: {np.mean(losing_banks):,.2f} руб")
            print(f"  Медианный финальный банк: {np.median(losing_banks):,.2f} руб")
            
            below_20 = sum(1 for fb in losing_banks if fb < ENTRY_FEE)
            exactly_0 = sum(1 for fb in losing_banks if fb == 0)
            print(f"  Имеют меньше {ENTRY_FEE} руб: {below_20}")
            print(f"  Полные банкротства (0 руб): {exactly_0}")
        
        positive_profits = [p for p in profits if p > 0]
        if positive_profits:
            print(f"\n  Среди выигравших:")
            print(f"  Средний выигрыш: {np.mean(positive_profits):,.2f} руб")
            print(f"  Максимальный выигрыш: {max(positive_profits):,.2f} руб")
    
    plt.tight_layout()
    plt.show()
    
    return detailed_stats

def plot_comparative_analysis(detailed_stats):
    print("\nГенерация сравнительного анализа...")
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    initial_banks_list = list(detailed_stats.keys())
    
    ax = axes[0, 0]
    
    win_percentages = []
    loss_percentages = []
    
    for bank in initial_banks_list:
        stats = detailed_stats[bank]
        wins = sum(stats['is_winners'])
        losses = 1000 - wins
        
        win_percentages.append(wins / 10)
        loss_percentages.append(losses / 10)
    
    x = np.arange(len(initial_banks_list))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, win_percentages, width, label='Выиграли', 
                  color='#2ecc71', edgecolor='black')
    bars2 = ax.bar(x + width/2, loss_percentages, width, label='Проиграли', 
                  color='#e74c3c', edgecolor='black')
    
    ax.set_xlabel('Начальный банк (руб)', fontsize=12)
    ax.set_ylabel('Процент игр (%)', fontsize=12)
    ax.set_title('Процент выигрышей и проигрышей', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{bank:,}' for bank in initial_banks_list])
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{height:.1f}%', ha='center', va='bottom', fontsize=10)
    
    ax = axes[0, 1]
    
    avg_profits = []
    for bank in initial_banks_list:
        stats = detailed_stats[bank]
        avg_profits.append(np.mean(stats['profits']))
    
    colors = ['#e74c3c' if p < 0 else '#2ecc71' for p in avg_profits]
    bars = ax.bar(range(len(initial_banks_list)), avg_profits,
                 color=colors, edgecolor='black')
    
    ax.set_xlabel('Начальный банк (руб)', fontsize=12)
    ax.set_ylabel('Средняя прибыль (руб)', fontsize=12)
    ax.set_title('Средняя прибыль', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(initial_banks_list)))
    ax.set_xticklabels([f'{bank:,}' for bank in initial_banks_list])
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax.grid(True, alpha=0.3, axis='y')
    
    ax.ticklabel_format(axis='y', style='plain')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    for bar, profit in zip(bars, avg_profits):
        ax.text(bar.get_x() + bar.get_width()/2., 
               bar.get_height() + (0.1 if profit >= 0 else -0.5),
               f'{profit:,.0f}', ha='center', va='bottom' if profit >= 0 else 'top', 
               fontsize=10, fontweight='bold')
    
    ax = axes[1, 0]
    
    avg_rounds = []
    for bank in initial_banks_list:
        stats = detailed_stats[bank]
        avg_rounds.append(np.mean(stats['total_rounds']))
    
    bars = ax.bar(range(len(initial_banks_list)), avg_rounds,
                 color='#3498db', edgecolor='black')
    
    ax.set_xlabel('Начальный банк (руб)', fontsize=12)
    ax.set_ylabel('Среднее число раундов', fontsize=12)
    ax.set_title('Средняя длительность игры', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(initial_banks_list)))
    ax.set_xticklabels([f'{bank:,}' for bank in initial_banks_list])
    ax.grid(True, alpha=0.3, axis='y')
    
    for bar, rounds in zip(bars, avg_rounds):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
               f'{rounds:.0f}', ha='center', va='bottom', fontsize=10)
    
    ax = axes[1, 1]
    
    max_wins = []
    for bank in initial_banks_list:
        stats = detailed_stats[bank]
        win_profits = [p for p, win in zip(stats['profits'], stats['is_winners']) if win]
        max_wins.append(max(win_profits) if win_profits else 0)
    
    bars = ax.bar(range(len(initial_banks_list)), max_wins,
                 color='#27ae60', edgecolor='black')
    
    ax.set_xlabel('Начальный банк (руб)', fontsize=12)
    ax.set_ylabel('Максимальный выигрыш (руб)', fontsize=12)
    ax.set_title('Максимальный выигрыш', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(initial_banks_list)))
    ax.set_xticklabels([f'{bank:,}' for bank in initial_banks_list])
    ax.grid(True, alpha=0.3, axis='y')
    
    ax.ticklabel_format(axis='y', style='plain')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    for bar, max_win in zip(bars, max_wins):
        if max_win > 0:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                   f'{max_win:,.0f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    plt.show()
    
    print("\n" + "="*80)
    print("ИТОГОВЫЙ АНАЛИЗ САНКТ-ПЕТЕРБУРГСКОГО ПАРАДОКСА")
    print("="*80)
    
    for bank in initial_banks_list:
        stats = detailed_stats[bank]
        wins = sum(stats['is_winners'])
        losses = 1000 - wins
        avg_profit = np.mean(stats['profits'])
        
        print(f"\nПри начальном банке {bank:,} руб:")
        print(f"  Выиграли (выход в плюс): {wins} ({wins/10:.1f}%)")
        print(f"  Проиграли (нет денег на ставку): {losses} ({losses/10:.1f}%)")
        print(f"  Средняя прибыль: {avg_profit:,.0f} руб")
        
        if avg_profit > 0:
            print(f"  → В СРЕДНЕМ игра ВЫГОДНА")
        else:
            print(f"  → В СРЕДНЕМ игра НЕВЫГОДНА")

def main():
    
    current_time = int(time.time() * 1000) % 1000000
    random.seed(current_time)
    np.random.seed(current_time)
    
    print("\n1. ДИНАМИКА ОДНОЙ ИГРЫ")
    plot_single_game_dynamics()
    
    print("\n2. 20 ИГРОКОВ С ОДИНАКОВЫМ БАНКОМ")
    twenty_games_stats = plot_20_players()
    
    print("\n3. СТАТИСТИКА 1000 ИГР")
    detailed_stats = simulate_1000_games()
    
    print("\n4. СРАВНИТЕЛЬНЫЙ АНАЛИЗ")
    plot_comparative_analysis(detailed_stats)

if __name__ == "__main__":
    main()