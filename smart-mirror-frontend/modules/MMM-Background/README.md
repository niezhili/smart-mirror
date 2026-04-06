# MMM-Background 日期优先级逻辑

本模块根据当前日期选择壁纸目录，优先级如下：

1. 节气（solar_term）
2. 节日（festival）
3. 常规文化图（cultures）

## 设计目标

- 同一日期命中节气与节日时，优先展示节气壁纸。
- 命中目录后，客户端继续在该目录图片集合中循环切换。
- 未命中特殊日期时，稳定回退到 cultures 目录。

## 伪代码

```text
输入: dateString (MM-DD)

if dateString 命中 solar_term 映射且目录存在:
  返回 images/solar_term/<termFolder>
else if dateString 命中 festival 映射且目录存在:
  返回 images/festival/<festivalFolder>
else:
  返回 images/cultures
```

## 备注

- 服务端目录解析只负责返回图片集合，不负责客户端切换动画。
- 客户端收到集合后使用现有轮播/手势逻辑完成循环展示。
