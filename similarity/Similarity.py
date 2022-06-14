import time
import tensorflow as tf2
tf = tf2.compat.v1
from similarity.buildGraph import build_graph
import matplotlib.pyplot as plt
import cv2
import os
from glob import glob

from PIL import Image
tf.logging.set_verbosity(tf.logging.ERROR)

def compare(target_img_path, input_img_paths):
    
  #====================================================================================

  # Load bytes of image files
  image_bytes = [tf.gfile.GFile(name, 'rb').read()
                for name in [target_img_path] + input_img_paths]

  hub_module_url = "https://tfhub.dev/google/imagenet/mobilenet_v2_100_96/feature_vector/1" #@param {type:"string"}

  with tf.Graph().as_default():
    input_byte, similarity_op = build_graph(hub_module_url, target_img_path)
    
    with tf.Session() as sess:
      sess.run(tf.global_variables_initializer())
      t0 = time.time() # for time check
      
      # Inference similarities
      similarities = sess.run(similarity_op, feed_dict={input_byte: image_bytes})
      
      print("%d images inference time: %.2f s" % (len(similarities), time.time() - t0))

  # 유사도 내림차순으로 정렬
  randDic = {}
  for similarity, input_img_path in zip(similarities[1:], input_img_paths):
    randDic[similarity] = input_img_path

  return randDic

  # # Display results
  # fig = plt.figure()
  # rows = 1
  # cols = 5
  # col = 1

  # #target
  # img1 = cv2.imread(target_img_path)
  # ax1 = fig.add_subplot(rows, cols, col)
  # ax1.imshow(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))
  # ax1.set_xlabel("- similarity: %.2f" % similarities[0])
  # ax1.set_xticks([]), ax1.set_yticks([])
  # ax1.set_title('Target')

  # #input images
  # for similarity, input_img_path in sortedDict.items():
  #     col = col + 1
  #     img = cv2.imread(input_img_path)
  #     ax = fig.add_subplot(rows, cols, col)
  #     ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
  #     ax.set_xlabel("similarity: %.2f" % similarity)
  #     ax.set_xticks([]), ax.set_yticks([])
  #     ax.set_title("Input" + str(col))
  #     if (col == 5): break
  # plt.show()

  [os.remove(f) for f in glob(r"images\*.jpeg")]
