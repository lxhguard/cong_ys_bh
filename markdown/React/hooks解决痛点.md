# React Hooks解决了什么问题

面试官经常会提问， `React Hook` 是什么版本出现的， 他解决了`Class`的什么问题？


## 1 分钟面试话术

> Hooks 是 React 16.8 正式引入的，主要解决 class 的四个痛点。

> **第一个是 this 指向问题**——class 方法在回调里 this 会丢，要到处 bind 或写箭头函数，而函数组件没有 this，天然避开了这个坑。

> 第二个是逻辑被打散在三个生命周期里，useEffect 把它聚到了一起。

> 第三个是状态逻辑复用，class 只能靠 HOC 和 render props，容易嵌套地狱，自定义 Hook 用函数组合就干净了。

> 第四个是 class 的心智负担和工程劣势——构造函数、生命周期记忆成本高，方法名也没法被压缩工具优化。所以 16.8 之后新代码默认函数组件。


## 版本

**React 16.8（2019 年 2 月）正式发布**，Hooks 转正（16.7 只有 alpha，别答错）。

## Hooks 解决的 class 痛点

| # | 痛点 | class 时代的问题 | Hooks 的解法 |
|---|---|---|---|
| 1 | **this 指向问题** | 回调里 `this` 丢失，要到处 `bind` 或写箭头函数，代码啰嗦且易错 | 函数组件**没有 this**，状态靠闭包捕获，天然正确 |
| 2 | 复杂组件逻辑被打散 | 同一份逻辑拆进 `componentDidMount` / `Update` / `WillUnmount` 三处，读代码来回跳 | **useEffect 内聚**：挂载/更新/卸载写在一起 |
| 3 | 状态逻辑复用难 | 只能靠 **HOC / render props / mixins**，产生嵌套地狱、命名冲突、来源难追踪 | **自定义 Hook**：逻辑抽成函数，可组合、无嵌套 |
| 4 | 心智负担 + 工程劣势 | constructor/super/生命周期记忆成本高；方法名**难以 minify**、bundle 偏大；TS 体验差 | 纯函数更轻、更小、类型友好 |



## 补充点（说了即区分度）

- 16.8 才转正，16.7 是 alpha 试验版
- Hooks **不废弃** class，两者共存
- React 18 并发特性主要服务 hooks 生态，**class 基本冻结**不再获得新能力
- 自定义 Hook 是「状态逻辑复用」的单元，不是组件

## 版本

**React 16.8（2019 年 2 月）正式发布**，Hooks 转正（16.7 只有 alpha 试验版，别答错）。

## Hooks 解决的 class 痛点（按你要求的顺序：this 指向放第一条）

**① this 指向问题（先说它）**

> 
> class 方法里的 `this` 在回调/事件处理器中会丢失，必须手动 `bind` 或写成箭头函数；方法多、层级深时到处都是 `this.fn = this.fn.bind(this)`，啰嗦且易错。Hooks 函数组件**根本没有 this**，状态和参数靠闭包捕获，天然正确。

**② 状态逻辑复用难**

> 
> class 想复用状态逻辑只能靠 **HOC / render props / mixins**，结果组件嵌套地狱（wrapper hell）、props 来源不明、命名冲突。自定义 Hook 把逻辑抽成纯函数，可组合、可测试、无嵌套。

**③ 复杂组件逻辑被打散**

> 
> 同一份逻辑被拆进 `componentDidMount` / `componentDidUpdate` / `componentWillUnmount` 三处，读代码要来回跳。`useEffect` 把挂载/更新/卸载的副作用写在一起，内聚。

**④ class 心智负担 + 工程劣势**

> 
> constructor / super / 生命周期记忆成本高；class 方法名**难以 minify**、tree-shaking 不彻底、bundle 偏大；TS 类型体验差。函数组件更轻、更小、类型友好。

## 1 分钟面试话术（this 开头版）

> 
> Hooks 是 React 16.8 正式引入的，它主要解决了 class 的四个痛点。**第一个是 this 指向问题**——class 方法在回调里 this 会丢，要到处 bind 或写箭头函数，而函数组件没有 this，天然避开了这个坑。第二个是状态逻辑复用，class 只能靠 HOC 和 render props，容易嵌套地狱，自定义 Hook 用函数组合就干净了。第三个是逻辑被打散在三个生命周期里，useEffect 把它聚到了一起。第四个是 class 的心智负担和工程劣势——构造函数、生命周期记忆成本高，方法名也没法被压缩工具优化。所以 16.8 之后新代码默认函数组件。

重排后的对照图（复习用）：

```
<html style="margin:0;padding:0;">
<title>React Hooks 解决的 class 痛点（this优先版）</title>
<div style="width:100%;box-sizing:border-box;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f4f6f9;padding:22px;border-radius:14px;">
  <div style="font-size:18px;font-weight:700;color:#1f2933;margin-bottom:4px;">React Hooks · 解决 class 的四大痛点</div>
  <div style="font-size:13px;color:#6b7280;margin-bottom:16px;">React 16.8（2019.02）正式发布 · 回答顺序：this → 复用 → 打散 → 心智负担</div>
  <div style="display:flex;flex-wrap:wrap;gap:12px;">
    <div style="flex:1 1 280px;min-width:260px;background:#fff;border-radius:10px;border-top:4px solid #e5484d;padding:12px 14px;">
      <div style="font-size:14px;font-weight:700;color:#e5484d;">① this 指向问题 · 先说</div>
      <div style="font-size:13px;color:#6b7280;text-decoration:line-through;margin-top:6px;">回调 this 丢失 → 到处 bind / 箭头函数</div>
      <div style="font-size:13px;color:#15803d;font-weight:600;margin-top:4px;">→ 函数组件无 this，闭包捕获天然正确</div>
    </div>
    <div style="flex:1 1 280px;min-width:260px;background:#fff;border-radius:10px;border-top:4px solid #f76b15;padding:12px 14px;">
      <div style="font-size:14px;font-weight:700;color:#f76b15;">② 状态逻辑复用难</div>
      <div style="font-size:13px;color:#6b7280;text-decoration:line-through;margin-top:6px;">HOC / render props → 嵌套地狱、命名冲突</div>
      <div style="font-size:13px;color:#15803d;font-weight:600;margin-top:4px;">→ 自定义 Hook：函数组合、零嵌套</div>
    </div>
    <div style="flex:1 1 280px;min-width:260px;background:#fff;border-radius:10px;border-top:4px solid #8b5cf6;padding:12px 14px;">
      <div style="font-size:14px;font-weight:700;color:#8b5cf6;">③ 复杂组件逻辑被打散</div>
      <div style="font-size:13px;color:#6b7280;text-decoration:line-through;margin-top:6px;">同一逻辑拆进 Mount / Update / Unmount 三处</div>
      <div style="font-size:13px;color:#15803d;font-weight:600;margin-top:4px;">→ useEffect 内聚，副作用写一处</div>
    </div>
    <div style="flex:1 1 280px;min-width:260px;background:#fff;border-radius:10px;border-top:4px solid #0d9488;padding:12px 14px;">
      <div style="font-size:14px;font-weight:700;color:#0d9488;">④ 心智负担 + 工程劣势</div>
      <div style="font-size:13px;color:#6b7280;text-decoration:line-through;margin-top:6px;">constructor/super/生命周期记忆成本；方法名难 minify</div>
      <div style="font-size:13px;color:#15803d;font-weight:600;margin-top:4px;">→ 纯函数更轻、bundle 更小、TS 友好</div>
    </div>
  </div>
  <div style="margin-top:14px;background:#1f2933;border-radius:10px;padding:12px 16px;color:#fff;">
    <div style="font-size:13px;font-weight:700;margin-bottom:6px;">补充点（说了即区分度）</div>
    <div style="font-size:13px;color:#e5e7eb;line-height:1.8;">16.8 才转正（16.7 是 alpha）｜ Hooks 不废弃 class，两者共存｜ React 18 并发特性主要服务 hooks 生态，class 基本冻结｜ 自定义 Hook 是「状态逻辑复用」的单元</div>
  </div>
</div>
```

```
