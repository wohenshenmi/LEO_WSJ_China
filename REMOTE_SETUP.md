# 远程机器环境配置说明

## 使用conda导出的环境配置文件

我们已经使用以下命令导出了当前conda环境的配置：

```bash
conda env export > environment.yml
```

同时创建了一个简化版本的配置文件 [environment_simple.yml](file:///C:/Users/liuma/Projects/LEO_WSJ_China/environment_simple.yml)，更适合在不同平台间使用。

## 在远程机器上创建和激活环境

### 1. 确保已安装Anaconda或Miniconda

首先确保远程机器上已安装Anaconda或Miniconda。

### 2. 传输环境配置文件

将 [environment_simple.yml](file:///C:/Users/liuma/Projects/LEO_WSJ_China/environment_simple.yml) 文件传输到远程机器上。

### 3. 创建新环境

在远程机器上运行以下命令创建与本地相同的环境：

```bash
conda env create -f environment_simple.yml
```

### 4. 激活环境

创建完成后，激活环境：

```bash
conda activate leo_wsj_china
```

### 5. 安装spaCy英文语言模型

由于spaCy语言模型在environment.yml中可能无法正确安装，需要手动安装：

```bash
python -m spacy download en_core_web_lg
```

或者，如果上面的命令不起作用，可以使用pip安装：

```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl
```

### 6. 验证安装

验证安装是否成功：

```bash
python -c "import spacy; nlp = spacy.load('en_core_web_lg'); print('spaCy和语言模型安装成功')"
```

## 更新环境配置文件

当环境中安装了新包后，可以通过以下命令更新环境配置文件：

```bash
conda env export > environment.yml
```

如果希望导出跨平台兼容的配置文件（不包含构建信息），可以使用：

```bash
conda env export --no-builds > environment_simple.yml
```

## 其他有用的conda命令

- 列出所有环境: `conda env list`
- 删除环境: `conda env remove -n leo_wsj_china`
- 更新环境中所有包: `conda update --all`
- 在环境中安装新包: `conda install package_name`