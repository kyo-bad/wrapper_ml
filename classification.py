#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.utils import resample
from sklearn.model_selection import train_test_split, StratifiedKFold, learning_curve
from sklearn.metrics import classification_report, roc_curve, auc
import seaborn as sns
from .mldata import MlData


def cr_to_df(cr: str):
    """
    convert classification_report to DataFrame
    :param cr: classification_report
    :return: pd.Dataframe
    """
    clf_report = list(filter(lambda x: len(x) != 0, re.split(" |\n", cr)))
    clf_report[clf_report.index("avg")] = "".join(clf_report[clf_report.index("avg"):clf_report.index("avg") + 3])
    del clf_report[clf_report.index("avg/total") + 1:clf_report.index("avg/total") + 3]
    column = clf_report[0:4]
    del clf_report[0:4]
    index = np.array(clf_report)[list(range(0, len(clf_report), 5))]
    # del np.array(clf_report)[list(range(0,len(clf_report),5))]
    result = [clf_report[i + 1:i + 5] for i in range(0, len(clf_report), 5)]
    crdf = pd.DataFrame(result, columns=column, index=index)
    crdf[["precision", "recall", "f1-score"]] = crdf[["precision", "recall", "f1-score"]].astype(float)
    crdf["support"] = crdf["support"].astype(int)
    return crdf


class Classification(MlData):
    """
    分類の基本評価指標を実装
    個別のアルゴリズムは派生クラスやset_classifierで定義
    """

    def __init__(self, dataFrame: pd.DataFrame, y_column: str, x_columns: list):
        super().__init__(dataFrame, y_column, x_columns)

    def cross_validation(self, k: int = 5):
        """
        交差検定を行う
        :param k: 交差数
        """
        feature = self.x_values.as_matrix()
        label = self.y_values.as_matrix()
        cv = StratifiedKFold(n_splits=k, shuffle=True).split(feature, label)
        # ラベルをshuffleするのでtrueとpredは再構成する必要あり
        true_label = np.array([])
        pred_label = np.array([])
        miss = pd.DataFrame(columns=["predict", "true"])  # 交差検定でミスしたラベルのインデックスとミスの仕方を記録

        model = self._return_base_model()
        for train_index, test_index in cv:
            model.fit(feature[train_index], label[train_index])
            pred = model.predict(feature[test_index])
            for i in range(0, len(test_index)):
                if pred[i] != label[test_index][i]:  # ミスってた場合
                    miss_row = pd.DataFrame([[pred[i], label[test_index][i]]],
                                            columns=["predict", "true"], index=[test_index[i]])
                    miss = pd.concat([miss, miss_row], axis=0)
            true_label = np.hstack([true_label, label[test_index]])
            pred_label = np.hstack([pred_label, pred])
        print(classification_report(true_label, pred_label))
        return cr_to_df(classification_report(true_label, pred_label)), miss

    def draw_learning_curve(self):
        """http://aidiary.hatenablog.com/entry/20150826/1440596779"""
        train_sizes, train_scores, test_scores = learning_curve(self._return_base_model(),
                                                                self.x_values.as_matrix(),
                                                                self.y_values.as_matrix(),
                                                                cv=10,
                                                                scoring="mean_squared_error",
                                                                train_sizes=np.linspace(0.5, 1.0, 10))
        plt.plot(train_sizes, train_scores.mean(axis=1), label="training scores")
        plt.plot(train_sizes, test_scores.mean(axis=1), label="test scores")
        plt.legend(loc="best")
        plt.show()

    def draw_roc_curve(self):

        train, test, train_label, test_label = train_test_split(self.x_values.as_matrix(),
                                                                self.y_values)
        probas_ = self._return_base_model().fit(train, train_label).predict_proba(test)

        # Compute ROC curve and area the curve
        fpr, tpr, thresholds = roc_curve(test_label, probas_[:, 1])
        roc_auc = auc(fpr, tpr)
        print("Area under the ROC curve :", roc_auc)

        # Plot ROC curve
        plt.clf()
        plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.0])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic example')
        plt.legend(loc="lower right")
        plt.show()
