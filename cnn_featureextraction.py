# -*- coding: utf-8 -*-
"""CNN_FeatureExtraction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pPcOJPfYWCy05TcIkSxalE6SmC9ebISI
"""

from google.colab import files
uploaded = files.upload()
!unzip '/content/train.zip'
!unzip '/content/valid.zip'

# Commented out IPython magic to ensure Python compatibility.
import glob
from PIL import Image
import os
import numpy as np
# Importing Keras
import tensorflow
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D,MaxPooling2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Flatten , Activation
from sklearn.model_selection import KFold
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV
from keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
# %matplotlib inline


# Seed value
# Apparently you may use different seed values at each stage
seed_value= 1000

# 1. Set `PYTHONHASHSEED` environment variable at a fixed value
import os
os.environ['PYTHONHASHSEED']=str(seed_value)

# 2. Set `python` built-in pseudo-random generator at a fixed value
import random
random.seed(seed_value)

# 3. Set `numpy` pseudo-random generator at a fixed value
np.random.seed(seed_value)

# 4. Set the `tensorflow` pseudo-random generator at a fixed value
tensorflow.random.set_seed(seed_value)
# for later versions: 
# tf.compat.v1.set_random_seed(seed_value)

# 5. Configure a new global `tensorflow` session
from tensorflow.keras import backend as K
session_conf = tensorflow.compat.v1.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
sess = tensorflow.compat.v1.Session(graph=tensorflow.compat.v1.get_default_graph(), config=session_conf)
tensorflow.compat.v1.keras.backend.set_session(sess)
# for later versions:
# session_conf = tf.compat.v1.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
# sess = tf.compat.v1.Session(graph=tf.compat.v1.get_default_graph(), config=session_conf)
# tf.compat.v1.keras.backend.set_session(sess)

def load_labels(myDir):
    labels=[]
    fileList = glob.glob(myDir)
    for fname in fileList:
        fileName = os.path.basename(fname)
        curLabel = fileName.split("-")[0]
        labels.append(curLabel)
    return np.asarray(labels)

# Function to Load Image data and then normalize it 
def load_data(myDir):
    fileList = glob.glob(myDir) 
    newsize = (32, 32)   
    x = np.array([np.array(Image.open(fname).resize(newsize)).flatten() for fname in fileList])
    x=x/255
    return x

myDir ="/content/train/*.png"
labels = load_labels(myDir)
data = load_data(myDir)
Labels = tensorflow.keras.utils.to_categorical(labels,10)

# converting the grey scale image to rgb images for transfer learning
rgb_batch = np.repeat(data[..., np.newaxis], 3, -1)    
print(rgb_batch.shape)

from tensorflow.keras.applications.vgg16 import VGG16
vgg_conv = VGG16(weights='imagenet' , include_top = False, input_shape=(32,32,3))

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test = train_test_split(rgb_batch,labels,test_size=0.3,random_state=seed_value) 
img_x , img_y = 32 , 32
X_train = X_train.reshape(X_train.shape[0] , img_x , img_y , 3)
X_test = X_test.reshape(X_test.shape[0] , img_x , img_y , 3)
input_shape = (img_x,img_y,1)

nTrain = X_train.shape[0]
nVal = X_test.shape[0]

train_features = np.zeros(shape=(nTrain,1,1,512))
val_feature = np.zeros(shape=(nVal,1,1,512))

train_features = vgg_conv.predict(X_train)
train_features = np.reshape(train_features,(nTrain,1*1*512))

val_features = vgg_conv.predict(X_test)
val_features = np.reshape(val_features,(nVal,1*1*512))

"""**Support Vector Algortihm**"""

from sklearn.svm import SVC

classifier = SVC(kernel = 'linear')
classifier.fit(train_features,y_train)

y_pred = classifier.predict(val_features)

#importing confusion matrix
from sklearn.metrics import confusion_matrix
confusion = confusion_matrix(y_test, y_pred)
print('Confusion Matrix\n')
print(confusion)

from sklearn.metrics import precision_score,recall_score,f1_score,accuracy_score
acc = accuracy_score(y_test, y_pred)
print(acc)

from sklearn import metrics
scores_metric=metrics.classification_report(y_test, y_pred, labels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
print(scores_metric)

myDir_valid ="/content/valid/*.png"
labels_valid = load_labels(myDir_valid)
data_valid = load_data(myDir_valid)
Labels_valid = tensorflow.keras.utils.to_categorical(labels_valid,10)
rgb_batch_valid = np.repeat(data_valid[..., np.newaxis], 3, -1)    
print(rgb_batch_valid.shape)
rgb_batch_valid = rgb_batch_valid.reshape(rgb_batch_valid.shape[0] , img_x , img_y , 3)

nValidated = rgb_batch_valid.shape[0]

validated_features = np.zeros(shape=(nValidated,1,1,512))

validated_features = vgg_conv.predict(rgb_batch_valid)
validated_features = np.reshape(validated_features,(nValidated,1*1*512))

y_pred_val = classifier.predict(validated_features)

#importing confusion matrix
from sklearn.metrics import confusion_matrix
confusion = confusion_matrix(labels_valid, y_pred_val)
print('Confusion Matrix\n')
print(confusion)

from sklearn import metrics
scores_metric=metrics.classification_report(labels_valid, y_pred_val, labels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
print(scores_metric)

from sklearn.metrics import precision_score,recall_score,f1_score,accuracy_score
prec = precision_score(labels_valid, y_pred_val , average = 'weighted')
print(prec)
rec = recall_score(labels_valid, y_pred_val , average = 'weighted')
print(rec)
acc = accuracy_score(labels_valid, y_pred_val)
print(acc)

