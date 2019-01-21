# 嵌入式系统设计期末项目

## 项目基本结构( 还未完全确定 )

进展：https://docs.qq.com/doc/DWWpPYVJZQWJOZkFi


## 基本构造



## 连线方式

### 51 单片机连接 esp8266 模块

这两个模块之间需要通过 urat 来传输信息

- 开门的指令

- 当前门的状态

- 在门输入的密码

具体连线如下

- esp8266 G(gound) <=> 51 GND 

- esp8266 Tx(transfer) <=> 51 P16(相当于 UART RX)

- esp8266 Rx(receive) <=> 51 P17(相当于 UART TX)


## API design

// todo 
- GET /poll : 轮询当前门锁的状态
    
    - request: 没有参数

    - reponse: 门的状态【开启或者关闭】

- POST: /open-door : 发送开门请求到服务器
    
    - request: 
        - parameter:
            - string: password
    - response:


- GET: /record : 获取本地数据库的状态，管理者页面
    
    - request

    - response : 渲染

        - log