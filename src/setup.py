'''
Created on 22-08-2011

@author: arkus
'''

from distutils.core import setup
setup(name='BumblePyy',
      version='0.1',
      author="@rkus",
      author_email="arkusx@gmail.com",
      url="http://github.com/glorpen/bumblepyy",
      packages=['bumblepyy'],
      provides="bumblepyy",
      requires=[
        "configobj", "python-daemon"
      ],
      data_files=[
        ('/etc/dbus-1/system.d', ['bumblepyy/dbus/org.bumblepyy.conf']),
        ('/etc', ['bumblepyy/bumblepyy.conf'])
      ],
      scripts=['bumblepyy/scripts/bumblepyy', 'bumblepyy/scripts/optirun'],
)

