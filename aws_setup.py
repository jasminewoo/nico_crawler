from core import config

if __name__ == '__main__':
    aws_region = input('aws_region:')
    aws_access_key_id = input('aws_access_key_id:')
    aws_secret_access_key = input('aws_secret_access_key:')

    kvps = {
        'aws_region': aws_region,
        'aws_access_key_id': aws_access_key_id,
        'aws_secret_access_key': aws_secret_access_key
    }

    config.save('config_secret.json', kvps)
