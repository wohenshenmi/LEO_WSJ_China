# 远程安装依赖说明

本文档说明如何在远程机器上安装本项目所需的依赖包。

## 方法一：使用 pip 安装（推荐）

1. 确保已安装 Python 3.9 或更高版本
2. 克隆或下载项目到本地
3. 进入项目根目录
4. 执行以下命令：

```bash
# 升级 pip
python -m pip install --upgrade pip

# 安装依赖包
pip install -r requirements.txt

# 下载 spaCy 英文语言模型
python -m spacy download en_core_web_lg
```

## 方法二：使用 conda 安装

```bash
# 创建虚拟环境
conda create -n leo_wsj_china python=3.9

# 激活环境
conda activate leo_wsj_china

# 安装主要依赖包
conda install pandas spacy gensim tqdm psutil numpy

# 安装 flashtext（需要从 conda-forge 频道安装）
conda install -c conda-forge flashtext

# 下载 spaCy 英文语言模型
python -m spacy download en_core_web_lg
```

## 验证安装

安装完成后，可以通过以下命令验证：

```bash
python -c "import spacy; nlp = spacy.load('en_core_web_lg'); print('spaCy和语言模型安装成功')"
```

## 注意事项

1. 如果使用 pip 安装遇到网络问题，可以使用国内镜像源：
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

2. spaCy 的 en_core_web_lg 模型较大（约500MB），请确保网络连接稳定。

3. 如果在安装过程中遇到权限问题，可以使用 `--user` 参数：
   ```bash
   pip install -r requirements.txt --user
   ```