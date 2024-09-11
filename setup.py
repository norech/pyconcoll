from setuptools import setup

setup(
    name='pyconcoll',
    version='0.1.0',
    description='Connected Collections',
    url='https://github.com/norech/pyconcoll',
    author='Alexis Cheron',
    author_email='contact@norech.com',
    license='BSD 2-clause',
    packages=['pyconcoll'],
    install_requires=['sortedcollections>=2.0.1'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
