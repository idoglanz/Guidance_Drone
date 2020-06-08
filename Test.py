import os
import sys
import time
import cv2
import tempfile
from pathlib import Path
airsim_dir_path = str(Path(os.getcwd()).parent) + '/AirSim/PythonClient/'
sys.path.append(airsim_dir_path)
from airsim import *


def test_drone():
    client = MultirotorClient()
    client.confirmConnection()
    client.enableApiControl(True)
    client.armDisarm(True)
    client.takeoffAsync()
    time.sleep(2)

    trajectory = [[0,0,-10,5], [10,10,-15,5], [10,-10,-15,5], [-10,-10,-15,10], [-10,10,-15,5], [10,10,-15,5], [0,0,-1,2]]

    for traj in trajectory:
        state = client.getMultirotorState()
        quad_pos = state.kinematics_estimated.position
        quad_vel = state.kinematics_estimated.linear_velocity
        print('>>>>> flying to:', traj)
        client.moveToPositionAsync(*traj).join()
        print('current velocities:', quad_vel)
        print('current position:', quad_pos, "\n\n")
        print('--------------------------------')
        # get_images(client)
        time.sleep(1)

    client.landAsync().join()


def get_images(client):
    responses = client.simGetImages([
        ImageRequest("0", ImageType.DepthVis),  # depth visualization image
        ImageRequest("1", ImageType.DepthPerspective, True),  # depth in perspective projection
        ImageRequest("1", ImageType.Scene),  # scene vision image in png format
        ImageRequest("1", ImageType.Scene, False,
                            False)])  # scene vision image in uncompressed RGBA array
    print('Retrieved images: %d' % len(responses))

    tmp_dir = os.path.join(os.getcwd(), "/pics")
    print("Saving images to %s" % tmp_dir)
    # try:
    #     os.makedirs(tmp_dir)
    # except OSError:
    #     if not os.path.isdir(tmp_dir):
    #         raise

    for idx, response in enumerate(responses):

        filename = os.path.join(tmp_dir, str(idx))

        if response.pixels_as_float:
            print("Type %d, size %d" % (response.image_type, len(response.image_data_float)))
            write_pfm(os.path.normpath(filename + '.pfm'), get_pfm_array(response))
        elif response.compress:  # png format
            print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
            write_file(os.path.normpath(filename + '.png'), response.image_data_uint8)
        else:  # uncompressed array
            print("Type %d, size %d" % (response.image_type, len(response.image_data_uint8)))
            img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)  # get numpy array
            img_rgb = img1d.reshape(response.height, response.width, 3)  # reshape array to 4 channel image array H X W X 3
            cv2.imwrite(os.path.normpath(filename + '.png'), img_rgb)  # write to png


# def test_get_images_at_positions():
#     from MultiRotorConnector import MultiRotorConnector
#     connector = MultiRotorConnector()
#
#     _ = connector.get_frame(path='dummy.png')
#     position = connector.get_position()
#     x_val = position.x_val
#     y_val = position.y_val
#     z_val = position.z_val
#     print("Initial Positions:", x_val, y_val, z_val)
#
#     count = 0
#     for i,z in enumerate([-9, -6, -3, 0, 3, 6, 9]):
#         for j,x in enumerate([0, 5, -5]):
#             for k,y in enumerate([0, 5, -5]):
#                 connector.move_to_position([x_val+x, y_val+y, z_val+z])
#                 time.sleep(1)
#                 path = 'TF_ObjectDetection/data/orig_data/' + str(count) + '.png'
#                 count += 1
#                 _ = connector.get_frame(path=path)
#                 print("\tTest Case:", x_val+x, y_val+y, z_val+z, path)

if __name__ == '__main__':
    test_drone()
