"""Get thumbnail given a picture"""
import time
import requests


_region = 'westcentralus'  # Here you enter the region of your subscription
_url = 'https://{}.api.cognitive.microsoft.com/vision/v1.0/generateThumbnail'.format(_region)
_key = '3ac00f829fca4195ad7e4109ef22a525'  # Here you have to paste your primary key
_maxNumRetries = 10


def processRequest(json, data, headers, params):
    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:

        response = requests.request('post', _url, json=json, data=data, headers=headers, params=params)

        if response.status_code == 429:

            print("Message: %s" % (response.json()))

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()))

        break

    return result


def get_thumbnail(raw_image):
    """Get the raw data for image using MICoft API"""

    # Computer Vision parameters
    params = {'width': '150',
              'height': '150',
              'smartCropping': 'true'}

    headers = {
        # Request headers.
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': _key,
    }

    json = None

    result = processRequest(json, raw_image, headers, params)
    return result
