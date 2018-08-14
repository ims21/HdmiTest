from distutils.core import setup
import setup_translate

pkg = 'Extensions.HdmiTest'
setup (name = 'enigma2-plugin-extensions-hdmitest',
       version = '0.44',
       description = 'plugin for monitoring and testing HDMI-CEC',
       packages = [pkg],
       package_dir = {pkg: 'plugin'},
       package_data = {pkg: ['locale/*.pot', 'locale/*/LC_MESSAGES/*.mo']},
       cmdclass = setup_translate.cmdclass, # for translation
      )
