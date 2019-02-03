nullcon HackIM 2019: mlAuth
=============================

## Description

Fool that mlAuth

An organisation has implemented an authentication system "mlAuth" using machine learning, which is 99.9% accurate. Every employee has a profile(represented by a string on 784 hex values). mlAuth is trained using these profiles to predict the probability of authenticity for an employee. System grants access only if the predicted probability is higher than 0.99. Hence, your aim is to generate a fake profile that will trick the 99.9% accurate mlAuth in granting you access. 
You can make use of dumped machine learning model to conduct your targeted attack. Are you smart enough to fool the "intelligent" mlAuth?

#### Files

`https://drive.google.com/file/d/1QvZBVns4ei1fqnhDe2uEBKiaEeRkdVwl/view?usp=sharing`

If the link doesn't work: [Python script](get_prob.py), [Keras model](keras_model)

#### Server

`http://ml.ctf.nullcon.net/predict`


## Solution

We have to find a vector of 784 hex values that will output a model probability greater than 0.99.

Since ML is just basically a lot of linear combinations of inputs, we can do a probability descent using the `keras_model` provided: at each step we modify the best index with the best value that will maximize the output probability.
Note that we could reach a local minima but didn't found any with this technique.

Let's also note for a fun fact that if you create the input vector using `np.random.seed(1)` you would get a probability output of `0.998838`. So this would be enough to find the flag.

For a less extreme example `seed=4`, we start with a probability of  `0.7991` and reach `0.9900121` after 223 steps.

The last step is to convert into the profile string and submit it to the server to retreive the flag.

## Code

The code is available [here](script.py).

## Flag

`hackim19{wh0_kn3w_ml_w0uld_61v3_y0u_1337_fl465}`