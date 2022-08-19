import cv2
import numpy as np 
import matplotlib.pyplot as plt
import tensorflow as tf
import os
import random
from tensorflow import keras
from keras.datasets import mnist
from keras.optimizers import SGD

def generate_image(v, x_test, y_test, predict, occurences):
    fig, ax = plt.subplots(1)

    ax.imshow(x_test[v].reshape(28, 28), cmap='plasma')
    ax.set_title('Image Number ' + str(occurences.index(v)) + ' of ' + str(len(occurences)) + ' Total Occurences')

    actual = np.where(y_test[v] == 1)
    legend = 'Predicted label: ' + str(np.argmax(predict[v])) + '\n' + 'Actual label: ' + str(actual[0][0])
    ax.text(x=1, y=25.9, s=legend, bbox={'facecolor': 'white', 'pad': 10})

    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    plt.show()

def find_all(x_test, y_test, predict):
    incorrect_predict = {}
    correct_predict = {}
    
    for i in range(len(x_test)):
        index = np.where(y_test[i] == 1)
        if index[0][0] != np.argmax(predict[i]):
            incorrect_predict.update({i: np.argmax(predict[i])})
        else:
            correct_predict.update({i: np.argmax(predict[i])})
    
    return incorrect_predict, correct_predict

def random_predict(predict):
    v = random.choice(predict)

    return v

def find_occurences(prediction, wanted):
    occurences = [k for k, v in prediction.items() if v == wanted]
    
    return occurences

def external_image(img, file, predict):
    fig, ax = plt.subplots(1)
    
    ax.imshow(img.reshape(28, 28), cmap='plasma')
    ax.set_title('Image ' + '\'' + str(file) + '\'' + ' After Processing')
    ax.text(x=1, y=25.9, s='Predicted label: ' + str(np.argmax(predict[0])), bbox={'facecolor': 'white', 'pad': 10})

    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    plt.show()

def external_data(file, input_dir):
    base_path = str(input_dir + '\\' + file)
    processed_path = str(os.getcwd() + '\processed_input\\' + file)

    base_img = cv2.imread(base_path)
    gray_img = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
    (thresh, black_white_img) = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY)
    inverted_img = cv2.bitwise_not(black_white_img)
    cv2.imwrite(processed_path, inverted_img)

    img = tf.keras.preprocessing.image.load_img(path=processed_path, color_mode='grayscale', target_size=(28, 28, 1))
    img = tf.keras.preprocessing.image.img_to_array(img)
    test_img = img.reshape((1, 784))

    return test_img, img

def mnist_data():
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train = x_train.reshape(60000, 784)
    x_test = x_test.reshape(10000, 784)

    y_train = keras.utils.to_categorical(y_train, 10)
    y_test = keras.utils.to_categorical(y_test, 10)

    return x_train, y_train, x_test, y_test

def create_model():
    model = keras.Sequential([
        keras.layers.Dense(784, activation='relu', input_shape=(784,)),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(10, activation='softmax')
    ])

    model.compile(
        optimizer=SGD(0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def new_model(x_train, y_train):
    model = create_model()

    model.summary()

    model.fit(x_train, y_train, epochs=150)
    model.save('mnist_model.h5')

    return model

def load_model(x_test, y_test):
    model = tf.keras.models.load_model("mnist_model.h5")

    model.summary()

    loss, acc = model.evaluate(x_test, y_test, verbose=2)
    print("Restored model, accuracy: {:5.2f}%".format(100 * acc))
    print("Restored model, loss: {:.2f}".format(loss))

    return model

def predict(model, x_test, y_test):
    print("\nExternal data must be placed in the 'input' folder.")
    external_mnist = input("Would you like to use your own external data or the MNIST data? (E/M): ")
    if external_mnist in ['E', 'e']:
        print()
        input_dir = str(os.getcwd() + '\input')
        curr_dir = os.listdir(input_dir)
      
        for file in curr_dir:
            test_img, img = external_data(file, input_dir)
            predict = model.predict(test_img)
            external_image(img, file, predict)
    elif external_mnist in ['M', 'm']:
        incorrect_correct = input("Would you like to see an incorrectly predicted image or a correctly predicted image? (I/C): ")

        number_range = input("Enter the number of the image you would like to see (0-9): ")
        try:
            assert int(number_range) in range(10)
        except AssertionError:
            print("Error: invalid input, exiting...")
            exit(1)

        predict = model.predict(x_test)
        incorrect_predict, correct_predict = find_all(x_test, y_test, predict)
        if incorrect_correct in ['I', 'i']:
            incorrect_occur = find_occurences(incorrect_predict, int(number_range))
            v = random_predict(incorrect_occur)
            generate_image(v, x_test, y_test, predict, incorrect_occur)
        elif incorrect_correct in ['C', 'c']:
            correct_occur = find_occurences(correct_predict, int(number_range))
            v = random_predict(correct_occur)
            generate_image(v, x_test, y_test, predict, correct_occur)
    else:
        print("Error: invalid input, exiting...")
        exit(1)

def main():
    x_train, y_train, x_test, y_test = mnist_data()

    curr_dir = os.listdir(os.getcwd())
    if 'mnist_model.h5' in curr_dir:
        model = load_model(x_test, y_test)
    else:
        model = new_model(x_train, y_train)

    try:
        predict(model, x_test, y_test)
    except UnboundLocalError:
        print('Error: model must be trained before use, exiting...')
        
if __name__ == "__main__":
    main()