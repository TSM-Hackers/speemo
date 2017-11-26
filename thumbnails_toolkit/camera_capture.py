import cv2


def capture_snapshot(filename):
    """Capture a snapshot, returns a cv2 image image

    Parameters
    ----------
    filename : str
        name of a file to store the image 

    Returns
    -------
    PIL.Image
        data for the pil image
    """
    # Camera 0 is the integrated web cam on my netbook
    camera_port = 0

    # Number of frames to throw away while the camera adjusts to light levels
    ramp_frames = 30

    # Now we can initialize the camera capture object with the cv2.VideoCapture class.
    # All it needs is the index to a camera port.
    camera = cv2.VideoCapture(camera_port)

    # Captures a single image from the camera and returns it in PIL format
    def get_image(camera):
        # read is the easiest way to get a full image out of a VideoCapture object.
        retval, im = camera.read()
        return im

    # Ramp the camera - these frames will be discarded and are only used to allow v4l2
    # to adjust light levels, if necessary
    for i in range(ramp_frames):
        temp = get_image(camera)
    print("Taking image...")
    # Take the actual image we want to keep
    camera_capture = get_image(camera)

    # A nice feature of the imwrite method is that it will automatically choose the
    # correct format based on the file extension you provide. Convenient!
    cv2.imwrite(filename, camera_capture)

    # You'll want to release the camera, otherwise you won't be able to create a new
    # capture object until your script exits
    del(camera)

    return camera_capture
