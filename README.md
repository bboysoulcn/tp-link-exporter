### tplinkTL-ER5120G v3.0的exporter

### 使用

python3以上的版本

先配置config.ini里面的参数之后安装依赖包

`pip install -r requirement.txt `

之后运行

`python main.py`

注意因为不知道路由器登陆密码是怎么加密的，我也懒得做这件事所以密码要使用路由器加密过后的加密字符串,加密字符串类似于下面这样，对应
config.ini中password_hash这个字段

`2a7289f40f4330b8e4e823cf5f338e622d17dc40c450ad61fe4b4b9f
9fc5385a64b5baf666128e6adf679d608e8ef07f09054bce435300902905ad2eb5514f8b7c3a355
6a875c923112bee66e2116c8e56918d534e25598ea29cb8dcec1c777ed6a29ac7ef93bbe9a4c9b38fdd18
2f786c73f716b0f9728e014e7c925b35573c`

sleep_time表示多久向路由器获取一次数据，因为每次获取数据都要执行登陆操作，所以建议时间为30s

bug反馈: bboysoulcn@gmail.com
tplink软件版本：1.0.0 Build 20180911 Rel.44265