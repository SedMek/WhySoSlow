import pyspeedtest
import time
import matplotlib.pyplot as plt
from statistics import mean
from datetime import datetime


def main():
    """
    Demonstration of pyspeedtest module
    :return: None
    """
    st = pyspeedtest.SpeedTest(runs=5)
    print('st.ping:', st.ping(), 'ms')
    print('st.download:', st.download() / (1024 * 1024), 'Mbps')
    print('st.upload:', st.upload() / (1024 * 1024), 'Mbps')


def save_records(time_list, down_list, filename='down.txt'):
    """
    saves the mesured download speed and the time of the measurement to a local text file
    :param down_list: download info
    :param time_list: time info (timestamp)
    :param filename: local storage file name
    :return: None
    """
    with open(filename, 'a') as the_file:
        the_file.write(str(time_list) + ';' + str(down_list) + '\n')


def to_mbps(value):
    """
    converts from bytes to Mb
    :param value: the value in bytes
    :return: the value in Mb
    """
    return round(value / (1024 * 1024))


def to_datetime(timestamp):
    """
    converts an integer timestamp to a string date
    :param timestamp: integer timestamp in seconds
    :return: string date under format %Y-%m-%d %H:%M:%S
    """
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def save_complaint(start_time, end_time, trigger_value, mean_value, filename='complaint.txt'):
    """
    Stores a complaint start_time + ';' + end_time + ';' + str(trigger_value) + ';' + str(mean_value) in a local text file
    :param start_time: the time when the download speed fell below the trigger_value
    :param end_time: the time when the download speed got over the trigger_value again
    :param trigger_value: the threshold value of download speed: if the speed is under this value, a complaint is issued
    :param mean_value: the mean value of donwload speed between start_time and end_time
    :param filename: local storage file name
    :return: None
    """
    with open(filename, 'a') as the_file:
        the_file.write(start_time + ';' + end_time + ';' + str(trigger_value) + ';' + str(mean_value) + '\n')


def prepare_complaint(time_list, down_list, value_trigger, duration_trigger):
    start_index = 0
    end_index = len(time_list) - 1
    is_down = False
    complaint_counter = 0
    for i in range(len(down_list)):
        print('------------- ', i, is_down, ' ------------')
        if down_list[i] <= value_trigger and not is_down:
            is_down = True
            start_index = i
        if (down_list[i] > value_trigger or i == len(down_list) - 1) and is_down:
            is_down = False
            end_index = i
            if time_list[end_index] - time_list[start_index] > duration_trigger:
                print(start_index, end_index)
                print(down_list[start_index:end_index])
                save_complaint(to_datetime(time_list[start_index]), to_datetime(time_list[end_index]), value_trigger,
                               mean(down_list[start_index:end_index]))
                complaint_counter += 1
    print("Finished complaint report! {} complaint(s) were issued.".format(complaint_counter))


def download_info(frequency=10, duration_covered=300, runs=5):
    """
    unit is Mbps
    :param frequency:
    :param duration_covered: in seconds
    :return:
    """
    st = pyspeedtest.SpeedTest(runs=runs)
    down_list = []
    time_list = []
    time_formatted_list = []
    for i in range(round(duration_covered / frequency)):
        time_list.append(round(time.time()))
        down_list.append(to_mbps(st.download()))
        time.sleep(frequency)
    return time_list, down_list


def download_graph(time_list, down_list, value_trigger):
    fig = plt.figure()
    plt.plot(time_list, down_list, 'b', time_list, [value_trigger for i in time_list], 'r')
    fig.savefig('plots/{}.png'.format(to_datetime(time_list[0]).replace(':','-')))


def down():
    time_list, down_list = download_info(frequency=60, duration_covered=1800, runs=5)
    save_records(time_list, down_list)
    value_trigger = 500
    duration_trigger = 120
    download_graph(time_list, down_list, value_trigger)
    prepare_complaint(time_list, down_list, value_trigger, duration_trigger)


if __name__ == "__main__":
    down()

    # time_list = [1545563002 + 60 * i for i in range(10)]
    # down_list = [10, 9, 3, 2, 1, 7, 8, 4, 5, 6]
    # down_list = [i*1024*1024 for i in down_list]
    # print(to_datetime(time.time()), type(time.time()))
    # prepare_complaint(down_list, time_list, 3, 60)
    # pass
