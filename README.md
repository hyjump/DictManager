# DictManager

### 爆破字典管理工具、自动去重、分类存储、多类字典生成

DictManager 是一个基于SQL爆破字典管理工具，允许用户创建、存储、去重和导出字典数据。该工具改写自 exhuz3u 的程序 [data_dict](https://github.com/exhuz3u/data_dict)，增加了删除类型功能和导入导出的编码选项。

### 功能：

- 创建新的字典类型表
- 向指定的字典类型添加数据，并自动去重
- 导出一个或多个字典类型的数据到文件，并自动去重
- 删除一个或多个字典类型
- 预览字典类型的数据
- 显示数据库中所有存在的字典类型及其行数

### 使用示例：

#### 显示现有字典类型
```bash
DictManager.py -s
```

#### 添加字典数据,缺省自动识别编码
```bash
DictManager.exe -i input.txt -t pass1 (-e gb18030)
```

#### 导出字典数据，默认utf-8
```bash
DictManager.exe -o result.txt -t pass1 pass2 (-e utf-8)
```

#### 删除字典类型
```bash
DictManager.exe -d pass1 pass2
```

#### 预览字典数据
```bash
DictManager.exe -p test
```

### 命令行参数说明：

- `-i <file>`: 输入一个字典文件。
- `-o <file>`: 输出一个字典文件。
- `-s`: 显示存在的字典类型。
- `-t <type1> <type2> ...`: 选择一个或多个字典类型进行存储或导出。
- `-d <type1> <type2> ...`: 删除一个或多个字典类型。
- `-e <encoding>`: 指定输入/输出文件的编码，默认为 `utf-8`。
- `-p <type>`: 预览指定类型的字典数据。

