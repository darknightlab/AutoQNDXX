# README

AUTO QNDXX

copied from a dalao

[main.py](/main.py)的来源未知，作者本人可联系我删除仓库。

## 批评形式主义

最近发现有同学是这样青年大学习的：

<details>

1. 点击fork本仓库
2. 点击进入Settings->Secrets->Actions

    ![secrets.png](/docs/imgs/secrets.png)

3. 点击 New repository secret 添加USERNAME，PASSWORD和ORG_ID。其中ORG_ID是用微信打开[这个页面](https://m.bjyouth.net/qndxx/index.html#/pages/home/my)并登录，页面上的神秘代码

4. 点击 Actions->定时学习->Run workflow 并测试是否成功

    ![actions.png](/docs/imgs/actions.png)

5. 每个星期二晚8点将会自动完成。[autostudy.yml](/.github/workflows/autostudy.yml)中的`- cron: "0 12 * * 2"`代表0分12时UTC每星期二执行。

</details>

这样**非常不好**，违背了学习的初衷，属于**形式主义**。
