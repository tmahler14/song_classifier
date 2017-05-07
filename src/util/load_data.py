import numpy as np

def load_all():	
	X_train = np.load('X_train.npy')
	X_test = np.load('X_test.npy')
	y_train = np.load('y_train.npy')
	y_test = np.load('y_test.npy')
	classes = np.load('classes.npy')
	return X_train, X_test, y_train, y_test, classes