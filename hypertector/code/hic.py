#!/usr/bin/env python
# coding=utf-8
# the cnn framework based on theano liberary
from __future__ import print_function
import numpy
import time
#import theano
#theano.config.device = 'gpu'
#theano.config.floatX = 'float32'

from keras.models import Sequential
from keras.layers.core import Dense,Dropout,Activation,Flatten,Reshape
from keras.layers.convolutional import Convolution2D, MaxPooling2D, Convolution1D, MaxPooling1D, Convolution3D, MaxPooling3D
from keras.optimizers import SGD
#import imdb
#from keras.processing import sequence
#from keras.layers.Activation import tanh, softmax

from keras.utils import np_utils

import scipy.io as sio
import random
import math

import scipy.io as sio

##################################################
#This function is used to construct the CNN model#
##################################################
def build_CNN_model(layers, loss, optimizer):
    
    model = Sequential()
    for layer in layers:
        model.add(layer)

    model.compile(loss=loss,optimizer=optimizer)
    
    return model

##########################################################
#This function is used to train the constructed CNN model#
##########################################################
#def train_model(model, x_train, y _train, x_val, y_val, batch_size,nb_epoch):
#    model.fit(x_train, y_train, batch_size = batch_size,
#             nb_epoch = nb_epoch, show_accuracy=True,verbose=1,
#             validation_data=(x_val, y_val))


################################
#按照数据预处理的格式，装载数据#
################################
def loadData(dataFile, typeId = -1, bShowData = False):
    data = sio.loadmat(dataFile)

    train_data = data['DataTr']
    train_label_temp = data['CIdTr'][0,:]
#    train_label = train_label[0,:]
#    return train_data,train_label
#    train_set = [train_data, train_label]

    test_data = data['DataTe']
    test_label_temp = data['CIdTe'][0,:]
#    test_set = [test_data, test_label]

    valid_data = data['DataTr']
    valid_label_temp = data['CIdTr'][0,:]
#    valid_set = [valid_data, valid_label]

#    def shared_dataset(data_xy, borrow=True):
#        data_x, data_y = data_xy
#        shared_x = theano.shared(numpy.asarray(data_x,dtype=theano.config.floatX))
#        shared_y = theano.shared(numpy.asarray(data_y,dtype='int32'))
#        return shared_x, shared_y

#   test_set_x, test_set_y = shared_dataset(test_set)
#    valid_set_x, valid_set_y = shared_dataset(valid_set)
#    train_set_x, train_set_y = shared_dataset(train_set)

#   rval = [(train_set_x, train_set_y), (valid_set_x, valid_set_y), (test_set_x, test_set_y)]
    

#    train_dataset_data = train_data.tolist()
#    test_dataset_data = test_data.tolist()
#    valid_dataset_data = valid_data.tolist()
    
    train_label = numpy.empty(len(train_label_temp))
    valid_label = numpy.empty(len(valid_label_temp))
    test_label = numpy.empty(len(test_label_temp))

    train_dataset_data = []
    nX = []
    count = 0
    for x in train_data:
        nx = []
        for w in x:
            nx.append(w)
        numpy.array(nx,dtype="object",copy=True)
        nX.append(nx)
        train_label[count] = int(train_label_temp[count])
        count = count + 1
    train_dataset_data = nX
#    testTemp = numpy.array(nX[:len(nX)])

    valid_dataset_data = []
    nX = []
    count = 0
    for x in valid_data:
        nx = []
        for w in x:
            nx.append(w)
        numpy.array(nx,dtype="object",copy=True)
        nX.append(nx)
        valid_label[count] = int(valid_label_temp[count])
        count = count + 1
    valid_dataset_data = nX


    test_dataset_data = []
    nX = []
    count = 0
    for x in test_data:
        nx = []
        for w in x:
            nx.append(w)
        numpy.array(nx,dtype="object",copy=True)
        nX.append(nx)
        test_label[count] = int(test_label_temp[count])
        count = count + 1
    test_dataset_data = nX

    train_dataset_data = numpy.array(train_dataset_data,dtype="object")
    test_dataset_data = numpy.array(test_dataset_data)
    valid_dataset_data = numpy.array(valid_dataset_data)

    return [(train_dataset_data, train_label),(valid_dataset_data,valid_label),(test_dataset_data,test_label)]
#    return rval

#######################################################################################
#currently, I wrote all the network constructing and training and testing in this file#
#laterly, I will seperate them apart.                                                 #
#######################################################################################
def temp_network(filePath, neuronLayers, con_step_length, max_pooling_feature_map_size, number_of_full_layer_nodes, learning_ratio, train_decay, batch_size, epoches):
    #get the train data, train label, validate data, validate label, test data, test label
    train_dataset, valid_dataset, test_dataset = loadData(filePath + ".mat")


    #the dimension of the input signal's chanel
    channel_length = train_dataset[0].shape[1]
    sample_counts = train_dataset[0].shape[0]

#    train_dataset, test_dataset = imdb.load_data()   
    #initialize parameters
    layer1_input_length = len(test_dataset[0][0])
    #con_filter_length = int((math.ceil( (layer1_input_length /  con_step_length) / neuronLayers)) * con_step_length)

    con_filter_length = int(math.ceil(neuronLayers * con_step_length))
    destinations = numpy.max(test_dataset[1])
    
    #############################
    #Network Information Display#
    #############################
    file = open(filePath + "description_SGD.txt",'w')

    file.write("The network have " + str(channel_length) + "input nodes in the 1st layer.\n")
    file.write("The amount of samples in the dataset is " + str(sample_counts) +".\n")
    file.write("The number of classification classes is " + str(destinations) +".\n")
    file.write("The size of the first convolutional layer is " + str(layer1_input_length)+".\n")
    file.write("There are "+str(number_of_full_layer_nodes)+" nodes in the fully connect layer.\n")

    print("The network have ", channel_length, "input nodes in the 1st layer.")
    print("The amount of samples in the dataset is ", sample_counts)
    print("The number of classification classes is ", destinations)
    print("The size of the first convolutional layer is ", layer1_input_length)
    print("There are ",number_of_full_layer_nodes," nodes in the fully connect layer.")

    #define some common parameters
    first_max_pooling_layer_kernel_size = 2


    #########################
    #Construct the CNN model# 
    #########################
##################################################################################################################
    model_not_use = Sequential()
    layer_not_in_use = Convolution2D(20,nb_row = con_filter_length, nb_col = 1,border_mode='valid', dim_ordering='th', bias=True,input_shape=(1,layer1_input_length, 1))
    layer2_prior_not_use = MaxPooling2D(pool_size = (first_max_pooling_layer_kernel_size,1), strides=(first_max_pooling_layer_kernel_size,1), border_mode='valid',dim_ordering='th')
    model_not_use.add(layer_not_in_use)
    model_not_use.add(layer2_prior_not_use)
#    print(str(layer2_prior_not_use))
    number_of_con_filters = layer2_prior_not_use.output_shape[2]
##################################################################################################################
    file.write('The number of convolutional filters is '+ str(number_of_con_filters)+ ",each kernel sizes "+ str(con_filter_length) + "X1.\n")
    
    model = Sequential()
   
    #the first convolutional layer
    layer1 = Convolution2D(number_of_con_filters,nb_row = con_filter_length, nb_col = 1,border_mode='valid', dim_ordering='th', bias=True,input_shape=(1,layer1_input_length, 1))
    

    print("The input to the first convolutional layer shapes", (1,layer1_input_length,1))
    file.write("The input to the first convolutional layer shapes 1X" + str(layer1_input_length) + "X1.\n"  )
    model.add(layer1)

    model.add(Activation('tanh'))

    layer2_prior = MaxPooling2D(pool_size = (first_max_pooling_layer_kernel_size,1), strides=(first_max_pooling_layer_kernel_size,1), border_mode='valid',dim_ordering='th')
    model.add(layer2_prior)
    print("the input and  output of the first convolutional layer shapes:" +str(layer1.input_shape) + "," + str(layer1.output_shape))
    print("the output of the first subsampling layer shapes:" + str(layer2_prior.output_shape))
    #from here on, modify the prior CCS/CCR network structure into HIC, proposed by Prof. Bai Gang on 2017/3/1.

    #将第一层的卷积层输出的数据，重新看做是一张图片，然后后面再对这张由由卷积输出的矩阵拼接成的图像进行卷积操作。
    #row_of_reshape = int(math.ceil(layer1_input_length / con_filter_length))
    row_of_reshape = layer2_prior.output_shape[2]
    print("the output will be reshaped into shape :" + str(row_of_reshape) + " X " + str(row_of_reshape))
    
    hic_reshape_layer = Reshape((1,row_of_reshape, row_of_reshape))
#    model.add(Reshape((row_of_reshape,int(number_of_con_filters))))
    model.add(hic_reshape_layer)
    print("after reshape, the image shapes:" + str(hic_reshape_layer.output_shape))

    #这样就相当于重新将输出结果组织成了一个新的普通的图像。
    #然后再用类似于对黑白图像的卷积方法，用一个3X3的固定大小的卷积核对其进行卷积->下采样->全连接->输出操作。
    #暂时先将这个卷积层的卷积核数量固定为20,大小固定为9X9
    number_of_con_filters_second = 20
    second_convolutional_kernel_size = 3
    layer_con_2 = Convolution2D(number_of_con_filters_second, nb_row = second_convolutional_kernel_size, nb_col = second_convolutional_kernel_size, border_mode='valid',dim_ordering='th',bias=True)
    model.add(layer_con_2)
    print("经过第二次卷积以后，卷积出来的feature map大小为：" + str(layer_con_2.output_shape))
    model.add(Activation('tanh'))

    #the max pooling layer after the first convolutional layer
    #first_feature_map_size = (layer1_input_length - con_filter_length) / con_step_length + 1
    #print ("After the convolutional operation, the length of the feature map size is: " + str(first_feature_map_size))
#    max_pooling_kernel_size = int(math.ceil(first_feature_map_size / max_pooling_feature_map_size))
    max_pooling_kernel_size = int(max_pooling_feature_map_size)
    print("The max pooling kernel size is ", max_pooling_kernel_size)
    file.write("The max pooling kernel size is " + str(max_pooling_kernel_size) +".\n")
    layer2 = MaxPooling2D(pool_size = (max_pooling_kernel_size,max_pooling_kernel_size), strides=(max_pooling_kernel_size,max_pooling_kernel_size), border_mode='valid',dim_ordering='th')
    model.add(layer2)
    print("经过下采样之后，得到的feature map每一个大小为：" + str(layer2.output_shape))
    
    #再加一个卷积层
#    numebr_of_con_filters_third = 20
#    layer_con_3 = Convolution2D(number_of_con_filters_second, nb_row = second_convolutional_kernel_size, nb_col = second_convolutional_kernel_size, border_mode='valid',dim_ordering='th',bias=True)
#    model.add(layer_con_3)
#    model.add(Activation('tanh'))
#    print("经过第三次卷积以后，得到的feature map的shape为：" + str(layer_con_3.output_shape))
    #Flatten the variables outputed from maxpooling layer

    #layer_maxpooling3 = MaxPooling2D(pool_size = (max_pooling_kernel_size,max_pooling_kernel_size), strides=(max_pooling_kernel_size,max_pooling_kernel_size), border_mode='valid',dim_ordering='th')
   # model.add(layer_maxpooling3)
   # print("经过最后一次下采样之后，得到的feature map每一个大小为：" + str(layer_maxpooling3.output_shape))

    #再加一个卷积层
#    numebr_of_con_filters_third = 20
#    layer_con_4 = Convolution2D(number_of_con_filters_second, nb_row = second_convolutional_kernel_size, nb_col = second_convolutional_kernel_size, border_mode='valid',dim_ordering='th',bias=True)
#    model.add(layer_con_4)
#    model.add(Activation('tanh'))
#    print("经过第四次卷积以后，得到的feature map的shape为：" + str(layer_con_4.output_shape))
    #Flatten the variables outputed from maxpooling layer

    layer_maxpooling3 = MaxPooling2D(pool_size = (max_pooling_kernel_size,max_pooling_kernel_size), strides=(2,2), border_mode='valid',dim_ordering='th')
    model.add(layer_maxpooling3)
    
    print("经过最后一次下采样之后，得到的feature map每一个大小为：" + str(layer_maxpooling3.output_shape))
    model.add(Flatten())
    
    #the fully connected layer
    layer3 = Dense(number_of_full_layer_nodes, bias = True)
    model.add(layer3)
    model.add(Activation('tanh'))

    #the activation layer which will output the final classification result
    layer4 = Dense(destinations + 1,activation = 'tanh', bias=True)
#    layer4 = Activation('tanh')
    model.add(layer4)

    layer5 = Activation('softmax')
    model.add(layer5)

    #the optimizer
    sgd = SGD(lr = learning_ratio, decay = train_decay, momentum = 0.6, nesterov=True)

    model.compile(optimizer=sgd, loss='categorical_crossentropy',metrics=['accuracy'])

    train_dataset_data = train_dataset[0].reshape(train_dataset[0].shape[0],1,train_dataset[0].shape[1],1)
    train_dataset_label = np_utils.to_categorical(train_dataset[1])
    print("The dataset used to train the model shapes ",train_dataset_data.shape)
    print("The label corresponding to the train data shapes ",train_dataset_label.shape)
    
    #prepare the validation dataset
    validation_dataset_data = valid_dataset[0].reshape(valid_dataset[0].shape[0],1,valid_dataset[0].shape[1],1)
    validation_dataset_label = np_utils.to_categorical(valid_dataset[1])
    validation_data = (validation_dataset_data,validation_dataset_label)

    

    history = model.fit(train_dataset_data, train_dataset_label, batch_size = batch_size, nb_epoch = epoches, verbose=1, validation_split=0, shuffle=True)
    model.save_weights(filePath + 'Model.h5', overwrite=True)
    
    sio.savemat(filePath + "Result.mat",{'loss':history.history['loss'],'accuracy':history.history['acc']})

    #test the model
    #prepare the testing dataset as the training dataset does
    
    test_dataset_data = test_dataset[0].reshape(test_dataset[0].shape[0],1,test_dataset[0].shape[1],1)
    test_dataset_label = np_utils.to_categorical(test_dataset[1])
    
    classes = model.predict_classes(test_dataset_data, verbose=1)
    test_dataset_label = test_dataset[1].astype(numpy.int) 
    print("对测试数据集的预测结果为：",classes)
    print("测试数据集中的真实结果为：",test_dataset_label)
    print("一共得到测试结果",len(classes),"个，一共有",len(test_dataset_label),"个.")

    test_accuracy = numpy.mean(numpy.equal(test_dataset_label, classes))

    print("The correct ratio of the trained CNN model is ",  test_accuracy)
    file.write("The correct ratio of the trained CNN model is " + str(test_accuracy) +".\n")

    file.close()
    return classes,test_dataset_label    

def network(path, con_step_length, max_pooling_feature_map_size, fullLayerSize, batch_size, learning_ratio, train_decay, epoches):
    return temp_network(path, con_step_length = con_step_length, max_pooling_feature_map_size = max_pooling_feature_map_size, number_of_full_layer_nodes = fullLayerSize, learning_ratio = learning_ratio, train_decay = train_decay, batch_size = batch_size,epoches = epoches)

def run_sub():
    for mark in range(15,31):
        print("现在的实验的数据集是：newKSC" + str(mark) + "N4.mat")
        file4pixel = "newKSC" + str(mark) + "N4"
	network(file4pixel, 5, 40, 10)

def run_network(datafile, neuronLayers, neighbors, maxPoolingSize, fullLayerSize, batch_size, learning_ratio, train_decay,epoches):
        print("=============== hic structure based ===============")
        f = open(datafile +"CNNTimeCounting.txt",'wb')
        print("现在执行的数据集是" + datafile +".mat, bling bling~~")
        f.write('------------------------------------------------------\n')
        f.write('start to train.......')
        startTime = time.clock()
        f.write('start time: ' + str(startTime) + '\n')
        temp_network(datafile, neuronLayers, neighbors, maxPoolingSize, fullLayerSize, learning_ratio, train_decay, batch_size, epoches)
        endTime = time.clock()
        f.write('end time: ' + str(endTime) + '\n')
        f.write('total time: ' + str(endTime - startTime))
        f.close()
        print('total time ：' + str(endTime - startTime))

if __name__ == '__main__':
    run_network("../experiments/KSC_1_20_2017_5_11_10_58/KSC_1_20", 4, 4, 2, 100, 100, 0.0001, 0.000001, 500)
