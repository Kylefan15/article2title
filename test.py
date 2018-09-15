import tensorflow as tf
import pickle
from model import Model
from utils import build_dict, build_dataset, batch_iter
import numpy as np

with open("args.pickle", "rb") as f:
    args = pickle.load(f)

print("Loading dictionary...")
word_dict, reversed_dict, article_max_len, summary_max_len = build_dict("valid", args.toy)
print("Loading validation dataset...")
valid_x, valid_y = build_dataset("valid", word_dict, article_max_len, summary_max_len, args.toy)
print('------valid_x:', len(valid_x), type(valid_x), np.shape(valid_x))
print('------valid_y:', len(valid_y), type(valid_y), np.shape(valid_y))
valid_x_len = list(map(lambda x: len([y for y in x if y != 0]), valid_x))
print('------valid_x_len:', len(valid_x_len), type(valid_x_len), np.shape(valid_x_len), valid_x_len)

with tf.Session() as sess:
    print("Loading saved model...")
    model = Model(reversed_dict, article_max_len, summary_max_len, args, forward_only=True)
    saver = tf.train.Saver(tf.global_variables())
    ckpt = tf.train.get_checkpoint_state("./saved_model/")
    saver.restore(sess, ckpt.model_checkpoint_path)

    batches = batch_iter(valid_x, valid_y, args.batch_size, 1)

    print("Writing summaries to 'result.txt'...")
    for batch_x, batch_y in batches:
        batch_x_len = list(map(lambda x: len([y for y in x if y != 0]), batch_x))

        print('batch_x:', len(batch_x), type(batch_x), np.shape(batch_x))
        print(batch_x)
        valid_feed_dict = {
            model.batch_size: len(batch_x),
            model.X: batch_x,
            model.X_len: batch_x_len,
        }

        prediction = sess.run(model.prediction, feed_dict=valid_feed_dict)
        prediction_output = list(map(lambda x: [reversed_dict[y] for y in x], prediction[:, 0, :]))

        with open("result.txt", "a") as f:
            for line in prediction_output:
                summary = list()
                for word in line:
                    if word == "</s>":
                        break
                    if word not in summary:
                        summary.append(word)
                print(" ".join(summary), file=f)

    print('Summaries are saved to "result.txt"...')
