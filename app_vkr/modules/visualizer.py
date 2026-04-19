import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import io
import base64
from datetime import datetime


class DataVisualizer:
    def __init__(self):
        plt.style.use('default')
        sns.set_palette("husl")

    def create_debt_dynamics_chart(self, dynamic_data):
        """Создает график динамики задолженности"""
        fig, ax = plt.subplots(figsize=(12, 6))

        periods = dynamic_data['periods']
        debts = dynamic_data['debts']
        charges = dynamic_data['charges']
        payments = dynamic_data['payments']

        x = range(len(periods))

        ax.plot(x, debts, marker='o', linewidth=2, label='Задолженность')
        ax.plot(x, charges, marker='s', linewidth=2, label='Начисления', alpha=0.7)
        ax.plot(x, payments, marker='^', linewidth=2, label='Платежи', alpha=0.7)

        ax.set_xlabel('Период')
        ax.set_ylabel('Сумма (руб.)')
        ax.set_title('Динамика начислений, платежей и задолженностей')
        ax.legend()
        ax.grid(True, alpha=0.3)

        ax.set_xticks(x)
        ax.set_xticklabels(periods, rotation=45)

        plt.tight_layout()

        return self._fig_to_base64(fig)

    def create_service_structure_chart(self, service_data):
        """Создает круговую диаграмму структуры долга по услугам"""
        fig, ax = plt.subplots(figsize=(10, 8))

        services = service_data['services']
        debts = service_data['debts']

        # Фильтруем мелкие доли
        total = sum(debts)
        threshold = total * 0.02  # 2% порог

        filtered_services = []
        filtered_debts = []
        other_debt = 0

        for service, debt in zip(services, debts):
            if debt >= threshold:
                filtered_services.append(service)
                filtered_debts.append(debt)
            else:
                other_debt += debt

        if other_debt > 0:
            filtered_services.append('Прочие')
            filtered_debts.append(other_debt)

        wedges, texts, autotexts = ax.pie(filtered_debts, labels=filtered_services, autopct='%1.1f%%',
                                          startangle=90)

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('Структура задолженности по видам услуг')

        plt.tight_layout()

        return self._fig_to_base64(fig)

    def create_forecast_chart(self, historical_data, forecast_data):
        """Создает график с историческими данными и прогнозом"""
        fig, ax = plt.subplots(figsize=(12, 6))

        hist_periods = [item['period'] for item in historical_data]
        hist_debts = [item['debt'] for item in historical_data]
        forecast_periods = [item['period'] for item in forecast_data]
        forecast_debts = [item['debt'] for item in forecast_data]

        all_periods = hist_periods + forecast_periods
        all_debts = hist_debts + forecast_debts

        x_hist = range(len(hist_periods))
        x_forecast = range(len(hist_periods), len(all_periods))

        ax.plot(x_hist, hist_debts, marker='o', linewidth=2, label='Исторические данные', color='blue')
        ax.plot(x_forecast, forecast_debts, marker='s', linewidth=2, label='Прогноз', color='red', linestyle='--')
        ax.axvline(x=len(hist_periods) - 0.5, color='gray', linestyle=':', alpha=0.7)

        ax.set_xlabel('Период')
        ax.set_ylabel('Задолженность (руб.)')
        ax.set_title('Прогноз динамики задолженности')
        ax.legend()
        ax.grid(True, alpha=0.3)

        x_ticks = list(x_hist) + list(x_forecast)
        ax.set_xticks(x_ticks[::max(1, len(x_ticks) // 10)])
        ax.set_xticklabels(all_periods[::max(1, len(all_periods) // 10)], rotation=45)

        plt.tight_layout()

        return self._fig_to_base64(fig)

    def create_aging_chart(self, aging_data):
        """Создает гистограмму возрастной структуры задолженности"""
        fig, ax = plt.subplots(figsize=(10, 6))

        categories = list(aging_data.keys())
        values = list(aging_data.values())
        colors = ['#28a745', '#ffc107', '#fd7e14', '#dc3545']

        bars = ax.bar(categories, values, color=colors)
        ax.set_title('Возрастная структура задолженности', fontsize=14)
        ax.set_ylabel('Сумма задолженности (руб.)')
        ax.set_xlabel('Срок просрочки')

        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.01,
                    f'{val:,.0f} руб.', ha='center', fontsize=9)

        plt.xticks(rotation=45)
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def create_risk_chart(self, risk_stats):
        """Создает круговую диаграмму классификации должников"""
        fig, ax = plt.subplots(figsize=(10, 8))

        labels = list(risk_stats.keys())
        values = list(risk_stats.values())

        colors = {
            'Критический': '#dc3545',
            'Высокий': '#fd7e14',
            'Средний': '#ffc107',
            'Низкий': '#28a745',
            'Минимальный': '#17a2b8'
        }
        color_list = [colors.get(label, '#6c757d') for label in labels]

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            colors=color_list,
            startangle=90
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('Классификация должников по группам риска', fontsize=14)

        legend_labels = [f'{label}: {val} чел.' for label, val in zip(labels, values)]
        ax.legend(legend_labels, loc='upper right', bbox_to_anchor=(1.3, 1))

        plt.tight_layout()

        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig):
        """Конвертирует matplotlib figure в base64 строку"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)
        return img_base64

    def create_forecast_chart_image(self, historical_data, forecast_data):
        """Создает график прогноза задолженности в виде изображения"""
        import matplotlib.pyplot as plt
        import io
        import base64

        hist_periods = [item['period'] for item in historical_data]
        hist_debts = [item['debt'] for item in historical_data]
        forecast_periods = [item['period'] for item in forecast_data]
        forecast_debts = [item['debt'] for item in forecast_data]

        all_periods = hist_periods + forecast_periods

        fig, ax = plt.subplots(figsize=(12, 6))

        x_hist = range(len(hist_periods))
        x_forecast = range(len(hist_periods), len(all_periods))

        ax.plot(x_hist, hist_debts, marker='o', linewidth=2, label='Исторические данные', color='blue')
        ax.plot(x_forecast, forecast_debts, marker='s', linewidth=2, label='Прогноз', color='red', linestyle='--')
        ax.axvline(x=len(hist_periods) - 0.5, color='gray', linestyle=':', alpha=0.7)

        ax.set_xlabel('Период')
        ax.set_ylabel('Задолженность (руб.)')
        ax.set_title('Прогноз динамики задолженности')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Настройка подписей оси X
        step = max(1, len(all_periods) // 10)
        x_ticks = list(range(0, len(hist_periods), step)) + list(range(len(hist_periods), len(all_periods), step))
        x_ticks = [i for i in x_ticks if i < len(all_periods)]
        x_labels = [all_periods[i] for i in x_ticks]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels, rotation=45)

        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(fig)

        return img_base64