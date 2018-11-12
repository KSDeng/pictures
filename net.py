import caffe
from caffe import layers as L, params as P
from caffe.coord_map import crop

def conv_relu(bottom, nout, ks=3, stride=1, pad=1):
    conv = L.Convolution(bottom, kernel_size=ks, stride=stride,
        #num_output=nout, pad=pad,
        num_output=nout, pad=pad,weight_filler=dict(type='xavier'),
        param=[dict(lr_mult=1, decay_mult=1), dict(lr_mult=2, decay_mult=0)])
    #return conv, L.ReLU(conv, in_place=True, relu_param=dict(negative_slope=0.2))
    bn = L.BatchNorm(conv, use_global_stats=False)
    scale = L.Scale(bn, bias_term=True)
    return conv, L.ReLU(scale, in_place=True)

def deconv_relu(bottom, nout, ks=2, stride=2, pad=0):
    deconv = L.Deconvolution(bottom, convolution_param=dict(kernel_size=ks, stride=stride,
        num_output=nout, pad=pad, weight_filler=dict(type='xavier')),
        param=[dict(lr_mult=1, decay_mult=1), dict(lr_mult=2, decay_mult=0)])
    return deconv#, L.ReLU(deconv, in_place=True)
def deconv(bottom, nout, ks=2, stride=2, pad=0):
    deconv = L.Deconvolution(bottom, convolution_param=dict(kernel_size=ks, stride=stride,
        num_output=nout, pad=pad, weight_filler=dict(type='xavier')),
        param=[dict(lr_mult=1, decay_mult=1), dict(lr_mult=2, decay_mult=0)])
    return deconv#, L.ReLU(deconv, in_place=True)
def max_pool(bottom, ks=2, stride=2):
    return L.Pooling(bottom, pool=P.Pooling.MAX, kernel_size=ks, stride=stride)

def fcn(split):
    n = caffe.NetSpec()
    pydata_params = dict(split=split, mean=(100,100,100),
            seed=1337)
    if split == 'train':
        pydata_params['tub_dir'] = '/data/xujw/2017train'
        pylayer = 'TubSegDataLayer'
    else:
        pydata_params['tub_dir'] = '../2017test'
        pylayer = 'TubSegDataLayer'
    n.data, n.label = L.Python(module='tub_layers', layer=pylayer,
            ntop=2, param_str=str(pydata_params))

    # the base net
    n.conv1_1, n.relu1_1 = conv_relu(n.data, 64)
    #n.conv1_2, n.relu1_2 = conv_relu(n.relu1_1, 64)
    n.pool1 = max_pool(n.relu1_1)

    n.conv2_1, n.relu2_1 = conv_relu(n.pool1, 128)
    #n.conv2_2, n.relu2_2 = conv_relu(n.relu2_1, 128)
    n.pool2 = max_pool(n.relu2_1)

    n.conv3_1, n.relu3_1 = conv_relu(n.pool2, 256)
    #n.conv3_2, n.relu3_2 = conv_relu(n.relu3_1, 256)
    n.pool3 = max_pool(n.relu3_1)

    n.conv4_1, n.relu4_1 = conv_relu(n.pool3, 512)
    #n.conv4_2, n.relu4_2 = conv_relu(n.relu4_1, 512)
    #n.drop4_3 = L.Dropout(n.relu4_2, dropout_ratio=0.5, in_place=True)
    n.pool4 = max_pool(n.relu4_1)

    n.conv5_1, n.relu5_1 = conv_relu(n.pool4, 1024)
    #n.conv5_2, n.relu5_2 = conv_relu(n.relu5_1, 1024)
    #n.drop5_3 = L.Dropout(n.relu5_2, dropout_ratio=0.5, in_place=True)


    n.updeconv4_1 = deconv(n.relu5_1, 512)
    n.upconcat4 = L.Concat(n.updeconv4_1, n.relu4_1)
    n.upconv4_2, n.uprelu4_2 = conv_relu(n.upconcat4, 512)
    #n.upconv4_3, n.uprelu4_3 = conv_relu(n.uprelu4_2, 512)


    n.updeconv3_1 = deconv(n.uprelu4_2, 256)
    n.upconcat3 = L.Concat(n.updeconv3_1, n.relu3_1)
    n.upconv3_2, n.uprelu3_2 = conv_relu(n.upconcat3, 256)
    #n.upconv3_3, n.uprelu3_3 = conv_relu(n.uprelu3_2, 256)

    n.updeconv2_1 = deconv(n.uprelu3_2, 128)
    n.upconcat2 = L.Concat(n.updeconv2_1, n.relu2_1)
    n.upconv2_2, n.uprelu2_2 = conv_relu(n.upconcat2, 128)
    #n.upconv2_3, n.uprelu2_3 = conv_relu(n.uprelu2_2, 128)


    n.updeconv1_1 = deconv(n.uprelu2_2, 64)
    n.upconcat1 = L.Concat(n.updeconv1_1, n.relu1_1)
    n.upconv1_2, n.uprelu1_2 = conv_relu(n.upconcat1, 64)


    n.score = L.Convolution(n.uprelu1_2, num_output=6, kernel_size=1, pad=0,
            #weight_filler=dict(type='xavier'),
            param=[dict(lr_mult=1, decay_mult=1), dict(lr_mult=2, decay_mult=0)])


    #n.loss = L.InvariantLoss(n.score, n.label)
    #n.loss = L.L1WeightedLoss(n.score, n.label)
    #n.loss = L.EuclideanLoss(n.score, n.label)
    #n.loss = L.SecOrderLoss(n.score, n.label)

    n.loss = L.SoftmaxWithLoss(n.score, n.label,
               loss_param=dict(normalize=False))

    return n.to_proto()

def make_net():
    with open('train.prototxt', 'w') as f:
        string = str(fcn('train'))
	f.write(string)


    with open('test.prototxt', 'w') as f:
	string = str(fcn('test'))
        f.write(string)

if __name__ == '__main__':
    make_net()
