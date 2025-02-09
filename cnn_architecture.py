# -*- coding: utf-8 -*-
"""CNN_Architecture.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/196j27_SgttOVCOfxWYoucWlUNkWhR3X2
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
    x = np.array([np.array(Image.open(fname)).flatten() for fname in fileList])
    x=x/255
    return x

myDir ="/content/train/*.png"
labels = load_labels(myDir)
data = load_data(myDir)
Labels = tensorflow.keras.utils.to_categorical(labels,10)

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test = train_test_split(data,Labels,test_size=0.3,random_state=seed_value) 
img_x , img_y = 28 , 28
X_train = X_train.reshape(X_train.shape[0] , img_x , img_y , 1)
X_test = X_test.reshape(X_test.shape[0] , img_x , img_y , 1)
input_shape = (img_x,img_y,1)

X_train.shape

model = Sequential()
model.add(Conv2D(16 , kernel_size=(5,5) , strides=(1,1) , padding = 'same' , activation='relu' , input_shape = input_shape))
model.add(MaxPooling2D(pool_size=(2,2) , strides=(2,2)))
model.add(Conv2D(32 , kernel_size=(5,5) , strides=(1,1) , padding = 'valid' , activation='relu'))
model.add(MaxPooling2D(pool_size=(2,2) , strides=(2,2)))
model.add(Flatten())
model.add(Dense(120 , activation='relu'))
model.add(Dense(80 , activation='relu'))
model.add(Dense(10 , activation='softmax'))

model.summary()

opt = tensorflow.keras.optimizers.Adam(learning_rate=0.001)
model.compile(loss='categorical_crossentropy',optimizer=opt,metrics=['accuracy'])

datagen = ImageDataGenerator(rotation_range=10,
                             width_shift_range = 0.2,
                             height_shift_range = 0.2,                             
                             horizontal_flip = True,
                             fill_mode = 'nearest'                              
                             )

datagen.fit(X_train)

history= model.fit(datagen.flow(X_train,y_train, batch_size=20),validation_data=(X_test,y_test), epochs=150 , verbose=1)

from keras.utils.vis_utils import plot_model
plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# Unseen Validation data
myDir_valid ="/content/valid/*.png"
labels_valid = load_labels(myDir_valid)
data_valid = load_data(myDir_valid)
Labels_valid = tensorflow.keras.utils.to_categorical(labels_valid,10)
data_valid = data_valid.reshape(data_valid.shape[0] , img_x , img_y , 1)

scores = model.evaluate(data_valid,Labels_valid)

# Confusion Matrix
rounded_predictions = model.predict_classes(data_valid, batch_size=20, verbose=0)

rounded_labels=np.argmax(Labels_valid, axis=1)

#importing confusion matrix
from sklearn.metrics import confusion_matrix
confusion = confusion_matrix(rounded_labels, rounded_predictions)
print('Confusion Matrix\n')
print(confusion)

from sklearn import metrics
scores_metric=metrics.classification_report(rounded_labels, rounded_predictions, labels=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
print(scores_metric)

from sklearn.metrics import precision_score,recall_score,f1_score,accuracy_score
prec = precision_score(rounded_labels, rounded_predictions , average = 'weighted')
print(prec)
rec = recall_score(rounded_labels, rounded_predictions , average = 'weighted')
print(rec)
acc = accuracy_score(rounded_labels, rounded_predictions)
print(acc)

