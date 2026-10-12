# 这是我自用的Sing-box和shadowrocket代理规则集
# 使用说明
- 每天自动同步上游的规则集，上游的规则集只有`json`和`srs`格式，只能给sing-box使用。
- 更新后，利用**Github Action**自动把目录：`hellotiansky/meta-rules-dat/tree/sing/geo`下的所有`json`格式转换出一份`list`格式规则集。
- `list`格式规则集供应给IOS客户端小火箭代理`shadowrocket`利用远程规则集`rule-set`引用。
- 自定义目录：`hellotiansky/meta-rules-dat/tree/sing/my_custom_rules`下是本人的自定义规则集，直接在线编辑`*.txt`文档，自动生成对应的srs/json/list规则集。
  默认只能生成域名后缀格式的规则集。
- `json/srs`给sing-box使用，`list`给shadowrocket使用。
