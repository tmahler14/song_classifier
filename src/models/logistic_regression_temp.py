"""
Logistic Regression Mode

@author - Tim Mahler
"""

#-------------------------
# Libs
#-------------------------

# External
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pymysql.cursors
import sys, os
from tqdm import tqdm
import time

from sklearn.externals.six import StringIO
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model  import Ridge
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV

from sklearn.metrics import classification_report

# Internal
sys.path.append( os.path.realpath("%s/.."%os.path.dirname(__file__)) )
from util import data_accessor_util

#-------------------------
# Globals
#-------------------------

# Get data
(train_X, train_Y, train_le, test_X, test_Y, test_le) = data_accessor_util.get_all_data_sets()

classes = list(test_le.classes_)
print test_le.inverse_transform([0, 1, 2, 3, 4, 5, 6])

# Convert to numpy
(train_X, train_Y, test_X, test_Y) = data_accessor_util.convert_data_sets_to_numpy(train_X, train_Y, test_X, test_Y)

Cs = {"C" : np.arange(10**-5,10**-1,0.025)}

print train_X
print train_Y

print

print Cs

#-------------------------
# Functions
#-------------------------

# Main func

log_regr = LogisticRegression(penalty="l1")

print "Running GridSearchCV"
best_fit = GridSearchCV(log_regr, Cs, cv=3, verbose=10, n_jobs=12)

best_fit.fit(train_X, train_Y)

# Print the estimator
best_estimator = best_fit.best_estimator_
print best_estimator

# Get predictions for model
y_pred_train = best_fit.predict(train_X)
y_pred_test = best_fit.predict(test_X)

y_pred_train = y_pred_train.reshape((y_pred_train.shape[0], 1))
y_pred_test = y_pred_test.reshape((y_pred_test.shape[0], 1))

print "Got predictions"

print y_pred_train.shape
print train_Y.shape

print y_pred_test.shape
print test_Y.shape

print "y_pred"
print y_pred_train

# Cal mean error rate
accuracy_train = np.mean(np.square(y_pred_train == train_Y))
accuracy_test = np.mean(np.square(y_pred_test == test_Y))

print "RESULTS\n*******************"
print "\naccuracy_train = %f"%(accuracy_train)
print "accuracy_test = %f"%(accuracy_test)
print

print(classification_report(test_Y, y_pred_test, target_names=classes))
