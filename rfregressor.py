#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

from .regression import Regression


class RFClassifier(Regression):
    """RandomForestによる分類"""

    def __init__(self, dataFrame: pd.DataFrame, y_column: str, x_columns: list):
        super().__init__(dataFrame, y_column, x_columns)

    def _return_base_model(self):
        return RandomForestRegressor(n_estimators=1000, n_jobs=-1, oob_score=True)

    def learn_all_data(self, isplot=True):
        self._clf = self._return_base_model()
        self._clf.fit(self.x_values().as_matrix(), self.y_values().as_matrix())
        self.predict = lambda x: self._clf.predict(x)

        self.importance = pd.DataFrame({"key": self.x_columns,
                                        "value": self._clf.feature_importances_})
        if isplot:
            sns.barplot(x='value', y='key', data=self.importance)
            plt.show()
