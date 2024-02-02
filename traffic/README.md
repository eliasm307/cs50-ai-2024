See https://cs50.harvard.edu/ai/2024/projects/5/traffic/

# Experimentation

Experiments were using the small data set with 3 categories.

## Basic

Constructed a basic initial model using some values from lecture

```py
model = keras.models.Sequential(
    [
        keras.layers.Conv2D(10, (3, 3), input_shape=IMG_DIMENSIONS_TUPLE),
        # Flatten image into a 1D array
        keras.layers.Flatten(),
        # Add hidden layers
        keras.layers.Dense(9, activation="relu"),
        # randomly remove some nodes so we prevent over dependence
        keras.layers.Dropout(0.5),
        # Add output layer for each label (softmax will turn output into a probability range)
        keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
    ]
)
```

This achieved a max accuracy of 0.6587. We will use this as a baseline.

## With "relu" activation on input layer

Added activation on input layer, based on lecture examples:

```py

model = keras.models.Sequential(
    [
        keras.layers.Conv2D(
            10, (3, 3), input_shape=IMG_DIMENSIONS_TUPLE, activation="relu"
        ),
        # Flatten image into a 1D array
        keras.layers.Flatten(),
        # Add hidden layers
        keras.layers.Dense(9, activation="relu"),
        # randomly remove some nodes so we prevent over dependence
        keras.layers.Dropout(0.5),
        # Add output layer for each label (softmax will turn output into a probability range)
        keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
    ]
)
```

This achieved a max accuracy of 0.6488, which is similar to the baseline so the activation
used doesn't seem to have a significant effect on the output

## Without dropout layer

Added activation on input layer, based on lecture examples:

```py

model = keras.models.Sequential(
    [
        keras.layers.Conv2D(
            10, (3, 3), input_shape=IMG_DIMENSIONS_TUPLE, activation="relu"
        ),
        # Flatten image into a 1D array
        keras.layers.Flatten(),
        # Add hidden layers
        keras.layers.Dense(9, activation="relu"),
        # Add output layer for each label (softmax will turn output into a probability range)
        keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
    ]
)
```

This achieved a max accuracy of 1, which is a perfect score, however the reliability of the model could be affected
if it has over-fit on the training data such that it cannot handle variations of the inputs accurately.
However it seems the dropout used does have an effect on accuracy but might also affect reliability.

# Increase number of filters

Increased the number of filters as follows:

```py
model = keras.models.Sequential(
    [
        keras.layers.Conv2D(
            32, (3, 3), input_shape=IMG_DIMENSIONS_TUPLE
        ),
        # Flatten image into a 1D array
        keras.layers.Flatten(),
        # Add hidden layers
        keras.layers.Dense(9, activation="relu"),
        # randomly remove some nodes so we prevent over dependence
        keras.layers.Dropout(0.5),
        # Add output layer for each label (softmax will turn output into a probability range)
        keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
    ]
)
```

This achieved a max accuracy of 0.6488, which is similar to the baseline so increasing the number of filters
used doesn't seem to have a significant effect on the output.

# Multiple hidden layers with low nodes

Increased the number of hidden layers as follows:

```py
model = keras.models.Sequential(
    [
        keras.layers.Conv2D(
            32, (3, 3), input_shape=IMG_DIMENSIONS_TUPLE
        ),
        # Flatten image into a 1D array
        keras.layers.Flatten(),
        # Add hidden layers
        keras.layers.Dense(9, activation="relu"),
        keras.layers.Dense(9, activation="relu"),
        keras.layers.Dense(9, activation="relu"),
        keras.layers.Dense(9, activation="relu"),
        keras.layers.Dense(9, activation="relu"),
        # randomly remove some nodes so we prevent over dependence
        keras.layers.Dropout(0.5),
        # Add output layer for each label (softmax will turn output into a probability range)
        keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
    ]
)
```

This achieved a max accuracy of 0.6389, which is similar to the baseline so increasing the number of hidden
layers used doesn't seem to have a significant effect on the output, if they each have a low number of nodes.

# Increase hidden layer density

Increased the number of hidden layer nodes as follows:

```py
model = keras.models.Sequential(
    [
        keras.layers.Conv2D(
            32, (3, 3), input_shape=IMG_DIMENSIONS_TUPLE
        ),
        # Flatten image into a 1D array
        keras.layers.Flatten(),
        # Add hidden layers
        keras.layers.Dense(90, activation="relu"),
        # randomly remove some nodes so we prevent over dependence
        keras.layers.Dropout(0.5),
        # Add output layer for each label (softmax will turn output into a probability range)
        keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
    ]
)
```

This achieved a max accuracy of 0.9980.
This suggests increasing the number of nodes hidden layers have has a significant effect on the model accuracy
for this type of application, even if we don't add more layers.

