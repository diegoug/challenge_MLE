import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb
from typing import Tuple, Union, List

warnings.filterwarnings('ignore')

class DelayModel:

    def __init__(self):
        self._model = None  # Model should be saved in this attribute.

    def preprocess(self, data: pd.DataFrame, target_column: str = None) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """
        # Generate additional features
        data['period_day'] = data['Fecha-I'].apply(self.get_period_day)
        data['high_season'] = data['Fecha-I'].apply(self.is_high_season)
        data['min_diff'] = data.apply(self.get_min_diff, axis=1)
        data['delay'] = np.where(data['min_diff'] > 15, 1, 0)

        # Generate features
        features = pd.concat([
            pd.get_dummies(data['OPERA'], prefix='OPERA'),
            pd.get_dummies(data['TIPOVUELO'], prefix='TIPOVUELO'),
            pd.get_dummies(data['MES'], prefix='MES'),
            pd.get_dummies(data['period_day'], prefix='period_day'),
            data[['high_season', 'min_diff']]
        ], axis=1)

        if target_column:
            target = data[target_column]
            return features, target
        return features

    def fit(self, features: pd.DataFrame, target: pd.DataFrame) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """
        # Calculate class balance
        n_y0 = len(target[target == 0])
        n_y1 = len(target[target == 1])
        scale = n_y0 / n_y1

        # Train the model with class balance
        self._model = xgb.XGBClassifier(random_state=1, learning_rate=0.01, scale_pos_weight=scale)
        self._model.fit(features, target)

    def predict(self, features: pd.DataFrame) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.
        
        Returns:
            (List[int]): predicted targets.
        """
        # Predict using the trained model
        if self._model is None:
            raise ValueError("Model is not trained yet.")
        return self._model.predict(features).tolist()

    @staticmethod
    def get_period_day(date: str) -> str:
        date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').time()
        morning_min = datetime.strptime("05:00", '%H:%M').time()
        morning_max = datetime.strptime("11:59", '%H:%M').time()
        afternoon_min = datetime.strptime("12:00", '%H:%M').time()
        afternoon_max = datetime.strptime("18:59", '%H:%M').time()
        evening_min = datetime.strptime("19:00", '%H:%M').time()
        evening_max = datetime.strptime("23:59", '%H:%M').time()
        night_min = datetime.strptime("00:00", '%H:%M').time()
        night_max = datetime.strptime("04:59", '%H:%M').time()

        if morning_min < date_time < morning_max:
            return 'mañana'
        elif afternoon_min < date_time < afternoon_max:
            return 'tarde'
        elif evening_min < date_time < evening_max or night_min < date_time < night_max:
            return 'noche'
        return 'noche'

    @staticmethod
    def is_high_season(fecha: str) -> int:
        fecha_año = int(fecha.split('-')[0])
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        range1_min = datetime.strptime('15-Dec', '%d-%b').replace(year=fecha_año)
        range1_max = datetime.strptime('31-Dec', '%d-%b').replace(year=fecha_año)
        range2_min = datetime.strptime('1-Jan', '%d-%b').replace(year=fecha_año)
        range2_max = datetime.strptime('3-Mar', '%d-%b').replace(year=fecha_año)
        range3_min = datetime.strptime('15-Jul', '%d-%b').replace(year=fecha_año)
        range3_max = datetime.strptime('31-Jul', '%d-%b').replace(year=fecha_año)
        range4_min = datetime.strptime('11-Sep', '%d-%b').replace(year=fecha_año)
        range4_max = datetime.strptime('30-Sep', '%d-%b').replace(year=fecha_año)

        if ((range1_min <= fecha <= range1_max) or 
            (range2_min <= fecha <= range2_max) or 
            (range3_min <= fecha <= range3_max) or
            (range4_min <= fecha <= range4_max)):
            return 1
        return 0

    @staticmethod
    def get_min_diff(data: pd.Series) -> float:
        fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
        fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
        min_diff = (fecha_o - fecha_i).total_seconds() / 60
        return min_diff

# Example usage
if __name__ == "__main__":
    # Load data
    data = pd.read_csv('/app/data/data.csv')
    
    # Initialize model
    model = DelayModel()
    
    # Preprocess data
    features, target = model.preprocess(data, target_column='delay')
    
    # Split data
    x_train, x_test, y_train, y_test = train_test_split(features, target, test_size=0.33, random_state=42)
    
    # Fit model
    model.fit(x_train, y_train)
    
    # Predict
    predictions = model.predict(x_test)
    
    # Evaluate
    print(classification_report(y_test, predictions))