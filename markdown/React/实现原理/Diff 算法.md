# Diff 算法原理

## 一、为什么需要 Diff

每次渲染都会生成新的虚拟 DOM 树，React 需要在 `beginWork` 里把新树和旧树对比，**找出最小变更集合**，只 patch 变化部分。暴力对比整棵树的编辑距离是 **O(n³)**，所以 React 用三条启发式策略把复杂度降到 **O(n)**。

## 二、三条策略（核心，面试先背这个）

| 策略 | 规则 | 后果 |
|---|---|---|
| **Tree Diff（同层比较）** | 只比较**同一层级**的节点，不跨层移动 | 跨层移动 = **删除 + 重建**，不做移动优化 |
| **Component Diff（类型判定）** | 两个节点 **type 不同** → 直接销毁重建**整棵子树**，不再往下递归 | 同位置不同组件，子树全部重建 |
| **Element Diff（key 复用）** | 同层列表用 **key** 唯一标识节点，最大化复用 | 同 key 同 type → 复用，只更新 props |

## 三、单节点 diff（判定表）

| 条件 | 行为 |
|---|---|
| key 相同 + type 相同 | **复用**节点，更新 props |
| key 相同 + type 不同 | 销毁重建（走 Component Diff） |
| key 不同 | 销毁重建 |

## 四、多节点 diff（数组 children，双指针算法）

React 16+ 对同一层的多个子节点用**三轮扫描**：

```
① 从左往右扫：key 相同 → 复用，直到遇到第一个 key 不同的节点停下（处理头部）
② 从右往左扫：key 相同 → 复用，处理尾部
③ 中间剩余：把旧节点的 key 建 Map（key → fiber），逐个查新剩余节点：
     命中 → 移动并标记 Placement（更新位置）
     未命中 → 新建
     旧的剩余没被用 → 标记 Deletion（删除）
```

最后把所有标记（Placement / Update / Deletion）收集进 effect 链表，交给 Commit 阶段统一执行。

## 五、key 的作用与 index 的坑（必考）

**key 是列表节点的身份标识**（同一父级下唯一），让 React 在顺序变化时还能认出"谁是谁"，从而复用。

用 **index 作 key** 的坑——头部插入时：

```jsx
// 旧：<li key={0}>A</li> <li key={1}>B</li> <li key={2}>C</li>
// 新：<li key={0}>X</li> <li key={1}>A</li> <li key={2}>B</li> <li key={3}>C</li>
//            ↑ index 全错位：React 认为 A 还是 key=0 的节点 → 复用错对象
```

后果：**内容、DOM 状态、输入框内容、滚动位置被错误复用**——列表项是 `key={index}` 时，在头部/中间插入一条，后面的项全被"张冠李戴"。

正确做法：key 用**稳定、唯一、可预测**的 id（数据 id / 唯一字段）；别用随机数（每次渲染新 key → 全部重建，diff 白费）。

## 六、为什么 O(n³) → O(n)

完整树编辑距离是 O(n³)，React 用「同层比较 + 类型判定 + key」三条**启发式假设**缩小比较范围 → O(n)。代价是假设不成立时性能退化（跨层移动、类型切换会退化成重建），但**正确性不受影响**——这就是 React 对"移动节点"场景不够高效的根因（这也是它没有专门优化"跨层移动"的原因）。

## 面试话术（1 分钟）

> Diff 发生在 render 阶段，目的是找出新旧树的最小差异。暴力对比是 O(n³)，React 用三条启发式策略降为 O(n)：一是**同层比较**，只比较同一层级，跨层移动直接删除重建；二是**类型不同就重建**，type 变了整棵子树销毁重建，不再往下递归；三是**key 复用**，列表用 key 标识身份，顺序变化时能认出同一个节点。多节点 diff 用双指针算法，先从左、再从右扫描复用的，中间剩余的部分用 key 建 Map 来判定移动、新建和删除，最后标记成 Placement/Update/Deletion 交给 commit。key 必须稳定唯一，用 index 在头部插入时会让后续节点全部错位复用，导致状态错乱。

流程图：

```html type="renderer"
<html style="margin:0;padding:0;">
<title>React Diff 算法原理</title>
<div style="width:100%;box-sizing:border-box;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;background:#f4f6f9;padding:22px;border-radius:14px;">
  <div style="font-size:18px;font-weight:700;color:#1f2933;margin-bottom:4px;">Diff 算法 · O(n³) → O(n)</div>
  <div style="font-size:13px;color:#6b7280;margin-bottom:16px;">三条启发式策略 + 双指针多节点 diff · 发生在 render 阶段的 beginWork</div>

  <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:10px;">
    <div style="flex:1 1 200px;min-width:180px;background:#fff;border-radius:10px;border-left:6px solid #3b82f6;padding:10px 12px;">
      <div style="font-size:13px;font-weight:700;color:#1d4ed8;">Tree Diff</div>
      <div style="font-size:13px;color:#374151;margin-top:4px;">只同层比较；跨层移动 = 删除+重建</div>
    </div>
    <div style="flex:1 1 200px;min-width:180px;background:#fff;border-radius:10px;border-left:6px solid #8b5cf6;padding:10px 12px;">
      <div style="font-size:13px;font-weight:700;color:#6d28d9;">Component Diff</div>
      <div style="font-size:13px;color:#374151;margin-top:4px;">type 不同 → 整棵子树销毁重建</div>
    </div>
    <div style="flex:1 1 200px;min-width:180px;background:#fff;border-radius:10px;border-left:6px solid #16a34a;padding:10px 12px;">
      <div style="font-size:13px;font-weight:700;color:#15803d;">Element Diff</div>
      <div style="font-size:13px;color:#374151;margin-top:4px;">列表用 key 标识身份 → 复用 + 移动</div>
    </div>
  </div>

  <div style="background:#fff;border-radius:10px;padding:14px;margin-bottom:10px;">
    <div style="font-size:13px;font-weight:700;color:#1f2933;margin-bottom:8px;">多节点 diff · 双指针三轮扫描</div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      <div style="background:#dbeafe;color:#1d4ed8;border-radius:6px;padding:6px 10px;font-size:13px;">① 从左往右<br><span style="font-weight:400;">key 相同复用，遇不同停</span></div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dbeafe;color:#1d4ed8;border-radius:6px;padding:6px 10px;font-size:13px;">② 从右往左<br><span style="font-weight:400;">处理尾部复用</span></div>
      <div style="color:#9ca3af;">→</div>
      <div style="background:#dbeafe;color:#1d4ed8;border-radius:6px;padding:6px 10px;font-size:13px;">③ 中间剩余<br><span style="font-weight:400;">key→Map：命中移动 / 未命中新建 / 旧多余删除</span></div>
    </div>
    <div style="font-size:12px;color:#6b7280;margin-top:6px;">产出标记：Placement（移动/插入）/ Update / Deletion → effect 链表 → commit 统一执行</div>
  </div>

  <div style="background:#fff;border-radius:10px;padding:14px;border:1px solid #fecaca;">
    <div style="font-size:13px;font-weight:700;color:#b91c1c;margin-bottom:6px;">index 作 key 的坑（必考）</div>
    <div style="font-size:13px;color:#374151;line-height:1.9;">
      旧：key=[0]A [1]B [2]C　→　新（头部插 X）：key=[0]X [1]A [2]B [3]C
      <br>React 按 key 认人：A 还是 key=0 → 与 X 位置相同被复用 → <b>内容/输入框/状态错位</b>
      <br>key 要求：稳定、唯一、可预测（用数据 id）；别用 index、别用随机数
    </div>
  </div>

  <div style="margin-top:12px;background:#fffbeb;border-left:4px solid #d97706;border-radius:8px;padding:10px 14px;font-size:13px;color:#92400e;">
    一句话：<b>同层比、类型变就重建、key 认身份</b>；代价是跨层移动不优化（退化为重建），但正确性不受影响。
  </div>
</div>
</html>
```
