# DictManager

### 爆破字典管理工具、自动去重、分类存储、多类字典生成，改写自exhuz3u的程序[data_dict](https://github.com/exhuz3u/data_dict),添加了删除类型功能和导入导出的编码选项

### example:

#### data_dict.py -s    
显示已经存在的字典类型（默认为空，需要自己往进添加）

#### data_dict.py -i bb.txt -t dir
将 bb.txt 字典文件的数据加入类型为 dir 的字典,且与原 dir 中的数据自动去重

#### data_dict.py -o result.txt -t dir pass
将 dir 和 pass 类型的字典取出到 result.txt 文件，且自动去重
