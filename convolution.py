# 用两层CNN对MNIST进行分类
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
mnist=input_data.read_data_sets("MNIST_data/",one_hot=True)

x=tf.placeholder(tf.float32,[None,784])
y_real=tf.placeholder(tf.float32,[None,10])
# 因为要使用CNN,因此必须把输入数据转换成二维形状
# 第一个-1表示第一维的大小是根据x自动确定的,最后一个1表示这里的图片是单通道
x_image=tf.reshape(x,[-1,28,28,1])

# 用于创建卷积核
def weight_variable(shape):
    # 得到一个形状如shape,标准差为0.1的截断正态分布的tensor(期望默认为0)
    # 舍弃偏离期望大于2倍标准差的值
    initial=tf.truncated_normal(shape,stddev=0.1)
    return tf.Variable(initial)

# 用于创建卷积的偏置
def bias_variable(shape):
    # 得到一个形状如shape,全为0.1的常数tensor
    initial=tf.constant(0.1,shape=shape)
    return tf.Variable(initial)
# 进行卷积操作
def conv2d(x,W):
    # strides参数一般为[1,stride_h,stride_w,1],因为不想在batch和channels上做卷积
    # x和W分别为input和filter
    return tf.nn.conv2d(x,W,strides=[1,1,1,1],padding='SAME')
def max_pool_2x2(x):
    # 参数ksize：池化窗口的大小，取一个四维向量
    # 一般是[1, height, width, 1]，因为我们不想在batch和channels上做池化，所以这两个维度设为了1
    return tf.nn.max_pool(x,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')
# 一个卷积层的"标配":卷积、激活函数、池化
w_conv1=weight_variable([5,5,1,32])
b_conv1=bias_variable([32])
h_conv1=tf.nn.relu(conv2d(x_image,w_conv1)+b_conv1)
h_pool1=max_pool_2x2(h_conv1)
# 第二个卷积层
w_conv2=weight_variable([5,5,32,64])
b_conv2=bias_variable([64])
h_conv2=tf.nn.relu(conv2d(h_pool1,w_conv2)+b_conv2)
h_pool2=max_pool_2x2(h_conv2)
# 以下是两个全连接层
w_fc1=weight_variable([7*7*64,1024])
b_fc1=bias_variable([1024])
h_pool2_flat=tf.reshape(h_pool2,[-1,7*7*64])
h_fc1=tf.nn.relu(tf.matmul(h_pool2_flat,w_fc1)+b_fc1)

keep_prob=tf.placeholder(tf.float32)
h_fc1_drop=tf.nn.dropout(h_fc1,keep_prob)

w_fc2=weight_variable([1024,10])
b_fc2=bias_variable([10])
y_conv=tf.matmul(h_fc1_drop,w_fc2)+b_fc2

cross_entropy=tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_real,logits=y_conv))
# 定义训练步骤、学习率和目标
train_step=tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

correct_prediction=tf.equal(tf.argmax(y_conv,1),tf.argmax(y_real,1))
accuracy=tf.reduce_mean(tf.cast(correct_prediction,tf.float32))
# 创建会话并初始化变量
sess=tf.InteractiveSession()
sess.run(tf.global_variables_initializer())

for i in range(1000):
    batch=mnist.train.next_batch(50)
    if i%10==0:
        train_accuracy=accuracy.eval(feed_dict={x:batch[0],y_real:batch[1],keep_prob:1.0})
        print("step %d, training accuracy %g"%(i,train_accuracy))
    train_step.run(feed_dict={x:batch[0],y_real:batch[1],keep_prob:0.5})

print("test accuracy %g"%accuracy.eval(feed_dict={x:mnist.test.images,y_real:mnist.test.labels,keep_prob:1.0}))








