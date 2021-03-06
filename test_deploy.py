import tensorflow as tf
import pickle
from model import Model
from utils import build_dict, build_dataset, batch_iter, build_deploy
import numpy as np
import time

t2 = time.time()

with open("args.pickle", "rb") as f:
    args = pickle.load(f)

str_from = 'five-time world champion michelle kwan withdrew from the #### us figure skating championships on wednesday , but will petition us skating officials for the chance to compete at the #### turin olympics .'

print("Loading dictionary...")
word_dict, reversed_dict, article_max_len, summary_max_len = build_dict("valid", args.toy)
valid_x, valid_y = build_deploy(str_from, word_dict, article_max_len, summary_max_len)
valid_x_len = list(map(lambda x: len([y for y in x if y != 0]), valid_x))

sess = tf.InteractiveSession()
print("Loading saved model...")
t1 = time.time()
model = Model(reversed_dict, article_max_len, summary_max_len, args, forward_only=True)
saver = tf.train.Saver(tf.global_variables())
ckpt = tf.train.get_checkpoint_state("./saved_model/")
saver.restore(sess, ckpt.model_checkpoint_path)
print('load model time:', str(time.time() - t1) + 's')

batches = batch_iter(valid_x, valid_y, args.batch_size, 1)

print("Start auto summarization...")
for batch_x, batch_y in batches:
    batch_x_len = list(map(lambda x: len([y for y in x if y != 0]), batch_x))
    valid_feed_dict = {
        model.batch_size: len(batch_x),
        model.X: batch_x,
        model.X_len: batch_x_len,
    }
    t0 = time.time()
    prediction = sess.run(model.prediction, feed_dict=valid_feed_dict)
    prediction_output = list(map(lambda x: [reversed_dict[y] for y in x], prediction[:, 0, :]))

    print('inference time:', str(time.time()-t0)+'s')

    line = prediction_output[0]
    summary = list()
    for word in line:
        if word == "</s>":
            break
        if word not in summary:
            summary.append(word)
    title_pred = " ".join(summary)
    print('title_pred:', '---- '+title_pred+'.')

print('run time:', str(time.time() - t2) + 's')
