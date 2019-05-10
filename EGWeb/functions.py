import tensorflow as tf
import numpy as np
import os, argparse, time, random
from EGWeb.BiLSTMCRF import BiLSTM_CRF
from EGWeb.BiLSTMutils import str2bool, get_entity
from EGWeb.BiLSTMData import read_dictionary, tag2label, random_embedding


def trigger_extract(content):
    result = {}

    args = {
        'batch_size':64,    # sample of each minibatch
        'epoch':40,         # epoch of training
        'hidden_dim':300,   # dim of hidden state
        'optimizer':'Adam',   # Adam/Adadelta/Adagrad/RMSProp/Momentum/SGD
        'CRF': True,        # use CRF at the top layer. if False, use Softmax
        'lr': 0.001,        # learning rate
        'clip':5.0,         # gradient clipping
        'dropout':0.5,      # dropout keep_prob
        'update_embedding':True,    # update embedding during training
        'embedding_dim':300,    # random init char embedding_dim
        'shuffle':True      # shuffle training data before each epoch
    }


    ## get char embeddings
    word2id = read_dictionary('data/word2id.pkl')    # 用以统计字的个数
    embeddings = random_embedding(word2id, args['embedding_dim'])  # 对字向量进行随机初始化

    ## paths setting
    paths = {}
    timestamp = '1552302320' # demo_model
    output_path = os.path.join('.', "data_save", timestamp)
    if not os.path.exists(output_path): os.makedirs(output_path)
    model_path = os.path.join(output_path, "checkpoints/")
    if not os.path.exists(model_path): os.makedirs(model_path)
    ckpt_file = tf.train.latest_checkpoint(model_path)
    paths['model_path'] = ckpt_file
    
    model = BiLSTM_CRF(args, embeddings, tag2label, word2id, paths)
    model.build_graph()
    saver = tf.train.Saver()
    with tf.Session() as sess:
        saver.restore(sess, ckpt_file)
        demo_sent = list(content.strip())
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        tag = model.demo_one(sess, demo_data)
        VERB, NOUN= get_entity(tag, demo_sent)
        result['VERB'] = VERB
        result['NOUN'] = NOUN
    return result