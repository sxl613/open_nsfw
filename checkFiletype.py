import magic
import os
import argparse

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
    if file_extension == ".jpg":
        file_extension = ".jpeg"
    file_extension = file_extension[1:]
    if not os.path.exists(filepath) or not os.path.isfile(filepath):
        raise IOError("File does not exist / checkFiletype's argument is not a file.")
    file_type, mime_extension = magic.from_file(filepath, mime = True).split('/')
    if mime_extension == file_extension:
        return True, file_extension, mime_extension, file_type
    else:
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






    

