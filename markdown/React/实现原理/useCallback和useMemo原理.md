# useCallback和useMemo原理

面试经常会问：useCallback 和 useMemo 的缺点，实现原理是什么，如何做到节省性能开销的？



# 面试话术（1 分钟）

> 
> useMemo 和 useCallback 的原理一样：在 hooks 链表的节点里存 `[值, 依赖数组]`，更新时用 Object.is 做浅比较，依赖没变就返回缓存的引用，变了才重新执行 create。useCallback 本质是 useMemo 的变体，缓存对象是函数。它们省性能的路径有两条：useMemo 跳过昂贵计算，useCallback 稳住引用配合 React.memo 让子组件跳过重渲染、也让 effect 依赖稳定。但我认为它们**不是免费的**：每次渲染都要比较依赖，缓存也占内存；而且浅比较对对象/数组依赖无效，写错依赖还会造成闭包陷阱。所以我的原则是**按需使用、有可测量收益才用**——React 官方也是这么建议的，React 19 甚至推出了自动 memo 的 React Compiler，说明手写属于不得已的手段。

配合这张「缓存判定流程 + 成本收益」图：

```html type="renderer"
<html style="margin:0;padding:0;">
<title>useMemo与useCallback原理与权衡</title>
<div style="width:100%;box-sizing:border-box;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f4f6f9;padding:22px;border-radius:14px;">
  <div style="font-size:18px;font-weight:700;color:#1f2933;margin-bottom:4px;">useMemo / useCallback · 原理与权衡</div>
  <div style="font-size:13px;color:#6b7280;margin-bottom:16px;">节点存 [值, deps] · Object.is 浅比较 · useCallback = useMemo 变体</div>

  <div style="background:#fff;border-radius:10px;padding:14px;margin-bottom:10px;">
    <div style="font-size:13px;font-weight:700;color:#1d4ed8;margin-bottom:8px;">更新阶段判定流程</div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <div style="background:#dbeafe;color:#1d4ed8;border-radius:6px;padding:6px 10px;font-size:13px;">取节点 [旧值, 旧deps]</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dbeafe;color:#1d4ed8;border-radius:6px;padding:6px 10px;font-size:13px;">Object.is 逐个比 deps</div>
      <div style="color:#9ca3af;">→</div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">没变 → 返回缓存（create 不执行）✅</div>
        <div style="background:#fee2e2;color:#b91c1c;border-radius:6px;padding:6px 10px;font-size:13px;">变了 → 重算 create，更新 [值, deps]</div>
      </div>
    </div>
  </div>

  <div style="background:#fff;border-radius:10px;padding:14px;margin-bottom:10px;">
    <div style="font-size:13px;font-weight:700;color:#15803d;margin-bottom:8px;">收益端 · 省在哪</div>
    <div style="font-size:13px;color:#374151;line-height:1.9;">useMemo → 跳过昂贵计算<br>useCallback → 引用稳定 → React.memo 子组件跳过重渲染 + effect 依赖不重跑<br>注：不阻止父组件自身渲染，只影响下游 memo / effect</div>
  </div>

  <div style="background:#fff;border-radius:10px;padding:14px;border:1px solid #fecaca;">
    <div style="font-size:13px;font-weight:700;color:#b91c1c;margin-bottom:8px;">成本端 · 坑在哪</div>
    <div style="font-size:13px;color:#374151;line-height:1.9;">每次渲染 O(n) 比较 deps + 缓存占内存｜对象/数组依赖浅比较必失效｜漏 deps → 闭包陷阱拿旧值｜不配 memo 就是白包一层｜React Compiler 已能自动 memo，手写是不得已</div>
  </div>

  <div style="margin-top:12px;background:#fffbeb;border-left:4px solid #d97706;border-radius:8px;padding:10px 14px;font-size:13px;color:#92400e;">
    判断标准：<b>不用它，性能问题能测量吗？</b>测不到 = 过早优化；有可测量收益（昂贵计算 / memo 子组件 / effect 依赖 / context value）才用。
  </div>
</div>
```



# 一、本质与实现原理

useMemo / useCallback 跟 useState 一样，都是挂在 **fiber 的 hooks 链表**上的节点，但节点里存的是 `[值, 依赖数组]`。原理就一句话：**依赖没变 → 返回缓存；依赖变了 → 重算并更新缓存**。

## 简化伪代码（概念一致）

```js
// ---- mount：创建节点，执行一次 create，存 [值, deps] ----
function mountMemo(create, deps) {
  const hook = mountWorkInProgressHook();
  hook.memoizedState = [create(), deps];   // 关键：值和依赖数组一起存
  return hook.memoizedState[0];
}

// ---- update：取节点，比较 deps，命中缓存或重算 ----
function updateMemo(create, deps) {
  const hook = updateWorkInProgressHook();
  const prev = hook.memoizedState;              // [旧值, 旧依赖]
  if (prev !== null && areHookInputsEqual(deps, prev[1])) {
    return prev[0];                             // ✅ 依赖没变 → 返回缓存，create 不执行
  }
  const nextValue = create();                   // 变了 → 重新执行
  hook.memoizedState = [nextValue, deps];
  return nextValue;
}

// ---- useCallback：useMemo 的变体，缓存的"值"就是函数 ----
function updateCallback(callback, deps) {
  const hook = updateWorkInProgressHook();
  if (areHookInputsEqual(deps, hook.memoizedState[1])) {
    return hook.memoizedState[0];               // 依赖没变 → 返回同一个函数引用
  }
  hook.memoizedState = [callback, deps];
  return callback;
}
```

两个关键实现细节：

- **`areHookInputsEqual` 是浅比较，用 `Object.is`** 逐个比依赖，不做深比较
- useCallback 就是 useMemo 的语法糖变体：`useCallback(fn, deps)` ≈ `useMemo(() => fn, deps)`

# 二、如何节省性能开销（收益端）

| 手段 | 机制 |
| --- | --- |
| **省重计算**（useMemo） | create 函数只在依赖变化时执行，跳过昂贵计算（大数组过滤/排序、对象创建） |
| **省重渲染**（useCallback） | 函数引用稳定 → 配合 `React.memo` 子组件做 **props 浅比较**，引用不变 → 跳过子组件整个渲染 |
| **省 effect 重跑** | 作为 `useEffect` 依赖的回调/值稳定 → 副作用不重复执行 |
| **省 context 下游渲染** | `value` 用 useMemo 包住 → 消费组件不因引用变化而重渲染 |

**关键链路**（面试必说）：父组件每次渲染都会创建新函数引用 → 没有 useCallback 时，`React.memo` 子组件比较 props 发现 `onClick` 引用变了 → 照样重渲染，memo 白搭。useCallback 稳住了引用，memo 的比较才有意义。

> 
> 注意：useMemo/useCallback **不会阻止父组件自己渲染**，它只影响「下游 memo 组件」和「effect 依赖」。

# 三、缺点（你的区分点，一定要讲全）

| 缺点 | 说明 |
| --- | --- |
| **不是零成本** | 每次渲染都要遍历比较 deps（O(n)）+ 缓存占内存不释放；比较本身就是开销 |
| **过早优化** | React 官方明确不建议默认使用；React 19 的 **React Compiler 自动 memo**，说明手写属于"不得已而为之" |
| **闭包陷阱（stale closure）** | deps 漏写 / 空依赖读外部 props/state → 缓存永远拿到**首次渲染的旧值** |
| **浅比较的局限** | 依赖是对象/数组时，每次渲染都是新引用 → `Object.is` 必不等 → **缓存必然失效**（最常见误用） |
| **依赖数组心智负担** | 写错 deps 的 bug 极难排查，`exhaustive-deps` 只能辅助不能兜底 |
| **引用稳定 ≠ 数据最新** | useCallback + memo 跳过渲染后，子组件可能拿到旧 props，UI 陈旧 |
| **单独用没意义** | useCallback 不配 memo 子组件 / effect 依赖，就是白包一层，纯增加比较开销 |

# 四、什么时候才值得用（判断标准）

- **useMemo**：create 是真实昂贵计算，或需要稳定引用传给 memo 子组件 / context value
- **useCallback**：回调传给 memo 子组件、或作为其他 hook 的依赖
- 反问自己：**不用它，性能问题能测量吗？** 测不到就是过早优化
