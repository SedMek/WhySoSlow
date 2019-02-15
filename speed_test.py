import pyspeedtest
import time
import matplotlib.pyplot as plt
from statistics import mean
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


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


def to_time(timestamp):
    """
    converts an integer timestamp to a string date
    :param timestamp: integer timestamp in seconds
    :return: string date under format %Y-%m-%d %H:%M:%S
    """
    return datetime.utcfromtimestamp(timestamp).strftime('%H:%M')


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
    total_down = 0
    for i in range(len(down_list)):
        # print('------------- ', i, is_down, ' ------------')
        if down_list[i] <= value_trigger:
            total_down += 1
        if down_list[i] <= value_trigger and not is_down:
            is_down = True
            start_index = i
        if (down_list[i] > value_trigger or i == len(down_list) - 1) and is_down:
            is_down = False
            end_index = i
            if time_list[end_index] - time_list[start_index] > duration_trigger:
                # print(start_index, end_index)
                # print(down_list[start_index:end_index])
                save_complaint(to_datetime(time_list[start_index]), to_datetime(time_list[end_index]), value_trigger,
                               mean(down_list[start_index:end_index]))
                complaint_counter += 1
    print("Finished complaint report! {} complaint(s) were issued.".format(complaint_counter))
    return complaint_counter, total_down


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
        print('------------- run {} -----------'.format(i))
        time_list.append(round(time.time()))
        down_list.append(to_mbps(st.download()))
        time.sleep(frequency)
    return time_list, down_list


def download_graph(time_list, down_list, value_trigger):
    fig = plt.figure(figsize=(9, 2))
    plt.plot(time_list, down_list, 'b', time_list, [value_trigger for i in time_list], 'r')
    # print(plt.xticks())
    plt.xlabel('heures')
    plt.ylabel('débit (Mbps)')
    plt.xticks([time_list[0], time_list[int(len(time_list) / 2)], time_list[-1]],
               [to_time(time_list[0]), to_time(time_list[int(len(time_list) / 2)]), to_time(time_list[-1])])
    fig.savefig('fig.png'.format(to_datetime(time_list[0]).replace(':', '-')))


def down():
    frequency = 60
    time_list, down_list = download_info(frequency=frequency, duration_covered=1200, runs=5)
    save_records(time_list, down_list)
    value_trigger = 600
    duration_trigger = 120
    download_graph(time_list, down_list, value_trigger)
    complaint_counter, total_down = prepare_complaint(time_list, down_list, value_trigger, duration_trigger)
    if complaint_counter > 0:
        send_password_mail("sedmekipest@gmail.com", '0000', value_trigger, frequency, total_down, time_list)


def send_password_mail(user_mail, contract_number, value_trigger, frequency, total_down, time_list):
    gmail_user = "hetcompte@gmail.com"
    gmail_pwd = "08587428aqwzsx"
    TO = user_mail
    SUBJECT = "Réclamation débit faible - Contrat n:{}".format(contract_number)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)
    # BODY = '\r\n'.join(['To: %s' % TO,
    #                     'From: %s' % gmail_user,
    #                     'Subject: %s' % SUBJECT,
    #                     '', TEXT]).encode('utf-8')
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = SUBJECT
    msgRoot['From'] = gmail_user
    msgRoot['To'] = user_mail
    # Create the body of the message.
    html = """Bonjour Monsieur/Madame,
            <p>Je suis propriétaire du contrat n: {}. Je vous contacte suite à la baisse répétitive que je constate sur mon débit: le débit était inférieur à {}Mbps (alors que mon contrat est de 1000Mbps) pendant {}minutes entre {} et {} aujourd'hui comme illustré dans le graphe suivant:</p>
            <img src='cid:image1'>
            
            <p>Veuillez fixer ce problème dans les délais les plus courts.
            <p>Si cela ne vous est pas possible, je demande qu'on révise mon abonnement pour trouver un prix adapté au service médiocre que je reçois!
            <p>Bien cordialement,
            <p>Ghassen Hamdi \
           """.format(contract_number, value_trigger, (frequency * total_down) // 60, to_time(time_list[0]),
                      to_time(time_list[-1]))
    # Record the MIME types.
    msgHtml = MIMEText(html, 'html')
    # add the image
    image_file = 'fig.png'
    img = open(image_file, 'rb').read()
    msgImg = MIMEImage(img, 'png')
    msgImg.add_header('Content-ID', '<image1>')
    msgImg.add_header('Content-Disposition', 'inline', filename=image_file)
    # attach both parts
    msgRoot.attach(msgHtml)
    msgRoot.attach(msgImg)
    server.sendmail(gmail_user, [TO], msgRoot.as_string())
    server.quit()
    print('email sent')


if __name__ == "__main__":
    down()