from distutils.core import setup
import py2exe

setup(windows = ['__main__.py'], data_files = [('images',['beastmaster_v_warlock.png','druid_v_necromancer.png','forcemaster_v_warlord.png','wizard_v_priestess.png','arial10x10.png'])])

#to run, use command line to this directory ending with \python.exe setup.py py2exe
