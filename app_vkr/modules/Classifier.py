import sqlite3
import pandas as pd


class DebtorClassifier:
    """Классификация должников по группам риска"""

    def __init__(self, database_path):
        self.database_path = database_path

    def classify_debtors(self, dataset_id):
        """
        Классификация должников по группам риска:
        - Критический
        - Высокий
        - Средний
        - Низкий
        - Минимальный
        """
        try:
            conn = sqlite3.connect(self.database_path)

            # Получаем данные по абонентам
            query = '''
                    SELECT account_id,
                           address,
                           resident_name,
                           charge_amount,
                           payment_amount
                    FROM payment_records
                    WHERE dataset_id = ?
                    '''

            df = pd.read_sql_query(query, conn, params=[dataset_id])
            conn.close()

            if df.empty:
                return {
                    'debtors': [],
                    'statistics': {
                        'by_risk': {},
                        'total_debtors': 0
                    }
                }

            # Расчет долга по каждой записи
            df['debt'] = df['charge_amount'] - df['payment_amount']

            # Агрегация по лицевым счетам
            account_data = df.groupby('account_id').agg({
                'debt': 'sum',
                'charge_amount': 'sum',
                'payment_amount': 'sum',
                'address': 'first',
                'resident_name': 'first'
            }).reset_index()

            # Только должники (долг > 0)
            debtors = account_data[account_data['debt'] > 0].copy()

            if debtors.empty:
                return {
                    'debtors': [],
                    'statistics': {
                        'by_risk': {},
                        'total_debtors': 0
                    }
                }

            # Расчет платежной дисциплины
            debtors['payment_ratio'] = debtors['payment_amount'] / debtors['charge_amount']
            debtors['payment_ratio'] = debtors['payment_ratio'].fillna(0)

            # Определение уровня риска
            def determine_risk(row):
                """Определение уровня риска на основе платежной дисциплины и суммы долга"""
                # Критический риск
                if row['payment_ratio'] < 0.3 or row['debt'] > 100000:
                    return 'Критический'
                # Высокий риск
                elif row['payment_ratio'] < 0.5 or row['debt'] > 50000:
                    return 'Высокий'
                # Средний риск
                elif row['payment_ratio'] < 0.7 or row['debt'] > 20000:
                    return 'Средний'
                # Низкий риск
                elif row['payment_ratio'] < 0.9 or row['debt'] > 5000:
                    return 'Низкий'
                # Минимальный риск
                else:
                    return 'Минимальный'

            debtors['risk_level'] = debtors.apply(determine_risk, axis=1)

            # Формирование рекомендаций
            def get_recommendation(risk_level, total_debt):
                """Получение рекомендации по работе с должником"""
                recommendations = {
                    'Критический': 'Немедленная передача в суд, ограничение выезда, арест имущества',
                    'Высокий': 'Досудебное уведомление, звонки, визиты, ограничение услуг',
                    'Средний': 'Регулярные звонки, SMS-напоминания, предупреждения',
                    'Низкий': 'SMS-напоминания, email-рассылки',
                    'Минимальный': 'Мониторинг, профилактические напоминания'
                }

                base = recommendations.get(risk_level, 'Мониторинг')

                if total_debt > 100000:
                    return f"{base} (приоритетный должник)"
                elif total_debt > 50000:
                    return f"{base} (повышенное внимание)"
                return base

            debtors['recommendation'] = debtors.apply(
                lambda x: get_recommendation(x['risk_level'], x['debt']), axis=1
            )

            # Подготовка результата
            debtors_list = debtors[[
                'account_id', 'resident_name', 'address',
                'debt', 'payment_ratio', 'risk_level', 'recommendation'
            ]].to_dict('records')

            # Сортировка по сумме долга
            debtors_list.sort(key=lambda x: x['debt'], reverse=True)

            # Статистика по группам риска
            risk_stats = debtors['risk_level'].value_counts().to_dict()
            risk_sums = debtors.groupby('risk_level')['debt'].sum().to_dict()

            return {
                'debtors': debtors_list[:20],  # Топ-20 должников
                'statistics': {
                    'by_risk': risk_stats,
                    'by_risk_sum': {k: round(v, 2) for k, v in risk_sums.items()},
                    'total_debtors': len(debtors),
                    'total_debt_sum': round(debtors['debt'].sum(), 2)
                }
            }

        except Exception as e:
            print(f"Ошибка в classify_debtors: {e}")
            return {
                'debtors': [],
                'statistics': {
                    'by_risk': {},
                    'total_debtors': 0
                }
            }