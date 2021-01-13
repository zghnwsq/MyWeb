import os
import zipfile
import glob


def unzip_file(dir_path, unzip_file_path):
    # 找到压缩文件夹
    dir_list = glob.glob(dir_path)
    if dir_list:
        # 循环zip文件夹
        for dir_zip in dir_list:
            # 以读的方式打开
            with zipfile.ZipFile(dir_zip, 'r') as f:
                for file in f.namelist():
                    f.extract(file, path=unzip_file_path)
            os.remove(dir_zip)


def zip_files(dir_path, zip_path):
    """
    :param dir_path: 需要压缩的文件目录
    :param zip_path: 压缩后的目录
    :return:
    """
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as f:
        for root, _, file_names in os.walk(dir_path):
            for filename in file_names:
                f.write(os.path.join(root, filename), filename)


def zip_file(file_path, zip_path):
    """
    :param file_path: 需要压缩的文件
    :param zip_path: 压缩后的目录
    :return:
    """
    file_name = file_path.split(os.sep)[-1]
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as f:
        f.write(file_path, file_name)


def zip_dir(dir_path, zip_path):
    """
    :param dir_path: 需要压缩的文件目录
    :param zip_path: 压缩后的目录
    :return:
    """
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as f:
        for d_path, dir_names, file_names in os.walk(dir_path):
            f_path = d_path.replace(dir_path, '')
            f_path = f_path and f_path + os.sep or ''
            for file_name in file_names:
                f.write(os.path.join(d_path, file_name), f_path + file_name)



# zip_dir(r'D:\PythonProject\PytestDemo\result\20201231_113716\html', r'D:/PythonProject/PytestDemo/zip/a.zip')
# unzip_file(r'D:\PythonProject\PytestDemo\zip\a.zip', r'D:\PythonProject\PytestDemo\unzip\html')







