# 为什么hooks不能嵌套

# 面试话术（30 秒）

> Hooks 必须顶层调用，是因为 React 内部把每个组件的 hook 按**调用顺序**存成一条链表挂在 fiber 上，渲染时也是按「第 N 次调用 → 链表第 N 个节点」来配对 state 的。它不按名字查找，只认顺序。所以如果 hook 出现在条件、循环或嵌套函数里，某次渲染的调用顺序一变，后面的 hook 全部错位，状态就会张冠李戴甚至崩溃。这也是为什么有 `rules-of-hooks` 这个 ESLint 规则在编译期强制约束。自定义 Hook 不违反这个规则，因为它只是渲染期间执行的普通函数，顺序仍然由组件决定。

下面这张「链表对齐 vs 错位」示意图配合理解：

```html type="renderer"
<html style="margin:0;padding:0;">
<title>Hooks 链表顺序匹配原理</title>
<div style="width:100%;box-sizing:border-box;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f4f6f9;padding:22px;border-radius:14px;">
  <div style="font-size:18px;font-weight:700;color:#1f2933;margin-bottom:4px;">Hooks 为什么必须顶层调用</div>
  <div style="font-size:13px;color:#6b7280;margin-bottom:16px;">fiber.memoizedState 上的链表 · React 按「调用顺序」配对 state，不按名字</div>

  <div style="background:#fff;border-radius:10px;padding:14px;margin-bottom:10px;">
    <div style="font-size:13px;font-weight:700;color:#15803d;margin-bottom:8px;">✅ 顺序稳定：两次渲染 1:1 对齐</div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <div style="font-size:12px;color:#6b7280;">第1次渲染</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">① useState(A)</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">② useEffect(B)</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">③ useState(C)</div>
    </div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:6px;">
      <div style="font-size:12px;color:#6b7280;">第2次渲染</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">① useState(A)</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">② useEffect(B)</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">③ useState(C)</div>
    </div>
  </div>

  <div style="background:#fff;border-radius:10px;padding:14px;border:1px solid #fecaca;">
    <div style="font-size:13px;font-weight:700;color:#b91c1c;margin-bottom:8px;">❌ if 里调用：第2次渲染少一个 → 整体错位</div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <div style="font-size:12px;color:#6b7280;">第1次渲染</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">① useState(A)</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">② useState(B) if内</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">③ useState(C)</div>
    </div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:6px;">
      <div style="font-size:12px;color:#6b7280;">第2次渲染</div>
      <div style="background:#dcfce7;color:#15803d;border-radius:6px;padding:6px 10px;font-size:13px;">① useState(A)</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#fee2e2;color:#b91c1c;border-radius:6px;padding:6px 10px;font-size:13px;border:2px dashed #ef4444;">② 取到 B 的节点（本该是 C）</div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#fecaca;color:#b91c1c;border-radius:6px;padding:6px 10px;font-size:13px;">③ 越界/取到错节点</div>
    </div>
  </div>

  <div style="margin-top:12px;background:#fffbeb;border-left:4px solid #d97706;border-radius:8px;padding:10px 14px;font-size:13px;color:#92400e;">
    关键句：<b>第 N 次调用 = 链表第 N 个节点</b>，不按名字、不按 Map，只认顺序 → 所以禁止 if / for / 嵌套函数里调用，靠 eslint 的 rules-of-hooks 静态拦截。
  </div>
</div>
```




# 一句话原因

**React 不按名字、只按「调用顺序」来匹配 state**——每次渲染时，组件里第 N 次调用 hook，就去取存储链表里的第 N 个节点。所以 hook 的调用顺序必须每次渲染完全一致，一旦条件/循环/嵌套改变了顺序，状态就全错位了。


# 原理：fiber 上的 hooks 链表

每个组件对应一个 fiber 节点，fiber 上挂着一个 **hooks 链表**（`memoizedState` 指向链表头，每个 hook 通过 `next` 串联）：

```text
fiber.memoizedState
   └─▶ hook1 (useState A) ──next──▶ hook2 (useEffect B) ──next──▶ hook3 (useState C)
         queue / memoizedState        queue / memoizedState       queue / memoizedState
```

**渲染时**：组件函数执行，第一次调用 `useState` → 取链表第 1 个节点，第二次调用 → 取第 2 个……React 拿着「这次调用」去更新「上次存的那个节点」的 state。

**更新时**：同样按顺序遍历，用 `queue` 里的 action 计算新状态，再把新值存回对应节点。

# 顺序一变，就错位

```js
function App({ flag }) {
  const [a, setA] = useState(0);
  if (flag) {
    const [b, setB] = useState(0);   // ❌ 条件里调用
  }
  const [c, setC] = useState(0);
  return null;
}
```

- `flag = true` 时：调用顺序是 useState(A) → useState(B) → useState(C)，链表有 3 个节点
- `flag = false` 时：只调用 2 个，链表还是 3 个节点 → 第二次调用 `useState` 时**取到了 B 的节点**，但它本意是 C → 状态张冠李戴，`c` 拿到的是 `b` 的值，严重时直接报错

同理，循环里调用 hook（数量随数据变化）、嵌套函数里调用（顺序不可控），都会破坏「第 N 次调用 = 第 N 个节点」的约定。

# 为什么 React 要这么设计（加分点）

**链表 + 顺序索引**是刻意的取舍：

- **性能**：不需要按名字做 Map 查找，遍历一次 O(n) 极快，且天然贴合「每次渲染全量执行」的模型
- **简单**：hook 不需要名字、不需要注册表，fiber 节点轻
- **代价**：调用顺序成了硬约束 → 用 ESLint 的 `rules-of-hooks` 在编译期静态拦截（检查 hook 是否出现在条件/循环/嵌套函数里）

# 两个容易混淆的补充

| 场景 | 为什么可以/不行 |
| --- | --- |
| 自定义 Hook 里调用 hooks | **可以**。自定义 Hook 本质是在组件渲染期间执行的普通函数，调用顺序仍由组件的渲染顺序决定，没有破坏「第 N 次调用」 |
| 事件回调里调用 hooks | **不行**。回调不在渲染期执行，fiber 的链表匹配流程不存在，也没有对应节点的 state 可更新 |

