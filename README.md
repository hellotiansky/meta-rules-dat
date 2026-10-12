# 这是我自用的Sing-box和shadowrocket代理规则集
# 使用说明
- 每天自动同步上游的规则集，更新后，Github Action自动把目录：`hellotiansky/meta-rules-dat/tree/sing/geo`下的json格式转换为一份`list`格式规则集
方便`shadowrocket`利用远程规则集`rule-set`引用。
- 自定义目录：`hellotiansky/meta-rules-dat/tree/sing/my_custom_rules`下是本人的自定义规则集，直接在线编辑`*.txt`文档，自动生成对应的srs/json/list规则集。
  默认只能生成域名后缀格式的规则集。
- `json/srs`给sing-box使用，`list`给shadowrocket使用。
