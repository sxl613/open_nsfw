#!/usr/bin/python
import magic
import os
import argparse

MIME_DICT = {
"flv" : "x-flv",
"mp4" : "mp4",
"m3u8" : "x-mpegurl",
"ts" : "MP2T",
"3gp" : "3gpp",
"mov" : "quicktime",
"avi" : "x-msvideo",
"wmv" : "x-ms-wmv",
"mkv" : "x-matroska",
"webm" : "webm",
"mpe" : "mpeg",
"mpg" : "mpeg",
"mpeg" : "mpeg",
"mp2" : "mp2",
"mpa" : "mpeg",
"mpv2" : "mpeg",
"bmp" : "bmp",	
"cod" : "cis-cod",	
"gif" : "gif",	
"ief" : "ief",	
"jpe" : "jpeg",	
"png" : "png",
"jpeg" : "jpeg",	
"jpg" : "jpeg",	
"jfif" : "pipeg",	
"svg" : "svg+xml",	
"tif" : "tiff",	
"tiff" : "tiff",	
"ras" : "x-cmu-raster",	
"cmx" : "x-cmx",	
"ico" : "x-icon"
}

def checkFiletype(filepath):
    """
    Args:
        filepath: path to file to be checked

    Returns:
        A tuple (True/False, file extension from filename, mime file extension, file_type <video, image, application, etc.>)

    Raises:
        IOError if the filepath points to a file that does not exist, or if something goes wrong during file opening
    """
    
    filepath = os.path.normpath(filepath) 
    _, file_extension = os.path.splitext(filepath)
    file_extension = file_extension[1:]
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        raise IOError("File does not exist / checkFiletype's argument is not a file.")
    file_type, mime_extension = magic.from_file(filepath, mime = True).lower().split('/')
    if not (file_type == 'video' or file_type == 'image'):
        return False, file_extension, mime_extension, file_type
    
    if MIME_DICT[file_extension] == mime_extension:
        return True, file_extension, mime_extension, file_type
    
    return False, file_extension, mime_extension, file_type


def isImage(filepath):
    """
        Return True if file at filepath is an image.
    """
    filepath = os.path.normpath(filepath)
    return magic.from_file(filepath, mime = True).split('/')[0] == 'image'

def isVideo(filepath):
    """
        Return True if file at filepath is a video.
    """
    filepath = os.path.normpath(filepath)
    return magic.from_file(filepath, mime = True).split('/')[0] == 'video'
