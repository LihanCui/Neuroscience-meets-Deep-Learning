from __future__ import print_function
import scipy.io as sio
import numpy as np
import keras
from keras.layers.convolutional import Convolution3D
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D, MaxPooling2D, MaxPooling3D
from keras.optimizers import Adam
from keras.utils import np_utils

data3DCNN = sio.loadmat("processedData.mat")

X_train = data3DCNN["xTrain"].astype("float64")
Y_train = data3DCNN["yTrainCond"].astype("int32")
yTrainWord = data3DCNN["yTrainWord"].astype("int32")

xValidate = data3DCNN["xValid"].astype("float64")
yValidateCond = data3DCNN["yValidCond"].astype("int32")
yValidateWord = data3DCNN["yValidWord"].astype("int32")

X_test = data3DCNN["xTest"].astype("float64")
Y_test = data3DCNN["yTestCond"].astype("int32")
yTestWord = data3DCNN["yTestWord"].astype("int32")

data_augmentation = False

nb_classes = 12
batch_size = 32
nb_epoch = 100

# Process y_train/y_test

Y_train = np.swapaxes(Y_train,0,1)
Y_test = np.swapaxes(Y_test,0,1)

Y_train = np_utils.to_categorical(Y_train, nb_classes)
Y_test = np_utils.to_categorical(Y_test, nb_classes)

model = Sequential()

model.add(Convolution3D(32, 3, 3, 3, border_mode='same', input_shape=X_train.shape[1:], dim_ordering='th'))
model.add(Activation('relu'))
model.add(Convolution3D(32, 3, 3, 2, dim_ordering='th'))
model.add(Activation('relu'))
model.add(MaxPooling3D(pool_size=(3, 3, 2), dim_ordering='th'))
model.add(Dropout(0.25))

model.add(Convolution3D(64, 3, 3, 3, border_mode='same', dim_ordering='th'))
model.add(Activation('relu'))
model.add(Convolution3D(64, 2, 2, 2, dim_ordering='th'))
model.add(Activation('relu'))
model.add(MaxPooling3D(pool_size=(3, 3, 3), dim_ordering='th'))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(50))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(nb_classes))
model.add(Activation('softmax'))

adam = Adam(0.0001)
model.compile(loss='categorical_crossentropy',
              optimizer=adam,
              metrics=['accuracy'])

X_train = X_train.astype('float32')
X_test = X_test.astype('float32')

if not data_augmentation:
    print('Not using data augmentation.')
    model.fit(X_train, Y_train,
              batch_size=batch_size,
              nb_epoch=nb_epoch,
              validation_data=(X_test, Y_test),
              shuffle=True)
else:
    print('Using real-time data augmentation.')

    # this will do preprocessing and realtime data augmentation
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        rotation_range=0,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # compute quantities required for featurewise normalization
    # (std, mean, and principal components if ZCA whitening is applied)
    datagen.fit(X_train)

    # fit the model on the batches generated by datagen.flow()
    model.fit_generator(datagen.flow(X_train, Y_train,
                        batch_size=batch_size),
                        samples_per_epoch=X_train.shape[0],
                        nb_epoch=nb_epoch,
                        validation_data=(X_test, Y_test))