# nonebot_plugin_group_enter_validation

## 使用：  
超管获取加群密钥，分发给用户，用户输入密钥加群，bot判断密钥进行审核，__每个密钥仅可使用一次__ ,该密钥的使用者QQ将被记录在 `data/group_entry_key.json` 的user中  

## env配置：  
 在.env文件中添加  
> `GROUP_LOGIN_KEY_LENGTH=10  #自定义每个密钥的字符个数`  

##  __超管__ 获取加群密钥指令：
以下命令需要加 __命令前缀__（默认为 / ），可自行设置为空    
> `/创建加群密钥 -g群号 -n生成密钥数量`  

例如： `/创建加群密钥 -g123456 -n10`  
一次获取密钥个数最少1个，最多30个  
  
## 注意：
1.确保bot是该群的群主或管理员  
2.加群验证方式必须设置为 __需要回答问题并由管理员审核__  
