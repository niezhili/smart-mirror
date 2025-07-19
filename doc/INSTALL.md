首先创建conda环境:
conda create -n smartmirror python=3.8
然后进入环境:
conda activate smartmirror
安装所需依赖(注意：下面的依赖是在win平台的下安装的，在树莓派上尝试去除版本号)：
pip install -r requirements.txt
如果遇到下面错误：
1.ERROR: Failed to build installable wheels for some pyproject.toml based projects (dlib)
这是因为缺少编译环境，可以使用conda来安装预编译的dlib：
conda install -c conda-forge dlib
