import os
import pickle
import getpass


def user_auth():
    user_config_file = '.UserConfig.pkl'
    if os.path.exists(user_config_file):
        with open(user_config_file, 'rb') as userConfigFileRb:
            user_info = pickle.load(userConfigFileRb)
            print(user_info)
    else:
        user_info = user_config()
        with open(user_config_file, 'wb') as userConfigFileWb:
            pickle.dump(user_info, userConfigFileWb)


def user_config():
    print('You never config user information.')
    print('App need to login to protect your data.')
    print('So you should take a few minutes to config your information.')
    email = input('E-mail: ')
    while True:
        passwd = getpass.getpass('Password: ')
        passwd_repeat = getpass.getpass('Password repeat: ')
        if passwd_repeat != passwd:
            print('Two passwords is not match. Please check.')
        else:
            print('Congratulations! You finish the information config.')
            return {'email': email, 'passwd': passwd}
