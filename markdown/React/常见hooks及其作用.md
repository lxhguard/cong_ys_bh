
# 常见hooks及其作用

## 一句话总览

常见 hooks 按职责分四类：**状态类**（useState / useReducer）、**副作用类**（useEffect）、**性能优化类**（useMemo / useCallback / useRef）、**跨组件共享类**（useContext）。

## 逐项表格（解决什么事）

| Hook | 解决什么 | 典型用法 | 注意点 |
| --- | --- | --- | --- |
| **useState** | 函数组件没有 this 和 `this.state`，需要一个本地状态 | `const [count, setCount] = useState(0)` | 更新是异步批量（React 18 自动批处理）；依赖旧值用函数式 `setCount(c => c + 1)`；初始值昂贵用惰性初始化 |
| **useReducer** | useState 面对**多个状态联动、转换规则复杂**时逻辑散落；把更新逻辑收敛成纯函数 | `const [state, dispatch] = useReducer(reducer, init)` | reducer 必须纯函数；dispatch 引用稳定（自带 useCallback 效果）；适合可测试的状态机 |
| **useEffect** | 替代生命周期：把「挂载/更新/卸载」的副作用聚合到一处，不再拆进三个生命周期方法 | `useEffect(() => { ...; return cleanup; }, [deps])` | 依赖数组控制时机：`[]` 只挂载跑、`[a]` a 变才跑、不传每次渲染跑；清理函数 = 卸载逻辑；注意闭包陷阱 |
| **useMemo** | 缓存**计算结果**：避免每次渲染重复计算昂贵值；保持值引用稳定 | `const v = useMemo(() => compute(a), [a])` | 依赖变了才重算；别滥用（早期优化是万恶之源）；核心价值是引用稳定 + 省重计算 |
| **useCallback** | 缓存**函数引用**：函数每次渲染都是新引用，传给 memo 子组件会导致其无谓重渲染 | `const fn = useCallback(() => {...}, [deps])` | 配合 `React.memo` 才有效；依赖空数组时引用永久稳定但闭包捕获初始值（stale closure 坑） |
| **useContext** | 跨层级共享数据，**避免 prop drilling**（逐层传 props） | `const { user } = useContext(UserCtx)` | 值变化 → **所有消费组件都重渲染**；不是状态管理（无自己的更新机制）；复杂场景拆 context / 包 useMemo |
| **useRef** | 跨渲染**持久化的可变引用**，修改**不触发渲染**；也用于拿 DOM | `const ref = useRef(0); ref.current++` | 改 current 不重渲染；比普通变量强在跨渲染存活；拿 DOM 是 `ref={ref}`；转发用 `forwardRef` |

## 高频追问（答出来就是 P6+ 区分度）

1. **useState vs useReducer 怎么选？**
单一独立状态 → useState；多个状态互相联动、更新规则多、需要可测试 → useReducer。useReducer 把「怎么变」从组件里抽走，reducer 是纯函数。
2. **useMemo vs useCallback 区别？**
useMemo 缓存**值**，useCallback 缓存**函数**；且 `useCallback(fn, deps)` 等价于 `useMemo(() => fn, deps)`。两者都要配合 `React.memo` 的引用比较才有意义。
3. **useRef vs useState？**
都跨渲染保留，但 **useRef 改值不触发渲染**，useState 会。所以"存但不显示"用 ref（定时器 id、上次的值），"存且要 UI 响应"用 state。
4. **useEffect 依赖数组的闭包陷阱？**`[]` 空依赖时 effect 闭包捕获**首次渲染**的值，之后永远拿旧值 → 解法：依赖补全、函数式更新、或用 ref 读最新值。
5. **useContext 性能问题？**
context 值一变，所有消费组件无条件重渲染 → 解法：把 value 用 `useMemo` 包住、拆分成多个小 context、或高频变化部分用状态管理库（zustand/redux）。
6. **useEffect 里 setState 会死循环吗？**
会——如果 setState 后依赖数组里的值又变了就会无限循环；解法是只依赖稳定值或把计算移出 effect。

## 1.5 分钟面试话术

> 
> 我把常见 hooks 按职责分四类。**状态类**：useState 是函数组件的本地状态；当状态结构复杂、多个状态联动时升级 useReducer，把更新逻辑收敛成纯函数 reducer，dispatch 引用还天然稳定。**副作用类**：useEffect 替代生命周期，把挂载、更新、卸载的副作用聚合到一处，依赖数组控制执行时机，返回清理函数做卸载逻辑。**性能优化类**：useMemo 缓存计算结果、useCallback 缓存函数引用，核心都是保持引用稳定，配合 React.memo 让子组件跳过无谓重渲染；useRef 提供跨渲染持久、改动不触发渲染的可变引用，也用来拿 DOM。**共享类**：useContext 解决跨层级数据共享、避免 prop drilling，但它没有自己的更新机制，值一变所有消费组件都重渲染，所以高频变化场景要拆 context 或上状态管理。

下面这张分类记忆图配合背诵：

```html type="renderer"
<html style="margin:0;padding:0;">
<title>常见 Hooks 分类与职责总览</title>
<div style="width:100%;box-sizing:border-box;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f4f6f9;padding:22px;border-radius:14px;">
  <div style="font-size:18px;font-weight:700;color:#1f2933;margin-bottom:4px;">常见 Hooks · 四类职责总览</div>
  <div style="font-size:13px;color:#6b7280;margin-bottom:16px;">React 16.8 引入 · 记忆链：状态 / 副作用 / 性能 / 共享</div>
  <div style="display:flex;flex-wrap:wrap;gap:12px;">
    <div style="flex:1 1 260px;min-width:240px;background:#fff;border-radius:10px;border-top:4px solid #16a34a;padding:12px 14px;">
      <div style="font-size:14px;font-weight:700;color:#15803d;">状态类</div>
      <div style="font-size:13px;color:#374151;margin-top:6px;line-height:1.7;"><b>useState</b> → 函数组件本地状态<br><b>useReducer</b> → 复杂联动状态、纯函数收敛更新逻辑</div>
    </div>
    <div style="flex:1 1 260px;min-width:240px;background:#fff;border-radius:10px;border-top:4px solid #e5484d;padding:12px 14px;">
      <div style="font-size:14px;font-weight:700;color:#b91c1c;">副作用类</div>
      <div style="font-size:13px;color:#374151;margin-top:6px;line-height:1.7;"><b>useEffect</b> → 替代生命周期，挂载/更新/卸载聚合一处，依赖数组控时机</div>
    </div>
    <div style="flex:1 1 260px;min-width:240px;background:#fff;border-radius:10px;border-top:4px solid #3b82f6;padding:12px 14px;">
      <div style="font-size:14px;font-weight:700;color:#1d4ed8;">性能优化类</div>
      <div style="font-size:13px;color:#374151;margin-top:6px;line-height:1.7;"><b>useMemo</b> → 缓存计算结果<br><b>useCallback</b> → 缓存函数引用<br><b>useRef</b> → 跨渲染持久、改值不渲染</div>
    </div>
    <div style="flex:1 1 260px;min-width:240px;background:#fff;border-radius:10px;border-top:4px solid #8b5cf6;padding:12px 14px;">
      <div style="font-size:14px;font-weight:700;color:#6d28d9;">跨组件共享类</div>
      <div style="font-size:13px;color:#374151;margin-top:6px;line-height:1.7;"><b>useContext</b> → 避免 prop drilling；注意：值变全量重渲染、非状态管理</div>
    </div>
  </div>
  <div style="margin-top:14px;background:#fffbeb;border-left:4px solid #d97706;border-radius:8px;padding:10px 14px;font-size:13px;color:#92400e;">
    追问速记：useReducer 管联动｜useCallback≈useMemo(()=&gt;fn)｜useRef 改值不渲染｜useEffect 空依赖闭包陷阱｜useContext 用 useMemo 包 value
  </div>
</div>
```
