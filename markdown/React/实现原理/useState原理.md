# useState原理

面试经常提问：说一下 useState 的实现，分析为什么 hook 不能写进if里。


# 面试话术（1 分钟）

> useState 依赖 React 渲染期的**双 dispatcher + fiber 上的 hooks 链表**：mount 阶段创建节点、update 阶段按**调用顺序**遍历配对；更新通过 **dispatch 入队**，在下一次渲染时遍历 **queue** 计算新值。

> useState 的实现分 mount 和 update 两套。mount 阶段在 fiber 的 memoizedState 上**创建** hooks 链表，每个节点只有 memoizedState、queue、next 三个字段，不存名字；update 阶段不新建节点，而是**沿链表 next 遍历**，用「第 N 次调用」去配对「第 N 个节点」，遍历 queue 里的 action 算出新状态。dispatch 在创建时就绑定好 fiber 和 queue，所以引用稳定。这也解释了为什么 hook 不能写进 if——if 会让不同渲染的调用顺序不一致，update 遍历时就会取错节点：要么状态错位，要么 hook 数量比上次多直接报错。所以 rules-of-hooks 是保护这个链表约定的，不是风格问题。

> useState 本质是 useReducer 的特例。首次渲染走 mountState，在 fiber 的 memoizedState 上创建 hook 节点，节点只有 memoizedState、queue、next 三个字段，不存名字；初始化支持惰性计算。更新渲染走 updateState，不建新节点，而是沿链表**按调用顺序**取节点，遍历 queue 里的 action（普通值和函数式更新）算出新 state 写回。dispatch 在创建时就绑定好了 fiber 和 queue，所以引用稳定。setState 只是入队并触发 scheduleUpdateOnFiber 调度，真正的计算发生在下次渲染，所以更新是异步、可合并的。也正因为顺序即身份，hook 必须顶层调用，这是 rules-of-hooks 存在的原因。

配合这张「mount 创建 / update 遍历 / if 破坏」示意图：

```html type="renderer"
<html style="margin:0;padding:0;">
<title>useState 实现与 if 破坏原理</title>
<div style="width:100%;box-sizing:border-box;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f4f6f9;padding:22px;border-radius:14px;">
  <div style="font-size:18px;font-weight:700;color:#1f2933;margin-bottom:4px;">useState 实现 · 为什么不能写进 if</div>
  <div style="font-size:13px;color:#6b7280;margin-bottom:16px;">hook 节点无名字，身份 = 调用顺序（第 N 次调用 ↔ 链表第 N 个节点）</div>

  <div style="background:#fff;border-radius:10px;padding:14px;margin-bottom:10px;">
    <div style="font-size:13px;font-weight:700;color:#1d4ed8;margin-bottom:8px;">① mount（首次渲染）：创建链表</div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <div style="background:#dbeafe;color:#1d4ed8;border-radius:6px;padding:6px 10px;font-size:13px;">useState(a) → 建节点①</div>
      <div style="color:#9ca3af;">next →</div>
      <div style="background:#dbeafe;color:#1d4ed8;border-radius:6px;padding:6px 10px;font-size:13px;">useState(b) → 建节点②</div>
      <div style="color:#9ca3af;">next →</div>
      <div style="background:#dbeafe;color:#1d4ed8;border-radius:6px;padding:6px 10px;font-size:13px;">useState(c) → 建节点③</div>
    </div>
    <div style="font-size:12px;color:#6b7280;margin-top:6px;">fiber.memoizedState 指向①，每个节点存 { memoizedState, queue, next }</div>
  </div>

  <div style="background:#fff;border-radius:10px;padding:14px;margin-bottom:10px;">
    <div style="font-size:13px;font-weight:700;color:#15803d;margin-bottom:8px;">② update（更新渲染）：不建节点，沿 next 遍历配对</div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">第1次调用 → 节点①</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">第2次调用 → 节点②</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">第3次调用 → 节点③</div>
    </div>
    <div style="font-size:12px;color:#6b7280;margin-top:6px;">遍历 queue.pending 的 action 链 → 算新 state → 写回对应节点</div>
  </div>

  <div style="background:#fff;border-radius:10px;padding:14px;border:1px solid #fecaca;">
    <div style="font-size:13px;font-weight:700;color:#b91c1c;margin-bottom:8px;">③ if 跳变：顺序变了 → 配对错位 / 越界</div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <div style="background:#fee2e2;color:#b91c1c;border-radius:6px;padding:6px 10px;font-size:13px;">第1次调用 → 节点①</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#fee2e2;color:#b91c1c;border-radius:6px;padding:6px 10px;font-size:13px;border:2px dashed #ef4444;">第2次调用 → 拿到节点②（本意是 c）</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#fecaca;color:#b91c1c;border-radius:6px;padding:6px 10px;font-size:13px;">取尽 → 报错 more hooks</div>
    </div>
    <div style="font-size:12px;color:#b91c1c;margin-top:6px;">根因：hook 身份 = 调用位置序号，if/for/嵌套函数改写了「第 N 个调用是谁」</div>
  </div>

  <div style="margin-top:12px;background:#fffbeb;border-left:4px solid #d97706;border-radius:8px;padding:10px 14px;font-size:13px;color:#92400e;">
    加分点：dispatch 创建时绑定 fiber+queue → 引用稳定，useCallback 空依赖里用 setState 不踩闭包坑；setState 只是入队，计算发生在下次渲染遍历 queue 时 → 所以异步、可合并。
  </div>
</div>
```


# 一、useState 的实现（简化源码视角）

## 1. 双 dispatcher 机制

React 渲染组件时分两个阶段，`useState` 被"换实现"：

| 阶段 | 挂载的 dispatcher | useState 走的方法 | 行为 |
| --- | --- | --- | --- |
| **mount**（首次渲染） | `HooksDispatcherOnMount` | `mountState` | **创建** hook 节点，初始化 state，返回 `[state, dispatch]` |
| **update**（更新渲染） | `HooksDispatcherOnUpdate` | `updateState` | **沿链表遍历取**已有节点，计算新 state，返回 `[newState, dispatch]` |

> 
> 顺带说：useState 底层和 useReducer 共用同一套 queue 机制，useState 只是把 reducer 固定为 `basicStateReducer`（`state => state` / 函数式更新的特化）。

## 2. 简化伪代码（概念一致，非逐行真实源码）

```js
// ---- 全局状态：正在渲染的 fiber + 当前 hook 指针 ----
let currentlyRenderingFiber = null;
let workInProgressHook = null;      // 指向"链表当前节点"

// ---- 取/建第 N 个 hook 节点（mount 建新，update 复用）----
function mountWorkInProgressHook() {
  const hook = { memoizedState: null, queue: null, next: null };
  if (workInProgressHook === null) {
    currentlyRenderingFiber.memoizedState = hook;  // 链表头
  } else {
    workInProgressHook.next = hook;               // 串联下一个
  }
  workInProgressHook = hook;
  return hook;
}

function updateWorkInProgressHook() {
  // update 阶段不再新建节点：沿上一次的链表 next 取
  const hook = workInProgressHook.next;           // ← 关键：位置即身份
  workInProgressHook = hook;
  return hook;
}

// ---- useState 的 mount 版：创建节点 + 初始化 ----
function mountState(initialState) {
  const hook = mountWorkInProgressHook();
  hook.memoizedState = typeof initialState === 'function'
    ? initialState()                                   // 惰性初始化
    : initialState;
  const queue = (hook.queue = { pending: null });
  // dispatch 绑定 fiber + queue（与 state 值无关 → 引用稳定）
  const dispatch = dispatchSetState.bind(null, currentlyRenderingFiber, queue);
  return [hook.memoizedState, dispatch];
}

// ---- useState 的 update 版：遍历 queue 算新值 ----
function updateState() {
  const hook = updateWorkInProgressHook();           // 取链表第 N 个已存在节点
  const queue = hook.queue;
  // 遍历 queue.pending 里挂的 action 链：baseState → action1 → action2 …
  let newState = hook.memoizedState;
  for (const action of queue.pending) {
    newState = typeof action === 'function' ? action(newState) : action;
  }
  hook.memoizedState = newState;
  return [hook.memoizedState, dispatch];
}
```

核心就一句话：**hook 节点只存 `{memoizedState, queue, next}`，没有名字**。React 不知道你调的是 useState 还是 useRef，它只认「这次渲染第 N 次调用 = 链表第 N 个节点」。

# 二、为什么不能写进 if（从实现层面分析）

看 update 阶段就懂了：**update 不新建节点，是沿 `next` 遍历旧链表**。节点身份 = 遍历到的位置。

```js
function App({ flag }) {
  const [a, setA] = useState(0);        // update 时 → 取节点①
  if (flag) {
    const [b, setB] = useState(0);      // 存在时 → 取节点②（不存在时这里不调用）
  }
  const [c, setC] = useState(0);        // update 时 → 取节点③
}
```

| flag 变化 | 发生了什么 |
| --- | --- |
| `true → false` | 第 2 次调用没了 → `setC` 这次是第 2 次调用，取到**节点②（b 的）**→ `c` 拿到 `b` 的值，状态张冠李戴 |
| `false → true` | 调用变多 → 遍历到链表末尾还没取够 → React 报 **"Rendered more hooks than during the previous render"**（hooks 数量比上次渲染多） |

根因：**hook 的身份不是名字，而是「调用位置序号」**。if/for/嵌套函数会在不同渲染里改变「第 N 个调用是谁」，链表配对就崩了。这也是为什么必须靠 `eslint-plugin-react-hooks` 的 `rules-of-hooks` 在编译期静态拦截——它不是风格建议，是在保护链表配对约定。

# 三、两个加分细节

1. **为什么 dispatch 引用稳定？** `dispatch` 创建时只绑定了 `fiber + queue`，跟具体的 state 值无关 → 所以 `useCallback(..., [])` 里直接用 `setState` 不会有闭包陷阱，React 官方明确 setState 的 dispatch 是稳定的。
2. **为什么 setState 是异步的？** dispatch 只是把 action **塞进 queue**，真正的计算发生在下一次渲染（update 阶段遍历 queue 时）→ 所以 `setState` 后立刻读 state 是旧值，多次 setState 会合并。


# 核心术语表（背下来，能说出这些词就是区分度）

| 术语 | 含义 | 一句话用法 |
|---|---|---|
| **dispatcher** | 渲染期切换的两套实现：`HooksDispatcherOnMount` / `HooksDispatcherOnUpdate` | "useState 在 mount 和 update 是两套方法" |
| **fiber** | 组件对应的节点，`memoizedState` 指向 hooks 链表头 | "state 存在 fiber 上，不在组件函数里" |
| **hooks 链表** | hook 节点只存 `{ memoizedState, queue, next }`，**不存名字** | "节点无名字，身份靠位置" |
| **调用顺序（call-site）** | 第 N 次调用 ↔ 链表第 N 个节点 | "顺序即身份" |
| **queue** | hook 上的 action 队列（`pending` 字段） | "dispatch 只是入队" |
| **basicStateReducer** | useState 底层固定的 reducer（`useReducer` 特例） | "useState = 简化版 useReducer" |
| **dispatch** | 创建时绑定 `fiber + queue` 的稳定函数引用 | "引用稳定，useCallback 空依赖可用" |
| **惰性初始化** | `useState(() => 计算)`，mount 时执行一次 | "昂贵初始值用它" |
| **函数式更新** | action 为函数 `(prev) => new`，遍历 queue 时调用 | "依赖旧值用它，避免闭包陷阱" |
| **scheduleUpdateOnFiber** | dispatch 入队后触发重新渲染调度 | "更新入口是调度，不是立即改值" |
| **批量/异步更新** | 计算发生在**下次渲染**遍历 queue 时 | "所以 setState 后立刻读是旧值" |
| **rules-of-hooks** | ESLint 静态约束：顶层、不写进 if/for/嵌套 | "它保护的是链表配对约定" |

# 追问防守（一句话接住）

- 问「为什么顺序不能变」→ 节点无名字，靠第 N 次调用配对，if 一跳变就错位/越界报错
- 问「为什么 setState 异步」→ dispatch 只入队，计算在下次渲染遍历 queue 时
- 问「为什么 dispatch 稳定」→ 绑定的是 fiber+queue，与 state 值无关
- 问「useState vs useReducer」→ 同一个 queue 机制，后者 reducer 可自定义、逻辑可收敛可测试
