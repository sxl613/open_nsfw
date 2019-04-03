#!/usr/bin/python
import numpy as np
import os
os.environ['GLOG_minloglevel'] = '2'        # to disable Caffe logging during execution
import sys
import argparse
import glob
import time
from PIL import Image
from io import BytesIO
import caffe
import random
import checkFiletype as cft
import cv2
import classify_nsfw as clf

"""
Check file extension: if the saved extensions does not agree with MIME flag as suspicious.

For image:  return a probability score

For video:  do a custom check on frames and return a probability score

For other extensions: ignore
"""


class NSFWDetect(object):
    LOW_THRESH = 0.6
    MEDIUM_THRESH = 0.7
    HIGH_THRESH = 0.8
    FRAME_COUNT_THRESH = 8
    def __init__(self, model_def = None, pretrained_model = None, output_layers = None):
        # Pre-load caffe model.
        self.nsfw_net = caffe.Net(model_def,  # pylint: disable=invalid-name
            pretrained_model, caffe.TEST)

        # Load transformer
        # Note that the parameters are hard-coded for best results
        self.caffe_transformer = caffe.io.Transformer({'data': self.nsfw_net.blobs['data'].data.shape})
        self.caffe_transformer.set_transpose('data', (2, 0, 1))  # move image channels to outermost
        self.caffe_transformer.set_mean('data', np.array([104, 117, 123]))  # subtract the dataset-mean value in each channel
        self.caffe_transformer.set_raw_scale('data', 255)  # rescale from [0, 1] to [0, 255]
        self.caffe_transformer.set_channel_swap('data', (2, 1, 0))  # swap channels from RGB to BGR

        self.output_layers = output_layers

    
    def classify_image(self, filepath):
        """
        Assumes filepath points to an image file.

        Returns a score based on the image.
        
        Raises:
            IOError if the filepath points to a file that does not exist, or if something goes wrong during file opening
        """
        print('Classify image')
        return self.caffe_preprocess_and_compute(Image.open(filepath))
    
    def classify_video(self, filepath):
        """
        Assumes filepath points to a video file.

        Returns a score based on the frames of the video.

        Goes through floor(sqrt(frame_count)) random frames from the video and checks the maximum of the explicitness scores. If that is bigger than a 
        threshold, go through the video file from the beginning: if any frame exceeds the threshold, flag it as explicit. Else flag as nonexplicit.
        
        Raises:
            IOError if the filepath points to a file that does not exist, or if something goes wrong during file opening
        """
        print('Classify video')
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            raise IOError("File does not exist / argument is not a file.")
        vidcap = cv2.VideoCapture(filepath)
        framecount = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
        n = framecount ** 0.5
        frames = []
        frame_scores = []
        print('Frame count is ', framecount)
        for i in range(int(n) + 1):
            vidcap.set(cv2.CAP_PROP_POS_FRAMES, random.randrange(framecount))
            success, image = vidcap.read()
            if success:
                frames.append(Image.fromarray(image))
        print('Loaded frames')
        for frame in frames:
            frame_scores.append(self.caffe_preprocess_and_compute(frame)[1])
        frame_scores = np.array(frame_scores)
        print(frame_scores)
        if np.sum(frame_scores >= self.LOW_THRESH) > self.FRAME_COUNT_THRESH or np.sum(frame_scores >= self.LOW_THRESH) == 0:
            return np.max(frame_scores)
        thresh = np.max(frame_scores)
        i = 0
        im = None
        while i < framecount:
            vidcap.set(cv2.CAP_PROP_POS_FRAMES, i)
            success, image = vidcap.read()
            if success:
                im = Image.fromarray(image)
            sc = self.caffe_preprocess_and_compute(im)[1]
            if sc >= thresh:
                return sc
            i += 1
        return 0.0

        

    
    def caffe_preprocess_and_compute(self, img):
        """
        Run a Caffe network on an input image after preprocessing it to prepare
        it for Caffe.
        :param  img:
            image to be input into Caffe.
        :param caffe.Net self.nsfw_net:
            A Caffe network with which to process pimg afrer preprocessing.
        :param list self.output_layers:
            A list of the names of the layers from caffe_net whose outputs are to
            to be returned.  If this is None, the default outputs for the network
            are returned.
        :return:
            Returns the requested outputs from the Caffe net.
        """
        if self.nsfw_net is not None:

            # Grab the default output names if none were requested specifically.
            if self.output_layers is None:
                self.output_layers = self.nsfw_net.outputs

            img_data_rs = NSFWDetect.resize_image(img, sz=(256, 256))
            image = caffe.io.load_image(BytesIO(img_data_rs))

            H, W, _ = image.shape
            _, _, h, w = self.nsfw_net.blobs['data'].data.shape
            h_off = max((H - h) / 2, 0)
            w_off = max((W - w) / 2, 0)
            crop = image[h_off:h_off + h, w_off:w_off + w, :]
            transformed_image = self.caffe_transformer.preprocess('data', crop)
            transformed_image.shape = (1,) + transformed_image.shape

            input_name = self.nsfw_net.inputs[0]
            all_outputs = self.nsfw_net.forward_all(blobs=self.output_layers,
                        **{input_name: transformed_image})

            outputs = all_outputs[self.output_layers[0]][0].astype(float)
            return outputs
        else:
            return []
    
    def run(self, filepath):
        filetype_check, file_extension, mime_extension, filetype = cft.checkFiletype(filepath)

        if file_extension != mime_extension:
            print('Suspicious file: extensions don\'t match up. File extension: {}, MIME extension: {}'.format(file_extension, mime_extension))
        
        if filetype == 'image':
            print('NSFW score: ', self.classify_image(filepath))
        if filetype == 'video':
            print('NSFW score: ', self.classify_video(filepath))
        else:
            print('Not image/video')
            return None

    @classmethod
    def resize_image(cls, im, sz=(256, 256)):
        """
        Resize image. Please use this resize logic for best results instead of the 
        caffe, since it was used to generate training dataset 
        :param PIL Image im:
            The image data
        :param sz tuple:
            The resized image dimensions
        :returns bytearray:
            A byte array with the resized image
        """
        #img_data = str(data)
        #im = Image.open(img_data)
        if im.mode != "RGB":
            im = im.convert('RGB')
        imr = im.resize(sz, resample=Image.BILINEAR)
        fh_im = BytesIO()
        imr.save(fh_im, format='JPEG')
        fh_im.seek(0)
        return bytearray(fh_im.read())






