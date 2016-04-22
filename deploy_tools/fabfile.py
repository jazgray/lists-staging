'''
Created on Apr 21, 2016

@author: Jim
'''
from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, settings, sudo
import random
#paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG) 

REPO_URL = 'https://github.com/jazgray/lists-staging'


def _create_directory_structure_if_necessary(site_folder):
  for subfolder in ('database', 'static', 'virtualenv', 'source'):
    sudo('mkdir -p %s/%s' % (site_folder, subfolder), user=env.user)
      
def _get_latest_source(source_folder):
  with settings(sudo_user=env.user):
    if exists(source_folder + '/.git'):
      sudo('cd %s && git fetch' % (source_folder,))
    else:
      sudo('git clone %s %s' % (REPO_URL, source_folder))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    sudo('cd %s && git reset --hard %s' % (source_folder, current_commit))
  
def _update_settings(source_folder, site_name):
  with settings(sudo_user=env.user):
    settings_path = source_folder + '/mysite/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False", use_sudo=True)
    sed(settings_path,
      'ALLOWED_HOSTS =.+$',
      'ALLOWED_HOSTS = ["%s"]' % (site_name,), use_sudo=True
    )
    secret_key_file = source_folder + '/mysite/secret_key.py'
    if not exists(secret_key_file):
      chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
      key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
      append(secret_key_file, "SECRET_KEY = '%s'" % (key,),use_sudo=True )
    append(settings_path, '\nfrom .secret_key import SECRET_KEY', use_sudo=True)
  
def _update_virtualenv(source_folder):
  with settings(sudo_user=env.user):
    virtualenv_folder = source_folder + '/../virtualenv'
    if not exists(virtualenv_folder + '/bin/pip'):
      sudo('virtualenv --python=python3.4 %s' % (virtualenv_folder,))
    sudo('%s/bin/pip install -r %s/requirements.txt' % (
      virtualenv_folder, source_folder
    ))

def _update_static_files(source_folder):
  with settings(sudo_user=env.user):
    sudo('cd %s && ../virtualenv/bin/python3.4 manage.py collectstatic --noinput' % 
    (source_folder,))
  
def _update_database(source_folder):
  with settings(sudo_user=env.user):
    sudo('cd %s && ../virtualenv/bin/python3.4 manage.py migrate --noinput' % 
      (source_folder,))

def deploy():
  
  with settings(user='jim'):
    
    site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    print (site_folder)
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(source_folder)
    _update_static_files(source_folder)
    _update_database(source_folder)