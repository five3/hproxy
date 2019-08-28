#!/usr/bin/env python
# coding=utf-8
from setuptools import setup, find_packages
# http://www.cnblogs.com/UnGeek/p/5922630.html
# http://blog.konghy.cn/2018/04/29/setup-dot-py/
# python setup.py sdist
# python setup.py bdist
# python setup.py bdist_egg
# python setup.py bdist_wheel
setup( 
    name="HProxy",
    version="0.1.{buildno}",
    keywords=("http proxy", "proxy base on host"),
    description="http proxy base on host",
    long_description="http proxy base on host",
    license="GPL V3",

    url="https://git.corpautohome.com/chenxiaowu/hproxy",
    author="Xiaowu Chen",
    author_email="chenxiaowu@autohome.com.cn",

    package_dir={'HProxy': 'HProxy'},         # 指定哪些包的文件被映射到哪个源码包
    packages=['HProxy'],       # 需要打包的目录。如果多个的话，可以使用find_packages()自动发现
    include_package_data=True,
    py_modules=[],          # 需要打包的python文件列表
    data_files=[],          # 打包时需要打包的数据文件
    platforms="any",
    install_requires=[      # 需要安装的依赖包
        'requests>=2.19.1',
        'flask>=1.0.2',
        'gunicorn>=19.9.0',
        'gevent>=1.4.0'
    ],
    scripts=[],             # 安装时需要执行的脚本列表
    entry_points={
        'console_scripts': [    # 配置生成命令行工具及入口
            'hproxy = HProxy:main'
        ]
    },
    classifiers=[           # 程序的所属分类列表
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    zip_safe=False
)
