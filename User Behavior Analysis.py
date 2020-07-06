#!/usr/bin/env python
# coding: utf-8

# #  单车案例

# 这是一份用户消费行为的分析报告，数据：某单车网站用户的消费记录

# 目录：
# 
# * 项目背景
# * 分析目标
# * 分析过程
# * 小结

# ## 一、项目背景

# CDNOW是美国的一家网上唱片公司，成立于1994年，后来被贝塔斯曼音乐集团收购。

# ## 二、分析目标

# 本次分析报告的数据来源于这家CD网站上的用户消费记录，旨在分析用户消费行为，建立RFM模型，分析复购率、回购率等关键指标。

# ## 三、分析过程

# * 准备工作（数据集观察与数据清洗）
# * 用户消费趋势分析（按月）——每月消费总金额、消费次数、产品购买量、消费人数、用户平均消费金额、用户平均消费次数
# * 用户个体消费分析——用户消费金额，产品购买量的描述性统计、用户消费金额和产品购买量分布、用户累计消费金额占比
# * 用户消费行为分析——用户第一次消费（首购）时间分布、用户最后一次消费时间分布、新老用户占比、用户分层RFM模型、各类用户（新用户、活跃用户、流失用户、回流用户）数量和占比、用户购买周期、用户生命周期
# * 用户复购率和回购率分析——复购率、回购率

# ### 1、准备工作（数据集观察与数据清洗）
# 
# （1）导入常用包

# In[1]:


import pandas as pd
import numpy as np
import os 
#结果保存路径
output_path='F:/some_now/pro_output'

if not os.path.exists(output_path):
    os.makedirs(output_path)


# （2）导入数据集

# 数据集为txt文件格式，没有列名，并且字段之间使用多个空格进行分隔。
# 
# 这里读取文件时使用sep='\s+'，如果在分隔符里存在多个字符串，可以用s+，+类似于正则匹配，无论分隔符有多少个空格都可以自动处理。

# In[104]:


datafile_path='F:/some_now/datafrog/bicyle_master.csv'

columns=['user_id','order_dt','order_products','order_amount']
df=pd.read_table('F:/some_now/datafrog/bicycle_master.txt',names=columns,sep='\s+')


# * user_id：用户ID
# * order_dt:购买日期
# * order_products：购买产品数
# * order_amount：购买金额

# In[4]:


df.info()


# In[5]:


df.head(2).append(df.tail())


# In[6]:


df.describe()


# 可以发现：
# * 订单的均值为2.4，这表明该批数据的订单消费量少，但是受极值（比如最大值99，最小值1）的影响。
# * 用户的消费金额中位数为25元，也存在极值的干扰。

# 对int类型的字段order_dt转换为日期格式

# In[105]:


df['order_dt']


# In[106]:


#转换格式后
df['order_dt']=pd.to_datetime(df.order_dt,format='%Y%m%d')
df['order_dt']


# In[109]:


df['month']=df['order_dt'].astype('datetime64[M]')
df['month']


# In[110]:


df.head(3)


# ### 2、进行用户消费趋势的分析（按月）
# * 每月的消费总额
# * 每月的消费次数
# * 每月的产品购买量
# * 每月的消费人数

# In[120]:


df.groupby('month')


# In[121]:


#月消费金额
df.groupby('month')['order_amount'].sum()


# In[119]:


grouped_month=df.groupby('month')

#按month进行分组后，对不同的列采用不同的聚合方法
grouped_month_info=grouped_month.agg({'order_amount':'sum','user_id':'count','order_products':'sum'})

grouped_month_info.head(5)


# In[124]:


grouped_month_info.rename(columns = {'order_amount':'消费金额', 'user_id': '消费次数', 
                                     'order_products': '产品购买量'}, inplace=True)
grouped_month_info


# In[126]:


df.head(5)


# In[135]:


grouped_month_info['消费人次']=grouped_month['user_id'].unique().apply(lambda x:len(x))
# grouped_month['user_id'].unique().apply(len)

# grouped_month['user_id'].unique().map(len)
grouped_month_info


# In[143]:


"""
为了便于画图，需要重置索引，同时也需要把month转化为str类型，
否则画图时datetime类型的month会在powerbi中会转化为时间戳（在Powerbi中图的布局和格式都会好看一些）
"""
grouped_month_info['month'] = grouped_month_info['month'].astype(str)
grouped_month_info


# In[38]:


grouped_month_info.to_excel(os.path.join(output_path,'月销售额、销售次数、产品购买量、消费人数.xlsx'))


# ![image.png](attachment:image.png)

# 由上图可知，消费金额在前三个月达到最高峰，后续消费较为稳定，有轻微下降趋势。

# ![image.png](attachment:image.png)

# 由上图可知，产品购买量在前三个月达到最高峰，后续较为稳定，有轻微下降趋势

# ![image.png](attachment:image.png)

# 由上图可知，
# * 每月消费人次低于每月消费次数，但差异不大。
# * 前三个月消费次数在10000笔左右，后续月份的平均消费次数为2500。
# * 前三个月每月的消费人次在8000-10000之间，后续月份的平均消费人次不达2000。

# In[39]:


#上述的汇总分析，也可以用数据透视表的方法实现
df.pivot_table(index='month'
              ,values=['order_products','order_amount','user_id']
              ,aggfunc={'order_products':'sum'
                       ,'order_amount':'sum'
                       ,'user_id':'count'}).head(5)


# * 每月用户平均消费金额

# In[54]:


amount=grouped_month.order_amount.sum()
num=df.groupby('month').user_id.apply(lambda x:len(x.drop_duplicates()))
avg_amount=amount/num
avg_amount.plot()


# 由上图可知，每月用户的平均消费金额都在37.5以上，1997年1月份最低，1998年11月最高，最高值为57月左右

# * 每月用户平均消费次数

# In[55]:


times=grouped_month.user_id.count()
num=df.groupby('month').user_id.apply(lambda x:len(x.drop_duplicates()))
avg_times=times/num
avg_times.plot()


# 由上图可知，每月用户平均消费次数都在1次以上，1997年1月份最低，1998年10月最高，最高值为1.4次左右

# ### 2、用户个体消费分析
# * 用户消费金额、消费次数的秒速统计
# * 用户消费金额和消费次数的散点图
# * 用户消费金额的分布图
# * 用户消费次数的分布图
# * 用户累计消费金额占比（百分之多少的用户占了百分之多少的消费额）

# In[148]:


grouped_user=df.groupby('user_id')
grouped_user_info=grouped_user.sum()
grouped_user_info


# In[149]:


grouped_user.sum().describe()


# * 由上表可知，用户平均购买的均值为7，但是中位数（50%）只有3，说明小部分用户购买了大量的产品（二八法则）
# * 用户平均消费106元，但中位数（50%）只有43，判断同上，但也可以发现是存在极值干扰的。

# In[153]:


grouped_user_info.rename(columns={'order_products':'消费产品','order_amount':'消费金额'},inplace=True)

grouped_user_info.to_excel(os.path.join(output_path,'用户个体消费行为分析.xlsx'),index=False)


# ![image.png](attachment:image.png)

# In[233]:


grouped_user_info


# In[228]:


grouped_user_info_order_amount=grouped_user_info['消费金额']
grouped_user_info_order_amount

grouped_user_info['消费金额'].max()

grouped_user_info['消费金额'].min()

grouped_user_info_order_amount_lst=[i for i in range(0,int(grouped_user_info_order_amount.max())+50,50)]

grouped_user_info_order_amount_lst

type(grouped_user_sum_order_amount_lst)

"""
pd.cut( series, bins, right=True, labels=None, retbins=False, precision=3, include_lowest=False, duplicates='raise', )
right=True表示分组右边闭合，right=False表示分组左边闭合，
labels表示分组的自定义标签。

labels : 数组或布尔值，可选.指定分箱的标签

如果是数组，长度要与分箱个数一致，比如“ bins”=[1、2、3、4]表示（1,2]，（2,3],（3,4]一共3个区间，则labels的长度也就是标签的个数也要是3
如果为False，则仅返回分箱的整数指示符，即x中的数据在第几个箱子里

"""
#label要比bins少一位数
grouped_user_info_order_amount=pd.cut(grouped_user_info_order_amount,bins=grouped_user_info_order_amount_lst,
                                      labels=grouped_user_info_order_amount_lst[1:])

grouped_user_info_order_amount.to_excel(os.path.join(output_path,'消费金额分布直方图.xlsx'))


# ![image.png](attachment:image.png)

# 从直方图可知，用户消费金额，呈现集中趋势，小部分异常值干扰判断，可以使用过滤操作排除异常。

# 使用切比雪夫定理过滤掉异常值，切比雪夫定理说明，95%的数据都分布在5个标准差之内，剩下5%的极值就不要了。

# In[232]:


grouped_user_info['消费金额'].mean()
grouped_user_info['消费金额'].std()


# order_amount (mean = 106 ,std = 241)  mean+5std = 1311

# ![image.png](attachment:image.png)

# In[234]:


grouped_user_info_order_products=grouped_user_info['消费产品']
grouped_user_info_order_products


# In[236]:


grouped_user_info['消费产品'].max()


# In[235]:


grouped_user_info['消费产品'].min()


# In[237]:


grouped_user_info_order_products_lst=[i for i in range(0,int(grouped_user_info_order_products.max())+50,50)]

grouped_user_info_order_products_lst


# In[ ]:


type(grouped_user_sum_order_products_lst)

"""
pd.cut( series, bins, right=True, labels=None, retbins=False, precision=3, include_lowest=False, duplicates='raise', )
right=True表示分组右边闭合，right=False表示分组左边闭合，
labels表示分组的自定义标签。

labels : 数组或布尔值，可选.指定分箱的标签

如果是数组，长度要与分箱个数一致，比如“ bins”=[1、2、3、4]表示（1,2]，（2,3],（3,4]一共3个区间，则labels的长度也就是标签的个数也要是3
如果为False，则仅返回分箱的整数指示符，即x中的数据在第几个箱子里

"""


# In[239]:


#label要比bins少一位数
grouped_user_info_order_products=pd.cut(grouped_user_info_order_products,bins=grouped_user_info_order_products_lst,
                                      labels=grouped_user_info_order_products_lst[1:])
grouped_user_info_order_products


# In[240]:


grouped_user_info_order_products.to_excel(os.path.join(output_path,'消费次数分布直方图.xlsx'))


# ![image.png](attachment:image.png)

# In[241]:


grouped_user_info['消费产品'].mean()+5*grouped_user_info['消费产品'].std()


# ![image.png](attachment:image.png)

# #### 计算累计消费金额占比 

# In[243]:


grouped_user_info.head(5)


# In[246]:


grouped_user_info.sort_values('消费金额')


# In[252]:


#cumsum求累加值

grouped_user_info=grouped_user.sum()
user_cumcum=grouped_user_info.sort_values('消费金额').apply(lambda x:x.cumsum()/x.sum())

user_cumcum.reset_index(inplace=True)

user_cumcum.to_excel(os.path.join(output_path,'累计销售情况占比.xlsx'))


# In[253]:


user_cumcum


# ![image.png](attachment:image.png)

# 按照用户消费金额进行升序排序，可以发现50%的用户仅仅贡献了10%左右的消费额度，而排名前20%的用户贡献了60%的消费额度，符合“二八法则”，这表明只要抓住前20%（（用户总数（23569）*80%=18855））的用户，便可达成目标销售额度的大部分，其余80%的客户可以做策略调整。

# ### 3、用户消费行为 
# - 用户第一次消费（首购）
# - 用户最后一次消费
# - 新老客户消费比
#  - 多少用户仅消费一次
#  - 每月新客占比
# - 用户分层
#  - RFM模型
#  - 新、老、活跃、回流、流失
# - 用户购买周期（按订单）
#  - 用户消费周期描述
#  - 用户消费周期分布
# - 用户生命周期（按第一次和最后一次消费）
#  -用户生命周期描述
#  - 用户生命周期分布

# In[255]:


grouped_user=df.groupby('user_id')
grouped_user


# In[259]:


grouped_user.min()


# In[260]:


grouped_user_min=grouped_user.min()['order_dt'].value_counts().reset_index().rename(columns={'index':'first_date'})


# In[261]:


grouped_user_min


# In[262]:


grouped_user_min['first_date']


# In[263]:


#如果把datetime64类型的first_date传入Powerbi会变成时间戳，为正常显示，需要将其转换为str类型
grouped_user_min['first_date']=grouped_user_min['first_date'].astype(str)
grouped_user_min.to_excel(os.path.join(output_path,'用户首购.xlsx'))


# In[264]:


grouped_user_min


# ![image.png](attachment:image.png)

# In[271]:


#用户最后一次额购买分布统计同理
grouped_user_max=grouped_user.max().order_dt.value_counts().reset_index().rename(columns={'index':'last_date'})
grouped_user_max


# In[272]:


grouped_user_max['last_date']=grouped_user_max['last_date'].astype(str)
grouped_user_max.to_excel(os.path.join(output_path,'用户最后一次购买分布.xlsx'))


# ![image.png](attachment:image.png)

# - 可以发现，用户最后一次购买出现断崖式下跌，结合用户首次购买分布图可以发现：用户流失比例基本一致，一开始用户迅猛增长数量比较多，但流失的也比较多，后面没有基本没有新增用户。用户最后一次购买的分布比首次购买的分布广。
# - 大部分用户的最后一次购买，主要集中在前三个月，说明很多用户购买了一次后就不再进行购买。
# - 随着时间的递增，最后一次购买的数量也在递增，消费呈现流失上升的状况，这种情况属于：随着时间的增长，可能运营没有跟上，或者其它原因导致用户忠诚度下降进而流失。

# In[273]:



#得到第一次和最后一次消费情况，如果min、max日期相同，说明只消费了一次
user_life=grouped_user['order_dt'].agg({'min','max'})
user_life.head()


# In[274]:


#统计只消费了一次的用户
(user_life['min']==user_life['max']).value_counts()


# 可以发现，只消费了一次的用户占总用户的近1/2

# #### 每月新用户占比

# In[277]:


# 按照month、userid分组，第一次和最后一次消费日期
user_life_month=df.groupby(['month','user_id']).order_dt.agg(['min','max']).reset_index()


# In[346]:


# 新增is_new字段，用于标记新用户
user_life_month['is_new']=(user_life_month['min']==user_life_month['max'])
user_life_month['is_new']


# In[283]:


# 再次按month分组，计算新用户占比
"""
value_counts()是计算分组数目
counts()是计算总数目
"""
user_life_month_pct=user_life_month.groupby('month')['is_new'].apply(lambda x:x.value_counts()/x.count()).reset_index()
# level_1为True的作图
user_life_month_pct[user_life_month_pct.level_1].plot(x='month',y='is_new')


# In[282]:


user_life_month_pct


# In[280]:


user_life_month


# #### 用户分层

# In[284]:


"""
RFM模型是衡量客户价值和客户创利能力的重要工具和手段。在众多的客户关系管理(CRM)的分析模式中，RFM模型是被广泛提到的。
该机械模型通过一个客户的近期购买行为、购买的总体频率以及花了多少钱3项指标来描述该客户的价值状况。
最近一次消费 (Recency)
消费频率 (Frequency)
消费金额 (Monetary)
"""
#画RFM，先对原始数据进行透视
rfm=df.pivot_table(index='user_id'
                  ,values=['order_products','order_amount','order_dt']
                  ,aggfunc={'order_products':'sum','order_amount':'sum','order_dt':'max'})
rfm.head(5)


# In[288]:


"""
最近一次消费 (Recency):
一般是计算距离今天最近的一次消费，这里因为时间太久远，就用的max值，数值越大就越久远，
时间格式相减，得到的是xxxdays，除以单位‘D’，就不会有单位了，只保留数值
消费频率 (Frequency)
消费金额 (Monetary)
"""
rfm['R']=(rfm.order_dt-rfm.order_dt.max())/np.timedelta64(1,'D')
#注意：这里除以单位‘D’，也是把datetime类型的数据转化为了float类型，因为.astype(float)和.values().astype(str)均不可,
#时间序列类型，无法转换成浮点型


# In[290]:


#重命名
rfm.rename(columns={'order_products':'F','order_amount':'M'},inplace=True)
rfm.head()


# In[291]:


def rfm_func(x):
    level=x.apply(lambda x:'1' if x>=0 else '0')
    #level的类型是series，index是R\F\M
    label=level['R']+level['F']+level['M']
    d={
        #R为1表示离均值较远，即时间久、F为1表示消费金额比较多，M为1表示消费频次比较多，所以是重要价值客户
       '111':'重要价值客户',
        '011':'重要保持客户',
        '101':'重要发展客户',
        '001':'重要挽留客户',
        '110':'一般价值客户',
        '010':'一般保持客户',
        '100':'一般发展客户',
        '000':'一般挽留客户',
    }
    result=d[label]
    return result

# 注意这里是要一行行的传递进来，所以 axis=1，传递一行得到一个 111，然后匹配返回一个值
rfm['label']=rfm[['R','F','M']].apply(lambda x:x-x.mean()).apply(rfm_func,axis=1)#高于均值赋值为1，低于均值赋值为0


# In[297]:


rfm1=rfm.reset_index()


# In[298]:


rfm1.to_excel(os.path.join(output_path,'RFM模型.xlsx'),index=False)


# ![image.png](attachment:image.png)

# In[301]:


rfm.groupby('label').sum().sort_values('F',)


# 由RFM分层可知，大部分用户是重要价值客户，复购频次高，消费金额大，但是这是由于极值的影响，所以RFM的划分标准应该以业务为准，也可以通过切比雪夫去除极值后求均值，并且RFM的各个划分标准可以都不一样。
# * 尽量用小部分的用户覆盖大部分的额度。
# * 不要为了数据好看而划分等级。
# 

# 用户生命周期：新、老、活跃、回流、流失（一段时间不消费，或者不活跃）

# In[302]:


#数据透视，求每月的消费次数，缺失值用0填充
pivoted_counts=df.pivot_table(index='user_id'
							,columns='month'
							,values='order_dt'
							,aggfunc='count').fillna(0)
pivoted_counts.head()


# In[303]:


#由于判断用户的状态不需要观察次数，所以我们把购买次数大于0的赋值为1，没有消费的赋值为0即可
df_purchase=pivoted_counts.applymap(lambda x:1 if x>0 else 0)
df_purchase.tail()


# In[308]:


len(df_purchase.columns)


# In[305]:


# 这里由于进行数据透视，填充了一些 null 值为0，而实际可能用户在当月根本就没有注册，
#这样会误导第一次消费数据的统计，所以写一个函数来处理

def active_status(data):
    status=[]
    # 数据一共有18个月份，每次输入一行数据，也就是一个user_id的信息，进行逐月判断
    for i in range(18):
        # 若本月没有消费
        if data[i]==0:
            # 判断之前有没有数据，之前有数据
            if len(status)>0:
                # 判断上个月是否为未注册（如果上个月未注册，本月没有消费，仍为未注册）
                if status[i-1]=='unreg':
                    status.append('unreg')
                # 上月有消费，本月没有消费，则为不活跃
                else:
                    status.append('unactive')
            # 之前一个数据都没有，就认为是未注册
            else:
                status.append('unreg')
 
        # 若本月消费
        else:
            # 之前无记录，本月是第一次消费，则为新用户
            if len(status)==0:
                status.append('new')
            # 之前有记录
            else:
                # 上个月是不活跃，这个月消费了，则为回流用户
                if status[i-1]=='unactive':
                    status.append('return')
                # 上个月未注册，这个月消费了，则为新用户
                elif status[i-1]=='unreg':
                    status.append('new')
                # 上个月消费了，本月仍消费，则为活跃用户
                else:
                    status.append('active')
    return status


# 关于active_status的说明：
# 
# 若本月没有消费，这里只是和上个月判断是否注册，有一定的缺陷，应该判断是否存在就可以了
# 
# * 若之前有数据，是未注册，则依旧为未注册
# * 若之前有数据，不是未注册，则为流失/不活跃
# * 若之前没有数据，为未注册
# 
# 若本月有消费
# * 若是第一次消费，则为新用户
# * 若之前有过消费，上个月为不活跃，则为回流
# * 若之前有过消费，上个月为未注册，则为新用户
# * 若之前有过消费，其他情况为活跃
# return:回流 new:新客 unreg:未注册 active:活跃

# In[309]:


purchase_stats=df_purchase.apply(lambda x: pd.Series(active_status(x),index=df_purchase.columns),axis=1)
purchase_stats.head()


# In[310]:


# 这里把未注册的替换为空值，这样 count 计算时不会计算到
# 得到每个月的用户分布
purchase_stats_ct=purchase_stats.replace('unreg',np.NaN).apply(lambda x:pd.value_counts(x))
purchase_stats_ct


# In[311]:


returnratee=purchase_stats_ct.apply(lambda x:x/x.sum(),axis=0)


# In[312]:


returnratee


# In[313]:


purchase_stats_ct_info = purchase_stats_ct.fillna(0).T


# In[314]:


purchase_stats_ct_info.head()


# In[315]:


purchase_stats_ct_info.index = purchase_stats_ct_info.index.astype(str)


# In[317]:


purchase_stats_ct_info.to_excel(os.path.join(output_path,'用户分层-新、活跃、流失、回流.xlsx'))


# ![image.png](attachment:image.png)

# * 由上图可以发现，在前三个月，新用户大量涌入，之后没有新增用户；
# * 前三各月，活跃用户较多，但随后下降
# * 回流用户，数量后期下降并稳定在1000左右
# * 流失用户（不活跃用户），数量非常多，前三个月后人数稳定在20000以上

# In[318]:


# 求出所有用户的占比
purchase_stats_ct.fillna(0).T.apply(lambda x:x/x.sum(),axis=1)


# #### 用户购买周期（按订单）

# In[319]:


# 计算相邻两个订单的时间间隔，shift 函数是对数据进行错位，所有数据会往下平移一下
order_diff=grouped_user.apply(lambda x:x.order_dt-x.order_dt.shift())
order_diff.head(10)


# In[320]:


#去掉单位
(order_diff/np.timedelta64(1,'D'))


# In[326]:


order_diff_info = (order_diff/np.timedelta64(1,'D'))
order_diff_cut_lst = [i for i in range(0,int(order_diff_info.max()),10)]
order_diff_info_hist = pd.cut(order_diff_info,bins=order_diff_cut_lst,labels=order_diff_cut_lst[1:])
#order_diff_info_hist 中的NaN值不能被Powerbi计数，所以需要进行值填充
order_diff_info_hist = order_diff_info_hist.fillna(10)


# In[328]:


order_diff_info_hist.to_excel(os.path.join(output_path,'用户购买周期时间差频率直方图.xlsx'))


# ![image.png](attachment:image.png)

# * 订单周期呈指数分布
# * 绝大部分用户的购买周期都低于100天

# ####  用户生命周期 

# In[329]:


# 用户生命周期（按第一次和最后一次消费）
(user_life['max']-user_life['min']).describe()


# In[330]:


user_life_info = ((user_life['max']-user_life['min'])/np.timedelta64(1,"D"))
user_life_lst = [i for i in range(0,((user_life['max']-user_life['min'])/np.timedelta64(1,"D")).count(),10)]
user_life_info_hist = pd.cut(user_life_info,bins=user_life_lst,labels=user_life_lst[1:])
user_life_info_hist_2 = user_life_info_hist.fillna(10)
user_life_info_hist_2.to_excel(os.path.join(output_path,'用户生命周期频率直方图.xlsx'))


# ![image.png](attachment:image.png)

# 用户的生命周期受只购买一次的用户影响比较厉害（可以排除）
# 

# In[331]:


user_life_info_hist.to_excel(os.path.join(output_path,'用户生命周期频率直方图（忽略一次购买）.xlsx'))


# ![image.png](attachment:image.png)

# ### 4、复购率和回购率分析
# - 复购率
#   - 自然月内，购买多次的用户占比(即，购买了两次及以上)
# - 回购率
#   - 曾经购买过的用户在某一时期的再次购买的占比（可能是在三个月内）

# In[332]:


# 复购率
pivoted_counts.head(10)


# In[333]:


# 区分一个，和一个以上的情况，以便于计算复购率，大于1为1，等于0 为0，等于1为0
purchase_r=pivoted_counts.applymap(lambda x: 1 if x>1 else np.NaN if x==0 else 0)
purchase_r.head()


# In[335]:


purchase_r_reshop = (purchase_r.sum()/purchase_r.count()).reset_index(name = 'reshop')
purchase_r_reshop['month'] = purchase_r_reshop['month'].astype(str)
purchase_r_reshop.to_excel(os.path.join(output_path,'复购人数与总消费人数比例.xlsx'))


# In[340]:


purchase_r_reshop


# ![image.png](attachment:image.png)

# 复购率稳定在20%左右，前一个月因为有大量新用户涌入，而这批用户只购买了一次，所以导致复购率降低

# In[336]:


# 回购率，知道是否消费就可以了
df_purchase.head()


# In[337]:


# 使用函数判断是否回购，这里定义的回购指当月消费过的用户下个月也消费了
def purchase_back(data):
    # 判断每一个月是否是回购，根据下个月是否购买来判断
    status=[]
    for i in range(17):
        # 本月消费
        if data[i]==1:
            # 下个月回购
            if data[i+1]==1:
                status.append(1)
            # 下个月没回购
            if data[i+1]==0:
                status.append(0)
        #  本月没消费，赋予空值，不参与计算
        else:
            status.append(np.NaN)
    # 第18个月补充NaN，因为没有下个月的数据了
    status.append(np.NaN)
    return status


# In[338]:


indexs=df['month'].sort_values().astype('str').unique()
purchase_b = df_purchase.apply(lambda x :pd.Series(purchase_back(x),index = indexs),axis =1)
purchase_b.head()


# In[339]:


purchase_b_backshop = purchase_b.sum()/purchase_b.count()
purchase_b_backshop.index = purchase_b_backshop.index.astype(str)
purchase_b_backshop.to_excel(os.path.join(output_path,'回购率.xlsx'))


# ![image.png](attachment:image.png)

# 回购率稳定在30%左右，前3个月因为有大量新用户涌入，而这批用户只购买了一次，所以导致回购率较低。

# ## 四、小结
1、用户消费趋势（每月）方面，前3个月有大量新用户涌入，消费金额、消费订单数、产品购买量均达到高峰，后续每月较为稳定。前3个月消费次数都在10000笔左右，后续月份的平均2500；前3个月产品购买量达到20000甚至以上，后续月份平均7000；前3个月消费人数在8000-10000之间，后续月份平均2000不到。

2、用户个体消费方面，小部分用户购买了大量的CD，拉高了平均消费金额。用户消费金额集中在0~100元，有大约17000名用户。用户购买量集中在0~5，有大约16000名用户。50%的用户仅贡献了15%的消费额度，15%的用户贡献了60%的消费额度。大致符合二八法则。

3、用户消费行为方面，首购和最后一次购买的时间，集中在前三个月，说明很多用户购买了一次后就不再进行购买。而且最后一次购买的用户数量也在随时间递增，消费呈现流失上升的状况。

4、从整体消费记录来看，有一半的用户，只消费了一次。从每月新用户占比来看，1997年1月新用户占比高达90%以上，后续有所下降，1997年4月到1998年6月维持在81%左右，1998年6月以后无新用户。

5、从RFM模型来看，在8种客户中，重要保持客户的消费频次和消费金额最高，人数排在第二位；而一般发展客户消费频次和消费金额排第二位，人数却是最多。

6、从用户分层情况来看，新用户从第4月份以后没有新增；活跃用户有所下降；回流用户数量趋于稳定，每月1000多。流失/不活跃用户，数量非常多，基本上每月都在20000以上。

7、用户购买周期方面，平均购买周期是68天，最小值0天，最大值533天。绝大部分用户的购买周期都低于100天。

8、用户生命周期方面，由于只购买一次的用户（生命周期为0天）占了接近一半，排除这部分用户的影响之后，用户平均生命周期276天，中位数302天。

9、复购率和回购率方面，复购率稳定在20%左右，回购率稳定在30%左右，前3个月因为有大量新用户涌入，而这批用户只购买了一次，所以导致复购率和回购率都比较低。
# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




